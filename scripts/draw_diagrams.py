"""Editable diagrams.net + SVG + vector PDF from a shared geometry model."""
from pathlib import Path
import math,html,xml.etree.ElementTree as ET,csv
import fitz
R=Path(__file__).resolve().parents[1];F=R/'figures';F.mkdir(exist_ok=True)
BLUE='#245776';PALE='#edf4f8';INK='#253643';GRAY='#7a8791'
class Canvas:
 def __init__(self,name,w,h,title):
  self.name=name;self.w=w;self.h=h;self.nodes=[];self.edges=[];self.n=0
  self.text(w/2,35,title,30,bold=True)
 def node(self,key,x,y,w,h,label,kind='rect',font=23,fill='white',stroke=INK,bold=False,under=False,dashed=False,double=False):
  self.nodes.append(dict(key=key,x=x,y=y,w=w,h=h,label=label,kind=kind,font=font,fill=fill,stroke=stroke,bold=bold,under=under,dashed=dashed,double=double));return key
 def text(self,x,y,label,font=20,bold=False):
  self.n+=1;return self.node('text'+str(self.n),x,y,max(30,max(map(len,label.split('\n')))*font*.57),font*1.35*len(label.split('\n')),label,'text',font,'none','none',bold)
 def get(self,k):return next(n for n in self.nodes if n['key']==k)
 def point(self,k,side):
  offset=0
  if isinstance(side,tuple):side,offset=side
  n=self.get(k);return (n['x']+(offset if side in ['t','b'] else 0)+{'l':-n['w']/2,'r':n['w']/2}.get(side,0),n['y']+(offset if side in ['l','r'] else 0)+{'t':-n['h']/2,'b':n['h']/2}.get(side,0))
 def line(self,pts,color=INK,width=2,dash=False):
  if dash:
   for a,b in zip(pts,pts[1:]):
    length=math.hypot(b[0]-a[0],b[1]-a[1])
    for i in range(0,int(length),12):
     j=min(i+7,length)
     self.edges.append(([(a[0]+(b[0]-a[0])*v/length,a[1]+(b[1]-a[1])*v/length) for v in [i,j]],color,width,False))
  else:self.edges.append((pts,color,width,dash))
 def mark(self,p,q,card):
  dx=q[0]-p[0];dy=q[1]-p[1];l=math.hypot(dx,dy);ux,uy=dx/l,dy/l;vx,vy=-uy,ux
  def pt(a,b=0):return(p[0]+ux*a+vx*b,p[1]+uy*a+vy*b)
  if card.endswith('N'):
   self.line([pt(0,-10),pt(16),pt(0,10)]);self.line([pt(0),pt(16)])
  else:self.line([pt(9,-10),pt(9,10)])
  if card.startswith('0'):
   self.n+=1;xx,yy=pt(30);self.node('mark'+str(self.n),xx,yy,15,15,'','oval',14,'white',INK)
  else:self.line([pt(27,-10),pt(27,10)])
 def edge(self,a,aside,b,bside,acard=None,bcard=None,via=None):
  pts=[self.point(a,aside)]+(via or [])+[self.point(b,bside)];pts=[v for j,v in enumerate(pts) if j==0 or v!=pts[j-1]];self.line(pts)
  if acard:self.mark(pts[0],pts[1],acard)
  if bcard:self.mark(pts[-1],pts[-2],bcard)
 def attribute(self,entity,key,x,y,label,under=False,partial=False):
  w=max(140,len(label)*12+30);self.node(key,x,y,w,52,label,'oval',21,under=under,dashed=False)
  n=self.get(entity);dx=n['x']-x;dy=n['y']-y;ratio=1/math.sqrt((dx/(w/2))**2+(dy/26)**2)
  a=(x+dx*ratio,y+dy*ratio)
  scale=min((n['w']/2)/abs(dx) if dx else 1e9,(n['h']/2)/abs(dy) if dy else 1e9)
  b=(n['x']-dx*scale,n['y']-dy*scale);self.line([a,b],width=1.5)
  if partial:self.line([(x-w*.32,y+15),(x+w*.32,y+15)],width=1.5,dash=True)
 def export(self,a3=True):
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>']
  mx=ET.Element('mxfile',host='app.diagrams.net',version='24.7.17');dg=ET.SubElement(mx,'diagram',name=self.name,id=self.name);model=ET.SubElement(dg,'mxGraphModel',page='1',pageWidth=str(self.w),pageHeight=str(self.h),grid='1');root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
  for j,(pts,color,width,dash) in enumerate(self.edges):
   svg.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
   cell=ET.SubElement(root,'mxCell',id='edge'+str(j),edge='1',parent='1',style=f'endArrow=none;startArrow=none;strokeColor={color};strokeWidth={width};'+('dashed=1;' if dash else ''))
   geo=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'});ET.SubElement(geo,'mxPoint',x=str(pts[0][0]),y=str(pts[0][1]),attrib={'as':'sourcePoint'});ET.SubElement(geo,'mxPoint',x=str(pts[-1][0]),y=str(pts[-1][1]),attrib={'as':'targetPoint'})
   if len(pts)>2:
    arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
    for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
  for n in self.nodes:
   x,y,w,h=n['x'],n['y'],n['w'],n['h'];kind=n['kind'];style=f'fill="{n["fill"]}" stroke="{n["stroke"]}" stroke-width="2"'+(' stroke-dasharray="8 5"' if n['dashed'] else '')
   if kind=='rect':svg.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" {style}/>')
   elif kind=='oval':svg.append(f'<ellipse cx="{x}" cy="{y}" rx="{w/2}" ry="{h/2}" {style}/>')
   elif kind=='diamond':svg.append(f'<polygon points="{x-w/2},{y} {x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}" {style}/>')
   if n['double']:
    if kind=='rect':svg.append(f'<rect x="{x-w/2+6}" y="{y-h/2+6}" width="{w-12}" height="{h-12}" fill="none" stroke="{n["stroke"]}" stroke-width="2"/>')
    elif kind=='diamond':svg.append(f'<polygon points="{x-w/2+7},{y} {x},{y-h/2+7} {x+w/2-7},{y} {x},{y+h/2-7} {x-w/2+7},{y}" fill="none" stroke="{n["stroke"]}" stroke-width="2"/>')
   lines=n['label'].split('\n');font=n['font'];base=y-(len(lines)-1)*font*.62+font*.34
   for k,l in enumerate(lines):
    if n['under']:
     tw=len(l)*font*.52
     svg.append(f'<line x1="{x-tw/2}" y1="{base+k*font*1.24+4}" x2="{x+tw/2}" y2="{base+k*font*1.24+4}" stroke="{INK}" stroke-width="1.5"/>')
    svg.append(f'<text x="{x}" y="{base+k*font*1.24}" text-anchor="middle" font-family="Helvetica" font-size="{font}" fill="{INK}"'+(' font-weight="bold"' if n['bold'] else '')+(' text-decoration="underline"' if n['under'] else '')+'>'+html.escape(l)+'</text>')
   shape={'rect':'rounded=0','oval':'ellipse','diamond':'rhombus','text':'text'}[kind]
   flags=(1 if n['bold'] else 0)+(4 if n['under'] else 0)
   st=f'{shape};html=1;whiteSpace=wrap;align=center;verticalAlign=middle;fillColor={n["fill"]};strokeColor={n["stroke"]};fontFamily=Helvetica;fontSize={font};fontStyle={flags};strokeWidth=2;'+('dashed=1;' if n['dashed'] else '')
   c=ET.SubElement(root,'mxCell',id=n['key'],value=html.escape(n['label']).replace('\n','<br>'),vertex='1',parent='1',style=st);ET.SubElement(c,'mxGeometry',x=str(x-w/2),y=str(y-h/2),width=str(w),height=str(h),attrib={'as':'geometry'})
   if n['double']:
    inner=ET.SubElement(root,'mxCell',id=n['key']+'_inner',value='',vertex='1',parent='1',style=f'{shape};fillColor=none;strokeColor={n["stroke"]};strokeWidth=2;');ET.SubElement(inner,'mxGeometry',x=str(x-w/2+6),y=str(y-h/2+6),width=str(w-12),height=str(h-12),attrib={'as':'geometry'})
  svg.append('</svg>');s='\n'.join(svg);(F/(self.name+'.svg')).write_text(s);ET.ElementTree(mx).write(F/(self.name+'.drawio'),encoding='utf-8',xml_declaration=True)
  doc=fitz.open('svg',s.encode());v=fitz.open('pdf',doc.convert_to_pdf());out=fitz.open();p=out.new_page(width=1190.55 if a3 else 841.89,height=841.89 if a3 else 595.28);p.show_pdf_page(fitz.Rect(18,18,p.rect.width-18,p.rect.height-18),v,0);out.save(F/(self.name+'.pdf'));p.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(F/(self.name+'.png'))
