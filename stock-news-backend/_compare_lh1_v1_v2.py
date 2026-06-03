import json
from pathlib import Path
from collections import defaultdict
v1=json.loads(Path('data/lh1_canonical_t3_fee_2023_to_now.json').read_text(encoding='utf-8'))
v2=json.loads(Path('data/lh1_v2_ml_combo_2023_to_now.json').read_text(encoding='utf-8'))
print('V1 windows',json.dumps(v1['windows'],ensure_ascii=False,indent=2))
print('V2 windows',json.dumps(v2['windows'],ensure_ascii=False,indent=2))
print('V2 rejects top',list(v2.get('rejects',{}).items())[:30])
def bysym(o):
 d=defaultdict(list)
 for t in o['trades']: d[t['symbol']].append(t)
 rows=[]
 for s,ts in d.items():
  n=len(ts); w=sum(1 for t in ts if t['netPnlPct']>0); sm=sum(t['netPnlPct'] for t in ts)
  rows.append((s,n,w,round(w/n*100,2),round(sm/n,2),round(sm,2)))
 return rows
print('V2 by symbol')
for row in sorted(bysym(v2), key=lambda x:x[-1], reverse=True): print(row)
