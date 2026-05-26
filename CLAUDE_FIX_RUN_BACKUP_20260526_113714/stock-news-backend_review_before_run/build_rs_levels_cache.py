from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from app.market_data import _load_history, _calc_technical
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/rs_levels_cache.json')
EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]


def sf(x):
    try:
        if x is None or x=='': return None
        v=float(x)
        if pd.isna(v): return None
        return v
    except Exception:
        return None

def enrich_last(df):
    if df is None or df.empty: return {}
    d=df.copy().sort_values('time').reset_index(drop=True)
    for c in ['open','high','low','close','volume']:
        d[c]=pd.to_numeric(d[c],errors='coerce')
    close=d.close; high=d.high; low=d.low
    ma20=close.rolling(20).mean().iloc[-1] if len(d)>=20 else None
    ma50=close.rolling(50).mean().iloc[-1] if len(d)>=50 else None
    ma200=close.rolling(200).mean().iloc[-1] if len(d)>=200 else None
    delta=close.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); rsi=(100-(100/(1+gain/loss.replace(0,float('nan'))))).iloc[-1]
    ema12=close.ewm(span=12,adjust=False).mean(); ema26=close.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; hist=(macd-macd.ewm(span=9,adjust=False).mean()).iloc[-1]
    vol20=d.volume.rolling(20).mean().iloc[-1] if len(d)>=20 else None
    vol_ratio=(d.volume.iloc[-1]/vol20) if vol20 and vol20>0 else None
    tr=pd.concat([(high-low),(high-close.shift()).abs(),(low-close.shift()).abs()],axis=1).max(axis=1)
    atr=tr.ewm(alpha=1/14,adjust=False).mean().iloc[-1] if len(d)>=14 else None
    return {"ma20":sf(ma20),"ma50":sf(ma50),"ma200":sf(ma200),"rsi14":sf(rsi),"macdHistogram":sf(hist),"volumeRatio":sf(vol_ratio),"atr14":sf(atr)}

def pull_levels(tech):
    def first(*keys):
        for k in keys:
            v=sf(tech.get(k))
            if v and v>0: return v
        return None
    return {
        'supportDay': first('activeSupportDay','supportDay','nearestSupport','support'),
        'resistanceDay': first('activeResistanceDay','resistanceDay','nearestResistance','resistance'),
        'supportWeek': first('activeSupportWeek','supportWeek'),
        'resistanceWeek': first('activeResistanceWeek','resistanceWeek'),
        'supportMonth': first('activeSupportMonth','supportMonth'),
        'resistanceMonth': first('activeResistanceMonth','resistanceMonth'),
    }

def fallback_levels(df, price):
    d=df.copy().sort_values('time').reset_index(drop=True)
    for c in ['high','low','close']: d[c]=pd.to_numeric(d[c],errors='coerce')
    hist=d.tail(80)
    lows=[float(x) for x in hist.low.dropna().tolist() if float(x)<=price*1.01]
    highs=[float(x) for x in hist.high.dropna().tolist() if float(x)>price]
    return (max(lows) if lows else None, min(highs) if highs else None)

def build_symbol(sym):
    df=_load_history(sym)
    if df is None or df.empty or len(df)<30:
        return None, 'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True)
    last=df.iloc[-1]
    price=sf(last.get('close'))
    if not price: return None, 'missing price'
    # Calculate once now, then persist. Future strategy reads this file only.
    tech=_calc_technical(price, sf(last.get('open')) or price, sf(last.get('open')) or price, sf(last.get('high')) or price, sf(last.get('low')) or price, price, df)
    lv=pull_levels(tech)
    if not lv['supportDay'] or not lv['resistanceDay']:
        fs,fr=fallback_levels(df, price)
        lv['supportDay']=lv['supportDay'] or fs
        lv['resistanceDay']=lv['resistanceDay'] or fr
    ind=enrich_last(df)
    return {
        'symbol':sym,
        'date':str(pd.to_datetime(last.get('time')).date()),
        'price':round(price,2),
        **{k:(round(v,2) if isinstance(v,float) else v) for k,v in lv.items()},
        **{k:(round(v,4) if isinstance(v,float) else v) for k,v in ind.items()},
        'trend':tech.get('effectiveTrend') or tech.get('trend'),
        'supportStrengthDay':tech.get('supportStrengthDay'),
        'resistanceStrengthDay':tech.get('resistanceStrengthDay'),
    }, None

def main():
    rows=[]; errors=[]
    for sym in UNIVERSE:
        try:
            row,err=build_symbol(sym)
            if row: rows.append(row); print(sym,'OK',flush=True)
            else: errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':str(e)}); print(sym,'ERR',e,flush=True)
    payload={'createdAt':datetime.now(timezone.utc).isoformat(),'note':'Precomputed R/S + indicators cache. Strategy/web must read this file, not rerun R/S. VIC/VHM excluded.','excluded':sorted(EXCLUDE),'universe':UNIVERSE,'count':len(rows),'items':rows,'errors':errors}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('saved',OUT,'count',len(rows),'errors',len(errors))
if __name__=='__main__': main()
