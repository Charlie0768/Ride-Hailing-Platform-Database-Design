"""Capture executable SQL and real table samples for report presentation."""
import os,subprocess,csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cmd=[os.environ.get('MYSQL_BIN','mysql'),'--no-defaults','--protocol=SOCKET','--socket='+os.environ.get('MYSQL_SOCKET','/tmp/ride_hailing.sock'),'-uroot','--batch','--raw','ride_hailing']
def query(sql):
 p=subprocess.run(cmd,input=sql,text=True,capture_output=True,check=True)
 return p.stdout,list(csv.DictReader(p.stdout.splitlines(),delimiter='\t'))
queries={
'show_tables':'SHOW TABLES;',
'describe_trip':'DESCRIBE trip;',
'app_user':"SELECT user_id,full_name,phone FROM app_user ORDER BY user_id LIMIT 3;",
'passenger':"SELECT * FROM passenger ORDER BY passenger_id LIMIT 3;",
'driver':"SELECT * FROM driver ORDER BY driver_id LIMIT 3;",
'vehicle':"SELECT * FROM vehicle ORDER BY plate LIMIT 3;",
'insurance_policy':"SELECT * FROM insurance_policy ORDER BY policy_id LIMIT 3;",
'driver_shift':"SELECT * FROM driver_shift ORDER BY driver_id,shift_start LIMIT 3;",
 'trip':"SELECT trip_id,passenger_id,plate,status,estimated_fare FROM trip ORDER BY trip_id LIMIT 6;",
'completed_trip':"SELECT * FROM completed_trip ORDER BY trip_id LIMIT 3;",
'cancelled_trip':"SELECT * FROM cancelled_trip ORDER BY trip_id LIMIT 3;",
'review':"SELECT trip_id,passenger_score,driver_score FROM review ORDER BY trip_id LIMIT 3;",
'surcharge':"SELECT * FROM surcharge ORDER BY trip_id LIMIT 3;",
'joined_example':"SELECT t.trip_id,t.status,t.plate,v.driver_id,t.estimated_fare,f.total_fare FROM trip t LEFT JOIN vehicle v ON v.plate=t.plate LEFT JOIN trip_financials f ON f.trip_id=t.trip_id ORDER BY t.trip_id LIMIT 6;"}
results={}
for key,sql in queries.items():
 out,rows=query(sql);(R/f'results/sample_{key}.tsv').write_text(out);results[key]={'sql':sql,'rows':rows}
steps=[('insert',"INSERT INTO app_user(user_id,full_name,phone) VALUES(9998,'CRUD Demo','demo-crud-9998');","SELECT user_id,full_name,phone FROM app_user WHERE user_id=9998;"),('update',"UPDATE app_user SET full_name='CRUD Updated' WHERE user_id=9998;","SELECT user_id,full_name,phone FROM app_user WHERE user_id=9998;"),('delete',"DELETE FROM app_user WHERE user_id=9998;","SELECT COUNT(*) AS remaining FROM app_user WHERE user_id=9998;")]
for key,mutation,sql in steps:
 query(mutation);out,rows=query(sql);(R/f'results/crud_{key}.tsv').write_text(out);results['crud_'+key]={'sql':mutation+'\n'+sql,'rows':rows}
assert query('SELECT COUNT(*) AS n FROM trip;')[1][0]['n']=='200'
(R/'results/report_evidence.json').write_text(json.dumps(results,indent=2))
(R/'sql/07_report_demonstrations.sql').write_text('USE ride_hailing;\n\n'+'\n\n'.join('-- '+key+'\n'+val['sql'] for key,val in results.items()))
print('Captured SHOW TABLES, DESCRIBE, 11 table samples, joined output and CRUD before/after results.')
