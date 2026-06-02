"""
candlesticks.py — Mẫu hình nến.
Dùng TA-Lib nếu có, fallback custom. Chỉ lấy tín hiệu trong `recent_bars` cuối.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .core import HAS_TALIB

if HAS_TALIB:
    import talib

# tên TA-Lib -> (nhãn, hướng mặc định)
_TALIB_FUNCS = {
    "CDLHAMMER": ("Hammer", "bullish"),
    "CDLINVERTEDHAMMER": ("Inverted Hammer", "bullish"),
    "CDLENGULFING": ("Engulfing", None),
    "CDLDOJI": ("Doji", "neutral"),
    "CDLSHOOTINGSTAR": ("Shooting Star", "bearish"),
    "CDLHANGINGMAN": ("Hanging Man", "bearish"),
    "CDLMORNINGSTAR": ("Morning Star", "bullish"),
    "CDLEVENINGSTAR": ("Evening Star", "bearish"),
    "CDLPIERCING": ("Piercing", "bullish"),
    "CDLDARKCLOUDCOVER": ("Dark Cloud Cover", "bearish"),
    "CDL3WHITESOLDIERS": ("Three White Soldiers", "bullish"),
    "CDL3BLACKCROWS": ("Three Black Crows", "bearish"),
    "CDLHARAMI": ("Harami", None),
    "CDLMARUBOZU": ("Marubozu", None),
    "CDLMORNINGDOJISTAR": ("Morning Doji Star", "bullish"),
    "CDLEVENINGDOJISTAR": ("Evening Doji Star", "bearish"),
    "CDLSPINNINGTOP": ("Spinning Top", "neutral"),
    "CDL3INSIDE": ("Three Inside", None),
    "CDL3OUTSIDE": ("Three Outside", None),
    "CDLBELTHOLD": ("Belt Hold", None),
}


def detect_candlesticks(df: pd.DataFrame, recent_bars: int = 30) -> list[dict]:
    if HAS_TALIB:
        sigs = _talib_candles(df)
    else:
        sigs = _custom_candles(df)
    cutoff = len(df) - recent_bars
    return [s for s in sigs if s["_idx"] >= cutoff]


def _mk(df, idx, name, direction):
    row = df.iloc[idx]
    return {
        "type": name, "category": "candlestick", "tier": 1, "direction": direction,
        "time": row["date"].strftime("%Y-%m-%d"), "price": float(row["close"]),
        "score": 55.0, "confidence": "low", "status": "completed",
        "_idx": int(idx),
        "evidence": {"volumeRatio": _vr(df, idx)},
    }


def _vr(df, idx):
    v = df["vol_ratio"].iloc[idx]
    return round(float(v), 2) if pd.notna(v) else None


def _talib_candles(df):
    o, h, l, c = (df[x].values.astype(float) for x in ["open", "high", "low", "close"])
    out = []
    for fn, (label, fixed_dir) in _TALIB_FUNCS.items():
        try:
            res = getattr(talib, fn)(o, h, l, c)
        except Exception:
            continue
        for i in np.nonzero(res)[0]:
            direction = fixed_dir or ("bullish" if res[i] > 0 else "bearish")
            out.append(_mk(df, int(i), label, direction))
    return out


def _custom_candles(df):
    """Fallback: hammer, shooting star, doji, engulfing, marubozu."""
    out = []
    o, h, l, c = (df[x].values for x in ["open", "high", "low", "close"])
    for i in range(1, len(df)):
        body = abs(c[i] - o[i])
        rng = h[i] - l[i]
        if rng <= 0:
            continue
        upper = h[i] - max(c[i], o[i])
        lower = min(c[i], o[i]) - l[i]
        # Hammer
        if lower > 2 * body and lower / rng > 0.45 and upper / rng < 0.2:
            out.append(_mk(df, i, "Hammer", "bullish"))
        # Shooting star
        elif upper > 2 * body and upper / rng > 0.45 and lower / rng < 0.2:
            out.append(_mk(df, i, "Shooting Star", "bearish"))
        # Doji
        elif body / rng < 0.1:
            out.append(_mk(df, i, "Doji", "neutral"))
        # Marubozu
        elif body / rng > 0.85:
            out.append(_mk(df, i, "Marubozu", "bullish" if c[i] > o[i] else "bearish"))
        # Engulfing
        prev_body = abs(c[i - 1] - o[i - 1])
        if c[i - 1] < o[i - 1] and c[i] > o[i] and c[i] >= o[i - 1] and o[i] <= c[i - 1] and body > prev_body:
            out.append(_mk(df, i, "Bullish Engulfing", "bullish"))
        elif c[i - 1] > o[i - 1] and c[i] < o[i] and o[i] >= c[i - 1] and c[i] <= o[i - 1] and body > prev_body:
            out.append(_mk(df, i, "Bearish Engulfing", "bearish"))
    return out
