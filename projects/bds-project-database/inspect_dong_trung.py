from pathlib import Path
import json
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))
r=next(x for x in rows if x.get('project_name')=='Đông Trung')
for k,v in r.items():
 if v: print(f'\n## {k}\n{v}')
