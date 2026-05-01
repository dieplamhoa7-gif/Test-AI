from __future__ import annotations
import json, statistics
from pathlib import Path
from collections import defaultdict, Counter

SRC=Path('data/v3_target6_partial_at6_exact_future_backtest.json')
OUT=Path('data/v3_prev3m_loser_futurepath_analysis.json')

SECTORS={
 'FPT':'Công nghệ','VTP':'Công nghệ','CTR':'Công nghệ',
 'MWG':'Bán lẻ','PNJ':'Bán lẻ',
 'HPG':'Thép','HSG':'Thép','NKG':'Thép',
 'SSI':'Chứng khoán','VCI':'Chứng khoán','VND':'Chứng khoán','HCM':'Chứng khoán','MBS':'Chứng khoán',
 'TCB':'Ngân hàng','MBB':'Ngân hàng','ACB':'Ngân hàng','CTG':'Ngân hàng','BID':'Ngân hàng','VPB':'Ngân hàng','STB':'Ngân hàng','VIB':'Ngân hàng',
 'VHM':'BĐS','VIC':'BĐS','VRE':'BĐS','KDH':'BĐS','DXG':'BĐS','NVL':'BĐS','KBC':'BĐS KCN','SZC':'BĐS KCN','BCM':'BĐS KCN','GVR':'Cao su/KCN',
 'VNM':'Tiêu dùng','MSN':'Tiêu dùng','SAB':'Tiêu dùng',
 'GAS':'Dầu khí','PLX':'Dầu khí','PVD':'Dầu khí','PVS':'Dầu khí',
 'DGC':'Hóa chất','DCM':'Phân bón','DPM':'Phân bón',
 'DIG':'BĐS','CEO':'BĐS','REE':'Điện/Hạ tầng','PC1':'Điện/Xây lắp','HDG':'BĐS/Năng lượng','KSB':'VLXD','ANV':'Thủy sản','VHC':'Thủy sản'
}

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

def bucket(v,bounds):
    if v is None: return 'NA'
    for label,lo,hi in bounds:
        if lo <= v < hi: return label
    return f'>={bounds[-1][2]}'

def path_features(t):
    entry=f(t.get('entry'))
    fp=t.get('futurePath') or []
    if not entry or not fp:
        return {}
    min_low=min(f(x.get('low'),entry) for x in fp)
    max_high=max(f(x.get('high'),entry) for x in fp)
    min_close=min(f(x.get('close'),entry) for x in fp)
    first_stop=None; first_neg2=None; first_pos3=None; first_break_entry=None
    for idx,x in enumerate(fp,1):
        low=f(x.get('low'),entry); high=f(x.get('high'),entry); close=f(x.get('close'),entry); stop=f(x.get('stop'))
        if first_stop is None and stop is not None and low<=stop: first_stop=idx
        if first_neg2 is None and low <= entry*0.98: first_neg2=idx
        if first_pos3 is None and high >= entry*1.03: first_pos3=idx
        if first_break_entry is None and close < entry: first_break_entry=idx
    return {
        'minDrawdownPct': round((min_low/entry-1)*100,2),
        'maxRunupPct': round((max_high/entry-1)*100,2),
        'minClosePct': round((min_close/entry-1)*100,2),
        'firstStopSession': first_stop,
        'firstMinus2PctSession': first_neg2,
        'firstPlus3PctSession': first_pos3,
        'firstCloseBelowEntrySession': first_break_entry,
        'brokeMinus2Within3': first_neg2 is not None and first_neg2<=3,
        'closedBelowEntryWithin3': first_break_entry is not None and first_break_entry<=3,
        'hadPlus3BeforeStop': first_pos3 is not None and (first_stop is None or first_pos3<first_stop)
    }

