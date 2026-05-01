from __future__ import annotations
import json, importlib.util, time
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.market_data import _load_history,_compute_indicators
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE
spec=importlib.util.spec_from_file_location('focused','backtest_v3_target_pct_exact_focused.py')
focused=importlib.util.module_from_spec(spec); spec.loader.exec_module(focused)
OUT=Path('data/v3_target6_partial_at6_exact_future_backtest.json')
EXCLUDE={'VIC','VHM'}; HORIZON=42
CONFIG={'targetPct':0.06,'minScore':68,'maxDist':3,'maxRisk':5}

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
            df=_load_history(sym); out[sym]=df; print('history',idx,sym,0 if df is None else len(df),flush=True)
        except Exception as e:
            out[sym]=None; print('history',idx,sym,'ERR',e,flush=True)
        if idx%15==0: time.sleep(40)
        else: time.sleep(1.1)
    return out

def market_proxy(symbols,histories):
    frames=[]
    for sym in symbols:
        if sym in EXCLUDE: continue
        df=histories.get(sym)
        if df is None or df.empty: continue
        d=df.copy(); d['time']=pd.to_datetime(d.time); d=d.sort_values('time'); d=d[['time','close']].dropna()
        if d.empty: continue
        d['norm']=pd.to_numeric(d.close,errors='coerce')/float(d.close.iloc[0])*100
        frames.append(d[['time','norm']].rename(columns={'norm':sym}))
    out=frames[0]
    for fr in frames[1:]: out=out.merge(fr,on='time',how='outer')
    out=out.sort_values('time').ffill(); cols=[c for c in out.columns if c!='time']; out['proxy']=out[cols].mean(axis=1)
    out['ma20']=out.proxy.rolling(20).mean(); out['ma50']=out.proxy.rolling(50).mean(); macd=ema(out.proxy,12)-ema(out.proxy,26); out['macdHist']=macd-ema(macd,9)
    delta=out.proxy.diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta.clip(upper=0)).rolling(14).mean(); out['rsi']=100-(100/(1+gain/loss.replace(0,1e-9)))
    return out[['time','proxy','ma20','ma50','rsi','macdHist']]

def regime_at(proxy,date,mode):
    d=proxy[proxy.time<=date]
    if d.empty: return False,{}
    row=d.iloc[-1]
    if mode=='strict': ok=(row.proxy>=row.ma20) and (row.ma20>=row.ma50*0.985) and (row.rsi>=45) and (row.macdHist>=d.iloc[-2].macdHist if len(d)>1 else True)
    elif mode=='loose': ok=(row.proxy>=row.ma50*0.98) and (row.rsi>=42)
    else: ok=True
    return bool(ok), {'mode':mode,'proxy':r(row.proxy),'ma20':r(row.ma20),'ma50':r(row.ma50),'rsi':r(row.rsi),'macdHist':r(row.macdHist,4),'ok':bool(ok)}

def trade_partial_at6(df,i,meta,cfg):
    entry=f(df.iloc[i+1].close); low=f(meta['supportZone'][0],meta['support']*0.985)
    stop0=max(low*0.98, entry*(1-cfg['maxRisk']/100)); risk=(entry-stop0)/entry*100
    if risk<=0 or risk>cfg['maxRisk']: return None
    t6=entry*1.06; future=df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    future_path=[]; half=False; realized=0.0; size=1.0; peak=entry; stop=stop0; outcome='timeout'; hold=len(future); exitd=str(future.iloc[-1].time.date())
    for n,(_,row) in enumerate(future.iterrows(),1):
        high=f(row.high); lowp=f(row.low); close=f(row.close); peak=max(peak,high)
        event=None
        if not half and high>=t6:
            realized += 0.5*6.0; size=0.5; half=True; stop=max(stop, entry*1.005); event='take_50_at_6'
        if half:
            stop=max(stop, peak*0.97, entry*1.005)
        hit_stop=lowp<=stop
        future_path.append({'date':str(row.time.date()),'open':r(row.open),'high':r(row.high),'low':r(row.low),'close':r(row.close),'stop':r(stop),'event':event})
        if hit_stop:
            realized += size*((stop-entry)/entry*100); outcome='win' if realized>0 else 'loss'; hold=n; exitd=str(row.time.date()); size=0; break
    if size>0:
        last=f(future.iloc[-1].close); realized += size*((last-entry)/entry*100); outcome='win' if realized>0 else 'loss' if realized<0 else 'flat'
    return {'outcome':outcome,'entry':r(entry),'stopInitial':r(stop0),'target6':r(t6),'pnlPct':r(realized),'riskPct':r(risk),'holdSessions':hold,'exitDate':exitd,'partialTaken':half,'futurePath':future_path}

