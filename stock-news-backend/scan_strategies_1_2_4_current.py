from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/strategies_1_2_4_current_forecast.json')
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
    if not av or not bv: return {'state':'unknown','cloudTop':None,'cloudBottom':None,'tenkan':r(tv),'kijun':r(kv),'bullishTkCross':bool(tv>kv) if tv and kv else False}
    return {'state':'above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud','cloudTop':r(max(av,bv)),'cloudBottom':r(min(av,bv)),'tenkan':r(tv),'kijun':r(kv),'bullishTkCross':bool(tv>kv)}

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
        if len(piv)<2: return {'rsiBullish':False,'macdBullish':False}
        p1,p2=piv[-2],piv[-1]; i1,i2=p1[0],p2[0]; lower=p2[1]<p1[1]
        return {'rsiBullish':bool(lower and f(rsi.iloc[i2])>f(rsi.iloc[i1])),'macdBullish':bool(lower and f(mh.iloc[i2])>f(mh.iloc[i1])),'priceLow1':r(p1[1]),'priceLow2':r(p2[1]),'rsiLow1':r(rsi.iloc[i1]),'rsiLow2':r(rsi.iloc[i2]),'macdHistLow1':r(mh.iloc[i1],4),'macdHistLow2':r(mh.iloc[i2],4)}
    except Exception as e: return {'rsiBullish':False,'macdBullish':False,'error':repr(e)}

def build_ai(df,ind):
    row=ind.iloc[-1]; price=f(df.iloc[-1].close); mh=f(row.get('histogram'))
    hists=[f(ind.iloc[j].get('histogram'),mh) for j in range(max(0,len(ind)-4),len(ind))]
    div=_detect_momentum_divergence(ind); div2=bullish_divergence_detail(df,ind)
    bullish=bool(div.get('bullish') or div2.get('rsiBullish') or div2.get('macdBullish'))
    return {'rsi':r(f(row.get('rsi14'),50)),'macd':r(f(row.get('macd')),4),'macdSignal':r(f(row.get('signal')),4),'macdHist':r(mh,4),'macdHistSeq':[r(x,4) for x in hists],'macdHistRecovering':bool(len(hists)>=3 and hists[-1]>hists[-2]>hists[-3]),'macdHistImproving':bool(len(hists)>=2 and hists[-1]>=hists[-2]),'bbPercent':r(f(row.get('bbPercent'),0.5),3),'volumeRatio':r(f(row.get('volumeRatio'),1),2),'roc20':r((price/f(df.close.iloc[-21],price)-1)*100 if len(df)>21 else 0),'ret5':r((price/f(df.close.iloc[-6],price)-1)*100 if len(df)>6 else 0),'ichimoku':ichimoku_state(df),'bullishDivergence':bullish,'bullishDivergenceDetail':div2,'bearishDivergence':bool(div.get('bearish'))}

def common(symbol,price,rs,ai):
    sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'))
    dist=(price-sup)/price*100 if price and sup else 999
    return {'symbol':symbol,'lastClose':r(price),'entryPrice':r(price),'stopLoss':r(price*0.94),'takeProfit':r(price*1.06),'support':r(sup),'resistance':r(res),'distSupportPct':r(dist),'entryIndicators':ai,'rsSnapshot':{'supportZoneDay':rs.get('supportZoneDay'),'resistanceZoneDay':rs.get('resistanceZoneDay'),'activeSupportDay':rs.get('activeSupportDay'),'activeResistanceDay':rs.get('activeResistanceDay')}}

def score_action(checks):
    ok=sum(1 for x,_ in checks if x); missing=[lab for x,lab in checks if not x]
    return ok, round(ok/len(checks)*100,2), missing

def eval_b4(symbol,price,rs,ai):
    base=common(symbol,price,rs,ai); dist=f(base['distSupportPct'],999)
    checks=[(ai['ichimoku']['state']=='above_cloud','above_cloud'),(dist<=3,'gần hỗ trợ <=3%'),(48<=f(ai['rsi'])<=62,'RSI 48-62'),(0.55<=f(ai['volumeRatio'])<=2.2,'volume 0.55-2.2'),(-8<=f(ai['roc20'])<=12,'ROC20 -8..12'),((ai['macdHistRecovering'] or (ai['bullishDivergence'] and f(ai['macdHist'])>=-0.05)),'MACD hồi hoặc phân kỳ dương'),(f(ai['bbPercent'])<=0.85,'BB<=0.85'),(not ai['bearishDivergence'],'không phân kỳ âm')]
    ok,rank,missing=score_action(checks); action='BUY' if ok==len(checks) else 'WATCH' if ok>=6 and not ai['bearishDivergence'] else 'REJECT'
    base.update({'strategy':'1_B4_Trend_Pullback','action':action,'rankScore':rank,'missingReasons':missing,'reason':'Mua hồi trong trend: above_cloud, gần hỗ trợ, RSI trung tính, MACD hồi/phân kỳ dương.'})
    return base

