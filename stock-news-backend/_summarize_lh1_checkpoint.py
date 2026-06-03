import json
from pathlib import Path
from collections import defaultdict

p = Path('data/lh1_canonical_t3_fee_2023_to_now.checkpoint.json')
o = json.loads(p.read_text(encoding='utf-8'))
print('done_symbols', len(o.get('counts', {})))
print('total_trades', len(o.get('trades', [])))
print('windows', json.dumps(o.get('windows', {}), ensure_ascii=False))
by = defaultdict(list)
for t in o.get('trades', []):
    by[t['symbol']].append(t)
for s, ts in by.items():
    wins = sum(1 for t in ts if float(t.get('netPnlPct', 0) or 0) > 0)
    avg = sum(float(t.get('netPnlPct', 0) or 0) for t in ts) / len(ts)
    sm = sum(float(t.get('netPnlPct', 0) or 0) for t in ts)
    print('symbol', s, 'trades', len(ts), 'wins', wins, 'winrate', round(wins/len(ts)*100,2), 'avg', round(avg,2), 'sum', round(sm,2))
