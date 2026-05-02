from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/rs_levels_only_cache.json')
TMP=Path('data/rs_levels_only_cache.partial.json')
SLEEP_EVERY=18
SLEEP_SECONDS=65

def load_partial():
    if not TMP.exists():
        return [], []
    try:
        d=json.loads(TMP.read_text(encoding='utf-8'))
        return d.get('items',[]), d.get('errors',[])
    except Exception:
        return [], []

def save(items, errors, final=False):
    payload={
        'createdAt':datetime.now().isoformat(),
        'method':'R/S-only cache from app.rs_levels.calc_rs_levels_only; full safe rerun with rate-limit sleeps; web reads output only',
        'count':len(items),
        'errorCount':len(errors),
        'universe':TECHNICAL_UNIVERSE,
        'items':items,
        'errors':errors,
    }
    (OUT if final else TMP).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

def run_symbol(sym:str):
    df=_load_history(sym)
    if df is None or df.empty:
        return None,'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    last=df.iloc[-1]
    price=float(last['close'])
    rs=calc_rs_levels_only(price,float(last.get('open',price)),float(last.get('open',price)),float(last.get('high',price)),float(last.get('low',price)),price,df)
    return {'symbol':sym,'date':str(last['time'].date()),'price':round(price,2),**rs},None

def main():
    items, errors = load_partial()
    done={x.get('symbol') for x in items} | {x.get('symbol') for x in errors}
    calls=0
    for sym in TECHNICAL_UNIVERSE:
        if sym in done:
            print(sym,'SKIP',flush=True); continue
        if calls and calls % SLEEP_EVERY == 0:
            print('sleep',SLEEP_SECONDS,'seconds for rate limit',flush=True)
            time.sleep(SLEEP_SECONDS)
        try:
            item,err=run_symbol(sym)
            calls+=1
            if item:
                items.append(item); print(sym,'OK',item.get('supportDay'),item.get('resistanceDay'),flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':str(e)}); print(sym,'ERR',e,flush=True)
        save(items, errors, final=False)
    save(items, errors, final=True)
    print('saved',OUT,'count',len(items),'errors',len(errors),flush=True)

if __name__=='__main__': main()
