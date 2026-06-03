import json
from pathlib import Path
from collections import defaultdict

SRC = Path('data/lh1_canonical_t3_fee_2023_to_now.json')
obj = json.loads(SRC.read_text(encoding='utf-8'))
trades = obj['trades']

by = defaultdict(list)
for t in trades:
    by[t['symbol']].append(t)

def metrics(ts):
    n = len(ts)
    wins = sum(1 for t in ts if float(t.get('netPnlPct', 0) or 0) > 0)
    losses = sum(1 for t in ts if float(t.get('netPnlPct', 0) or 0) < 0)
    sm = sum(float(t.get('netPnlPct', 0) or 0) for t in ts)
    avg = sm / n if n else 0
    return {
        'trades': n,
        'wins': wins,
        'losses': losses,
        'winRatePct': round(wins / n * 100, 2) if n else 0,
        'avgNetPnlPct': round(avg, 2),
        'sumNetPnlPct': round(sm, 2),
    }

def subset_stats(symbols):
    xs = [t for t in trades if t['symbol'] in symbols]
    return metrics(xs)

rows = []
for sym, ts in by.items():
    m = metrics(ts)
    rows.append((sym, m))

# candidate filters from strict to relaxed
candidates = {
    'strict_best': [sym for sym, m in rows if m['trades'] >= 4 and m['winRatePct'] >= 70 and m['avgNetPnlPct'] >= 1.2 and m['sumNetPnlPct'] > 0],
    'balanced_best': [sym for sym, m in rows if m['trades'] >= 4 and m['winRatePct'] >= 60 and m['avgNetPnlPct'] >= 1.0 and m['sumNetPnlPct'] > 0],
    'quality_positive': [sym for sym, m in rows if m['trades'] >= 3 and m['winRatePct'] >= 60 and m['avgNetPnlPct'] >= 0.8 and m['sumNetPnlPct'] > 0],
    'remove_negative': [sym for sym, m in rows if m['sumNetPnlPct'] > 0],
}

out = {
    'full': subset_stats(set(by.keys())),
    'symbolMetrics': {sym: m for sym, m in sorted(rows)},
    'candidates': {name: {'symbols': syms, 'stats': subset_stats(syms)} for name, syms in candidates.items()},
}
print(json.dumps(out, ensure_ascii=False, indent=2))
