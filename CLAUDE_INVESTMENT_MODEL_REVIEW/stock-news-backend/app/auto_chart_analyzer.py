"""
auto_chart_analyzer — Orchestrator: gọi tất cả detector + format JSON
                      tương thích TradingView Lightweight Charts API.

Module này là entry point duy nhất frontend cần gọi:
    from app.auto_chart_analyzer import analyze_symbol
    result = analyze_symbol("FPT", ohlc_df)
    # result là dict JSON-safe, vẽ trực tiếp lên chart TradingView Lightweight

Schema output (TradingView Lightweight Charts):
{
  "symbol": "FPT", "asOfDate": "2026-05-26", "asOfPrice": 73.5,
  "trendlines": [                          # → chart.addLineSeries() + series.setData(points)
    {"id", "type", "points": [{time, value}, {time, value}], "lineStyle": {color, lineWidth, lineStyle}, ...}
  ],
  "parallelChannels": [                    # → 2 lineSeries (main + parallel)
    {"id", "type", "mainLine": {points}, "parallelLine": {points}, ...}
  ],
  "pitchforks": [                          # → 3 lineSeries (median, upper, lower)
    {"id", "type", "medianLine": {points}, "upperLine": {points}, "lowerLine": {points}, ...}
  ],
  "linregChannels": [                      # → 3 lineSeries
    {"id", "type", "meanLine", "upperLine", "lowerLine", ...}
  ],
  "srLevels": [                            # → series.createPriceLine() horizontal
    {"id", "type", "price", "zone", "priceLine": {price, color, lineWidth, lineStyle, title}, ...}
  ],
  "patterns": [                            # → các shape annotation (polygon/path)
    {"id", "name", "category", "keyPoints": {...}, "annotation": {time, text, position, shape, color}}
  ],
  "candlestickSignals": [                  # → series.setMarkers()
    {"id", "name", "marker": {time, position, color, shape, text}}
  ],
  "summary": {...}
}
"""

from __future__ import annotations
from dataclasses import asdict
from typing import Any
import datetime as dt
import pandas as pd

from app.auto_chart_core import TrendlineDetector, SRLevelDetector
from app.auto_chart_advanced_trendlines import (
    ParallelChannelDetector, AndrewsPitchforkDetector, LinearRegressionChannelDetector,
)
from app.auto_chart_patterns import (
    ReversalPatternDetector, ContinuationPatternDetector, CandlestickDetector,
)


# ─────────────────────────────────────────────────────────────────────────────
# Color theme & line style cho TradingView Lightweight Charts
# ─────────────────────────────────────────────────────────────────────────────
COLORS = {
    "uptrend":            {"color": "#26a69a", "lineWidth": 2, "lineStyle": 0},  # Solid green
    "downtrend":          {"color": "#ef5350", "lineWidth": 2, "lineStyle": 0},  # Solid red
    "uptrend_channel":    {"color": "#80cbc4", "lineWidth": 1, "lineStyle": 2},  # Dashed light green
    "downtrend_channel":  {"color": "#ffab91", "lineWidth": 1, "lineStyle": 2},  # Dashed light red
    "pitchfork_median":   {"color": "#ffa726", "lineWidth": 2, "lineStyle": 0},  # Solid orange
    "pitchfork_branch":   {"color": "#ffcc80", "lineWidth": 1, "lineStyle": 1},  # Dotted orange
    "linreg_mean":        {"color": "#42a5f5", "lineWidth": 2, "lineStyle": 0},  # Solid blue
    "linreg_band":        {"color": "#90caf9", "lineWidth": 1, "lineStyle": 1},  # Dotted light blue
    "support":            {"color": "#26a69a", "lineWidth": 2, "lineStyle": 2},  # Dashed green
    "resistance":         {"color": "#ef5350", "lineWidth": 2, "lineStyle": 2},  # Dashed red
    "pattern_bullish":    {"color": "#26a69a"},
    "pattern_bearish":    {"color": "#ef5350"},
    "candle_bullish":     {"color": "#00c853"},
    "candle_bearish":     {"color": "#d50000"},
}

# Marker shape mapping
SHAPE_BY_PATTERN = {
    "hammer": "arrowUp", "bullish_engulfing": "arrowUp", "morning_star": "arrowUp",
    "shooting_star": "arrowDown", "bearish_engulfing": "arrowDown", "evening_star": "arrowDown",
}


