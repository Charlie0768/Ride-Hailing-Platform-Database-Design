from pathlib import Path
import fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];qa=R/'build/qa_final';qa.mkdir(exist_ok=True)
for lang in ['en','zh']:
 d=fitz.open(R/f'report_{lang}.pdf')
 assert len(d)>=25
 assert 'Group G6' in d[0].get_text() and 'Lin Shuaiyu' in d[0].get_text()
 for i,p in enumerate(d):
  pix=p.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False);pix.save(qa/f'{lang}-{i+1:02}.png')
 for start in range(0,len(d),4):
  sheet=Image.new('RGB',(1200,1700),'#dddddd');dr=ImageDraw.Draw(sheet)
  for j in range(start,min(start+4,len(d))):
   im=Image.open(qa/f'{lang}-{j+1:02}.png');im.thumbnail((590,815));x=(j-start)%2*600;y=(j-start)//2*850
   sheet.paste(im,(x,y+25));dr.text((x+8,y+5),f'{lang} page {j+1}',fill='black')
  sheet.save(qa/f'{lang}-sheet-{start//4+1}.png')
 print(lang,len(d),'cover verified; all pages rendered')
