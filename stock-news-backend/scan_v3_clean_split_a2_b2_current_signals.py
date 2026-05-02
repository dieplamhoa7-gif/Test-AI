from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/v3_clean_split_a2_b2_current_signals.json')
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

def ichimoku_state(df):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    a=((ten+kij)/2).shift(26); b=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    price=f(c.iloc[-1]); av=f(a.iloc[-1]); bv=f(b.iloc[-1]); tv=f(ten.iloc[-1]); kv=f(kij.iloc[-1])
    if not av or not bv:
        return {'state':'unknown','bullishTkCross':bool(tv>kv) if tv and kv else False,'tenkan':r(tv),'kijun':r(kv),'cloudTop':None,'cloudBottom':None}
    return {'state':'above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud','bullishTkCross':bool(tv>kv),'tenkan':r(tv),'kijun':r(kv),'cloudTop':r(max(av,bv)),'cloudBottom':r(min(av,bv))}

def action_indicators(price,row,hist,ind_until):
    rsi=f(row.get('rsi14'),50); macd=f(row.get('macd')); sig=f(row.get('signal')); mh=f(row.get('histogram'))
    bbp=f(row.get('bbPercent'),0.5); volr=f(row.get('volumeRatio'),1)
    roc20=(price/f(hist.close.iloc[-21],price)-1)*100 if len(hist)>21 else 0
    ret5=(price/f(hist.close.iloc[-6],price)-1)*100 if len(hist)>6 else 0
    div=_detect_momentum_divergence(ind_until); ichi=ichimoku_state(hist)
    hists=[]
    for j in range(max(0,len(ind_until)-4),len(ind_until)):
        hists.append(f(ind_until.iloc[j].get('histogram'),mh))
    mh_prev=hists[-2] if len(hists)>=2 else mh
    macd_recovering=bool(len(hists)>=3 and hists[-1]>hists[-2]>hists[-3])
    macd_not_falling=bool(len(hists)>=2 and hists[-1]>=hists[-2])
    return {'rsi':r(rsi),'macd':r(macd,4),'macdSignal':r(sig,4),'macdHist':r(mh,4),'macdHistSeq':[r(x,4) for x in hists],'macdHistImproving':macd_not_falling,'macdHistRecovering':macd_recovering,'bbPercent':r(bbp,3),'volumeRatio':r(volr,2),'roc20':r(roc20),'ret5':r(ret5),'ichimoku':ichi,'bullishDivergence':bool(div.get('bullish')),'bearishDivergence':bool(div.get('bearish'))}

def eval_strategy(name,price,rs,ai):
    sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'))
    dist=(price-sup)/price*100 if price and sup else 999
    rsi=f(ai['rsi']); bbp=f(ai['bbPercent']); volr=f(ai['volumeRatio']); roc=f(ai['roc20']); mh=f(ai['macdHist']); improving=ai['macdHistImproving']; ichi=ai['ichimoku']['state']
    reasons=[]
    if ai.get('bearishDivergence'): reasons.append('bearish divergence')
    if name=='A2_oversold_near_support':
        checks=[ichi!='below_cloud', dist<=2.5, rsi<=45, bbp<=0.55, 0.55<=volr<=2.5, roc>=-12, ai.get('macdHistRecovering'), not ai.get('bearishDivergence')]
        labels=['không thủng mây dưới','gần hỗ trợ <=2.5%','RSI <=45','BB thấp <=0.55','volume vừa','ROC20 không quá xấu','MACD hist hồi dần 3 phiên','không bearish divergence']
        ok=sum(1 for x in checks if x)
        passed=all(checks)
        if not passed: reasons=[labels[i] for i,x in enumerate(checks) if not x]
        target=price*1.10; stop=price*0.94
        score=ok/len(checks)*100
    elif name=='B2_confirmed_rebound_above_cloud':
        checks=[ichi=='above_cloud', dist<=3.0, 48<=rsi<=62, 0.55<=volr<=2.5, -8<=roc<=15, ai.get('macdHistRecovering'), bbp<=0.9, not ai.get('bearishDivergence')]
        labels=['above cloud','gần hỗ trợ <=3%','RSI 48-62','volume vừa','ROC20 hợp lệ','MACD hist hồi dần 3 phiên','BB không quá cao','không bearish divergence']
        ok=sum(1 for x in checks if x)
        passed=all(checks)
        if not passed: reasons=[labels[i] for i,x in enumerate(checks) if not x]
        target=price*1.06; stop=price*0.94
        score=ok/len(checks)*100
    else:
        return None
    macd_ok = bool(ai.get('macdHistRecovering'))
    watch_ok = score>=75 and dist<=3.5 and macd_ok and not ai.get('bearishDivergence')
    action='BUY' if passed else 'WATCH' if watch_ok else 'REJECT'
    entry=r(sup or price)
    target_pct=10 if name.startswith('A2') else 6
    return {'strategy':name,'action':action,'rankScore':r(score),'entryPrice':entry,'lastClose':r(price),'stopLoss':r(entry*0.94),'takeProfit':r(entry*(1+target_pct/100)),'targetPct':target_pct,'stopPct':6,'distSupportPct':r(dist),'support':r(sup),'resistance':r(res),'reasonsOk':[] if not passed else ['đạt đủ điều kiện'], 'missingReasons':reasons,'entryIndicators':ai,'rsSnapshot':{'supportZoneDay':rs.get('supportZoneDay'),'resistanceZoneDay':rs.get('resistanceZoneDay'),'activeSupportDay':rs.get('activeSupportDay'),'activeResistanceDay':rs.get('activeResistanceDay')}}

