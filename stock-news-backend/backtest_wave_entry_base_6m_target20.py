from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
from app.market_data import _load_history, _compute_indicators, _detect_momentum_divergence
from app.technical_filters import TECHNICAL_UNIVERSE

OUT = Path('data/wave_entry_base_6m_target20_backtest.json')
EXCLUDE = {'VIC','VHM'}
HORIZON = 84


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

def slope(series, n=5):
    if len(series) < n+1: return 0.0
    return (f(series.iloc[-1]) / f(series.iloc[-1-n], f(series.iloc[-1])) - 1) * 100

def ichimoku_state(df):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    a=((ten+kij)/2).shift(26); b=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    price=f(c.iloc[-1]); av=f(a.iloc[-1]); bv=f(b.iloc[-1])
    if not av or not bv: return {'state':'unknown','cloudTop':None,'cloudBottom':None}
    return {'state':'above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud','cloudTop':r(max(av,bv)),'cloudBottom':r(min(av,bv))}

def calc_base_features(hist):
    close=pd.to_numeric(hist.close,errors='coerce')
    high=pd.to_numeric(hist.high,errors='coerce')
    low=pd.to_numeric(hist.low,errors='coerce')
    vol=pd.to_numeric(hist.volume,errors='coerce') if 'volume' in hist.columns else pd.Series([0]*len(hist))
    base126=hist.tail(126); base252=hist.tail(252) if len(hist)>=252 else hist.tail(len(hist))
    def base_stats(df):
        c=pd.to_numeric(df.close,errors='coerce'); h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); v=pd.to_numeric(df.volume,errors='coerce') if 'volume' in df.columns else pd.Series([0]*len(df))
        hi=f(h.max()); lo=f(l.min()); last=f(c.iloc[-1]); rng=(hi-lo)/lo*100 if lo else 999
        pos=(last-lo)/(hi-lo)*100 if hi>lo else 50
        ma20=c.rolling(20).mean(); ma50=c.rolling(50).mean()
        flat=abs(slope(ma50.dropna(),20)) if len(ma50.dropna())>25 else 999
        dry= f(v.tail(20).mean()) / f(v.tail(100).mean(), f(v.tail(20).mean())) if len(v)>=100 and f(v.tail(100).mean()) else 1
        return {'high':hi,'low':lo,'rangePct':r(rng),'positionPct':r(pos),'ma50Slope20Pct':r(flat),'volumeDryRatio20v100':r(dry,2)}
    s126=base_stats(base126); s252=base_stats(base252)
    don20=f(high.tail(21).iloc[:-1].max()) if len(high)>=21 else f(high.max())
    don60=f(high.tail(61).iloc[:-1].max()) if len(high)>=61 else f(high.max())
    return {'base6m':s126,'base12m':s252,'donchian20Prev':r(don20),'donchian60Prev':r(don60)}

