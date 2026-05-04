from __future__ import annotations
import json, math, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history, _compute_indicators, _detect_momentum_divergence, _price_zone_state, _volume_state, _effective_trend, _setup_type, _signal_score

RS_IN=Path('data/rs_levels_vn100_cache.json')
PREV=Path('data/v3_full_indicator_cache.json')
OUT=Path('data/v3_full_indicator_cache_v2.json')
TMP=Path('data/v3_full_indicator_cache_v2_vn100.partial.json')
SLEEP_EVERY=18
SLEEP_SECONDS=65


def f(v,d=0.0):
    try:
        if v is None: return d
        if hasattr(v,'item'): v=v.item()
        if pd.isna(v): return d
        return float(v)
    except Exception: return d

def s(v,n=2):
    try:
        if v is None or pd.isna(v): return None
        return round(float(v),n)
    except Exception: return v

def load_json(p):
    return json.load(open(p,encoding='utf-8')) if p.exists() else {}


def save_payload(path, items, errors, fallbacks):
    payload={'createdAt':datetime.now().isoformat(),'method':'V3 full indicator cache v2: adds Ichimoku/Keltner/ROC20 and transparent component scoring; reads RS cache, no RS recomputation','rsInput':str(RS_IN),'count':len(items),'errorCount':len(errors),'fallbackCount':len(fallbacks),'fallbackSymbols':fallbacks,'items':items,'errors':errors}
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

def ichimoku(df):
    high=pd.to_numeric(df['high'],errors='coerce'); low=pd.to_numeric(df['low'],errors='coerce'); close=pd.to_numeric(df['close'],errors='coerce')
    tenkan=(high.rolling(9).max()+low.rolling(9).min())/2
    kijun=(high.rolling(26).max()+low.rolling(26).min())/2
    span_a=((tenkan+kijun)/2).shift(26)
    span_b=((high.rolling(52).max()+low.rolling(52).min())/2).shift(26)
    chikou=close.shift(-26)
    i=len(df)-1
    price=f(close.iloc[i]); a=f(span_a.iloc[i]); b=f(span_b.iloc[i]); t=f(tenkan.iloc[i]); k=f(kijun.iloc[i])
    cloud_top=max(a,b) if a and b else None; cloud_bottom=min(a,b) if a and b else None
    state='unknown'
    if cloud_top and cloud_bottom:
        if price>cloud_top: state='above_cloud'
        elif price<cloud_bottom: state='below_cloud'
        else: state='in_cloud'
    return {'tenkan':s(t),'kijun':s(k),'senkouSpanA':s(a),'senkouSpanB':s(b),'cloudTop':s(cloud_top),'cloudBottom':s(cloud_bottom),'chikou':s(chikou.iloc[i]) if i < len(chikou) else None,'state':state,'bullishTkCross': bool(t>k) if t and k else False}

def atr_series(df, n=14):
    h=pd.to_numeric(df['high'],errors='coerce'); l=pd.to_numeric(df['low'],errors='coerce'); c=pd.to_numeric(df['close'],errors='coerce')
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def keltner(df):
    c=pd.to_numeric(df['close'],errors='coerce')
    mid=c.ewm(span=20,adjust=False).mean(); atr=atr_series(df,14)
    upper=mid+2*atr; lower=mid-2*atr
    price=f(c.iloc[-1]); u=f(upper.iloc[-1]); m=f(mid.iloc[-1]); lo=f(lower.iloc[-1])
    pct=(price-lo)/(u-lo) if u and lo and u!=lo else None
    state='neutral'
    if pct is not None:
        if pct>=0.85: state='upper_band'
        elif pct<=0.15: state='lower_band'
        elif price>m: state='above_mid'
        else: state='below_mid'
    return {'upper':s(u),'mid':s(m),'lower':s(lo),'percent':s(pct,3),'state':state}

def roc(df, n=20):
    c=pd.to_numeric(df['close'],errors='coerce')
    if len(c)<=n: return None
    prev=f(c.iloc[-1-n]); cur=f(c.iloc[-1])
    return s((cur/prev-1)*100,2) if prev else None

