import json
from pathlib import Path
p=Path('data/lh1_moneyflow_ml_is_only_research.json')
o=json.loads(p.read_text(encoding='utf-8'))
print('baseline',json.dumps(o['baseline'],ensure_ascii=False))
for i,r in enumerate(o['topRuns'][:12],1):
 print('\nRANK',i,r['group'],r['model'],r['mode'],'th',r['threshold'])
 print('overall',json.dumps(r['overall'],ensure_ascii=False))
 print('featureCount',r['featureCount'])
 print('features',r['features'][:30])