def summ(ts):
    n=len(ts); w=[x for x in ts if f(x['pnlPct'])>0]; l=[x for x in ts if f(x['pnlPct'])<0]; flat=[x for x in ts if f(x['pnlPct'])==0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'flats':len(flat),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def run_window(name,start,end,proxy,histories,regime_mode):
    trades=[]; counts={}
    for sym in TECHNICAL_UNIVERSE[:50]:
        if sym in EXCLUDE: continue
        df=histories.get(sym)
        if df is None or df.empty or len(df)<260: counts[sym]={'error':'missing/short'}; continue
        df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
        c={'loops':0,'regimePass':0,'signals':0,'trades':0}
        for i in range(100,len(df)-HORIZON-2):
            t=df.iloc[i].time
            if t<start or t>=end: continue
            c['loops']+=1; ok_reg,reg=regime_at(proxy,t,regime_mode)
            if not ok_reg: continue
            c['regimePass']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
            rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist)
            meta=focused.score_meta(price,rs,row,hist,ind.iloc[:i+1].copy())
            if meta['rsi']<32 or meta['bbPercent']>0.9 or meta['volumeRatio']>3 or meta['roc20']<-10: continue
            if meta['score']<CONFIG['minScore'] or meta['dist']>CONFIG['maxDist']: continue
            tr=trade_partial_at6(df,i,meta,CONFIG)
            if tr:
                tr.update({'symbol':sym,'date':str(df.iloc[i+1].time.date()),'score':meta['score'],'distSupportPct':meta['dist'],'rsi':meta['rsi'],'ichimoku':meta['ichimoku'],'bullishDivergence':meta['bullishDivergence'],'marketRegime':reg})
                trades.append(tr); c['trades']+=1
            c['signals']+=1
        counts[sym]=c; print(name,regime_mode,sym,c,flush=True)
    return {'window':name,'regimeMode':regime_mode,'start':str(start.date()),'end':str(end.date()),'summary':summ(trades),'trades':trades,'counts':counts}

def main():
    symbols=TECHNICAL_UNIVERSE[:50]; histories=load_histories(symbols); proxy=market_proxy(symbols,histories); now=pd.Timestamp(datetime.now())
    windows={'current180':(now-timedelta(days=180),now),'prev3m':(now-timedelta(days=270),now-timedelta(days=180))}
    results={}
    for mode in ['none','loose','strict']:
        results[mode]={}
        for name,(st,en) in windows.items(): results[mode][name]=run_window(name,st,en,proxy,histories,mode)
    payload={'createdAt':datetime.now().isoformat(),'method':'Exact future-path V3: exclude VIC/VHM; target +6 then take 50%, trail remaining 3% from peak / entry+0.5; tests no/loose/strict market regime ex VIC/VHM.','config':{'target6TakePct':50,'trailAfterTarget6':'max(entry+0.5%, peak-3%)','scoreMin':68,'distSupportMaxPct':3,'riskMaxPct':5},'results':results,'proxyRows':len(proxy)}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summary':{m:{w:results[m][w]['summary'] for w in results[m]} for m in results}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