# Function architecture: original categories retained; database scope is explicit.
for name,title,groups in [
 ('01_frontend','Front-end functional structure',[
 ('Passenger',[('Registration and profile',False),('Request, cancel and track trips',False),('Driver and vehicle information',False),('Fare details and passenger feedback',False),('Login / payment / live navigation',True)]),
 ('Driver',[('Registration and profile',False),('Assignment, start and completion',False),('Passenger and trip information',False),('Fare summary and driver feedback',False),('Login / route guidance',True)])]),
 ('02_backend','Back-office functional structure',[
 ('Identity and assets',[('User and driver records',False),('Driver eligibility review',True),('Vehicles and insurance records',False)]),
 ('Operations',[('Trip assignment and status',False),('Driver shift records',False),('Orders and bilateral reviews',False)]),
 ('Finance and location',[('Fare components and summaries',False),('Payments and settlement',True),('Real-time map services',True)])])]:
  c=Canvas(name,1400,900,title);c.node('root',700,130,360,65,'User-facing services' if name.startswith('01') else 'Back-office services',fill=PALE,bold=True)
  xs=[350,1050] if len(groups)==2 else [240,700,1160]
  for gi,((label,items),x) in enumerate(zip(groups,xs)):
   g='g'+str(gi);c.node(g,x,270,350,60,label,fill=PALE,bold=True);c.edge('root','b',g,'t',via=[(700,205),(x,205)])
   for j,(label,future) in enumerate(items):
    k=f'{g}_{j}';y=380+j*85;c.node(k,x,y,350,62,label,font=20,fill='#f4f4f4' if future else 'white',stroke=GRAY if future else BLUE,dashed=future)
    c.edge(g,'b',k,'l',via=[(x,315),(x-195,315),(x-195,y)])
  c.text(700,815,'Solid: database-supported functions. Gray: external or future services.',22)
  c.text(700,853,'Functional decomposition only; a working graphical application is not claimed.',20)
  c.export(False)
