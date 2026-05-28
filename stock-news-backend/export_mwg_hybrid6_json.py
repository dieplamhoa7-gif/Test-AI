import json
from pathlib import Path
from run_mwg_six_trend_methods import method_hybrid, df

lines = method_hybrid()
out = {
    'symbol': 'MWG',
    'asOfDate': str(df.iloc[-1]['time']),
    'asOfPrice': float(df.iloc[-1]['close']),
    'createdAt': '2026-05-28T08:55:00+00:00',
    'summary': {
        'trendlines': len(lines),
        'parallelChannels': 0,
        'pitchforks': 0,
        'linregChannels': 0,
        'srLevels': 0,
        'patterns': 0,
        'candlestickSignals': 0,
        'currentBias': 'experimental-hybrid-6'
    },
    'trendlines': [],
    'srLevels': [],
    'patterns': [],
    'candlestickSignals': [],
    'rows': []
}
for i, tl in enumerate(lines, start=1):
    out['trendlines'].append({
        'id': f'hybrid6_{i}',
        'type': 'uptrend' if tl.kind == 'support' else 'downtrend',
        'points': [
            {'time': int(tl.x0), 'value': round(float(tl.y0), 2)},
            {'time': int(tl.x1), 'value': round(float(tl.y1), 2)}
        ],
        'slopePerBar': round(float(tl.slope), 5),
        'touches': int(tl.touches),
        'lengthBars': int(tl.x1 - tl.x0),
        'rSquared': 0.9,
        'valid': True,
        'score': round(float(tl.trust), 2),
        'trust': round(float(tl.trust), 2),
        'breaks': int(tl.breaks),
        'source': tl.note or tl.method,
        'touchPoints': []
    })
path = Path('firebase_public/data/charts/MWG_hybrid6_day.json')
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(path)
