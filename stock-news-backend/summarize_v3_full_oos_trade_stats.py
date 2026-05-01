from __future__ import annotations
import json, statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime

SRC=Path('data/v3_target6_partial_at6_exact_future_backtest.json')
FULL=Path('data/v3_full_indicator_cache_v2.json')
OUT=Path('data/v3_full_oos_trade_stats_entry_exit.json')

def f(v,d=None):
    try:
        if v is None: return d
        return float(v)
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def avg(xs):
    xs=[x for x in xs if x is not None]
    return round(sum(xs)/len(xs),3) if xs else None

def summ(ts):
    n=len(ts); w=[x for x in ts if f(x.get('pnlPct'),0)>0]; l=[x for x in ts if f(x.get('pnlPct'),0)<0]
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg([f(x.get('pnlPct')) for x in ts]),'sumPnlPct':round(sum(f(x.get('pnlPct'),0) for x in ts),2),'avgWinPct':avg([f(x.get('pnlPct')) for x in w]),'avgLossPct':avg([f(x.get('pnlPct')) for x in l]),'avgHoldSessions':avg([f(x.get('holdSessions')) for x in ts])}

def load_full_cache():
    if not FULL.exists(): return {}
    raw=json.load(open(FULL,encoding='utf-8'))
    if isinstance(raw,dict):
        if 'symbols' in raw and isinstance(raw['symbols'],dict): return raw['symbols']
        if 'data' in raw and isinstance(raw['data'],dict): return raw['data']
        return raw
    return {}

def pick_indicator(cache,sym):
    d=cache.get(sym) or {}
    if isinstance(d,list): d=d[-1] if d else {}
    return d if isinstance(d,dict) else {}

def flatten_ind(d):
    # Preserve the most useful full indicators; handles both flat and nested cache shapes.
    out={}
    keys=['close','rsi14','macdLine','macdSignal','macdHist','ret5','volumeRatio','adx14','plusDI','minusDI','ma20','ma50','ma200','bbPercent','vwap','roc20','effectiveTrend','signalScore','riskReward','activeSupportDay','activeResistanceDay','supportZoneDay','resistanceZoneDay']
    for k in keys:
        if k in d: out[k]=d.get(k)
    for nested in ['ichimoku','keltner','v3FullScore','bollinger','donchian','marketStructure','divergence']:
        if nested in d: out[nested]=d.get(nested)
    return out

def enrich_trade(t,full_cache):
    x=dict(t)
    fp=x.get('futurePath') or []
    x['entryPrice']=x.get('entry')
    x['sellPoint']={'exitDate':x.get('exitDate'),'outcome':x.get('outcome'),'pnlPct':x.get('pnlPct'),'partialTaken':x.get('partialTaken')}
    # Find events in sim path
    events=[]
    for p in fp:
        if p.get('event') or p.get('simEvent'):
            events.append({'date':p.get('date'),'event':p.get('event') or p.get('simEvent'),'high':p.get('high'),'low':p.get('low'),'close':p.get('close'),'stop':p.get('stop') or p.get('simStop')})
    x['sellPoint']['events']=events
    if fp:
        min_low=min(f(p.get('low'),f(x.get('entry'),0)) for p in fp)
        max_high=max(f(p.get('high'),f(x.get('entry'),0)) for p in fp)
        ent=f(x.get('entry'),0)
        x['pathStats']={'maxRunupPct':r((max_high/ent-1)*100) if ent else None,'maxDrawdownPct':r((min_low/ent-1)*100) if ent else None,'futureSessions':len(fp)}
    x['fullIndicatorsLatestCache']=flatten_ind(pick_indicator(full_cache,x.get('symbol')))
    return x

def by_symbol(trades):
    g=defaultdict(list)
    for t in trades: g[t.get('symbol')].append(t)
    rows=[]
    for sym,arr in g.items():
        s=summ(arr); s['symbol']=sym
        s['avgScore']=avg([f(t.get('score')) for t in arr]); s['avgDistSupportPct']=avg([f(t.get('distSupportPct')) for t in arr]); s['avgRsi']=avg([f(t.get('rsi')) for t in arr])
        wins=[t for t in arr if f(t.get('pnlPct'),0)>0]
        s['profitable']=s['sumPnlPct']>0
        s['sampleEntryExit']=[{'date':t.get('date'),'entry':t.get('entryPrice'),'exitDate':t.get('sellPoint',{}).get('exitDate'),'pnlPct':t.get('pnlPct'),'outcome':t.get('outcome'),'score':t.get('score'),'distSupportPct':t.get('distSupportPct'),'rsi':t.get('rsi')} for t in arr[:5]]
        rows.append(s)
    return sorted(rows,key=lambda x:x['sumPnlPct'],reverse=True)

def main():
    data=json.load(open(SRC,encoding='utf-8'))
    full=load_full_cache()
    # OOS here = prev3m relative to current180 optimization/test discussion.
    result={}
    for mode in ['none','loose','strict']:
        result[mode]={}
        for win in ['current180','prev3m']:
            trades=[enrich_trade(t,full) for t in data['results'][mode][win]['trades']]
            winners=[t for t in trades if f(t.get('pnlPct'),0)>0]
            losers=[t for t in trades if f(t.get('pnlPct'),0)<0]
            result[mode][win]={'summary':summ(trades),'profitableSymbols':by_symbol(trades),'winnerTrades':[{'symbol':t.get('symbol'),'date':t.get('date'),'entry':t.get('entryPrice'),'exitDate':t.get('sellPoint',{}).get('exitDate'),'pnlPct':t.get('pnlPct'),'outcome':t.get('outcome'),'score':t.get('score'),'distSupportPct':t.get('distSupportPct'),'rsi':t.get('rsi'),'sellEvents':t.get('sellPoint',{}).get('events',[]),'pathStats':t.get('pathStats')} for t in winners], 'loserCount':len(losers)}
    payload={'createdAt':datetime.now().isoformat(),'sourceTrades':str(SRC),'fullIndicatorCache':str(FULL),'note':'This summarizes exact futurePath trades and attaches latest full-indicator cache snapshot per symbol. For exact indicator-at-entry component attribution, rerun exact backtest while persisting full score_meta per trade/date. OOS treated as prev3m window.', 'results':result}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={m:{w:{'summary':result[m][w]['summary'],'topProfitableSymbols':result[m][w]['profitableSymbols'][:10]} for w in result[m]} for m in result}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