# Complete Chen/EER model: every non-inherited conceptual attribute is shown.
c=Canvas('03_chen_eer',2500,1900,'Complete conceptual ER/EER model')
entities=[('u',400,220,'APP USER',False),('p',150,650,'PASSENGER',False),('d',700,650,'DRIVER',False),('v',1150,650,'VEHICLE',False),('i',1150,220,'INSURANCE',False),('h',700,1250,'DRIVER SHIFT',True),('t',1850,650,'TRIP',False),('c',1500,1250,'COMPLETED TRIP',False),('x',2200,1250,'CANCELLED TRIP',False),('r',1150,1510,'REVIEW',True),('s',1750,1510,'SURCHARGE',True)]
for k,x,y,label,weak in entities:c.node(k,x,y,220,70,label,font=23,double=weak,fill='white')
attrs={
'u':[(110,100,'user_id',True),(400,80,'full_name',False),(690,100,'phone [UQ]',False),(120,340,'email',False),(680,340,'birth_date',False)],
'p':[(150,810,'tier',False)],
'd':[(560,820,'license_no [UQ]',False),(830,820,'lifetime_km',False)],
'v':[(1030,510,'plate',True),(1280,510,'model',False),(1030,810,'color',False),(1280,810,'capacity',False)],
'i':[(930,80,'policy_id',True),(1150,80,'valid_from',False),(1380,80,'valid_to',False)],
'h':[(550,1430,'shift_start',False),(850,1430,'shift_end',False)],
 't':[(1540,430,'trip_id',True),(1650,290,'requested_at',False),(1850,250,'started_at',False),(2050,290,'origin_zone',False),(2230,430,'destination_zone',False),(2320,650,'service_type',False),(2220,830,'estimated_km',False),(2080,960,'estimated_fare',False),(1750,960,'status',False)],
'c':[(1230,1110,'ended_at',False),(1460,1080,'base_fare',False),(1770,1360,'tip',False),(1760,1250,'actual_km',False)],
'x':[(2080,1440,'cancelled_at',False),(2320,1440,'reason',False)],
'r':[(900,1510,'passenger_score',False),(910,1660,'passenger_comment',False),(1180,1690,'driver_score',False),(1450,1660,'driver_comment',False)],
's':[(1750,1680,'amount',False)]}
for entity,items in attrs.items():
 for j,(x,y,label,key) in enumerate(items):c.attribute(entity,f'a_{entity}_{j}',x,y,label,key,entity=='h' and j==0)
