from __future__ import annotations
import json, itertools
from pathlib import Path
import pandas as pd

SRC=Path('data/vn100_history_from_2023.json')
OUT=Path('data/lh2_2025_2026_priority_optimizer_v1.json')
START=pd.Timestamp('2023-01-01'); END=pd.Timestamp('2026-06-01')
FEE=0.5; MIN_HOLD=3; HORIZON=60

def f(v,d=0.0):
    try:
        if v is None or pd.isna(v): return d
        if hasattr(v,'item'): v=v.item()
        return float(v)
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def atomic(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(path)

def enrich(df):
    df=df.copy(); c=df.close.astype(float); h=df.high.astype(float); l=df.low.astype(float); v=df.volume.astype(float)
    df['ma20']=c.rolling(20).mean(); df['ret20']=c.pct_change(20,fill_method=None)*100
    df['vol20']=v.rolling(20).mean(); df['volRatio']=v/df['vol20'].replace(0,pd.NA)
    df['high20_prev']=h.rolling(20).max().shift(1); df['high50_prev']=h.rolling(50).max().shift(1)
    df['rangePos60']=(c-l.rolling(60).min())/(h.rolling(60).max()-l.rolling(60).min()).replace(0,pd.NA)
    direction=c.diff().fillna(0).apply(lambda x:1 if x>0 else (-1 if x<0 else 0)); df['obv']=(direction*v).cumsum(); df['obvSlope20']=df['obv'].diff(20)/df['obv'].abs().rolling(60).mean().replace(0,pd.NA)
    tp=(h+l+c)/3; df['vwap20']=(tp*v).rolling(20).sum()/v.rolling(20).sum().replace(0,pd.NA); df['vwapSlope5']=df['vwap20'].diff(5)/df['vwap20'].shift(5)*100
    return df

def load():
    data=json.loads(SRC.read_text(encoding='utf-8')).get('symbols',{}); out={}
    for sym,o in data.items():
        rows=o.get('rows') or []
        if len(rows)<260: continue
        df=pd.DataFrame(rows); df['time']=pd.to_datetime(df['time'])
        for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
        out[sym]=enrich(df.sort_values('time').reset_index(drop=True))
    return out

def market(hist):
    closes=[df[['time','close']].rename(columns={'close':s}).set_index('time') for s,df in hist.items()]
    close=pd.concat(closes,axis=1).sort_index(); ret=close.pct_change(fill_method=None); idx=(1+ret.mean(axis=1).fillna(0)).cumprod()*1000
    return pd.DataFrame({'mktRet20':idx.pct_change(20,fill_method=None)*100,'breadth':(close>close.rolling(20).mean()).sum(axis=1)/close.count(axis=1)*100})

def sim_exit(df,i):
    if i+1>=len(df): return None
    entry=f(df.iloc[i+1].close); target=entry*1.12; stop=entry*0.95; zone=max(f(df.iloc[i].high20_prev),f(df.iloc[i].high50_prev)); fut=df.iloc[i+2:i+2+HORIZON]
    for n,(_,row) in enumerate(fut.iterrows(),1):
        if n>=3:
            no_follow=f(row.close)<entry*1.03
            fail=f(row.close)<zone or f(row.close)<f(row.ma20) or f(row.close)<f(row.vwap20)
            if no_follow and fail:
                gross=(f(row.close)/entry-1)*100
                return {'netPnlPct':r(gross-FEE),'holdSessions':n,'exitDate':str(row.time.date()),'exitType':'failure_exit'}
        if n<MIN_HOLD: continue
        if f(row.low)<=stop: return {'netPnlPct':-5.5,'holdSessions':n,'exitDate':str(row.time.date()),'exitType':'stop'}
        if f(row.high)>=target: return {'netPnlPct':11.5,'holdSessions':n,'exitDate':str(row.time.date()),'exitType':'target'}
    if fut.empty: return None
    gross=(f(fut.iloc[-1].close)/entry-1)*100; return {'netPnlPct':r(gross-FEE),'holdSessions':len(fut),'exitDate':str(fut.iloc[-1].time.date()),'exitType':'timeout'}

def summary(rows):
    n=len(rows); vals=[f(x.get('netPnlPct')) for x in rows]; w=sum(v>0 for v in vals); stops=sum(x.get('exitType')=='stop' for x in rows)
    return {'trades':n,'wins':w,'losses':n-w,'winRatePct':r(w/n*100) if n else 0,'avgNetPnlPct':r(sum(vals)/n) if n else 0,'sumNetPnlPct':r(sum(vals)),'stopRatePct':r(stops/n*100) if n else 0,'avgHold':r(sum(f(x.get('holdSessions')) for x in rows)/n) if n else 0}

def gate_grid():
    for rslo,rshi,vlo,vhi,obv,vwap,breadth,rp,need50 in itertools.product(
        [5,7,9], [12,16,20], [1.2,1.5,1.8], [2.3,3.0,4.0], [0,0.3,0.6,0.8], [0,0.3,0.6], [45,50,55], [0.85,0.9,0.95], [False,True]
    ):
        if rslo<rshi and vlo<vhi:
            yield {'rslo':rslo,'rshi':rshi,'vlo':vlo,'vhi':vhi,'obv':obv,'vwap':vwap,'breadth':breadth,'rangePos60':rp,'needBreakout50':need50}

def passg(row,rs,br,g):
    breakout20=f(row.close)>f(row.high20_prev); breakout50=f(row.close)>f(row.high50_prev)
    breakout=breakout50 if g['needBreakout50'] else (breakout20 or breakout50)
    return breakout and g['rslo']<=rs<=g['rshi'] and g['vlo']<=f(row.volRatio)<=g['vhi'] and f(row.obvSlope20)>=g['obv'] and f(row.vwapSlope5)>=g['vwap'] and br>=g['breadth'] and f(row.rangePos60)>=g['rangePos60'] and f(row.close)>=f(row.ma20) and f(row.close)>=f(row.vwap20)

def score(m25,m26,mall):
    if m25['trades']<2 or mall['trades']<4: return -999999
    s=m25['avgNetPnlPct']*5 + m25['winRatePct']*.35 - m25['stopRatePct']*.2 + min(m25['trades'],12)*.8
    if m26['trades']:
        s+=m26['avgNetPnlPct']*4 + m26['winRatePct']*.25 - m26['stopRatePct']*.2 + min(m26['trades'],6)
    else: s-=5
    s+=mall['avgNetPnlPct']*1.2 + mall['winRatePct']*.08 - mall['stopRatePct']*.05 + min(mall['trades'],30)*.08
    if mall['avgNetPnlPct']<1 or mall['winRatePct']<45: s-=25
    return s

def main():
    hist=load(); mkt=market(hist); rows=[]
    for sym,df in hist.items():
        for i in range(120,len(df)-HORIZON-2):
            date=df.iloc[i].time
            if date<START or date>=END or date not in mkt.index: continue
            row=df.iloc[i]; rs=f(row.ret20)-f(mkt.loc[date].mktRet20); br=f(mkt.loc[date].breadth)
            if not (f(row.close)>=f(row.ma20) and f(row.close)>=f(row.vwap20)): continue
            if not (f(row.close)>f(row.high20_prev) or f(row.close)>f(row.high50_prev)): continue
            ex=sim_exit(df,i)
            if not ex: continue
            rows.append({**ex,'symbol':sym,'signalDate':str(date.date()),'entryDate':str(df.iloc[i+1].time.date()),'features':{'rs':r(rs),'breadth':r(br),'volRatio':r(row.volRatio),'obvSlope20':r(row.obvSlope20,4),'vwapSlope5':r(row.vwapSlope5),'rangePos60':r(row.rangePos60),'breakout50':bool(f(row.close)>f(row.high50_prev))}})
    def filt(g, a, b):
        aa=pd.Timestamp(a); bb=pd.Timestamp(b); out=[]
        for x in rows:
            d=pd.Timestamp(x['signalDate']); ft=x['features']
            if aa<=d<bb and g['rslo']<=ft['rs']<=g['rshi'] and g['vlo']<=ft['volRatio']<=g['vhi'] and ft['obvSlope20']>=g['obv'] and ft['vwapSlope5']>=g['vwap'] and ft['breadth']>=g['breadth'] and ft['rangePos60']>=g['rangePos60'] and (ft['breakout50'] or not g['needBreakout50']):
                out.append(x)
        return out
    scored=[]
    for g in gate_grid():
        t25=filt(g,'2025-01-01','2026-01-01'); t26=filt(g,'2026-01-01','2026-07-01'); tall=filt(g,'2023-01-01','2026-07-01')
        m25=summary(t25); m26=summary(t26); mall=summary(tall); s=score(m25,m26,mall)
        if s>-999999:
            scored.append({'gate':g,'score':r(s,3),'summary2025':m25,'summary2026':m26,'summaryAll':mall,'trades':tall})
    scored.sort(key=lambda x:(x['score'],x['summary2025']['avgNetPnlPct'],x['summaryAll']['trades']), reverse=True)
    best=scored[0] if scored else None
    out={'status':'completed','createdAt':pd.Timestamp.now().isoformat(),'method':'LH2 2025-2026 Priority Optimizer v1','baseCandidates':len(rows),'best':{k:v for k,v in best.items() if k!='trades'} if best else None,'top30':[{k:v for k,v in x.items() if k!='trades'} for x in scored[:30]],'bestTrades':best['trades'] if best else []}
    atomic(OUT,out)
    print(json.dumps({'baseCandidates':len(rows),'best':out['best']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