def main():
    results=[]; errors=[]
    for idx,sym in enumerate(TECHNICAL_UNIVERSE[:50],1):
        if sym in EXCLUDE: continue
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<160:
                errors.append({'symbol':sym,'error':'missing/short','rows':0 if df is None else len(df)}); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True)
            ind=_compute_indicators(df.copy()); row=ind.iloc[-1]; hist=df.copy(); price=f(df.iloc[-1].close)
            rs=calc_rs_levels_only(price,f(df.iloc[-1].open),f(df.iloc[-1].open),f(df.iloc[-1].high),f(df.iloc[-1].low),price,hist)
            ai=action_indicators(price,row,hist,ind.copy())
            symres=[]
            for strat in ['A2_oversold_near_support','B2_confirmed_rebound_above_cloud']:
                ev=eval_strategy(strat,price,rs,ai)
                if ev:
                    ev.update({'symbol':sym,'asOfDate':str(df.iloc[-1].time.date()),'lastClose':r(price)})
                    symres.append(ev)
            best=sorted(symres,key=lambda x:({'BUY':2,'WATCH':1,'REJECT':0}[x['action']],x['rankScore']),reverse=True)[0]
            results.append(best)
            print(sym,best['action'],best['strategy'],best['rankScore'],flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',e,flush=True)
        if idx%15==0: time.sleep(40)
        else: time.sleep(1.05)
    buys=sorted([x for x in results if x['action']=='BUY'],key=lambda x:x['rankScore'],reverse=True)
    watch=sorted([x for x in results if x['action']=='WATCH'],key=lambda x:x['rankScore'],reverse=True)
    rejects=sorted([x for x in results if x['action']=='REJECT'],key=lambda x:x['rankScore'],reverse=True)
    payload={'createdAt':datetime.now().isoformat(),'method':'Current signal scan using saved clean split A2/B2 rules. Not historical winners. R/S only for zone/entry/stop/target; action uses RSI/MACD/BB/Volume/ROC/Ichimoku/Divergence. Excludes VIC/VHM.','summary':{'buyCount':len(buys),'watchCount':len(watch),'rejectCount':len(rejects),'errorCount':len(errors)},'buy':buys,'watchlist':watch[:20],'rejectTop':rejects[:20],'errors':errors}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summary':payload['summary'],'buy':[(x['symbol'],x['strategy'],x['entryPrice'],x['stopLoss'],x['takeProfit'],x['rankScore']) for x in buys],'watchTop':[(x['symbol'],x['strategy'],x['rankScore'],x['missingReasons'][:3]) for x in watch[:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
