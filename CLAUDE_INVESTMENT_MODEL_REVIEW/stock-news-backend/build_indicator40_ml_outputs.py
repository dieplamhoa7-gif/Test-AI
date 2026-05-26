from __future__ import annotations
import json, math, warnings, datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')
from ta.trend import SMAIndicator, EMAIndicator, WMAIndicator, MACD, IchimokuIndicator, ADXIndicator, AroonIndicator, TRIXIndicator, PSARIndicator, CCIIndicator, MassIndex
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, ROCIndicator, AwesomeOscillatorIndicator, UltimateOscillator, TSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel, DonchianChannel
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator, AccDistIndexIndicator, MFIIndicator, NegativeVolumeIndexIndicator
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

HIST=Path('stock-news-backend/data/vn100_history_2025_06_2026_05_cache.json')
D1A_SRC=Path('stock-news-backend/data/d1a_full_research_features_is_oos.json')
OUT=Path('stock-news-backend/data/indicator40_ml_research_output.json')
CFG=Path('stock-news-backend/data/indicator40_ml_selected_config.json')
SPLITS=['2025-10-01','2026-01-01']

INDICATOR_GROUPS={
 'TREND':['sma','ema','wma','macd','ichimoku','adx','psar','supertrend','dmi','aroon','zigzag','trix'],
 'MOMENTUM':['rsi','stochastic','cci','williams_r','momentum','roc','ao','ultimate_osc','tsi','kdj'],
 'VOLATILITY':['bollinger','atr','keltner','donchian','stddev','hist_vol','choppiness','chaikin_vol','rvi','mass_index'],
 'VOLUME':['vwap','obv','cmf','ad','mfi','vwma','pvi','nvi','vosc','klinger'],
}

