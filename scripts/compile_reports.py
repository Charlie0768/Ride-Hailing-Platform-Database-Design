"""Regenerate LaTeX from verified results and compile both PDFs."""
from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'scripts/build_reports.py')],check=True)
(root/'build').mkdir(exist_ok=True)
for lang in ['en','zh']:
 for _ in range(2):
  p=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(root/'build'),str(root/f'source/report_{lang}.tex')],capture_output=True,text=True,cwd=root)
  (root/f'build/xelatex_{lang}.txt').write_text(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError(f'Compile failed; see build/xelatex_{lang}.txt')
 log=(root/f'build/report_{lang}.log').read_text()
 if 'Overfull' in log or 'Missing character' in log:raise RuntimeError(f'Layout/font issue in {lang}; inspect log')
 shutil.copy2(root/f'build/report_{lang}.pdf',root/f'report_{lang}.pdf')
 print(root/f'report_{lang}.pdf')
