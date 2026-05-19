from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path('data')
IN = ROOT / 'v3_full_indicator_cache_v2.json'
OUT = ROOT / 'strategy_results_cache.json'
EXCLUDE = {'VIC', 'VHM'}

ORDER = ['b4_trend_pullback', 'shakeout_breakdown_rebound', 'clean_split_a_bottom']
NAMES = {
    'b4_trend_pullback': 'Trend Pullback Pro',
    'clean_split_a_bottom': 'Support Rebound Hunter',
    'shakeout_breakdown_rebound': 'Shakeout Rebound',
}


def f(v: Any, d: float = 0.0) -> float:
    try:
        if v is None:
            return d
        return float(v)
    except Exception:
        return d


def r(v: Any, n: int = 2):
    try:
        return round(float(v), n)
    except Exception:
        return None


def load_indicator_items() -> list[dict[str, Any]]:
    data = json.loads(IN.read_text(encoding='utf-8'))
    return [x for x in data.get('items', []) if str(x.get('symbol') or '').upper() not in EXCLUDE]


def base_ai(ind: dict[str, Any]) -> dict[str, Any]:
    div = ind.get('divergence') or {}
    ichi = ind.get('ichimoku') or {}
    return {
        'rsi': r(ind.get('rsi14')),
        'macd': r(ind.get('macd'), 4),
        'macdSignal': r(ind.get('signal'), 4),
        'macdHist': r(ind.get('histogram'), 4),
        'macdHistSeq': ind.get('macdHistSeq') or [],
        'macdHistImproving': bool(ind.get('macdHistImproving', False)),
        'macdHistRecovering': bool(ind.get('macdHistRecovering', False)),
        'bbPercent': r(ind.get('bbPercent'), 3),
        'volumeRatio': r(ind.get('volumeRatio'), 2),
        'roc20': r(ind.get('roc20')),
        'ret5': r(ind.get('ret5')),
        'ichimoku': ichi,
        'bullishDivergence': bool(div.get('bullish')),
        'bearishDivergence': bool(div.get('bearish')),
        'v3FullScore': ind.get('v3FullScore'),
    }


def rs_snapshot(rs: dict[str, Any]) -> dict[str, Any]:
    return {
        'supportZoneDay': rs.get('supportZoneDay'),
        'resistanceZoneDay': rs.get('resistanceZoneDay'),
        'activeSupportDay': rs.get('activeSupportDay'),
        'activeResistanceDay': rs.get('activeResistanceDay'),
    }


def support_resistance(item: dict[str, Any]) -> tuple[float, float]:
    rs = item.get('rs') or {}
    ind = item.get('indicators') or {}
    sup = f(rs.get('activeSupportDay') or rs.get('supportDay') or ind.get('activeSupportDay'))
    res = f(rs.get('activeResistanceDay') or rs.get('resistanceDay') or ind.get('activeResistanceDay'))
    return sup, res


def norm_result(item: dict[str, Any], sid: str, strategy_name: str, action: str, score: float, target_pct: float, stop_pct: float, missing: list[str], ai: dict[str, Any]) -> dict[str, Any]:
    sym = str(item.get('symbol') or '').upper()
    price = f(item.get('price'))
    rs = item.get('rs') or {}
    sup, res = support_resistance(item)
    entry = sup or price
    dist = (price - sup) / price * 100 if price and sup else 999
    return {
        'symbol': sym,
        'strategy': strategy_name,
        'action': action,
        'rankScore': r(score),
        'entryPrice': r(entry),
        'lastClose': r(price),
        'stopLoss': r(entry * (1 - stop_pct / 100)),
        'takeProfit': r(entry * (1 + target_pct / 100)),
        'targetPct': target_pct,
        'stopPct': stop_pct,
        'distSupportPct': r(dist),
        'support': r(sup),
        'resistance': r(res),
        'missingReasons': missing,
        'entryIndicators': ai,
        'rsSnapshot': rs_snapshot(rs),
        'asOfDate': item.get('date'),
        'source': 'v3_full_indicator_cache_v2.json',
        'strategyId': sid,
    }


def eval_b4(item: dict[str, Any]) -> dict[str, Any]:
    ind = item.get('indicators') or {}; ai = base_ai(ind); price = f(item.get('price')); sup, _ = support_resistance(item)
    dist = (price - sup) / price * 100 if price and sup else 999
    checks = [
        ((ai['ichimoku'] or {}).get('state') == 'above_cloud', 'above cloud'),
        (dist <= 3, 'gần hỗ trợ <=3%'),
        (48 <= f(ai['rsi']) <= 62, 'RSI 48-62'),
        (0.55 <= f(ai['volumeRatio']) <= 2.2, 'volume vừa'),
        (-8 <= f(ai['roc20']) <= 12, 'ROC20 hợp lệ'),
        ((ai.get('macdHistRecovering') or (ai.get('bullishDivergence') and f(ai['macdHist']) >= -0.05)), 'MACD hồi dần hoặc phân kỳ dương'),
        (f(ai['bbPercent']) <= 0.85, 'BB không quá cao'),
        (not ai.get('bearishDivergence'), 'không bearish divergence'),
    ]
    ok = sum(1 for x, _ in checks if x); missing = [lab for x, lab in checks if not x]
    action = 'BUY' if ok == len(checks) else 'WATCH' if ok >= 6 and not ai.get('bearishDivergence') else 'REJECT'
    return norm_result(item, 'b4_trend_pullback', 'B4_above_cloud_bullish_div_or_recovering', action, ok / len(checks) * 100, 6, 6, missing, ai)