# ─────────────────────────────────────────────────────────────────────────────
# Format helpers
# ─────────────────────────────────────────────────────────────────────────────
def _fmt_trendline(tl) -> dict:
    style = dict(COLORS[tl.type])
    return {
        "id": tl.id, "type": tl.type, "points": tl.points,
        "slopePerBar": round(tl.slope_per_bar, 5), "touches": tl.touches,
        "lengthBars": tl.length_bars, "rSquared": tl.r_squared,
        "valid": tl.valid, "score": tl.score,
        "touchPoints": tl.touch_points or [],
        "reversalConfirmed": bool(getattr(tl, 'reversal_confirmed', False)),
        "touchRulePass": bool(tl.touches >= 4 or (tl.touches == 3 and getattr(tl, 'reversal_confirmed', False))),
        "lineStyle": style,
    }


def _fmt_parallel_channel(ch) -> dict:
    main_style = dict(COLORS[ch.type])
    par_style = dict(COLORS[ch.type])
    par_style["lineStyle"] = 2  # dashed cho line song song
    return {
        "id": ch.id, "type": ch.type, "baseTrendlineId": ch.base_trendline_id,
        "mainLine": {**ch.main_line, "lineStyle": main_style},
        "parallelLine": {**ch.parallel_line, "lineStyle": par_style},
        "widthAtr": ch.width, "score": ch.score,
    }


def _fmt_pitchfork(pf) -> dict:
    median_style = dict(COLORS["pitchfork_median"])
    branch_style = dict(COLORS["pitchfork_branch"])
    return {
        "id": pf.id, "type": pf.type,
        "anchors": {"p1": pf.anchor_p1, "p2": pf.anchor_p2, "p3": pf.anchor_p3},
        "medianLine": {**pf.median_line, "lineStyle": median_style},
        "upperLine": {**pf.upper_line, "lineStyle": branch_style},
        "lowerLine": {**pf.lower_line, "lineStyle": branch_style},
        "score": pf.score,
    }


def _fmt_linreg(ch) -> dict:
    mean_style = dict(COLORS["linreg_mean"])
    band_style = dict(COLORS["linreg_band"])
    return {
        "id": ch.id, "type": ch.type,
        "windowStartTime": ch.window_start_time, "windowEndTime": ch.window_end_time,
        "slopePerBar": round(ch.slope_per_bar, 5), "rSquared": ch.r_squared,
        "std": ch.std,
        "meanLine": {**ch.mean_line, "lineStyle": mean_style},
        "upperLine": {**ch.upper_line, "lineStyle": band_style},
        "lowerLine": {**ch.lower_line, "lineStyle": band_style},
    }


def _fmt_sr(level) -> dict:
    style = dict(COLORS[level.type])
    title = f"{'S' if level.type == 'support' else 'R'} {level.price:.2f} • {level.confidence:.0f}%"
    return {
        "id": level.id, "type": level.type,
        "price": level.price, "zone": level.zone,
        "sources": level.sources, "touches": level.touches,
        "confidence": level.confidence,
        "touchPoints": level.touch_points or [],
        "reversalConfirmed": bool(getattr(level, 'reversal_confirmed', False)),
        "touchRulePass": bool(level.touches >= 4 or (level.touches == 3 and getattr(level, 'reversal_confirmed', False))),
        "priceLine": {
            "price": level.price,
            "color": style["color"], "lineWidth": style["lineWidth"],
            "lineStyle": style["lineStyle"], "title": title,
        },
    }


def _fmt_pattern(p) -> dict:
    color = COLORS["pattern_bullish"]["color"] if "bullish" in p.category else COLORS["pattern_bearish"]["color"]
    return {
        "id": p.id, "name": p.name, "category": p.category,
        "startTime": p.start_time, "endTime": p.end_time,
        "keyPoints": p.key_points,
        "pivotPrice": p.pivot_price, "targetPrice": p.target_price, "stopPrice": p.stop_price,
        "completion": p.completion, "description": p.description,
        "annotation": {
            "time": p.end_time, "text": p.name.replace("_", " ").title(),
            "position": "aboveBar" if "bearish" in p.category else "belowBar",
            "color": color,
            "shape": "arrowDown" if "bearish" in p.category else "arrowUp",
        },
    }


