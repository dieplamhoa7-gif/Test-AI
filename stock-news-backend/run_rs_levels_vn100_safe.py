from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/rs_levels_vn100_cache.json')
TMP=Path('data/rs_levels_vn100_cache.partial.json')
REM=Path('data/vn100_remaining_symbols.json')
SLEEP_EVERY=18
SLEEP_SECONDS=65
MIN_HISTORY=30


def load_universe() -> list[str]:
    base=[str(s).strip().upper() for s in TECHNICAL_UNIVERSE if str(s).strip()]
    extra=[]
    if REM.exists():
        try:
            data=json.loads(REM.read_text(encoding='utf-8'))
            extra=[str(s).strip().upper() for s in data.get('symbols',[]) if str(s).strip()]
        except Exception:
            extra=[]
    universe=[]
    for s in base+extra:
        if s and s not in universe:
            universe.append(s)
    return universe


def load_partial():
    if not TMP.exists(): return [], []
    try:
        d=json.loads(TMP.read_text(encoding='utf-8'))
        return d.get('items',[]), d.get('errors',[])
    except Exception:
        return [], []


def save(items, errors, universe, final=False):
    payload={
        'createdAt':datetime.now().isoformat(),
        'universe':'VN100 local universe = TECHNICAL_UNIVERSE + data/vn100_remaining_symbols.json',
        'method':'R/S-only VN100 cache; calc_rs_levels_only with per-timeframe MA anchors; output-only for web',
        'universeCount':len(universe),
        'count':len(items),
        'errorCount':len(errors),
        'items':items,
        'errors':errors,
    }
    (OUT if final else TMP).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')


def run_symbol(sym:str):
    df=_load_history(sym)
    if df is None or df.empty: return None,'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    if len(df)<MIN_HISTORY: return None,f'insufficient history {len(df)}'
    last=df.iloc[-1]; price=float(last['close'])
    rs=calc_rs_levels_only(price,float(last.get('open',price)),float(last.get('open',price)),float(last.get('high',price)),float(last.get('low',price)),price,df)
    return {'symbol':sym,'date':str(last['time'].date()),'price':round(price,2),**rs},None


def main():
    universe=load_universe(); items, errors=load_partial()
    done={x.get('symbol') for x in items}|{x.get('symbol') for x in errors}
    calls=0
    print('VN100 universe',len(universe),'already done',len(done),flush=True)
    for sym in universe:
        if sym in done:
            print(sym,'SKIP',flush=True); continue
        if calls and calls % SLEEP_EVERY == 0:
            print('sleep',SLEEP_SECONDS,'seconds for rate limit',flush=True); time.sleep(SLEEP_SECONDS)
        try:
            item,err=run_symbol(sym); calls+=1
            if item:
                items.append(item); print(sym,'OK',item.get('activeSupportWeek'),item.get('activeResistanceWeek'),item.get('activeSupportMonth'),item.get('activeResistanceMonth'),flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',repr(e),flush=True)
        save(items,errors,universe,final=False)
    save(items,errors,universe,final=True)
    print('saved',OUT,'universe',len(universe),'count',len(items),'errors',len(errors),flush=True)

if __name__=='__main__': main()
