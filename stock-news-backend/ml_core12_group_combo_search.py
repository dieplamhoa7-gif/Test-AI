from __future__ import annotations
import json, datetime as dt, itertools, warnings
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_fscore_support
warnings.filterwarnings('ignore')
HIST=Path('stock-news-backend/data/vn100_history_2025_06_2026_05_cache.json')
SRC=Path('stock-news-backend/data/d1a_full_research_features_is_oos.json')
SR=Path('stock-news-backend/data/sr_cluster_features_by_sector.json')
PARAM=Path('stock-news-backend/data/core12_param_optimizer_result.json')
CHK=Path('stock-news-backend/data/core12_group_combo_search_checkpoint.jsonl')
OUT=Path('stock-news-backend/data/core12_group_combo_search_result.json')
CFG=Path('stock-news-backend/data/core12_group_combo_config.json')
SPLITS=['2025-10-01','2026-01-01']
SECTORS={'BANK':['VCB','BID','CTG','TCB','VPB','MBB','ACB','STB','HDB','VIB','TPB','LPB','SHB','EIB','MSB','OCB','SSB'],'CHUNG_KHOAN':['SSI','VND','VCI','HCM','MBS','SHS','FTS','CTS','BSI','VIX'],'BDS':['VIC','VHM','VRE','NVL','PDR','DXG','KDH','NLG','DIG','CEO','BCG'],'RETAIL_CONSUMER':['MWG','FRT','PNJ','MSN','SAB','VNM','DGW'],'ENERGY_UTIL':['GAS','POW','PVD','PVS','PLX','BSR','NT2'],'INDUSTRIAL_LOGISTICS':['GMD','VSC','HAH','KBC','IDC','SZC','VGC'],'STEEL_MATERIAL':['HPG','HSG','NKG','VGC','GEX','DGC','DPM','DCM','BMP']}
def sg(sym,fb=None):
 for g,ss in SECTORS.items():
  if sym in ss: return g
 return fb or 'OTHER'
def ema(s,n): return s.ewm(span=max(2,int(round(n))),adjust=False).mean()
def rsi(c,n):
 n=max(2,int(round(n))); d=c.diff(); up=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean(); return 100-100/(1+up/(dn+1e-12))
