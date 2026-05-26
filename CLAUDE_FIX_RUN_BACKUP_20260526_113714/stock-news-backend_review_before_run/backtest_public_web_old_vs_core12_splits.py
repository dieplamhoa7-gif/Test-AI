from __future__ import annotations
import json, math
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd
from refresh_eod_all_stocks_lh import calc_core12

ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'
HIST=DATA/'vn100_history_2025_06_2026_05_cache.json'
OUT=DATA/'backtest_public_web_old_vs_core12_splits.json'
EXCLUDE={'VIC','VHM'}; HORIZON=42

def f(v,d=0.0):
    try:
        if v is None: return d
        x=float(v); return d if math.isnan(x) else x
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def rolling_feats(df):
    d=df.copy().sort_values('time').reset_index(drop=True)
    for c in ['open','high','low','close','volume']: d[c]=pd.to_numeric(d[c],errors='coerce')
    close=d.close; high=d.high; low=d.low; vol=d.volume
    ma20=close.rolling(20).mean(); std20=close.rolling(20).std(ddof=1)
    delta=close.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    d['rsi14']=100-100/(1+gain/loss.replace(0,float('nan')))
    ema12=close.ewm(span=12,adjust=False).mean(); ema26=close.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; sig=macd.ewm(span=9,adjust=False).mean()
    d['macd']=macd; d['signal']=sig; d['histogram']=macd-sig
    d['macdHistRecovering']=(d['histogram']>d['histogram'].shift(1))&(d['histogram'].shift(1)>d['histogram'].shift(2))
    d['bbPercent']=(close-(ma20-2*std20))/((ma20+2*std20)-(ma20-2*std20))
    d['volumeRatio']=vol/vol.rolling(20).mean(); d['roc20']=(close/close.shift(20)-1)*100
    tenkan=(high.rolling(9).max()+low.rolling(9).min())/2; kijun=(high.rolling(26).max()+low.rolling(26).min())/2
    a=((tenkan+kijun)/2).shift(26); b=((high.rolling(52).max()+low.rolling(52).min())/2).shift(26)
    d['ichiState']=['above_cloud' if c>max(x,y) else 'below_cloud' if c<min(x,y) else 'in_cloud' for c,x,y in zip(close,a.fillna(close),b.fillna(close))]
    return d

def sr_levels(hist, price):
    lows=[]; highs=[]; lo=hist.low.reset_index(drop=True); hi=hist.high.reset_index(drop=True)
    for i in range(max(2,len(hist)-160),len(hist)-2):
        if lo.iloc[i]<=lo.iloc[i-2:i+3].min(): lows.append(float(lo.iloc[i]))
        if hi.iloc[i]>=hi.iloc[i-2:i+3].max(): highs.append(float(hi.iloc[i]))
    sup=sorted([x for x in lows if x<price*1.01],key=lambda x:abs(price-x))[:1]
    res=sorted([x for x in highs if x>price*0.99],key=lambda x:abs(x-price))[:1]
    return (sup[0] if sup else 0),(res[0] if res else 0)

def trade(df,i,target,stop):
    if i+1>=len(df): return None
    entry=f(df.iloc[i+1].close); fut=df.iloc[i+2:i+2+HORIZON]
    if not entry or fut.empty: return None
    st=entry*(1-stop/100); tg=entry*(1+target/100); pnl=None; hold=len(fut); outcome='timeout'; exitd=str(fut.iloc[-1].time.date())
    for n,(_,row) in enumerate(fut.iterrows(),1):
        if f(row.high)>=tg: pnl=target; hold=n; outcome='win'; exitd=str(row.time.date()); break
        if f(row.low)<=st: pnl=-stop; hold=n; outcome='loss'; exitd=str(row.time.date()); break
    if pnl is None:
        pnl=(f(fut.iloc[-1].close)/entry-1)*100; outcome='win' if pnl>0 else 'loss' if pnl<0 else 'flat'
    return {'entry':r(entry),'pnlPct':r(pnl),'outcome':outcome,'holdSessions':hold,'exitDate':exitd}

CORE_CACHE={}

def core(sym,df,i):
    key=(sym,i)
    if key in CORE_CACHE: return CORE_CACHE[key]
    try:
        hist=df.iloc[:i+1].copy()
        rs=((calc_core12(sym,hist) or {}).get('tasks') or {}).get('RS') or {}; vals=rs.get('values') or {}
        def first(g):
            d=vals.get(g) or {}; return next(iter(d.values())) if isinstance(d,dict) and d else None
        out={'neg':f(rs.get('negative')),'pos':f(rs.get('positive')),'roc':first('ROC_MOMENTUM')}
    except Exception:
        out={'neg':0,'pos':0,'roc':None}
    CORE_CACHE[key]=out
    return out