# Utility indicators not directly available in ta.
def safe(s): return pd.to_numeric(s, errors='coerce').astype(float)
def slope(s,n): return s - s.shift(n)
def pct_rank(s,n=60): return s.rolling(n,min_periods=max(10,n//3)).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
def supertrend(close, high, low, period=10, mult=3.0):
    atr=AverageTrueRange(high,low,close,window=period).average_true_range()
    hl2=(high+low)/2; upper=hl2+mult*atr; lower=hl2-mult*atr
    st=pd.Series(index=close.index,dtype=float); direction=pd.Series(index=close.index,dtype=float)
    for i in range(len(close)):
        if i==0 or pd.isna(atr.iloc[i]): st.iloc[i]=np.nan; direction.iloc[i]=0; continue
        if close.iloc[i] > upper.iloc[i-1]: direction.iloc[i]=1
        elif close.iloc[i] < lower.iloc[i-1]: direction.iloc[i]=-1
        else: direction.iloc[i]=direction.iloc[i-1] if not pd.isna(direction.iloc[i-1]) else 0
        st.iloc[i]=lower.iloc[i] if direction.iloc[i]>=0 else upper.iloc[i]
    return st,direction

def choppiness(high, low, close, n=14):
    atr1=AverageTrueRange(high,low,close,window=1).average_true_range()
    trsum=atr1.rolling(n).sum(); denom=high.rolling(n).max()-low.rolling(n).min()
    return 100*np.log10(trsum/denom.replace(0,np.nan))/np.log10(n)

def klinger(high, low, close, volume, fast=34, slow=55, signal=13):
    tp=(high+low+close)/3; trend=np.sign(tp.diff()).replace(0,np.nan).ffill().fillna(1)
    vf=volume*trend*abs(2*((tp-tp.shift(1))/(high-low).replace(0,np.nan))).replace([np.inf,-np.inf],np.nan).fillna(0)
    ko=vf.ewm(span=fast,adjust=False).mean()-vf.ewm(span=slow,adjust=False).mean()
    sig=ko.ewm(span=signal,adjust=False).mean()
    return ko, sig

def zigzag_proxy(close, n=20):
    roll_hi=close.rolling(n).max(); roll_lo=close.rolling(n).min()
    return ((close>=roll_hi.shift(1)).astype(float) - (close<=roll_lo.shift(1)).astype(float))

def add_indicator40(df):
    o,h,l,c,v=[safe(df[x]) for x in ['open','high','low','close','volume']]
    out=pd.DataFrame({'date':df['time'].astype(str),'close':c,'volume':v})
    # Trend
    for n in [10,20,50,100,200]:
        sma=SMAIndicator(c,n).sma_indicator(); ema=EMAIndicator(c,n).ema_indicator()
        out[f'sma{n}_dist']=c/sma-1; out[f'ema{n}_dist']=c/ema-1
        if n in [10,20,50]: out[f'sma{n}_slope5']=slope(sma,5)/c
    for n in [20,50]: out[f'wma{n}_dist']=c/WMAIndicator(c,n).wma()-1
    macd=MACD(c); out['macd']=macd.macd(); out['macd_signal']=macd.macd_signal(); out['macd_hist']=macd.macd_diff(); out['macd_hist_slope5']=slope(out['macd_hist'],5)
    ichi=IchimokuIndicator(h,l); out['ichi_conv_base']=ichi.ichimoku_conversion_line()-ichi.ichimoku_base_line(); out['ichi_cloud_pos']=c-((ichi.ichimoku_a()+ichi.ichimoku_b())/2)
    adx=ADXIndicator(h,l,c); out['adx14']=adx.adx(); out['plusDI']=adx.adx_pos(); out['minusDI']=adx.adx_neg(); out['diSpread']=out['plusDI']-out['minusDI']
    psar=PSARIndicator(h,l,c).psar(); out['psar_dist']=c/psar-1
    st,st_dir=supertrend(c,h,l); out['supertrend_dist']=c/st-1; out['supertrend_dir']=st_dir
    ar=AroonIndicator(h,l,window=25); out['aroon_up']=ar.aroon_up(); out['aroon_down']=ar.aroon_down(); out['aroon_osc']=out['aroon_up']-out['aroon_down']
    out['zigzag20']=zigzag_proxy(c,20); out['trix15']=TRIXIndicator(c,15).trix(); out['trix_slope5']=slope(out['trix15'],5)
    # Momentum
    for n in [7,14,21]: out[f'rsi{n}']=RSIIndicator(c,n).rsi(); out[f'rsi{n}_slope5']=slope(out[f'rsi{n}'],5)
    stoch=StochasticOscillator(h,l,c,window=14,smooth_window=3); out['stoch_k']=stoch.stoch(); out['stoch_d']=stoch.stoch_signal(); out['stoch_spread']=out['stoch_k']-out['stoch_d']
    for n in [20,40]: out[f'cci{n}']=CCIIndicator(h,l,c,window=n).cci()
    out['williams_r14']=WilliamsRIndicator(h,l,c,lbp=14).williams_r()
    for n in [10,20,40,60]: out[f'mom{n}']=c-c.shift(n); out[f'roc{n}']=ROCIndicator(c,n).roc()
    out['ao']=AwesomeOscillatorIndicator(h,l).awesome_oscillator(); out['ao_slope5']=slope(out['ao'],5)
    out['ultimate_osc']=UltimateOscillator(h,l,c).ultimate_oscillator(); out['tsi']=TSIIndicator(c).tsi()
    out['kdj_j']=3*out['stoch_k']-2*out['stoch_d']
    # Volatility
    bb=BollingerBands(c,window=20,window_dev=2); out['bb_width']=bb.bollinger_wband(); out['bb_pct']=bb.bollinger_pband(); out['bb_break_low']=(c<bb.bollinger_lband()).astype(float)
    atr=AverageTrueRange(h,l,c,window=14).average_true_range(); out['atr14_pct']=atr/c; out['atr14_slope5']=slope(atr,5)/c
    kc=KeltnerChannel(h,l,c,window=20); out['keltner_width']=(kc.keltner_channel_hband()-kc.keltner_channel_lband())/c; out['keltner_pos']=(c-kc.keltner_channel_lband())/(kc.keltner_channel_hband()-kc.keltner_channel_lband()).replace(0,np.nan)
    dc=DonchianChannel(h,l,c,window=20); out['donchian_pos']=dc.donchian_channel_pband(); out['donchian_width']=dc.donchian_channel_wband()
    out['std20_pct']=c.rolling(20).std()/c; ret=c.pct_change(); out['hist_vol20']=ret.rolling(20).std()*np.sqrt(252)
    out['choppiness14']=choppiness(h,l,c,14)
    hl_range=h-l; out['chaikin_vol']=hl_range.ewm(span=10,adjust=False).mean().pct_change(10)
    up_std=ret.where(ret>0,0).rolling(14).std(); dn_std=ret.where(ret<0,0).abs().rolling(14).std(); out['rvi14']=100*up_std/(up_std+dn_std).replace(0,np.nan)
    out['mass_index']=MassIndex(h,l).mass_index()
    # Volume
    out['vwap20_dist']=c/VolumeWeightedAveragePrice(h,l,c,v,window=20).volume_weighted_average_price()-1
    obv=OnBalanceVolumeIndicator(c,v).on_balance_volume(); out['obv_slope20']=slope(obv,20)/v.rolling(20).mean(); out['obv_pct_rank60']=pct_rank(obv,60)
    out['cmf20']=ChaikinMoneyFlowIndicator(h,l,c,v,window=20).chaikin_money_flow()
    ad=AccDistIndexIndicator(h,l,c,v).acc_dist_index(); out['ad_slope20']=slope(ad,20)/v.rolling(20).mean()
    out['mfi14']=MFIIndicator(h,l,c,v,window=14).money_flow_index()
    for n in [20,50]: out[f'vwma{n}_dist']=c/((c*v).rolling(n).sum()/v.rolling(n).sum())-1
    pvi=pd.Series(1000.0,index=c.index); nvi=NegativeVolumeIndexIndicator(c,v).negative_volume_index()
    for i in range(1,len(c)):
        pvi.iloc[i]=pvi.iloc[i-1]*(1+(c.iloc[i]/c.iloc[i-1]-1)) if v.iloc[i]>v.iloc[i-1] and c.iloc[i-1] else pvi.iloc[i-1]
    out['pvi_slope20']=slope(pvi,20); out['nvi_slope20']=slope(nvi,20)
    vol_fast=v.rolling(5).mean(); vol_slow=v.rolling(20).mean(); out['vosc_5_20']=(vol_fast-vol_slow)/vol_slow.replace(0,np.nan)
    ko,ks=klinger(h,l,c,v); out['klinger']=ko; out['klinger_signal_spread']=ko-ks
    return out.replace([np.inf,-np.inf],np.nan)

def load_feature_rows():
    hist=json.load(open(HIST,encoding='utf-8'))['symbols']
    d1items=json.load(open(D1A_SRC,encoding='utf-8'))['items']
    need={(x['symbol'],x['date']) for x in d1items}
    d1map={(x['symbol'],x['date']):x for x in d1items}
    rows=[]
    for sym,payload in hist.items():
        if not any(s==sym for s,_ in need): continue
        df=pd.DataFrame(payload['rows']).sort_values('time').reset_index(drop=True)
        if len(df)<80: continue
        feat=add_indicator40(df)
        for _,r in feat.iterrows():
            key=(sym,str(r['date']))
            if key not in d1map: continue
            base=d1map[key]
            f={k:float(v) for k,v in r.items() if k not in ['date'] and pd.notna(v) and isinstance(v,(int,float,np.integer,np.floating))}
            rows.append({'symbol':sym,'date':key[1],'sector':base.get('sector'),'indicator40':f,'rs':base['rs'],'lc':base['lc'],'fullResearchFeatures':base['fullResearchFeatures'],'mtfAsOfDate':base.get('mtfAsOfDate') or {}})
    rows.sort(key=lambda x:(x['date'],x['symbol']))
    return rows

def labels(kind,r):
    lc=r['lc']; rs=r['rs']; f=r['fullResearchFeatures']; mtf=r['mtfAsOfDate']
    if kind=='D1A':
        future_survive=(lc.get('futureMin20') or 0)>-8 and (lc.get('futureClose20') or 0)>-5
        absorption=(f.get('dryUp20_norm',0)>0 or f.get('greenAbsorb10_norm',0)>0 or f.get('baseQualityScore_norm',0)>0)
        base_ok=(f.get('range40Pct_inv',0)>0 or f.get('tightClose20_norm',0)>0 or rs.get('nearSupport'))
        return int(bool(future_survive and (absorption or base_ok)))
    if kind=='D1S':
        future_bad=(lc.get('futureMin20') or 0)<-10 or ((lc.get('futureClose20') or 0)<-6 and (lc.get('futureMin20') or 0)<-7)
        structural=rs.get('supportBroken') or rs.get('weekSupportBroken') or f.get('support_break',0)>0 or f.get('break_ma_cluster',0)>0
        distro=f.get('distribution_cluster',0)>0 or (f.get('two_red_high_vol_5d',0)>0 and f.get('close_low_cluster',0)>0)
        mtf_bad=((mtf.get('W_rsi14') or 50)<42 and not mtf.get('W_macdImproving')) or (not mtf.get('W_aboveMa20') and not mtf.get('W_maTrendUp'))
        return int(bool(future_bad and (structural or distro or mtf_bad)))
    if kind=='RS':
        # support/resistance usefulness proxy: near support/base survives OR breakout/reclaim does not fail badly.
        near=bool(rs.get('nearSupport') or abs(rs.get('distSupportPct') or 99)<4)
        survive=(lc.get('futureMin20') or 0)>-7
        rebound=(lc.get('futureMax20') or 0)>5
        return int(bool(near and survive and rebound))
    raise ValueError(kind)

def met(y,p):
    pr,rc,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0)
    return {'n':len(y),'tp':int(((p==1)&(y==1)).sum()),'fp':int(((p==1)&(y==0)).sum()),'tn':int(((p==0)&(y==0)).sum()),'fn':int(((p==0)&(y==1)).sum()),'precision':round(pr*100,2),'recall':round(rc*100,2),'accuracy':round(accuracy_score(y,p)*100,2),'f1':round(f1*100,2),'predN':int((p==1).sum()),'oracleN':int((y==1).sum())}

def tune(y,prob,mode='balanced'):
    best=(-1,.5,None)
    for th in np.linspace(.1,.9,81):
        st=met(y,(prob>=th).astype(int))
        if st['predN']<max(5,int(len(y)*.015)): continue
        obj=st['f1']+.8*st['precision']+.6*st['recall']
        if mode=='precision': obj=st['f1']+1.4*st['precision']+.35*st['recall']
        if obj>best[0]: best=(obj,float(th),st)
    return best

def model(name,seed):
    if name=='ET': return ExtraTreesClassifier(n_estimators=320,max_depth=5,min_samples_leaf=6,class_weight='balanced',random_state=seed,n_jobs=1)
    if name=='RF': return RandomForestClassifier(n_estimators=320,max_depth=5,min_samples_leaf=8,class_weight='balanced',random_state=seed,n_jobs=1)
    if name=='HGB': return HistGradientBoostingClassifier(max_iter=160,learning_rate=.04,max_leaf_nodes=10,l2_regularization=.5,random_state=seed)
    return Pipeline([('s',StandardScaler()),('l',LogisticRegression(max_iter=1000,C=.35,class_weight='balanced',random_state=seed))])

def eval_task(rows,task,features,model_name,mode):
    res=[]; imps=[]
    for split in SPLITS:
        tr=[r for r in rows if r['date']<split]; te=[r for r in rows if r['date']>=split]
        ytr=np.array([labels(task,r) for r in tr]); yte=np.array([labels(task,r) for r in te])
        if len(set(ytr))<2 or yte.sum()<3: return None
        Xtr=np.array([[r['indicator40'].get(f,0.0) for f in features] for r in tr],float)
        Xte=np.array([[r['indicator40'].get(f,0.0) for f in features] for r in te],float)
        m=model(model_name,abs(hash((task,model_name,mode,len(features))))%100000)
        try: m.fit(Xtr,ytr); ptr=m.predict_proba(Xtr)[:,1]; pte=m.predict_proba(Xte)[:,1]
        except Exception: return None
        _,th,isst=tune(ytr,ptr,mode); oos=met(yte,(pte>=th).astype(int))
        imp={}
        if hasattr(m,'feature_importances_'):
            imp={k:round(float(v),5) for k,v in sorted(zip(features,m.feature_importances_),key=lambda kv:kv[1],reverse=True)[:20]}
        res.append({'split':split,'threshold':round(th,3),'isStats':isst,'oosStats':oos,'topFeatures':imp})
    avgP=sum(x['oosStats']['precision'] for x in res)/len(res); avgR=sum(x['oosStats']['recall'] for x in res)/len(res); avgF=sum(x['oosStats']['f1'] for x in res)/len(res); minP=min(x['oosStats']['precision'] for x in res); minF=min(x['oosStats']['f1'] for x in res)
    score=avgF+.8*avgP+.55*avgR+.4*minP+.3*minF
    return {'score':round(score,3),'avgPrecision':round(avgP,2),'avgRecall':round(avgR,2),'avgF1':round(avgF,2),'minPrecision':round(minP,2),'minF1':round(minF,2),'splits':res}

def main():
    rows=load_feature_rows()
    all_features=sorted({k for r in rows for k in r['indicator40']})
    # remove constant features
    vals=np.array([[r['indicator40'].get(f,0.0) for f in all_features] for r in rows],float)
    keep=[f for i,f in enumerate(all_features) if np.nanstd(vals[:,i])>1e-9]
    groups={'ALL40':keep}
    # prefix groups from indicator names
    for g,inds in INDICATOR_GROUPS.items():
        fs=[f for f in keep if any(f.startswith(ind) or ind in f for ind in inds)]
        groups[g]=fs
    # individual indicator family groups
    for ind in sum(INDICATOR_GROUPS.values(),[]):
        fs=[f for f in keep if f.startswith(ind) or ind in f]
        if fs: groups['IND_'+ind]=fs
    runs=[]
    for task in ['RS','D1A','D1S']:
        pos=sum(labels(task,r) for r in rows)
        for g,fs in groups.items():
            if len(fs)<2: continue
            for mn in ['ET','RF','HGB','LOG']:
                for mode in ['balanced','precision']:
                    rr=eval_task(rows,task,fs,mn,mode)
                    if rr: runs.append({'task':task,'positiveRate':round(pos/len(rows)*100,2),'positiveN':pos,'group':g,'featureCount':len(fs),'model':mn,'mode':mode,**rr})
    runs.sort(key=lambda x:(x['task'], -x['score']))
    bytask={}
    for task in ['RS','D1A','D1S']:
        top=[r for r in runs if r['task']==task]
        bytask[task]=top[:20]
    payload={'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'sourceRows':len(rows),'featureCount':len(keep),'indicatorGroups':INDICATOR_GROUPS,'topByTask':bytask}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    cfg={'createdAt':payload['createdAt'],'sourceResearch':str(OUT),'selected':{task:bytask[task][0] if bytask[task] else None for task in bytask},'scannerRule':'Use selected feature families/configs from this artifact; production scanners must not retrain/search.'}
    CFG.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'out':str(OUT),'config':str(CFG),'rows':len(rows),'features':len(keep),'best':cfg['selected']},ensure_ascii=False,indent=2)[:24000])
if __name__=='__main__': main()