# EER specialization: single parent line denotes partial; o/d circle denotes overlap/disjoint.
c.node('o',400,430,58,58,'o','oval',28);c.edge('u','b','o','t');c.edge('o','l','p','t',via=[(150,430)]);c.edge('o','r','d','t',via=[(700,430)])
c.text(400,515,'partial, overlapping',22)
c.node('dis',1850,1100,58,58,'d','oval',28);c.edge('t','b','dis','t');c.edge('dis','l','c','t',via=[(1500,1160)]);c.edge('dis','r','x','t',via=[(2200,1100)])
c.text(2070,1060,'partial, disjoint',22)
# Binary relationships with endpoint cardinalities, matching LN3's min/max glyphs.
for key,x,y,l,ident in [('owns',925,650,'Owns',False),('covers',1150,400,'Covers',False),('logs',700,1040,'Logs',True),('serves',1500,650,'Serves',False),('requests',1400,920,'Requests',False),('reviewrel',1340,1400,'Receives',True),('surrel',1630,1400,'Has',True)]:c.node(key,x,y,155,80,l,'diamond',22,double=ident)
c.edge('d','r','owns','l','1');c.edge('owns','r','v','l',None,'0N')
c.edge('v','t','covers','b','1');c.edge('covers','t','i','b',None,'0N')
c.edge('d','b','logs','t','1',via=[(700,720),(700,970)]);c.edge('logs','b','h','t',None,'0N')
c.edge('v','r','serves','l','01');c.edge('serves','r','t','l',None,'0N')
c.edge('p','r','requests','l','1',via=[(310,650),(310,920)])
c.edge('requests','r','t',('l',25),None,'0N',via=[(1580,920),(1580,675)])
c.edge('c','l','reviewrel','t','1',via=[(1390,1250),(1340,1250)])
c.edge('reviewrel','l','r','t',None,'01',via=[(1150,1400)])
c.edge('c','b','surrel','t','1',via=[(1500,1330),(1630,1330)])
c.edge('surrel','r','s','t',None,'01',via=[(1750,1400)])
c.text(1250,1790,'Rectangle: entity | double rectangle: weak entity | ellipse: attribute | underlined: identifier | [UQ]: alternate unique key',22)
c.text(1250,1830,'Diamond: relationship | double diamond: identifying relationship | dashed underline: partial key | o: overlap | d: disjoint',22)
c.text(1250,1870,'Single supertype line: partial specialization. Role and outcome keys are inherited; foreign keys appear in the relational diagram.',21)
c.export(True)
# Relational diagram generated from the executed column dictionary.
meta=list(csv.DictReader((R/'results/data_dictionary.tsv').read_text().splitlines(),delimiter='\t'))
c=Canvas('04_relational',2450,1700,'Relational schema with attributes, keys and cardinalities')
positions={'app_user':(260,280),'passenger':(780,180),'driver':(780,580),'vehicle':(1290,580),'insurance_policy':(1840,580),'driver_shift':(780,1120),'trip':(1840,1120),'completed_trip':(1290,1420),'cancelled_trip':(2250,1430),'review':(260,1400),'surcharge':(260,1020)}
# Keep boxes within canvas: cancelled at right is slightly narrower.
fks={'passenger':['passenger_id'],'driver':['driver_id'],'vehicle':['driver_id'],'insurance_policy':['plate'],'driver_shift':['driver_id'],'trip':['passenger_id','plate'],'completed_trip':['trip_id'],'cancelled_trip':['trip_id'],'review':['trip_id'],'surcharge':['trip_id']}
heights={}
for tab,(x,y) in positions.items():
 rows=[r for r in meta if r['TABLE_NAME']==tab];w=380 if tab!='cancelled_trip' else 360;h=55+len(rows)*34;heights[tab]=h
 c.node(tab,x,y,w,h,'',fill='white',stroke=BLUE)
 c.node(tab+'_head',x,y-h/2+26,w,52,tab,font=24,fill=PALE,stroke=BLUE,bold=True)
 for j,r in enumerate(rows):
  tags=[]
  if r['COLUMN_KEY']=='PRI':tags.append('PK')
  if r['COLUMN_NAME'] in fks.get(tab,[]):tags.append('FK')
  if r['COLUMN_KEY']=='UNI':tags.append('UQ')
  flag='/'.join(tags) or '-';label=f"{flag:5} {r['COLUMN_NAME']}"+(' ?' if r['IS_NULLABLE']=='YES' else '')
  c.text(x,y-h/2+73+j*34,label,21)
