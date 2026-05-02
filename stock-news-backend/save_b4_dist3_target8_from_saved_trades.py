from __future__ import annotations
import json
from pathlib import Path

BASE=Path('data/b4_trend_pullback_insample4m_oos20_backtest.json')
OUT=Path('data/b4_trend_pullback_dist3_target8_from_saved_trades.json')
d=json.loads(BASE.read_text(encoding='utf-8'))
trades=d['insample4m']['trades']

def simulate(t,target_pct=8):
    entry=t['entry']; target=entry*(1+target_pct/100); stop=entry*0.94
    size=1.0; realized=0.0; half=False; peak=entry; hold=0; outcome='timeout'; exitDate=t.get('exitDate')
    for n,row in enumerate(t.get('futurePath') or [],1):
        high=float(row.get('high') or 0); low=float(row.get('low') or 0); close=float(row.get('close') or 0)
        peak=max(peak,high); hold=n; exitDate=row.get('date')
        if (not half) and high>=target:
            realized += 0.5*target_pct; size=0.5; half=True; stop=max(entry*1.005, peak*0.97)
        if half: stop=max(stop, entry*1.005, peak*0.97)
        if low<=stop:
            realized += size*((stop-entry)/entry*100); size=0; outcome='win' if realized>0 else 'loss'; break
    if size>0 and t.get('futurePath'):
        last=float(t['futurePath'][-1].get('close') or entry)
        realized += size*((last-entry)/entry*100); outcome='win' if realized>0 else 'loss' if realized<0 else 'flat'
    x=dict(t); x.update({'targetPct':target_pct,'target':round(target,2),'stopInitial':round(entry*0.94,2),'pnlPct':round(realized,2),'outcome':outcome,'partialTaken':half,'holdSessions':hold,'exitDate':exitDate})
    return x

def summary(rows):
    wins=[x for x in rows if x['pnlPct']>0]; losses=[x for x in rows if x['pnlPct']<0]
    return {'totalTrades':len(rows),'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/len(rows)*100,2) if rows else 0,'avgPnlPct':round(sum(x['pnlPct'] for x in rows)/len(rows),2) if rows else 0,'sumPnlPct':round(sum(x['pnlPct'] for x in rows),2),'avgWinPct':round(sum(x['pnlPct'] for x in wins)/len(wins),2) if wins else 0,'avgLossPct':round(sum(x['pnlPct'] for x in losses)/len(losses),2) if losses else 0,'avgHoldSessions':round(sum(x['holdSessions'] for x in rows)/len(rows),2) if rows else 0}
rows=[simulate(t,8) for t in trades]
payload={'createdAt':d.get('createdAt'),'name':'Trend Pullback Pro dist<=3 target8 from saved trades','source':str(BASE),'entryFilter':'distSupport <= 3% locked B4 trades','exit':{'targetPct':8,'takeProfitAtTargetPct':50,'trailingAfterTarget':'max(entry+0.5%, peak-3%)','stopPct':6},'summary':summary(rows),'trades':rows}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'summary':payload['summary'],'trades':[(x['symbol'],x['signalDate'],x['pnlPct']) for x in rows]},ensure_ascii=False,indent=2))
