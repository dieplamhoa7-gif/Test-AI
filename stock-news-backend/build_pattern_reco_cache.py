from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pattern_engine_v2.analyze import analyze
ROOT=Path(__file__).resolve().parent
CHART_DIR=ROOT/'firebase_public'/'data'/'charts'
OUT=ROOT/'firebase_public'/'data'/'pattern_reco_cache.json'
TZ=timezone(timedelta(hours=7))
market=json.loads((ROOT/'firebase_public'/'data'/'market_data.json').read_text(encoding='utf-8'))
symbols=[str(x.get('symbol') or x.get('ticker') or '').upper() for x in market.get('items',[])]
items=[]; errors=[]
for i,s in enumerate(symbols,1):
    p=CHART_DIR/f'{s}_day.json'
    if not p.exists():
        p=CHART_DIR/f'{s}_auto_chart_day.json'
    try:
        r=analyze(p,symbol=s,include_experimental=True)
        pats=[{k:v for k,v in ptn.items() if not k.startswith('_')} for ptn in (r.get('patterns') or [])]
        items.append({'symbol':s,'timeframe':r.get('timeframe'),'bars':r.get('bars'),'period':r.get('period'),'lastClose':r.get('lastClose'),'summary':r.get('summary'),'patterns':pats[:40],'patternCount':len(pats)})
    except Exception as e:
        errors.append({'symbol':s,'error':repr(e)})
    if i%10==0: print('processed',i,'/',len(symbols),flush=True)
payload={'source':'pattern_engine_v2','updatedAt':datetime.now(TZ).isoformat(timespec='seconds'),'count':len(items),'errorCount':len(errors),'items':items,'errors':errors[:50]}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps({'output':str(OUT),'count':len(items),'errors':len(errors)},ensure_ascii=False))