def score_item(price, rs, ind):
    # 0-100 composite, transparent component score.
    scores={}
    rsi=f(ind.get('rsi14'),50)
    scores['rsi']=15 if 40<=rsi<=60 else 10 if 35<=rsi<40 or 60<rsi<=68 else 5 if 30<=rsi<35 or 68<rsi<=75 else 0
    hist=f(ind.get('histogram'),0); macd=f(ind.get('macd'),0); sig=f(ind.get('signal'),0)
    scores['macd']=15 if macd>sig and hist>0 else 10 if hist>=0 else 5 if hist>-0.15 else 0
    adx=f(ind.get('adx14'),0); pdi=f(ind.get('plusDi'),0); mdi=f(ind.get('minusDi'),0)
    scores['adxDi']=15 if adx>=20 and pdi>=mdi else 10 if pdi>=mdi else 5 if adx<18 else 0
    ma20=f(ind.get('ma20'),price); ma50=f(ind.get('ma50'),price); ma200=f(ind.get('ma200'),price)
    scores['maTrend']=15 if price>=ma20>=ma50 and price>=ma200 else 10 if price>=ma50 else 5 if price>=ma200 else 0
    bbp=ind.get('bbPercent'); bbp=f(bbp,0.5)
    scores['bollinger']=10 if 0.2<=bbp<=0.75 else 7 if 0.08<=bbp<0.2 else 4 if 0.75<bbp<=0.92 else 0
    vwap=f(ind.get('vwapDay'),0); scores['vwap']=8 if vwap and price>=vwap else 4 if vwap else 0
    vr=f(ind.get('volumeRatio'),1); scores['volume']=8 if 0.8<=vr<=1.8 else 5 if vr<0.8 else 4
    ichi=ind.get('ichimoku') or {}; ist=ichi.get('state')
    scores['ichimoku']=10 if ist=='above_cloud' and ichi.get('bullishTkCross') else 7 if ist=='above_cloud' else 4 if ist=='in_cloud' else 0
    kc=ind.get('keltner') or {}; kp=kc.get('percent'); kp=f(kp,0.5)
    scores['keltner']=7 if 0.2<=kp<=0.8 else 4 if kp<0.2 else 2
    r20=ind.get('roc20'); r20=f(r20,0)
    scores['roc20']=7 if 0<r20<=12 else 4 if -5<=r20<=0 else 2 if r20>12 else 0
    div=ind.get('divergence') or {}
    scores['divergence']=5 if div.get('bullish') else 2 if not div.get('bearish') else 0
    active_support=f(rs.get('activeSupportDay') or rs.get('supportDay'),0); active_res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'),0)
    rr=f(ind.get('riskReward'),0)
    dist_sup=abs(price-active_support)/price*100 if active_support and price else None
    scores['rsPosition']=10 if dist_sup is not None and dist_sup<=2 and rr>=1 else 7 if rr>=1.2 else 3 if rr>=0.8 else 0
    total=sum(scores.values()); max_total=140
    return {'totalRaw':total,'maxRaw':max_total,'score100':round(total/max_total*100,2),'components':scores,'notes':'Score minh bạch theo từng chỉ báo; dùng để xếp hạng, chưa phải tín hiệu mua độc lập.'}

