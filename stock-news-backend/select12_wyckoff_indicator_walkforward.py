# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from ta.momentum import RSIIndicator, ROCIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, ADXIndicator, CCIIndicator, EMAIndicator, SMAIndicator, TRIXIndicator
from ta.volatility import AverageTrueRange, BollingerBands, DonchianChannel
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator, MFIIndicator, AccDistIndexIndicator

from wyckoff_features import snapshots_for_rows

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'vn100_history_from_2023.json'
OUT = ROOT / 'data' / 'select12_wyckoff_indicator_walkforward.json'
HORIZONS = [10, 20, 40]
SPLITS = ['2024-01-01', '2024-07-01', '2025-01-01', '2025-07-01', '2026-01-01']
TARGETS = ['label_markup', 'label_markdown', 'label_range']
WYCKOFF = ['springScore','upthrustScore','sosScore','sowScore','dryTestScore','absorptionScore','distributionScore','markupReadinessScore','markdownReadinessScore','rangeContinuationScore']
BAR = ['close_pos','vol_rel20','range_rel20','ret_1d','ret_3d','ret_5d','range_width_pct']
INDICATORS = [
 'rsi14','rsi7','rsi21','rsi14_slope3','roc10','roc20','stoch_k14','stoch_d14','willr14','cci10','cci20',
 'macd_hist','macd_line','adx14','plus_di14','minus_di14','ema20_dist','ema50_dist','sma20_dist','sma50_dist',
 'trix15','atr14_pct','atr14_slope3','bb_width20','bb_pct20','donchian_pos20','obv_slope10','cmf20','mfi14','ad_slope10',
 'vol_z20','vol_rel20_ind','vol_slope3'
]
ALL_FEATURES = WYCKOFF + BAR + INDICATORS
TRAIN_MIN = 18000
TEST_MIN = 6000

def load_symbols():
    return (json.loads(DATA.read_text(encoding='utf-8')).get('symbols') or {})

def safe(s):
    return pd.to_numeric(s, errors='coerce').replace([np.inf,-np.inf], np.nan)

def enrich(rows):
    df=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
    for c in ['open','high','low','close','volume']:
        df[c]=safe(df[c])
    c,h,l,v=df['close'],df['high'],df['low'],df['volume']
    df['rsi14']=RSIIndicator(c,14).rsi(); df['rsi7']=RSIIndicator(c,7).rsi(); df['rsi21']=RSIIndicator(c,21).rsi(); df['rsi14_slope3']=df['rsi14']-df['rsi14'].shift(3)
    df['roc10']=ROCIndicator(c,10).roc(); df['roc20']=ROCIndicator(c,20).roc()
    st=StochasticOscillator(h,l,c,14,3); df['stoch_k14']=st.stoch(); df['stoch_d14']=st.stoch_signal(); df['willr14']=WilliamsRIndicator(h,l,c,14).williams_r()
    df['cci10']=CCIIndicator(h,l,c,10).cci(); df['cci20']=CCIIndicator(h,l,c,20).cci()
    macd=MACD(c); df['macd_hist']=macd.macd_diff(); df['macd_line']=macd.macd()
    adx=ADXIndicator(h,l,c,14); df['adx14']=adx.adx(); df['plus_di14']=adx.adx_pos(); df['minus_di14']=adx.adx_neg()
    df['ema20_dist']=c/EMAIndicator(c,20).ema_indicator()-1; df['ema50_dist']=c/EMAIndicator(c,50).ema_indicator()-1
    df['sma20_dist']=c/SMAIndicator(c,20).sma_indicator()-1; df['sma50_dist']=c/SMAIndicator(c,50).sma_indicator()-1
    df['trix15']=TRIXIndicator(c,15).trix()
    atr=AverageTrueRange(h,l,c,14).average_true_range(); df['atr14_pct']=atr/c; df['atr14_slope3']=df['atr14_pct']-df['atr14_pct'].shift(3)
    bb=BollingerBands(c,20,2); df['bb_width20']=bb.bollinger_wband(); df['bb_pct20']=bb.bollinger_pband()
    dc=DonchianChannel(h,l,c,20); lo=dc.donchian_channel_lband(); hi=dc.donchian_channel_hband(); df['donchian_pos20']=(c-lo)/(hi-lo).replace(0,np.nan)
    obv=OnBalanceVolumeIndicator(c,v).on_balance_volume(); df['obv_slope10']=obv-obv.shift(10)
    df['cmf20']=ChaikinMoneyFlowIndicator(h,l,c,v,20).chaikin_money_flow(); df['mfi14']=MFIIndicator(h,l,c,v,14).money_flow_index()
    ad=AccDistIndexIndicator(h,l,c,v).acc_dist_index(); df['ad_slope10']=ad-ad.shift(10)
    vma=v.rolling(20).mean(); vs=v.rolling(20).std(); df['vol_z20']=(v-vma)/vs.replace(0,np.nan); df['vol_rel20_ind']=v/vma.replace(0,np.nan); df['vol_slope3']=df['vol_rel20_ind']-df['vol_rel20_ind'].shift(3)
    return df

