from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history, _compute_indicators, _detect_momentum_divergence, _price_zone_state, _volume_state, _effective_trend, _setup_type, _signal_score

RS_IN=Path('data/rs_levels_only_cache.json')
OUT=Path('data/v3_full_indicator_cache.json')

def to_float(v, default=0.0):
    try:
        if v is None: return default
        if hasattr(v,'item'): v=v.item()
        return float(v)
    except Exception:
        return default

def safe(v, nd=2):
    try:
        if v is None or pd.isna(v): return None
        return round(float(v), nd)
    except Exception:
        return v

def load_rs():
    data=json.load(open(RS_IN,encoding='utf-8'))
    return {x['symbol']:x for x in data.get('items',[])}

def build_one(sym, rs):
    df=_load_history(sym)
    if df is None or df.empty:
        return None, 'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    if len(df)<60:
        return None, f'short history {len(df)}'
    daily=_compute_indicators(df.copy())
    row=daily.iloc[-1]
    price=to_float(row.get('close'), to_float(df.iloc[-1].get('close')))
    rsi=to_float(row.get('rsi14'),50)
    macd=to_float(row.get('macd'),0)
    signal=to_float(row.get('signal'),0)
    histogram=to_float(row.get('histogram'),0)
    adx=to_float(row.get('adx14'),0)
    plus_di=to_float(row.get('plusDi'),0)
    minus_di=to_float(row.get('minusDi'),0)
    ma20=to_float(row.get('ma20'),price)
    ma50=to_float(row.get('ma50'),ma20)
    ma200=to_float(row.get('ma200'),ma50)
    bb_upper=to_float(row.get('bbUpper'),price)
    bb_lower=to_float(row.get('bbLower'),price)
    bb_percent=to_float(row.get('bbPercent'),0.5)
    volume_ratio=to_float(row.get('volumeRatio'),1)
    atr=to_float(rs.get('atr'), max(price*0.03,0.01))
    vwap=to_float(rs.get('vwapDay'), None)
    don_hi=rs.get('donchianHighDay'); don_lo=rs.get('donchianLowDay'); don_mid=rs.get('donchianMidDay')
    structure=rs.get('marketStructureDay')
    raw_trend='Tăng' if price>ma20 and macd>signal and plus_di>=minus_di else 'Giảm' if price<ma20 and macd<signal and minus_di>plus_di else 'Trung tính'
    strength='Rất mạnh' if adx>=35 else 'Mạnh' if adx>=25 else 'Trung bình' if adx>=18 else 'Yếu'
    eff_trend, trend_reason=_effective_trend(raw_trend,rsi,vwap,price,structure,macd,signal)
    zone_state=_price_zone_state(price,rsi,bb_percent,don_hi,don_lo,vwap)
    support_high=None
    if isinstance(rs.get('supportZoneDay'),list) and len(rs['supportZoneDay'])>=2:
        support_high=to_float(rs['supportZoneDay'][1], rs.get('activeSupportDay'))
    else:
        support_high=to_float(rs.get('activeSupportDay'),price)
    resistance_high=None
    if isinstance(rs.get('resistanceZoneDay'),list) and len(rs['resistanceZoneDay'])>=2:
        resistance_high=to_float(rs['resistanceZoneDay'][1], rs.get('activeResistanceDay'))
    else:
        resistance_high=to_float(rs.get('activeResistanceDay'),price)
    vol_state=_volume_state(volume_ratio,price,support_high,resistance_high,atr)
    setup=_setup_type(price,support_high,resistance_high,atr,zone_state,eff_trend,vol_state)
    support=to_float(rs.get('activeSupportDay') or rs.get('supportDay'),0)
    resistance=to_float(rs.get('activeResistanceDay') or rs.get('resistanceDay'),0)
    risk=max(price-support,0.01) if support else 0.01
    reward=max(resistance-price,0.0) if resistance else 0.0
    risk_reward=round(reward/risk,2) if risk else 0
    score=_signal_score(eff_trend,strength,zone_state,vol_state,setup,risk_reward)
    divergence=_detect_momentum_divergence(daily)
    ret5=safe(price/to_float(daily.iloc[-6].get('close'),price)-1,4) if len(daily)>=6 else None
    item={
        'symbol':sym,'date':str(df.iloc[-1]['time'].date()),'price':safe(price,2),
        'rsSource':'data/rs_levels_only_cache.json','rs':rs,
        'indicators':{
            'rsi14':safe(rsi,2),'macd':safe(macd,4),'signal':safe(signal,4),'histogram':safe(histogram,4),
            'adx14':safe(adx,2),'plusDi':safe(plus_di,2),'minusDi':safe(minus_di,2),
            'ma20':safe(ma20,2),'ma50':safe(ma50,2),'ma200':safe(ma200,2),
            'bbUpper':safe(bb_upper,2),'bbLower':safe(bb_lower,2),'bbPercent':safe(bb_percent,3),
            'vwapDay':rs.get('vwapDay'),'donchianHighDay':don_hi,'donchianLowDay':don_lo,'donchianMidDay':don_mid,
            'marketStructureDay':structure,'volumeRatio':safe(volume_ratio,2),'ret5':ret5,
            'divergence':divergence,'effectiveTrend':eff_trend,'trendReason':trend_reason,'trendStrength':strength,
            'zoneState':zone_state,'volumeState':vol_state,'setupType':setup,'signalScore':score,'riskReward':risk_reward,
            'fibonacciLevelsDay':rs.get('fibonacciLevelsDay'),
            'fibonacciLevelsWeek':rs.get('fibonacciLevelsWeek'),
            'fibonacciLevelsMonth':rs.get('fibonacciLevelsMonth')
        }
    }
    return item, None

def main():
    rs_map=load_rs(); items=[]; errors=[]
    for sym,rs in rs_map.items():
        try:
            item,err=build_one(sym,rs)
            if item:
                items.append(item); print(sym,'OK',item['indicators']['adx14'],item['indicators']['riskReward'],flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',repr(e),flush=True)
    payload={'createdAt':datetime.now().isoformat(),'method':'V3 full indicator cache; reads R/S from rs_levels_only_cache and does not recompute R/S','rsInput':str(RS_IN),'count':len(items),'errorCount':len(errors),'items':items,'errors':errors}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('saved',OUT,'count',len(items),'errors',len(errors))
if __name__=='__main__': main()