def _fmt_candle(p) -> dict:
    color = COLORS["candle_bullish"]["color"] if "bullish" in p.category else COLORS["candle_bearish"]["color"]
    shape = SHAPE_BY_PATTERN.get(p.name, "circle")
    return {
        "id": p.id, "name": p.name, "category": p.category,
        "time": p.end_time,
        "marker": {
            "time": p.end_time,
            "position": "belowBar" if "bullish" in p.category else "aboveBar",
            "color": color, "shape": shape,
            "text": p.description,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def analyze_symbol(symbol: str, df: pd.DataFrame, *,
                   detect_patterns: bool = True,
                   detect_advanced_trendlines: bool = True) -> dict:
    """
    Phân tích chart 1 symbol → trả dict JSON sẵn sàng cho TradingView Lightweight Charts.

    Args:
        symbol: ticker
        df: OHLC DataFrame columns [time, open, high, low, close, volume]
        detect_patterns: có chạy ReversalPatternDetector + ContinuationPatternDetector + Candlestick không
        detect_advanced_trendlines: có chạy ParallelChannel + Pitchfork + LinregChannel không

    Returns:
        dict JSON-safe đầy đủ trendlines, channels, S/R, patterns, candlestick signals.
    """
    if df is None or df.empty:
        return {"symbol": symbol, "error": "empty dataframe"}
    df = df.copy().reset_index(drop=True)
    for c in ["open", "high", "low", "close", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    last_row = df.iloc[-1]
    price = float(last_row["close"])

    # Core: trendlines + S/R
    tl_det = TrendlineDetector()
    sr_det = SRLevelDetector()
    trendlines = tl_det.detect(df)
    sr_levels = sr_det.detect(df)

    # Advanced trendlines
    parallel_channels = []
    pitchforks = []
    linreg_channels = []
    if detect_advanced_trendlines:
        parallel_channels = ParallelChannelDetector().detect(df, trendlines)
        pitchforks = AndrewsPitchforkDetector().detect(df)
        linreg_channels = LinearRegressionChannelDetector().detect(df)

    # Patterns
    reversal_patterns = []
    continuation_patterns = []
    candlestick_signals = []
    if detect_patterns:
        reversal_patterns = ReversalPatternDetector().detect(df)
        continuation_patterns = ContinuationPatternDetector().detect(df)
        candlestick_signals = CandlestickDetector().detect(df)

    # Tìm nearest S/R
    supports = sorted([s for s in sr_levels if s.type == "support"],
                      key=lambda x: -x.price)  # gần giá nhất ở đầu (vì support < price)
    resistances = sorted([r for r in sr_levels if r.type == "resistance"],
                         key=lambda x: x.price)  # gần giá nhất ở đầu (resistance > price)
    nearest_support = supports[0].price if supports else None
    nearest_resistance = resistances[0].price if resistances else None

    # Current bias từ trendlines + patterns
    n_up = sum(1 for t in trendlines if t.type == "uptrend" and t.valid)
    n_down = sum(1 for t in trendlines if t.type == "downtrend" and t.valid)
    n_bullish_pat = sum(1 for p in (reversal_patterns + continuation_patterns) if "bullish" in p.category)
    n_bearish_pat = sum(1 for p in (reversal_patterns + continuation_patterns) if "bearish" in p.category)
    if n_up > n_down and n_bullish_pat >= n_bearish_pat:
        bias = "bullish"
    elif n_down > n_up and n_bearish_pat >= n_bullish_pat:
        bias = "bearish"
    else:
        bias = "neutral"

    payload = {
        "symbol": symbol,
        "asOfDate": str(last_row["time"].date()),
        "asOfPrice": round(price, 2),
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "trendlines": [_fmt_trendline(t) for t in trendlines],
        "parallelChannels": [_fmt_parallel_channel(c) for c in parallel_channels],
        "pitchforks": [_fmt_pitchfork(p) for p in pitchforks],
        "linregChannels": [_fmt_linreg(c) for c in linreg_channels],
        "srLevels": [_fmt_sr(s) for s in sr_levels],
        "patterns": [_fmt_pattern(p) for p in (reversal_patterns + continuation_patterns)],
        "candlestickSignals": [_fmt_candle(c) for c in candlestick_signals],
        "summary": {
            "trendlines": len(trendlines),
            "parallelChannels": len(parallel_channels),
            "pitchforks": len(pitchforks),
            "linregChannels": len(linreg_channels),
            "srLevels": len(sr_levels),
            "patterns": len(reversal_patterns) + len(continuation_patterns),
            "candlestickSignals": len(candlestick_signals),
            "currentBias": bias,
            "nearestSupport": nearest_support,
            "nearestResistance": nearest_resistance,
        },
    }
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: gọi từ web_app.py
# ─────────────────────────────────────────────────────────────────────────────
def analyze_from_history_cache(symbol: str, history_loader, *, timeframe: str = "day", **kw):
    """
    Wrapper gọi history loader (e.g. app.market_data._load_history) rồi analyze.
    Tự resample sang week/month nếu cần.
    """
    df = history_loader(symbol)
    if df is None or df.empty:
        return {"symbol": symbol, "error": "no history"}
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    if timeframe == "week":
        df = (df.set_index("time")
                .resample("W-FRI")
                .agg({"open": "first", "high": "max", "low": "min",
                      "close": "last", "volume": "sum"})
                .dropna().reset_index())
    elif timeframe == "month":
        df = (df.set_index("time")
                .resample("ME")
                .agg({"open": "first", "high": "max", "low": "min",
                      "close": "last", "volume": "sum"})
                .dropna().reset_index())
    return analyze_symbol(symbol, df, **kw)
