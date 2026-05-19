from __future__ import annotations
import json, math, statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import pandas as pd

import ml_core12_group_combo_search as core12
from refresh_eod_all_stocks_lh import calc_indicators, calc_core12

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
HIST=DATA/'vn100_history_2025_06_2026_05_cache.json'
OUT=DATA/'backtest_public_web_core12_canonical.json'
EXCLUDE={'VIC','VHM'}
HORIZON=42
START_DAYS=365

def f(v,d=0.0):
    try:
        if v is None: return d
        x=float(v)
        if math.isnan(x): return d
        return x
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def trade_manage(df,i,target_pct,stop_pct):
    if i+1>=len(df): return None
    entry=f(df.iloc[i+1].close); stop=entry*(1-stop_pct/100); target=entry*(1+target_pct/100)
    fut=df.iloc[i+2:i+2+HORIZON]
    if fut.empty: return None
    peak=entry; pnl=None; outcome='timeout'; hold=len(fut); exit_date=str(fut.iloc[-1].time.date())
    for n,(_,row) in enumerate(fut.iterrows(),1):
        hi=f(row.high); lo=f(row.low); peak=max(peak,hi)
        if hi>=target:
            pnl=target_pct; outcome='win'; hold=n; exit_date=str(row.time.date()); break
        if lo<=stop:
            pnl=-stop_pct; outcome='loss'; hold=n; exit_date=str(row.time.date()); break
    if pnl is None:
        last=f(fut.iloc[-1].close); pnl=(last/entry-1)*100; outcome='win' if pnl>0 else 'loss' if pnl<0 else 'flat'
    return {'entry':r(entry),'pnlPct':r(pnl),'outcome':outcome,'holdSessions':hold,'exitDate':exit_date}

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
    d['volumeRatio']=vol/vol.rolling(20).mean()
    d['roc20']=(close/close.shift(20)-1)*100
    tenkan=(high.rolling(9).max()+low.rolling(9).min())/2; kijun=(high.rolling(26).max()+low.rolling(26).min())/2
    span_a=((tenkan+kijun)/2).shift(26); span_b=((high.rolling(52).max()+low.rolling(52).min())/2).shift(26)
    d['ichiState']=['above_cloud' if c>max(a,b) else 'below_cloud' if c<min(a,b) else 'in_cloud' for c,a,b in zip(close,span_a.fillna(close),span_b.fillna(close))]
    d['ma20']=ma20; d['ma50']=close.rolling(50).mean(); d['ma200']=close.rolling(200).mean()
    return d

def sr_levels(hist, price):
    lows=[]; highs=[]; lo=hist.low.reset_index(drop=True); hi=hist.high.reset_index(drop=True)
    for i in range(max(2,len(hist)-160),len(hist)-2):
        if lo.iloc[i]<=lo.iloc[i-2:i+3].min(): lows.append(float(lo.iloc[i]))
        if hi.iloc[i]>=hi.iloc[i-2:i+3].max(): highs.append(float(hi.iloc[i]))
    sups=sorted([x for x in lows if x<price*1.01],key=lambda x:abs(price-x))[:5]
    ress=sorted([x for x in highs if x>price*0.99],key=lambda x:abs(x-price))[:5]
    return (sups[0] if sups else 0),(ress[0] if ress else 0)

def core_scores(sym,hist):
    c=calc_core12(sym,hist)
    tasks=(c or {}).get('tasks') or {}; rs=tasks.get('RS') or {}
    vals=rs.get('values') or {}; pos=f(rs.get('positive')); neg=f(rs.get('negative'))
    def first(group):
        if group not in vals: return None
        dd=vals[group]
        return next(iter(dd.values())) if isinstance(dd,dict) and dd else None
    return {'corePos':pos,'coreNeg':neg,'coreScore':f(rs.get('score')),'mfi':first('MFI_CMF'),'roc':first('ROC_MOMENTUM'),'ma':first('MA_EMA_WMA'),'vwap':first('VWAP_VWMA')}

