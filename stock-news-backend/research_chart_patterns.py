from pathlib import Path
import json, math, statistics
SRC=Path('firebase_public/data/charts')
OUT=Path('data/chart_pattern_research.json')

def pivots(rows,w=3):
    hi=[]; lo=[]
    for i in range(w,len(rows)-w):
        seg=rows[i-w:i+w+1]
        if rows[i]['high']>=max(r['high'] for r in seg): hi.append(i)
        if rows[i]['low']<=min(r['low'] for r in seg): lo.append(i)
    return hi,lo

def atr(rows,n=20):
    recent=rows[-n:]
    return sum(r['high']-r['low'] for r in recent)/max(1,len(recent))

def line_eval(rows,i,j,key):
    if j<=i: return None
    y1=rows[i][key]; y2=rows[j][key]; slope=(y2-y1)/(j-i); a=y1-slope*i
    tolerance=max(atr(rows)*0.45, rows[-1]['close']*0.006)
    touches=0; violations=0; max_break=0
    for k,r in enumerate(rows[i:]):
        idx=i+k; y=a+slope*idx
        val=r['low'] if key=='low' else r['high']
        close=r['close']
        if abs(val-y)<=tolerance: touches+=1
        if key=='low':
            br=max(0,y-close)
        else:
            br=max(0,close-y)
        if br>tolerance: violations+=1; max_break=max(max_break,br)
    span=j-i; slope_pct=slope/rows[-1]['close']*100
    score=touches*18 + min(span,80)*0.25 - violations*20 - max_break/max(tolerance,1e-9)*10
    if abs(slope_pct)>1.2: score-=15
    y_now=a+slope*(len(rows)-1)
    dist=abs(rows[-1]['close']-y_now)/rows[-1]['close']*100
    if dist>18: score-=20
    return {'i':i,'j':j,'priceNow':round(y_now,3),'slopePctPerBar':round(slope_pct,4),'touches':touches,'violations':violations,'score':round(score,2),'distPct':round(dist,2),'points':[{'time':rows[i]['time'],'value':round(y1,3)},{'time':rows[-1]['time'],'value':round(y_now,3)}]}

def best_trendlines(rows):
    hi,lo=pivots(rows,3); out=[]
    for piv,key,typ in [(lo,'low','support-trend'),(hi,'high','resistance-trend')]:
        cands=[]
        for a in piv[-14:]:
            for b in piv[-14:]:
                if b>a+12:
                    ev=line_eval(rows,a,b,key)
                    if ev and ev['touches']>=3 and ev['violations']<=2 and ev['score']>=35:
                        ev.update({'type':typ,'anchors':[rows[a]['time'],rows[b]['time']]}); cands.append(ev)
        cands.sort(key=lambda x:x['score'], reverse=True)
        out += cands[:2]
    return out

def sr_levels(rows):
    hi,lo=pivots(rows,3); tol=max(atr(rows)*0.65, rows[-1]['close']*0.01); levels=[]
    for piv,key,typ in [(lo,'low','support'),(hi,'high','resistance')]:
        clusters=[]
        for idx in piv[-60:]:
            p=rows[idx][key]
            for c in clusters:
                if abs(p-c['price'])<=tol:
                    c['vals'].append(p); c['idx'].append(idx); c['price']=sum(c['vals'])/len(c['vals']); break
            else: clusters.append({'price':p,'vals':[p],'idx':[idx]})
        for c in clusters:
            touches=len(c['idx']); recency=max(c['idx'])/len(rows); dist=abs(rows[-1]['close']-c['price'])/rows[-1]['close']*100
            score=touches*22+recency*15-max(0,dist-12)*2
            if touches>=2:
                levels.append({'type':typ,'price':round(c['price'],3),'zoneLow':round(c['price']-tol,3),'zoneHigh':round(c['price']+tol,3),'touches':touches,'distPct':round(dist,2),'score':round(score,2)})
    return sorted(levels,key=lambda x:x['score'],reverse=True)[:8]

def patterns(rows):
    out=[]; last=rows[-1]; closes=[r['close'] for r in rows]
    hi20=max(r['high'] for r in rows[-20:]); lo20=min(r['low'] for r in rows[-20:]); rng=(hi20-lo20)/last['close']*100
    vol20=sum(r.get('volume',0) for r in rows[-20:])/20
    if rng<12: out.append({'type':'box-consolidation','text':'Hộp tích lũy 20 phiên','score':round(100-rng*5,1),'rangePct':round(rng,2),'low':lo20,'high':hi20})
    if last['close']>hi20*0.995 and last.get('volume',0)>vol20*1.3: out.append({'type':'breakout-watch','text':'Tiệm cận/vượt đỉnh hộp kèm volume','score':75})
    red_vol=sum(1 for r in rows[-10:] if r['close']<r['open'] and r.get('volume',0)>vol20*1.2)
    if red_vol>=3: out.append({'type':'distribution-risk','text':'Nhiều phiên đỏ volume cao','score':min(95,50+red_vol*10)})
    return out

def main():
    items=[]
    for p in SRC.glob('*.json'):
        if '_' in p.stem or p.stem=='index': continue
        d=json.loads(p.read_text(encoding='utf-8')); rows=d.get('rows',[])
        if len(rows)<80: continue
        rows=rows[-220:]
        tl=best_trendlines(rows); sr=sr_levels(rows); pt=patterns(rows)
        if tl or sr or pt:
            items.append({'symbol':p.stem,'close':rows[-1]['close'],'trendlines':tl,'levels':sr,'patterns':pt})
    items.sort(key=lambda x:max([t.get('score',0) for t in x['trendlines']]+[l.get('score',0) for l in x['levels']]+[p.get('score',0) for p in x['patterns']]+[0]), reverse=True)
    OUT.write_text(json.dumps({'count':len(items),'items':items},ensure_ascii=False,indent=2),encoding='utf-8')
    print('research items',len(items),'out',OUT)
if __name__=='__main__': main()