def forward(rows, idx, horizon):
    if idx+horizon>=len(rows): return None
    close=float(rows[idx]['close']); fut=rows[idx+1:idx+horizon+1]
    if close<=0 or not fut: return None
    ret=float(fut[-1]['close'])/close-1; max_up=max(float(r['high']) for r in fut)/close-1; max_down=min(float(r['low']) for r in fut)/close-1
    return {'ret':ret,'max_up':max_up,'max_down':max_down,'label_markup':int(ret>0.06 and max_down>-0.06),'label_markdown':int(ret<-0.06 or max_down<-0.08),'label_range':int(abs(ret)<0.03 and max_up<0.05 and max_down>-0.05)}

def build_panel():
    panel=[]
    for sym,payload in load_symbols().items():
        rows=(payload or {}).get('rows') or []
        if len(rows)<140: continue
        df=enrich(rows); snaps=snapshots_for_rows(rows,symbol=sym,lookback=60,min_bars=80); by_time={str(r.get('time')):i for i,r in enumerate(rows)}
        for snap in snaps:
            t=str(snap.get('time')); idx=by_time.get(t)
            if idx is None: continue
            bar=snap.get('bar') or {}; tr=snap.get('range') or {}; scores=snap.get('scores') or {}
            rec={'symbol':sym,'time':t,'close_pos':float(bar.get('close_pos') or 0),'vol_rel20':float(bar.get('vol_rel20') or 0),'range_rel20':float(bar.get('range_rel20') or 0),'ret_1d':float(bar.get('ret_1d') or 0),'ret_3d':float(bar.get('ret_3d') or 0),'ret_5d':float(bar.get('ret_5d') or 0),'range_width_pct':float(tr.get('width_pct') or 0)}
            for f in WYCKOFF: rec[f]=float(scores.get(f) or 0)
            for f in INDICATORS: rec[f]=float(df.iloc[idx].get(f) if pd.notna(df.iloc[idx].get(f)) else 0)
            ok=True
            for hzn in HORIZONS:
                fs=forward(rows,idx,hzn)
                if not fs: ok=False; break
                for k,v in fs.items(): rec[f'h{hzn}_{k}']=v
            if ok: panel.append(rec)
    return sorted(panel,key=lambda x:(x['time'],x['symbol']))

def model_lr():
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sc',StandardScaler()),('lr',LogisticRegression(max_iter=1200,class_weight='balanced'))])

