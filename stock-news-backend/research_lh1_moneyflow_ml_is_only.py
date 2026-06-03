from __future__ import annotations
import json, importlib.util
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'
TRADES=DATA/'lh1_canonical_t3_fee_2023_to_now.json'
HIST=DATA/'vn100_history_from_2023.json'
IND40=ROOT/'build_indicator40_ml_outputs.py'
OUT=DATA/'lh1_moneyflow_ml_is_only_research.json'
CSV=DATA/'lh1_moneyflow_ml_is_only_research.csv'
spec=importlib.util.spec_from_file_location('ind40',IND40); ind40=importlib.util.module_from_spec(spec); spec.loader.exec_module(ind40)
GROUPS={
 'MONEYFLOW_CORE':['obv','cmf','mfi','vwap','vwma','ad_','adline','klinger','vosc','pvi','nvi','volume','vol'],
 'MONEYFLOW_PRICE':['obv','cmf','mfi','vwap','vwma','ad_','klinger','vosc','pvi','nvi','volume','roc','rsi','bb','atr'],
 'OBV_CMF_MFI':['obv','cmf','mfi'],
 'VWAP_VOLUME':['vwap','vwma','volume','vol','vosc'],
 'SMARTMONEY_PLUS_LH1':['obv','cmf','mfi','vwap','vwma','ad_','klinger','vosc','pvi','nvi','volume','lh1_volumeRatio','lh1_ret5','lh1_roc20','lh1_macdHist','lh1_bbPercent'],
}
def f(v,d=0.0):
    try:
        if v is None or pd.isna(v): return d
        if hasattr(v,'item'): v=v.item()
        return float(v)
    except Exception: return d

def metrics(rows):
    n=len(rows); wins=sum(1 for r in rows if f(r.get('netPnlPct'))>0); sm=sum(f(r.get('netPnlPct')) for r in rows)
    return {'trades':n,'wins':wins,'losses':n-wins,'winRatePct':round(wins/n*100,2) if n else 0,'avgNetPnlPct':round(sm/n,2) if n else 0,'sumNetPnlPct':round(sm,2)}

def clf(name,seed):
    if name=='ET': return ExtraTreesClassifier(n_estimators=320,max_depth=3,min_samples_leaf=5,class_weight='balanced',random_state=seed,n_jobs=1)
    if name=='RF': return RandomForestClassifier(n_estimators=320,max_depth=3,min_samples_leaf=5,class_weight='balanced',random_state=seed,n_jobs=1)
    return Pipeline([('s',StandardScaler()),('l',LogisticRegression(max_iter=1200,C=.35,class_weight='balanced',random_state=seed))])

def load_rows():
    trades=json.loads(TRADES.read_text(encoding='utf-8'))['trades']; hist=json.loads(HIST.read_text(encoding='utf-8'))['symbols']
    need=defaultdict(set); tb={}
    for t in trades:
        need[t['symbol']].add(t['signalDate']); tb[(t['symbol'],t['signalDate'])]=t
    rows=[]; all_feats=set()
    for sym,dates in need.items():
        raw=(hist.get(sym) or {}).get('rows') or []
        if not raw: continue
        df=pd.DataFrame(raw).sort_values('time').reset_index(drop=True)
        feat=ind40.add_indicator40(df).fillna(0)
        c=pd.to_numeric(df.close,errors='coerce'); h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); v=pd.to_numeric(df.volume,errors='coerce'); o=pd.to_numeric(df.open,errors='coerce')
        direction=c.diff().fillna(0).apply(lambda x:1 if x>0 else -1 if x<0 else 0)
        obv=(direction*v).fillna(0).cumsum(); feat['mf_obv_slope10']=obv-obv.shift(10); feat['mf_obv_rank60']=(obv-obv.rolling(60).min())/(obv.rolling(60).max()-obv.rolling(60).min()).replace(0,np.nan)*100
        mf_mult=((c-l)-(h-c))/(h-l).replace(0,np.nan); mf_vol=(mf_mult*v).astype(float); feat['mf_cmf20']=mf_vol.rolling(20).sum()/v.rolling(20).sum().replace(0,np.nan)
        tp=(h+l+c)/3; raw_mf=tp*v; pos=raw_mf.where(tp>tp.shift(1),0).rolling(14).sum(); neg=raw_mf.where(tp<tp.shift(1),0).rolling(14).sum(); feat['mf_mfi14']=100-100/(1+(pos/neg.replace(0,np.nan)))
        vwap=(tp*v).rolling(20).sum()/v.rolling(20).sum().replace(0,np.nan); feat['mf_vwap20_dist']=(c/vwap-1)*100
        feat['mf_vol_ratio20']=v/v.rolling(20).mean().replace(0,np.nan); feat['mf_green_vol_ratio10']=((c>o)*v).rolling(10).sum()/v.rolling(10).sum().replace(0,np.nan)
        feat=feat.fillna(0)
        for _,r in feat.iterrows():
            d=str(r.get('date') or r.get('time'))[:10]
            if d not in dates: continue
            t=tb[(sym,d)]; feats={k:float(vv) for k,vv in r.items() if k not in ('date','time') and isinstance(vv,(int,float,np.integer,np.floating)) and np.isfinite(vv)}
            ai=t.get('entryIndicators') or {}
            for k in ['rsi','macdHist','bbPercent','volumeRatio','roc20','ret5']:
                feats['lh1_'+k]=f(ai.get(k))
            all_feats.update(feats)
            row=dict(t); row['features']=feats; row['label']=1 if f(t.get('netPnlPct'))>0 else 0; rows.append(row)
    rows.sort(key=lambda x:(x['signalDate'],x['symbol']))
    return rows,sorted(all_feats)

