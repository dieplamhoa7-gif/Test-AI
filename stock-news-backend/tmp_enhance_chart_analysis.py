from pathlib import Path
p=Path('build_stock_chart_cache.py')
s=p.read_text(encoding='utf-8')
old="""def trendlines(rows):
    if len(rows)<40: return []
    recent=rows[-120:]
    lows=sorted(range(len(recent)), key=lambda i: recent[i]['low'])[:2]
    highs=sorted(range(len(recent)), key=lambda i: recent[i]['high'], reverse=True)[:2]
    lines=[]
    for idxs, key, kind in [(sorted(lows),'low','support'),(sorted(highs),'high','resistance')]:
        if len(idxs)==2 and idxs[0]!=idxs[1]:
            lines.append({'type':kind,'points':[{'time':recent[idxs[0]]['time'],'value':recent[idxs[0]][key]},{'time':recent[idxs[1]]['time'],'value':recent[idxs[1]][key]}]})
    return lines
"""
new="""def pivot_points(rows, w=3):
    highs=[]; lows=[]
    for i in range(w, len(rows)-w):
        seg=rows[i-w:i+w+1]
        if rows[i]['high'] >= max(x['high'] for x in seg): highs.append(i)
        if rows[i]['low'] <= min(x['low'] for x in seg): lows.append(i)
    return highs, lows

def line_from_points(rows, i, j, key, typ, color=None):
    if i==j: return None
    vi=rows[i][key]; vj=rows[j][key]
    slope=(vj-vi)/(j-i)
    # extend to the latest bar for easier visual reading
    end=len(rows)-1
    vend=vj+slope*(end-j)
    return {'type':typ,'method':'pivot','points':[{'time':rows[i]['time'],'value':round(vi,4)},{'time':rows[end]['time'],'value':round(vend,4)}], 'anchors':[rows[i]['time'], rows[j]['time']], 'slope':round(slope,6), 'label':typ}

def cluster_levels(rows, key, typ, lookback=160, max_levels=5):
    recent=rows[-lookback:]
    atr=sum((r['high']-r['low']) for r in recent[-20:])/max(1,min(20,len(recent)))
    tol=max(atr*0.7, (recent[-1]['close'] if recent else 1)*0.012)
    piv_h,piv_l=pivot_points(recent,3)
    piv=piv_l if key=='low' else piv_h
    clusters=[]
    for idx in piv:
        price=recent[idx][key]
        for c in clusters:
            if abs(price-c['price'])<=tol:
                c['vals'].append(price); c['touches']+=1; c['last']=idx; c['price']=sum(c['vals'])/len(c['vals']); break
        else:
            clusters.append({'price':price,'vals':[price],'touches':1,'last':idx})
    clusters.sort(key=lambda c:(c['touches'], c['last']), reverse=True)
    out=[]
    for c in clusters[:max_levels]:
        p=round(c['price'],4); zone=round(tol,4)
        out.append({'type':typ,'method':'pivot-cluster','price':p,'zoneLow':round(p-zone,4),'zoneHigh':round(p+zone,4),'touches':c['touches'],'points':[{'time':recent[0]['time'],'value':p},{'time':recent[-1]['time'],'value':p}], 'label':f"{typ} {p:g}"})
    return out

def pattern_labels(rows):
    out=[]
    if len(rows)<25: return out
    last=rows[-1]; prev=rows[-2]
    body=abs(last['close']-last['open']); rng=max(1e-9,last['high']-last['low'])
    upper=last['high']-max(last['open'],last['close']); lower=min(last['open'],last['close'])-last['low']
    vol20=sum(r.get('volume',0) for r in rows[-20:])/20
    if lower>body*2 and lower/rng>0.45: out.append({'time':last['time'],'price':last['low'],'type':'hammer','text':'Hammer/rút chân'})
    if upper>body*2 and upper/rng>0.45: out.append({'time':last['time'],'price':last['high'],'type':'shooting-star','text':'Râu trên/xả'})
    if last['close']>last['open'] and prev['close']<prev['open'] and last['close']>=prev['open'] and last['open']<=prev['close']: out.append({'time':last['time'],'price':last['high'],'type':'bullish-engulfing','text':'Bull engulf'})
    if last.get('volume',0)>vol20*1.8 and last['close']<last['open']: out.append({'time':last['time'],'price':last['high'],'type':'distribution-volume','text':'Vol đỏ lớn'})
    return out

def trendlines(rows):
    if len(rows)<40: return []
    recent=rows[-180:]
    highs,lows=pivot_points(recent,3)
    lines=[]
    for piv,key,typ in [(lows,'low','support-trend'),(highs,'high','resistance-trend')]:
        if len(piv)>=2:
            # Prefer recent anchors but keep enough distance
            pairs=[(a,b) for a in piv[-8:] for b in piv[-8:] if b>a+8]
            if pairs:
                a,b=max(pairs, key=lambda x:x[1])
                ln=line_from_points(recent,a,b,key,typ)
                if ln: lines.append(ln)
    lines += cluster_levels(rows,'low','horizontal-support')
    lines += cluster_levels(rows,'high','horizontal-resistance')
    return lines[:12]
"""
s=s.replace(old,new)
s=s.replace("'trendline':lines[0] if lines else None,'trendlines':lines}", "'trendline':lines[0] if lines else None,'trendlines':lines,'patterns':pattern_labels(rows)}")
p.write_text(s,encoding='utf-8')
print('patched chart analysis')
