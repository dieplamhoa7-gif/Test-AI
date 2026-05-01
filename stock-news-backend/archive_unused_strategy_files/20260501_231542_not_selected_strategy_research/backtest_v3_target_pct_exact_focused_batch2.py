from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.market_data import _load_history,_compute_indicators,_detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/v3_target_pct_exact_focused_backtest_batch2.json')
LOOKBACK_DAYS=180; HORIZON=42; MAX_SYMBOLS=50; SYMBOL_OFFSET=50
CONFIGS=[]
for target in [0.06,0.07]:
  for min_score in [60,65,68,70,72]:
    for max_dist in [3,4,5]:
      for max_risk in [4,5]:
        CONFIGS.append({'targetPct':target,'minScore':min_score,'maxDist':max_dist,'maxRisk':max_risk})

def f(v,d=0.0):
    try:
        if v is None: return d
        if hasattr(v,'item'): v=v.item()
        if pd.isna(v): return d
        return float(v)
    except Exception: return d

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def atr_series(df,n=14):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def ichimoku_state(df):
    h=pd.to_numeric(df.high,errors='coerce'); l=pd.to_numeric(df.low,errors='coerce'); c=pd.to_numeric(df.close,errors='coerce')
    ten=(h.rolling(9).max()+l.rolling(9).min())/2; kij=(h.rolling(26).max()+l.rolling(26).min())/2
    a=((ten+kij)/2).shift(26); b=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    price=f(c.iloc[-1]); av=f(a.iloc[-1]); bv=f(b.iloc[-1]); tv=f(ten.iloc[-1]); kv=f(kij.iloc[-1])
    if not av or not bv: return 'unknown', bool(tv>kv) if tv and kv else False
    return ('above_cloud' if price>max(av,bv) else 'below_cloud' if price<min(av,bv) else 'in_cloud'), bool(tv>kv) if tv and kv else False

def keltner_pct(df):
    c=pd.to_numeric(df.close,errors='coerce'); mid=c.ewm(span=20,adjust=False).mean(); atr=atr_series(df,14); up=mid+2*atr; lo=mid-2*atr
    den=f(up.iloc[-1])-f(lo.iloc[-1]); return (f(c.iloc[-1])-f(lo.iloc[-1]))/den if den else 0.5

def score_meta(price, rs, row, hist, ind_until):
    rsi=f(row.get('rsi14'),50); macd=f(row.get('macd')); sig=f(row.get('signal')); mh=f(row.get('histogram'))
    ma20=f(row.get('ma20'),price); ma50=f(row.get('ma50'),ma20); ma200=f(row.get('ma200'),ma50)
    bbp=f(row.get('bbPercent'),0.5); volr=f(row.get('volumeRatio'),1); vwap=f(rs.get('vwapDay'),0)
    sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); zone=rs.get('supportZoneDay') or [sup*0.985,sup*1.015]
    div=_detect_momentum_divergence(ind_until); bullish=bool(div.get('bullish'))
    ist,ib=ichimoku_state(hist); kp=keltner_pct(hist); roc20=(price/f(hist.close.iloc[-21],price)-1)*100 if len(hist)>21 else 0
    score=0
    score += 18 if 38<=rsi<=58 else 12 if 34<=rsi<=65 else 5 if 30<=rsi<=72 else 0
    score += 20 if macd>sig and mh>0 else 14 if mh>=0 else 8 if mh>-0.12 else 3 if mh>-0.25 else 0
    score += 14 if price>=ma20>=ma50 else 10 if price>=ma50 else 7 if price>=ma200 else 4
    score += 12 if 0.12<=bbp<=0.72 else 8 if bbp<0.12 else 4 if bbp<=0.88 else 0
    score += 8 if vwap and price>=vwap else 5 if vwap else 0
    score += 12 if 0.55<=volr<=1.8 else 8 if volr<0.55 else 5 if volr<=2.8 else 0
    score += 10 if ist=='above_cloud' and ib else 7 if ist=='above_cloud' else 5 if ist in ['in_cloud','unknown'] else 2
    score += 8 if 0.12<=kp<=0.75 else 5 if kp<0.12 else 3
    score += 8 if -2<=roc20<=10 else 5 if -8<=roc20< -2 else 3 if roc20>10 else 0
    dist=(price-sup)/price*100 if sup and price else 999
    score += 16 if dist<=2 else 12 if dist<=4 else 8 if dist<=6 else 4 if dist<=8.5 else 0
    score += 8 if bullish else 0
    return {'score':round(score/134*100,2),'dist':round(dist,2),'rsi':r(rsi),'hist':r(mh,4),'bbPercent':r(bbp,3),'volumeRatio':r(volr),'roc20':r(roc20),'support':sup,'supportZone':zone,'ichimoku':ist,'bullishDivergence':bullish}

