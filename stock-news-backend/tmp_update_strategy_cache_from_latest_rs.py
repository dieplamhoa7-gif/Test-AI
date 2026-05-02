from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

rs_path=Path('data/rs_levels_only_cache.json')
cache_path=Path('data/strategy_results_cache.json')
rs=json.loads(rs_path.read_text(encoding='utf-8'))
rs_by={x['symbol']:x for x in rs.get('items',[])}
d=json.loads(cache_path.read_text(encoding='utf-8'))
updated=[]
for strat in d.get('strategies',[]):
    for bucket in ('buy','watchlist'):
        for x in strat.get(bucket,[]):
            sym=x.get('symbol')
            r=rs_by.get(sym)
            if not r: continue
            old_entry=x.get('entryPrice')
            entry=float(r.get('activeSupportDay') or r.get('supportDay') or old_entry or 0)
            if entry<=0: continue
            x['entryPrice']=round(entry,2)
            x['support']=round(entry,2)
            x['resistance']=round(float(r.get('activeResistanceDay') or r.get('resistanceDay') or x.get('resistance') or 0),2)
            x['rsSnapshot']={
                'supportZoneDay':r.get('supportZoneDay'),
                'resistanceZoneDay':r.get('resistanceZoneDay'),
                'activeSupportDay':r.get('activeSupportDay'),
                'activeResistanceDay':r.get('activeResistanceDay'),
                'rsDate':r.get('date'),
            }
            tp=float(x.get('targetPct') or 0)
            sp=float(x.get('stopPct') or 0)
            if tp: x['takeProfit']=round(entry*(1+tp/100),2)
            if sp: x['stopLoss']=round(entry*(1-sp/100),2)
            last=float(x.get('lastClose') or r.get('price') or 0)
            x['lastClose']=round(float(r.get('price') or last),2)
            if last: x['gapToEntryPct']=round((last/entry-1)*100,2)
            x['asOfDate']=r.get('date') or x.get('asOfDate')
            updated.append({'symbol':sym,'oldEntry':old_entry,'newEntry':x['entryPrice'],'target':x.get('takeProfit'),'stop':x.get('stopLoss'),'price':x.get('lastClose')})
d['updatedAt']=datetime.now().isoformat()
d['rsCacheSource']='data/rs_levels_only_cache.json'
d['rsCacheCreatedAt']=rs.get('createdAt')
d['note']='Current strategy signal cache refreshed with latest R/S-only cache; web reads output only.'
cache_path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'updatedCount':len(updated),'updated':updated},ensure_ascii=False,indent=2))
