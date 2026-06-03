from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
import pandas as pd

import backtest_b4_trend_pullback_locked as lh1
from app.market_data import _compute_indicators
from app.rs_levels import calc_rs_levels_only

SRC = Path('data/vn100_history_from_2023.json')
OUT = Path('data/lh1_v2_ml_combo_2023_to_now.json')
START = pd.Timestamp('2023-01-01')
END = pd.Timestamp('2026-06-01')
FEE_PCT = 0.5
MIN_HOLD = 3
HORIZON = 42
WINDOWS = {
    '2023': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-01-01')),
    '2024': (pd.Timestamp('2024-01-01'), pd.Timestamp('2025-01-01')),
    '2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2026-01-01')),
    '2026_ytd': (pd.Timestamp('2026-01-01'), END),
    'all_2023_now': (START, END),
}

def f(v, d=0.0):
    try:
        if v is None or pd.isna(v): return d
        if hasattr(v, 'item'): v = v.item()
        return float(v)
    except Exception:
        return d

def r(v, n=2):
    try: return round(float(v), n)
    except Exception: return None

def load_histories(symbols):
    obj=json.loads(SRC.read_text(encoding='utf-8'))
    data=obj.get('symbols',{})
    out={}
    for sym in symbols:
        rows=((data.get(sym) or {}).get('rows') or [])
        if not rows:
            out[sym]=None; continue
        df=pd.DataFrame(rows)
        df['time']=pd.to_datetime(df['time'])
        for c in ['open','high','low','close','volume']:
            df[c]=pd.to_numeric(df[c],errors='coerce')
        out[sym]=df.sort_values('time').reset_index(drop=True)
    return out

def add_ml_features(df, ind):
    df=df.copy(); ind=ind.copy()
    c=df['close']; v=df['volume']
    ind['sma10']=c.rolling(10).mean()
    ind['sma10_dist']=(c/ind['sma10']-1)*100
    low14=df['low'].rolling(14).min(); high14=df['high'].rolling(14).max()
    ind['williams_r14']=-100*(high14-c)/(high14-low14).replace(0,pd.NA)
    low14s=df['low'].rolling(14).min(); high14s=df['high'].rolling(14).max()
    ind['stoch_k']=100*(c-low14s)/(high14s-low14s).replace(0,pd.NA)
    tr1=(df['high']-df['low'])
    tr2=(df['high']-c.shift(1)).abs()
    tr3=(df['low']-c.shift(1)).abs()
    atr14=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1).rolling(14).mean()
    ind['atr14']=atr14
    high20=df['high'].rolling(20).max(); low20=df['low'].rolling(20).min()
    ind['keltner_width']=(high20-low20)/c*100
    ind['std20_pct']=c.rolling(20).std()/c*100
    ind['ema20']=c.ewm(span=20, adjust=False).mean()
    ind['ema20_dist']=(c/ind['ema20']-1)*100
    ind['mom10']=c-c.shift(10)
    ind['mom20']=c-c.shift(20)
    ind['hist_vol20']=c.pct_change().rolling(20).std()*(252**0.5)*100
    direction=c.diff().fillna(0).apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))
    obv=(direction*v).fillna(0).cumsum()
    ind['obv']=obv
    ind['obv_ma20']=obv.rolling(20).mean()
    ind['obv_pct_rank60']=(obv-obv.rolling(60).min())/(obv.rolling(60).max()-obv.rolling(60).min()).replace(0,pd.NA)*100
    tr_sum=atr14.rolling(14).sum()
    hh=df['high'].rolling(14).max(); ll=df['low'].rolling(14).min()
    ind['choppiness14']=100*(tr_sum/(hh-ll).replace(0,pd.NA)).apply(lambda x: pd.NA if pd.isna(x) or x<=0 else __import__('math').log10(x)/__import__('math').log10(14)*100)
    return ind

