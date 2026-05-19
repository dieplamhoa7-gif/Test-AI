from __future__ import annotations
import json, sys, datetime as dt
from pathlib import Path
import pandas as pd
import numpy as np
ROOT = Path(__file__).resolve().parent
HIST=ROOT / 'data/vn100_history_2025_06_2026_05_cache.json'
OUT=ROOT / 'data/sr_levels_practical_selected.json'
SYMS=sys.argv[1:] or ['MWG','FPT','VPB','VCI','SSI','MSN']

def atr(df,n=14):
    h,l,c=df.high,df.low,df.close
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def ichimoku(df):
    h,l=df.high,df.low
    return (h.rolling(9).max()+l.rolling(9).min())/2,(h.rolling(26).max()+l.rolling(26).min())/2,(h.rolling(52).max()+l.rolling(52).min())/2
def rsi(close,n=14):
    d=close.diff(); up=d.clip(lower=0).rolling(n).mean(); dn=(-d.clip(upper=0)).rolling(n).mean()
    return 100-100/(1+up/(dn+1e-9))
def mfi(df,n=14):
    tp=(df.high+df.low+df.close)/3; mf=tp*df.volume; sg=np.sign(tp.diff()).fillna(0)
    pos=mf.where(sg>0,0).rolling(n).sum(); neg=mf.where(sg<0,0).rolling(n).sum()
    return 100-100/(1+pos/(neg+1e-9))
def supertrend(df,n=10,mult=3):
    a=atr(df,n); hl2=(df.high+df.low)/2; lower=hl2-mult*a; upper=hl2+mult*a
    st=pd.Series(index=df.index,dtype=float); direc=pd.Series(index=df.index,dtype=int)
    for i in range(len(df)):
        if i==0 or pd.isna(a.iloc[i]): st.iloc[i]=np.nan; direc.iloc[i]=1; continue
        prev=st.iloc[i-1] if pd.notna(st.iloc[i-1]) else lower.iloc[i]
        pdirec=direc.iloc[i-1] if pd.notna(direc.iloc[i-1]) else 1
        direc.iloc[i]=1 if df.close.iloc[i]>prev else (-1 if df.close.iloc[i]<prev else pdirec)
        st.iloc[i]=max(lower.iloc[i],prev) if direc.iloc[i]>0 else min(upper.iloc[i],prev)
    return st

def points(df,lookback=180):
    sub=df.tail(lookback).reset_index(drop=True); pts=[]
    # swing: require local extremum and some prominence
    for win,w in [(3,1.1),(5,1.25)]:
        for i in range(win,len(sub)-win):
            if sub.high.iloc[i]>=sub.high.iloc[i-win:i+win+1].max(): pts.append({'p':float(sub.high.iloc[i]),'src':'swing_high','w':w})
            if sub.low.iloc[i]<=sub.low.iloc[i-win:i+win+1].min(): pts.append({'p':float(sub.low.iloc[i]),'src':'swing_low','w':w})
    # high volume price nodes
    lo,hi=float(sub.low.min()),float(sub.high.max())
    if hi>lo:
        bins=48; edges=np.linspace(lo,hi,bins+1); vols=np.zeros(bins)
        for _,r in sub.iterrows():
            a=max(0,np.searchsorted(edges,r.low,side='right')-1); b=min(bins-1,np.searchsorted(edges,r.high,side='left'))
            if b>=a: vols[a:b+1]+=float(r.volume)/(b-a+1)
        for i in np.argsort(vols)[-8:]: pts.append({'p':float((edges[i]+edges[i+1])/2),'src':'vol_node','w':1+float(vols[i]/(vols.max()+1e-9))})
    ten,kij,spanb=ichimoku(df); vwap=(df.close*df.volume).rolling(30).sum()/(df.volume.rolling(30).sum()+1e-9); st=supertrend(df)
    for src,ser,w in [('ma20',df.close.rolling(20).mean(),.85),('ma50',df.close.rolling(50).mean(),.9),('ma100',df.close.rolling(100).mean(),.75),('ma200',df.close.rolling(200).mean(),.7),('vwap30',vwap,.9),('ich_tenkan',ten,.7),('ich_kijun',kij,.9),('ich_spanb',spanb,.75),('supertrend',st,.9)]:
        val=ser.iloc[-1]
        if pd.notna(val): pts.append({'p':float(val),'src':src,'w':w})
    return pts

