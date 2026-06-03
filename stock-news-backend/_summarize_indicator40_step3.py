import json
from pathlib import Path
p=Path('data/core12_step3_combo_5to8_from_step2_precision_first_rs_d1a_d1s_fast.json')
o=json.loads(p.read_text(encoding='utf-8'))
sel=o.get('selectedByTask',{})
for task, arr in sel.items():
 print('\nTASK',task)
 for i,r in enumerate(arr[:10],1):
  print(i,'families=',r.get('families'),'model=',r.get('model'),'avgP=',r.get('avgPrecision'),'minP=',r.get('minPrecision'),'avgR=',r.get('avgRecall'),'pred=',r.get('totalPredN'),'pass70=',r.get('passP70'))
  print('  sets=',r.get('setNames'))