# Contacts at box boundaries. Cardinality is relationship-specific; table columns show FK locations.
c.edge('app_user','r','passenger','l','1','01',via=[(500,280),(500,180)])
c.edge('app_user','b','driver','l','1','01',via=[(260,580)])
c.edge('driver','r','vehicle','l','1','0N')
c.edge('vehicle','r','insurance_policy','l','1','0N')
c.edge('driver','b','driver_shift','t','1','0N')
c.edge('passenger','r','trip','t','1','0N',via=[(2050,180),(2050,820),(1840,820)])
c.edge('vehicle','b','trip','l','01','0N',via=[(1290,1120)])
c.edge('trip','b','completed_trip','r','1','01',via=[(1840,1420)])
c.edge('trip','r','cancelled_trip','t','1','01',via=[(2250,1120)])
c.edge('completed_trip','l','review','r','1','01',via=[(1010,1420),(1010,1540),(510,1540),(510,1400)])
c.edge('completed_trip','t','surcharge','r','1','01',via=[(1290,1280),(1040,1280),(1040,1020)])
c.text(1225,1635,'PK = primary key; FK = foreign key; UQ = alternate unique key; ? = nullable. All columns shown; SQL types are in the data dictionary.',23)
c.text(1225,1675,'Endpoint notation: || exactly one; circle + bar zero or one; circle + crow foot zero or many. State-dependent constraints also apply.',22)
c.export(True)
print('Created four diagrams in SVG, PDF, PNG and editable diagrams.net format.')