def build(sym, rs):
    df=_load_history(sym)
    if df is None or df.empty: return None,'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    if len(df)<80: return None,f'short history {len(df)}'
    daily=_compute_indicators(df.copy()); row=daily.iloc[-1]
    price=f(row.get('close'), f(df.iloc[-1].get('close')))
    rsi=f(row.get('rsi14'),50); macd=f(row.get('macd'),0); sig=f(row.get('signal'),0); hist=f(row.get('histogram'),0)
    adx=f(row.get('adx14'),0); pdi=f(row.get('plusDi'),0); mdi=f(row.get('minusDi'),0)
    ma20=f(row.get('ma20'),price); ma50=f(row.get('ma50'),ma20); ma200=f(row.get('ma200'),ma50)
    bbp=f(row.get('bbPercent'),0.5); bbu=f(row.get('bbUpper'),price); bbl=f(row.get('bbLower'),price)
    volr=f(row.get('volumeRatio'),1)
    atr=f(rs.get('atr'), price*0.03); vwap=rs.get('vwapDay')
    structure=rs.get('marketStructureDay'); don_hi=rs.get('donchianHighDay'); don_lo=rs.get('donchianLowDay'); don_mid=rs.get('donchianMidDay')
    raw_trend='Tăng' if price>ma20 and macd>sig and pdi>=mdi else 'Giảm' if price<ma20 and macd<sig and mdi>pdi else 'Trung tính'
    strength='Rất mạnh' if adx>=35 else 'Mạnh' if adx>=25 else 'Trung bình' if adx>=18 else 'Yếu'
    eff,reason=_effective_trend(raw_trend,rsi,f(vwap,None),price,structure,macd,sig)
    zone=_price_zone_state(price,rsi,bbp,don_hi,don_lo,f(vwap,None))
    sup_zone=rs.get('supportZoneDay') or [rs.get('activeSupportDay'),rs.get('activeSupportDay')]
    res_zone=rs.get('resistanceZoneDay') or [rs.get('activeResistanceDay'),rs.get('activeResistanceDay')]
    vol_state=_volume_state(volr,price,f(sup_zone[-1],price),f(res_zone[-1],price),atr)
    setup=_setup_type(price,f(sup_zone[-1],price),f(res_zone[-1],price),atr,zone,eff,vol_state)
    support=f(rs.get('activeSupportDay') or rs.get('supportDay'),0); resistance=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'),0)
    risk=max(price-support,0.01); reward=max(resistance-price,0); rr=round(reward/risk,2) if risk else 0
    base_score=_signal_score(eff,strength,zone,vol_state,setup,rr)
    ind={'rsi14':s(rsi),'macd':s(macd,4),'signal':s(sig,4),'histogram':s(hist,4),'adx14':s(adx),'plusDi':s(pdi),'minusDi':s(mdi),'ma20':s(ma20),'ma50':s(ma50),'ma200':s(ma200),'bbUpper':s(bbu),'bbLower':s(bbl),'bbPercent':s(bbp,3),'vwapDay':vwap,'donchianHighDay':don_hi,'donchianLowDay':don_lo,'donchianMidDay':don_mid,'marketStructureDay':structure,'volumeRatio':s(volr),'divergence':_detect_momentum_divergence(daily),'effectiveTrend':eff,'trendReason':reason,'trendStrength':strength,'zoneState':zone,'volumeState':vol_state,'setupType':setup,'signalScore':base_score,'riskReward':rr,'ichimoku':ichimoku(df),'keltner':keltner(df),'roc20':roc(df,20),'fibonacciLevelsDay':rs.get('fibonacciLevelsDay'),'fibonacciLevelsWeek':rs.get('fibonacciLevelsWeek'),'fibonacciLevelsMonth':rs.get('fibonacciLevelsMonth')}
    ind['v3FullScore']=score_item(price,rs,ind)
    return {'symbol':sym,'date':str(df.iloc[-1]['time'].date()),'price':s(price),'rsSource':str(RS_IN),'rs':rs,'indicators':ind},None

def main():
    rs_items=(load_json(RS_IN).get('items') or [])
    prev={x['symbol']:x for x in (load_json(PREV).get('items') or [])}
    partial=load_json(TMP)
    items=partial.get('items') or []
    errors=partial.get('errors') or []
    fallbacks=partial.get('fallbackSymbols') or []
    done={x.get('symbol') for x in items}|{x.get('symbol') for x in errors}
    calls=0
    print('V3 indicator universe',len(rs_items),'already done',len(done),flush=True)
    for rs in rs_items:
        sym=rs['symbol']
        if sym in done:
            print(sym,'SKIP',flush=True); continue
        if calls and calls % SLEEP_EVERY == 0:
            print('sleep',SLEEP_SECONDS,'seconds for rate limit',flush=True); time.sleep(SLEEP_SECONDS)
        try:
            item,err=build(sym,rs); calls+=1
            if item:
                items.append(item); print(sym,'OK',item['indicators']['v3FullScore']['score100'],flush=True)
            elif sym in prev:
                old=dict(prev[sym]); old['stale']=True; old['staleReason']=err; items.append(old); fallbacks.append(sym); print(sym,'FALLBACK',err,flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            if sym in prev:
                old=dict(prev[sym]); old['stale']=True; old['staleReason']=repr(e); items.append(old); fallbacks.append(sym); print(sym,'FALLBACK',repr(e),flush=True)
            else:
                errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',repr(e),flush=True)
        save_payload(TMP,items,errors,fallbacks)
    save_payload(OUT,items,errors,fallbacks)
    print('saved',OUT,'count',len(items),'errors',len(errors),'fallbacks',len(fallbacks))
if __name__=='__main__': main()
