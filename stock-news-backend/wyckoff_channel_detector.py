from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parent
OVERRIDES_PATH = ROOT / 'data' / 'wyckoff_channel_overrides.json'


@dataclass
class Pivot:
    idx: int
    time: str
    kind: str  # 'high' | 'low'
    price: float


def _to_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    if 'time' in out.columns:
        out['time'] = pd.to_datetime(out['time'])
    for c in ['open', 'high', 'low', 'close', 'volume']:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors='coerce')
    return out


def detect_pivots(df: pd.DataFrame, left: int = 2, right: int = 2) -> list[Pivot]:
    df = _to_rows(df)
    pivots: list[Pivot] = []
    n = len(df)
    if n < left + right + 3:
        return pivots
    for i in range(left, n - right):
        lo = float(df.iloc[i]['low'])
        hi = float(df.iloc[i]['high'])
        low_ok = all(lo <= float(df.iloc[j]['low']) for j in range(i - left, i + right + 1) if j != i)
        high_ok = all(hi >= float(df.iloc[j]['high']) for j in range(i - left, i + right + 1) if j != i)
        ts = str(pd.Timestamp(df.iloc[i]['time']).date())
        if low_ok:
            pivots.append(Pivot(i, ts, 'low', lo))
        if high_ok:
            pivots.append(Pivot(i, ts, 'high', hi))
    pivots.sort(key=lambda p: p.idx)
    return pivots


def _fit_line(points: list[tuple[int, float]]) -> tuple[float, float] | None:
    if len(points) < 2:
        return None
    xs = pd.Series([p[0] for p in points], dtype=float)
    ys = pd.Series([p[1] for p in points], dtype=float)
    var = float(xs.var())
    if var == 0:
        return None
    slope = float(ys.cov(xs) / var)
    intercept = float(ys.mean() - slope * xs.mean())
    return slope, intercept


def _line_value(line: tuple[float, float], x: int) -> float:
    return line[0] * x + line[1]


