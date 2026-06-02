"""Convert Claude original MWG_patterns_forecast.json into a COMPACT overlay
suitable for the LightweightCharts frontend without overloading the page.

Rules:
- Keep top supports/resistances (max 4 each, dedup within 2%).
- Keep top trendlines (max 2 per direction).
- Keep top "big" patterns by score (Tier 2/3) up to 3.
- Keep darvas/FVG/OB as zones, max 3 total.
- Keep recent candlestick (last 30 bars) max 4.
- Forecast line: keep all points (small).
"""
from __future__ import annotations
import json, math, pathlib

LABEL = {
    'support-cluster':'Hỗ trợ','resistance-cluster':'Kháng cự',
    'support-trendline':'Trendline hỗ trợ','resistance-trendline':'Trendline kháng cự',
    'double-bottom':'2 Đáy','double-top':'2 Đỉnh','triple-bottom':'3 Đáy','triple-top':'3 Đỉnh',
    'head-shoulders':'Vai-Đầu-Vai','inverse-head-shoulders':'VĐV ngược',
    'ascending-triangle':'Tam giác tăng','descending-triangle':'Tam giác giảm','symmetrical-triangle':'Tam giác cân',
    'falling-wedge':'Nêm giảm','rising-wedge':'Nêm tăng',
    'up-channel':'Kênh tăng','down-channel':'Kênh giảm',
    'darvas-box':'Hộp Darvas','cup-handle':'Cốc-Tay cầm',
    'rounding-bottom':'Đáy tròn','rounding-top':'Đỉnh tròn',
    'bull-flag':'Cờ tăng','bear-flag':'Cờ giảm',
    'spring-shakeout':'Spring','upthrust-bull-trap':'Upthrust',
    'fvg-bullish':'FVG tăng','fvg-bearish':'FVG giảm',
    'order-block-bullish':'OB tăng','order-block-bearish':'OB giảm',
}

def lab(t): return LABEL.get(t, t)

def finite(v):
    try: return v is not None and math.isfinite(float(v))
    except Exception: return False

def dedupe_levels(levels, pct=0.02):
    out = []
    for lv in sorted(levels, key=lambda x: -x['score']):
        v = lv['value']
        if not any(abs(v / max(1e-9, o['value']) - 1) < pct for o in out):
            out.append(lv)
    return out