def calc(df,indicator,params,sr=None):
 c=df.close.astype(float); h=df.high.astype(float); l=df.low.astype(float); v=df.volume.astype(float); out={}
 if indicator=='SR_CLUSTER': return {'SR_'+k:pd.Series([val]*len(df),index=df.index) for k,val in (sr or {}).items()}
 if indicator=='MA_EMA_WMA':
  n=int(round(params[0])); kind=int(round(params[1] if len(params)>1 else 0)); base=ema(c,n) if kind>=1 else c.rolling(n).mean(); tag=('EMA' if kind>=1 else 'MA')+str(n); out[tag+'_dist']=(c/base-1)*100; out[tag+'_slope5']=base.pct_change(5)*100
 elif indicator=='ADX_DMI':
  n=int(round(params[0])); up=h.diff(); dn=-l.diff(); plusDM=((up>dn)&(up>0))*up; minusDM=((dn>up)&(dn>0))*dn; tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.ewm(alpha=1/n,adjust=False).mean(); plus=100*plusDM.ewm(alpha=1/n,adjust=False).mean()/(atr+1e-12); minus=100*minusDM.ewm(alpha=1/n,adjust=False).mean()/(atr+1e-12); dx=100*(plus-minus).abs()/((plus+minus)+1e-12); out[f'ADX{n}']=dx.ewm(alpha=1/n,adjust=False).mean(); out[f'DI{n}_spread']=plus-minus
 elif indicator=='MACD':
  fast=int(round(params[0])); slow=max(fast+3,int(round(params[1]))); sig=int(round(params[2])); m=ema(c,fast)-ema(c,slow); hist=m-ema(m,sig); out[f'MACD{fast}_{slow}_{sig}_hist']=hist; out[f'MACD{fast}_{slow}_{sig}_slope5']=hist.diff(5)
 elif indicator=='SUPERTREND':
  n=int(round(params[0])); mul=float(params[1]); tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.rolling(n).mean(); mid=(h+l)/2; upper=mid+mul*atr; lower=mid-mul*atr; out[f'ST{n}_{mul:.1f}_dist']=np.where(c>=mid,(c-lower)/(c+1e-12),(c-upper)/(c+1e-12))*100; out[f'ST{n}_{mul:.1f}_dir']=(c>=mid).astype(float)
 elif indicator=='TRIX':
  n=int(round(params[0])); t=ema(ema(ema(c,n),n),n).pct_change()*100; out[f'TRIX{n}']=t; out[f'TRIX{n}_slope5']=t.diff(5)
 elif indicator=='ICHIMOKU':
  ten=int(round(params[0])); kij=max(ten+3,int(round(params[1]))); span=max(kij+5,int(round(params[2]))); tenv=(h.rolling(ten).max()+l.rolling(ten).min())/2; kijv=(h.rolling(kij).max()+l.rolling(kij).min())/2; spanA=(tenv+kijv)/2; spanB=(h.rolling(span).max()+l.rolling(span).min())/2; out[f'ICHI{ten}_{kij}_{span}_cloud_pos']=(c-np.maximum(spanA,spanB))/(c+1e-12)*100; out[f'ICHI{ten}_{kij}_{span}_tk']=(tenv-kijv)/(c+1e-12)*100
 elif indicator=='VWAP_VWMA':
  n=int(round(params[0])); vw=(c*v).rolling(n).sum()/(v.rolling(n).sum()+1e-12); out[f'VWAP{n}_dist']=(c/vw-1)*100; out[f'VWMA{n}_slope5']=vw.pct_change(5)*100
 elif indicator=='PVI_NVI':
  n=int(round(params[0])); pvi=pd.Series(index=df.index,dtype=float); nvi=pd.Series(index=df.index,dtype=float); pvi.iloc[0]=1000; nvi.iloc[0]=1000; ret=c.pct_change().fillna(0)
  for i in range(1,len(df)):
   pvi.iloc[i]=pvi.iloc[i-1]*(1+ret.iloc[i]) if v.iloc[i]>v.iloc[i-1] else pvi.iloc[i-1]; nvi.iloc[i]=nvi.iloc[i-1]*(1+ret.iloc[i]) if v.iloc[i]<v.iloc[i-1] else nvi.iloc[i-1]
  out[f'PVI_slope{n}']=pvi.pct_change(n)*100; out[f'NVI_slope{n}']=nvi.pct_change(n)*100
 elif indicator=='ROC_MOMENTUM':
  n=int(round(params[0])); out[f'ROC{n}']=c.pct_change(n)*100; out[f'MOM{n}']=c.diff(n)/(c.shift(n)+1e-12)*100
 elif indicator=='RSI':
  n=int(round(params[0])); rr=rsi(c,n); out[f'RSI{n}']=rr; out[f'RSI{n}_slope5']=rr.diff(5)
 elif indicator=='MFI_CMF':
  n=int(round(params[0])); mode=int(round(params[1] if len(params)>1 else 0)); tp=(h+l+c)/3; raw=tp*v; mfm=((c-l)-(h-c))/((h-l).replace(0,np.nan)); mfv=mfm*v
  if mode==0:
   pos=raw.where(tp.diff()>0,0).rolling(n).sum(); neg=raw.where(tp.diff()<0,0).rolling(n).sum(); out[f'MFI{n}']=100-100/(1+pos/(neg+1e-12))
  else: out[f'CMF{n}']=mfv.rolling(n).sum()/(v.rolling(n).sum()+1e-12)
 return {k:pd.Series(v).replace([np.inf,-np.inf],np.nan).fillna(0) for k,v in out.items()}
def label(task,s):
 lc=s['lc']; rs=s['rs']; f=s['fullResearchFeatures']; mtf=s.get('mtfAsOfDate') or {}
 if task=='RS': return int((rs.get('nearSupport') or abs(rs.get('distSupportPct') or 99)<4) and (lc.get('futureMin20') or 0)>-7 and (lc.get('futureMax20') or 0)>5)
 if task=='D1A': return int((lc.get('futureMin20') or 0)>-8 and (lc.get('futureClose20') or 0)>-5 and (f.get('dryUp20_norm',0)>0 or f.get('greenAbsorb10_norm',0)>0 or f.get('baseQualityScore_norm',0)>0 or rs.get('nearSupport')))
 bad=(lc.get('futureMin20') or 0)<-10 or ((lc.get('futureClose20') or 0)<-6 and (lc.get('futureMin20') or 0)<-7); struct=rs.get('supportBroken') or rs.get('weekSupportBroken') or f.get('support_break',0)>0 or f.get('break_ma_cluster',0)>0; distro=f.get('distribution_cluster',0)>0 or (f.get('two_red_high_vol_5d',0)>0 and f.get('close_low_cluster',0)>0); mtfb=((mtf.get('W_rsi14') or 50)<42 and not mtf.get('W_macdImproving')) or (not mtf.get('W_aboveMa20') and not mtf.get('W_maTrendUp')); return int(bad and (struct or distro or mtfb))
def met(y,p):
 pr,rc,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0); return {'precision':round(pr*100,2),'recall':round(rc*100,2),'f1':round(f1*100,2),'predN':int((p==1).sum()),'tp':int(((p==1)&(y==1)).sum()),'fp':int(((p==1)&(y==0)).sum()),'oracleN':int((y==1).sum()),'n':len(y)}
