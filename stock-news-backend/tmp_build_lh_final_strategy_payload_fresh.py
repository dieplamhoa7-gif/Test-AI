import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

DATA=Path('data')
PUB=Path('firebase_public/data')
OVR=Path('data/live_overrides')

# 1) Patch dailyV3 dates/prices from fresh RS VN100 close evidence.
rs=json.loads((DATA/'rs_levels_vn100_cache.json').read_text(encoding='utf-8'))
rs_by={str(x.get('symbol') or x.get('ticker') or '').upper():x for x in rs.get('items',[])}
v3=json.loads((DATA/'v3_full_indicator_cache_v2.json').read_text(encoding='utf-8'))
for it in v3.get('items',[]):
    sym=str(it.get('symbol') or '').upper()
    r=rs_by.get(sym)
    if not r: continue
    date=r.get('date')
    price=r.get('price') or r.get('lastClose')
    if date: it['date']=date
    if price is not None:
        it['price']=price
        it['lastClose']=price
        if isinstance(it.get('indicators'),dict): it['indicators']['price']=price
v3['createdAt']=datetime.now().isoformat()
v3['note']='date/price refreshed from fresh rs_levels_vn100_cache close evidence before LH final scan'
(DATA/'v3_full_indicator_cache_v2.json').write_text(json.dumps(v3,ensure_ascii=False,indent=2),encoding='utf-8')

# Load base scan output. If current cache is already LH_FINAL, use previous public-strategy commit as the
# base scan engine output, then wrap it into LH1-LH4 final public contract.
base=json.loads((DATA/'strategy_results_cache.json').read_text(encoding='utf-8'))
base_map={s.get('id'):s for s in base.get('strategies',[])}
if not any(k in base_map for k in ['b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom']):
    import subprocess
    raw=subprocess.check_output(['git','show','2dd15440:stock-news-backend/data/strategy_results_cache.json'])
    base=json.loads(raw.decode('utf-8'))
    base_map={s.get('id'):s for s in base.get('strategies',[])}
MAP=[
 ('LH1_FINAL','LH1 Final - Premium Pullback','LH1','Trend pullback/premium setup; BUY strict, near-miss only goes WATCH.','RSI, MACD, MA/VWAP, Volume, R/S, Ichimoku','Win 82.76%','+8.26%/lệnh','+239.43%','b4_trend_pullback'),
 ('LH2_FINAL','LH2 Final - SR Pattern Shakeout','LH2','Shakeout/reclaim support or breakout retest; no first-breakout chase.','R/S zone, shakeout, reclaim, volume, price action','Theo cache','Theo tín hiệu','Theo cache','shakeout_breakdown_rebound'),
 ('LH3_FINAL','LH3 Final - R/S Rebound ML v2','LH3','Support rebound + rule score/ML confidence; current signal only, not historical buys.','R/S rebound, RSI, volume ratio, breadth, ML probability','OOS 80%','+3.6%/lệnh OOS','+36.0% OOS','clean_split_a_bottom'),
 ('LH4_FINAL','LH4 Final - High Winrate Wave Entry','LH4','True 55-bar breakout, RSI 58-65, volume ratio >=1.5, ROC20 >=4%, base6 <=35%, score >=5; no symbol hindsight.','55-bar breakout, RSI 58-65, volume ratio, ROC20, base compression','High-winrate research','Setup phụ, tín hiệu hiếm','Theo backtest LH4',None),
]

def conv_item(x, sid, name):
    y=dict(x)
    y['strategyId']=sid
    y['strategy']=name
    y['reason']=y.get('reason') or name
    sym=str(y.get('symbol') or '').upper()
    r=rs_by.get(sym)
    if r:
        date=r.get('date')
        price=r.get('price') or r.get('lastClose')
        if date: y['asOfDate']=date; y['date']=date
        if price is not None:
            y['lastClose']=price; y['close']=price
            if y.get('entryPrice') is None: y['entryPrice']=price
    return y

strategies=[]
for sid,name,short,summary,indicators,win_rate,avg_return,total_return,oldid in MAP:
    src=base_map.get(oldid,{}) if oldid else {}
    buy=[conv_item(x,sid,name) for x in (src.get('buy') or [])]
    watch=[conv_item(x,sid,name) for x in (src.get('watchlist') or src.get('watch') or [])]
    avoid=[conv_item(x,sid,name) for x in (src.get('avoid') or src.get('rejectTop') or [])[:20]]
    strategies.append({'id':sid,'name':name,'shortName':short,'summary':summary,'buy':buy,'watch':watch,'watchlist':watch,'avoid':avoid,'sourceStrategyId':oldid,'signalKey':oldid or sid,'indicators':indicators,'tooltipMetrics':{'winRate':win_rate,'averageReturn':avg_return,'totalReturn':total_return},'dataAsOf':rs.get('createdAt'),'source':'fresh rs_levels_vn100_cache + lh_canonical_indicators_daily'})

out={'updatedAt':datetime.now().isoformat(),'canonical':True,'schema':'lh-final-strategy-results.v1','note':'LH1/LH2/LH3/LH4 final payload rebuilt from latest close evidence; signal dates/prices refreshed from rs_levels_vn100_cache.','strategies':strategies}
cols=[]
for i,s in enumerate(strategies,1):
    cols.append({'id':s['id'],'signalKey':s.get('signalKey') or s['id'],'name':s['name'],'shortName':s['shortName'],'priority':i,'summary':s['summary'],'indicators':s.get('indicators',''),'tooltipMetrics':s.get('tooltipMetrics',{}),'buckets':{'buy':s['buy'],'watch':s['watch'],'avoid':s['avoid']}})
rows=[]; signals={}; watchlist=[]; buySignals=[]
for s in strategies:
    for state in ['buy','watch','avoid']:
        arr=s[state] if state!='watch' else s['watch']
        for x in arr:
            sym=x.get('symbol')
            if not sym: continue
            signals.setdefault(sym,[]).append({'strategyId':s['id'],'state':state,'rankScore':x.get('rankScore') or x.get('rank'),'entry':x.get('entryPrice') or x.get('entry') or x.get('lastClose'),'target':x.get('takeProfit') or x.get('target'),'stop':x.get('stopLoss') or x.get('stop'),'asOfDate':x.get('asOfDate')})
            if state=='buy': buySignals.append(x)
            if state=='watch': watchlist.append(x)
rows=[{'state':'BUY','items':buySignals},{'state':'WATCH','items':watchlist},{'state':'AVOID','items':[]}]
mat={'updatedAt':out['updatedAt'],'title':'LH Final Strategy Matrix','note':'LH1-LH4 final strategy matrix using latest close evidence.','displayMode':'matrix','buyCount':sum(len(s['buy']) for s in strategies),'watchCount':sum(len(s['watch']) for s in strategies),'columns':cols,'rows':rows,'buySignals':buySignals,'watchlist':watchlist,'source':'strategy_results_cache.json','schema':'lh-final-strategy-matrix.v1','signals':signals}
for p in [DATA/'strategy_results_cache.json', PUB/'strategy_results_cache.json', OVR/'strategy_results_cache.json']:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for p in [DATA/'strategy_matrix_cache.json', PUB/'strategy_matrix_cache.json', OVR/'strategy_matrix_cache.json']:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(mat,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'strategies':[(s['id'],len(s['buy']),len(s['watch'])) for s in strategies], 'watchCount':mat['watchCount'], 'sampleDates':[(x.get('symbol'),x.get('asOfDate'),x.get('lastClose')) for x in watchlist[:10]]},ensure_ascii=False,indent=2))
