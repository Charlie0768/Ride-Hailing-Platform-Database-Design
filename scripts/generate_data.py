"""Deterministic synthetic records; no real customer information."""
from pathlib import Path
import random,datetime as dt,json
r=random.Random(20261118); root=Path(__file__).resolve().parents[1]
lines=['USE ride_hailing;']
def q(x):
 if x is None:return 'NULL'
 if isinstance(x,(int,float)):return str(x)
 return "'"+str(x).replace("'","''")+"'"
def insert(t,v):lines.append(f"INSERT INTO {t} VALUES("+','.join(map(q,v))+');')
for uid in list(range(1,9))+list(range(101,127)):
 insert('app_user',[uid,f'Demo User {uid}',f'+860000{uid:06}',f'user{uid}@example.invalid','1995-06-15'])
for uid in [1]+list(range(101,126)):insert('passenger',[uid,r.choice(['STANDARD','GOLD','PLATINUM'])])
for did in range(1,9):insert('driver',[did,f'DEMO-LIC-{did:03}',1000+did*125])
vehicles=[]
for vid in range(1,13):
 did=(vid-1)%8+1; plate=f'DEMO{vid:03}';vehicles.append((plate,did))
 insert('vehicle',[plate,did,['Sedan','MPV','Electric'][vid%3],['White','Blue','Black'][vid%3],4 if vid%3 else 6])
 insert('insurance_policy',[vid,plate,'2026-01-01', '2026-11-10' if vid<=3 else '2027-01-01'])
for did in range(1,9):
 for day in range(1,21):
  for start,end in [(6,13),(14,23)]:insert('driver_shift',[did,f'2026-10-{day:02} {start:02}:00:00',f'2026-10-{day:02} {end:02}:00:00'])
states=['COMPLETED']*130+['CANCELLED']*30+['ASSIGNED']*20+['IN_PROGRESS']*10+['REQUESTED']*10
r.shuffle(states)
for tid,state in enumerate(states,1):
 day=(tid-1)//10+1; tm=dt.datetime(2026,10,day,8+(tid%10),tid%50)
 plate,did=vehicles[(tid-1)%len(vehicles)]
 est=round(r.uniform(18,95),2); km=round(r.uniform(3,25),2)
 insert('trip',[tid,r.choice([1]+list(range(101,126))),None,tm,None,r.choice(['Central','North','East','West']),r.choice(['Airport','Station','South']),r.choice(['STANDARD','COMFORT']),km,est,'REQUESTED'])
 if state!='REQUESTED' and not(state=='CANCELLED' and tid%2==0):lines.append(f'CALL assign_trip({tid},{did},{q(plate)});')
 if state in ['IN_PROGRESS','COMPLETED']:
  lines.append(f'CALL start_trip({tid},{q(tm+dt.timedelta(minutes=8))});')
 if state=='COMPLETED':
  base=round(est*r.uniform(.8,1.2),2);tip=r.choice([0,0,0,2,5]);extra=r.choice([0,0,0,4,8])
  lines.append(f'CALL complete_trip({tid},{q(tm+dt.timedelta(minutes=35))},{base},{tip},{round(km*r.uniform(.9,1.2),2)},{extra});')
  if tid%4:
   insert('review',[tid,r.randint(65,100),'Synthetic passenger feedback',r.randint(70,100) if tid%3 else None,'Synthetic driver feedback' if tid%3 else None])
 if state=='CANCELLED':lines.append(f'CALL cancel_trip({tid},{q(tm+dt.timedelta(minutes=4))},{q(r.choice(["Plans changed","Waiting time","Wrong pickup"]))});')
(root/'sql/03_seed.sql').write_text('\n'.join(lines)+'\n')
(root/'results/data_generation.json').write_text(json.dumps({'seed':20261118,'synthetic':True,'trips':200,'window':'2026-10-01 through 2026-10-20','states':{s:states.count(s) for s in sorted(set(states))}},indent=2))
