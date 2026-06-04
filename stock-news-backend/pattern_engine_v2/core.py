"""
core.py — Data loading, indicators, pivot/ZigZag engine.

Tất cả detector dùng chung pivot list + indicator DataFrame từ đây.
Nguyên tắc: KHÔNG dùng dữ liệu tương lai. Mọi tính toán tại bar i chỉ
dùng dữ liệu <= i (rolling/expanding). Pivot có confirm-lag để tránh nhìn trộm.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

# ----- optional libs với fallback -----
try:
    import talib  # noqa
    HAS_TALIB = True
except Exception:
    HAS_TALIB = False

try:
    from scipy.signal import find_peaks  # noqa
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False


# =====================================================================
# DATA LOADER
# =====================================================================
def load_data(path: str | Path) -> pd.DataFrame:
    """Đọc CSV hoặc JSON OHLCV -> DataFrame chuẩn: date/open/high/low/close/volume."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        df.columns = [str(c).strip().lstrip("\ufeff").lower() for c in df.columns]
    else:
        raw = json.loads(path.read_text(encoding="utf-8"))
        rows = raw.get("rows", raw) if isinstance(raw, dict) else raw
        df = pd.DataFrame(rows)
        df.columns = [str(c).strip().lower() for c in df.columns]

    if "time" in df.columns:
        df = df.rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    return df


def infer_timeframe(df: pd.DataFrame) -> str:
    gap = df["date"].diff().dropna().dt.days.median()
    if gap <= 2:
        return "daily"
    if gap <= 10:
        return "weekly"
    return "monthly"


# =====================================================================
# INDICATORS (tự tính bằng pandas, không phụ thuộc TA-Lib)
# =====================================================================
def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    df["sma20"] = c.rolling(20).mean()
    df["sma50"] = c.rolling(50).mean()
    df["ema20"] = c.ewm(span=20, adjust=False).mean()
    df["ema50"] = c.ewm(span=50, adjust=False).mean()

    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    df["atr20"] = tr.rolling(20).mean()
    df["atr_pct"] = df["atr20"] / c * 100

    df["vol20"] = v.rolling(20).mean()
    df["vol_ratio"] = v / df["vol20"]

    df["rsi14"] = _rsi(c, 14)

    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df


# =====================================================================
# PIVOT ENGINE
# =====================================================================
def find_pivots(df: pd.DataFrame, distance: int = 3, prom_mult: float = 0.6) -> list[dict]:
    """
    Trả về pivot highs/lows. Prominence động theo ATR để thích ứng biến động.
    confirm_lag = distance: pivot tại i chỉ được xác nhận sau `distance` bar -> không nhìn trộm.
    """
    high = df["high"].values
    low = df["low"].values
    atr = df["atr20"].fillna(df["close"].iloc[-1] * 0.03).values
    base_prom = float(np.nanmedian(atr) * prom_mult)
    pivots: list[dict] = []

    if HAS_SCIPY:
        ph, _ = find_peaks(high, distance=distance, prominence=base_prom)
        pl, _ = find_peaks(-low, distance=distance, prominence=base_prom)
    else:
        ph = _naive_peaks(high, distance)
        pl = _naive_peaks(-np.array(low), distance)

    for i in ph:
        pivots.append({"index": int(i), "date": df["date"].iloc[i],
                       "value": float(high[i]), "kind": "high"})
    for i in pl:
        pivots.append({"index": int(i), "date": df["date"].iloc[i],
                       "value": float(low[i]), "kind": "low"})
    pivots.sort(key=lambda p: p["index"])
    return pivots


def _naive_peaks(arr, distance):
    out = []
    n = len(arr)
    for i in range(distance, n - distance):
        window = arr[i - distance:i + distance + 1]
        if arr[i] == window.max() and (arr[i] > arr[i - 1] or arr[i] > arr[i + 1]):
            out.append(i)
    return out


def split_pivots(pivots: list[dict]):
    highs = [p for p in pivots if p["kind"] == "high"]
    lows = [p for p in pivots if p["kind"] == "low"]
    return highs, lows


# =====================================================================
# Helpers chung cho detector
# =====================================================================
def fit_line(xs, ys):
    """Linear fit -> (slope, intercept). xs là index (int)."""
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    if len(xs) < 2:
        return 0.0, float(ys[0]) if len(ys) else 0.0
    slope, intercept = np.polyfit(xs, ys, 1)
    return float(slope), float(intercept)


def line_val(slope, intercept, x):
    return slope * x + intercept


def pct(a, b):
    return abs(a - b) / b if b else 0.0


def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))
