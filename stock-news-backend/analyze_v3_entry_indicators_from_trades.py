from __future__ import annotations
import json, statistics
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

SRC=Path('data/v3_target6_partial_at6_exact_future_backtest.json')
OUT=Path('data/v3_entry_indicator_analysis.json')

def f(v,d=None):
    try:
        if v is None: return d
        return float(v)
    except Exception: return d

def avg(xs):
    xs=[x for x in xs if x is not None]
    return round(sum(xs)/len(xs),3) if xs else None

def med(xs):
    xs=[x for x in xs if x is not None]
    return round(statistics.median(xs),3) if xs else None

def pct(part,total): return round(part/total*100,2) if total else 0

def bucket(v,bounds):
    if v is None: return 'NA'
    for label,lo,hi in bounds:
        if lo <= v < hi: return label
    return f'>={bounds[-1][2]}'

def summarize(ts):
    n=len(ts); w=[t for t in ts if f(t.get('pnlPct'),0)>0]; l=[t for t in ts if f(t.get('pnlPct'),0)<0]
    return {'n':n,'winRatePct':pct(len(w),n),'avgPnlPct':avg([f(t.get('pnlPct')) for t in ts]),'sumPnlPct':round(sum(f(t.get('pnlPct'),0) for t in ts),2),'avgScore':avg([f(t.get('score')) for t in ts]),'avgDistSupportPct':avg([f(t.get('distSupportPct')) for t in ts]),'avgRsi':avg([f(t.get('rsi')) for t in ts]),'avgHist':avg([f(t.get('hist')) for t in ts]),'avgBbPercent':avg([f(t.get('bbPercent')) for t in ts]),'avgVolumeRatio':avg([f(t.get('volumeRatio')) for t in ts]),'avgRoc20':avg([f(t.get('roc20')) for t in ts])}

def split_bucket(trades, field, bounds):
    g=defaultdict(list)
    for t in trades: g[bucket(f(t.get(field)),bounds)].append(t)
    return {k:summarize(v) for k,v in sorted(g.items())}

def split_bool(trades, field):
    g=defaultdict(list)
    for t in trades: g[str(bool(t.get(field)))].append(t)
    return {k:summarize(v) for k,v in sorted(g.items())}

def split_cat(trades, field):
    g=defaultdict(list)
    for t in trades: g[str(t.get(field))].append(t)
    return {k:summarize(v) for k,v in sorted(g.items(), key=lambda kv: len(kv[1]), reverse=True)}

def compare_win_loss(trades):
    w=[t for t in trades if f(t.get('pnlPct'),0)>0]; l=[t for t in trades if f(t.get('pnlPct'),0)<0]
    fields=['score','distSupportPct','rsi','hist','bbPercent','volumeRatio','roc20','riskPct','holdSessions']
    return {field:{'winnerAvg':avg([f(t.get(field)) for t in w]),'loserAvg':avg([f(t.get(field)) for t in l]),'winnerMedian':med([f(t.get(field)) for t in w]),'loserMedian':med([f(t.get(field)) for t in l])} for field in fields}

def indicator_report(trades):
    return {
        'summary':summarize(trades),
        'winLossCompare':compare_win_loss(trades),
        'byScore':split_bucket(trades,'score',[('68-72',68,72),('72-76',72,76),('76-80',76,80),('80-85',80,85),('85+',85,999)]),
        'byDistSupportPct':split_bucket(trades,'distSupportPct',[('0-1',0,1),('1-2',1,2),('2-2.5',2,2.5),('2.5-3',2.5,3),('3+',3,999)]),
        'byRsi':split_bucket(trades,'rsi',[('<=40',-999,40),('40-45',40,45),('45-50',45,50),('50-55',50,55),('55-60',55,60),('60+',60,999)]),
        'byMacdHist':split_bucket(trades,'hist',[('<-0.25',-999,-0.25),('-0.25--0.12',-0.25,-0.12),('-0.12-0',-0.12,0),('0-0.12',0,0.12),('0.12+',0.12,999)]),
        'byBbPercent':split_bucket(trades,'bbPercent',[('<0.12',-999,0.12),('0.12-0.35',0.12,0.35),('0.35-0.55',0.35,0.55),('0.55-0.72',0.55,0.72),('0.72-0.9',0.72,0.9),('0.9+',0.9,999)]),
        'byVolumeRatio':split_bucket(trades,'volumeRatio',[('<0.55',-999,0.55),('0.55-1',0.55,1),('1-1.8',1,1.8),('1.8-2.8',1.8,2.8),('2.8+',2.8,999)]),
        'byRoc20':split_bucket(trades,'roc20',[('<-8',-999,-8),('-8--2',-8,-2),('-2-0',-2,0),('0-5',0,5),('5-10',5,10),('10+',10,999)]),
        'byIchimoku':split_cat(trades,'ichimoku'),
        'byBullishDivergence':split_bool(trades,'bullishDivergence'),
    }

def main():
    data=json.load(open(SRC,encoding='utf-8'))
    results={}
    for mode in ['none','loose','strict']:
        results[mode]={}
        for win in ['current180','prev3m']:
            trades=data['results'][mode][win]['trades']
            results[mode][win]=indicator_report(trades)
    payload={'createdAt':datetime.now().isoformat(),'source':str(SRC),'note':'Analyzes entry indicators persisted in exact future-path trades: score, distSupportPct, RSI, MACD hist, BB percent, volume ratio, ROC20, Ichimoku, bullish divergence. Does not include ADX/DI/full component because they were not persisted in this backtest.', 'results':results}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={m:{w:{'summary':results[m][w]['summary'],'winLossCompare':results[m][w]['winLossCompare'],'byDistSupportPct':results[m][w]['byDistSupportPct'],'byRsi':results[m][w]['byRsi'],'byBbPercent':results[m][w]['byBbPercent'],'byVolumeRatio':results[m][w]['byVolumeRatio'],'byRoc20':results[m][w]['byRoc20'],'byIchimoku':results[m][w]['byIchimoku']} for w in results[m]} for m in results}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