def eval_v3_focused(symbol,price,rs,ai):
    base=common(symbol,price,rs,ai); dist=f(base['distSupportPct'],999)
    # Approximate current version of saved V3 +6 focused rule: score>=68, dist<=3, risk<=5, no trend/ADX, bullish div bonus, bearish ignored.
    score=50
    if dist<=1.5: score+=18
    elif dist<=3: score+=12
    if f(ai['rsi'])<=45: score+=8
    elif f(ai['rsi'])<=55: score+=4
    if ai['macdHistImproving']: score+=6
    if f(ai['bbPercent'])<=0.55: score+=6
    if 0.55<=f(ai['volumeRatio'])<=2.5: score+=5
    if f(ai['roc20'])>=-12: score+=5
    if ai['bullishDivergence']: score+=4
    risk=6.0
    checks=[(score>=68,'score>=68'),(dist<=3,'gần hỗ trợ <=3%'),(risk<=6,'risk <=6% approx'),(f(ai['roc20'])>=-12,'ROC20 không quá xấu'),(0.55<=f(ai['volumeRatio'])<=2.5,'volume hợp lệ')]
    ok,rank,missing=score_action(checks); action='BUY' if ok==len(checks) else 'WATCH' if ok>=4 else 'REJECT'
    base.update({'strategy':'2_V3_Plus6_Focused','action':action,'rankScore':rank,'v3ApproxScore':r(score),'missingReasons':missing,'reason':'V3 +6 focused xấp xỉ current: gần hỗ trợ, score đủ, momentum không quá xấu. Bản này regime-dependent.'})
    return base

def eval_clean_a(symbol,price,rs,ai):
    base=common(symbol,price,rs,ai); dist=f(base['distSupportPct'],999)
    checks=[(ai['ichimoku']['state']!='below_cloud','không below_cloud'),(dist<=2,'gần hỗ trợ <=2%'),(f(ai['rsi'])<=40,'RSI<=40'),(f(ai['bbPercent'])<=0.45,'BB<=0.45'),(0.55<=f(ai['volumeRatio'])<=2.5,'volume 0.55-2.5'),((ai['macdHistImproving'] or ai['bullishDivergence'] or f(ai['macdHist'])>=-0.03),'MACD không xấu hoặc phân kỳ dương'),(not ai['bearishDivergence'],'không phân kỳ âm')]
    ok,rank,missing=score_action(checks); action='BUY' if ok==len(checks) else 'WATCH' if ok>=5 and ai['ichimoku']['state']!='below_cloud' else 'REJECT'
    base.update({'strategy':'4_Clean_Split_A_Baseline','action':action,'rankScore':rank,'missingReasons':missing,'reason':'Clean Split A: oversold gần hỗ trợ, BB thấp, volume ổn, không thủng mây dưới.'})
    return base

def main():
    all_rows=[]; errors=[]
    for idx,sym in enumerate(TECHNICAL_UNIVERSE[:50],1):
        if sym in EXCLUDE: continue
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<160: errors.append({'symbol':sym,'error':'missing/short'}); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True)
            ind=_compute_indicators(df.copy()); price=f(df.iloc[-1].close)
            rs=calc_rs_levels_only(price,f(df.iloc[-1].open),f(df.iloc[-1].open),f(df.iloc[-1].high),f(df.iloc[-1].low),price,df)
            ai=build_ai(df,ind)
            for ev in (eval_b4(sym,price,rs,ai), eval_v3_focused(sym,price,rs,ai), eval_clean_a(sym,price,rs,ai)):
                ev['asOfDate']=str(df.iloc[-1].time.date()); all_rows.append(ev)
            print(sym,'ok',flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',e,flush=True)
        if idx%15==0: time.sleep(40)
        else: time.sleep(1.05)
    grouped={}
    for st in ['1_B4_Trend_Pullback','2_V3_Plus6_Focused','4_Clean_Split_A_Baseline']:
        rows=[x for x in all_rows if x['strategy']==st]
        grouped[st]={'buy':sorted([x for x in rows if x['action']=='BUY'],key=lambda x:x['rankScore'],reverse=True),'watchlist':sorted([x for x in rows if x['action']=='WATCH'],key=lambda x:x['rankScore'],reverse=True)[:15],'rejectCount':sum(1 for x in rows if x['action']=='REJECT')}
    payload={'createdAt':datetime.now().isoformat(),'method':'Current forecast for saved strategies 1,2,4. Web/current scan only; not historical winners. Exit assumed target +6, take 50/trailing/stop 6 where applicable. V3 focused current scoring is an approximation of saved focused rule.','strategies':grouped,'errors':errors}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={st:{'buy':[(x['symbol'],x['entryPrice'],x['stopLoss'],x['takeProfit'],x['rankScore']) for x in grouped[st]['buy']],'watch':[(x['symbol'],x['rankScore'],x['missingReasons'][:3]) for x in grouped[st]['watchlist'][:8]],'reject':grouped[st]['rejectCount']} for st in grouped}
    print(json.dumps({'output':str(OUT),'compact':compact,'errors':len(errors)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
