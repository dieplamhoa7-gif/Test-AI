from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/v3_b4_bullish_divergence_current_signals.json')
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
    if not av or not bv: return {'state':'unknown','bullishTkCross':bool(tv>kv) if tv and kv else False,'cloudTop':None,'cloudBottom':None,'tenkan':r(tv),'kijun':r(kv)}
    return {'state':'above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud','bullishTkCross':bool(tv>kv),'cloudTop':r(max(av,bv)),'cloudBottom':r(min(av,bv)),'tenkan':r(tv),'kijun':r(kv)}

def pivot_lows(vals,left=2,right=2):
    out=[]; vals=list(vals)
    for i in range(left,len(vals)-right):
        v=vals[i]
        if v is None or pd.isna(v): continue
        win=[x for x in vals[i-left:i+right+1] if x is not None and not pd.isna(x)]
        if win and all(v<=x for x in win): out.append((i,float(v)))
    return out

def bullish_divergence_detail(hist,ind):
    try:
        close=pd.to_numeric(hist.close,errors='coerce').tail(60).reset_index(drop=True)
        rsi=pd.to_numeric(ind['rsi14'],errors='coerce').tail(60).reset_index(drop=True)
        mh=pd.to_numeric(ind['histogram'],errors='coerce').tail(60).reset_index(drop=True)
        piv=pivot_lows(close,2,2)
        if len(piv)<2: return {'rsiBullish':False,'macdBullish':False,'detail':'not_enough_pivots'}
        p1,p2=piv[-2],piv[-1]; i1,i2=p1[0],p2[0]
        price_lower=p2[1]<p1[1]
        return {'rsiBullish':bool(price_lower and f(rsi.iloc[i2])>f(rsi.iloc[i1])),'macdBullish':bool(price_lower and f(mh.iloc[i2])>f(mh.iloc[i1])),'priceLow1':r(p1[1]),'priceLow2':r(p2[1]),'rsiLow1':r(rsi.iloc[i1]),'rsiLow2':r(rsi.iloc[i2]),'macdHistLow1':r(mh.iloc[i1],4),'macdHistLow2':r(mh.iloc[i2],4)}
    except Exception as e:
        return {'rsiBullish':False,'macdBullish':False,'detail':repr(e)}

def indicators(price,row,hist,ind):
    mh=f(row.get('histogram')); hists=[f(ind.iloc[j].get('histogram'),mh) for j in range(max(0,len(ind)-4),len(ind))]
    recovering=bool(len(hists)>=3 and hists[-1]>hists[-2]>hists[-3])
    div=_detect_momentum_divergence(ind); div2=bullish_divergence_detail(hist,ind); ichi=ichimoku_state(hist)
    return {'rsi':r(f(row.get('rsi14'),50)),'macd':r(f(row.get('macd')),4),'macdSignal':r(f(row.get('signal')),4),'macdHist':r(mh,4),'macdHistSeq':[r(x,4) for x in hists],'macdHistRecovering':recovering,'bbPercent':r(f(row.get('bbPercent'),0.5),3),'volumeRatio':r(f(row.get('volumeRatio'),1),2),'roc20':r((price/f(hist.close.iloc[-21],price)-1)*100 if len(hist)>21 else 0),'ret5':r((price/f(hist.close.iloc[-6],price)-1)*100 if len(hist)>6 else 0),'ichimoku':ichi,'bullishDivergence':bool(div.get('bullish') or div2.get('rsiBullish') or div2.get('macdBullish')),'bullishDivergenceDetail':div2,'bearishDivergence':bool(div.get('bearish'))}

def eval_b4(price,rs,ai):
    sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'))
    dist=(price-sup)/price*100 if price and sup else 999
    checks=[
        (ai['ichimoku']['state']=='above_cloud','above cloud'),
        (dist<=3,'gần hỗ trợ <=3%'),
        (48<=f(ai['rsi'])<=62,'RSI 48-62'),
        (0.55<=f(ai['volumeRatio'])<=2.2,'volume vừa'),
        (-8<=f(ai['roc20'])<=12,'ROC20 hợp lệ'),
        ((ai.get('macdHistRecovering') or (ai.get('bullishDivergence') and f(ai['macdHist'])>=-0.05)),'MACD hồi dần hoặc phân kỳ dương'),
        (f(ai['bbPercent'])<=0.85,'BB không quá cao'),
        (not ai.get('bearishDivergence'),'không bearish divergence'),
    ]
    ok=sum(1 for x,_ in checks if x); missing=[lab for x,lab in checks if not x]
    action='BUY' if ok==len(checks) else 'WATCH' if ok>=6 and not ai.get('bearishDivergence') else 'REJECT'
    return {'strategy':'B4_above_cloud_bullish_div_or_recovering','action':action,'rankScore':r(ok/len(checks)*100),'entryPrice':r(price),'stopLoss':r(price*0.94),'takeProfit':r(price*1.06),'targetPct':6,'stopPct':6,'distSupportPct':r(dist),'support':r(sup),'resistance':r(res),'missingReasons':missing,'entryIndicators':ai,'rsSnapshot':{'supportZoneDay':rs.get('supportZoneDay'),'resistanceZoneDay':rs.get('resistanceZoneDay'),'activeSupportDay':rs.get('activeSupportDay'),'activeResistanceDay':rs.get('activeResistanceDay')}}

def main():
    rows=[]; errors=[]
    for idx,sym in enumerate(TECHNICAL_UNIVERSE[:50],1):
        if sym in EXCLUDE: continue
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<160:
                errors.append({'symbol':sym,'error':'missing/short'}); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True)
            ind=_compute_indicators(df.copy()); row=ind.iloc[-1]; price=f(df.iloc[-1].close)
            rs=calc_rs_levels_only(price,f(df.iloc[-1].open),f(df.iloc[-1].open),f(df.iloc[-1].high),f(df.iloc[-1].low),price,df)
            ai=indicators(price,row,df,ind); ev=eval_b4(price,rs,ai); ev.update({'symbol':sym,'asOfDate':str(df.iloc[-1].time.date()),'lastClose':r(price)})
            rows.append(ev); print(sym,ev['action'],ev['rankScore'],flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',e,flush=True)
        if idx%15==0: time.sleep(40)
        else: time.sleep(1.05)
    buys=sorted([x for x in rows if x['action']=='BUY'],key=lambda x:x['rankScore'],reverse=True)
    watch=sorted([x for x in rows if x['action']=='WATCH'],key=lambda x:x['rankScore'],reverse=True)
    payload={'createdAt':datetime.now().isoformat(),'method':'Current forecast scan using best stable B4 target +6: above_cloud, near support, RSI 48-62, volume 0.55-2.2, ROC -8..12, MACD recovering or bullish RSI/MACD divergence, BB<=0.85, no bearish divergence. Not historical winners.','summary':{'buyCount':len(buys),'watchCount':len(watch),'rejectCount':len(rows)-len(buys)-len(watch),'errorCount':len(errors)},'buy':buys,'watchlist':watch[:20],'errors':errors}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summary':payload['summary'],'buy':[(x['symbol'],x['entryPrice'],x['stopLoss'],x['takeProfit'],x['rankScore']) for x in buys],'watchTop':[(x['symbol'],x['rankScore'],x['missingReasons'][:3]) for x in watch[:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
