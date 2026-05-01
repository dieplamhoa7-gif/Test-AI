from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path('data')
OUT = ROOT / 'strategy_results_cache.json'

SOURCES = {
    'b4_trend_pullback': ROOT / 'v3_b4_bullish_divergence_current_signals.json',
    'clean_split_a_bottom': ROOT / 'v3_clean_split_a2_b2_current_signals.json',
    'shakeout_breakdown_rebound': ROOT / 'shakeout_rebound_current_signals.json',
}

NAMES = {
    'b4_trend_pullback': 'Trend Pullback Pro',
    'clean_split_a_bottom': 'Support Rebound Hunter',
    'shakeout_breakdown_rebound': 'Shakeout Rebound',
}

ORDER = ['b4_trend_pullback', 'shakeout_breakdown_rebound', 'clean_split_a_bottom']


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def norm_item(item: dict, sid: str) -> dict:
    x = dict(item)
    x['strategy'] = sid
    if 'entryPrice' not in x and 'price' in x:
        x['entryPrice'] = x.get('price')
    if 'takeProfit' not in x and 'target' in x:
        x['takeProfit'] = x.get('target')
    return x


def main() -> None:
    strategies = []
    source_files = []
    for sid in ORDER:
        path = SOURCES[sid]
        data = load(path)
        buy = [norm_item(x, sid) for x in data.get('buy', [])]
        watch = [norm_item(x, sid) for x in data.get('watchlist', [])]
        summary = data.get('summary', {})
        reject_count = (
            summary.get('rejectCount')
            if 'rejectCount' in summary
            else summary.get('reject')
            if 'reject' in summary
            else len(data.get('rejects', [])) or len(data.get('rejectTop', []))
        )
        strategies.append({
            'id': sid,
            'name': NAMES[sid],
            'buy': buy,
            'watchlist': watch,
            'rejectCount': reject_count,
            'source': str(path),
            'canonical': True,
            'method': data.get('method') or data.get('strategy') or data.get('description'),
        })
        source_files.append(str(path))

    payload = {
        'updatedAt': datetime.now().isoformat(),
        'note': 'Current strategy signal cache rebuilt from canonical selected strategy scanners only. Web reads output only.',
        'canonical': True,
        'sourceFiles': source_files,
        'strategies': strategies,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'output': str(OUT),
        'strategies': [
            {
                'id': s['id'],
                'buy': [x.get('symbol') for x in s['buy']],
                'watch': [x.get('symbol') for x in s['watchlist']],
                'rejectCount': s['rejectCount'],
                'source': s['source'],
            }
            for s in strategies
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
