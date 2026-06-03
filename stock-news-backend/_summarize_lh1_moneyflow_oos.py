import json
from pathlib import Path
p=Path('data/lh1_moneyflow_ml_oos_research.json')
o=json.loads(p.read_text(encoding='utf-8'))
print('baseline',json.dumps(o['baseline'],ensure_ascii=False))
for i,r in enumerate(o['topRuns'][:12],1):
 print('\nRANK',i,r['group'],r['model'],r['mode'])
 print('overall',json.dumps(r['overall'],ensure_ascii=False))
 for sp in r['splits']:
  print(' ',sp['split'],'th',sp['threshold'],'train',sp['trainStats'],'test',sp['testStats'])
