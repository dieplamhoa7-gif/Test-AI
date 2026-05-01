import json
from pathlib import Path
src=Path('data/strategies_1_2_4_current_forecast.json')
out=Path('data/strategy_results_cache.json')
d=json.loads(src.read_text(encoding='utf-8')) if src.exists() else {'createdAt':None,'strategies':{}}
strategies=d.get('strategies',{})

def item(x):
    return {
        'symbol': x.get('symbol'),
        'entryPrice': x.get('entryPrice'),
        'stopLoss': x.get('stopLoss'),
        'takeProfit': x.get('takeProfit'),
        'rankScore': x.get('rankScore'),
        'action': x.get('action'),
        'reason': x.get('reason'),
        'asOfDate': x.get('asOfDate'),
    }

payload={'updatedAt':d.get('createdAt'), 'note':'Current strategy signal cache; web reads this output only. Shakeout is NOT mapped from V3 Plus6; it must come only from scan_shakeout_current_cache.py / _shakeout_candidate.', 'strategies':[]}
# Trend pullback
st=strategies.get('1_B4_Trend_Pullback',{})
payload['strategies'].append({'id':'b4_trend_pullback','name':'Trend Pullback Pro','buy':[item(x) for x in st.get('buy',[])],'watchlist':[item(x) for x in st.get('watchlist',[])],'rejectCount':len(st.get('rejects',[]))})
# Shakeout real-only
shake_path=Path('data/shakeout_rebound_current_signals.json')
if shake_path.exists():
    sh=json.loads(shake_path.read_text(encoding='utf-8'))
    shake_buy=[item(x) for x in sh.get('buy',[])]
    shake_watch=[item(x) for x in sh.get('watchlist',[])]
    shake_reject=len(sh.get('rejects',[]))
else:
    shake_buy=[]; shake_watch=[]; shake_reject=0
payload['strategies'].append({'id':'shakeout_breakdown_rebound','name':'Shakeout Rebound','buy':shake_buy,'watchlist':shake_watch,'rejectCount':shake_reject,'note':'Real shakeout only; never V3 Plus6.'})
# Support rebound
st=strategies.get('4_Clean_Split_A_Baseline',{})
payload['strategies'].append({'id':'clean_split_a_bottom','name':'Support Rebound Hunter','buy':[item(x) for x in st.get('buy',[])],'watchlist':[item(x) for x in st.get('watchlist',[])],'rejectCount':len(st.get('rejects',[]))})
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(out, [(s['id'], len(s['buy']), len(s['watchlist']), s['rejectCount']) for s in payload['strategies']])
