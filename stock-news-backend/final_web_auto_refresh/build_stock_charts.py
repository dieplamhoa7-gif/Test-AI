from pathlib import Path
import json, statistics
SRC=Path('data/vn100_history_2025_06_2026_05_cache.json')
OUT=Path('firebase_public/data/charts')
MAX_ROWS=260

def ma(rows,n):
    out=[]
    for i in range(len(rows)):
        if i+1>=n:
            vals=[r['close'] for r in rows[i+1-n:i+1]]
            out.append({'time':rows[i]['time'],'value':round(sum(vals)/n,4)})
    return out

def ema(rows,n):
    out=[]; k=2/(n+1); e=None
    for r in rows:
        c=r['close']; e=c if e is None else c*k+e*(1-k)
        out.append({'time':r['time'],'value':round(e,4)})
    return out

def rsi(rows,n=14):
    out=[]; gains=[]; losses=[]
    for i in range(1,len(rows)):
        ch=rows[i]['close']-rows[i-1]['close']; gains.append(max(ch,0)); losses.append(max(-ch,0))
        if i>=n:
            g=sum(gains[-n:])/n; l=sum(losses[-n:])/n; val=100 if l==0 else 100-100/(1+g/l)
            out.append({'time':rows[i]['time'],'value':round(val,2)})
    return out

def boll(rows,n=20):
    up=[]; mid=[]; low=[]
    for i in range(len(rows)):
        if i+1>=n:
            vals=[r['close'] for r in rows[i+1-n:i+1]]; m=sum(vals)/n; sd=statistics.pstdev(vals)
            t=rows[i]['time']; mid.append({'time':t,'value':round(m,4)}); up.append({'time':t,'value':round(m+2*sd,4)}); low.append({'time':t,'value':round(m-2*sd,4)})
    return {'upper':up,'middle':mid,'lower':low}

def macd(rows):
    e12=ema(rows,12); e26=ema(rows,26); m=[]
    for a,b in zip(e12,e26): m.append({'time':a['time'],'value':round(a['value']-b['value'],4)})
    sig=[]; k=2/10; e=None
    for x in m:
        e=x['value'] if e is None else x['value']*k+e*(1-k); sig.append({'time':x['time'],'value':round(e,4)})
    hist=[{'time':a['time'],'value':round(a['value']-b['value'],4)} for a,b in zip(m,sig)]
    return {'macd':m,'signal':sig,'histogram':hist}

def pivot_points(rows, w=3):
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

def aggregate(rows,frame):
    if frame=='day': return rows
    from datetime import date
    out=[]; cur=None; curkey=None
    for r in rows:
        y,m,d=map(int,r['time'][:10].split('-')); dt=date(y,m,d)
        key=f'{dt.isocalendar().year}-W{dt.isocalendar().week:02d}' if frame=='week' else f'{y:04d}-{m:02d}'
        tm=dt.isoformat() if frame=='week' else f'{y:04d}-{m:02d}-01'
        if key!=curkey:
            if cur: out.append(cur)
            curkey=key; cur={'time':tm,'open':r['open'],'high':r['high'],'low':r['low'],'close':r['close'],'volume':r.get('volume',0)}
        else:
            cur['high']=max(cur['high'],r['high']); cur['low']=min(cur['low'],r['low']); cur['close']=r['close']; cur['volume']+=r.get('volume',0)
    if cur: out.append(cur)
    return out

def payload(sym,source,rows,frame):
    rows=rows[-(120 if frame=='month' else 180 if frame=='week' else MAX_ROWS):]
    lines=trendlines(rows)
    return {'symbol':sym,'frame':frame,'source':source,'rows':rows,'ma20':ma(rows,20),'ma50':ma(rows,50),'ema20':ema(rows,20),'ema50':ema(rows,50),'bollinger':boll(rows),'macd':macd(rows),'rsi':rsi(rows),'trendline':lines[0] if lines else None,'trendlines':lines,'patterns':pattern_labels(rows)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SRC.read_text(encoding='utf-8')); idx=[]
    for sym, obj in data.get('symbols',{}).items():
        rows=[{k:(float(v) if k!='time' else v) for k,v in r.items()} for r in obj.get('rows',[]) if r.get('time')]
        if len(rows)<30: continue
        for frame,suf in [('day',''),('week','_week'),('month','_month')]:
            fr=aggregate(rows,frame)
            if len(fr)<10: continue
            out=payload(sym,data.get('source'),fr,frame)
            (OUT/f'{sym}{suf}.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
            idx.append({'symbol':sym,'frame':frame,'rows':len(out['rows']),'path':f'/data/charts/{sym}{suf}.json'})
    (OUT/'index.json').write_text(json.dumps({'count':len(idx),'items':idx},ensure_ascii=False,indent=2),encoding='utf-8')
    print('charts',len(idx))
if __name__=='__main__': main()