def select12(train, label_col):
    X=np.array([[x.get(f,0.0) for f in ALL_FEATURES] for x in train],float); y=np.array([int(x[label_col]) for x in train])
    imp=SimpleImputer(strategy='median'); X=imp.fit_transform(X)
    rf=RandomForestClassifier(n_estimators=220,max_depth=6,min_samples_leaf=60,class_weight='balanced_subsample',random_state=42,n_jobs=-1)
    rf.fit(X,y)
    idx=np.argsort(-rf.feature_importances_)[:12]
    return [ALL_FEATURES[i] for i in idx], {ALL_FEATURES[i]:round(float(rf.feature_importances_[i]),5) for i in idx}

def eval_one(panel, split, hzn, target):
    label_col=f'h{hzn}_{target}'; train=[x for x in panel if x['time']<split]; test=[x for x in panel if x['time']>=split]
    if len(train)<TRAIN_MIN or len(test)<TEST_MIN: return {'split':split,'skipped':'rows','trainRows':len(train),'testRows':len(test)}
    ytr=np.array([int(x[label_col]) for x in train]); yte=np.array([int(x[label_col]) for x in test])
    if len(np.unique(ytr))<2 or len(np.unique(yte))<2: return {'split':split,'skipped':'class'}
    selected, importance=select12(train,label_col)
    Xtr=np.array([[x.get(f,0.0) for f in selected] for x in train],float); Xte=np.array([[x.get(f,0.0) for f in selected] for x in test],float)
    m=model_lr(); m.fit(Xtr,ytr); ptr=m.predict_proba(Xtr)[:,1]; pte=m.predict_proba(Xte)[:,1]; pred=(pte>=0.5).astype(int)
    order=np.argsort(-pte); ranked={}
    for k in [50,100,300]:
        kk=min(k,len(order)); items=[test[i] for i in order[:kk]]
        ranked[f'top{kk}']={'n':kk,'avgRetPct':round(mean(x[f'h{hzn}_ret'] for x in items)*100,2),'hitRatePct':round(mean(int(x[label_col]) for x in items)*100,2),'avgMaxUpPct':round(mean(x[f'h{hzn}_max_up'] for x in items)*100,2),'avgMaxDownPct':round(mean(x[f'h{hzn}_max_down'] for x in items)*100,2)}
    coefs={f:round(float(c),4) for f,c in zip(selected,m.named_steps['lr'].coef_[0])}
    return {'split':split,'selected12':selected,'rfImportance':importance,'trainRows':len(train),'testRows':len(test),'trainPositiveRatePct':round(float(ytr.mean()*100),2),'testPositiveRatePct':round(float(yte.mean()*100),2),'trainAUC':round(float(roc_auc_score(ytr,ptr)),4),'testAUC':round(float(roc_auc_score(yte,pte)),4),'precision':round(float(precision_score(yte,pred,zero_division=0)),4),'recall':round(float(recall_score(yte,pred,zero_division=0)),4),'f1':round(float(f1_score(yte,pred,zero_division=0)),4),'coefs':coefs,'rankedOOS':ranked}

def agg(valid):
    if not valid: return {'nSplits':0}
    out={'nSplits':len(valid)}
    for k in ['testAUC','precision','recall','f1']:
        vals=[x[k] for x in valid]; out[f'avg_{k}']=round(mean(vals),4); out[f'min_{k}']=round(min(vals),4); out[f'max_{k}']=round(max(vals),4)
    cnt=Counter(f for x in valid for f in x['selected12']); out['topSelected']=cnt.most_common(20)
    return out

def main():
    panel=build_panel(); out={'rows':len(panel),'allFeatures':ALL_FEATURES,'results':{}}
    for h in HORIZONS:
        out['results'][f'h{h}']={}
        for target in TARGETS:
            splits=[eval_one(panel,s,h,target) for s in SPLITS]
            valid=[s for s in splits if 'testAUC' in s]
            out['results'][f'h{h}'][target]={'summary':agg(valid),'splits':splits}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    preview={h:{t:out['results'][h][t]['summary'] for t in TARGETS} for h in out['results']}
    print(json.dumps({'rows':len(panel),'output':str(OUT),'preview':preview},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
