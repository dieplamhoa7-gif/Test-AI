from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

p=Path('data/strategy_results_cache.json')
d=json.loads(p.read_text(encoding='utf-8'))
for s in d.get('strategies',[]):
    if s.get('id')=='b4_trend_pullback':
        s['note']='Trend Pullback Pro upgraded to target +8% from saved in-sample 4m target8 table.'
        s['targetPct']=8
        s['targetSource']='data/b4_trend_pullback_dist3_target8_from_saved_trades.json'
        for bucket in ('buy','watchlist'):
            for x in s.get(bucket,[]):
                e=x.get('entryPrice') or x.get('support') or x.get('lastClose')
                if e:
                    x['targetPct']=8
                    x['takeProfit']=round(float(e)*1.08,2)
                    x['stopPct']=6
                    x['stopLoss']=round(float(e)*0.94,2)
                    x['reason']=(x.get('reason') or '') + ' Target web: +8% từ điểm mua.'
d['updatedAt']=datetime.now().isoformat()
d['note']='Current strategy signal cache: Trend Pullback Pro target upgraded to +8% from saved canonical target8 table; web reads output only.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'updatedAt':d['updatedAt'],'b4':[(x.get('symbol'),x.get('entryPrice'),x.get('takeProfit'),x.get('stopLoss'),x.get('targetPct')) for s in d['strategies'] if s.get('id')=='b4_trend_pullback' for x in s.get('watchlist',[])]},ensure_ascii=False,indent=2))