def action_indicators(hist, ind):
    row=ind.iloc[-1]; price=f(hist.iloc[-1].close); close=pd.to_numeric(hist.close,errors='coerce')
    ma20=f(close.rolling(20).mean().iloc[-1]); ma50=f(close.rolling(50).mean().iloc[-1]); ma200=f(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else 0
    mh=f(row.get('histogram')); hists=[f(ind.iloc[j].get('histogram'), mh) for j in range(max(0,len(ind)-4),len(ind))]
    volr=f(row.get('volumeRatio'),1); rsi=f(row.get('rsi14'),50)
    roc20=(price/f(close.iloc[-21],price)-1)*100 if len(close)>21 else 0
    div=_detect_momentum_divergence(ind)
    bf=calc_base_features(hist); ichi=ichimoku_state(hist)
    return {'price':r(price),'ma20':r(ma20),'ma50':r(ma50),'ma200':r(ma200),'ma20Slope5Pct':r(slope(close.rolling(20).mean().dropna(),5)),'ma50Slope20Pct':r(slope(close.rolling(50).mean().dropna(),20)),'rsi':r(rsi),'macdHist':r(mh,4),'macdHistSeq':[r(x,4) for x in hists],'macdHistRising':bool(len(hists)>=3 and hists[-1]>hists[-2]>hists[-3]),'macdHistPositive':bool(mh>0),'volumeRatio':r(volr,2),'roc20':r(roc20),'bbPercent':r(f(row.get('bbPercent'),0.5),3),'ichimoku':ichi,'bearishDivergence':bool(div.get('bearish')),'base':bf}

def pass_strategy(name, ai):
    p=f(ai['price']); ma20=f(ai['ma20']); ma50=f(ai['ma50']); ma200=f(ai['ma200']); base=ai['base']; b6=base['base6m']; b12=base['base12m']
    rsi=f(ai['rsi']); vol=f(ai['volumeRatio']); roc=f(ai['roc20']); bbp=f(ai['bbPercent']); ichi=ai['ichimoku']['state']
    extended=(p/ma20-1)*100 if ma20 else 999
    base6_ok=f(b6['rangePct'])<=35 and f(b6['ma50Slope20Pct'])<=8 and f(b6['positionPct'])>=55
    base12_ok=f(b12['rangePct'])<=55 and f(b12['ma50Slope20Pct'])<=12
    dry_ok=f(b6.get('volumeDryRatio20v100'),1)<=1.25
    breakout20=p>f(base['donchian20Prev'])
    breakout60=p>f(base['donchian60Prev'])
    common=[]
    if ichi!='above_cloud': common.append('not_above_cloud')
    if not (p>ma20>0 and p>ma50>0): common.append('not_above_ma20_ma50')
    if ma20 and ma50 and ma20 < ma50*0.985: common.append('ma20_below_ma50')
    if ai['bearishDivergence']: common.append('bearish_divergence')
    if extended>12: common.append('too_extended_ma20')
    if not (55<=rsi<=72): common.append('rsi_not_55_72')
    if not (1.15<=vol<=3.0): common.append('volume_not_confirm')
    if roc<3: common.append('roc20_weak')
    if not ai['macdHistPositive']: common.append('macd_hist_not_positive')
    if common: return False, common[0]
    if name=='WaveA_base_breakout_safe':
        if not base6_ok: return False,'no_6m_base'
        if not dry_ok: return False,'base_volume_not_dry'
        if not breakout20: return False,'no_breakout20'
        if not ai['macdHistRising']: return False,'macd_not_rising3'
        if bbp>1.05: return False,'bb_too_high'
        return True,'ok'
    if name=='WaveB_early_wave_from_base':
        if not base6_ok: return False,'no_6m_base'
        if not (ai['macdHistRising'] or (ai['macdHistPositive'] and roc>=5)): return False,'momentum_not_starting'
        if not (p>=f(base['donchian20Prev'])*0.985): return False,'not_near_breakout20'
        if rsi>68: return False,'rsi_too_hot_early'
        return True,'ok'
    if name=='WaveC_strong_momentum_after_base':
        if not base6_ok: return False,'no_6m_base'
        if not breakout60: return False,'no_breakout60'
        if roc<5: return False,'roc20_lt5'
        if not ai['macdHistRising']: return False,'macd_not_rising3'
        return True,'ok'
    return False,'unknown'

def trade_manage(df,i,target_pct=8,stop_pct=6,trail_pct=4):
    entry=f(df.iloc[i+1].close); stop=entry*(1-stop_pct/100); target=entry*(1+target_pct/100); future=df.iloc[i+2:i+2+HORIZON]
    if not entry or future.empty: return None
    size=1.0; realized=0.0; partial=False; peak=entry; hold=len(future); exitd=str(future.iloc[-1].time.date()); outcome='timeout'; path=[]
    for n,(_,row) in enumerate(future.iterrows(),1):
        high=f(row.high); low=f(row.low); close=f(row.close); peak=max(peak,high); event=None
        if not partial and high>=target:
            realized += 0.5*target_pct; size=0.5; partial=True; stop=max(stop,entry*1.01); event='take_50_at_target'
        if partial: stop=max(stop,entry*1.01,peak*(1-trail_pct/100))
        if low<=stop:
            realized += size*((stop-entry)/entry*100); size=0; outcome='win' if realized>0 else 'loss'; hold=n; exitd=str(row.time.date()); event=(event+'+stop' if event else 'stop'); path.append({'date':str(row.time.date()),'close':r(close),'stop':r(stop),'event':event}); break
        path.append({'date':str(row.time.date()),'close':r(close),'stop':r(stop),'event':event})
    if size>0:
        last=f(future.iloc[-1].close); realized += size*((last-entry)/entry*100); outcome='win' if realized>0 else 'loss' if realized<0 else 'flat'
    return {'entry':r(entry),'stopInitial':r(entry*(1-stop_pct/100)),'target':r(target),'pnlPct':r(realized),'outcome':outcome,'holdSessions':hold,'exitDate':exitd,'partialTaken':partial,'futurePath':path}

def summ(ts):
    n=len(ts); w=[x for x in ts if f(x['pnlPct'])>0]; l=[x for x in ts if f(x['pnlPct'])<0]; fl=[x for x in ts if f(x['pnlPct'])==0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'flats':len(fl),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def load_histories(symbols):
    out={}
    for idx,sym in enumerate(symbols,1):
        try:
            df=_load_history(sym); out[sym]=df; print('history',idx,sym,0 if df is None else len(df),flush=True)
        except Exception as e:
            out[sym]=None; print('history',idx,sym,'ERR',e,flush=True)
        if idx%15==0: time.sleep(40)
        else: time.sleep(1.05)
    return out

def run_window(name,start,end,histories):
    strategies=['WaveA_base_breakout_safe','WaveB_early_wave_from_base','WaveC_strong_momentum_after_base']
    out={s:{'trades':[],'rejects':Counter()} for s in strategies}; counts={}
    for sym in TECHNICAL_UNIVERSE[:50]:
        if sym in EXCLUDE: continue
        df=histories.get(sym)
        if df is None or df.empty or len(df)<280: counts[sym]={'error':'missing/short'}; continue
        df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
        c={'loops':0,'candidates':0}
        for i in range(252,len(df)-HORIZON-2):
            t=df.iloc[i].time
            if t<start or t>=end: continue
            c['loops']+=1; hist=df.iloc[:i+1].copy(); ai=action_indicators(hist, ind.iloc[:i+1].copy())
            for strat in strategies:
                ok,reason=pass_strategy(strat,ai)
                if not ok: out[strat]['rejects'][reason]+=1; continue
                tr=trade_manage(df,i,target_pct=20,stop_pct=8,trail_pct=8)
                if tr:
                    tr.update({'symbol':sym,'signalDate':str(df.iloc[i].time.date()),'entryDate':str(df.iloc[i+1].time.date()),'strategy':strat,'entryIndicators':ai})
                    out[strat]['trades'].append(tr); c['candidates']+=1
        counts[sym]=c; print(name,sym,c,flush=True)
    result={}
    for s,node in out.items(): result[s]={'summary':summ(node['trades']),'trades':node['trades'],'rejects':dict(node['rejects'].most_common(20))}
    return {'window':name,'start':str(start.date()),'end':str(end.date()),'results':result,'counts':counts}

def main():
    histories=load_histories(TECHNICAL_UNIVERSE[:50]); now=pd.Timestamp(datetime.now())
    current=run_window('current180',now-timedelta(days=180),now,histories)
    prev=run_window('prev3m',now-timedelta(days=270),now-timedelta(days=180),histories)
    payload={'createdAt':datetime.now().isoformat(),'name':'Wave Entry after 6m base accumulation target20','method':'Looks for stocks forming a 6-month base, then entering wave by breakout/early momentum/strong momentum. Output saved; web should only read cache. Exit: target +20%, take 50%, trailing 8%, stop 8%, horizon 84 sessions. User requested 6m base only to allow OOS and 20% profit target.','windows':{'current180':current,'prev3m':prev}}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={w:{s:payload['windows'][w]['results'][s]['summary'] for s in payload['windows'][w]['results']} for w in payload['windows']}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