def summarize_group(trades):
    return {
        'count':len(trades),
        'avgPnlPct':avg([f(t.get('pnlPct')) for t in trades]),
        'avgScore':avg([f(t.get('score')) for t in trades]),
        'avgDistSupportPct':avg([f(t.get('distSupportPct')) for t in trades]),
        'avgRsi':avg([f(t.get('rsi')) for t in trades]),
        'avgRiskPct':avg([f(t.get('riskPct')) for t in trades]),
        'avgHoldSessions':avg([f(t.get('holdSessions')) for t in trades]),
        'avgMinDrawdownPct':avg([t.get('_feat',{}).get('minDrawdownPct') for t in trades]),
        'avgMaxRunupPct':avg([t.get('_feat',{}).get('maxRunupPct') for t in trades]),
        'quickMinus2Within3Pct':round(sum(1 for t in trades if t.get('_feat',{}).get('brokeMinus2Within3'))/len(trades)*100,2) if trades else 0,
        'closeBelowEntryWithin3Pct':round(sum(1 for t in trades if t.get('_feat',{}).get('closedBelowEntryWithin3'))/len(trades)*100,2) if trades else 0,
        'hadPlus3BeforeStopPct':round(sum(1 for t in trades if t.get('_feat',{}).get('hadPlus3BeforeStop'))/len(trades)*100,2) if trades else 0,
    }

def main():
    data=json.load(open(SRC,encoding='utf-8'))
    results=data['results']
    analysis={}
    for mode in ['none','loose','strict']:
        trades=results[mode]['prev3m']['trades']
        for t in trades:
            t['_sector']=SECTORS.get(t.get('symbol'),'Khác')
            t['_feat']=path_features(t)
        losers=[t for t in trades if f(t.get('pnlPct'),0)<0]
        winners=[t for t in trades if f(t.get('pnlPct'),0)>0]
        by_sector=defaultdict(list); by_symbol=defaultdict(list); by_group=defaultdict(list)
        for t in losers:
            by_sector[t['_sector']].append(t); by_symbol[t['symbol']].append(t)
            sec=t['_sector']
            if sec in ('Ngân hàng','Chứng khoán','Thép','BĐS','BĐS KCN','Cao su/KCN'):
                by_group[sec].append(t)
        score_b=Counter(bucket(f(t.get('score')), [('68-70',68,70),('70-75',70,75),('75-80',75,80),('80+',80,999)]) for t in losers)
        dist_b=Counter(bucket(f(t.get('distSupportPct')), [('0-1',0,1),('1-2',1,2),('2-3',2,3),('3+',3,999)]) for t in losers)
        rsi_b=Counter(bucket(f(t.get('rsi')), [('32-40',32,40),('40-50',40,50),('50-60',50,60),('60+',60,999)]) for t in losers)
        runup_b=Counter(bucket(t['_feat'].get('maxRunupPct'), [('<0',-999,0),('0-2',0,2),('2-4',2,4),('4-6',4,6),('6+',6,999)]) for t in losers)
        analysis[mode]={
            'summary':results[mode]['prev3m']['summary'],
            'losers':summarize_group(losers),
            'winners':summarize_group(winners),
            'sectorLosers':{k:summarize_group(v) for k,v in sorted(by_sector.items(), key=lambda kv: len(kv[1]), reverse=True)},
            'symbolLosers':{k:summarize_group(v) for k,v in sorted(by_symbol.items(), key=lambda kv: len(kv[1]), reverse=True)},
            'focusGroupLosers':{k:summarize_group(v) for k,v in by_group.items()},
            'loserBuckets':{
                'score':dict(score_b),'distSupportPct':dict(dist_b),'rsi':dict(rsi_b),'maxRunupPctBeforeLoss':dict(runup_b)
            },
            'worstLosers':[ {k:t.get(k) for k in ['symbol','date','_sector','pnlPct','score','distSupportPct','rsi','riskPct','holdSessions','entry','stopInitial']} | {'features':t['_feat']} for t in sorted(losers,key=lambda x:f(x.get('pnlPct'),0))[:20] ],
            'quickBreakLosers':[ {k:t.get(k) for k in ['symbol','date','_sector','pnlPct','score','distSupportPct','rsi','riskPct','holdSessions']} | {'features':t['_feat']} for t in losers if t['_feat'].get('brokeMinus2Within3') ][:30]
        }
    # candidate lessons based on none + loose primarily
    payload={'source':str(SRC),'createdAt':__import__('datetime').datetime.now().isoformat(),'analysis':analysis,
             'notes':'Focus on prev3m losing trades using saved futurePath. Fields volumeRatio/ROC/BB are not persisted in trade records; next backtest should persist full score_meta components if deeper component attribution is needed.'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'modes':{m:{'summary':analysis[m]['summary'],'losers':analysis[m]['losers'],'topSectorLosers':list(analysis[m]['sectorLosers'].items())[:5],'buckets':analysis[m]['loserBuckets']} for m in analysis}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
