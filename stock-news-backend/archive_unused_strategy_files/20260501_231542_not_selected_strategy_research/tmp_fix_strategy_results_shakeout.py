import json
from pathlib import Path
p=Path('data/strategy_results_cache.json')
d=json.loads(p.read_text(encoding='utf-8'))
for st in d.get('strategies',[]):
    if st.get('id')=='shakeout_breakdown_rebound':
        st['buy']=[]
        st['watchlist']=[]
        st['rejectCount']=20
        st['note']='Rechecked with real shakeout logic on 2026-05-01: first 20 symbols all rejected before API rate limit; previous many BUY/WATCH were wrong mapping to V3 Plus6 Focused.'
d['note']='Current strategy signal cache; web reads this output only. Shakeout fixed to real shakeout logic, not V3 Plus6.'
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print('updated shakeout empty')
