from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _compute_indicators, _build_support_resistance, _pivot_from_recent, _pivot_levels
from app.technical_filters import TECHNICAL_UNIVERSE
try:
    from vnstock import Quote
except Exception:
    Quote = None

REM=Path('data/vn100_remaining_symbols.json')
OUT=Path('data/hourly_indicators_vn100_cache.json')
TMP=Path('data/hourly_indicators_vn100_cache.partial.json')
SLEEP_EVERY=18
SLEEP_SECONDS=65
MIN_BARS=80


def universe():
    base=[str(s).strip().upper() for s in TECHNICAL_UNIVERSE if str(s).strip()]
    extra=[]
    if REM.exists():
        try: extra=[str(s).strip().upper() for s in json.loads(REM.read_text(encoding='utf-8')).get('symbols',[]) if str(s).strip()]
        except Exception: extra=[]
    out=[]
    for s in base+extra:
        if s not in out: out.append(s)
    return out

def load_partial():
    if not TMP.exists(): return [], []
    try:
        d=json.loads(TMP.read_text(encoding='utf-8'))
        return d.get('items',[]), d.get('errors',[])
    except Exception: return [], []

def save(items, errors, uni, final=False):
    payload={'createdAt':datetime.now().isoformat(),'universe':'VN100 local universe','method':'1H indicators/support-resistance precomputed locally; output-only for web','interval':'1H','universeCount':len(uni),'count':len(items),'errorCount':len(errors),'items':items,'errors':errors}
    (OUT if final else TMP).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

def f(v, default=None):
    try:
        if v is None or pd.isna(v): return default
        return float(v)
    except Exception: return default

def r(v,n=2):
    x=f(v,None)
    return round(x,n) if x is not None else None

def fetch_hour(sym):
    if Quote is None: raise RuntimeError('Quote unavailable')
    df=Quote(symbol=sym, source='VCI').history(start='2025-01-01', end=pd.Timestamp.today().strftime('%Y-%m-%d'), interval='1H')
    if not isinstance(df,pd.DataFrame) or df.empty: raise RuntimeError('missing 1H history')
    df=df.rename(columns={'datetime':'time','date':'time','Date':'time'})
    if 'volume' not in df.columns: df['volume']=0
    need=['time','open','high','low','close','volume']
    if any(c not in df.columns for c in need): raise RuntimeError(f'missing cols {df.columns.tolist()}')
    df=df[need].dropna().copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    return df

def run(sym):
    df=fetch_hour(sym)
    if len(df)<MIN_BARS: return None, f'insufficient 1H history {len(df)}'
    calc=_compute_indicators(df.copy()); row=calc.iloc[-1]
    last=df.iloc[-1]; price=float(last['close']); high=float(last['high']); low=float(last['low'])
    pivot,s1,r1,s2,r2=_pivot_from_recent(df, high, low, price, 20)
    ma20=f(row.get('ma20'),price); ma50=f(row.get('ma50'),ma20); ma200=f(row.get('ma200'),ma50)
    sr=_build_support_resistance(price, df.tail(240), pivot, s1, r1, s2, r2, ma20, ma50, ma200)
    item={
        'symbol':sym,'date':str(last['time']),'price':round(price,2),
        'rsi14Hour':r(row.get('rsi14')),'adx14Hour':r(row.get('adx14')),'plusDiHour':r(row.get('plusDi')),'minusDiHour':r(row.get('minusDi')),
        'ma20Hour':r(ma20),'ma50Hour':r(ma50),'ma200Hour':r(ma200),
        'bbUpperHour':r(row.get('bbUpper')),'bbLowerHour':r(row.get('bbLower')),'bbMiddleHour':r(row.get('bbMid')),'bbPercentHour':r(row.get('bbPercent'),3),
        'pivotHour':r(pivot),'supportHour':r(sr['activeSupport']),'resistanceHour':r(sr['activeResistance']),
        'supportLevelsHour':[round(float(x),1) for x in sr.get('supports',[])],
        'resistanceLevelsHour':[round(float(x),1) for x in sr.get('resistances',[])],
        'activeSupportHour':r(sr['activeSupport'],1),'activeResistanceHour':r(sr['activeResistance'],1),'srStatusHour':sr.get('srStatus'),
    }
    return item,None

def main():
    uni=universe(); items,errors=load_partial(); done={x.get('symbol') for x in items}|{x.get('symbol') for x in errors}; calls=0
    print('VN100 hourly universe',len(uni),'already done',len(done),flush=True)
    for sym in uni:
        if sym in done:
            print(sym,'SKIP',flush=True); continue
        if calls and calls%SLEEP_EVERY==0:
            print('sleep',SLEEP_SECONDS,'seconds for rate limit',flush=True); time.sleep(SLEEP_SECONDS)
        try:
            item,err=run(sym); calls+=1
            if item:
                items.append(item); print(sym,'OK',item.get('rsi14Hour'),item.get('activeSupportHour'),item.get('activeResistanceHour'),flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',repr(e),flush=True)
        save(items,errors,uni,final=False)
    save(items,errors,uni,final=True); print('saved',OUT,'count',len(items),'errors',len(errors),flush=True)
if __name__=='__main__': main()
