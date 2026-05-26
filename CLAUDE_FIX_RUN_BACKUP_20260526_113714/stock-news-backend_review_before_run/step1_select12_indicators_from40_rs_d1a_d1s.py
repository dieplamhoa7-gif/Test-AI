from __future__ import annotations
import json, csv, datetime as dt, importlib.util, warnings
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'
HIST=DATA/'vn100_history_2025_06_2026_05_cache.json'
D1SRC=DATA/'d1a_full_research_features_is_oos.json'
IND40=ROOT/'build_indicator40_ml_outputs.py'
OUT=DATA/'core12_step1_select12_from40_rs_d1a_d1s.json'
CSV=DATA/'core12_step1_select12_from40_rs_d1a_d1s.csv'
SPLITS=['2025-10-01','2026-01-01']
INDICATOR_MAP={
 'SMA':['sma'], 'EMA':['ema'], 'WMA':['wma'], 'MACD':['macd'], 'ICHIMOKU':['ichi'], 'ADX':['adx'], 'PSAR':['psar'], 'SUPERTREND':['supertrend'], 'DMI':['plusDI','minusDI','diSpread'], 'AROON':['aroon'], 'ZIGZAG':['zigzag'], 'TRIX':['trix'],
 'RSI':['rsi'], 'STOCHASTIC':['stoch'], 'CCI':['cci'], 'WILLIAMS_R':['williams'], 'MOMENTUM':['mom'], 'ROC':['roc'], 'AO':['ao'], 'ULTIMATE_OSC':['ultimate'], 'TSI':['tsi'], 'KDJ':['kdj'],
 'BOLLINGER':['bb'], 'ATR':['atr'], 'KELTNER':['keltner'], 'DONCHIAN':['donchian'], 'STDDEV':['std'], 'HIST_VOL':['hist_vol'], 'CHOPPINESS':['choppiness'], 'CHAIKIN_VOL':['chaikin_vol'], 'RVI':['rvi'], 'MASS_INDEX':['mass_index'],
 'VWAP':['vwap'], 'OBV':['obv'], 'CMF':['cmf'], 'AD_LINE':['ad_slope'], 'MFI':['mfi'], 'VWMA':['vwma'], 'PVI':['pvi'], 'NVI':['nvi'], 'VOSC':['vosc'], 'KLINGER':['klinger']
}
spec=importlib.util.spec_from_file_location('ind40',IND40); ind40=importlib.util.module_from_spec(spec); spec.loader.exec_module(ind40)
def load_rows():
    hist=json.load(open(HIST,encoding='utf-8'))['symbols']
    src=json.load(open(D1SRC,encoding='utf-8'))['items']
    need={(x['symbol'],x['date']) for x in src}; smap={(x['symbol'],x['date']):x for x in src}
    rows=[]
    for sym,p in hist.items():
        if not any(s==sym for s,_ in need): continue
        df=pd.DataFrame(p['rows']).sort_values('time').reset_index(drop=True)
        feat=ind40.add_indicator40(df).fillna(0)
        for _,r in feat.iterrows():
            key=(sym,str(r['date']))
            if key not in smap: continue
            base=smap[key]
            feats={k:float(v) for k,v in r.items() if k!='date' and isinstance(v,(int,float,np.integer,np.floating)) and np.isfinite(v)}
            rows.append({'symbol':sym,'date':key[1],'sector':base.get('sector'),'features40':feats,'rs':base.get('rs') or {},'lc':base.get('lc') or {},'full':base.get('fullResearchFeatures') or {},'mtf':base.get('mtfAsOfDate') or {}})
    rows.sort(key=lambda x:(x['date'],x['symbol']))
    return rows
def label(task,r):
    lc,rs,f,mtf=r['lc'],r['rs'],r['full'],r['mtf']
    if task=='RS':
        near=bool(rs.get('nearSupport') or abs(rs.get('distSupportPct') or 99)<4)
        survive=(lc.get('futureMin20') or 0)>-7
        rebound=(lc.get('futureMax20') or 0)>5
        return int(near and survive and rebound)
    if task=='D1A':
        future_survive=(lc.get('futureMin20') or 0)>-8 and (lc.get('futureClose20') or 0)>-5
        absorption=(f.get('dryUp20_norm',0)>0 or f.get('greenAbsorb10_norm',0)>0 or f.get('baseQualityScore_norm',0)>0)
        base_ok=(f.get('range40Pct_inv',0)>0 or f.get('tightClose20_norm',0)>0 or rs.get('nearSupport'))
        return int(future_survive and (absorption or base_ok))
    if task=='D1S':
        future_bad=(lc.get('futureMin20') or 0)<-10 or ((lc.get('futureClose20') or 0)<-6 and (lc.get('futureMin20') or 0)<-7)
        structural=rs.get('supportBroken') or rs.get('weekSupportBroken') or f.get('support_break',0)>0 or f.get('break_ma_cluster',0)>0
        distro=f.get('distribution_cluster',0)>0 or (f.get('two_red_high_vol_5d',0)>0 and f.get('close_low_cluster',0)>0)
        mtf_bad=((mtf.get('W_rsi14') or 50)<42 and not mtf.get('W_macdImproving')) or (not mtf.get('W_aboveMa20') and not mtf.get('W_maTrendUp'))
        return int(future_bad and (structural or distro or mtf_bad))
    raise ValueError(task)
