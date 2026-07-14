from pathlib import Path
from pattern_engine_v2.analyze import analyze
for sym in ['MWG','FPT','HPG','SSI','VCB']:
    p=Path('firebase_public/data/charts')/f'{sym}_auto_chart_day.json'
    if not p.exists(): continue
    r=analyze(p,symbol=sym,include_experimental=True)
    pats=[x for x in r.get('patterns',[]) if any(k in x.get('type','') for k in ['double','triple'])]
    print('\n',sym, len(pats))
    for x in pats[:8]:
        print(x['type'], x['direction'], x.get('score'), x.get('confidence'), x.get('status'), x.get('levels'), x.get('evidence',{}).get('notes'))