def evals(sym,df,i):
    row=df.iloc[i]; hist=df.iloc[:i+1].copy(); price=f(row.close); sup,res=sr_levels(hist,price); dist=(price-sup)/price*100 if price and sup else 999
    cs=core_scores(sym,hist)
    ai={'rsi':f(row.rsi14),'bbp':f(row.bbPercent),'volr':f(row.volumeRatio,1),'roc':f(cs.get('roc'), f(row.roc20)),'macdRec':bool(row.macdHistRecovering),'ichi':row.ichiState,'coreNeg':cs['coreNeg'],'corePos':cs['corePos']}
    out={}
    b4=[ai['ichi']=='above_cloud',dist<=3,48<=ai['rsi']<=62,0.55<=ai['volr']<=2.2,-12<=ai['roc']<=12,ai['macdRec'],ai['bbp']<=0.85,ai['coreNeg']<=2]
    out['b4_trend_pullback']=sum(b4)==len(b4)
    a2=[ai['ichi']!='below_cloud',dist<=2.8,ai['rsi']<=48,ai['bbp']<=0.6,0.45<=ai['volr']<=2.5,ai['roc']>=-18,ai['coreNeg']<=3]
    b2=[ai['ichi']=='above_cloud',dist<=3.2,45<=ai['rsi']<=64,0.45<=ai['volr']<=2.5,-15<=ai['roc']<=15,ai['bbp']<=0.9,ai['coreNeg']<=3]
    out['clean_split_a_bottom']=sum(a2)==len(a2) or sum(b2)==len(b2)
    break_pct=(sup-price)/sup*100 if sup else -999
    sh=[2<=break_pct<=4,ai['rsi']>=20,ai['volr']<=2.6,ai['coreNeg']<=4]
    out['shakeout_breakdown_rebound']=sum(sh)==len(sh)
    return out, {'price':r(price),'support':r(sup),'distSupportPct':r(dist),'core':cs,'ai':ai}

def summ(trades):
    n=len(trades); wins=[t for t in trades if f(t['pnlPct'])>0]; losses=[t for t in trades if f(t['pnlPct'])<0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    return {'trades':n,'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgPnlPct':avg(trades,'pnlPct'),'sumPnlPct':round(sum(f(t['pnlPct']) for t in trades),2),'avgHold':avg(trades,'holdSessions')}

def main():
    raw=json.loads(HIST.read_text(encoding='utf-8'))['symbols']
    start=pd.Timestamp(datetime.now()-timedelta(days=START_DAYS))
    buckets={k:[] for k in ['b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom']}
    scanned={}
    for sym,obj in sorted(raw.items()):
        if sym in EXCLUDE: continue
        rows=obj.get('rows') or []
        if len(rows)<260: continue
        df=rolling_feats(pd.DataFrame(rows)); df['time']=pd.to_datetime(df.time)
        cnt=0
        for i in range(220,len(df)-HORIZON-2):
            if df.iloc[i].time<start: continue
            sig,meta=evals(sym,df,i); cnt+=1
            for sid,ok in sig.items():
                if ok:
                    target=10 if sid=='clean_split_a_bottom' else 6; stop=6 if sid!='shakeout_breakdown_rebound' else 4
                    tr=trade_manage(df,i,target,stop)
                    if tr: tr.update({'symbol':sym,'signalDate':str(df.iloc[i].time.date()),'strategyId':sid,**meta}); buckets[sid].append(tr)
        scanned[sym]=cnt
        print(sym,cnt,{k:sum(1 for t in v if t['symbol']==sym) for k,v in buckets.items()},flush=True)
    payload={'createdAt':datetime.now().isoformat(),'source':str(HIST),'method':'Backtest 3 public web rules using latest vnstock history and Core12/canonical-preferred features. Entry next session close; horizon 42 sessions; fixed target/stop per strategy.','windowDays':START_DAYS,'summaries':{k:summ(v) for k,v in buckets.items()},'trades':buckets,'scanned':scanned}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summaries':payload['summaries']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