def trade_manage_t3_fee(df, i):
    entry = f(df.iloc[i+1].close)
    if not entry: return None
    stop = entry * 0.94
    target = entry * 1.06
    future = df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    size=1.0; realized=0.0; half=False; peak=entry
    hold=len(future); exitd=str(future.iloc[-1].time.date()); outcome='timeout'
    for n,(_,row) in enumerate(future.iterrows(),1):
        high=f(row.high); low=f(row.low); peak=max(peak, high)
        if n < MIN_HOLD:
            continue
        if not half and high >= target:
            realized += 0.5 * 6
            size = 0.5
            half = True
            stop = max(stop, entry * 1.005)
        if half:
            stop = max(stop, entry * 1.005, peak * 0.97)
        if low <= stop:
            realized += size * ((stop-entry)/entry*100)
            gross=realized; net=gross-FEE_PCT
            outcome='win' if net>0 else 'loss' if net<0 else 'flat'
            hold=n; exitd=str(row.time.date())
            return {'outcome':outcome,'entry':r(entry),'stopInitial':r(entry*0.94),'target':r(target),'grossPnlPct':r(gross),'netPnlPct':r(net),'feePct':FEE_PCT,'riskPct':6,'holdSessions':hold,'exitDate':exitd,'partialTaken':half}
    if size>0:
        last=f(future.iloc[-1].close)
        realized += size*((last-entry)/entry*100)
    gross=realized; net=gross-FEE_PCT
    outcome='win' if net>0 else 'loss' if net<0 else 'flat'
    return {'outcome':outcome,'entry':r(entry),'stopInitial':r(entry*0.94),'target':r(target),'grossPnlPct':r(gross),'netPnlPct':r(net),'feePct':FEE_PCT,'riskPct':6,'holdSessions':hold,'exitDate':exitd,'partialTaken':half}

def ml_pass(ai, row):
    rs_score = 0
    d1a_score = 0
    reasons = []

    # RS combo: ROC, Williams %R, SMA dist, Stoch, Choppiness, OBV
    if -6 <= f(ai.get('roc20')) <= 6:
        rs_score += 1
    else:
        reasons.append('roc_bad')
    wr = f(row.get('williams_r14'), -50)
    if -85 <= wr <= -35:
        rs_score += 1
    else:
        reasons.append('wr_bad')
    sma10_dist = f(row.get('sma10_dist'), 0)
    if -3.5 <= sma10_dist <= 2.5:
        rs_score += 1
    else:
        reasons.append('sma10_dist_bad')
    stoch_k = f(row.get('stoch_k'), 50)
    if 35 <= stoch_k <= 80:
        rs_score += 1
    else:
        reasons.append('stoch_bad')
    chop = f(row.get('choppiness14'), 50)
    if 38 <= chop <= 68:
        rs_score += 1
    else:
        reasons.append('chop_bad')
    obv_rank = f(row.get('obv_pct_rank60'), 50)
    if obv_rank >= 35:
        rs_score += 1
    else:
        reasons.append('obv_weak')

    # D1A combo: Keltner width, StdDev, EMA20, Momentum, HistVol
    kw = f(row.get('keltner_width'), 999)
    if 4 <= kw <= 18:
        d1a_score += 1
    else:
        reasons.append('keltner_bad')
    std20 = f(row.get('std20_pct'), 999)
    if 1.2 <= std20 <= 5.5:
        d1a_score += 1
    else:
        reasons.append('std_bad')
    ema20_dist = f(row.get('ema20_dist'), 999)
    if -2.5 <= ema20_dist <= 4.0:
        d1a_score += 1
    else:
        reasons.append('ema20_dist_bad')
    mom10 = f(row.get('mom10'), 0)
    mom20 = f(row.get('mom20'), 0)
    if mom10 >= -0.5 and mom20 >= -1.5:
        d1a_score += 1
    else:
        reasons.append('mom_bad')
    hv20 = f(row.get('hist_vol20'), 999)
    if 12 <= hv20 <= 55:
        d1a_score += 1
    else:
        reasons.append('histvol_bad')

    # Need both structure and confirmation, not just one side.
    ok = (rs_score >= 4 and d1a_score >= 3) or (rs_score >= 5 and d1a_score >= 2)
    return ok, rs_score, d1a_score, reasons

