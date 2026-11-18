"""Run against a dedicated MySQL schema. Credentials may be supplied via mysql defaults."""
from pathlib import Path
import os,subprocess,json,csv,concurrent.futures
root=Path(__file__).resolve().parents[1]
bin=os.environ.get('MYSQL_BIN','mysql'); socket=os.environ.get('MYSQL_SOCKET','/tmp/ride_hailing.sock')
base=[bin,'--no-defaults','--protocol=SOCKET',f'--socket={socket}','-uroot','--batch','--raw','ride_hailing']
def run(sql,check=True):
 p=subprocess.run(base,input=sql,text=True,capture_output=True)
 if check and p.returncode:raise RuntimeError(p.stderr+'\n'+sql)
 return p
checks=[]
def record(name,ok,detail=''):
 checks.append({'test':name,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError(name+': '+detail)
def negative(name,sql,code):
 p=run('START TRANSACTION;'+sql+';ROLLBACK;',False)
 record(name,p.returncode!=0 and f'ERROR {code} ' in p.stderr,p.stderr.strip())
def scalar(sql):return run(sql).stdout.strip().splitlines()[-1]
negative('duplicate primary key',"INSERT INTO app_user VALUES(1,'X','x',NULL,NULL)",1062)
negative('invalid foreign key',"INSERT INTO passenger VALUES(999999,'STANDARD')",1452)
negative('invalid score',"UPDATE review SET passenger_score=101 LIMIT 1",3819)
negative('empty review',"UPDATE review SET passenger_score=NULL,driver_score=NULL LIMIT 1",3819)
negative('duplicate review',"INSERT INTO review SELECT * FROM review LIMIT 1",1062)
negative('invalid shift chronology',"INSERT INTO driver_shift VALUES(1,'2030-01-01 10:00:00','2030-01-01 09:00:00')",3819)
negative('negative amount',"UPDATE completed_trip SET base_fare=-1 LIMIT 1",3819)
negative('missing required field',"INSERT INTO app_user VALUES(9999,NULL,'test9999',NULL,NULL)",1048)
negative('vehicle ownership immutable',"UPDATE vehicle SET driver_id=2 WHERE plate='DEMO001'",1644)
completed=scalar("SELECT MIN(trip_id) FROM completed_trip")
negative('completion cancellation exclusion',f"INSERT INTO cancelled_trip VALUES({completed},'2026-12-01','test')",1644)
# Safe lifecycle fixture. Removed before the published analytics are collected.
run("INSERT INTO trip VALUES(9001,101,NULL,'2026-10-01 08:00:00',NULL,'Central','Airport','STANDARD',10,30,'REQUESTED');")
negative('driver vehicle mismatch',"CALL assign_trip(9001,2,'DEMO001')",1644)
record('failed assignment unchanged',scalar('SELECT status FROM trip WHERE trip_id=9001')=='REQUESTED')
run("CALL assign_trip(9001,1,'DEMO001');")
negative('start before request',"CALL start_trip(9001,'2026-09-01')",3819)
run("CALL start_trip(9001,'2026-10-01 08:10:00');")
negative('end before start',"CALL complete_trip(9001,'2026-10-01 08:05:00',25,2,10,4)",1644)
negative('partial operation rollback',"CALL complete_trip(9001,'2026-10-01 09:00:00',25,2,10,-1)",1644)
record('no detail after rollback',scalar('SELECT COUNT(*) FROM completed_trip WHERE trip_id=9001')=='0')
record('state after rollback',scalar('SELECT status FROM trip WHERE trip_id=9001')=='IN_PROGRESS')
# Competing completions serialize on the same trip row.
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 ps=list(pool.map(lambda _:run("CALL complete_trip(9001,'2026-10-01 09:00:00',25,2,10,4)",False),range(2)))
record('concurrent completion one winner',sum(p.returncode==0 for p in ps)==1 and any('ERROR 1644 ' in p.stderr for p in ps),'; '.join(p.stderr.strip() or 'success' for p in ps))
record('completed fare and single detail',scalar('SELECT total_fare FROM trip_financials WHERE trip_id=9001')=='31.00')
negative('cannot cancel completed trip',"CALL cancel_trip(9001,'2026-10-02','test')",1644)
negative('cannot delete referenced user','DELETE FROM app_user WHERE user_id=1',1451)
run('START TRANSACTION;DELETE FROM surcharge WHERE trip_id=9001;DELETE FROM completed_trip WHERE trip_id=9001;DELETE FROM trip WHERE trip_id=9001;COMMIT;')
run("INSERT INTO trip VALUES(9002,101,NULL,'2026-10-01 08:00:00',NULL,'Central','Airport','STANDARD',10,30,'REQUESTED');CALL cancel_trip(9002,'2026-10-01 08:05:00','Plans changed');")
record('successful cancellation',scalar('SELECT status FROM trip WHERE trip_id=9002')=='CANCELLED')
run('START TRANSACTION;DELETE FROM cancelled_trip WHERE trip_id=9002;DELETE FROM trip WHERE trip_id=9002;COMMIT;')
run("START TRANSACTION; INSERT INTO app_user VALUES(9999,'Temporary','demo-temp',NULL,NULL);UPDATE app_user SET full_name='Updated' WHERE user_id=9999;DELETE FROM app_user WHERE user_id=9999;COMMIT;")
record('insert update delete cycle',scalar('SELECT COUNT(*) FROM app_user WHERE user_id=9999')=='0')
record('200 trips retained',scalar('SELECT COUNT(*) FROM trip')=='200')
record('state detail consistency',scalar("SELECT COUNT(*) FROM trip t LEFT JOIN completed_trip c ON c.trip_id=t.trip_id LEFT JOIN cancelled_trip x ON x.trip_id=t.trip_id WHERE (t.status='COMPLETED')<>(c.trip_id IS NOT NULL) OR (t.status='CANCELLED')<>(x.trip_id IS NOT NULL)")=='0')
record('warehouse count reconciliation',scalar('SELECT (SELECT COUNT(*) FROM dw_trip_fact)=(SELECT COUNT(*) FROM completed_trip)')=='1')
record('warehouse fare reconciliation',scalar('SELECT (SELECT SUM(total_fare) FROM dw_trip_fact)=(SELECT SUM(total_fare) FROM trip_financials)')=='1')
record('financial view no fanout',scalar('SELECT COUNT(*)=COUNT(DISTINCT trip_id) FROM trip_financials')=='1')
record('role overlap supported',scalar('SELECT COUNT(*) FROM passenger p JOIN driver d ON d.driver_id=p.passenger_id')=='1')
record('multiple daily shifts',scalar("SELECT COUNT(*) FROM driver_shift WHERE driver_id=1 AND DATE(shift_start)='2026-10-01'")=='2')
# Temporary least-privilege account; no password, socket-only isolated test server.
run("CREATE USER 'rh_validation'@'localhost'; GRANT 'ride_hailing_app' TO 'rh_validation'@'localhost'; SET DEFAULT ROLE 'ride_hailing_app' TO 'rh_validation'@'localhost';")
limited=[x if x!='-uroot' else '-urh_validation' for x in base]
p=subprocess.run(limited,input="UPDATE trip SET status='CANCELLED' WHERE trip_id=1;",text=True,capture_output=True)
record('app cannot bypass transitions',p.returncode!=0 and 'ERROR 1142 ' in p.stderr,p.stderr.strip())
p=subprocess.run(limited,input="INSERT INTO trip(trip_id,passenger_id,requested_at,origin_zone,destination_zone,service_type,estimated_km,estimated_fare) VALUES(9003,101,'2026-10-01','East','West','STANDARD',5,20);CALL cancel_trip(9003,'2026-10-01 00:10:00','test');",text=True,capture_output=True)
record('app authorized request and cancel',p.returncode==0,p.stderr.strip())
run("DELETE FROM cancelled_trip WHERE trip_id=9003;DELETE FROM trip WHERE trip_id=9003;DROP USER 'rh_validation'@'localhost';")
# Actual server metadata used to generate the dictionary.
metadata=run("SELECT TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_KEY FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='ride_hailing' AND TABLE_NAME NOT LIKE 'dw_%' AND TABLE_NAME NOT IN ('trip_financials','trip_service') ORDER BY TABLE_NAME,ORDINAL_POSITION").stdout
(root/'results/data_dictionary.tsv').write_text(metadata)
queries={
'version':'SELECT VERSION() AS version',
'counts':"SELECT 'app_user' AS table_name,COUNT(*) AS rows_n FROM app_user"+''.join(f" UNION ALL SELECT '{t}',COUNT(*) FROM {t}" for t in ['passenger','driver','vehicle','insurance_policy','driver_shift','trip','completed_trip','cancelled_trip','review','surcharge']),
'status':"SELECT status,COUNT(*) AS trips,ROUND(100*COUNT(*)/(SELECT COUNT(*) FROM trip),2) AS percent_all FROM trip GROUP BY status ORDER BY status",
'finance':"SELECT COUNT(*) AS completed,SUM(total_fare) AS total_fare,ROUND(AVG(total_fare),2) AS mean_fare,ROUND(AVG(total_fare-estimated_fare),2) AS mean_difference,SUM(surcharge) AS surcharges,SUM(tip) AS tips FROM trip_financials",
'drivers':"SELECT d.driver_id,COUNT(f.trip_id) AS completed,COALESCE(SUM(f.total_fare),0) AS gross_fare,ROUND(AVG(r.passenger_score),2) AS mean_score,COUNT(r.passenger_score) AS scored FROM driver d LEFT JOIN trip_financials f ON f.driver_id=d.driver_id LEFT JOIN review r ON r.trip_id=f.trip_id GROUP BY d.driver_id ORDER BY gross_fare DESC",
'insurance':"SELECT policy_id,plate,valid_to FROM insurance_policy WHERE valid_to BETWEEN '2026-11-01' AND DATE_ADD('2026-11-01',INTERVAL 30 DAY) ORDER BY policy_id",
'daily':"SELECT date_key,COUNT(*) AS trips,SUM(total_fare) AS gross_fare FROM dw_trip_fact GROUP BY date_key ORDER BY date_key",
'rollup':"SELECT d.calendar_year,d.calendar_month,v.model,COUNT(*) AS trips,SUM(f.total_fare) AS gross_fare FROM dw_trip_fact f JOIN dw_date d ON d.date_key=f.date_key JOIN dw_vehicle v ON v.vehicle_key=f.vehicle_key GROUP BY d.calendar_year,d.calendar_month,v.model WITH ROLLUP",
'window':"SELECT date_key,SUM(total_fare) AS daily_fare,LAG(SUM(total_fare)) OVER(ORDER BY date_key) AS previous_day_fare FROM dw_trip_fact GROUP BY date_key ORDER BY date_key",
'nested':"SELECT driver_id,ROUND(AVG(total_fare),2) AS mean_fare FROM trip_financials GROUP BY driver_id HAVING AVG(total_fare)>(SELECT AVG(total_fare) FROM trip_financials)",
'explain':"EXPLAIN SELECT trip_id,status FROM trip WHERE passenger_id=101 AND requested_at>='2026-10-05' AND requested_at<'2026-10-10'",
}
results={}
for name,sql in queries.items():
 out=run(sql).stdout
 (root/f'results/{name}.tsv').write_text(out)
 results[name]=list(csv.DictReader(out.splitlines(),delimiter='\t'))
(root/'results/query_results.json').write_text(json.dumps(results,indent=2))
(root/'results/validation.json').write_text(json.dumps(checks,indent=2))
(root/'sql/05_queries.sql').write_text('USE ride_hailing;\n\n'+'\n\n'.join('-- '+name+'\n'+sql+';' for name,sql in queries.items()))
print(json.dumps({'passed':sum(c['passed'] for c in checks),'total':len(checks),'finance':results['finance'],'version':results['version']},indent=2))
