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
from sklearn.metrics import precision_recall_fscore_support

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
TRADES=DATA/'lh1_canonical_t3_fee_2023_to_now.json'
HIST=DATA/'vn100_history_from_2023.json'
IND40=ROOT/'build_indicator40_ml_outputs.py'
OUT=DATA/'lh1_v3_ml_probability_gate_research.json'
CSV=DATA/'lh1_v3_ml_probability_gate_research.csv'

spec=importlib.util.spec_from_file_location('ind40', IND40)
ind40=importlib.util.module_from_spec(spec); spec.loader.exec_module(ind40)

WALK_SPLITS=[
    ('2024', '2023-01-01', '2024-01-01', '2025-01-01'),
    ('2025', '2023-01-01', '2025-01-01', '2026-01-01'),
    ('2026_ytd', '2023-01-01', '2026-01-01', '2026-06-01'),
]
FEATURE_FAMILIES={
 'RS_TOP':['roc','williams','sma10','stoch','choppiness','obv'],
 'D1A_TOP':['keltner','std20','ema20','mom','hist_vol'],
 'RS_D1A_TOP':['roc','williams','sma10','stoch','choppiness','obv','keltner','std20','ema20','mom','hist_vol'],
 'TREND_MOM_VOL':['sma','ema','roc','mom','rsi','macd','volume','obv','atr','bb'],
 'ALL40':None,
}

def f(v,d=0.0):
    try:
        if v is None or pd.isna(v): return d
        if hasattr(v,'item'): v=v.item()
        return float(v)
    except Exception: return d

def metrics(rows):
    n=len(rows); wins=sum(1 for r in rows if f(r.get('netPnlPct'))>0); sm=sum(f(r.get('netPnlPct')) for r in rows)
    return {'trades':n,'wins':wins,'losses':n-wins,'winRatePct':round(wins/n*100,2) if n else 0,'avgNetPnlPct':round(sm/n,2) if n else 0,'sumNetPnlPct':round(sm,2),'avgHold':round(sum(f(r.get('holdSessions')) for r in rows)/n,2) if n else 0}

def clf(name,seed):
    if name=='ET': return ExtraTreesClassifier(n_estimators=240,max_depth=3,min_samples_leaf=5,class_weight='balanced',random_state=seed,n_jobs=1)
    if name=='RF': return RandomForestClassifier(n_estimators=240,max_depth=3,min_samples_leaf=5,class_weight='balanced',random_state=seed,n_jobs=1)
    return Pipeline([('s',StandardScaler()),('l',LogisticRegression(max_iter=1000,C=.35,class_weight='balanced',random_state=seed))])

def load_feature_rows():
    trades=json.loads(TRADES.read_text(encoding='utf-8'))['trades']
    hist=json.loads(HIST.read_text(encoding='utf-8'))['symbols']
    need=defaultdict(set)
    trade_by_key={}
    for t in trades:
        key=(t['symbol'], t['signalDate'])
        need[t['symbol']].add(t['signalDate'])
        trade_by_key[key]=t
    rows=[]; all_feats=set()
    for sym, dates in need.items():
        hp=hist.get(sym) or {}; raw=hp.get('rows') or []
        if not raw: continue
        df=pd.DataFrame(raw).sort_values('time').reset_index(drop=True)
        # indicator40 expects usual OHLCV columns and creates date column
        feat=ind40.add_indicator40(df).fillna(0)
        for _,r in feat.iterrows():
            d=str(r.get('date') or r.get('time'))[:10]
            if d not in dates: continue
            t=trade_by_key[(sym,d)]
            feats={k:float(v) for k,v in r.items() if k not in ('date','time') and isinstance(v,(int,float,np.integer,np.floating)) and np.isfinite(v)}
            # add canonical entry indicators too, point-in-time saved at signal
            ai=t.get('entryIndicators') or {}
            for k in ['rsi','macd','macdSignal','macdHist','bbPercent','volumeRatio','roc20','ret5']:
                feats['lh1_'+k]=f(ai.get(k))
            ichi=ai.get('ichimoku') or {}
            for k in ['tenkan','kijun','cloudTop','cloudBottom']:
                feats['lh1_ichi_'+k]=f(ichi.get(k))
            feats['lh1_bullishDivergence']=1.0 if ai.get('bullishDivergence') else 0.0
            all_feats.update(feats)
            row=dict(t)
            row['features']=feats
            row['label']=1 if f(t.get('netPnlPct'))>0 else 0
            rows.append(row)
    rows.sort(key=lambda x:(x['signalDate'],x['symbol']))
    return rows, sorted(all_feats)

def choose_features(all_feats,family):
    toks=FEATURE_FAMILIES[family]
    if toks is None:
        return all_feats
    return [x for x in all_feats if any(tok.lower() in x.lower() for tok in toks)]

