import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
js=BASE/'web/manual_records_merged_reports.js'
db=json.loads(js.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
items=sum(len(g.get('financial_items') or []) for g in db['groups'])
fin_groups=sum(1 for g in db['groups'] if g.get('financial_items'))
reports=sum(len(g.get('reports') or []) for g in db['groups'])
full_lens=[len(r.get('full_excerpt') or '') for g in db['groups'] for r in g.get('reports') or []]
assert db['totals']['groups']==len(db['groups'])==186
assert db['totals']['raw_records']==260
assert db['totals']['financial_items']==items==2164, (db['totals']['financial_items'], items)
assert db['totals']['financial_groups']==fin_groups==164, fin_groups
assert reports==260, reports
assert min(full_lens)>=0 and max(full_lens)>10000 and sum(full_lens)//len(full_lens)>2500
# A12/A14 scenario checks
g=next(g for g in db['groups'] if 'A12' in g['project_name'] and 'A14' in g['project_name'])
vals='\n'.join(x['label']+' '+x['value'] for x in g['financial_items'])
for needle in ['Giá đấu giá max: 290', '341tr/m2', '372tr/m2', '337 tr/m2', '358 tr/m2', 'LNTT/TMĐT: 40.2', 'LNTT/TMĐT: 28']:
    # tolerate normalized labels value without colon after parsing
    assert needle.replace(':','')[:12].lower() in vals.replace(':','').lower(), needle
assert len(g['financial_items'])>=12
# Report tabs/source fields present in frontend
ui=(BASE/'web/manual-database.js').read_text(encoding='utf-8')
for needle in ['reportTabs(g)', 'sourceText(r)', 'Diễn giải nguồn đầy đủ', 'hasImageMarker']:
    assert needle in ui, needle
print('VERIFY_OK')
print(json.dumps({'groups':len(db['groups']),'reports':reports,'financial_groups':fin_groups,'financial_items':items,'full_excerpt_avg':sum(full_lens)//len(full_lens),'full_excerpt_max':max(full_lens),'a12_a14_items':len(g['financial_items'])},ensure_ascii=False,indent=2))
