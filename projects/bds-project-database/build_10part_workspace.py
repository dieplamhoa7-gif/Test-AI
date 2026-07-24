import csv,json,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
SRC=BASE/'teams_project_review_with_dates.csv'
OUT=BASE/'manual_10parts'
OUT.mkdir(exist_ok=True)
rows=[]
with SRC.open(encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f):
        rows.append(r)
# keep original order, split into 10 near-equal parts
n=len(rows); size=math.ceil(n/10)
manifest=[]
for i in range(10):
    part=rows[i*size:(i+1)*size]
    p=OUT/f'part_{i+1:02d}.json'
    p.write_text(json.dumps(part,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest.append({'part':i+1,'file':str(p.relative_to(BASE)),'rows':len(part),'chunk_start':part[0]['chunk_id'] if part else None,'chunk_end':part[-1]['chunk_id'] if part else None,'status':'pending'})
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('rows',n,'parts',len(manifest))
for m in manifest: print(m)
