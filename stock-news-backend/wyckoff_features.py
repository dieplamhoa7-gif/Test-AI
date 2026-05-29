# -*- coding: utf-8 -*-
"""Wyckoff feature/score engine for LH Investment research.

This module converts Wyckoff concepts into measurable, backtestable features.
It intentionally avoids hard phase labeling; instead it emits event scores and
scenario probabilities that can be consumed by ML/backtests/chart overlays.

Input rows are dicts with at least: time, open, high, low, close, volume.
All calculations use historical bars up to the current row only.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from statistics import mean
from typing import Any, Iterable

EPS = 1e-9


def _f(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        v = row.get(key, default)
        return float(default if v is None else v)
    except Exception:
        return float(default)


def _avg(vals: Iterable[float]) -> float:
    vals = [float(v) for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else 0.0


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))


def _safe_div(a: float, b: float, default: float = 0.0) -> float:
    return default if abs(b) < EPS else a / b


def _pct(a: float, b: float) -> float:
    return _safe_div(a, b, 0.0) - 1.0


def moving_avg(values: list[float], idx: int, window: int) -> float:
    start = max(0, idx - window + 1)
    return _avg(values[start : idx + 1])


def prior_window(rows: list[dict[str, Any]], idx: int, window: int) -> list[dict[str, Any]]:
    start = max(0, idx - window)
    return rows[start:idx]


@dataclass
class WyckoffBarFeatures:
    spread: float
    body: float
    close_pos: float
    upper_wick: float
    lower_wick: float
    vol_rel20: float
    range_rel20: float
    ret_1d: float
    ret_3d: float
    ret_5d: float


@dataclass
class WyckoffRange:
    low: float
    high: float
    mid: float
    width_pct: float
    age: int


@dataclass
class WyckoffScores:
    springScore: float
    upthrustScore: float
    sosScore: float
    sowScore: float
    dryTestScore: float
    absorptionScore: float
    distributionScore: float
    markupReadinessScore: float
    markdownReadinessScore: float
    rangeContinuationScore: float
    bias: str


@dataclass
class WyckoffSnapshot:
    symbol: str | None
    time: str | None
    close: float
    bar: WyckoffBarFeatures
    range: WyckoffRange | None
    scores: WyckoffScores
    events: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def bar_features(rows: list[dict[str, Any]], idx: int) -> WyckoffBarFeatures:
    row = rows[idx]
    op = _f(row, "open")
    hi = _f(row, "high")
    lo = _f(row, "low")
    cl = _f(row, "close")
    vol = _f(row, "volume")
    spreads = [max(EPS, _f(r, "high") - _f(r, "low")) for r in rows]
    vols = [_f(r, "volume") for r in rows]
    spread = max(EPS, hi - lo)
    body = abs(cl - op)
    close_pos = _clamp((cl - lo) / spread, 0.0, 1.0)
    upper_wick = max(0.0, hi - max(op, cl))
    lower_wick = max(0.0, min(op, cl) - lo)
    vol_ma20 = moving_avg(vols, idx, 20)
    spread_ma20 = moving_avg(spreads, idx, 20)

    def ret(n: int) -> float:
        if idx < n:
            return 0.0
        prev = _f(rows[idx - n], "close")
        return _pct(cl, prev)

    return WyckoffBarFeatures(
        spread=round(spread, 4),
        body=round(body, 4),
        close_pos=round(close_pos, 4),
        upper_wick=round(upper_wick, 4),
        lower_wick=round(lower_wick, 4),
        vol_rel20=round(_safe_div(vol, vol_ma20, 1.0), 4),
        range_rel20=round(_safe_div(spread, spread_ma20, 1.0), 4),
        ret_1d=round(ret(1), 4),
        ret_3d=round(ret(3), 4),
        ret_5d=round(ret(5), 4),
    )


def detect_trading_range(rows: list[dict[str, Any]], idx: int, lookback: int = 60) -> WyckoffRange | None:
    hist = prior_window(rows, idx, lookback)
    if len(hist) < max(25, lookback // 2):
        return None
    lows = [_f(r, "low") for r in hist if _f(r, "low") > 0]
    highs = [_f(r, "high") for r in hist if _f(r, "high") > 0]
    if not lows or not highs:
        return None
    lo = min(lows)
    hi = max(highs)
    mid = (lo + hi) / 2
    width_pct = _safe_div(hi - lo, mid, 0.0)
    return WyckoffRange(low=round(lo, 4), high=round(hi, 4), mid=round(mid, 4), width_pct=round(width_pct, 4), age=len(hist))


def _trend_score(rows: list[dict[str, Any]], idx: int, lookback: int = 30) -> float:
    if idx < lookback:
        return 0.0
    now = _f(rows[idx], "close")
    past = _f(rows[idx - lookback], "close")
    return _pct(now, past)


def _future_confirm(rows: list[dict[str, Any]], idx: int, direction: str, days: int = 3) -> float:
    """Optional confirmation if called retrospectively; current production should not rely on future bars.

    Kept tiny and neutral: when idx is not at end in offline labeling/backtest it can be used to
    inspect next-bar behavior. For live scoring, callers should pass only rows up to current bar.
    """
    if idx + 1 >= len(rows):
        return 0.0
    close = _f(rows[idx], "close")
    fut = rows[idx + 1 : min(len(rows), idx + 1 + days)]
    if not fut or close <= 0:
        return 0.0
    max_hi = max(_f(r, "high") for r in fut)
    min_lo = min(_f(r, "low") for r in fut)
    if direction == "up":
        return _clamp(_pct(max_hi, close) * 500, 0, 15)
    return _clamp(-_pct(min_lo, close) * 500, 0, 15)


def score_spring(row: dict[str, Any], bar: WyckoffBarFeatures, tr: WyckoffRange | None) -> float:
    if tr is None:
        return 0.0
    lo = _f(row, "low")
    cl = _f(row, "close")
    op = _f(row, "open")
    score = 0.0
    support = tr.low
    tol = max(support * 0.006, (tr.high - tr.low) * 0.04)
    if lo < support - tol * 0.2:
        score += 22
    elif lo <= support + tol:
        score += 12
    if cl >= support:
        score += 24
    if cl >= op * 0.995:
        score += 8
    if bar.lower_wick >= bar.spread * 0.35:
        score += 12
    if bar.close_pos >= 0.55:
        score += 10
    if bar.vol_rel20 >= 1.15:
        score += 10
    elif bar.vol_rel20 <= 0.9 and cl >= support:
        score += 6  # dry reclaim/test can also be valid late in accumulation
    if min(op, cl) < support - tol:
        score -= 25
    return round(_clamp(score), 2)


def score_upthrust(row: dict[str, Any], bar: WyckoffBarFeatures, tr: WyckoffRange | None) -> float:
    if tr is None:
        return 0.0
    hi = _f(row, "high")
    cl = _f(row, "close")
    op = _f(row, "open")
    score = 0.0
    resistance = tr.high
    tol = max(resistance * 0.006, (tr.high - tr.low) * 0.04)
    if hi > resistance + tol * 0.2:
        score += 22
    elif hi >= resistance - tol:
        score += 12
    if cl <= resistance:
        score += 24
    if cl <= op * 1.005:
        score += 8
    if bar.upper_wick >= bar.spread * 0.35:
        score += 12
    if bar.close_pos <= 0.45:
        score += 10
    if bar.vol_rel20 >= 1.15:
        score += 10
    if max(op, cl) > resistance + tol:
        score -= 25
    return round(_clamp(score), 2)


def score_sos(row: dict[str, Any], bar: WyckoffBarFeatures, tr: WyckoffRange | None) -> float:
    if tr is None:
        return 0.0
    cl = _f(row, "close")
    op = _f(row, "open")
    score = 0.0
    if cl > tr.high:
        score += 26
    if cl > op:
        score += 10
    if bar.close_pos >= 0.7:
        score += 16
    if bar.range_rel20 >= 1.05:
        score += 14
    if bar.vol_rel20 >= 1.05:
        score += 14
    if tr.width_pct >= 0.08:
        score += 10
    if bar.upper_wick > bar.spread * 0.45:
        score -= 14
    return round(_clamp(score), 2)


def score_sow(row: dict[str, Any], bar: WyckoffBarFeatures, tr: WyckoffRange | None) -> float:
    if tr is None:
        return 0.0
    cl = _f(row, "close")
    op = _f(row, "open")
    score = 0.0
    if cl < tr.low:
        score += 26
    if cl < op:
        score += 10
    if bar.close_pos <= 0.3:
        score += 16
    if bar.range_rel20 >= 1.05:
        score += 14
    if bar.vol_rel20 >= 1.05:
        score += 14
    if tr.width_pct >= 0.08:
        score += 10
    if bar.lower_wick > bar.spread * 0.45:
        score -= 14
    return round(_clamp(score), 2)


def score_dry_test(row: dict[str, Any], bar: WyckoffBarFeatures, tr: WyckoffRange | None) -> float:
    if tr is None:
        return 0.0
    lo = _f(row, "low")
    hi = _f(row, "high")
    cl = _f(row, "close")
    score = 0.0
    near_support = abs(_pct(lo, tr.low)) <= 0.018 or abs(_pct(cl, tr.low)) <= 0.018
    near_resistance = abs(_pct(hi, tr.high)) <= 0.018 or abs(_pct(cl, tr.high)) <= 0.018
    if near_support or near_resistance:
        score += 28
    if bar.vol_rel20 <= 0.85:
        score += 24
    elif bar.vol_rel20 <= 1.0:
        score += 14
    if bar.range_rel20 <= 0.9:
        score += 18
    if near_support and bar.close_pos >= 0.5:
        score += 12
    if near_resistance and bar.close_pos <= 0.5:
        score += 12
    return round(_clamp(score), 2)


def score_effort_result(bar: WyckoffBarFeatures) -> tuple[float, float]:
    """Return (absorptionScore, distributionScore) from effort/result mismatch."""
    absorption = 0.0
    distribution = 0.0
    high_effort = bar.vol_rel20 >= 1.35
    small_result = bar.range_rel20 <= 0.95 or bar.body <= bar.spread * 0.35
    if high_effort and small_result:
        if bar.close_pos >= 0.5:
            absorption += 42
        else:
            distribution += 42
    if bar.lower_wick >= bar.spread * 0.4 and bar.vol_rel20 >= 1.0:
        absorption += 24
    if bar.upper_wick >= bar.spread * 0.4 and bar.vol_rel20 >= 1.0:
        distribution += 24
    if bar.close_pos >= 0.72 and bar.vol_rel20 >= 1.05:
        absorption += 12
    if bar.close_pos <= 0.28 and bar.vol_rel20 >= 1.05:
        distribution += 12
    return round(_clamp(absorption), 2), round(_clamp(distribution), 2)


def combine_scores(rows: list[dict[str, Any]], idx: int, symbol: str | None = None, lookback: int = 60) -> WyckoffSnapshot:
    row = rows[idx]
    close = _f(row, "close")
    bar = bar_features(rows, idx)
    tr = detect_trading_range(rows, idx, lookback=lookback)

    spring = score_spring(row, bar, tr)
    upthrust = score_upthrust(row, bar, tr)
    sos = score_sos(row, bar, tr)
    sow = score_sow(row, bar, tr)
    dry = score_dry_test(row, bar, tr)
    absorption, distribution = score_effort_result(bar)

    trend30 = _trend_score(rows, idx, 30)
    in_range_bonus = 0.0
    if tr is not None and tr.low <= close <= tr.high:
        in_range_bonus = 10.0

    markup = _clamp(0.34 * spring + 0.28 * sos + 0.18 * dry + 0.20 * absorption + max(0, trend30) * 80)
    markdown = _clamp(0.34 * upthrust + 0.28 * sow + 0.18 * dry + 0.20 * distribution + max(0, -trend30) * 80)
    range_continue = _clamp(in_range_bonus + 0.28 * dry + 0.18 * (100 - max(sos, sow)) + (tr.width_pct * 120 if tr else 0))

    if markup >= max(markdown, range_continue) and markup >= 45:
        bias = "markup"
    elif markdown >= max(markup, range_continue) and markdown >= 45:
        bias = "markdown"
    elif range_continue >= 38:
        bias = "range"
    else:
        bias = "neutral"

    events: list[str] = []
    if spring >= 55:
        events.append("spring")
    if upthrust >= 55:
        events.append("upthrust")
    if sos >= 55:
        events.append("SOS")
    if sow >= 55:
        events.append("SOW")
    if dry >= 55:
        events.append("dry_test")
    if absorption >= 50:
        events.append("absorption")
    if distribution >= 50:
        events.append("distribution")

    scores = WyckoffScores(
        springScore=spring,
        upthrustScore=upthrust,
        sosScore=sos,
        sowScore=sow,
        dryTestScore=dry,
        absorptionScore=absorption,
        distributionScore=distribution,
        markupReadinessScore=round(markup, 2),
        markdownReadinessScore=round(markdown, 2),
        rangeContinuationScore=round(range_continue, 2),
        bias=bias,
    )
    return WyckoffSnapshot(
        symbol=symbol,
        time=row.get("time"),
        close=round(close, 4),
        bar=bar,
        range=tr,
        scores=scores,
        events=events,
    )


def latest_snapshot(rows: list[dict[str, Any]], symbol: str | None = None, lookback: int = 60) -> dict[str, Any]:
    clean = [r for r in rows if all(k in r for k in ("open", "high", "low", "close", "volume"))]
    if len(clean) < 30:
        raise ValueError("not enough OHLCV rows for Wyckoff snapshot")
    return combine_scores(clean, len(clean) - 1, symbol=symbol, lookback=lookback).to_dict()


def snapshots_for_rows(rows: list[dict[str, Any]], symbol: str | None = None, lookback: int = 60, min_bars: int = 80) -> list[dict[str, Any]]:
    clean = [r for r in rows if all(k in r for k in ("open", "high", "low", "close", "volume"))]
    out: list[dict[str, Any]] = []
    for idx in range(max(30, min_bars), len(clean)):
        out.append(combine_scores(clean, idx, symbol=symbol, lookback=lookback).to_dict())
    return out


__all__ = [
    "WyckoffBarFeatures",
    "WyckoffRange",
    "WyckoffScores",
    "WyckoffSnapshot",
    "latest_snapshot",
    "snapshots_for_rows",
    "combine_scores",
    "detect_trading_range",
    "bar_features",
]
