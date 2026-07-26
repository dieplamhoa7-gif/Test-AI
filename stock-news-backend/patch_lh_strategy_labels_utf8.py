from __future__ import annotations

import json
from pathlib import Path

FILES = [
    Path('data/strategy_matrix_cache.json'),
    Path('data/live_overrides/strategy_matrix_cache.json'),
    Path('firebase_public/data/strategy_matrix_cache.json'),
]

PATCH = {
    'LH1_FINAL': {
        'name': 'LH1 - Trend Pullback / Kéo nền xu hướng',
        'shortName': 'LH1 - Kéo nền xu hướng',
    },
    'LH2_FINAL': {
        'name': 'LH2 - Balanced Breakout / Breakout cân bằng',
        'shortName': 'LH2 - Breakout cân bằng',
    },
    'LH3_FINAL': {
        'name': 'LH3 - Support Rebound / Hồi phục hỗ trợ',
        'shortName': 'LH3 - Hồi phục hỗ trợ',
    },
    'LH4_FINAL': {
        'name': 'LH4 - Wave Momentum Entry / Sóng tăng',
        'shortName': 'LH4 - Sóng tăng',
    },
}

NOTE = 'LH1-LH4 matrix: headers show strategy group names; tooltip includes full description, indicators, validation win rate/trades/avg/total return.'

for path in FILES:
    data = json.loads(path.read_text(encoding='utf-8'))
    for col in data.get('columns', []):
        patch = PATCH.get(col.get('id'))
        if patch:
            col.update(patch)
    data['note'] = NOTE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'patched {path}')
