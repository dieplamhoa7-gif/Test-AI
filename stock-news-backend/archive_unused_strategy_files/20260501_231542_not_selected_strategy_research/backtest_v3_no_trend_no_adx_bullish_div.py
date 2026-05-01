from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_price_zone_state,_volume_state,_setup_type,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/v3_no_trend_no_adx_bullish_div_backtest.json')
LOOKBACK_DAYS=180; HORIZON=42; MAX_SYMBOLS=50

def f(v,d=0.0):
    try:
        if v is None: return d
        if hasattr(v,'item'): v=v.item()
        if pd.isna(v): return d
        return float(v)
    except Exception: return d

def s(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def atr_series(df,n=14):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def ichimoku_state(df):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    a=((ten+kij)/2).shift(26); b=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    price=f(c.iloc[-1]); av=f(a.iloc[-1]); bv=f(b.iloc[-1]); tv=f(ten.iloc[-1]); kv=f(kij.iloc[-1])
    if not av or not bv: return 'unknown', bool(tv>kv) if tv and kv else False
    top=max(av,bv); bot=min(av,bv)
    return ('above_cloud' if price>top else 'below_cloud' if price<bot else 'in_cloud'), bool(tv>kv) if tv and kv else False

def keltner_pct(df):
    c=pd.to_numeric(df.close,errors='coerce'); mid=c.ewm(span=20,adjust=False).mean(); atr=atr_series(df,14); up=mid+2*atr; lo=mid-2*atr
    den=f(up.iloc[-1])-f(lo.iloc[-1]); return (f(c.iloc[-1])-f(lo.iloc[-1]))/den if den else 0.5

def score_setup(price, rs, row, hist_df, daily_until):
    rsi=f(row.get('rsi14'),50); macd=f(row.get('macd')); sig=f(row.get('signal')); mh=f(row.get('histogram'))
    ma20=f(row.get('ma20'),price); ma50=f(row.get('ma50'),ma20); ma200=f(row.get('ma200'),ma50)
    bbp=f(row.get('bbPercent'),0.5); volr=f(row.get('volumeRatio'),1)
    vwap=f(rs.get('vwapDay'),0); don_hi=rs.get('donchianHighDay'); don_lo=rs.get('donchianLowDay')
    sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay')); atr=f(rs.get('atr'),price*0.03)
    sup_zone=rs.get('supportZoneDay') or [sup*0.985,sup*1.015]; res_zone=rs.get('resistanceZoneDay') or [res*0.985,res*1.015]
    zone_state=_price_zone_state(price,rsi,bbp,don_hi,don_lo,vwap or None)
    vol_state=_volume_state(volr,price,f(sup_zone[-1],sup),f(res_zone[-1],res),atr)
    setup=_setup_type(price,f(sup_zone[-1],sup),f(res_zone[-1],res),atr,zone_state,'Trung tính',vol_state)
    rr=round(max(res-price,0)/max(price-sup,0.01),2) if sup else 0
    div=_detect_momentum_divergence(daily_until)
    bullish=bool(div.get('bullish'))
    # No trend, no ADX/DI, no bearish divergence penalty. Bullish divergence is only reversal bonus.
    score=0
    score += 15 if 38<=rsi<=62 else 10 if 34<=rsi<=70 else 4 if 30<=rsi<=75 else 0
    score += 18 if macd>sig and mh>0 else 12 if mh>=0 else 7 if mh>-0.15 else 2 if mh>-0.3 else 0
    score += 16 if price>=ma20>=ma50 else 11 if price>=ma50 else 7 if price>=ma200 else 3
    score += 12 if 0.12<=bbp<=0.78 else 8 if bbp<0.12 else 4 if bbp<=0.92 else 0
    score += 8 if vwap and price>=vwap else 5 if vwap else 0
    score += 10 if 0.55<=volr<=2.3 else 6 if volr<0.55 else 4 if volr<=3 else 0
    ist,ib=ichimoku_state(hist_df); score += 10 if ist=='above_cloud' and ib else 7 if ist=='above_cloud' else 5 if ist in ['in_cloud','unknown'] else 2
    kp=keltner_pct(hist_df); score += 8 if 0.15<=kp<=0.82 else 5 if kp<0.15 else 3
    roc20=(price/f(hist_df.close.iloc[-21],price)-1)*100 if len(hist_df)>21 else 0; score += 8 if -3<=roc20<=12 else 5 if -10<=roc20< -3 else 3 if roc20>12 else 0
    dist=(price-sup)/price*100 if sup and price else 999
    score += 14 if dist<=2 else 10 if dist<=4 else 6 if dist<=7.5 else 3 if dist<=10 else 0
    score += 8 if bullish else 0
    score100=round(score/127*100,2)
    ok=score100>=55 and dist<=8.5 and rsi>=32 and bbp<=0.94 and volr<=3.2 and roc20>=-12
    return ok, {'score':score100,'dist':round(dist,2),'rr':rr,'rsi':s(rsi),'ichimoku':ist,'hist':s(mh,4),'support':sup,'resistance':res,'supportZone':sup_zone,'bullishDivergence':bullish,'roc20':s(roc20),'bbPercent':s(bbp,3),'volumeRatio':s(volr)}

def run_trade(df,i,meta):
    entry=f(df.iloc[i+1].close); low=f(meta['supportZone'][0],meta['support']*0.985); stop=low*0.95; risk=entry-stop
    if risk<=0 or risk/entry*100>14: return None
    target=entry+risk*3; future=df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    outcome='timeout'; exitp=f(future.iloc[-1].close); hold=len(future); exitd=str(future.iloc[-1].time.date())
    for n,(_,r) in enumerate(future.iterrows(),1):
        hs=f(r.high)>=target; hl=f(r.low)<=stop
        if hs and hl: outcome='loss'; exitp=stop; hold=n; exitd=str(r.time.date()); break
        if hs: outcome='win'; exitp=target; hold=n; exitd=str(r.time.date()); break
        if hl: outcome='loss'; exitp=stop; hold=n; exitd=str(r.time.date()); break
    return {'outcome':outcome,'entry':s(entry),'stop':s(stop),'target':s(target),'pnlPct':s((exitp-entry)/entry*100),'riskPct':s(risk/entry*100),'rr':3,'holdSessions':hold,'exitDate':exitd}

def summ(ts):
    n=len(ts); w=[x for x in ts if x['outcome']=='win']; l=[x for x in ts if x['outcome']=='loss']; to=[x for x in ts if x['outcome']=='timeout']
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
    cutoff=pd.Timestamp(datetime.now()-timedelta(days=LOOKBACK_DAYS)); trades=[]; counts={}
    for sym in TECHNICAL_UNIVERSE[:MAX_SYMBOLS]:
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<160: counts[sym]={'error':'missing/short'}; print(sym,'ERR'); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
            c={'loops':0,'signals':0,'trades':0}
            for i in range(100,len(df)-HORIZON-2):
                if df.iloc[i].time<cutoff: continue
                c['loops']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; daily_until=ind.iloc[:i+1].copy(); price=f(df.iloc[i].close)
                rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist)
                ok,meta=score_setup(price,rs,row,hist,daily_until)
                if not ok: continue
                c['signals']+=1; tr=run_trade(df,i,meta)
                if tr:
                    tr.update({'symbol':sym,'date':str(df.iloc[i+1].time.date()),'score':meta['score'],'distSupportPct':meta['dist'],'rsi':meta['rsi'],'ichimoku':meta['ichimoku'],'bullishDivergence':meta['bullishDivergence']}); trades.append(tr); c['trades']+=1
            counts[sym]=c; print(sym,c,flush=True)
        except Exception as e:
            counts[sym]={'error':repr(e)}; print(sym,'ERR',e,flush=True)
    split=pd.Timestamp(datetime.now()-timedelta(days=60)); sample=[t for t in trades if pd.Timestamp(t['date'])<split]; oos=[t for t in trades if pd.Timestamp(t['date'])>=split]
    payload={'createdAt':datetime.now().isoformat(),'method':'V3 no trend/no ADX/no bearish divergence; bullish divergence only as reversal bonus; RS-only engine; target 3R horizon 42','lookbackDays':LOOKBACK_DAYS,'horizon':HORIZON,'summary':{'sample':summ(sample),'oos':summ(oos),'all':summ(trades)},'trades':trades,'counts':counts}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['summary'],ensure_ascii=False,indent=2)); print('saved',OUT)
if __name__=='__main__': main()