def trade(df,i,meta,cfg):
    entry=f(df.iloc[i+1].close); low=f(meta['supportZone'][0],meta['support']*0.985)
    stop=max(low*0.98, entry*(1-cfg['maxRisk']/100)); risk=(entry-stop)/entry*100
    if risk<=0 or risk>cfg['maxRisk']: return None
    target=entry*(1+cfg['targetPct']); future=df.iloc[i+2:i+2+HORIZON]
    if future.empty: return None
    outcome='timeout'; exitp=f(future.iloc[-1].close); hold=len(future); exitd=str(future.iloc[-1].time.date())
    for n,(_,row) in enumerate(future.iterrows(),1):
        hit_t=f(row.high)>=target; hit_s=f(row.low)<=stop
        if hit_t and hit_s: outcome='loss'; exitp=stop; hold=n; exitd=str(row.time.date()); break
        if hit_t: outcome='win'; exitp=target; hold=n; exitd=str(row.time.date()); break
        if hit_s: outcome='loss'; exitp=stop; hold=n; exitd=str(row.time.date()); break
    return {'outcome':outcome,'entry':r(entry),'stop':r(stop),'target':r(target),'pnlPct':r((exitp-entry)/entry*100),'riskPct':r(risk),'holdSessions':hold,'exitDate':exitd}

def summ(ts):
    n=len(ts); w=[x for x in ts if x['outcome']=='win']; l=[x for x in ts if x['outcome']=='loss']; to=[x for x in ts if x['outcome']=='timeout']
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
    cutoff=pd.Timestamp(datetime.now()-timedelta(days=LOOKBACK_DAYS)); by_cfg={json.dumps(c,sort_keys=True):[] for c in CONFIGS}; counts={}
    for sym in TECHNICAL_UNIVERSE[SYMBOL_OFFSET:SYMBOL_OFFSET+MAX_SYMBOLS]:
        try:
            df=_load_history(sym)
            if df is None or df.empty or len(df)<160: counts[sym]={'error':'missing/short'}; print(sym,'ERR'); continue
            df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); ind=_compute_indicators(df.copy())
            c={'loops':0,'signals':0}
            for i in range(100,len(df)-HORIZON-2):
                if df.iloc[i].time<cutoff: continue
                c['loops']+=1; hist=df.iloc[:i+1].copy(); row=ind.iloc[i]; price=f(df.iloc[i].close)
                rs=calc_rs_levels_only(price,f(df.iloc[i].open),f(df.iloc[i].open),f(df.iloc[i].high),f(df.iloc[i].low),price,hist)
                meta=score_meta(price,rs,row,hist,ind.iloc[:i+1].copy())
                if meta['rsi']<32 or meta['bbPercent']>0.9 or meta['volumeRatio']>3 or meta['roc20']<-10: continue
                for cfg in CONFIGS:
                    if meta['score']<cfg['minScore'] or meta['dist']>cfg['maxDist']: continue
                    tr=trade(df,i,meta,cfg)
                    if tr:
                        tr.update({'symbol':sym,'date':str(df.iloc[i+1].time.date()),'score':meta['score'],'distSupportPct':meta['dist'],'rsi':meta['rsi'],'ichimoku':meta['ichimoku'],'bullishDivergence':meta['bullishDivergence']})
                        by_cfg[json.dumps(cfg,sort_keys=True)].append(tr); c['signals']+=1
            counts[sym]=c; print(sym,c,flush=True)
        except Exception as e:
            counts[sym]={'error':repr(e)}; print(sym,'ERR',e,flush=True)
    results=[]
    for k,ts in by_cfg.items():
        sm=summ(ts)
        if sm['totalTrades']<10: continue
        cfg=json.loads(k); score=sm['winRatePct']*3+sm['avgPnlPct']*20+min(sm['totalTrades'],100)*0.03+sm['sumPnlPct']/100
        results.append({'config':{'targetPct':round(cfg['targetPct']*100,1),'minScore':cfg['minScore'],'maxDistSupportPct':cfg['maxDist'],'maxRiskPct':cfg['maxRisk']},'score':round(score,2),'summary':sm,'sampleTrades':ts[:100]})
    results.sort(key=lambda x:(x['summary']['winRatePct'],x['summary']['avgPnlPct'],x['summary']['sumPnlPct']),reverse=True)
    balanced=sorted([x for x in results if x['summary']['totalTrades']>=30 and x['summary']['avgPnlPct']>0],key=lambda x:x['score'],reverse=True)
    payload={'createdAt':datetime.now().isoformat(),'sample':'180 ngày gần nhất; TECHNICAL_UNIVERSE batch 2 offset 50, tối đa 50 mã; vào lệnh phiên kế tiếp; horizon 42; không trend, không ADX/DI; bullish divergence chỉ cộng điểm','method':'Exact path focused grid target +6/+7, score/distance/risk tight filters','topWinRate':results[:30],'topBalanced':balanced[:30],'counts':counts}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'bestWinRate':results[0] if results else None,'bestBalanced':balanced[0] if balanced else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
