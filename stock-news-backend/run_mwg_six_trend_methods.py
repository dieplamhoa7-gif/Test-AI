import json, math
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import differential_evolution

OUT=Path('local_trend_method_reviews'); OUT.mkdir(exist_ok=True)
rows=json.loads(Path('firebase_public/data/charts/MWG.json').read_text(encoding='utf-8'))['rows']
df=pd.DataFrame(rows)
for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c], errors='coerce')
df=df.dropna().reset_index(drop=True)
N=len(df)


def atr_series(d, n=14):
    h=d.high.astype(float); l=d.low.astype(float); c=d.close.astype(float)
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()
ATR=float(atr_series(df).iloc[-1])

@dataclass
class TL:
    method:str; kind:str; x0:int; y0:float; x1:int; y1:float; slope:float; intercept:float
    touches:int=0; breaks:int=0; trust:float=0; note:str=''

def line_y(tl, x): return tl.slope*x+tl.intercept

def find_major_pivots(d, amplitude_atr=2.2, neighborhood=30, distance=5):
    h=d.high.values; l=d.low.values
    hi,_=find_peaks(h, distance=distance, prominence=ATR*1.0)
    lo,_=find_peaks(-l, distance=distance, prominence=ATR*1.0)
    highs=[]; lows=[]
    for i in hi:
        a=max(0,i-neighborhood); b=min(len(d),i+neighborhood+1)
        amp=h[i]-l[a:b].min()
        if amp>=amplitude_atr*ATR: highs.append({'idx':int(i),'price':float(h[i]),'amp':float(amp)})
    for i in lo:
        a=max(0,i-neighborhood); b=min(len(d),i+neighborhood+1)
        amp=h[a:b].max()-l[i]
        if amp>=amplitude_atr*ATR: lows.append({'idx':int(i),'price':float(l[i]),'amp':float(amp)})
    return highs,lows

def collect_metrics(tl, tol_mult=.75, d=None):
    if d is None:
        d = df
    tol=ATR*tol_mult
    arr=d.low.values if tl.kind=='support' else d.high.values
    closes=d.close.values
    touches=[]; breaks=0
    for i in range(tl.x0, len(d)):
        y=line_y(tl,i); dist=abs(arr[i]-y)
        if dist<=tol: touches.append((i,float(arr[i]),dist))
        if tl.kind=='support' and closes[i] < y-1.5*ATR: breaks+=1
        if tl.kind=='resistance' and closes[i] > y+1.5*ATR: breaks+=1
    ded=[]
    for t in touches:
        if ded and t[0]-ded[-1][0]<=8 and abs(t[1]-ded[-1][1])<=0.8*ATR:
            if t[2]<ded[-1][2]: ded[-1]=t
        else: ded.append(t)
    length=len(d)-1-tl.x0
    tl.touches=len(ded); tl.breaks=breaks
    tl.trust=tl.touches*18 + min(30,length/7) - breaks*18 + (10 if length>120 else 0)
    return tl,ded

def cluster(lines, maxn=8, price_tol=.025, slope_tol=.05):
    lines=sorted(lines,key=lambda x:(x.touches, -x.breaks, x.trust), reverse=True)
    out=[]
    for l in lines:
        dup=False
        for s in out:
            last_near=abs(l.y1/s.y1-1)<=price_tol if s.y1 else False
            mid_l=(line_y(l,l.x0)+l.y1)/2; mid_s=(line_y(s,s.x0)+s.y1)/2
            mid_near=abs(mid_l/mid_s-1)<=price_tol if mid_s else False
            slope_near=abs(l.slope-s.slope)<=slope_tol and np.sign(l.slope)==np.sign(s.slope)
            if l.kind==s.kind and slope_near and (last_near or mid_near):
                dup=True
                break
        if not dup:
            out.append(l)
        if len(out)>=maxn:
            break
    return out

def mk_line(method, kind, a, b, note=''):
    slope=(b['price']-a['price'])/(b['idx']-a['idx']); intercept=a['price']-slope*a['idx']
    return TL(method, kind, a['idx'], a['price'], N-1, slope*(N-1)+intercept, slope, intercept, note=note)

def method_major_pivot():
    highs,lows=find_major_pivots(df,2.2,30)
    lines=[]
    for piv,kind in [(lows,'support'),(highs,'resistance')]:
        for i in range(len(piv)):
            for j in range(i+1,len(piv)):
                if piv[j]['idx']-piv[i]['idx']<80: continue
                if kind=='support' and piv[j]['price']<piv[i]['price']-ATR: continue
                if kind=='resistance' and piv[j]['price']>piv[i]['price']+ATR: continue
                tl=mk_line('1 Major Pivot',kind,piv[i],piv[j])
                tl,_=collect_metrics(tl,.75)
                if tl.touches>=3 and tl.breaks<=4: lines.append(tl)
    return cluster(lines,8)

def resample_weekly(d):
    dd=d.copy(); dd['date']=pd.to_datetime(dd.time); dd=dd.set_index('date')
    w=dd.resample('W-FRI').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna().reset_index()
    w['time']=w['date'].dt.strftime('%Y-%m-%d')
    return w

