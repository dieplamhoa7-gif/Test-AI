import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

BASE = Path('firebase_public/data/charts')
ZONE_PCT = 0.003
MIN_TOUCH = 3
MIN_SPAN = 45


def atr_series(df, n=14):
    h=df.high.astype(float); l=df.low.astype(float); c=df.close.astype(float)
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()


def build_for_symbol(symbol: str):
    path = BASE / f'{symbol}.json'
    if not path.exists():
        return None
    try:
        rows = json.loads(path.read_text(encoding='utf-8')).get('rows') or []
    except Exception:
        return None
    if len(rows) < 80:
        return None
    df = pd.DataFrame(rows)
    for c in ['open','high','low','close','volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna().reset_index(drop=True)
    if len(df) < 80:
        return None
    N = len(df)
    ATR = float(atr_series(df).iloc[-1])
    hi_idx,_=find_peaks(df.high.values, distance=5, prominence=ATR*0.8)
    lo_idx,_=find_peaks(-df.low.values, distance=5, prominence=ATR*0.8)

    def annotate(idxs, kind):
        out=[]
        arr=df.high.values if kind=='high' else df.low.values
        for i in idxs:
            a=max(0,i-20); b=min(N,i+21)
            amp=(arr[i]-df.low.values[a:b].min()) if kind=='high' else (df.high.values[a:b].max()-arr[i])
            if amp>=1.8*ATR:
                out.append({'idx':int(i),'price':float(arr[i]),'kind':kind,'time':str(df.iloc[i].time),'amp':float(amp)})
        return out

    highs=annotate(hi_idx,'high'); lows=annotate(lo_idx,'low')
    candle_high=df.high.values
    candle_low=df.low.values
    candle_close=df.close.values
    lines=[]
    for anchor_pivots, kind in [(lows,'support'), (highs,'resistance')]:
        side_price_arr = candle_low if kind=='support' else candle_high
        for i in range(len(anchor_pivots)):
            for j in range(i+1, len(anchor_pivots)):
                a,b=anchor_pivots[i], anchor_pivots[j]
                span=b['idx']-a['idx']
                if span<MIN_SPAN: continue
                slope=(b['price']-a['price'])/span
                if kind=='support' and slope < -0.05: continue
                if kind=='resistance' and slope > 0.05: continue
                intercept=a['price']-slope*a['idx']
                touches=[]
                for k in range(a['idx'], min(N, b['idx']+1)):
                    y=slope*k+intercept
                    px=float(side_price_arr[k])
                    rel=abs(px/max(1e-9,y)-1)
                    if rel<=ZONE_PCT:
                        touches.append({'idx':k,'price':px,'time':str(df.iloc[k].time),'rel':rel})
                touches=sorted(touches,key=lambda x:x['idx'])
                zones=[]
                for t in touches:
                    if zones and t['idx']-zones[-1]['idx']<=4 and abs(t['price']/zones[-1]['price']-1)<=ZONE_PCT:
                        if t['rel']<zones[-1]['rel']:
                            zones[-1]=t
                    else:
                        zones.append(t)
                if len(zones)<MIN_TOUCH: continue
                first,last=zones[0], zones[-1]
                length=last['idx']-first['idx']
                if length<MIN_SPAN: continue
                breaks=0
                for k in range(first['idx'], last['idx']+1):
                    y=slope*k+intercept
                    if kind=='support' and df.close.iloc[k] < y*(1-ZONE_PCT*1.2): breaks+=1
                    if kind=='resistance' and df.close.iloc[k] > y*(1+ZONE_PCT*1.2): breaks+=1
                if breaks > max(2, len(zones), length//60):
                    continue
                last_close = float(df.close.iloc[N-1])
                y_last = slope*(N-1)+intercept
                if last_close > 0 and abs(y_last/last_close - 1) > 0.35:
                    continue
                score=len(zones)*35 + length*0.35 - breaks*18 + a['amp']*0.8 + b['amp']*0.8
                end_idx = N - 1
                end_time = str(df.iloc[end_idx].time)
                lines.append({
                    'kind':kind,'slope':float(slope),'score':float(score),'touches':len(zones),'breaks':int(breaks),
                    'x0':first['idx'],'x1':end_idx,'y0':float(slope*first['idx']+intercept),'y1':float(slope*end_idx+intercept),
                    'points':[{'time':first['time'],'value':round(float(slope*first['idx']+intercept),2)},{'time':end_time,'value':round(float(slope*end_idx+intercept),2)}],
                    'touchPoints':[{'idx':z['idx'],'time':z['time'],'price':round(z['price'],2)} for z in zones],
                    'source':'touchzone-0.3pct-full'
                })
    def pick_side(side_lines, max_lines=6):
        side_lines = sorted(side_lines, key=lambda x:(x['touches'], -x['breaks'], x['score']), reverse=True)
        picked=[]
        family_counts={}
        for l in side_lines:
            lmid=(l['y0']+l['y1'])/2
            family_key=None
            for idx,s in enumerate(picked):
                smid=(s['y0']+s['y1'])/2
                slope_near=abs(l['slope']-s['slope'])<=0.03 and np.sign(l['slope'])==np.sign(s['slope'])
                price_near=abs(lmid/smid-1)<=0.02 if smid else False
                overlap=not (l['x1']<s['x0'] or l['x0']>s['x1'])
                if slope_near and price_near and overlap:
                    family_key=idx
                    break
            if family_key is None:
                picked.append(l)
                family_counts[len(picked)-1] = 1
            elif family_counts.get(family_key, 0) < 2:
                picked.append(l)
                family_counts[family_key] = family_counts.get(family_key, 0) + 1
            if len(picked)>=max_lines:
                break
        return picked
    sup_lines=[l for l in lines if l['kind']=='support']
    res_lines=[l for l in lines if l['kind']=='resistance']
    selected=pick_side(sup_lines, 6) + pick_side(res_lines, 6)
    payload={
        'symbol':symbol,'asOfDate':str(df.iloc[-1].time),'asOfPrice':float(df.iloc[-1].close),'createdAt':'2026-05-28T09:55:00+00:00',
        'summary':{'trendlines':len(selected),'parallelChannels':0,'pitchforks':0,'linregChannels':0,'srLevels':0,'patterns':0,'candlestickSignals':0,'currentBias':'touchzone-0.3pct'},
        'trendlines':[], 'srLevels':[], 'patterns':[], 'candlestickSignals':[], 'rows':[]
    }
    for i,l in enumerate(selected,1):
        payload['trendlines'].append({
            'id':f'touchzone_{i}','type':'uptrend' if l['kind']=='support' else 'downtrend','points':l['points'],'slopePerBar':round(l['slope'],5),
            'touches':l['touches'],'lengthBars':int(l['x1']-l['x0']),'rSquared':0.9,'valid':True,'score':round(l['score'],2),'trust':round(l['score'],2),
            'breaks':l['breaks'],'source':l['source'],'touchPoints':l['touchPoints']
        })
    out = BASE / f'{symbol}_touchzone_day.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return symbol, len(selected)

symbols=[]
for p in BASE.glob('*.json'):
    name=p.stem
    if '_' in name:
        continue
    symbols.append(name.upper())
symbols=sorted(set(symbols))
results=[]
for s in symbols:
    r=build_for_symbol(s)
    if r:
        results.append(r)
print('generated', len(results), 'symbols')
print(results[:20])
