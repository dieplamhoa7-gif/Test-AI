from __future__ import annotations
import json, sys, datetime as dt
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parent
HIST=ROOT / 'data/vn100_history_2025_06_2026_05_cache.json'
OUT=ROOT / 'data/sr_levels_major_selected.json'
# reuse practical builder internals
spec=importlib.util.spec_from_file_location('pr', ROOT / 'build_sr_levels_practical_selected.py')
pr=importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
SYMS=sys.argv[1:] or ['MWG','FPT','VPB','VCI','SSI','MSN']

def select_major(levels, price, min_pct=0.055, n=4):
    min_gap=price*min_pct
    selected=[]
    for lv in sorted(levels,key=lambda x:abs(x['center']-price)):
        if all(abs(lv['center']-s['center'])>=min_gap for s in selected):
            selected.append(lv)
        else:
            for i,s in enumerate(selected):
                if abs(lv['center']-s['center'])<min_gap and lv['strength']>s['strength']*1.25:
                    selected[i]=lv
                    break
    return sorted(selected,key=lambda x:abs(x['center']-price))[:n]

def analyze_major(sym, rows):
    base=pr.analyze(sym, rows)
    price=base['close']
    # recompute all tight clusters, then pick major supports/resistances with 5.5% gap.
    import pandas as pd
    df=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
    for col in ['open','high','low','close','volume']: df[col]=pd.to_numeric(df[col],errors='coerce')
    atrv=float(pr.atr(df).iloc[-1]); cls=pr.cluster(pr.points(df), price, atrv)
    current=base.get('currentZone',[])[:1]
    cur_centers=[c['center'] for c in current]
    # major S/R must be outside current zone and not within 1% of close, otherwise it is just noise/current handling.
    supports=[c for c in cls if c['center'] < price*0.99 and all(abs(c['center']-cc)>price*0.025 for cc in cur_centers)]
    resistances=[c for c in cls if c['center'] > price*1.01 and all(abs(c['center']-cc)>price*0.025 for cc in cur_centers)]
    base['minorSupports']=base.get('supports',[])
    base['minorResistances']=base.get('resistances',[])
    base['supports']=select_major(supports,price,0.055)
    base['resistances']=select_major(resistances,price,0.055)
    base['majorGapPct']=5.5
    return base

def main():
    data=json.load(open(HIST,encoding='utf-8'))['symbols']
    items=[]
    for sym in SYMS: items.append(analyze_major(sym,data[sym]['rows']) if sym in data else {'symbol':sym,'error':'missing'})
    payload={'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'source':str(HIST),'method':'Major practical S/R: narrow actionable zones, but displayed S/R levels separated by >=5.5% of price. Minor levels retained as minorSupports/minorResistances.','items':items}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
