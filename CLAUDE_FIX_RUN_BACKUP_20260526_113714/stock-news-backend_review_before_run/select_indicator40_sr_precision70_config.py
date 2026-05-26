from __future__ import annotations
import json, datetime as dt
from pathlib import Path
CHK=Path('stock-news-backend/data/indicator40_sr_sector_ml_checkpoint.jsonl')
RESEARCH=Path('stock-news-backend/data/indicator40_sr_sector_ml_research.json')
OUT=Path('stock-news-backend/data/indicator40_sr_precision70_config.json')

def load_runs():
    runs=[]
    if CHK.exists():
        for line in CHK.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r=json.loads(line)
                if not r.get('error'): runs.append(r)
    # include topBySectorTask from research, because it may contain finalized top records beyond checkpoint view
    if RESEARCH.exists():
        j=json.load(open(RESEARCH,encoding='utf-8'))
        for tasks in j.get('topBySectorTask',{}).values():
            for arr in tasks.values():
                for r in arr:
                    if not r.get('error'): runs.append(r)
    # de-dupe by full key; keep better avgPrecision version if duplicated
    by={}
    for r in runs:
        k=(r['sectorGroup'],r['task'],r['group'],r['model'],r['mode'])
        if k not in by or (r.get('avgPrecision',0),r.get('minPrecision',0),r.get('avgF1',0))>(by[k].get('avgPrecision',0),by[k].get('minPrecision',0),by[k].get('avgF1',0)):
            by[k]=r
    return list(by.values())

def precision_rank(r):
    # Hòa preference: avg precision > 70, but avoid totally meaningless one-signal configs when possible.
    preds=[sp['oosStats']['predN'] for sp in r.get('splits',[])]
    pred_total=sum(preds)
    min_pred=min(preds) if preds else 0
    stable_bonus=min(r.get('minPrecision',0),70)*1.2 + min_pred*1.5 + min(pred_total,20)*0.5
    return r.get('avgPrecision',0)*4 + r.get('minPrecision',0)*2 + r.get('avgF1',0)*.7 + r.get('avgRecall',0)*.2 + stable_bonus

def main():
    runs=load_runs()
    candidates=[]
    relaxed=[]
    for r in runs:
        if r.get('avgPrecision',0)>=70:
            candidates.append(r)
        elif r.get('avgPrecision',0)>=60 and r.get('minPrecision',0)>=50:
            relaxed.append(r)
    by={}
    for r in sorted(candidates,key=precision_rank,reverse=True):
        by.setdefault(r['sectorGroup'],{}).setdefault(r['task'],r)
    relaxed_by={}
    for r in sorted(relaxed,key=precision_rank,reverse=True):
        relaxed_by.setdefault(r['sectorGroup'],{}).setdefault(r['task'],r)
    payload={
      'createdAt':dt.datetime.now().isoformat(timespec='seconds'),
      'selectionPolicy':'Precision-first. Primary target avgPrecision >=70%. Recall may be low. Prefer minPrecision >=50% and non-trivial OOS predN.',
      'primaryCount':len(candidates),
      'relaxedCount':len(relaxed),
      'selectedPrecision70':by,
      'selectedRelaxed60IfNo70':relaxed_by,
      'allPrecision70':sorted(candidates,key=precision_rank,reverse=True)[:50]
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'out':str(OUT),'primaryCount':len(candidates),'relaxedCount':len(relaxed),'selectedPrecision70':{s:{t:{k:v for k,v in r.items() if k in ['sectorGroup','task','group','model','mode','avgPrecision','minPrecision','avgRecall','avgF1','minF1']} for t,r in tasks.items()} for s,tasks in by.items()},'selectedRelaxed60IfNo70':{s:{t:{k:v for k,v in r.items() if k in ['sectorGroup','task','group','model','mode','avgPrecision','minPrecision','avgRecall','avgF1','minF1']} for t,r in tasks.items()} for s,tasks in relaxed_by.items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
