from __future__ import annotations
import json
import importlib.util
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.market_data import _load_history,_compute_indicators
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

spec=importlib.util.spec_from_file_location('focused','backtest_v3_target_pct_exact_focused.py')
focused=importlib.util.module_from_spec(spec); spec.loader.exec_module(focused)
OUT=Path('data/v3_target_pct_exact_prev3m_backtest.json')
HORIZON=42
CONFIG={'targetPct':0.06,'minScore':68,'maxDist':3,'maxRisk':5}

def f(v,d=0.0):
    try:
        if v is None: return d
        if hasattr(v,'item'): v=v.item()
        if pd.isna(v): return d
        return float(v)
    except Exception: return d

def main():
    # Previous 3 months before current 180-day window: roughly now-270d to now-180d.
    end=pd.Timestamp(datetime.now()-timedelta(days=180))
    start=pd.Timestamp(datetime.now()-timedelta(days=270))
    trades=[]; counts={}
    for sym in TECHNICAL_UNIVERSE[:50]:
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<260:
                counts[sym]={'error':'missing/short','rows':0 if df is None else len(df)}; print(sym,'ERR'); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
            c={'loops':0,'signals':0,'trades':0}
            for i in range(100,len(df)-HORIZON-2):
                t=df.iloc[i].time
                if t<start or t>=end: continue
                c['loops']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
                rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist)
                meta=focused.score_meta(price,rs,row,hist,ind.iloc[:i+1].copy())
                if meta['rsi']<32 or meta['bbPercent']>0.9 or meta['volumeRatio']>3 or meta['roc20']<-10: continue
                if meta['score']<CONFIG['minScore'] or meta['dist']>CONFIG['maxDist']: continue
                tr=focused.trade(df,i,meta,CONFIG)
                if tr:
                    tr.update({'symbol':sym,'date':str(df.iloc[i+1].time.date()),'score':meta['score'],'distSupportPct':meta['dist'],'rsi':meta['rsi'],'ichimoku':meta['ichimoku'],'bullishDivergence':meta['bullishDivergence']})
                    trades.append(tr); c['trades']+=1
                c['signals']+=1
            counts[sym]=c; print(sym,c,flush=True)
        except Exception as e:
            counts[sym]={'error':repr(e)}; print(sym,'ERR',e,flush=True)
    payload={'createdAt':datetime.now().isoformat(),'sample':f'Previous 3 months before current 180-day test window: {start.date()} to {end.date()}, TECHNICAL_UNIVERSE first 50','config':{'targetPct':6,'minScore':68,'maxDistSupportPct':3,'maxRiskPct':5,'horizon':HORIZON},'summary':focused.summ(trades),'trades':trades,'counts':counts}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'sample':payload['sample'],'summary':payload['summary']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
