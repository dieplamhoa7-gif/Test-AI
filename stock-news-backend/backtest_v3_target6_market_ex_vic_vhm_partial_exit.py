from __future__ import annotations
import json
import importlib.util
import time
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.market_data import _load_history,_compute_indicators
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

spec=importlib.util.spec_from_file_location('focused','backtest_v3_target_pct_exact_focused.py')
focused=importlib.util.module_from_spec(spec); spec.loader.exec_module(focused)
OUT=Path('data/v3_target6_market_ex_vic_vhm_partial_exit_backtest.json')
HORIZON=42
CONFIG={'targetPct':0.06,'minScore':68,'maxDist':3,'maxRisk':5}
EXCLUDE={'VIC','VHM'}

def f(v,d=0.0):
    try:
        if v is None: return d
        if hasattr(v,'item'): v=v.item()
        if pd.isna(v): return d
        return float(v)
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def ema(s,span): return s.ewm(span=span,adjust=False).mean()

def load_histories(symbols):
    out={}
    for idx,sym in enumerate(symbols,1):
        try:
            df=_load_history(sym)
            out[sym]=df
            print('history',idx,sym,0 if df is None else len(df),flush=True)
        except Exception as e:
            out[sym]=None
            print('history',idx,sym,'ERR',e,flush=True)
        if idx % 15 == 0:
            time.sleep(40)
        else:
            time.sleep(1.2)
    return out


def market_proxy(symbols, histories):
    frames=[]
    for sym in symbols:
        if sym in EXCLUDE: continue
        df=histories.get(sym)
        if df is None or df.empty: continue
        d=df.copy(); d['time']=pd.to_datetime(d.time); d=d.sort_values('time')
        d=d[['time','close']].dropna();
        if d.empty: continue
        d['norm']=pd.to_numeric(d.close,errors='coerce')/float(d.close.iloc[0])*100
        frames.append(d[['time','norm']].rename(columns={'norm':sym}))
    if not frames: return pd.DataFrame()
    out=frames[0]
    for fr in frames[1:]: out=out.merge(fr,on='time',how='outer')
    out=out.sort_values('time').ffill().dropna(how='all')
    cols=[c for c in out.columns if c!='time']; out['proxy']=out[cols].mean(axis=1)
    out['ma20']=out.proxy.rolling(20).mean(); out['ma50']=out.proxy.rolling(50).mean()
    macd=ema(out.proxy,12)-ema(out.proxy,26); out['macdHist']=macd-ema(macd,9)
    delta=out.proxy.diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta.clip(upper=0)).rolling(14).mean(); out['rsi']=100-(100/(1+gain/loss.replace(0,1e-9)))
    out['regimeOk']= (out.proxy>=out.ma20) & (out.ma20>=out.ma50*0.985) & (out.rsi>=45) & (out.macdHist>=out.macdHist.shift(1))
    return out[['time','proxy','ma20','ma50','rsi','macdHist','regimeOk']]

def regime_at(proxy,date):
    if proxy.empty: return False, {}
    d=proxy[proxy.time<=date]
    if d.empty: return False, {}
    row=d.iloc[-1]
    return bool(row.regimeOk), {'proxy':r(row.proxy),'ma20':r(row.ma20),'ma50':r(row.ma50),'rsi':r(row.rsi),'macdHist':r(row.macdHist,4),'regimeOk':bool(row.regimeOk)}

def trade_partial(df,i,meta,cfg):
    entry=f(df.iloc[i+1].close); low=f(meta['supportZone'][0],meta['support']*0.985)
    stop=max(low*0.98, entry*(1-cfg['maxRisk']/100)); risk=(entry-stop)/entry*100
    if risk<=0 or risk>cfg['maxRisk']: return None
    t1=entry*1.03; t2=entry*(1+cfg['targetPct']); trail_active=False; half_done=False; realized=0.0; size=1.0; peak=entry
    future=df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    outcome='timeout'; hold=len(future); exitd=str(future.iloc[-1].time.date()); last_close=f(future.iloc[-1].close)
    for n,(_,row) in enumerate(future.iterrows(),1):
        high=f(row.high); lowp=f(row.low); close=f(row.close); peak=max(peak,high)
        if not half_done and high>=t1:
            realized += 0.5*3.0; size=0.5; half_done=True; trail_active=True; stop=max(stop, entry*1.005)
        # chốt lời khi có điều chỉnh sau khi đã đạt t1: trailing stop 3% từ peak hoặc về breakeven+
        if trail_active:
            trail=max(entry*1.005, peak*0.97)
            stop=max(stop,trail)
        hit_stop=lowp<=stop; hit_t2=high>=t2
        if hit_t2:
            realized += size*cfg['targetPct']*100; outcome='win'; hold=n; exitd=str(row.time.date()); size=0; break
        if hit_stop:
            realized += size*((stop-entry)/entry*100); outcome='partial_win' if realized>0 else 'loss'; hold=n; exitd=str(row.time.date()); size=0; break
    if size>0:
        realized += size*((last_close-entry)/entry*100)
        outcome='partial_win' if realized>0 and half_done else 'timeout'
    return {'outcome':outcome,'entry':r(entry),'stopInitial':r(max(low*0.98, entry*(1-cfg['maxRisk']/100))),'pnlPct':r(realized),'riskPct':r(risk),'target1Pct':3,'target2Pct':cfg['targetPct']*100,'holdSessions':hold,'exitDate':exitd,'partialTaken':half_done}

