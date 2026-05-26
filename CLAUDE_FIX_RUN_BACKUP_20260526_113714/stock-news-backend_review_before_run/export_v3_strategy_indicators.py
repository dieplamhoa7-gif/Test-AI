from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

OUT=Path('data/v3_strategy_indicators_spec.json')

payload={
  'createdAt': datetime.now().isoformat(),
  'strategy': 'Confirmed Support V3 - current patched version',
  'purpose': 'Mua khi cổ phiếu test hỗ trợ, giữ được hỗ trợ ở phiên xác nhận, trend chưa gãy, có xác nhận động lượng/volume.',
  'dataFields': {
    'price': ['open','high','low','close','volume'],
    'supportResistance': [
      'supportZonesDay nếu có',
      'fallback: activeSupportDay',
      'fallback: supportDay',
      'fallback: nearSupportDay',
      'fallback: supportLevelsDay',
      'resistanceLevelsDay'
    ],
    'movingAverages': ['MA10','MA20','MA50'],
    'momentum': ['RSI14','MACD histogram'],
    'volatility': ['ATR14'],
    'volume': ['volume','volume average 20','volume ratio'],
    'recentReturn': ['ret5 = close / close.shift(5) - 1'],
    'futurePathForBacktest': ['future open/high/low/close/volume up to 42 sessions']
  },
  'setupRules': [
    {
      'step': 1,
      'name': 'Support zone detection',
      'rule': 'Ưu tiên supportZonesDay có score >=55. Nếu field cũ không còn, dựng zone từ activeSupportDay/supportDay/nearSupportDay/supportLevelsDay.',
      'fallbackZone': 'low = support * 0.985, high = support * 1.015, center = support, score = max(55, min(85, 80 - distance_to_price_pct*5))'
    },
    {
      'step': 2,
      'name': 'Touch support',
      'rule': 'Phiên touch phải có low <= zone_high và close >= zone_low.'
    },
    {
      'step': 3,
      'name': 'Confirmation candle',
      'rule': 'Phiên sau phải giữ vùng: close >= zone_low và low <= zone_high; close_pos >= 0.55; và có nến xanh hoặc rút chân dưới hoặc reclaim.'
    },
    {
      'step': 4,
      'name': 'MA structure filter',
      'rule': 'close_confirm >= MA50*0.985; MA20 >= MA50*0.975; MA50 hiện tại >= MA50 cách 10 phiên *0.985.'
    },
    {
      'step': 5,
      'name': 'Recent drop filter',
      'rule': 'ret5 >= -9%, tránh mua cổ phiếu vừa rơi quá mạnh.'
    },
    {
      'step': 6,
      'name': 'RSI/MACD/Volume confirmation',
      'rule': 'Cần đạt ít nhất 2/3: RSI OK, MACD histogram OK, Volume OK.',
      'details': {
        'rsiOk': 'RSI confirm >=39 và RSI confirm >= RSI touch - 0.5',
        'histOk': 'MACD histogram confirm >= MACD histogram touch',
        'volOk': 'Volume confirm >= 70% volume touch và volume touch <= 2.2 * vol20'
      }
    },
    {
      'step': 7,
      'name': 'Original V3 risk/target',
      'rule': 'Bản gốc dùng stop quanh dưới zone/touch/confirm theo ATR, riskPct 1% đến 6.2%, target 1R hoặc kháng cự gần nếu RR phù hợp.'
    },
    {
      'step': 8,
      'name': 'Current high-target test',
      'rule': 'Biến thể đang test: stop rộng hơn dưới support zone, target cao hơn 2.5R-3R, horizon tối đa 42 phiên.'
    }
  ],
  'currentOutputFiles': {
    'setupFile': 'data/v3_confirmed_support_setups_with_future.json',
    'debugCounts': 'data/v3_pipeline_debug_counts.json',
    'wideStopHighTargetResults': 'data/v3_saved_setups_wide_stop_high_target_results.json'
  },
  'nextPartsSuggested': [
    'Part 2: chạy thống kê từng tầng filter V3 sau khi patch fallback support zone.',
    'Part 3: xuất bảng 9 setup V3 hiện có với toàn bộ indicator snapshot.',
    'Part 4: chạy lại target/stop grid từ setup file, không tính lại R/S.',
    'Part 5: nếu cần nhiều setup hơn, nới từng điều kiện V3 một cách có kiểm soát.'
  ]
}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print('saved',OUT)
print(json.dumps({'strategy':payload['strategy'],'rules':len(payload['setupRules']),'file':str(OUT)},ensure_ascii=False,indent=2))