def major_pivot_on_df(dfin):
    n_local=len(dfin)
    atr_local=float(atr_series(dfin).iloc[-1])
    highs,lows=find_major_pivots(dfin,2.2,30)
    lines=[]
    for piv,kind in [(lows,'support'),(highs,'resistance')]:
        for i in range(len(piv)):
            for j in range(i+1,len(piv)):
                if piv[j]['idx']-piv[i]['idx']<max(12, n_local//4): continue
                if kind=='support' and piv[j]['price']<piv[i]['price']-atr_local: continue
                if kind=='resistance' and piv[j]['price']>piv[i]['price']+atr_local: continue
                slope=(piv[j]['price']-piv[i]['price'])/(piv[j]['idx']-piv[i]['idx']); intercept=piv[i]['price']-slope*piv[i]['idx']
                tl=TL('2 MTF Weekly→Daily',kind,piv[i]['idx'],piv[i]['price'],n_local-1,slope*(n_local-1)+intercept,slope,intercept,note='weekly major pivot')
                arr=dfin.low.values if kind=='support' else dfin.high.values
                closes=dfin.close.values
                touches=[]; breaks=0
                for k in range(tl.x0, n_local):
                    y=slope*k+intercept; dist=abs(arr[k]-y)
                    if dist<=0.75*atr_local: touches.append((k,float(arr[k]),dist))
                    if kind=='support' and closes[k] < y-1.5*atr_local: breaks+=1
                    if kind=='resistance' and closes[k] > y+1.5*atr_local: breaks+=1
                ded=[]
                for t in touches:
                    if ded and t[0]-ded[-1][0]<=2 and abs(t[1]-ded[-1][1])<=0.8*atr_local:
                        if t[2]<ded[-1][2]: ded[-1]=t
                    else: ded.append(t)
                tl.touches=len(ded); tl.breaks=breaks; tl.trust=tl.touches*18 + min(30,(n_local-1-tl.x0)/2) - breaks*18
                if tl.touches>=2 and tl.breaks<=3: lines.append(tl)
    return cluster(lines,8)

def project_weekly_lines():
    w=resample_weekly(df)
    weekly=major_pivot_on_df(w.reset_index(drop=True))
    out=[]
    ratio=max(1, len(df)//max(1,len(w)))
    for tl in weekly:
        x0=min(len(df)-1, tl.x0*ratio); x1=len(df)-1
        y0=tl.y0; y1=tl.y1
        slope=(y1-y0)/(x1-x0) if x1>x0 else 0; inter=y0-slope*x0
        p=TL('2 MTF Weekly→Daily',tl.kind,x0,y0,x1,slope*x1+inter,slope,inter,note='projected weekly')
        p,_=collect_metrics(p,.9)
        if p.touches>=2 and p.breaks<=5: out.append(p)
    return cluster(out,8)

def method_log():
    d=df.copy(); highs,lows=find_major_pivots(d,2.0,30); lines=[]
    for piv,kind in [(lows,'support'),(highs,'resistance')]:
        for i in range(len(piv)):
            for j in range(i+1,len(piv)):
                if piv[j]['idx']-piv[i]['idx']<80 or piv[i]['price']<=0 or piv[j]['price']<=0: continue
                sl=(math.log(piv[j]['price'])-math.log(piv[i]['price']))/(piv[j]['idx']-piv[i]['idx']); ic=math.log(piv[i]['price'])-sl*piv[i]['idx']
                y0=math.exp(sl*piv[i]['idx']+ic); y1=math.exp(sl*(len(d)-1)+ic)
                slope=(y1-y0)/(len(d)-1-piv[i]['idx']); inter=y0-slope*piv[i]['idx']
                tl=TL('3 Log Trend',kind,piv[i]['idx'],y0,len(d)-1,y1,slope,inter,note='log fit projected linear')
                tl,_=collect_metrics(tl,.9)
                if tl.touches>=3 and tl.breaks<=5: lines.append(tl)
    return cluster(lines,8)

def method_segmented():
    y=df.close.values; best=[]
    # simple 3 segment scan by local SSE reduction
    for a in range(60,N-100,20):
        for b in range(a+50,N-40,20):
            segs=[(0,a),(a,b),(b,N-1)]
            lines=[]
            for s,e in segs:
                x=np.arange(s,e+1); yy=y[s:e+1]
                if len(x)<30: continue
                m,c=np.polyfit(x,yy,1); kind='support' if m>=0 else 'resistance'
                tl=TL('4 Segmented Regression',kind,s,float(m*s+c),N-1,float(m*(N-1)+c),float(m),float(c),note=f'segment {s}-{e}')
                tl,_=collect_metrics(tl,1.05)
                if tl.touches>=2 and tl.breaks<=6: lines.append(tl)
            if len(lines)>len(best): best=lines
    return cluster(best,8)

def method_global_opt():
    highs,lows=find_major_pivots(df,1.6,20); lines=[]
    for piv,kind in [(lows,'support'),(highs,'resistance')]:
        if len(piv)<3: continue
        xs=np.array([p['idx'] for p in piv]); ys=np.array([p['price'] for p in piv])
        sl_min,sl_max=-0.25,0.25; ic_min=float(min(ys)-60); ic_max=float(max(ys)+60)
        def obj(v):
            sl,ic=v; pred=sl*xs+ic; dist=np.abs(ys-pred); touches=np.sum(dist<=0.75*ATR); penalty=np.mean(np.minimum(dist/(ATR*3),3))
            return -touches + penalty
        try:
            res=differential_evolution(obj,[(sl_min,sl_max),(ic_min,ic_max)],maxiter=80,popsize=8,polish=False,seed=7)
            sl,ic=res.x; x0=int(xs.min()); y0=float(sl*x0+ic); y1=float(sl*(N-1)+ic)
            tl=TL('5 Global Multi-touch Opt',kind,x0,y0,N-1,y1,float(sl),float(ic))
            tl,_=collect_metrics(tl,.85)
            if tl.touches>=3 and tl.breaks<=5: lines.append(tl)
        except Exception: pass
    return cluster(lines,8)

def method_hybrid():
    all_lines=method_major_pivot()+project_weekly_lines()+method_log()+method_segmented()+method_global_opt()
    filtered=[]
    for l in all_lines:
        l.method='6 Hybrid Best-of'
        min_touches = 4 if l.kind == 'support' else 3
        if l.touches < min_touches:
            continue
        if l.breaks > 1:
            continue
        if l.trust < 120:
            continue
        if (l.x1 - l.x0) < 90:
            continue
        filtered.append(l)
    return cluster(filtered,7,price_tol=.018,slope_tol=.04)

methods=[method_major_pivot, project_weekly_lines, method_log, method_segmented, method_global_opt, method_hybrid]
results={}

def plot(name, lines):
    fig,ax=plt.subplots(figsize=(16,8),dpi=150)
    x=np.arange(len(df)); ax.plot(x,df.close.values,color='#d9e4ff',lw=1.35,label='MWG close')
    for tl in lines:
        col='#00e676' if tl.kind=='support' else '#ff5252'
        ax.plot([tl.x0,tl.x1],[tl.y0,tl.y1],color=col,lw=2.3,alpha=.95)
        ax.text(tl.x1,tl.y1,('S' if tl.kind=='support' else 'R')+f' {tl.y1:.1f} T{tl.touches} B{tl.breaks} Q{tl.trust:.0f}',color=col,fontsize=8,fontweight='bold',bbox=dict(boxstyle='round,pad=.2',fc='#111827',ec=col,alpha=.9))
    ax.set_title(f'MWG Day - {name} | lines {len(lines)}',color='white',fontsize=15,fontweight='bold')
    ax.set_facecolor('#0f172a'); fig.patch.set_facecolor('#0f172a'); ax.grid(color='#334155',alpha=.35); ax.tick_params(colors='#cbd5e1')
    for sp in ax.spines.values(): sp.set_color('#475569')
    ax.legend(facecolor='#0f172a',edgecolor='#475569',labelcolor='white')
    fig.tight_layout(); out=OUT/(name.lower().replace(' ','_').replace('→','to').replace('/','_')+'.png'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
    return out

summary=[]
for fn in methods:
    lines=fn(); name=lines[0].method if lines else fn.__name__.replace('_',' ')
    results[name]=lines; out=plot(name,lines)
    summary.append((name,len(lines),str(out),[(l.kind,round(l.y1,2),l.touches,l.breaks,round(l.trust,1),l.note) for l in lines]))

# combined 2x3
fig,axs=plt.subplots(3,2,figsize=(18,18),dpi=130); axs=axs.ravel()
for ax,(name,_,_,_) in zip(axs,summary):
    lines=results[name]; x=np.arange(len(df)); ax.plot(x,df.close.values,color='#d9e4ff',lw=1)
    for tl in lines:
        col='#00e676' if tl.kind=='support' else '#ff5252'; ax.plot([tl.x0,tl.x1],[tl.y0,tl.y1],color=col,lw=1.8)
    ax.set_title(f'{name} ({len(lines)})',color='white'); ax.set_facecolor('#0f172a'); ax.grid(color='#334155',alpha=.3); ax.tick_params(colors='#cbd5e1')
    for sp in ax.spines.values(): sp.set_color('#475569')
fig.patch.set_facecolor('#0f172a'); fig.tight_layout(); combined=OUT/'mwg_six_methods_combined.png'; fig.savefig(combined,bbox_inches='tight')

md=['# MWG six trendline methods local review','']
for name,cnt,out,items in summary:
    md.append(f'## {name}'); md.append(f'- lines: {cnt}'); md.append(f'- image: {out}');
    for it in items: md.append(f'  - {it}')
    md.append('')
md.append(f'Combined: {combined}')
(OUT/'summary.md').write_text('\n'.join(md),encoding='utf-8')
print('\n'.join(md))
