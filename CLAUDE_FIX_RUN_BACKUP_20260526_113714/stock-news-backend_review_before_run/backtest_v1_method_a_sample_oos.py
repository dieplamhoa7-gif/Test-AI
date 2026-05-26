from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from app.market_data import _load_history, _calc_technical
from app.technical_filters import TECHNICAL_UNIVERSE

EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]
OUT=Path('data/v1_method_a_sample_oos_backtest.json')
LOOKBACK_DAYS=180
OOS_DAYS=60
HORIZON=10
MIN_BARS=120

def enrich(df):
    df=df.copy()
    for c in ['open','high','low','close','volume']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df['vol20']=df.volume.rolling(20).mean()
    d=df.close.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean()
    df['rsi']=100-(100/(1+g/l.replace(0,1e-9)))
    return df

def nearest_support_resistance(df, i):
    row=df.iloc[i]
    tech=_calc_technical(float(row.close),float(row.open),float(row.open),float(row.high),float(row.low),float(row.close),df.iloc[:i+1].copy())
    price=float(row.close)
    supports=[]
    for z in tech.get('supportZonesDay') or []:
        try:
            supports.append(float(z.get('center') or z.get('high') or z.get('low')))
        except Exception: pass
    supports += [float(x) for x in (tech.get('supportLevelsDay') or []) if float(x)>0]
    supports=[s for s in supports if s>0 and s<=price*1.01]
    resist=[float(x) for x in (tech.get('resistanceLevelsDay') or []) if float(x)>price]
    if not supports or not resist: return None, None
    return max(supports), min(resist)

def run_symbol(sym, start_date):
    df=_load_history(sym)
    if df is None or df.empty or len(df)<MIN_BARS: return []
    df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich(df)
    trades=[]
    for i in range(80, len(df)-HORIZON-1):
        if df.iloc[i].time < start_date: continue
        price=float(df.iloc[i].close)
        support,resistance=nearest_support_resistance(df,i)
        if not support or not resistance: continue
        entry_low=support; entry_high=support*1.02; stop=support*0.98
        # Method A: only enter if current close is within support zone S -> S*1.02
        if not (entry_low <= price <= entry_high):
            continue
        risk=price-stop; reward=resistance-price
        if risk<=0 or reward<=0: continue
        rr=reward/risk
        if rr < 1.0: continue
        # light quality filters to avoid dead support
        rsi=float(df.iloc[i].rsi or 0); vol=float(df.iloc[i].volume or 0); vol20=float(df.iloc[i].vol20 or vol or 1)
        if rsi < 38: continue
        if vol > vol20*2.5: continue
        future=df.iloc[i+1:i+1+HORIZON]
        outcome='timeout'; exitp=float(future.iloc[-1].close); exitd=str(future.iloc[-1].time.date()); hold=len(future)
        for k,r in future.iterrows():
            hit_stop=float(r.low)<=stop; hit_target=float(r.high)>=resistance
            hold=int(k-i)
            if hit_stop and hit_target:
                outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
            if hit_target:
                outcome='win'; exitp=resistance; exitd=str(r.time.date()); break
            if hit_stop:
                outcome='loss'; exitp=stop; exitd=str(r.time.date()); break
        pnl=(exitp-price)/price*100
        trades.append({'symbol':sym,'date':str(df.iloc[i].time.date()),'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(price,2),'support':round(support,2),'stop':round(stop,2),'target':round(resistance,2),'rr':round(rr,2),'riskPct':round(risk/price*100,2),'rewardPct':round(reward/price*100,2),'holdSessions':hold,'rsi':round(rsi,2),'volRatio':round(vol/vol20,2) if vol20 else None})
    return trades

def summary(ts):
    n=len(ts); w=[t for t in ts if t['outcome']=='win']; l=[t for t in ts if t['outcome']=='loss']; to=[t for t in ts if t['outcome']=='timeout']
    def s(xs,k): return round(sum(float(x[k]) for x in xs),2) if xs else 0
    def avg(xs,k): return round(s(xs,k)/len(xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'lossRatePct':round(len(l)/n*100,2) if n else 0,'timeoutRatePct':round(len(to)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':s(ts,'pnlPct'),'totalWinPct':s(w,'pnlPct'),'totalLossPct':s(l,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRR':avg(ts,'rr'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
    now=datetime.now(); start=pd.Timestamp(now-timedelta(days=LOOKBACK_DAYS)); split=pd.Timestamp(now-timedelta(days=OOS_DAYS))
    all_trades=[]
    for sym in UNIVERSE:
        try:
            t=run_symbol(sym,start); print(sym,len(t)); all_trades+=t
        except Exception as e:
            print(sym,'ERR',e)
    sample=[t for t in all_trades if pd.Timestamp(t['date']) < split]
    oos=[t for t in all_trades if pd.Timestamp(t['date']) >= split]
    payload={'createdAt':datetime.now().isoformat(),'method':'V1 Method A excluding VIC/VHM: entry S to S*1.02, stop S*0.98, target nearest resistance, RR>=1, RSI>=38, vol<=2.5x vol20','universe':UNIVERSE,'excluded':sorted(EXCLUDE),'lookbackDays':LOOKBACK_DAYS,'sampleDays':LOOKBACK_DAYS-OOS_DAYS,'oosDays':OOS_DAYS,'horizonSessions':HORIZON,'summary':{'sample':summary(sample),'oos':summary(oos),'all':summary(all_trades)},'sampleTrades':sample,'oosTrades':oos}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],ensure_ascii=True,indent=2))
    print('saved',OUT)
if __name__=='__main__': main()