def eval_clean(item: dict[str, Any]) -> dict[str, Any]:
    ind = item.get('indicators') or {}; ai = base_ai(ind); price = f(item.get('price')); sup, _ = support_resistance(item)
    dist = (price - sup) / price * 100 if price and sup else 999
    candidates = []
    for name in ['A2_oversold_near_support', 'B2_confirmed_rebound_above_cloud']:
        rsi = f(ai['rsi']); bbp = f(ai['bbPercent']); volr = f(ai['volumeRatio']); roc = f(ai['roc20']); ichi = (ai['ichimoku'] or {}).get('state')
        if name.startswith('A2'):
            checks = [ichi != 'below_cloud', dist <= 2.5, rsi <= 45, bbp <= 0.55, 0.55 <= volr <= 2.5, roc >= -12, ai.get('macdHistRecovering'), not ai.get('bearishDivergence')]
            labels = ['không thủng mây dưới', 'gần hỗ trợ <=2.5%', 'RSI <=45', 'BB thấp <=0.55', 'volume vừa', 'ROC20 không quá xấu', 'MACD hist hồi dần 3 phiên', 'không bearish divergence']
            target_pct = 10
        else:
            checks = [ichi == 'above_cloud', dist <= 3.0, 48 <= rsi <= 62, 0.55 <= volr <= 2.5, -8 <= roc <= 15, ai.get('macdHistRecovering'), bbp <= 0.9, not ai.get('bearishDivergence')]
            labels = ['above cloud', 'gần hỗ trợ <=3%', 'RSI 48-62', 'volume vừa', 'ROC20 hợp lệ', 'MACD hist hồi dần 3 phiên', 'BB không quá cao', 'không bearish divergence']
            target_pct = 6
        ok = sum(1 for x in checks if x); score = ok / len(checks) * 100; passed = all(checks)
        missing = [labels[i] for i, x in enumerate(checks) if not x]
        watch_ok = score >= 75 and dist <= 3.5 and ai.get('bullishDivergence') and not ai.get('bearishDivergence')
        action = 'BUY' if passed else 'WATCH' if watch_ok else 'REJECT'
        candidates.append(norm_result(item, 'clean_split_a_bottom', name, action, score, target_pct, 6, missing, ai))
    return sorted(candidates, key=lambda x: ({'BUY': 2, 'WATCH': 1, 'REJECT': 0}[x['action']], x['rankScore'] or 0), reverse=True)[0]


def eval_shakeout(item: dict[str, Any]) -> dict[str, Any]:
    ind = item.get('indicators') or {}; ai = base_ai(ind); price = f(item.get('price')); sup, _ = support_resistance(item)
    break_pct = (sup - price) / sup * 100 if sup else -999
    checks = [
        (2 <= break_pct <= 4, 'thủng hỗ trợ 2-4%'),
        (f(ai['rsi']) >= 20, 'RSI không quá yếu'),
        (f(ai['volumeRatio'], 1) <= 2.4, 'volume không xả quá mạnh'),
    ]
    ok = sum(1 for x, _ in checks if x); missing = [lab for x, lab in checks if not x]
    action = 'BUY' if ok == len(checks) else 'WATCH' if ok >= 2 else 'REJECT'
    score = 75 + (4 - abs(3 - break_pct) * 4) + (5 if 25 <= f(ai['rsi']) <= 45 else 0) + (3 if f(ai['volumeRatio'], 1) <= 1.3 else 0) if break_pct > -900 else 0
    return norm_result(item, 'shakeout_breakdown_rebound', 'shakeout_breakdown_rebound', action, score, 6, 4, missing, ai)


def pack_strategy(sid: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    buy = sorted([x for x in rows if x['action'] == 'BUY'], key=lambda x: x.get('rankScore') or 0, reverse=True)
    watch = sorted([x for x in rows if x['action'] == 'WATCH'], key=lambda x: x.get('rankScore') or 0, reverse=True)
    rejects = sorted([x for x in rows if x['action'] == 'REJECT'], key=lambda x: x.get('rankScore') or 0, reverse=True)
    return {
        'id': sid,
        'name': NAMES[sid],
        'buy': buy[:12],
        'watchlist': watch[:20],
        'rejectTop': rejects[:20],
        'rejectCount': len(rejects),
        'source': str(IN),
        'canonical': True,
        'method': 'Rules evaluated from one canonical indicator/R-S cache; no per-strategy history reload or R/S recomputation.',
    }


def main() -> None:
    items = load_indicator_items()
    by_sid = {sid: [] for sid in ORDER}
    for item in items:
        by_sid['b4_trend_pullback'].append(eval_b4(item))
        by_sid['clean_split_a_bottom'].append(eval_clean(item))
        by_sid['shakeout_breakdown_rebound'].append(eval_shakeout(item))
    strategies = [pack_strategy(sid, by_sid[sid]) for sid in ORDER]
    payload = {
        'updatedAt': datetime.now().isoformat(),
        'note': 'Current strategy signal cache rebuilt directly from canonical v3_full_indicator_cache_v2.json. Web reads output only.',
        'canonical': True,
        'sourceFiles': [str(IN)],
        'removedIntermediateFiles': [
            'data/v3_b4_bullish_divergence_current_signals.json',
            'data/v3_clean_split_a2_b2_current_signals.json',
            'data/shakeout_rebound_current_signals.json',
        ],
        'strategies': strategies,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'source': str(IN), 'strategies': [{'id': s['id'], 'buy': len(s['buy']), 'watch': len(s['watchlist']), 'rejectCount': s['rejectCount']} for s in strategies]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
