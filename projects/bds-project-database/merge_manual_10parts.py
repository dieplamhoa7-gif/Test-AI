import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
records=[]; reviews=[]; summary=[]
for i in range(1,11):
    p=BASE/'manual_10parts'/f'part_{i:02d}_records.json'
    d=json.loads(p.read_text(encoding='utf-8'))
    records+=d['records']; reviews+= [{**r,'part':i} for r in d['review']]
    summary.append({'part':i,'records':len(d['records']),'review':len(d['review']),'merged':sum(1 for r in d['records'] if r['update_count']>1),'financial':sum(1 for r in d['records'] if r['financial_items'])})
final={'records':records,'review':reviews,'summary':summary}
(BASE/'manual_10parts_final_database.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'web'/'manual_10parts_final_database.js').write_text('window.MANUAL_10PARTS_DB = '+json.dumps(final,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('records',len(records),'review',len(reviews),'merged',sum(1 for r in records if r['update_count']>1),'financial',sum(1 for r in records if r['financial_items']))
for s in summary: print(s)
