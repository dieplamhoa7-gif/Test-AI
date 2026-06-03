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
OUT=DATA/'lh1_moneyflow_ml_oos_research.json'
CSV=DATA/'lh1_moneyflow_ml_oos_research.csv'
spec=importlib.util.spec_from_file_location('ind40',IND40); ind40=importlib.util.module_from_spec(spec); spec.loader.exec_module(ind40)
SPLITS=[('2024','2023-01-01','2024-01-01','2025-01-01'),('2025','2023-01-01','2025-01-01','2026-01-01'),('2026_ytd','2023-01-01','2026-01-01','2026-06-01')]
GROUPS={
 'MONEYFLOW_CORE':['ad_slope20','chaikin_vol','cmf20','hist_vol20','klinger','klinger_signal_spread','lh1_volumeRatio','mf_cmf20','mf_green_vol_ratio10','mf_mfi14','mf_obv_rank60','mf_obv_slope10','mf_vol_ratio20','mf_vwap20_dist','mfi14','nvi_slope20','obv_pct_rank60','obv_slope20','pvi_slope20','volume','vosc_5_20','vwap20_dist','vwma20_dist','vwma50_dist'],
 'VWAP_VOLUME':['chaikin_vol','hist_vol20','lh1_volumeRatio','mf_green_vol_ratio10','mf_vol_ratio20','mf_vwap20_dist','volume','vosc_5_20','vwap20_dist','vwma20_dist','vwma50_dist'],
 'SMARTMONEY_PLUS_LH1':['ad_slope20','cmf20','klinger','klinger_signal_spread','lh1_bbPercent','lh1_macdHist','lh1_ret5','lh1_roc20','lh1_volumeRatio','mf_cmf20','mf_mfi14','mf_obv_rank60','mf_obv_slope10','mf_vwap20_dist','mfi14','nvi_slope20','obv_pct_rank60','obv_slope20','pvi_slope20','volume','vosc_5_20','vwap20_dist','vwma20_dist','vwma50_dist'],
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
    rows=[]
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
            t=tb[(sym,d)]
            feats={k:float(vv) for k,vv in r.items() if k not in ('date','time') and isinstance(vv,(int,float,np.integer,np.floating)) and np.isfinite(vv)}
            ai=t.get('entryIndicators') or {}
            for k in ['rsi','macdHist','bbPercent','volumeRatio','roc20','ret5']:
                feats['lh1_'+k]=f(ai.get(k))
            row=dict(t); row['features']=feats; row['label']=1 if f(t.get('netPnlPct'))>0 else 0; rows.append(row)
    rows.sort(key=lambda x:(x['signalDate'],x['symbol']))
    return rows

def tune_threshold(train_rows, probs, mode):
    y=np.array([r['label'] for r in train_rows]); pnl=np.array([f(r['netPnlPct']) for r in train_rows]); best=None
    for th in np.linspace(.2,.9,71):
        pred=probs>=th; n=int(pred.sum())
        if n<max(8,int(len(train_rows)*.10)): continue
        wr=float(y[pred].mean()*100); avg=float(pnl[pred].mean()); sm=float(pnl[pred].sum())
        if mode=='precision': score=wr*2.0+avg*14+min(n,60)*.08
        elif mode=='pnl': score=avg*32+wr*.9+min(sm,120)*.12
        else: score=wr*1.4+avg*24+min(n,80)*.10
        cand=(score,float(th),{'trainTrades':n,'trainWinRatePct':round(wr,2),'trainAvgNetPnlPct':round(avg,2),'trainSumNetPnlPct':round(sm,2)})
        if best is None or cand[0]>best[0]: best=cand
    return best

def eval_one(rows, group, model, mode):
    feats=GROUPS[group]
    selected=[]; splits=[]
    for split_name, tr_start, tr_end, te_end in SPLITS:
        tr=[r for r in rows if tr_start<=r['signalDate']<tr_end]
        te=[r for r in rows if tr_end<=r['signalDate']<te_end]
        if len(tr)<30 or not te or len(set(r['label'] for r in tr))<2: continue
        Xtr=np.array([[r['features'].get(k,0.0) for k in feats] for r in tr],float)
        Xte=np.array([[r['features'].get(k,0.0) for k in feats] for r in te],float)
        keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
        if len(keep)<3: continue
        feats2=[feats[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
        m=clf(model, abs(hash((group,model,mode,split_name)))%100000)
        m.fit(Xtr,np.array([r['label'] for r in tr]))
        tuned=tune_threshold(tr,m.predict_proba(Xtr)[:,1],mode)
        if tuned is None: continue
        _,th,train_stats=tuned
        probs=m.predict_proba(Xte)[:,1]
        picks=[]
        for r0,p in zip(te,probs):
            if p>=th:
                rr=dict(r0); rr['moneyflowProb']=round(float(p),4); rr['split']=split_name; picks.append(rr); selected.append(rr)
        splits.append({'split':split_name,'threshold':round(th,3),'trainStats':train_stats,'testStats':metrics(picks),'featureCount':len(feats2),'features':feats2})
    if not splits: return None
    overall=metrics(selected)
    return {'group':group,'model':model,'mode':mode,'overall':overall,'splits':splits,'selectedTradesSample':selected[:25]}

def main():
    rows=load_rows(); baseline=json.loads(TRADES.read_text(encoding='utf-8'))['windows']['all_2023_now']; runs=[]
    for g in GROUPS:
        for m in ['LOG','ET','RF']:
            for mode in ['balanced','precision','pnl']:
                r=eval_one(rows,g,m,mode)
                if r:
                    runs.append(r)
                    print(json.dumps({'group':g,'model':m,'mode':mode,'overall':r['overall']},ensure_ascii=False),flush=True)
    runs.sort(key=lambda x:(x['overall']['avgNetPnlPct'],x['overall']['winRatePct'],x['overall']['trades']), reverse=True)
    payload={'createdAt':pd.Timestamp.now().isoformat(),'method':'OOS moneyflow ML research for LH1 accepted signals. Train on past, test on future. Selected groups come from IS research only.','baseline':baseline,'topRuns':runs[:20]}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    with CSV.open('w',encoding='utf-8-sig') as f:
        f.write('rank,group,model,mode,trades,winRatePct,avgNetPnlPct,sumNetPnlPct\n')
        for i,r in enumerate(runs[:50],1):
            o=r['overall']; f.write(f"{i},{r['group']},{r['model']},{r['mode']},{o['trades']},{o['winRatePct']},{o['avgNetPnlPct']},{o['sumNetPnlPct']}\n")
    print(json.dumps({'out':str(OUT),'csv':str(CSV),'baseline':baseline,'best':runs[0] if runs else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
