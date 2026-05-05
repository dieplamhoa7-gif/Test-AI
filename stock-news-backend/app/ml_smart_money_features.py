from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import math
import pandas as pd


def _num(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except Exception:
        return default


def _safe(v: Any, digits: int = 4) -> float | None:
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return None
        return round(x, digits)
    except Exception:
        return None


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "time" in out.columns:
        out["time"] = pd.to_datetime(out["time"], errors="coerce")
        out = out.sort_values("time")
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in out.columns:
            out[col] = 0
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)


def anchored_vwap_features(df: pd.DataFrame, lookback: int = 55) -> dict[str, Any]:
    """VWAP-style features inspired by YinYangAlgorithms.

    Local/model feature only. It does not emit buy/sell advice by itself.
    Anchors VWAP to recent swing high/low window and scores price position,
    slope, and band deviation.
    """
    d = _normalize_ohlcv(df).tail(max(lookback, 20)).copy()
    if len(d) < 10:
        return {"available": False, "reason": "not_enough_data"}
    typical = (d["high"] + d["low"] + d["close"]) / 3.0
    vol = d["volume"].replace(0, pd.NA).fillna(1.0)
    pv = typical * vol
    vwap = pv.cumsum() / vol.cumsum()
    dev = (typical - vwap).rolling(20, min_periods=5).std().fillna(0)
    upper1 = vwap + dev
    lower1 = vwap - dev
    price = _num(d["close"].iloc[-1])
    last_vwap = _num(vwap.iloc[-1])
    prev_vwap = _num(vwap.iloc[-5] if len(vwap) >= 5 else vwap.iloc[0])
    slope_pct = (last_vwap / prev_vwap - 1) * 100 if prev_vwap else 0.0
    band_width = _num(upper1.iloc[-1] - lower1.iloc[-1])
    z = (price - last_vwap) / band_width if band_width else 0.0
    if price >= last_vwap and slope_pct > 0.2:
        regime = "above_rising_vwap"
    elif price >= last_vwap:
        regime = "above_flat_vwap"
    elif slope_pct < -0.2:
        regime = "below_falling_vwap"
    else:
        regime = "below_flat_vwap"
    return {
        "available": True,
        "lookback": lookback,
        "vwap": _safe(last_vwap, 2),
        "vwapSlopePct5": _safe(slope_pct, 3),
        "vwapUpper1": _safe(upper1.iloc[-1], 2),
        "vwapLower1": _safe(lower1.iloc[-1], 2),
        "vwapZ": _safe(z, 3),
        "regime": regime,
        "aboveVwap": bool(price >= last_vwap),
    }


def donchian_smart_money_structure(df: pd.DataFrame, window: int = 20) -> dict[str, Any]:
    """ICT/Smart-Money-inspired Donchian structure features.

    Detects break of structure (BOS), change of character (CHoCH), premium/
    discount position, and liquidity sweep around Donchian extremes.
    """
    d = _normalize_ohlcv(df).copy()
    if len(d) < window + 5:
        return {"available": False, "reason": "not_enough_data"}
    hi = d["high"].rolling(window, min_periods=window).max().shift(1)
    lo = d["low"].rolling(window, min_periods=window).min().shift(1)
    mid = (hi + lo) / 2.0
    close = d["close"]
    high = d["high"]
    low = d["low"]
    last_hi = _num(hi.iloc[-1])
    last_lo = _num(lo.iloc[-1])
    last_mid = _num(mid.iloc[-1])
    price = _num(close.iloc[-1])
    prev_price = _num(close.iloc[-2])
    bos_up = bool(price > last_hi) if last_hi else False
    bos_down = bool(price < last_lo) if last_lo else False
    prev_above_mid = prev_price >= _num(mid.iloc[-2], last_mid)
    now_above_mid = price >= last_mid if last_mid else False
    choch = "bullish_choch" if (not prev_above_mid and now_above_mid) else "bearish_choch" if (prev_above_mid and not now_above_mid) else "none"
    sweep_high = bool(high.iloc[-1] > last_hi and price < last_hi) if last_hi else False
    sweep_low = bool(low.iloc[-1] < last_lo and price > last_lo) if last_lo else False
    pos = (price - last_lo) / (last_hi - last_lo) if last_hi and last_lo and last_hi > last_lo else 0.5
    zone = "discount" if pos < 0.382 else "premium" if pos > 0.618 else "equilibrium"
    if bos_up:
        structure = "bullish_bos"
    elif bos_down:
        structure = "bearish_bos"
    elif choch != "none":
        structure = choch
    else:
        structure = "range"
    return {
        "available": True,
        "window": window,
        "donchianHigh": _safe(last_hi, 2),
        "donchianLow": _safe(last_lo, 2),
        "donchianMid": _safe(last_mid, 2),
        "positionPct": _safe(pos * 100, 2),
        "zone": zone,
        "structure": structure,
        "bosUp": bos_up,
        "bosDown": bos_down,
        "choch": choch,
        "liquiditySweepHigh": sweep_high,
        "liquiditySweepLow": sweep_low,
    }


def build_ml_features(df: pd.DataFrame) -> dict[str, Any]:
    vwap = anchored_vwap_features(df)
    smc20 = donchian_smart_money_structure(df, 20)
    smc55 = donchian_smart_money_structure(df, 55)
    score = 50.0
    if vwap.get("aboveVwap"):
        score += 10
    if _num(vwap.get("vwapSlopePct5")) > 0:
        score += 8
    if smc20.get("bosUp") or smc20.get("choch") == "bullish_choch":
        score += 12
    if smc20.get("liquiditySweepLow"):
        score += 8
    if smc20.get("zone") == "discount":
        score += 5
    if smc20.get("bosDown") or smc20.get("choch") == "bearish_choch":
        score -= 15
    if vwap.get("regime") == "below_falling_vwap":
        score -= 12
    score = max(0, min(100, score))
    return {
        "version": "ml-smart-money-features-v1",
        "vwapYinYang": vwap,
        "ictDonchian20": smc20,
        "ictDonchian55": smc55,
        "mlFeatureScore": round(score, 2),
        "note": "Local/model feature output only; frontend should consume summary output, not formulas/model.",
    }
