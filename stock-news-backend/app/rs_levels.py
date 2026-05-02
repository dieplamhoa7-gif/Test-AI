from __future__ import annotations
from typing import Any
import pandas as pd
from .market_data import (
    _pivot_from_recent,
    _pivot_levels,
    _to_ohlc,
    _build_support_resistance,
    _safe_number,
)


def _fibonacci_levels(df: pd.DataFrame | None, lookback: int = 180) -> list[float]:
    if df is None or df.empty:
        return []
    recent = df.tail(lookback).copy()
    if recent.empty or "high" not in recent.columns or "low" not in recent.columns:
        return []
    high = float(pd.to_numeric(recent["high"], errors="coerce").max())
    low = float(pd.to_numeric(recent["low"], errors="coerce").min())
    if not high or not low or high <= low:
        return []
    return [round(high - (high - low) * x, 2) for x in (0.236, 0.382, 0.5, 0.618, 0.786)]


def calc_rs_levels_only(
    last_price: float,
    ref_price: float,
    open_price: float,
    high_price: float,
    low_price: float,
    avg_price: float,
    history_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Calculate support/resistance only, without full _calc_technical indicators.

    Uses the same current R/S engine as app.market_data._calc_technical:
    pivot levels + MA placeholders + swing levels + volume levels + VWAP + Donchian + Fibonacci + ATR.
    It intentionally does NOT compute RSI/MACD/ADX/Bollinger/recommendations.
    """
    pivot_day, support_day, resistance_day, support_day_2, resistance_day_2 = _pivot_levels(high_price, low_price, last_price)
    pivot_week, support_week, resistance_week, support_week_2, resistance_week_2 = _pivot_levels(high_price, low_price, last_price)
    pivot_month, support_month, resistance_month, support_month_2, resistance_month_2 = _pivot_levels(high_price, low_price, last_price)

    daily_raw = _to_ohlc(history_df, "day") if history_df is not None and not history_df.empty else pd.DataFrame()
    weekly_raw = _to_ohlc(history_df, "week") if history_df is not None and not history_df.empty else pd.DataFrame()
    monthly_raw = _to_ohlc(history_df, "month") if history_df is not None and not history_df.empty else pd.DataFrame()

    def _ma_anchors(frame_df: pd.DataFrame | None, fallback: float) -> tuple[float, float, float]:
        if frame_df is None or frame_df.empty:
            base = float(fallback or last_price)
            return base, base * 0.985, base * 0.955
        close = pd.to_numeric(frame_df["close"], errors="coerce")
        base = float(fallback or last_price)
        ma20_val = close.rolling(20, min_periods=min(20, max(5, len(close)))).mean().iloc[-1] if len(close) >= 5 else base
        ma20_local = float(ma20_val) if pd.notna(ma20_val) else base
        ma50_val = close.rolling(50, min_periods=min(50, max(10, len(close)))).mean().iloc[-1] if len(close) >= 10 else ma20_local
        ma50_local = float(ma50_val) if pd.notna(ma50_val) else ma20_local
        ma200_val = close.rolling(200, min_periods=min(200, max(20, len(close)))).mean().iloc[-1] if len(close) >= 20 else ma50_local
        ma200_local = float(ma200_val) if pd.notna(ma200_val) else ma50_local
        return ma20_local, ma50_local, ma200_local

    # R/S anchors must be computed per timeframe. Do not reuse daily MA anchors for week/month.
    if daily_raw is not None and not daily_raw.empty:
        ma20, ma50, ma200 = _ma_anchors(daily_raw, avg_price or last_price)
        ma20_week, ma50_week, ma200_week = _ma_anchors(weekly_raw, last_price)
        ma20_month, ma50_month, ma200_month = _ma_anchors(monthly_raw, last_price)
        pivot_day, support_day, resistance_day, support_day_2, resistance_day_2 = _pivot_from_recent(daily_raw, high_price, low_price, last_price, 10)
        pivot_week, support_week, resistance_week, support_week_2, resistance_week_2 = _pivot_from_recent(weekly_raw, high_price, low_price, last_price, 10)
        pivot_month, support_month, resistance_month, support_month_2, resistance_month_2 = _pivot_from_recent(monthly_raw, high_price, low_price, last_price, 10)
    else:
        ma20, ma50, ma200 = _ma_anchors(pd.DataFrame(), avg_price or last_price)
        ma20_week, ma50_week, ma200_week = ma20, ma50, ma200
        ma20_month, ma50_month, ma200_month = ma20, ma50, ma200

    sr_day = _build_support_resistance(last_price, daily_raw, pivot_day, support_day, resistance_day, support_day_2, resistance_day_2, ma20, ma50, ma200)
    sr_week = _build_support_resistance(last_price, weekly_raw, pivot_week, support_week, resistance_week, support_week_2, resistance_week_2, ma20_week, ma50_week, ma200_week)
    sr_month = _build_support_resistance(last_price, monthly_raw, pivot_month, support_month, resistance_month, support_month_2, resistance_month_2, ma20_month, ma50_month, ma200_month)
    fib_day = _fibonacci_levels(daily_raw, 180)
    fib_week = _fibonacci_levels(weekly_raw, 80)
    fib_month = _fibonacci_levels(monthly_raw, 36)

    return {
        "pivotDay": _safe_number(pivot_day, 2),
        "supportDay": _safe_number(sr_day["activeSupport"], 2),
        "resistanceDay": _safe_number(sr_day["activeResistance"], 2),
        "supportDay2": _safe_number(support_day_2, 2),
        "resistanceDay2": _safe_number(resistance_day_2, 2),
        "supportLevelsDay": [round(float(x), 1) for x in sr_day["supports"]],
        "resistanceLevelsDay": [round(float(x), 1) for x in sr_day["resistances"]],
        "nearSupportDay": _safe_number(sr_day["nearSupport"], 1),
        "nextSupportDay": _safe_number(sr_day["nextSupport"], 1),
        "nearResistanceDay": _safe_number(sr_day["nearResistance"], 1),
        "nextResistanceDay": _safe_number(sr_day["nextResistance"], 1),
        "activeSupportDay": _safe_number(sr_day["activeSupport"], 1),
        "activeResistanceDay": _safe_number(sr_day["activeResistance"], 1),
        "supportZoneDay": sr_day["supportZone"],
        "resistanceZoneDay": sr_day["resistanceZone"],
        "srStatusDay": sr_day["srStatus"],
        "pivotWeek": _safe_number(pivot_week, 2),
        "supportWeek": _safe_number(sr_week["activeSupport"], 2),
        "resistanceWeek": _safe_number(sr_week["activeResistance"], 2),
        "supportLevelsWeek": [round(float(x), 1) for x in sr_week["supports"]],
        "resistanceLevelsWeek": [round(float(x), 1) for x in sr_week["resistances"]],
        "activeSupportWeek": _safe_number(sr_week["activeSupport"], 1),
        "activeResistanceWeek": _safe_number(sr_week["activeResistance"], 1),
        "srStatusWeek": sr_week["srStatus"],
        "pivotMonth": _safe_number(pivot_month, 2),
        "supportMonth": _safe_number(sr_month["activeSupport"], 2),
        "resistanceMonth": _safe_number(sr_month["activeResistance"], 2),
        "supportLevelsMonth": [round(float(x), 1) for x in sr_month["supports"]],
        "resistanceLevelsMonth": [round(float(x), 1) for x in sr_month["resistances"]],
        "activeSupportMonth": _safe_number(sr_month["activeSupport"], 1),
        "activeResistanceMonth": _safe_number(sr_month["activeResistance"], 1),
        "srStatusMonth": sr_month["srStatus"],
        "atr": _safe_number(sr_day["atr"], 1),
        "vwapDay": _safe_number(sr_day.get("vwap"), 1),
        "donchianHighDay": _safe_number(sr_day.get("donchianHigh"), 1),
        "donchianLowDay": _safe_number(sr_day.get("donchianLow"), 1),
        "donchianMidDay": _safe_number(sr_day.get("donchianMid"), 1),
        "marketStructureDay": sr_day.get("marketStructure"),
        "fibonacciLevelsDay": fib_day,
        "fibonacciLevelsWeek": fib_week,
        "fibonacciLevelsMonth": fib_month,
        "ma20Anchor": _safe_number(ma20, 2),
        "ma50Anchor": _safe_number(ma50, 2),
        "ma200Anchor": _safe_number(ma200, 2),
    }