def tune_threshold(train_rows, probs, mode):
    best=None
    y=np.array([r['label'] for r in train_rows])
    pnl=np.array([f(r.get('netPnlPct')) for r in train_rows])
    for th in np.linspace(.20,.90,71):
        pred=probs>=th
        n=int(pred.sum())
        if n<max(8, int(len(train_rows)*0.12)): continue
        wr=float(y[pred].mean()*100) if n else 0
        avg=float(pnl[pred].mean()) if n else 0
        sm=float(pnl[pred].sum()) if n else 0
        # modes: precision first, pnl first, balanced
        if mode=='precision': score=wr*2.0 + avg*12 + min(n,50)*0.15
        elif mode=='pnl': score=avg*30 + wr*0.9 + min(sm,80)*0.15
        else: score=wr*1.35 + avg*22 + min(n,60)*0.12
        cand=(score, float(th), {'trainTrades':n,'trainWinRatePct':round(wr,2),'trainAvgNetPnlPct':round(avg,2),'trainSumNetPnlPct':round(sm,2)})
        if best is None or cand[0]>best[0]: best=cand
    return best

def eval_model(rows, all_feats, family, model_name, mode):
    features=choose_features(all_feats,family)
    out=[]; selected=[]
    for split_name, train_start, train_end, test_end in WALK_SPLITS:
        tr=[r for r in rows if train_start <= r['signalDate'] < train_end]
        te=[r for r in rows if train_end <= r['signalDate'] < test_end]
        if len(tr)<30 or len(te)<1 or len(set(r['label'] for r in tr))<2: continue
        Xtr=np.array([[r['features'].get(k,0.0) for k in features] for r in tr],float)
        Xte=np.array([[r['features'].get(k,0.0) for k in features] for r in te],float)
        keep=[i for i,s in enumerate(Xtr.std(axis=0)) if s>1e-9]
        if len(keep)<3: continue
        f2=[features[i] for i in keep]; Xtr=Xtr[:,keep]; Xte=Xte[:,keep]
        m=clf(model_name, abs(hash((family,model_name,mode,split_name)))%100000)
        m.fit(Xtr, np.array([r['label'] for r in tr]))
        ptr=m.predict_proba(Xtr)[:,1]
        tuned=tune_threshold(tr, ptr, mode)
        if tuned is None: continue
        _,th,train_stats=tuned
        pte=m.predict_proba(Xte)[:,1]
        pick=[]
        for r0,p in zip(te,pte):
            if p>=th:
                rr=dict(r0); rr['mlProb']=round(float(p),4); rr['split']=split_name; pick.append(rr); selected.append(rr)
        out.append({'split':split_name,'trainN':len(tr),'testN':len(te),'threshold':round(th,3),'trainStats':train_stats,'testStats':metrics(pick),'featureCount':len(f2),'features':f2[:80]})
    if not out: return None
    allstats=metrics(selected)
    # require not just 1 lucky split
    score=allstats['winRatePct']*1.6 + allstats['avgNetPnlPct']*28 + min(allstats['trades'],80)*0.15 + allstats['sumNetPnlPct']*0.08
    return {'family':family,'model':model_name,'mode':mode,'score':round(score,3),'overall':allstats,'splits':out,'selectedTradesSample':selected[:30]}

def window_stats(rows):
    wins={
      '2023':('2023-01-01','2024-01-01'),
      '2024':('2024-01-01','2025-01-01'),
      '2025':('2025-01-01','2026-01-01'),
      '2026_ytd':('2026-01-01','2026-06-01'),
      'all_2023_now':('2023-01-01','2026-06-01')}
    return {k:metrics([r for r in rows if a<=r['signalDate']<b]) for k,(a,b) in wins.items()}

def main():
    rows, all_feats=load_feature_rows()
    baseline=json.loads(TRADES.read_text(encoding='utf-8'))
    runs=[]
    for fam in FEATURE_FAMILIES:
        for mn in ['LOG','ET','RF']:
            for mode in ['balanced','precision','pnl']:
                r=eval_model(rows,all_feats,fam,mn,mode)
                if r:
                    runs.append(r)
                    print(json.dumps({'family':fam,'model':mn,'mode':mode,'overall':r['overall'],'score':r['score']},ensure_ascii=False),flush=True)
    runs.sort(key=lambda x:(x['overall']['avgNetPnlPct'],x['overall']['winRatePct'],x['overall']['trades'],x['score']), reverse=True)
    payload={'createdAt':pd.Timestamp.now().isoformat(),'method':'LH1_v3 research: ML probability gate trained only on prior accepted LH1 signals. Label = canonical LH1 netPnlPct > 0. Features = indicator40 + saved point-in-time LH1 indicators at signal date. Walk-forward splits train past/test future; no production changes.','baselineWindows':baseline['windows'],'baselineAll':baseline['windows']['all_2023_now'],'rows':len(rows),'featureCount':len(all_feats),'topRuns':runs[:20]}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    with CSV.open('w',encoding='utf-8-sig') as f:
        f.write('rank,family,model,mode,trades,winRatePct,avgNetPnlPct,sumNetPnlPct,score\n')
        for i,r in enumerate(runs[:50],1):
            o=r['overall']; f.write(f"{i},{r['family']},{r['model']},{r['mode']},{o['trades']},{o['winRatePct']},{o['avgNetPnlPct']},{o['sumNetPnlPct']},{r['score']}\n")
    print(json.dumps({'out':str(OUT),'csv':str(CSV),'baseline':baseline['windows']['all_2023_now'],'best':runs[0] if runs else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
