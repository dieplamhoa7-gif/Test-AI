from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

SRC=Path('data/v3_clean_split_rs_action_relaxed_a2_b2_backtest.json')
OUT=Path('data/v3_clean_split_indicator_filter_optimization.json')

def f(v,d=None):
    try:
        if v is None: return d
        return float(v)
    except Exception: return d

def summ(ts):
    n=len(ts); w=[t for t in ts if f(t.get('pnlPct'),0)>0]; l=[t for t in ts if f(t.get('pnlPct'),0)<0]
    avg=lambda xs,k: round(sum(f(x.get(k),0) for x in xs)/len(xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':round(sum(f(t.get('pnlPct'),0) for t in ts),2),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def ind(t,k,d=None):
    ai=t.get('entryIndicators') or {}
    if k.startswith('ichimoku.'):
        return (ai.get('ichimoku') or {}).get(k.split('.',1)[1])
    return ai.get(k,d)

def passes(t,cfg):
    ai=t.get('entryIndicators') or {}
    rsi=f(ai.get('rsi'),999); bb=f(ai.get('bbPercent'),999); vol=f(ai.get('volumeRatio'),999); roc=f(ai.get('roc20'),0); mh=f(ai.get('macdHist'),0); dist=f(t.get('distSupportPct'),999)
    ichi=(ai.get('ichimoku') or {}).get('state')
    if cfg.get('requireAboveCloud') and ichi!='above_cloud': return False
    if dist>cfg.get('maxDist',999): return False
    if rsi<cfg.get('minRsi',-999) or rsi>cfg.get('maxRsi',999): return False
    if bb<cfg.get('minBb',-999) or bb>cfg.get('maxBb',999): return False
    if vol<cfg.get('minVol',-999) or vol>cfg.get('maxVol',999): return False
    if roc<cfg.get('minRoc',-999) or roc>cfg.get('maxRoc',999): return False
    if mh<cfg.get('minMacdHist',-999): return False
    if cfg.get('requireMacdImproving') and not ai.get('macdHistImproving'): return False
    if cfg.get('noBearishDiv') and ai.get('bearishDivergence'): return False
    return True

def analyze_bad(trades):
    winners=[t for t in trades if f(t.get('pnlPct'),0)>0]; losers=[t for t in trades if f(t.get('pnlPct'),0)<0]
    fields=['rsi','bbPercent','volumeRatio','roc20','macdHist']
    out={}
    for k in fields:
        out[k]={'winnerAvg':round(sum(f(ind(t,k),0) for t in winners)/len(winners),3) if winners else None,'loserAvg':round(sum(f(ind(t,k),0) for t in losers)/len(losers),3) if losers else None}
    out['ichimokuStateLosers']={}
    for t in losers:
        s=ind(t,'ichimoku.state','NA'); out['ichimokuStateLosers'][s]=out['ichimokuStateLosers'].get(s,0)+1
    return out

def grid_A2(base):
    configs=[]
    for maxDist in [1.5,2.0,2.2,2.5]:
      for maxRsi in [40,42,45]:
       for maxBb in [0.35,0.45,0.55]:
        for maxVol in [1.8,2.2,2.5]:
         for minMh in [-0.08,-0.05,0.0]:
          configs.append({'name':'A2_refined','maxDist':maxDist,'minRsi':-999,'maxRsi':maxRsi,'minBb':-999,'maxBb':maxBb,'minVol':0.55,'maxVol':maxVol,'minRoc':-12,'maxRoc':999,'minMacdHist':minMh,'noBearishDiv':True})
    return configs

def grid_B2(base):
    configs=[]
    for maxDist in [2.0,2.5,2.8,3.0]:
     for minRsi,maxRsi in [(48,55),(50,55),(50,58),(52,60),(48,62)]:
      for maxBb in [0.65,0.75,0.85,0.9]:
       for minVol,maxVol in [(0.55,1.8),(0.7,1.8),(0.55,2.2),(0.7,2.5)]:
        for minRoc,maxRoc in [(-5,10),(-8,12),(-8,15),(0,12)]:
         for minMh in [-0.05,0.0]:
          configs.append({'name':'B2_refined','requireAboveCloud':True,'maxDist':maxDist,'minRsi':minRsi,'maxRsi':maxRsi,'minBb':-999,'maxBb':maxBb,'minVol':minVol,'maxVol':maxVol,'minRoc':minRoc,'maxRoc':maxRoc,'minMacdHist':minMh,'noBearishDiv':True})
    return configs

def optimize(trades, configs, min_current=8, min_oos=0):
    rows=[]
    for cfg in configs:
        cur=[t for t in trades['current180'] if passes(t,cfg)]
        oos=[t for t in trades['prev3m'] if passes(t,cfg)]
        sc=summ(cur); so=summ(oos)
        if sc['totalTrades']<min_current or so['totalTrades']<min_oos: continue
        # prefer OOS not terrible, current strong, enough trades
        score=sc['sumPnlPct'] + max(so['sumPnlPct'], -20)*2 + sc['winRatePct']*0.8 + so['winRatePct']*0.6 + min(sc['totalTrades'],50)*1.2 + min(so['totalTrades'],50)*0.6
        if so['sumPnlPct']>=0: score+=30
        rows.append({'score':round(score,2),'config':cfg,'current180':sc,'prev3m':so})
    rows.sort(key=lambda x:(x['score'],x['prev3m']['sumPnlPct'],x['current180']['sumPnlPct'],x['current180']['totalTrades']),reverse=True)
    return rows[:50]

def main():
    data=json.load(open(SRC,encoding='utf-8'))['windows']
    # use target6_half for B2, target10_full and target6 for A2
    sets={
      'A2_target6':{'current180':data['current180']['results']['A2_oversold_near_support_relaxed']['target6_half_trail_stop6']['trades'],'prev3m':data['prev3m']['results']['A2_oversold_near_support_relaxed']['target6_half_trail_stop6']['trades']},
      'A2_target10_full':{'current180':data['current180']['results']['A2_oversold_near_support_relaxed']['target10_full_stop6']['trades'],'prev3m':data['prev3m']['results']['A2_oversold_near_support_relaxed']['target10_full_stop6']['trades']},
      'B2_target6':{'current180':data['current180']['results']['B2_confirmed_rebound_above_cloud_relaxed']['target6_half_trail_stop6']['trades'],'prev3m':data['prev3m']['results']['B2_confirmed_rebound_above_cloud_relaxed']['target6_half_trail_stop6']['trades']},
      'B2_target10_full':{'current180':data['current180']['results']['B2_confirmed_rebound_above_cloud_relaxed']['target10_full_stop6']['trades'],'prev3m':data['prev3m']['results']['B2_confirmed_rebound_above_cloud_relaxed']['target10_full_stop6']['trades']},
    }
    result={}
    for name,tr in sets.items():
        cfgs=grid_A2(tr) if name.startswith('A2') else grid_B2(tr)
        result[name]={'base':{'current180':summ(tr['current180']),'prev3m':summ(tr['prev3m']),'indicatorBadness':{'current180':analyze_bad(tr['current180']),'prev3m':analyze_bad(tr['prev3m'])}},'topRefined':optimize(tr,cfgs,min_current=5 if name.startswith('A2') else 10,min_oos=0)}
    payload={'createdAt':datetime.now().isoformat(),'source':str(SRC),'method':'Analyze weak indicators and lower/demote noisy indicator ranges via filter grid over saved clean-split trades. R/S indicators remain hard filters only.','results':result}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={k:{'base':v['base'],'top5':v['topRefined'][:5]} for k,v in result.items()}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