def summarize(trades):
    n=len(trades); wins=[t for t in trades if f(t.get('netPnlPct'))>0]; losses=[t for t in trades if f(t.get('netPnlPct'))<0]
    avg=lambda xs,k: round(sum(f(x.get(k)) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x.get(k)) for x in xs),2) if xs else 0
    return {'trades':n,'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgNetPnlPct':avg(trades,'netPnlPct'),'sumNetPnlPct':sm(trades,'netPnlPct'),'avgGrossPnlPct':avg(trades,'grossPnlPct'),'avgHold':avg(trades,'holdSessions')}

def run():
    symbols=[s for s in lh1.TECHNICAL_UNIVERSE[:50] if s not in lh1.EXCLUDE]
    histories=load_histories(symbols)
    trades=[]; rejects=Counter(); counts={}
    for sym,df in histories.items():
        if df is None or df.empty or len(df)<260:
            counts[sym]={'error':'missing/short'}; continue
        ind=add_ml_features(df, _compute_indicators(df.copy()))
        c={'loops':0,'trades':0}
        used_until=-1
        for i in range(200, len(df)-HORIZON-2):
            if i<=used_until: continue
            t=pd.Timestamp(df.iloc[i].time)
            if t<START or t>=END: continue
            c['loops']+=1
            hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
            rs=calc_rs_levels_only(price, f(df.iloc[i].open), f(df.iloc[i].open), f(df.iloc[i].high), f(df.iloc[i].low), price, hist)
            ai=lh1.action_indicators(price,row,hist,ind.iloc[:i+1].copy())
            ok0,reason=lh1.pass_b4(price,rs,ai)
            if not ok0:
                rejects['base_'+reason]+=1; continue
            ok1, rs_score, d1a_score, bads = ml_pass(ai, row)
            if not ok1:
                rejects['ml_reject']+=1
                for b in bads: rejects['ml_'+b]+=1
                continue
            tr=trade_manage_t3_fee(df,i)
            if not tr: continue
            sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
            dist=(price-sup)/price*100 if price and sup else 999
            tr.update({'symbol':sym,'signalDate':str(df.iloc[i].time.date()),'entryDate':str(df.iloc[i+1].time.date()),'strategy':'LH1_v2_ml_combo','distSupportPct':r(dist),'support':rs.get('activeSupportDay'),'resistance':rs.get('activeResistanceDay'),'entryIndicators':ai,'mlScores':{'rsScore':rs_score,'d1aScore':d1a_score,'williamsR14':r(row.get('williams_r14'),2),'sma10Dist':r(row.get('sma10_dist'),2),'stochK':r(row.get('stoch_k'),2),'choppiness14':r(row.get('choppiness14'),2),'obvPctRank60':r(row.get('obv_pct_rank60'),2),'keltnerWidth':r(row.get('keltner_width'),2),'std20Pct':r(row.get('std20_pct'),2),'ema20Dist':r(row.get('ema20_dist'),2),'mom10':r(row.get('mom10'),2),'mom20':r(row.get('mom20'),2),'histVol20':r(row.get('hist_vol20'),2)}})
            trades.append(tr); c['trades']+=1; used_until=i+tr['holdSessions']+1
        counts[sym]=c
        print(sym,c,flush=True)
    payload={'createdAt':pd.Timestamp.now().isoformat(),'strategy':'LH1_v2_ml_combo','source':str(SRC),'rules':{'base':'canonical LH1 pass_b4','mlComboRS':['ROC','WILLIAMS_R','SMA','STOCHASTIC','CHOPPINESS','OBV'],'mlComboD1A':['KELTNER','STDDEV','EMA','MOMENTUM','HIST_VOL'],'passRule':'(RS>=4 and D1A>=3) or (RS>=5 and D1A>=2)','minHold':'T+3 / 3 bars','feePct':FEE_PCT},'windows':{},'rejects':dict(rejects.most_common(80)),'counts':counts,'trades':trades}
    for w,(st,en) in WINDOWS.items():
        sub=[x for x in trades if st<=pd.Timestamp(x['signalDate'])<en]
        payload['windows'][w]=summarize(sub)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['windows'],ensure_ascii=False,indent=2))
if __name__=='__main__': run()
