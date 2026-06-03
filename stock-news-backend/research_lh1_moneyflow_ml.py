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
OUT=DATA/'lh1_moneyflow_ml_research.json'
CSV=DATA/'lh1_moneyflow_ml_research.csv'
spec=importlib.util.spec_from_file_location('ind40',IND40); ind40=importlib.util.module_from_spec(spec); spec.loader.exec_module(ind40)
SPLITS=[('2024','2023-01-01','2024-01-01','2025-01-01'),('2025','2023-01-01','2025-01-01','2026-01-01'),('2026_ytd','2023-01-01','2026-01-01','2026-06-01')]
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
  # add extra money flow features from raw OHLCV, point-in-time
  c=pd.to_numeric(df.close,errors='coerce'); h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); v=pd.to_numeric(df.volume,errors='coerce')
  direction=c.diff().fillna(0).apply(lambda x:1 if x>0 else -1 if x<0 else 0)
  obv=(direction*v).fillna(0).cumsum(); feat['mf_obv_slope10']=obv-obv.shift(10); feat['mf_obv_rank60']=(obv-obv.rolling(60).min())/(obv.rolling(60).max()-obv.rolling(60).min()).replace(0,pd.NA)*100
  mf_mult=((c-l)-(h-c))/(h-l).replace(0,pd.NA); mf_vol=mf_mult*v; feat['mf_cmf20']=mf_vol.rolling(20).sum()/v.rolling(20).sum().replace(0,pd.NA)
  tp=(h+l+c)/3; raw_mf=tp*v; pos=raw_mf.where(tp>tp.shift(1),0).rolling(14).sum(); neg=raw_mf.where(tp<tp.shift(1),0).rolling(14).sum(); feat['mf_mfi14']=100-100/(1+(pos/neg.replace(0,pd.NA)))
  vwap=(tp*v).rolling(20).sum()/v.rolling(20).sum().replace(0,pd.NA); feat['mf_vwap20_dist']=(c/vwap-1)*100
  feat['mf_vol_ratio20']=v/v.rolling(20).mean(); feat['mf_green_vol_ratio10']=((c>df.open)*v).rolling(10).sum()/v.rolling(10).sum().replace(0,pd.NA)
  feat=feat.fillna(0)
  for _,r in feat.iterrows():
   d=str(r.get('date') or r.get('time'))[:10]
   if d not in dates: continue
   t=tb[(sym,d)]; feats={k:float(vv) for k,vv in r.items() if k not in ('date','time') and isinstance(vv,(int,float,np.integer,np.floating)) and np.isfinite(vv)}
   ai=t.get('entryIndicators') or {}
   for k in ['rsi','macdHist','bbPercent','volumeRatio','roc20','ret5']:
    feats['lh1_'+k]=f(ai.get(k))
   all_feats.update(feats); row=dict(t); row['features']=feats; row['label']=1 if f(t.get('netPnlPct'))>0 else 0; rows.append(row)
 rows.sort(key=lambda x:(x['signalDate'],x['symbol'])); return rows,sorted(all_feats)
def choose(all_feats,g):
 toks=GROUPS[g]
 return [x for x in all_feats if any(tok.lower() in x.lower() for tok in toks)]
def tune(train,prob,mode):
 best=None; y=np.array([r['label'] for r in train]); pnl=np.array([f(r['netPnlPct']) for r in train])
 for th in np.linspace(.2,.9,71):
  pred=prob>=th; n=int(pred.sum())
  if n<max(8,int(len(train)*.10)): continue
  wr=float(y[pred].mean()*100); avg=float(pnl[pred].mean()); sm=float(pnl[pred].sum())
  score=wr*1.5+avg*26+min(n,60)*.12 if mode=='balanced' else wr*2.2+avg*12+min(n,50)*.1 if mode=='precision' else avg*34+wr*.8+min(sm,80)*.15
  cand=(score,float(th),{'trainTrades':n,'trainWinRatePct':round(wr,2),'trainAvgNetPnlPct':round(avg,2),'trainSumNetPnlPct':round(sm,2)})
  if best is None or cand[0]>best[0]: best=cand
 return best
def eval_one(rows,all_feats,g,mn,mode):
 feats=choose(all_feats,g); selected=[]; splits=[]
 for sp,ta,tb,tc in SPLITS:
  tr=[r for r in rows if ta<=r['signalDate']<tb]; te=[r for r in rows if tb<=r['signalDate']<tc]
  if len(tr)<30 or not te or len(set(r['label'] for r in tr))<2: continue
  Xtr=np.array([[r['features'].get(k,0) for k in feats] for r in tr],float); Xte=np.array([[r['features'].get(k,0) for k in feats] for r in te],float)
  keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
  if len(keep)<3: continue
  f2=[feats[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
  m=clf(mn,abs(hash((g,mn,mode,sp)))%100000); m.fit(Xtr,np.array([r['label'] for r in tr])); tuned=tune(tr,m.predict_proba(Xtr)[:,1],mode)
  if tuned is None: continue
  _,th,tst=tuned; pte=m.predict_proba(Xte)[:,1]; pick=[]
  for r0,p in zip(te,pte):
   if p>=th:
    rr=dict(r0); rr['moneyflowProb']=round(float(p),4); rr['split']=sp; pick.append(rr); selected.append(rr)
  splits.append({'split':sp,'threshold':round(th,3),'trainStats':tst,'testStats':metrics(pick),'featureCount':len(f2),'features':f2[:60]})
 if not splits: return None
 overall=metrics(selected); score=overall['winRatePct']*1.5+overall['avgNetPnlPct']*30+min(overall['trades'],80)*.15+overall['sumNetPnlPct']*.08
 return {'group':g,'model':mn,'mode':mode,'score':round(score,3),'overall':overall,'splits':splits,'selectedTradesSample':selected[:20]}
def main():
 rows,all_feats=load_rows(); baseline=json.loads(TRADES.read_text(encoding='utf-8'))['windows']['all_2023_now']; runs=[]
 for g in GROUPS:
  for mn in ['LOG','ET','RF']:
   for mode in ['balanced','precision','pnl']:
    r=eval_one(rows,all_feats,g,mn,mode)
    if r:
     runs.append(r); print(json.dumps({'group':g,'model':mn,'mode':mode,'overall':r['overall'],'score':r['score']},ensure_ascii=False),flush=True)
 runs.sort(key=lambda x:(x['overall']['avgNetPnlPct'],x['overall']['winRatePct'],x['overall']['trades']),reverse=True)
 OUT.write_text(json.dumps({'createdAt':pd.Timestamp.now().isoformat(),'method':'Moneyflow ML research for LH1 accepted signals. Label=canonical trade win. Features: indicator40 moneyflow + engineered OBV/CMF/MFI/VWAP/volume features, point-in-time only. Walk-forward train past/test future.','baseline':baseline,'rows':len(rows),'topRuns':runs[:30]},ensure_ascii=False,indent=2),encoding='utf-8')
 with CSV.open('w',encoding='utf-8-sig') as fcsv:
  fcsv.write('rank,group,model,mode,trades,winRatePct,avgNetPnlPct,sumNetPnlPct,score\n')
  for i,r in enumerate(runs[:50],1):
   o=r['overall']; fcsv.write(f"{i},{r['group']},{r['model']},{r['mode']},{o['trades']},{o['winRatePct']},{o['avgNetPnlPct']},{o['sumNetPnlPct']},{r['score']}\n")
 print(json.dumps({'out':str(OUT),'csv':str(CSV),'baseline':baseline,'best':runs[0] if runs else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