def choose(all_feats,g):
    toks=GROUPS[g]
    return [x for x in all_feats if any(tok.lower() in x.lower() for tok in toks)]

def tune_is(rows,prob,mode):
    y=np.array([r['label'] for r in rows]); pnl=np.array([f(r['netPnlPct']) for r in rows]); best=None
    for th in np.linspace(.2,.9,71):
        pred=prob>=th; n=int(pred.sum())
        if n<max(10,int(len(rows)*.08)): continue
        wr=float(y[pred].mean()*100); avg=float(pnl[pred].mean()); sm=float(pnl[pred].sum())
        if mode=='precision': score=wr*2.0+avg*14+min(n,80)*.05
        elif mode=='pnl': score=avg*32+wr*.9+min(sm,120)*.12
        else: score=wr*1.4+avg*24+min(n,100)*.08
        cand=(score,float(th),{'trades':n,'winRatePct':round(wr,2),'avgNetPnlPct':round(avg,2),'sumNetPnlPct':round(sm,2)})
        if best is None or cand[0]>best[0]: best=cand
    return best

def eval_one(rows,all_feats,g,mn,mode):
    feats=choose(all_feats,g)
    X=np.array([[r['features'].get(k,0) for k in feats] for r in rows],float)
    keep=[i for i,s in enumerate(X.std(axis=0)) if s>1e-9]
    if len(keep)<3: return None
    feats=[feats[i] for i in keep]; X=X[:,keep]
    m=clf(mn,abs(hash((g,mn,mode)))%100000); y=np.array([r['label'] for r in rows]); m.fit(X,y)
    p=m.predict_proba(X)[:,1]; tuned=tune_is(rows,p,mode)
    if tuned is None: return None
    _,th,st=tuned; picked=[]
    for r0,pp in zip(rows,p):
        if pp>=th:
            rr=dict(r0); rr['moneyflowProb']=round(float(pp),4); picked.append(rr)
    return {'group':g,'model':mn,'mode':mode,'threshold':round(th,3),'overall':metrics(picked),'isStats':st,'featureCount':len(feats),'features':feats[:80],'selectedTradesSample':picked[:25]}

def main():
    rows,all_feats=load_rows(); baseline=json.loads(TRADES.read_text(encoding='utf-8'))['windows']['all_2023_now']; runs=[]
    for g in GROUPS:
        for mn in ['LOG','ET','RF']:
            for mode in ['balanced','precision','pnl']:
                r=eval_one(rows,all_feats,g,mn,mode)
                if r:
                    runs.append(r); print(json.dumps({'group':g,'model':mn,'mode':mode,'threshold':r['threshold'],'overall':r['overall']},ensure_ascii=False),flush=True)
    runs.sort(key=lambda x:(x['overall']['avgNetPnlPct'],x['overall']['winRatePct'],x['overall']['trades']),reverse=True)
    OUT.write_text(json.dumps({'createdAt':pd.Timestamp.now().isoformat(),'method':'IS-only moneyflow ML research for LH1 accepted signals. No OOS used. Label=canonical trade win. Features are point-in-time moneyflow/smart money and LH1 indicators only.','baseline':baseline,'rows':len(rows),'topRuns':runs[:30]},ensure_ascii=False,indent=2),encoding='utf-8')
    with CSV.open('w',encoding='utf-8-sig') as fcsv:
        fcsv.write('rank,group,model,mode,threshold,trades,winRatePct,avgNetPnlPct,sumNetPnlPct\n')
        for i,r in enumerate(runs[:50],1):
            o=r['overall']; fcsv.write(f"{i},{r['group']},{r['model']},{r['mode']},{r['threshold']},{o['trades']},{o['winRatePct']},{o['avgNetPnlPct']},{o['sumNetPnlPct']}\n")
    print(json.dumps({'out':str(OUT),'csv':str(CSV),'baseline':baseline,'best':runs[0] if runs else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
