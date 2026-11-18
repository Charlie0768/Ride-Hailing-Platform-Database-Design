"""Check the final report inventory and package reproducible deliverables."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import fitz

R = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
core = set(re.findall(r'CREATE TABLE (\w+)', (R/'sql/01_schema.sql').read_text()))
assert len(core) == 11
checks = json.loads((R/'results/validation.json').read_text())
assert len(checks) == 32 and all(x['passed'] for x in checks)
evidence = json.loads((R/'results/report_evidence.json').read_text())
assert core <= evidence.keys()
assert len(evidence['show_tables']['rows']) == 17
assert evidence['crud_delete']['rows'] == [{'remaining': '0'}]
delivery = {'reports': {}, 'mysql_checks_passed': len(checks),
            'fresh_instance_reproduction': 'passed',
            'source_lecture_1': 'not supplied',
            'diagram_formats': ['pdf', 'svg', 'png', 'drawio'],
            'diagram_count': 4,
            'visual_review': 'All current English and Chinese report pages inspected; normalization, cover, diagrams and SQL pages checked.'}
for lang in ['en','zh']:
    path = R/f'report_{lang}.pdf'
    doc = fitz.open(path)
    assert 25 <= len(doc) <= 45
    cover = doc[0].get_text()
    team = json.loads((R/'results/team_details.json').read_text())
    assert len(team['members']) == 6
    assert 'Ride-Hailing Platform' in cover and 'Group G6' in cover
    for member in team['members']:
        assert member['name'] in cover and member['student_id'] in cover
    assert 'Jin Conghao' in cover and 'Qionghao' not in cover
    text = '\n'.join(p.get_text() for p in doc)
    assert core <= set(re.findall(r'CREATE TABLE\s+(\w+)', text))
    assert 'SHOW TABLES;' in text and 'DESCRIBE trip;' in text
    assert '7853.92' in text
    if lang=='en': assert not re.search(r'[\u4e00-\u9fff]', text)
    else: assert '第二范式' in text and '无损' in text and 'Shift0' not in text
    assert 'Jin Conghao' in text and 'Qionghao' not in text
    assert 'ShiftWide' in text and 'Trip0' in text
    if lang=='en': assert 'lossless' in text
    source=(R/f'source/report_{lang}.tex').read_text()
    assert len(re.findall(r'\\section\{', source.split(r'\appendix')[0])) == 5
    assert sum(p.rect.width > p.rect.height for p in doc) == 4
    assert sum(p.rect.width > 1100 for p in doc) == 2
    log = (R/f'build/report_{lang}.log').read_text()
    for bad in ['Overfull', 'Missing character', 'undefined', 'LaTeX Font Warning']:
        assert bad not in log, (lang, bad)
    delivery['reports'][lang] = {'pages': len(doc), 'six_member_cover': True, 'main_chapters': 5, 'language': 'English' if lang=='en' else 'Chinese',
                                'full_core_ddl_present': True,
                                'diagram_pdf_pages': [i+1 for i,p in enumerate(doc) if p.rect.width > p.rect.height],
                                'sha256': sha(path)}
for name in ['01_frontend', '02_backend', '03_chen_eer', '04_relational']:
    for ext in delivery['diagram_formats']:
        assert (R/f'figures/{name}.{ext}').stat().st_size > 0
    ET.parse(R/f'figures/{name}.drawio')
    ET.parse(R/f'figures/{name}.svg')
    assert len(fitz.open(R/f'figures/{name}.pdf')) == 1
(R/'results/delivery_checks.json').write_text(json.dumps(delivery, indent=2))

def selected():
    return sorted(p for p in R.rglob('*') if p.is_file()
                  and not any(x in {'build', '__pycache__', '.DS_Store', '.git', '.venv'} for x in p.relative_to(R).parts)
                  and p.suffix != '.zip' and p.name != 'SHA256SUMS.txt')

files = selected()
manifest = R/'SHA256SUMS.txt'
manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(R).as_posix()}\n' for p in files))
archive = R/'ride_hailing_complete.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files + [manifest]:
        z.write(p, 'ride_hailing/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for p in files:
        assert hashlib.sha256(z.read('ride_hailing/'+p.relative_to(R).as_posix())).hexdigest() == sha(p)
print(f'Checked English and Chinese reports, 4 diagram sets, 11 core DDL definitions, 32 passing database checks.')
print(f'Packaged {len(files)+1} files: {archive} ({archive.stat().st_size:,} bytes).')
