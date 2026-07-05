# -*- coding: utf-8 -*-
import json
from pathlib import Path
p=Path('firebase_public/data/warrants_data.json')
data=json.loads(p.read_text(encoding='utf-8'))
items=data.get('items',[])
print('count', data.get('count'), 'updatedAt', data.get('updatedAt'), 'source', data.get('source'))
fields=['code','underlying','underlyingPrice','marketPrice','lastPrice','bid','ask','exercisePrice','conversionRatio','breakeven','daysLeft','leverage','intrinsicValue','timeValue','spreadPct','moneyness','advancedSignal','source']
for code in ['CFPT2601','CMWG2511','CHPG2523']:
    x=next((i for i in items if i.get('code')==code), None)
    print(code, {k:x.get(k) for k in fields} if x else None)
