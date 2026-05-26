from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/rs_levels_only_cache.json')
EXCLUDE=set()

def run_symbol(sym:str):
    df=_load_history(sym)
    if df is None or df.empty:
        return None,'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    last=df.iloc[-1]
    price=float(last['close'])
    rs=calc_rs_levels_only(price,float(last.get('open',price)),float(last.get('open',price)),float(last.get('high',price)),float(last.get('low',price)),price,df)
    return {
        'symbol':sym,
        'date':str(last['time'].date()),
        'price':round(price,2),
        **rs,
    },None

def main():
    items=[]; errors=[]
    for sym in [s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]:
        try:
            item,err=run_symbol(sym)
            if item:
                items.append(item); print(sym,'OK',item.get('supportDay'),item.get('resistanceDay'),flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':str(e)}); print(sym,'ERR',e,flush=True)
    payload={
        'createdAt':datetime.now().isoformat(),
        'method':'R/S-only cache from app.rs_levels.calc_rs_levels_only; avoids full _calc_technical indicators/recommendations',
        'count':len(items),
        'errorCount':len(errors),
        'items':items,
        'errors':errors,
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('saved',OUT,'count',len(items),'errors',len(errors))
if __name__=='__main__': main()
