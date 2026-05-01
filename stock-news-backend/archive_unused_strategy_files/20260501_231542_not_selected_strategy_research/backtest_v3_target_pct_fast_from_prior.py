from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

IN=Path('data/v3_no_trend_no_adx_bullish_div_backtest.json')
OUT=Path('data/v3_target_pct_fast_grid_from_prior.json')
TARGETS=[6,7]
MIN_SCORES=[55,58,60,62,65,68,70,72,75,78]
MAX_DIST=[3,4,5,6,7.5,8.5]
MAX_RISK=[4,5,6,7,8,9,10]

def f(v,d=0.0):
    try: return float(v) if v is not None else d
    except Exception: return d

def summ(ts):
    n=len(ts); w=[x for x in ts if x['outcome']=='win']; l=[x for x in ts if x['outcome']=='loss']; to=[x for x in ts if x['outcome']=='timeout']
    avg=lambda xs,k: round(sum(f(x[k]) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x[k]) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def convert_trade_3r_to_pct(t,target_pct):
    # Approximation from saved 3R trade path unavailable: if 3R target hit, assume +target%; if stop hit, same stop; timeout cap by original timeout pnl.
    nt=dict(t); nt['targetPct']=target_pct
    if t['outcome']=='win':
        nt['pnlPct']=target_pct; nt['outcome']='win'
    elif t['outcome']=='loss':
        nt['pnlPct']=t['pnlPct']; nt['outcome']='loss'
    else:
        # timeout: if original timeout pnl >= target then count as target win; else keep timeout pnl.
        if f(t.get('pnlPct'))>=target_pct:
            nt['pnlPct']=target_pct; nt['outcome']='win'
        else:
            nt['pnlPct']=t.get('pnlPct'); nt['outcome']='timeout'
    return nt

def main():
    d=json.load(open(IN,encoding='utf-8')); base=d.get('trades') or []
    results=[]
    for target in TARGETS:
      converted=[convert_trade_3r_to_pct(t,target) for t in base]
      for ms in MIN_SCORES:
       for md in MAX_DIST:
        for mr in MAX_RISK:
         ts=[t for t in converted if f(t.get('score'))>=ms and f(t.get('distSupportPct'))<=md and f(t.get('riskPct'))<=mr]
         sm=summ(ts)
         if sm['totalTrades']<20: continue
         score=sm['winRatePct']*3 + sm['avgPnlPct']*20 + min(sm['totalTrades'],300)*0.02 + sm['sumPnlPct']/100
         results.append({'config':{'targetPct':target,'minScore':ms,'maxDistSupportPct':md,'maxRiskPct':mr},'score':round(score,2),'summary':sm,'sampleTrades':ts[:100]})
    results.sort(key=lambda r:(r['summary']['winRatePct'],r['summary']['avgPnlPct'],r['summary']['sumPnlPct']),reverse=True)
    # also best balanced with positive sum and enough trades
    balanced=sorted([r for r in results if r['summary']['avgPnlPct']>0 and r['summary']['totalTrades']>=50],key=lambda r:r['score'],reverse=True)
    payload={'createdAt':datetime.now().isoformat(),'method':'Fast grid approximation from prior 3R trades: target converted to +6/+7 where path detail unavailable. Use for direction only; exact path backtest should be separate optimized stage.','source':str(IN),'topWinRate':results[:30],'topBalanced':balanced[:30]}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'bestWinRate':results[0] if results else None,'bestBalanced':balanced[0] if balanced else None},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