def cluster(pts,price,atrv):
    # very tight cluster radius; zone itself intentionally narrow for actionable S/R
    radius=max(price*0.0025, min(price*0.006, atrv*0.28))
    clusters=[]
    for p in sorted(pts,key=lambda x:x['p']):
        found=False
        for c in clusters:
            if abs(p['p']-c['center'])<=radius:
                c['pts'].append(p); c['center']=sum(x['p']*x['w'] for x in c['pts'])/sum(x['w'] for x in c['pts']); found=True; break
        if not found: clusters.append({'center':p['p'],'pts':[p]})
    out=[]
    half=max(price*0.0015, min(price*0.004, atrv*0.18))
    for c in clusters:
        if len(c['pts'])<2: continue
        vals=[x['p'] for x in c['pts']]; ws=[x['w'] for x in c['pts']]; center=sum(v*w for v,w in zip(vals,ws))/sum(ws)
        src={}
        for x in c['pts']: src[x['src']]=src.get(x['src'],0)+1
        # prefer narrow actionable band around weighted center, not entire min-max cluster
        lo=center-half; hi=center+half
        strength=sum(ws)+len(c['pts'])*0.75+1/(1+abs(price-center)/max(atrv,1e-6))
        out.append({'low':round(lo,2),'high':round(hi,2),'center':round(center,2),'strength':round(strength,2),'touches':len(c['pts']),'sources':src,'distPct':round((price-center)/price*100,2),'widthPct':round((hi-lo)/price*100,2)})
    return sorted(out,key=lambda x:x['center'])

def dedupe_gap(levels,price,atrv,side):
    # enforce practical separation between displayed S/R levels
    min_gap=max(price*0.018, atrv*0.85)  # around 1.8% or 0.85 ATR
    selected=[]
    for lv in sorted(levels,key=lambda x:abs(x['center']-price)):
        if all(abs(lv['center']-s['center'])>=min_gap for s in selected):
            selected.append(lv)
        else:
            # if too close, keep stronger one
            for i,s in enumerate(selected):
                if abs(lv['center']-s['center'])<min_gap and lv['strength']>s['strength']*1.15:
                    selected[i]=lv
                    break
    return sorted(selected,key=lambda x:abs(x['center']-price))[:4]

def analyze(sym,rows):
    df=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
    for col in ['open','high','low','close','volume']: df[col]=pd.to_numeric(df[col],errors='coerce')
    price=float(df.close.iloc[-1]); atrv=float(atr(df).iloc[-1]); cls=cluster(points(df),price,atrv)
    current=[]
    for c in cls:
        if c['low']<=price<=c['high'] or abs(c['center']-price)<=max(price*0.004,atrv*0.25): current.append(c)
    # remove current levels from S/R candidates and enforce below/above with buffer
    cur_centers=[c['center'] for c in current]
    supports=[c for c in cls if c['center']<price and all(abs(c['center']-cc)>max(price*0.008,atrv*.45) for cc in cur_centers)]
    resistances=[c for c in cls if c['center']>price and all(abs(c['center']-cc)>max(price*0.008,atrv*.45) for cc in cur_centers)]
    supports=dedupe_gap(supports,price,atrv,'S'); resistances=dedupe_gap(resistances,price,atrv,'R')
    return {'symbol':sym,'date':str(df.time.iloc[-1]),'close':round(price,2),'atr14':round(atrv,2),'currentZone':current[:1],'supports':supports,'resistances':resistances,'indicators':{'ma20':round(float(df.close.rolling(20).mean().iloc[-1]),2),'ma50':round(float(df.close.rolling(50).mean().iloc[-1]),2),'rsi14':round(float(rsi(df.close).iloc[-1]),2),'mfi14':round(float(mfi(df).iloc[-1]),2)}}

def main():
    data=json.load(open(HIST,encoding='utf-8'))['symbols']; items=[]
    for sym in SYMS: items.append(analyze(sym,data[sym]['rows']) if sym in data else {'symbol':sym,'error':'missing'})
    payload={'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'source':str(HIST),'method':'Practical S/R v2: tight cluster radius, narrow actionable bands, min display gap between S/R levels, separate current zone.','items':items}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