def convert(symbol='MWG'):
    root = pathlib.Path(__file__).resolve().parent
    src = root / 'firebase_public' / 'charts_debug' / f'{symbol}_patterns_forecast.json'
    dst = root / 'firebase_public' / 'data' / 'patterns' / f'{symbol}_patterns_overlay.json'
    d = json.loads(src.read_text(encoding='utf-8'))
    last = d.get('lastDate')
    last_close = d.get('lastClose')
    pats = d.get('patterns', [])
    fc_points = d.get('forecast', {}).get('points', [])
    fc_scen = d.get('forecast', {}).get('scenarios', {})

    overlay = {
        'symbol': symbol,
        'source': 'claude-original-compact',
        'createdAt': d.get('createdAt'),
        'timeframe': d.get('timeframe'),
        'lastClose': last_close,
        'summary': d.get('summary', {}),
        'labels': [],
        'lines': [],
        'zones': [],
        'forecast': fc_points,
        'scenarios': fc_scen,
        'note': 'Compact projection of Claude original output; full chart at /charts_debug/<SYM>_patterns_forecast.html',
    }

    # 1) Supports / resistances clusters
    supports, resistances = [], []
    for p in pats:
        t = p.get('type', '')
        if t in ('support-cluster', 'resistance-cluster'):
            pts = (p.get('lines') or [{}])[0].get('points') or []
            if pts and finite(pts[0].get('value')):
                entry = {'time': pts[0]['time'], 'value': float(pts[0]['value']), 'score': p.get('score') or 0, 'type': t}
                (supports if 'support' in t else resistances).append(entry)
    supports = dedupe_levels(supports)[:4]
    resistances = dedupe_levels(resistances)[:4]
    for lv in supports:
        overlay['lines'].append({'type': 'support', 'name': lv['type'], 'text': f"Hỗ trợ {lv['value']:g}", 'direction': 'bullish', 'color': '#16a34a', 'dash': True, 'points': [{'time': lv['time'], 'value': lv['value']}, {'time': last, 'value': lv['value']}]})
        overlay['labels'].append({'time': last, 'price': lv['value'], 'text': f"Hỗ trợ {lv['value']:g}", 'kind': 'sr-label', 'role': 'primary', 'direction': 'bullish', 'color': '#16a34a'})
    for lv in resistances:
        overlay['lines'].append({'type': 'resistance', 'name': lv['type'], 'text': f"Kháng cự {lv['value']:g}", 'direction': 'bearish', 'color': '#dc2626', 'dash': True, 'points': [{'time': lv['time'], 'value': lv['value']}, {'time': last, 'value': lv['value']}]})
        overlay['labels'].append({'time': last, 'price': lv['value'], 'text': f"Kháng cự {lv['value']:g}", 'kind': 'sr-label', 'role': 'primary', 'direction': 'bearish', 'color': '#dc2626'})

    # 2) Trendlines
    tl_bull, tl_bear = [], []
    for p in pats:
        t = p.get('type', '')
        if t in ('support-trendline', 'resistance-trendline'):
            lines = p.get('lines') or []
            if not lines: continue
            pts = [{'time': q.get('time'), 'value': q.get('value')} for q in (lines[0].get('points') or []) if q.get('time') and finite(q.get('value'))]
            if len(pts) < 2: continue
            entry = {'pts': pts, 'score': p.get('score') or 0, 'type': t}
            (tl_bull if 'support' in t else tl_bear).append(entry)
    for arr, col, direction, label_txt in ((tl_bull, '#0891b2', 'bullish', 'Trendline hỗ trợ'),
                                           (tl_bear, '#db2777', 'bearish', 'Trendline kháng cự')):
        for tl in sorted(arr, key=lambda x: -x['score'])[:2]:
            overlay['lines'].append({'type': tl['type'], 'name': tl['type'], 'text': label_txt, 'direction': direction, 'color': col, 'points': tl['pts']})

    # 3) Big patterns
    big_types = {'double-bottom', 'double-top', 'triple-bottom', 'triple-top', 'head-shoulders', 'inverse-head-shoulders', 'cup-handle', 'ascending-triangle', 'descending-triangle', 'symmetrical-triangle', 'falling-wedge', 'rising-wedge', 'up-channel', 'down-channel', 'bull-flag', 'bear-flag', 'rounding-bottom', 'rounding-top'}
    big = [p for p in pats if p.get('type') in big_types]
    big.sort(key=lambda x: -(x.get('score') or 0))
    for p in big[:3]:
        t = p['type']; direction = p.get('direction', 'neutral')
        col = '#16a34a' if direction == 'bullish' else '#dc2626' if direction == 'bearish' else '#6b7280'
        for ln in (p.get('lines') or []):
            pts = [{'time': q.get('time'), 'value': q.get('value')} for q in (ln.get('points') or []) if q.get('time') and finite(q.get('value'))]
            if len(pts) >= 2:
                lcol = '#f59e0b' if ln.get('name') == 'neckline' else col
                overlay['lines'].append({'type': t, 'name': ln.get('name') or t, 'text': lab(t) if ln.get('name') != 'neckline' else 'Neckline', 'direction': direction, 'color': lcol, 'dash': ln.get('name') == 'neckline', 'points': pts})
        anchor = None
        for ln in (p.get('lines') or []):
            pts = ln.get('points') or []
            if pts and finite(pts[0].get('value')):
                anchor = pts[0]; break
        if anchor:
            lv = p.get('levels') or {}
            tgt = f" → {lv['target']}" if finite(lv.get('target')) else ''
            overlay['labels'].append({'time': anchor['time'], 'price': anchor['value'], 'text': lab(t) + tgt, 'kind': 'pattern-title', 'role': 'primary', 'direction': direction, 'color': col, 'yShift': 32 if direction == 'bearish' else -32})

    # 4) Zones: Darvas / FVG / OB
    zones = []
    for p in pats:
        t = p.get('type', '')
        lv = p.get('levels') or {}
        if t == 'darvas-box' and finite(lv.get('support')) and finite(lv.get('resistance')):
            x0 = (p.get('lines') or [{}])[0].get('points') or [{}]
            zones.append({'type': t, 'text': lab(t), 'from': (x0[0].get('time') if x0 else p.get('time')) or p.get('time'), 'to': last, 'low': lv['support'], 'high': lv['resistance'], 'color': 'rgba(168,85,247,0.10)', 'score': p.get('score') or 0})
        elif t.startswith('fvg') and finite(lv.get('gapLow')) and finite(lv.get('gapHigh')):
            zones.append({'type': t, 'text': lab(t), 'from': p.get('time'), 'to': last, 'low': lv['gapLow'], 'high': lv['gapHigh'], 'color': 'rgba(22,163,74,0.18)' if 'bull' in t else 'rgba(220,38,38,0.18)', 'score': p.get('score') or 0})
        elif t.startswith('order-block') and finite(lv.get('obLow')) and finite(lv.get('obHigh')):
            zones.append({'type': t, 'text': lab(t), 'from': p.get('time'), 'to': last, 'low': lv['obLow'], 'high': lv['obHigh'], 'color': 'rgba(16,185,129,0.22)' if 'bull' in t else 'rgba(244,63,94,0.22)', 'score': p.get('score') or 0})
    zones.sort(key=lambda z: -z['score'])
    overlay['zones'] = zones[:3]

    # 5) Forecast label
    if fc_points:
        q = fc_points[-1]
        if q.get('time') and finite(q.get('value')):
            overlay['labels'].append({'time': q['time'], 'price': q['value'], 'text': f"Dự báo {q['value']}", 'kind': 'forecast-label', 'role': 'primary', 'direction': 'neutral', 'color': '#2563eb'})

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(overlay, ensure_ascii=False, indent=2), encoding='utf-8')
    print(dst, 'lines', len(overlay['lines']), 'labels', len(overlay['labels']), 'zones', len(overlay['zones']))

if __name__ == '__main__':
    convert()