def model(name):
 if name=='ET': return ExtraTreesClassifier(n_estimators=220,max_depth=4,min_samples_leaf=5,class_weight='balanced',random_state=21,n_jobs=1)
 if name=='RF': return RandomForestClassifier(n_estimators=220,max_depth=4,min_samples_leaf=6,class_weight='balanced',random_state=22,n_jobs=1)
 if name=='HGB': return HistGradientBoostingClassifier(max_iter=120,learning_rate=.04,max_leaf_nodes=8,l2_regularization=.5,random_state=23)
 return Pipeline([('s',StandardScaler()),('l',LogisticRegression(max_iter=800,C=.35,class_weight='balanced',random_state=24))])
def tune(y,prob,mode):
 best=(-1,.5,None)
 for th in np.linspace(.1,.95,86):
  st=met(y,(prob>=th).astype(int))
  if st['predN']<max(2,int(len(y)*.006)): continue
  obj=st['precision']*3+st['f1']*.7+min(st['predN'],18)*.55 if mode=='precision' else st['precision']*2+st['recall']*1.2+st['f1']*1.5+min(st['predN'],30)*.35
  if obj>best[0]: best=(obj,float(th),st)
 return best
def eval_combo(rows,task,features,mn,mode):
 res=[]
 for sp in SPLITS:
  tr=[r for r in rows if r['date']<sp]; te=[r for r in rows if r['date']>=sp]
  ytr=np.array([label(task,r['src']) for r in tr]); yte=np.array([label(task,r['src']) for r in te])
  if len(set(ytr))<2 or yte.sum()<2: return None
  Xtr=np.array([[r['features'].get(f,0) for f in features] for r in tr],float); Xte=np.array([[r['features'].get(f,0) for f in features] for r in te],float)
  keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
  if len(keep)<3: return None
  f2=[features[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
  m=model(mn)
  try: m.fit(Xtr,ytr); ptr=m.predict_proba(Xtr)[:,1]; pte=m.predict_proba(Xte)[:,1]
  except Exception as e: return None
  _,th,isst=tune(ytr,ptr,mode); oos=met(yte,(pte>=th).astype(int)); imp={}
  if hasattr(m,'feature_importances_'): imp={k:round(float(v),5) for k,v in sorted(zip(f2,m.feature_importances_),key=lambda kv:kv[1],reverse=True)[:20]}
  res.append({'split':sp,'threshold':round(th,3),'isStats':isst,'oosStats':oos,'topFeatures':imp})
 avgP=sum(x['oosStats']['precision'] for x in res)/2; minP=min(x['oosStats']['precision'] for x in res); avgR=sum(x['oosStats']['recall'] for x in res)/2; avgF=sum(x['oosStats']['f1'] for x in res)/2; minF=min(x['oosStats']['f1'] for x in res); pred=sum(x['oosStats']['predN'] for x in res)
 hit70_50=avgP>=70 and minP>=50 and avgR>=50
 return {'avgPrecision':round(avgP,2),'minPrecision':round(minP,2),'avgRecall':round(avgR,2),'avgF1':round(avgF,2),'minF1':round(minF,2),'predTotal':pred,'hit70_50':hit70_50,'score':round(avgP*3+minP*1.5+avgR*.6+avgF*.8+min(pred,40)*.4+(40 if hit70_50 else 0),3),'splits':res}
def select_candidates():
 j=json.load(open(PARAM,encoding='utf-8'))['topBySectorTask']; out={}
 for s,tasks in j.items():
  for t,arr in tasks.items():
   # sorted already by precision; keep diverse top one per indicator then force at least 5, max 8
   chosen=[]; seen=set()
   for r in arr:
    if r['indicator'] in seen: continue
    if r['predTotal']>=2 and (r['avgPrecision']>=50 or r['avgRecall']>=45 or r['avgF1']>=40):
     chosen.append(r); seen.add(r['indicator'])
    if len(chosen)>=8: break
   # always include SR for RS/D1A if present
   sr=[r for r in arr if r['indicator']=='SR_CLUSTER']
   if sr and t in ['RS','D1A'] and 'SR_CLUSTER' not in seen: chosen.append(sr[0])
   out[(s,t)]=chosen[:8]
 return out
def main():
 hist=json.load(open(HIST,encoding='utf-8'))['symbols']; src=json.load(open(SRC,encoding='utf-8'))['items']; srcmap={(x['symbol'],x['date']):x for x in src}; srmap={(x['symbol'],x['date']):x['features'] for x in json.load(open(SR,encoding='utf-8'))['items']}
 raw={sym:pd.DataFrame(p['rows']).sort_values('time').reset_index(drop=True) for sym,p in hist.items() if any(k[0]==sym for k in srcmap)}
 base=[]
 for sym,df in raw.items():
  for i,r in df.iterrows():
   key=(sym,str(r['time']))
   if key in srcmap: base.append({'symbol':sym,'date':key[1],'sectorGroup':sg(sym,srcmap[key].get('sector')),'idx':i,'src':srcmap[key]})
 cand=select_candidates(); done=set(); runs=[]
 if CHK.exists():
  for line in CHK.read_text(encoding='utf-8').splitlines():
   if line.strip():
    r=json.loads(line); done.add((r['sectorGroup'],r['task'],tuple(r['indicators']),r['model'],r['mode'])); runs.append(r)
 with CHK.open('a',encoding='utf-8') as out:
  for (sector,task),inds in cand.items():
   if len(inds)<5: continue
   rows0=base if sector=='ALL' else [r for r in base if r['sectorGroup']==sector]
   # build feature frames for all chosen indicators
   feat_by_sym={sym:{} for sym in raw}
   for rec in inds:
    ind=rec['indicator']; params=rec.get('params') or {}
    for sym,df in raw.items():
     if ind=='SR_CLUSTER': continue
     feat_by_sym[sym].update(calc(df,ind,params))
   rows=[]
   for r in rows0:
    feats={k:float(v.iloc[r['idx']]) for k,v in feat_by_sym[r['symbol']].items()}
    # merge sr actual available distance/strength features if chosen
    if any(x['indicator']=='SR_CLUSTER' for x in inds): feats.update({'SR_'+k:v for k,v in srmap.get((r['symbol'],r['date']),{}).items()})
    rows.append({**r,'features':feats})
   all_feats=sorted({k for r in rows for k in r['features']})
   combos=[]
   base_names=[r['indicator'] for r in inds]
   # 5 indicator mandatory combo + all chosen + selected 6/7 combos if enough
   for k in range(5,min(8,len(inds))+1):
    for comb in itertools.combinations(inds,k): combos.append(list(comb))
   for comb in combos:
    names=[r['indicator'] for r in comb]
    feat_prefix=[]
    for nm in names:
     if nm=='SR_CLUSTER': feat_prefix.append('SR_')
     elif nm=='MA_EMA_WMA': feat_prefix += ['MA','EMA']
     elif nm=='ADX_DMI': feat_prefix += ['ADX','DI']
     elif nm=='ROC_MOMENTUM': feat_prefix += ['ROC','MOM']
     else: feat_prefix.append(nm.split('_')[0] if '_' in nm else nm)
    feats=[f for f in all_feats if any(f.startswith(p) for p in feat_prefix)]
    if len(feats)<5: continue
    for mn in ['LOG','ET','RF','HGB']:
     for mode in ['precision','balanced70_50']:
      key=(sector,task,tuple(names),mn,mode)
      if key in done: continue
      rr=eval_combo(rows,task,feats,mn,mode)
      if rr:
       pos=sum(label(task,r['src']) for r in rows); rec={'sectorGroup':sector,'sampleCount':len(rows),'task':task,'positiveN':pos,'positiveRate':round(pos/len(rows)*100,2),'indicators':names,'indicatorParams':{x['indicator']:x.get('params') for x in comb},'model':mn,'mode':mode,'featureCount':len(feats),**rr}
       out.write(json.dumps(rec,ensure_ascii=False)+'\n'); out.flush(); runs.append(rec)
       print(json.dumps({'done':len(runs),'latest':{k:rec[k] for k in ['sectorGroup','task','indicators','model','mode','avgPrecision','minPrecision','avgRecall','avgF1','hit70_50']}},ensure_ascii=False),flush=True)
      if len(runs)%20==0: finalize(runs)
 finalize(runs); print(json.dumps({'out':str(OUT),'config':str(CFG),'runs':len(runs)},ensure_ascii=False))
def finalize(runs):
 good=[r for r in runs if not r.get('error')]
 by={}
 for r in sorted(good,key=lambda x:(x['hit70_50'],x['avgPrecision'],x['minPrecision'],x['avgRecall'],x['score']),reverse=True): by.setdefault(r['sectorGroup'],{}).setdefault(r['task'],[]).append(r)
 OUT.write_text(json.dumps({'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'method':'Core12 group-combination search, minimum 5 indicators, IS threshold and OOS evaluation on two splits. Modes: precision and balanced70_50.','runs':len(good),'topBySectorTask':{s:{t:a[:30] for t,a in tasks.items()} for s,tasks in by.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
 CFG.write_text(json.dumps({'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'selected':{s:{t:a[0] for t,a in tasks.items()} for s,tasks in by.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
