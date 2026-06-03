import json
from pathlib import Path
p=Path('data/lh1_v3_ml_probability_gate_research.json')
o=json.loads(p.read_text(encoding='utf-8'))
print('baseline',json.dumps(o['baselineAll'],ensure_ascii=False))
for i,r in enumerate(o['topRuns'][:10],1):
 print('\nRANK',i,r['family'],r['model'],r['mode'],'score',r['score'])
 print('overall',json.dumps(r['overall'],ensure_ascii=False))
 for sp in r['splits']:
  print(' ',sp['split'],'th',sp['threshold'],'train',sp['trainStats'],'test',sp['testStats'],'featN',sp['featureCount'])
