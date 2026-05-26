from __future__ import annotations
import json, csv, datetime as dt, itertools, importlib.util, warnings
from pathlib import Path
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'
STEP2=DATA/'core12_step2_tune_params_for12_precision_first_rs_d1a_d1s.json'
OUT=DATA/'core12_step3_combo_5to8_from_step2_precision_first_rs_d1a_d1s_fast.json'
CSV=DATA/'core12_step3_combo_5to8_from_step2_precision_first_rs_d1a_d1s_fast.csv'
SPLITS=['2025-10-01','2026-01-01']; MIN_PRED={'RS':10,'D1A':10,'D1S':5}; MIN_RECALL={'RS':2.0,'D1A':2.0,'D1S':2.0}
spec=importlib.util.spec_from_file_location('step2',ROOT/'step2_tune_params_for12_precision_first_rs_d1a_d1s.py'); step2=importlib.util.module_from_spec(spec); spec.loader.exec_module(step2)
def stats(y,p):
 pr,rc,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0); return {'n':int(len(y)),'tp':int(((p==1)&(y==1)).sum()),'fp':int(((p==1)&(y==0)).sum()),'tn':int(((p==0)&(y==0)).sum()),'fn':int(((p==0)&(y==1)).sum()),'precision':round(pr*100,2),'recall':round(rc*100,2),'accuracy':round(accuracy_score(y,p)*100,2),'f1':round(f1*100,2),'predN':int((p==1).sum()),'oracleN':int((y==1).sum())}
def tune(y,prob,task):
 cand=[]
 for th in np.linspace(.10,.99,60):
  st=stats(y,(prob>=th).astype(int))
  if st['predN']<max(MIN_PRED[task],int(len(y)*.003)) or st['recall']<MIN_RECALL[task]: continue
  cand.append((st['precision'],st['recall'],st['predN'],st['f1'],float(th),st))
 if not cand: return None
 cand.sort(key=lambda x:(x[0],x[1],x[2],x[3]),reverse=True); return cand[0]
def eval_combo(rows,task,combo,model):
 features=sorted({f for r in combo for f in r['features']}); splits=[]
 for sp in SPLITS:
  tr=[r for r in rows if r['date']<sp]; te=[r for r in rows if r['date']>=sp]
  ytr=np.array([step2.label(task,r) for r in tr]); yte=np.array([step2.label(task,r) for r in te])
  if len(set(ytr))<2 or yte.sum()<2: return None
  Xtr=np.array([[r['features40'].get(f,0.0) for f in features] for r in tr],float); Xte=np.array([[r['features40'].get(f,0.0) for f in features] for r in te],float)
  keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
  if len(keep)<5: return None
  f2=[features[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
  m=step2.clf(model,abs(hash((task,tuple(x['family']+'|'+x['setName'] for x in combo),model,sp)))%100000)
  try:
   m.fit(Xtr,ytr); tuned=tune(ytr,m.predict_proba(Xtr)[:,1],task)
   if tuned is None: return None
   _,_,_,_,th,isst=tuned; oos=stats(yte,(m.predict_proba(Xte)[:,1]>=th).astype(int))
  except Exception: return None
  splits.append({'split':sp,'threshold':round(th,3),'isStats':isst,'oosStats':oos,'featureCount':len(f2)})
 avgP=float(np.mean([s['oosStats']['precision'] for s in splits])); avgR=float(np.mean([s['oosStats']['recall'] for s in splits])); minP=min(s['oosStats']['precision'] for s in splits); avgF=float(np.mean([s['oosStats']['f1'] for s in splits])); pred=sum(s['oosStats']['predN'] for s in splits); pass70=avgP>=70 and minP>=50 and pred>=MIN_PRED[task]
 return {'task':task,'groupSize':len(combo),'families':[r['family'] for r in combo],'setNames':[r['setName'] for r in combo],'model':model,'featureCount':len(features),'avgPrecision':round(avgP,2),'avgRecall':round(avgR,2),'minPrecision':round(minP,2),'avgF1':round(avgF,2),'totalPredN':int(pred),'passP70':pass70,'score':round(avgP*10+avgR*.7+minP*3+min(pred,80)*.05+avgF*.2,3),'splits':splits}
def main():
 rows=step2.load_rows(); s2=json.load(open(STEP2,encoding='utf-8'))['selectedByTask']; runs=[]
 for task,arr in s2.items():
  # keep only best variant per family, ranked by Step2 precision-first; this avoids duplicated SMA/MOMENTUM combos and finishes fast.
  pool=[]; seen=set()
  for r in arr:
   if r['family'] not in seen:
    pool.append(r); seen.add(r['family'])
   if len(pool)>=8: break
  combos=[]
  for k in range(5,min(8,len(pool))+1): combos += list(itertools.combinations(pool,k))
  for combo in combos:
   best=None
   for mn in ['ET','RF','LOG']:
    rr=eval_combo(rows,task,combo,mn)
    if rr and (best is None or (rr['avgPrecision'],rr['avgRecall'],rr['minPrecision'],rr['totalPredN'])>(best['avgPrecision'],best['avgRecall'],best['minPrecision'],best['totalPredN'])): best=rr
   if best:
    runs.append(best); print(json.dumps({k:best[k] for k in ['task','groupSize','families','model','avgPrecision','avgRecall','minPrecision','totalPredN','passP70']},ensure_ascii=False),flush=True)
 selected={}
 for task in ['RS','D1A','D1S']:
  arr=[r for r in runs if r['task']==task]; arr.sort(key=lambda x:(x['avgPrecision'],x['avgRecall'],x['minPrecision'],x['totalPredN'],x['avgF1']),reverse=True); selected[task]=arr[:20]
 OUT.write_text(json.dumps({'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'method':'FAST STEP3: combine best Step2 variant per family into groups of 5-8 families. Rank precision first, recall second.','sourceStep2':str(STEP2),'selectedByTask':selected,'allRuns':runs},ensure_ascii=False,indent=2),encoding='utf-8')
 with CSV.open('w',encoding='utf-8-sig',newline='') as f:
  fields=['task','rank','groupSize','families','setNames','model','featureCount','avgPrecision','avgRecall','minPrecision','avgF1','totalPredN','passP70','score']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for task,arr in selected.items():
   for i,r in enumerate(arr,1):
    row={k:(json.dumps(r[k],ensure_ascii=False) if k in ['families','setNames'] else r.get(k)) for k in fields}; row['rank']=i; w.writerow(row)
 print(json.dumps({'out':str(OUT),'csv':str(CSV),'runs':len(runs),'selected':{t:[{k:r[k] for k in ['groupSize','families','model','avgPrecision','avgRecall','minPrecision','totalPredN','passP70']} for r in a[:5]] for t,a in selected.items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
