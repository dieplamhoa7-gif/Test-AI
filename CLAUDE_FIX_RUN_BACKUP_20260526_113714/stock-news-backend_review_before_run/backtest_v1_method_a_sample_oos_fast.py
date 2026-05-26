from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from app.market_data import _load_history
from app.technical_filters import TECHNICAL_UNIVERSE
EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]
OUT=Path('data/v1_method_a_sample_oos_fast.json')
LOOKBACK_DAYS=180; OOS_DAYS=60; HORIZON=10

def enrich(df):
    df=df.copy()
    for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
    df['vol20']=df.volume.rolling(20).mean(); df['ma20']=df.close.rolling(20).mean(); df['ma50']=df.close.rolling(50).mean()
    d=df.close.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean(); df['rsi']=100-(100/(1+g/l.replace(0,1e-9)))
    return df

def levels(df,i,lookback=60):
    hist=df.iloc[max(0,i-lookback):i]
    if len(hist)<30: return None,None
    price=float(df.iloc[i].close)
    lows=hist.low.dropna().tolist(); highs=hist.high.dropna().tolist()
    sups=[x for x in lows if x<=price*1.005]
    ress=[x for x in highs if x>price]
    if not sups or not ress: return None,None
    # use nearest robust quantile-ish levels to avoid one-day spike too close
    support=max(sups)
    resistance=min(ress)
    return support,resistance

def run_symbol(sym,start):
    df=_load_history(sym)
    if df is None or df.empty or len(df)<100: return []
    df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich(df)
    trades=[]
    for i in range(70,len(df)-HORIZON-1):
        if df.iloc[i].time<start: continue
        price=float(df.iloc[i].close); support,resistance=levels(df,i)
        if not support or not resistance: continue
        entry_low=support; entry_high=support*1.02; stop=support*0.98; target=resistance
        if not(entry_low<=price<=entry_high): continue
        risk=price-stop; reward=target-price
        if risk<=0 or reward<=0: continue
        rr=reward/risk
        if rr<1: continue
        rsi=float(df.iloc[i].rsi or 0); vol=float(df.iloc[i].volume or 0); vol20=float(df.iloc[i].vol20 or vol or 1)
        if rsi<38 or vol>vol20*2.5: continue
        future=df.iloc[i+1:i+1+HORIZON]
        outcome='timeout'; exitp=float(future.iloc[-1].close); exitd=str(future.iloc[-1].time.date()); hold=len(future)
        for k,r in future.iterrows():
            hit_stop=float(r.low)<=stop; hit_target=float(r.high)>=target; hold=int(k-i)
            if hit_stop and hit_target: outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
            if hit_target: outcome='win'; exitp=target; exitd=str(r.time.date()); break
            if hit_stop: outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
        pnl=(exitp-price)/price*100
        trades.append({'symbol':sym,'date':str(df.iloc[i].time.date()),'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(price,2),'support':round(support,2),'stop':round(stop,2),'target':round(target,2),'rr':round(rr,2),'riskPct':round(risk/price*100,2),'rewardPct':round(reward/price*100,2),'holdSessions':hold,'rsi':round(rsi,2),'volRatio':round(vol/vol20,2) if vol20 else None})
    return trades

def summary(ts):
    n=len(ts); w=[t for t in ts if t['outcome']=='win']; l=[t for t in ts if t['outcome']=='loss']; to=[t for t in ts if t['outcome']=='timeout']
    def sm(xs,k): return round(sum(float(x[k]) for x in xs),2) if xs else 0
    def avg(xs,k): return round(sm(xs,k)/len(xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'lossRatePct':round(len(l)/n*100,2) if n else 0,'timeoutRatePct':round(len(to)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'totalWinPct':sm(w,'pnlPct'),'totalLossPct':sm(l,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRR':avg(ts,'rr'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
    now=datetime.now(); start=pd.Timestamp(now-timedelta(days=LOOKBACK_DAYS)); split=pd.Timestamp(now-timedelta(days=OOS_DAYS)); all=[]
    for sym in UNIVERSE:
        try:
            t=run_symbol(sym,start); print(sym,len(t),flush=True); all+=t
        except Exception as e: print(sym,'ERR',e,flush=True)
    sample=[t for t in all if pd.Timestamp(t['date'])<split]; oos=[t for t in all if pd.Timestamp(t['date'])>=split]
    payload={'createdAt':datetime.now().isoformat(),'method':'V1 Method A FAST excluding VIC/VHM: support=nearest rolling 60D low <= price, entry S-S*1.02, stop S*0.98, target nearest rolling resistance, RR>=1, RSI>=38, vol<=2.5x','excluded':sorted(EXCLUDE),'universe':UNIVERSE,'lookbackDays':LOOKBACK_DAYS,'sampleDays':LOOKBACK_DAYS-OOS_DAYS,'oosDays':OOS_DAYS,'horizonSessions':HORIZON,'summary':{'sample':summary(sample),'oos':summary(oos),'all':summary(all)},'sampleTrades':sample,'oosTrades':oos}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],ensure_ascii=True,indent=2)); print('saved',OUT)
if __name__=='__main__': main()