def eval_sig(sym,df,i,version):
    row=df.iloc[i]; hist=df.iloc[:i+1].copy(); price=f(row.close); sup,_=sr_levels(hist,price); dist=(price-sup)/price*100 if price and sup else 999
    rsi=f(row.rsi14); bb=f(row.bbPercent); vol=f(row.volumeRatio,1); roc_daily=f(row.roc20); ichi=row.ichiState; macd=bool(row.macdHistRecovering)
    b4_base=[ichi=='above_cloud',dist<=3,48<=rsi<=62,0.55<=vol<=2.2,-12<=roc_daily<=12,macd,bb<=0.85]
    clean_a_base=[ichi!='below_cloud',dist<=2.8,rsi<=48,bb<=0.6,0.45<=vol<=2.5,roc_daily>=-18]
    clean_b_base=[ichi=='above_cloud',dist<=3.2,45<=rsi<=64,0.45<=vol<=2.5,-15<=roc_daily<=15,bb<=0.9]
    br=(sup-price)/sup*100 if sup else -999
    shake_base=[2<=br<=4,rsi>=20,vol<=2.6]
    neg=0; roc=roc_daily
    if version=='old':
        return {'b4_trend_pullback':all(b4_base),'clean_split_a_bottom':all(clean_a_base) or all(clean_b_base),'shakeout_breakdown_rebound':all(shake_base)}, {'price':r(price),'support':r(sup),'distSupportPct':r(dist),'coreNeg':neg}
    # New/Core12 version only computes Core12 for daily-rule candidates. This is equivalent to using Core12 as an added filter/replacement without wasting calls on obvious rejects.
    maybe_b4=all(b4_base[:-1]) or all(b4_base)
    maybe_clean=all(clean_a_base[:-1]) or all(clean_b_base[:-1]) or all(clean_a_base) or all(clean_b_base)
    maybe_shake=all(shake_base)
    if maybe_b4 or maybe_clean or maybe_shake:
        c=core(sym,df,i); neg=c['neg']; roc=f(c.get('roc'),roc_daily)
    b4=[ichi=='above_cloud',dist<=3,48<=rsi<=62,0.55<=vol<=2.2,-12<=roc<=12,macd,bb<=0.85,neg<=2]
    clean_a=[ichi!='below_cloud',dist<=2.8,rsi<=48,bb<=0.6,0.45<=vol<=2.5,roc>=-18,neg<=3]
    clean_b=[ichi=='above_cloud',dist<=3.2,45<=rsi<=64,0.45<=vol<=2.5,-15<=roc<=15,bb<=0.9,neg<=3]
    shake=[2<=br<=4,rsi>=20,vol<=2.6,neg<=4]
    return {'b4_trend_pullback':all(b4),'clean_split_a_bottom':all(clean_a) or all(clean_b),'shakeout_breakdown_rebound':all(shake)}, {'price':r(price),'support':r(sup),'distSupportPct':r(dist),'coreNeg':neg}

def summ(ts):
    n=len(ts); wins=[x for x in ts if f(x['pnlPct'])>0]; losses=[x for x in ts if f(x['pnlPct'])<0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    return {'trades':n,'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':round(sum(f(x['pnlPct']) for x in ts),2),'avgHold':avg(ts,'holdSessions')}

def run_window(name,start,end,frames):
    buckets={v:{s:[] for s in ['b4_trend_pullback','clean_split_a_bottom','shakeout_breakdown_rebound']} for v in ['old','core12']}
    for n,(sym,df) in enumerate(frames.items(),1):
        if n % 10 == 0:
            print(name,'symbol',n,'/',len(frames),sym,flush=True)
        for i in range(220,len(df)-HORIZON-2):
            t=df.iloc[i].time
            if t<start or t>=end: continue
            for ver in ['old','core12']:
                sig,meta=eval_sig(sym,df,i,ver)
                for sid,ok in sig.items():
                    if not ok: continue
                    target=10 if sid=='clean_split_a_bottom' else 6; stop=4 if sid=='shakeout_breakdown_rebound' else 6
                    tr=trade(df,i,target,stop)
                    if tr: tr.update({'symbol':sym,'signalDate':str(t.date()),'strategyId':sid,**meta}); buckets[ver][sid].append(tr)
    return {'name':name,'start':str(start.date()),'end':str(end.date()),'summaries':{v:{s:summ(buckets[v][s]) for s in buckets[v]} for v in buckets},'trades':buckets}

def main():
    raw=json.loads(HIST.read_text(encoding='utf-8'))['symbols']; frames={}
    # VN100/full refreshed universe, but only symbols with enough historical bars.
    for sym,obj in sorted(raw.items()):
        if sym in EXCLUDE: continue
        rows=obj.get('rows') or []
        if len(rows)<280: continue
        df=rolling_feats(pd.DataFrame(rows)); df['time']=pd.to_datetime(df.time); frames[sym]=df
    print('eligible symbols',len(frames),flush=True)
    windows=[('IS_2025H2',pd.Timestamp('2025-07-01'),pd.Timestamp('2026-01-01')),('OOS_2026',pd.Timestamp('2026-01-01'),pd.Timestamp(datetime.now()))]
    results=[]
    for w in windows:
        print('RUN',w[0],flush=True)
        results.append(run_window(*w,frames))
    # simple walk-forward: 6m train label + following 2m test segments; rules fixed, report test only
    wf=[]; start=pd.Timestamp('2025-01-01')
    while start+pd.DateOffset(months=8)<pd.Timestamp(datetime.now()):
        test_start=start+pd.DateOffset(months=6); test_end=start+pd.DateOffset(months=8)
        print('RUN WF',test_start.date(),test_end.date(),flush=True)
        wf.append(run_window('WF_test_'+str(test_start.date())+'_'+str(test_end.date()),test_start,test_end,frames)); start+=pd.DateOffset(months=3)
    payload={'createdAt':datetime.now().isoformat(),'method':'Compare old daily-rule version vs Core12/canonical version with IS, OOS, and walk-forward test windows. Core12 is recomputed rolling per historical signal.','windows':results,'walkForward':wf}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'windows':[{k:w[k] for k in ['name','start','end']}|{'summaries':w['summaries']} for w in results],'walkForwardCount':len(wf)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
