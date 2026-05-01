from __future__ import annotations
import json, importlib.util, time
from pathlib import Path
from datetime import datetime,timedelta
from collections import Counter
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/v3_clean_split_cloud_rebound_backtest.json')
EXCLUDE={'VIC','VHM'}
HORIZON=42

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

def atr_series(df,n=14):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def ichimoku_state(df):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    a=((ten+kij)/2).shift(26); b=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    price=f(c.iloc[-1]); av=f(a.iloc[-1]); bv=f(b.iloc[-1]); tv=f(ten.iloc[-1]); kv=f(kij.iloc[-1])
    if not av or not bv: return {'state':'unknown','bullishTkCross':bool(tv>kv) if tv and kv else False,'tenkan':r(tv),'kijun':r(kv),'cloudTop':None,'cloudBottom':None}
    return {'state':'above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud','bullishTkCross':bool(tv>kv),'tenkan':r(tv),'kijun':r(kv),'cloudTop':r(max(av,bv)),'cloudBottom':r(min(av,bv))}

def action_indicators(price,row,hist,ind_until):
    rsi=f(row.get('rsi14'),50); macd=f(row.get('macd')); sig=f(row.get('signal')); mh=f(row.get('histogram'))
    bbp=f(row.get('bbPercent'),0.5); volr=f(row.get('volumeRatio'),1)
    roc20=(price/f(hist.close.iloc[-21],price)-1)*100 if len(hist)>21 else 0
    ret5=(price/f(hist.close.iloc[-6],price)-1)*100 if len(hist)>6 else 0
    div=_detect_momentum_divergence(ind_until); ichi=ichimoku_state(hist)
    mh_prev=f(ind_until.iloc[-2].get('histogram'),mh) if len(ind_until)>1 else mh
    return {'rsi':r(rsi),'macd':r(macd,4),'macdSignal':r(sig,4),'macdHist':r(mh,4),'macdHistImproving':bool(mh>=mh_prev),'bbPercent':r(bbp,3),'volumeRatio':r(volr,2),'roc20':r(roc20),'ret5':r(ret5),'ichimoku':ichi,'bullishDivergence':bool(div.get('bullish')),'bearishDivergence':bool(div.get('bearish'))}

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

def pass_strategy(name,rs,ai):
    price=f(rs.get('_price')); sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
    dist=(price-sup)/price*100 if price and sup else 999
    rsi=f(ai['rsi']); bbp=f(ai['bbPercent']); volr=f(ai['volumeRatio']); roc=f(ai['roc20']); mh=f(ai['macdHist']); improving=ai['macdHistImproving']; ichi=ai['ichimoku']['state']
    if ai.get('bearishDivergence'): return False, 'bearish_divergence'
    # R/S is hard filter only, not scoring.
    cloud_bottom=f(ai.get('ichimoku',{}).get('cloudBottom'))
    cloud_top=f(ai.get('ichimoku',{}).get('cloudTop'))
    cloud_touch=bool(cloud_bottom and price>=cloud_bottom*0.985 and price<=cloud_bottom*1.035)
    # New rule from user: if price already breaks below lower cloud, do not buy.
    if ichi=='below_cloud': return False,'below_cloud_no_buy'
    if name=='A3_oversold_cloud_bottom_rebound':
        if not cloud_touch: return False,'not_touch_cloud_bottom'
        if dist>2.5: return False,'dist>2.5'
        if rsi>45: return False,'rsi>45'
        if bbp>0.6: return False,'bbp>0.6'
        if volr<0.55 or volr>2.5: return False,'vol_bad'
        if roc<-12: return False,'roc<-12'
        if not (improving or mh>=-0.05 or ai.get('bullishDivergence')): return False,'macd_not_bounce'
        return True,'ok'
    if name=='B3_confirmed_rebound_cloud_safe':
        # Prefer above cloud; allow in_cloud only when price is near lower cloud and momentum is improving.
        if not (ichi=='above_cloud' or (ichi=='in_cloud' and cloud_touch)): return False,'not_cloud_safe'
        if dist>3.0: return False,'dist>3'
        if not (48<=rsi<=60): return False,'rsi_not_48_60'
        if volr<0.55 or volr>2.2: return False,'vol_bad'
        if roc<-8 or roc>12: return False,'roc_bad'
        if not (mh>=-0.03 or improving): return False,'macd_bad'
        if bbp>0.8: return False,'bbp_too_high'
        return True,'ok'
    return False,'unknown_strategy'

