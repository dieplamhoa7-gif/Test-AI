from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from app.market_data import _load_history
from app.technical_filters import TECHNICAL_UNIVERSE

EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]
OUT=Path('data/v1_method_b_sample_oos_fast.json')
LOOKBACK_DAYS=180
OOS_DAYS=60
HORIZON=10


def enrich(df):
    df=df.copy()
    for c in ['open','high','low','close','volume']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df['vol20']=df.volume.rolling(20).mean()
    df['ma20']=df.close.rolling(20).mean()
    df['ma50']=df.close.rolling(50).mean()
    d=df.close.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean()
    df['rsi']=100-(100/(1+g/l.replace(0,1e-9)))
    df[['open','high','low','close','volume','vol20','ma20','ma50','rsi']]=df[['open','high','low','close','volume','vol20','ma20','ma50','rsi']].apply(pd.to_numeric, errors='coerce')
    ema12=df.close.ewm(span=12,adjust=False).mean(); ema26=df.close.ewm(span=26,adjust=False).mean(); macd=ema12-ema26
    df['macdHist']=macd-macd.ewm(span=9,adjust=False).mean()
    return df


def levels(df,i,lookback=60):
    hist=df.iloc[max(0,i-lookback):i]
    if len(hist)<30: return None,None
    price=float(df.iloc[i].close)
    lows=pd.to_numeric(hist.low, errors='coerce').dropna().tolist()
    highs=pd.to_numeric(hist.high, errors='coerce').dropna().tolist()
    sups=[float(x) for x in lows if float(x)<=price*1.005]
    ress=[float(x) for x in highs if float(x)>price]
    if not sups or not ress: return None,None
    return max(sups), min(ress)


def run_symbol(sym,start):
    df=_load_history(sym)
    if df is None or df.empty or len(df)<100: return []
    df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich(df)
    trades=[]
    for i in range(70,len(df)-HORIZON-1):
        if df.iloc[i].time<start: continue
        price=pd.to_numeric(pd.Series([df.iloc[i].close]), errors='coerce').iloc[0]
        if pd.isna(price): continue
        price=float(price); support,resistance=levels(df,i)
        if not support or not resistance: continue
        # Method B: still only buy near support, but stop is fixed -4% from entry.
        entry_low=support; entry_high=support*1.02
        if not(entry_low<=price<=entry_high): continue
        stop=price*0.96
        risk=price-stop
        # Target: prefer nearest resistance if it gives >=1R, otherwise use fixed 1R.
        target=resistance if (resistance-price)>=risk else price+risk
        reward=target-price
        rr=reward/risk if risk>0 else 0
        if rr<1: continue
        row=df.iloc[i]
        rsi=float(row.rsi) if pd.notna(row.rsi) else 0
        vol=float(row.volume) if pd.notna(row.volume) else 0
        vol20=float(row.vol20) if pd.notna(row.vol20) and float(row.vol20)>0 else (vol or 1)
        hist=float(row.macdHist) if pd.notna(row.macdHist) else 0
        # light quality filters: avoid weak breakdown support
        if rsi<38: continue
        if vol>vol20*2.5: continue
        ma50=float(row.ma50) if pd.notna(row.ma50) else 0
        if ma50>0 and float(row.close)<ma50*0.96: continue
        future=df.iloc[i+1:i+1+HORIZON]
        outcome='timeout'; exitp=float(future.iloc[-1].close); exitd=str(future.iloc[-1].time.date()); hold=len(future)
        for k,r in future.iterrows():
            hit_stop=float(r.low)<=stop; hit_target=float(r.high)>=target; hold=int(k-i)
            if hit_stop and hit_target:
                outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
            if hit_target:
                outcome='win'; exitp=target; exitd=str(r.time.date()); break
            if hit_stop:
                outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
        pnl=(exitp-price)/price*100
        trades.append({'symbol':sym,'date':str(row.time.date()),'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(price,2),'support':round(support,2),'entryZone':f'{entry_low:.2f} - {entry_high:.2f}','stop':round(stop,2),'target':round(target,2),'nearestResistance':round(resistance,2),'rr':round(rr,2),'riskPct':round(risk/price*100,2),'rewardPct':round(reward/price*100,2),'holdSessions':hold,'rsi':round(rsi,2),'hist':round(hist,3),'volRatio':round(vol/vol20,2) if vol20 else None})
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
        except Exception as e:
            print(sym,'ERR',e,flush=True)
    sample=[t for t in all if pd.Timestamp(t['date'])<split]; oos=[t for t in all if pd.Timestamp(t['date'])>=split]
    payload={'createdAt':datetime.now().isoformat(),'method':'V1 Method B FAST excluding VIC/VHM: entry support to support*1.02, stop entry*0.96, target nearest resistance if >=1R else 1R, RR>=1, RSI>=38, vol<=2.5x, close>=MA50*0.96','excluded':sorted(EXCLUDE),'universe':UNIVERSE,'lookbackDays':LOOKBACK_DAYS,'sampleDays':LOOKBACK_DAYS-OOS_DAYS,'oosDays':OOS_DAYS,'horizonSessions':HORIZON,'summary':{'sample':summary(sample),'oos':summary(oos),'all':summary(all)},'sampleTrades':sample,'oosTrades':oos}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],ensure_ascii=True,indent=2)); print('saved',OUT)

if __name__=='__main__': main()
