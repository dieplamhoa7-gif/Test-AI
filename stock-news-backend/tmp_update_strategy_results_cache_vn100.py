import json
from pathlib import Path
src=Path('data/three_strategies_vn100_cache_signals.json')
out=Path('data/strategy_results_cache.json')
d=json.loads(src.read_text(encoding='utf-8'))
name_map={'b4_trend_pullback':'Trend Pullback Pro','clean_split_a_bottom':'Support Rebound Hunter','shakeout_breakdown_rebound':'Shakeout Rebound'}
payload={'updatedAt':d.get('createdAt'),'note':'Current strategy signal cache refreshed from VN100 cache scan. Source: data/three_strategies_vn100_cache_signals.json. Web reads output only.','strategies':[]}
for sid in ['b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom']:
    st=d['strategies'][sid]
    payload['strategies'].append({'id':sid,'name':name_map[sid],'buy':st.get('buy',[]),'watchlist':st.get('watchlist',[]),'rejectCount':len(st.get('rejects',[])),'source':str(src)})
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print([(s['id'], [x['symbol'] for x in s['buy']], [x['symbol'] for x in s['watchlist']]) for s in payload['strategies']])