def trade_manage(df,i,rs,variant):
    entry=f(df.iloc[i+1].close); sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); zone=rs.get('supportZoneDay') or [sup*0.985,sup*1.015]
    if not entry or not sup: return None
    stop_pct=variant['stopPct']/100; stop=min(entry*(1-stop_pct), f(zone[0],sup)*0.985) if variant.get('belowSupportToo') else entry*(1-stop_pct)
    # hạn chế stop quá xa theo yêu cầu: dùng fixed support-break 6%, không loại risk >5 như cũ
    target=entry*(1+variant['targetPct']/100); future=df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    size=1.0; realized=0.0; half=False; peak=entry; hold=len(future); exitd=str(future.iloc[-1].time.date()); outcome='timeout'; path=[]
    for n,(_,row) in enumerate(future.iterrows(),1):
        high=f(row.high); low=f(row.low); close=f(row.close); peak=max(peak,high); event=None
        if variant.get('takeHalf') and not half and high>=target:
            realized += 0.5*variant['targetPct']; size=0.5; half=True; event='take_50_at_target'
            stop=max(stop,entry*1.005)
        elif not variant.get('takeHalf') and high>=target:
            realized += size*variant['targetPct']; size=0; outcome='win'; hold=n; exitd=str(row.time.date()); event='take_full_target'; path.append({'date':str(row.time.date()),'open':r(row.open),'high':r(row.high),'low':r(row.low),'close':r(row.close),'stop':r(stop),'event':event}); break
        if half and variant.get('trailAfterTarget'):
            stop=max(stop,entry*1.005,peak*(1-variant.get('trailPct',3)/100))
        if low<=stop:
            realized += size*((stop-entry)/entry*100); size=0; outcome='win' if realized>0 else 'loss'; hold=n; exitd=str(row.time.date()); event=(event+'+stop' if event else 'stop'); path.append({'date':str(row.time.date()),'open':r(row.open),'high':r(row.high),'low':r(row.low),'close':r(row.close),'stop':r(stop),'event':event}); break
        path.append({'date':str(row.time.date()),'open':r(row.open),'high':r(row.high),'low':r(row.low),'close':r(row.close),'stop':r(stop),'event':event})
    if size>0:
        last=f(future.iloc[-1].close); realized += size*((last-entry)/entry*100); outcome='win' if realized>0 else 'loss' if realized<0 else 'flat'
    return {'outcome':outcome,'entry':r(entry),'stopInitial':r(entry*(1-stop_pct)),'target':r(target),'pnlPct':r(realized),'riskPct':r((entry-entry*(1-stop_pct))/entry*100),'holdSessions':hold,'exitDate':exitd,'partialTaken':half,'futurePath':path}

def summ(ts):
    n=len(ts); w=[x for x in ts if f(x['pnlPct'])>0]; l=[x for x in ts if f(x['pnlPct'])<0]; fl=[x for x in ts if f(x['pnlPct'])==0]
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'flats':len(fl),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def run_window(name,start,end,histories):
    strategies=['A3_oversold_cloud_bottom_rebound','B3_confirmed_rebound_cloud_safe']
    variants=[{'name':'target6_half_trail_stop6','targetPct':6,'stopPct':6,'takeHalf':True,'trailAfterTarget':True,'trailPct':3},{'name':'target10_half_trail_stop6','targetPct':10,'stopPct':6,'takeHalf':True,'trailAfterTarget':True,'trailPct':3},{'name':'target10_full_stop6','targetPct':10,'stopPct':6,'takeHalf':False,'trailAfterTarget':False}]
    out={s:{v['name']:{'trades':[],'rejects':Counter()} for v in variants} for s in strategies}
    counts={}
    for sym in TECHNICAL_UNIVERSE[:50]:
        if sym in EXCLUDE: continue
        df=histories.get(sym)
        if df is None or df.empty or len(df)<260: counts[sym]={'error':'missing/short'}; continue
        df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
        c={'loops':0,'candidates':0}
        for i in range(100,len(df)-HORIZON-2):
            t=df.iloc[i].time
            if t<start or t>=end: continue
            c['loops']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
            rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist); rs['_price']=price
            ai=action_indicators(price,row,hist,ind.iloc[:i+1].copy())
            for strat in strategies:
                ok,reason=pass_strategy(strat,rs,ai)
                if not ok:
                    for v in variants: out[strat][v['name']]['rejects'][reason]+=1
                    continue
                c['candidates']+=1
                dist=(price-f(rs.get('activeSupportDay') or rs.get('supportDay')))/price*100
                for v in variants:
                    tr=trade_manage(df,i,rs,v)
                    if tr:
                        tr.update({'symbol':sym,'signalDate':str(df.iloc[i].time.date()),'entryDate':str(df.iloc[i+1].time.date()),'strategy':strat,'variant':v['name'],'distSupportPct':r(dist),'support':rs.get('activeSupportDay'),'resistance':rs.get('activeResistanceDay'),'supportZone':rs.get('supportZoneDay'),'resistanceZone':rs.get('resistanceZoneDay'),'entryIndicators':ai})
                        out[strat][v['name']]['trades'].append(tr)
        counts[sym]=c; print(name,sym,c,flush=True)
    result={}
    for strat in strategies:
        result[strat]={}
        for v in variants:
            node=out[strat][v['name']]
            result[strat][v['name']]={'summary':summ(node['trades']),'trades':node['trades'],'rejects':dict(node['rejects'].most_common(20))}
    return {'window':name,'start':str(start.date()),'end':str(end.date()),'results':result,'counts':counts}

def main():
    symbols=TECHNICAL_UNIVERSE[:50]; histories=load_histories(symbols); now=pd.Timestamp(datetime.now())
    current=run_window('current180',now-timedelta(days=180),now,histories)
    prev=run_window('prev3m',now-timedelta(days=270),now-timedelta(days=180),histories)
    payload={'createdAt':datetime.now().isoformat(),'method':'Clean split cloud rebound A3/B3. User rule: below_cloud / thủng mây dưới thì không mua. A3 buys only near lower cloud touch with rebound indicators. B3 buys above_cloud or in_cloud near lower cloud with improving momentum. R/S still only zone/stop-target. Excludes VIC/VHM. Saves full entryIndicators and futurePath.','windows':{'current180':current,'prev3m':prev}}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={w:{s:{v:payload['windows'][w]['results'][s][v]['summary'] for v in payload['windows'][w]['results'][s]} for s in payload['windows'][w]['results']} for w in payload['windows']}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
