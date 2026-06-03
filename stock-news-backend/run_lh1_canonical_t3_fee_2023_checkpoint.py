from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
import pandas as pd

import backtest_b4_trend_pullback_locked as lh1
from app.market_data import _compute_indicators
from app.rs_levels import calc_rs_levels_only

SRC = Path('data/vn100_history_from_2023.json')
OUT = Path('data/lh1_canonical_t3_fee_2023_to_now.json')
CHECKPOINT = Path('data/lh1_canonical_t3_fee_2023_to_now.checkpoint.json')
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
            gross=realized
            net=gross-FEE_PCT
            outcome='win' if net>0 else 'loss' if net<0 else 'flat'
            hold=n; exitd=str(row.time.date())
            return {'outcome':outcome,'entry':r(entry),'stopInitial':r(entry*0.94),'target':r(target),'grossPnlPct':r(gross),'netPnlPct':r(net),'feePct':FEE_PCT,'riskPct':6,'holdSessions':hold,'exitDate':exitd,'partialTaken':half}
    if size>0:
        last=f(future.iloc[-1].close)
        realized += size*((last-entry)/entry*100)
    gross=realized; net=gross-FEE_PCT
    outcome='win' if net>0 else 'loss' if net<0 else 'flat'
    return {'outcome':outcome,'entry':r(entry),'stopInitial':r(entry*0.94),'target':r(target),'grossPnlPct':r(gross),'netPnlPct':r(net),'feePct':FEE_PCT,'riskPct':6,'holdSessions':hold,'exitDate':exitd,'partialTaken':half}

def summarize(trades):
    n=len(trades); wins=[t for t in trades if f(t.get('netPnlPct'))>0]; losses=[t for t in trades if f(t.get('netPnlPct'))<0]
    avg=lambda xs,k: round(sum(f(x.get(k)) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x.get(k)) for x in xs),2) if xs else 0
    return {'trades':n,'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgNetPnlPct':avg(trades,'netPnlPct'),'sumNetPnlPct':sm(trades,'netPnlPct'),'avgGrossPnlPct':avg(trades,'grossPnlPct'),'avgHold':avg(trades,'holdSessions')}

def finalize(payload):
    payload['windows']={}
    trades=payload.get('trades', [])
    for w,(st,en) in WINDOWS.items():
        sub=[x for x in trades if st<=pd.Timestamp(x['signalDate'])<en]
        payload['windows'][w]=summarize(sub)
    payload['createdAt']=pd.Timestamp.now().isoformat()
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    CHECKPOINT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

def run():
    symbols=[s for s in lh1.TECHNICAL_UNIVERSE[:50] if s not in lh1.EXCLUDE]
    histories=load_histories(symbols)
    if CHECKPOINT.exists():
        try:
            payload=json.loads(CHECKPOINT.read_text(encoding='utf-8'))
        except Exception:
            payload={}
    else:
        payload={}
    payload.setdefault('strategy','LH1 Pullback')
    payload.setdefault('source',str(SRC))
    payload.setdefault('universe','backtest_b4_trend_pullback_locked.TECHNICAL_UNIVERSE[:50] excluding EXCLUDE')
    payload.setdefault('rules',{'minHold':'T+3 / 3 bars','feePct':FEE_PCT,'entry':'next close after signal','exit':'canonical LH1 partial/trailing, exits ignored before T+3'})
    payload.setdefault('rejects',{})
    payload.setdefault('counts',{})
    payload.setdefault('trades',[])
    done=set(payload.get('counts',{}).keys())
    rejects=Counter(payload.get('rejects',{}))
    for idx,sym in enumerate(symbols,1):
        if sym in done:
            print('skip', idx, sym, flush=True); continue
        df=histories.get(sym)
        if df is None or df.empty or len(df)<260:
            payload['counts'][sym]={'error':'missing/short'}; finalize(payload); print('short', idx, sym, flush=True); continue
        ind=_compute_indicators(df.copy())
        c={'loops':0,'trades':0}
        used_until=-1
        print('start', idx, '/', len(symbols), sym, 'rows', len(df), flush=True)
        for i in range(100, len(df)-HORIZON-2):
            if i<=used_until: continue
            t=pd.Timestamp(df.iloc[i].time)
            if t<START or t>=END: continue
            c['loops']+=1
            hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
            rs=calc_rs_levels_only(price, f(df.iloc[i].open), f(df.iloc[i].open), f(df.iloc[i].high), f(df.iloc[i].low), price, hist)
            ai=lh1.action_indicators(price,row,hist,ind.iloc[:i+1].copy())
            ok,reason=lh1.pass_b4(price,rs,ai)
            if not ok:
                rejects[reason]+=1; continue
            tr=trade_manage_t3_fee(df,i)
            if not tr: continue
            sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
            dist=(price-sup)/price*100 if price and sup else 999
            tr.update({'symbol':sym,'signalDate':str(df.iloc[i].time.date()),'entryDate':str(df.iloc[i+1].time.date()),'strategy':'LH1 Pullback canonical pass_b4 + T3 fee','distSupportPct':r(dist),'support':rs.get('activeSupportDay'),'resistance':rs.get('activeResistanceDay'),'entryIndicators':ai})
            payload['trades'].append(tr); c['trades']+=1; used_until=i+tr['holdSessions']+1
        payload['counts'][sym]=c
        payload['rejects']=dict(rejects.most_common(50))
        finalize(payload)
        print('done', idx, sym, c, flush=True)
    finalize(payload)
    print(json.dumps(payload['windows'],ensure_ascii=False,indent=2), flush=True)
if __name__=='__main__': run()
