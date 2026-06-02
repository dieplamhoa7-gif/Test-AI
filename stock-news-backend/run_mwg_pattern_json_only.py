from __future__ import annotations
import sys, json
from pathlib import Path
from datetime import datetime, timezone
from pattern_engine.core import load_data, add_indicators, find_pivots, infer_timeframe, HAS_TALIB, HAS_SCIPY
from pattern_engine.candlesticks import detect_candlesticks
from pattern_engine import chart_patterns as cp
from pattern_engine import experimental as ex
from pattern_engine.forecast import forecast, build_scenarios

def detect_all(df, pivots, include_experimental=True):
    patterns=[]
    patterns += detect_candlesticks(df, recent_bars=30)
    patterns += cp.support_resistance(df, pivots)
    patterns += cp.trendlines(df, pivots)
    patterns += cp.double_patterns(df, pivots)
    patterns += cp.head_shoulders(df, pivots)
    patterns += cp.triangle_wedge_channel(df, pivots, lookback=40)
    patterns += cp.darvas_box(df, lookback=30)
    patterns += cp.cup_handle(df, pivots, lookback=60)
    patterns += cp.rounding(df, lookback=40)
    patterns += cp.flags(df)
    patterns += cp.spring_upthrust(df, pivots)
    patterns += cp.gaps(df)
    patterns += cp.vsa_signals(df)
    patterns += cp.indicator_patterns(df, pivots)
    if include_experimental:
        patterns += ex.harmonic(df, pivots)
        patterns += ex.elliott(df, pivots)
        patterns += ex.smart_money(df, pivots)
        patterns += ex.wyckoff(df)
    return patterns

def summarize(patterns, df):
    close=float(df['close'].iloc[-1])
    active=[p for p in patterns if p.get('status') in ('active','forming','completed')]
    bull=sorted([p for p in active if p.get('direction')=='bullish'], key=lambda x:-float(x.get('score',0)))
    bear=sorted([p for p in active if p.get('direction')=='bearish'], key=lambda x:-float(x.get('score',0)))
    bw=sum(float(p.get('score',0)) for p in bull); br=sum(float(p.get('score',0)) for p in bear)
    bias='bullish' if bw>br*1.2 else 'bearish' if br>bw*1.2 else 'neutral'
    supports=sorted({round(float(p['levels']['support']),2) for p in patterns if p.get('levels',{}).get('support') and float(p['levels']['support'])<close}, reverse=True)
    resist=sorted({round(float(p['levels']['resistance']),2) for p in patterns if p.get('levels',{}).get('resistance') and float(p['levels']['resistance'])>close})
    return {'bias':bias,'bullScore':round(bw,1),'bearScore':round(br,1),'topBullishSignals':[{'type':p['type'],'score':p['score'],'conf':p['confidence']} for p in bull[:8]],'topBearishSignals':[{'type':p['type'],'score':p['score'],'conf':p['confidence']} for p in bear[:8]],'keyLevels':{'supports':supports[:6],'resistances':resist[:6]}}

def main():
    csv=Path(sys.argv[1]); out_dir=Path(sys.argv[2]); out_dir.mkdir(parents=True, exist_ok=True)
    df=load_data(csv); tf=infer_timeframe(df); df=add_indicators(df); pivots=find_pivots(df,distance=3)
    patterns=detect_all(df,pivots,include_experimental=True)
    fc=forecast(df,horizon=20,fit_window=min(60,len(df)))
    scenarios=build_scenarios(df,patterns,fc)
    summary=summarize(patterns,df)
    out={'symbol':'MWG','timeframe':tf,'createdAt':datetime.now(timezone.utc).isoformat(),'source':csv.name,'bars':len(df),'lastDate':df['date'].iloc[-1].strftime('%Y-%m-%d'),'lastClose':round(float(df['close'].iloc[-1]),2),'engineFlags':{'talib':HAS_TALIB,'scipy':HAS_SCIPY},'patterns':[{k:v for k,v in p.items() if not k.startswith('_')} for p in patterns],'forecast':{**fc,'scenarios':scenarios},'summary':summary}
    p=out_dir/'MWG_patterns_forecast.json'; p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(p),'patterns':len(patterns),'summary':summary},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
