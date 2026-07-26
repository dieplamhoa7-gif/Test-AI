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
        'name': 'LH1 - Trend Pullback',
        'shortName': 'LH1 - Trend Pullback',
        'summary': 'Trend Pullback: mua nhịp kéo hồi trong xu hướng tăng; chỉ chọn cổ phiếu còn giữ nền giá tốt, giá gần vùng hỗ trợ, xu hướng/động lượng chưa gãy. Đạt đủ điều kiện mới vào BUY; thiếu nhẹ một vài tiêu chí thì đưa vào WATCH để theo dõi.',
    },
    'LH2_FINAL': {
        'name': 'LH2 - Shakeout Rebound',
        'shortName': 'LH2 - Shakeout Rebound',
        'summary': 'Shakeout Rebound: bắt nhịp hồi sau pha rũ hàng; giá thủng/kiểm định hỗ trợ ngắn hạn để loại bỏ lực yếu rồi kéo ngược lại vùng hỗ trợ cũ. Chiến lược biến động mạnh hơn, cần stop chặt và ưu tiên mã có dòng tiền quay lại rõ.',
        'indicators': 'Support break/reclaim %, vùng hỗ trợ/kháng cự ngày, RSI14, Volume Ratio, MACD Histogram, MA20/MA50, RS Rank/sức mạnh tương đối, OBV slope20, VWAP slope5, breadth/thị trường chung, ADX14, Range Position 60 phiên.',
    },
    'LH3_FINAL': {
        'name': 'LH3 - Support Rebound',
        'shortName': 'LH3 - Support Rebound',
        'summary': 'Support Rebound: hồi phục từ nền hỗ trợ; ưu tiên mã đang chạm/gần hỗ trợ mạnh, có dấu hiệu bật lại bằng điểm luật và xác suất ML. Dùng để bắt nhịp hồi có kiểm soát rủi ro, không mua khi hỗ trợ bị phá rõ.',
    },
    'LH4_FINAL': {
        'name': 'LH4 - Wave Momentum Entry',
        'shortName': 'LH4 - Wave Momentum Entry',
        'summary': 'Wave Momentum Entry: mua theo sóng tăng sau nền tích lũy đủ lâu; nền không quá rộng, sau đó có breakout/động lượng tăng xác nhận bằng MACD/volume/ROC/trend. Bộ lọc rất chặt nên hiện tại có thể không có BUY/WATCH nếu thị trường không đạt chuẩn.',
    },
}

NOTE = 'LH1-LH4 canonical names restored: Trend Pullback, Shakeout Rebound, Support Rebound, Wave Momentum Entry. Tooltip includes full description, indicators, validation win rate/trades/avg/total return.'

for path in FILES:
    data = json.loads(path.read_text(encoding='utf-8'))
    for col in data.get('columns', []):
        patch = PATCH.get(col.get('id'))
        if patch:
            col.update(patch)
    data['note'] = NOTE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'patched {path}')
