from __future__ import annotations
import json, importlib.util
from pathlib import Path
from datetime import datetime

SRC=Path('data/v3_target6_market_ex_vic_vhm_partial_exit_backtest.json')
OUT=Path('data/v3_target6_market_ex_vic_vhm_partial_at6_backtest.json')

# Exact recompute from saved trade path is not possible from partial_exit output because future candles were not persisted.
# This file documents corrected exit assumption and converts existing baseline exact +6 trades where available.
BASE=Path('data/v3_target_pct_exact_focused_backtest.json')
PREV=Path('data/v3_target_pct_exact_prev3m_backtest.json')

def f(v,d=0.0):
    try: return float(v) if v is not None else d
    except Exception: return d

def summ(ts):
    n=len(ts); wins=[x for x in ts if f(x.get('pnlPct'))>0]; losses=[x for x in ts if f(x.get('pnlPct'))<0]; flats=[x for x in ts if f(x.get('pnlPct'))==0]
    avg=lambda xs,k: round(sum(f(x.get(k)) for x in xs)/len(xs),2) if xs else 0
    sm=lambda xs,k: round(sum(f(x.get(k)) for x in xs),2) if xs else 0
    return {'totalTrades':n,'wins':len(wins),'losses':len(losses),'flats':len(flats),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'avgWinPct':avg(wins,'pnlPct'),'avgLossPct':avg(losses,'pnlPct'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def load(path):
    return json.load(open(path,encoding='utf-8')) if path.exists() else {}

def convert_exact_win_to_partial_at6(trades):
    # If exact +6 target is hit, corrected partial-at-6 would realize at least +3% on 50% and trail the rest.
    # Without future candles after +6, use conservative approximation:
    # - win => +3% locked on half + remaining marked as original full +6 target = +6% if no trailing info.
    # - loss/timeout unchanged.
    out=[]
    for t in trades:
        x=dict(t)
        if f(x.get('pnlPct'))>=5.99 or x.get('outcome')=='win':
            x['pnlPct']=6.0
            x['outcome']='win_partial_at6_approx'
            x['partialAt6Pct']=50
        out.append(x)
    return out

def main():
    base=load(BASE); prev=load(PREV)
    # Extract top config trades from focused file if available; fallback to all trades in prev exact.
    top=(base.get('topWinRate') or [])
    cur_trades=(top[0].get('sampleTrades') if top else []) or []
    prev_trades=prev.get('trades') or []
    cur=convert_exact_win_to_partial_at6(cur_trades)
    prv=convert_exact_win_to_partial_at6(prev_trades)
    payload={'createdAt':datetime.now().isoformat(),'method':'Corrected assumption requested by user: take profit 50% at +6%, not +3%; remaining position trails only after +6. This summary uses existing exact +6 outputs as conservative approximation because future candles were not persisted in previous files. Exact recompute should be separate if needed.','currentApprox':{'source':str(BASE),'summary':summ(cur),'trades':cur},'prev3mApprox':{'source':str(PREV),'summary':summ(prv),'trades':prv},'note':'For exact partial-at-6, next script must persist future path per trade and evaluate trailing after +6.'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'currentApprox':payload['currentApprox']['summary'],'prev3mApprox':payload['prev3mApprox']['summary']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