def stats(y,p):
    pr,rc,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0)
    return {'n':int(len(y)),'tp':int(((p==1)&(y==1)).sum()),'fp':int(((p==1)&(y==0)).sum()),'tn':int(((p==0)&(y==0)).sum()),'fn':int(((p==0)&(y==1)).sum()),'precision':round(pr*100,2),'recall':round(rc*100,2),'accuracy':round(accuracy_score(y,p)*100,2),'f1':round(f1*100,2),'predN':int((p==1).sum()),'oracleN':int((y==1).sum())}
def clf(name,seed):
    if name=='ET': return ExtraTreesClassifier(n_estimators=260,max_depth=4,min_samples_leaf=6,class_weight='balanced',random_state=seed,n_jobs=1)
    if name=='RF': return RandomForestClassifier(n_estimators=260,max_depth=4,min_samples_leaf=8,class_weight='balanced',random_state=seed,n_jobs=1)
    return Pipeline([('s',StandardScaler()),('l',LogisticRegression(max_iter=1000,C=.3,class_weight='balanced',random_state=seed))])
def tune(y,prob):
    best=(-1,.5,None)
    for th in np.linspace(.1,.9,81):
        st=stats(y,(prob>=th).astype(int))
        if st['predN']<max(3,int(len(y)*.01)): continue
        score=st['f1']+1.15*st['precision']+0.45*st['recall']
        if score>best[0]: best=(score,float(th),st)
    return best
def eval_one(rows,task,indicator,model):
    prefs=INDICATOR_MAP[indicator]
    feats=sorted([f for f in {k for r in rows for k in r['features40']} if any(f.startswith(p) or p in f for p in prefs)])
    if not feats: return None
    splits=[]
    for sp in SPLITS:
        tr=[r for r in rows if r['date']<sp]; te=[r for r in rows if r['date']>=sp]
        ytr=np.array([label(task,r) for r in tr]); yte=np.array([label(task,r) for r in te])
        if len(set(ytr))<2 or yte.sum()<2: return None
        Xtr=np.array([[r['features40'].get(f,0.0) for f in feats] for r in tr],float); Xte=np.array([[r['features40'].get(f,0.0) for f in feats] for r in te],float)
        keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
        if not keep: return None
        f2=[feats[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
        m=clf(model,abs(hash((task,indicator,model,sp)))%100000); m.fit(Xtr,ytr)
        ptr=m.predict_proba(Xtr)[:,1]; _,th,isst=tune(ytr,ptr)
        pte=m.predict_proba(Xte)[:,1]
        splits.append({'split':sp,'threshold':round(th,3),'isStats':isst,'oosStats':stats(yte,(pte>=th).astype(int)),'features':f2})
    avgP=float(np.mean([s['oosStats']['precision'] for s in splits])); avgR=float(np.mean([s['oosStats']['recall'] for s in splits])); avgF=float(np.mean([s['oosStats']['f1'] for s in splits])); minP=min(s['oosStats']['precision'] for s in splits); pred=sum(s['oosStats']['predN'] for s in splits)
    score=avgF+1.15*avgP+0.45*avgR+0.45*minP+min(pred,50)*0.08
    return {'task':task,'indicator':indicator,'model':model,'featureCount':len(feats),'avgPrecision':round(avgP,2),'avgRecall':round(avgR,2),'avgF1':round(avgF,2),'minPrecision':round(minP,2),'totalPredN':int(pred),'score':round(score,3),'splits':splits}
def main():
    rows=load_rows(); runs=[]
    for task in ['RS','D1A','D1S']:
        for ind in INDICATOR_MAP:
            best=None
            for mn in ['LOG','ET','RF']:
                r=eval_one(rows,task,ind,mn)
                if r and (best is None or r['score']>best['score']): best=r
            if best:
                runs.append(best)
                print(json.dumps({k:best[k] for k in ['task','indicator','model','avgPrecision','avgRecall','minPrecision','totalPredN','score']},ensure_ascii=False),flush=True)
    selected={}
    for task in ['RS','D1A','D1S']:
        arr=[r for r in runs if r['task']==task]
        arr.sort(key=lambda x:(x['score'],x['avgPrecision'],x['avgRecall']),reverse=True)
        selected[task]=arr[:12]
    payload={'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'method':'STEP 1 ONLY: select exactly 12 indicators out of the 40 indicator families for each task RS/D1A/D1S. Point-in-time features are computed on each historical sample date. Future fields are used only to build labels. No Step2 parameter tuning and no Step3 grouping/combo are used here.','splits':SPLITS,'sourceFeatureFile':str(D1SRC),'rows':len(rows),'indicatorMap':INDICATOR_MAP,'selected12ByTask':selected,'allRuns':runs}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    with CSV.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['task','rank','indicator','model','featureCount','avgPrecision','avgRecall','avgF1','minPrecision','totalPredN','score']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for task,arr in selected.items():
            for i,r in enumerate(arr,1): w.writerow({k:(i if k=='rank' else r.get(k)) for k in fields})
    print(json.dumps({'out':str(OUT),'csv':str(CSV),'selected':{t:[{k:r[k] for k in ['indicator','model','avgPrecision','avgRecall','minPrecision','totalPredN','score']} for r in a] for t,a in selected.items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