def _load_overrides() -> dict[str, Any]:
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        return json.loads(OVERRIDES_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _build_override_channel(df: pd.DataFrame, symbol: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    lows = payload.get('lowPoints') or []
    highs = payload.get('highPoints') or []
    if len(lows) < 2 or len(highs) < 2:
        return None
    rows = _to_rows(df)
    time_to_idx = {str(pd.Timestamp(t).date()): i for i, t in enumerate(rows['time'])}
    low_pts: list[Pivot] = []
    high_pts: list[Pivot] = []
    for item in lows:
        ts = str(item['time'])
        idx = time_to_idx.get(ts)
        if idx is None:
            return None
        low_pts.append(Pivot(idx, ts, 'low', float(item.get('price', rows.iloc[idx]['low']))))
    for item in highs:
        ts = str(item['time'])
        idx = time_to_idx.get(ts)
        if idx is None:
            return None
        high_pts.append(Pivot(idx, ts, 'high', float(item.get('price', rows.iloc[idx]['high']))))
    direction = payload.get('type', 'SIDEWAY_UP')
    start_idx = min(low_pts[0].idx, high_pts[0].idx)
    end_idx = max(low_pts[-1].idx, high_pts[-1].idx)
    rel_low_pts = [Pivot(p.idx - start_idx, p.time, p.kind, p.price) for p in low_pts]
    rel_high_pts = [Pivot(p.idx - start_idx, p.time, p.kind, p.price) for p in high_pts]
    low_line = _fit_line([(p.idx, p.price) for p in rel_low_pts])
    high_line = _fit_line([(p.idx, p.price) for p in rel_high_pts])
    if not low_line or not high_line:
        return None
    avg_price = float(rows['close'].median()) if len(rows) else 1.0
    slope_gap = abs(low_line[0] - high_line[0])
    width0 = _line_value(high_line, rel_low_pts[0].idx) - _line_value(low_line, rel_low_pts[0].idx)
    width1 = _line_value(high_line, rel_high_pts[-1].idx) - _line_value(low_line, rel_high_pts[-1].idx)
    width_mid = max((width0 + width1) / 2.0, 0.001)
    width_change = abs(width1 - width0) / width_mid * 100
    return {
        'type': direction,
        'confidence': float(payload.get('confidence', 92.0)),
        'reason': payload.get('reason', 'manual Wyckoff anchor override'),
        'isHistorical': bool(payload.get('isHistorical', True)),
        'window': {'start_idx': start_idx, 'end_idx': end_idx},
        'anchors': {
            'lowPoints': [p.__dict__ for p in rel_low_pts],
            'highPoints': [p.__dict__ for p in rel_high_pts],
        },
        'lines': {
            'lowLine': {'slope': low_line[0], 'intercept': low_line[1]},
            'highLine': {'slope': high_line[0], 'intercept': high_line[1]},
        },
        'metrics': {
            'slopePctPerBar': round(((low_line[0] + high_line[0]) / 2.0) / max(avg_price, 0.001) * 100, 4),
            'parallelGapPct': round(slope_gap / max(avg_price, 0.001) * 100, 4),
            'widthChangePct': round(width_change, 2),
        },
        'wyckoffNotes': payload.get('wyckoffNotes', ['manual analyst-reviewed anchors']),
        'override': True,
        'symbol': symbol,
    }


def detect_local_wyckoff_channel(
    df: pd.DataFrame,
    main_tr: dict | None = None,
    events: list[dict] | None = None,
    scores: dict | None = None,
    lookback: int = 120,
    symbol: str = '',
) -> dict[str, Any]:
    """Detect local rising/falling range with Wyckoff-aware validation.

    Core idea:
    - find local pivots in a recent working window
    - build channel candidates from rising lows + rising highs (or falling highs/lows)
    - require roughly parallel upper/lower lines
    - penalize candidates when Wyckoff weakness contradicts a rising channel
      or strength contradicts a falling channel
    - return the best *local* channel instead of projecting from the whole TR
    """
    df = _to_rows(df)
    events = events or []
    scores = scores or {}
    overrides = _load_overrides()
    if symbol and symbol in overrides:
        overridden = _build_override_channel(df, symbol, overrides[symbol])
        if overridden:
            return overridden
    n = len(df)
    if n < 40:
        return {
            'type': 'NONE',
            'confidence': 0.0,
            'reason': 'not enough bars',
            'window': None,
            'anchors': {},
        }

    end_idx = n - 1
    start_idx = max(0, n - lookback)
    if main_tr:
        start_idx = max(start_idx, int(main_tr.get('start_idx', start_idx)))
        end_idx = min(end_idx, int(main_tr.get('end_idx', end_idx)))
    work = df.iloc[start_idx:end_idx + 1].copy().reset_index(drop=True)
    base_offset = start_idx

    pivots = detect_pivots(work)
    lows = [p for p in pivots if p.kind == 'low']
    highs = [p for p in pivots if p.kind == 'high']
    if len(lows) < 2 or len(highs) < 2:
        return {
            'type': 'NONE',
            'confidence': 0.0,
            'reason': 'not enough pivots',
            'window': {'start_idx': start_idx, 'end_idx': end_idx},
            'anchors': {},
        }

    event_types = {e.get('type') for e in events}
    strength_score = float(scores.get('springScore', 0) or 0) + float(scores.get('sosScore', 0) or 0)
    weakness_score = float(scores.get('upthrustScore', 0) or 0) + float(scores.get('sowScore', 0) or 0)

    candidates: list[dict[str, Any]] = []

    def add_candidate(direction: str, low_pts: list[Pivot], high_pts: list[Pivot]) -> None:
        if len(low_pts) < 2 or len(high_pts) < 2:
            return
        low_line = _fit_line([(p.idx, p.price) for p in low_pts])
        high_line = _fit_line([(p.idx, p.price) for p in high_pts])
        if not low_line or not high_line:
            return
        low_slope, high_slope = low_line[0], high_line[0]
        slope_gap = abs(low_slope - high_slope)
        avg_price = float(work['close'].median()) if len(work) else 1.0
        if avg_price <= 0:
            return
        slope_pct = ((low_slope + high_slope) / 2.0) / avg_price * 100
        width0 = _line_value(high_line, low_pts[0].idx) - _line_value(low_line, low_pts[0].idx)
        width1 = _line_value(high_line, high_pts[-1].idx) - _line_value(low_line, high_pts[-1].idx)
        width_mid = max((width0 + width1) / 2.0, 0.001)
        width_change = abs(width1 - width0) / width_mid * 100

        if direction == 'up':
            monotonic = all(low_pts[i].price > low_pts[i - 1].price for i in range(1, len(low_pts))) and all(high_pts[i].price > high_pts[i - 1].price for i in range(1, len(high_pts)))
            slope_ok = low_slope > 0 and high_slope > 0 and slope_pct <= 0.22
        else:
            monotonic = all(low_pts[i].price < low_pts[i - 1].price for i in range(1, len(low_pts))) and all(high_pts[i].price < high_pts[i - 1].price for i in range(1, len(high_pts)))
            slope_ok = low_slope < 0 and high_slope < 0 and slope_pct >= -0.22
        if not monotonic or not slope_ok:
            return

        score = 50.0
        score += min(18.0, (len(low_pts) + len(high_pts)) * 3.0)
        score -= min(20.0, slope_gap / avg_price * 5000.0)
        score -= min(15.0, width_change * 0.35)

        wyckoff_notes: list[str] = []
        if direction == 'up':
            if 'SOW' in event_types or 'LPSY' in event_types or 'UTAD' in event_types:
                score -= 20.0
                wyckoff_notes.append('weakness events present, rising channel is suspect')
            if weakness_score > strength_score + 8:
                score -= 12.0
                wyckoff_notes.append('weakness score dominates strength score')
            if 'SOS' in event_types or 'LPS' in event_types or strength_score >= weakness_score:
                score += 8.0
                wyckoff_notes.append('strength supports rising range interpretation')
        else:
            if 'SOS' in event_types or 'LPS' in event_types or 'Spring' in event_types:
                score -= 18.0
                wyckoff_notes.append('strength events present, falling channel is suspect')
            if strength_score > weakness_score + 8:
                score -= 12.0
                wyckoff_notes.append('strength score dominates weakness score')
            if 'SOW' in event_types or 'LPSY' in event_types or weakness_score >= strength_score:
                score += 8.0
                wyckoff_notes.append('weakness supports falling range interpretation')

        candidates.append({
            'direction': direction,
            'score': round(score, 2),
            'slopePctPerBar': round(slope_pct, 4),
            'parallelGapPct': round(slope_gap / avg_price * 100, 4),
            'widthChangePct': round(width_change, 2),
            'lowPoints': [p.__dict__ for p in low_pts],
            'highPoints': [p.__dict__ for p in high_pts],
            'lowLine': {'slope': low_line[0], 'intercept': low_line[1]},
            'highLine': {'slope': high_line[0], 'intercept': high_line[1]},
            'start_idx': base_offset + min(low_pts[0].idx, high_pts[0].idx),
            'end_idx': base_offset + max(low_pts[-1].idx, high_pts[-1].idx),
            'isHistorical': base_offset + max(low_pts[-1].idx, high_pts[-1].idx) < n - 8,
            'wyckoffNotes': wyckoff_notes,
        })

    # Search both recent and slightly older local structures because the best
    # Wyckoff sideway-up/down channel may be a historical local segment that has
    # already failed later, but is still the visually correct range analysts draw.
    for low_start in range(max(0, len(lows) - 7), max(0, len(lows) - 2)):
        for high_start in range(max(0, len(highs) - 7), max(0, len(highs) - 2)):
            low_slice = lows[low_start: min(len(lows), low_start + 4)]
            high_slice = highs[high_start: min(len(highs), high_start + 4)]
            for lc in range(2, len(low_slice) + 1):
                for hc in range(2, len(high_slice) + 1):
                    add_candidate('up', low_slice[:lc], high_slice[:hc])
                    add_candidate('down', low_slice[:lc], high_slice[:hc])

    if not candidates:
        return {
            'type': 'NONE',
            'confidence': 0.0,
            'reason': 'no valid local Wyckoff channel candidate',
            'window': {'start_idx': start_idx, 'end_idx': end_idx},
            'anchors': {},
        }

    best = max(candidates, key=lambda x: x['score'])
    if best['direction'] == 'up':
        ctype = 'SIDEWAY_UP'
        reason = 'local rising range built from higher lows + higher highs, then filtered by Wyckoff strength/weakness'
    else:
        ctype = 'SIDEWAY_DOWN'
        reason = 'local falling range built from lower highs + lower lows, then filtered by Wyckoff strength/weakness'

    confidence = max(0.0, min(100.0, best['score']))
    if confidence < 55:
        ctype = 'RANGE_MIXED'
        reason = 'geometry exists but Wyckoff confirmation is weak/mixed'

    return {
        'type': ctype,
        'confidence': round(confidence, 1),
        'reason': reason,
        'isHistorical': bool(best.get('isHistorical')),
        'window': {'start_idx': best['start_idx'], 'end_idx': best['end_idx']},
        'anchors': {
            'lowPoints': best['lowPoints'],
            'highPoints': best['highPoints'],
        },
        'lines': {
            'lowLine': best['lowLine'],
            'highLine': best['highLine'],
        },
        'metrics': {
            'slopePctPerBar': best['slopePctPerBar'],
            'parallelGapPct': best['parallelGapPct'],
            'widthChangePct': best['widthChangePct'],
        },
        'wyckoffNotes': best['wyckoffNotes'],
    }