def summ(ts):
    n=len(ts); wins=[x for x in ts if x['pnlPct']>0]; losses=[x for x in ts if x['pnlPct']<0]; flat=[x for x in ts if x['pnlPct']==0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(wins),'losses':len(losses),'flats':len(flat),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(wins,'pnlPct'),'avgLossPct':avg(losses,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def run_window(name,start,end,proxy,histories):
    trades=[]; counts={}
    for sym in TECHNICAL_UNIVERSE[:50]:
        if sym in EXCLUDE: continue
        try:
            df=histories.get(sym)
            if df is None or df.empty or len(df)<260:
                counts[sym]={'error':'missing/short','rows':0 if df is None else len(df)}; continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
            c={'loops':0,'regimePass':0,'signals':0,'trades':0}
            for i in range(100,len(df)-HORIZON-2):
                t=df.iloc[i].time
                if t<start or t>=end: continue
                c['loops']+=1; ok_reg,reg=regime_at(proxy,t)
                if not ok_reg: continue
                c['regimePass']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
                rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist)
                meta=focused.score_meta(price,rs,row,hist,ind.iloc[:i+1].copy())
                if meta['rsi']<32 or meta['bbPercent']>0.9 or meta['volumeRatio']>3 or meta['roc20']<-10: continue
                if meta['score']<CONFIG['minScore'] or meta['dist']>CONFIG['maxDist']: continue
                tr=trade_partial(df,i,meta,CONFIG)
                if tr:
                    tr.update({'symbol':sym,'date':str(df.iloc[i+1].time.date()),'score':meta['score'],'distSupportPct':meta['dist'],'rsi':meta['rsi'],'ichimoku':meta['ichimoku'],'bullishDivergence':meta['bullishDivergence'],'marketRegime':reg})
                    trades.append(tr); c['trades']+=1
                c['signals']+=1
            counts[sym]=c; print(name,sym,c,flush=True)
        except Exception as e:
            counts[sym]={'error':repr(e)}; print(name,sym,'ERR',e,flush=True)
    return {'window':name,'start':str(start.date()),'end':str(end.date()),'summary':summ(trades),'trades':trades,'counts':counts}

def main():
    symbols=TECHNICAL_UNIVERSE[:50]
    histories=load_histories(symbols)
    proxy=market_proxy(symbols,histories)
    now=pd.Timestamp(datetime.now())
    current_start=now-timedelta(days=180); current_end=now
    prev_start=now-timedelta(days=270); prev_end=now-timedelta(days=180)
    cur=run_window('current180',current_start,current_end,proxy,histories)
    prev=run_window('prev3m',prev_start,prev_end,proxy,histories)
    payload={'createdAt':datetime.now().isoformat(),'method':'V3 target +6% with market proxy regime excluding VIC/VHM and partial exit: sell 50% at +3%, remaining target +6%, trail on correction. No stock trend/ADX, bullish divergence bonus only.','excludeFromTradingAndProxy':list(EXCLUDE),'config':{'target2Pct':6,'target1Pct':3,'minScore':68,'maxDistSupportPct':3,'maxRiskPct':5,'marketRegime':'equal-weight proxy ex VIC/VHM: proxy>=MA20, MA20>=MA50*0.985, RSI>=45, MACD hist improving'},'proxySampleRows':len(proxy),'current180':cur,'prev3m':prev}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'current180':cur['summary'],'prev3m':prev['summary']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
