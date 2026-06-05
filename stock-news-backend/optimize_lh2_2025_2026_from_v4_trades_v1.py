import json, itertools, pathlib, pandas as pd
DATA=pathlib.Path('data')
SRC=DATA/'lh2_v4_leader_momentum_backtest.json'
OUT=DATA/'lh2_2025_2026_priority_from_v4_optimizer_v1.json'
TRADES=json.loads(SRC.read_text(encoding='utf-8')).get('trades',[])

def f(v,d=0.0):
    try:
        if v is None or pd.isna(v): return d
        return float(v)
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def sm(rows):
    n=len(rows); vals=[f(x.get('netPnlPct')) for x in rows]; w=sum(v>0 for v in vals); stops=sum(x.get('exitType')=='stop' for x in rows)
    return {'trades':n,'wins':w,'losses':n-w,'winRatePct':r(w/n*100) if n else 0,'avgNetPnlPct':r(sum(vals)/n) if n else 0,'sumNetPnlPct':r(sum(vals)),'stopRatePct':r(stops/n*100) if n else 0,'avgHold':r(sum(f(x.get('holdSessions')) for x in rows)/n) if n else 0}

def inwin(x,a,b):
    d=pd.Timestamp(x['signalDate']); return pd.Timestamp(a)<=d<pd.Timestamp(b)

def passg(t,g):
    s=t.get('scores') or {}
    return (g['rslo']<=f(s.get('rel20Pct'))<=g['rshi'] and g['vlo']<=f(s.get('volumeRatio'))<=g['vhi'] and f(s.get('obvSlope20'))>=g['obv'] and f(s.get('vwapSlope5'))>=g['vwap'] and f(s.get('breadth'))>=g['breadth'] and f(s.get('rangePos60'))>=g['rangePos60'] and (bool(s.get('breakout50')) or not g['needBreakout50']))

def gates():
    for rslo,rshi,vlo,vhi,obv,vwap,breadth,rp,need50 in itertools.product([5,7,9,11],[12,16,20,25],[1.2,1.5,1.8],[2.3,3.0,4.0],[0,0.3,0.6,0.8],[0,0.3,0.6],[45,50,55],[0.85,0.9,0.95],[False,True]):
        if rslo<rshi and vlo<vhi:
            yield {'rslo':rslo,'rshi':rshi,'vlo':vlo,'vhi':vhi,'obv':obv,'vwap':vwap,'breadth':breadth,'rangePos60':rp,'needBreakout50':need50}

def score(m25,m26,mall):
    if m25['trades']<2 or mall['trades']<4: return -999999
    s=m25['avgNetPnlPct']*5 + m25['winRatePct']*.35 - m25['stopRatePct']*.2 + min(m25['trades'],10)*.8
    if m26['trades']:
        s+=m26['avgNetPnlPct']*4 + m26['winRatePct']*.25 - m26['stopRatePct']*.2 + min(m26['trades'],6)
    else:
        s-=5
    s+=mall['avgNetPnlPct']*1.2 + mall['winRatePct']*.08 - mall['stopRatePct']*.05
    if mall['avgNetPnlPct']<1 or mall['winRatePct']<45: s-=25
    return s

scored=[]
for g in gates():
    rows=[t for t in TRADES if passg(t,g)]
    t25=[t for t in rows if inwin(t,'2025-01-01','2026-01-01')]
    t26=[t for t in rows if inwin(t,'2026-01-01','2026-07-01')]
    m25=sm(t25); m26=sm(t26); mall=sm(rows); s=score(m25,m26,mall)
    if s>-999999:
        scored.append({'gate':g,'score':r(s,3),'summary2025':m25,'summary2026':m26,'summaryAll':mall,'trades':rows})
scored.sort(key=lambda x:(x['score'],x['summary2025']['avgNetPnlPct'],x['summaryAll']['trades']), reverse=True)
best=scored[0] if scored else None
out={'status':'completed','createdAt':pd.Timestamp.now().isoformat(),'method':'LH2 2025-2026 Priority from v4 trade universe optimizer v1','source':str(SRC),'baseline':{'2025':sm([t for t in TRADES if inwin(t,'2025-01-01','2026-01-01')]),'2026':sm([t for t in TRADES if inwin(t,'2026-01-01','2026-07-01')]),'all':sm(TRADES)},'best':{k:v for k,v in best.items() if k!='trades'} if best else None,'top30':[{k:v for k,v in x.items() if k!='trades'} for x in scored[:30]],'bestTrades':best['trades'] if best else []}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'baseline':out['baseline'],'best':out['best']},ensure_ascii=False,indent=2))
