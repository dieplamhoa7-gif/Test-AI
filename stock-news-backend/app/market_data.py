from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic
from typing import Any
import math

import httpx
import pandas as pd

try:
    from vnstock import Listing, Quote
except Exception:  # pragma: no cover
    Listing = None
    Quote = None

DEFAULT_TICKERS = ["MWG", "FPT", "HPG", "SSI"]

MARKET_CACHE_TTL_SECONDS = 60
SYMBOL_CACHE_TTL_SECONDS = 60

_market_cache: list[dict[str, Any]] = []
_symbol_detail_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_symbol_cache: list[dict[str, str]] = []
_last_updated: str | None = None
_last_market_refresh_at: float = 0.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_ohlc(df: pd.DataFrame, frame: str) -> pd.DataFrame:
    frame = frame.lower()
    work = df.copy()
    work["time"] = pd.to_datetime(work["time"])
    work = work.sort_values("time")
    if frame == "day":
        return work.reset_index(drop=True)
    rule = {"week": "W-FRI", "month": "ME"}.get(frame)
    if not rule:
        return work.reset_index(drop=True)
    ohlc = (
        work.set_index("time")
        .resample(rule)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return ohlc


def _compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy().reset_index(drop=True)
    close = work["close"].astype(float)
    high = work["high"].astype(float)
    low = work["low"].astype(float)

    work["ma20"] = close.rolling(20).mean()
    work["ma50"] = close.rolling(50).mean()
    work["ma200"] = close.rolling(200).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    work["macd"] = ema12 - ema26
    work["signal"] = work["macd"].ewm(span=9, adjust=False).mean()
    work["histogram"] = work["macd"] - work["signal"]

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    work["rsi14"] = (100 - (100 / (1 + rs))).astype(float)

    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    work["bbMid"] = bb_mid
    work["bbUpper"] = bb_mid + bb_std * 2
    work["bbLower"] = bb_mid - bb_std * 2
    work["bbPercent"] = ((close - work["bbLower"]) / (work["bbUpper"] - work["bbLower"]).replace(0, float("nan"))).astype(float)
    work["volumeAvg20"] = work["volume"].astype(float).rolling(20).mean() if "volume" in work.columns else 0
    work["volumeRatio"] = (work["volume"].astype(float) / work["volumeAvg20"].replace(0, float("nan"))).astype(float) if "volume" in work.columns else 1

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(((up_move > down_move) & (up_move > 0)) * up_move, index=work.index).fillna(0.0).astype(float)
    minus_dm = pd.Series(((down_move > up_move) & (down_move > 0)) * down_move, index=work.index).fillna(0.0).astype(float)
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1).astype(float)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    work["plusDi"] = (100 * plus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr).astype(float)
    work["minusDi"] = (100 * minus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr).astype(float)
    dx = (((work["plusDi"] - work["minusDi"]).abs() / (work["plusDi"] + work["minusDi"]).replace(0, float("nan"))) * 100).astype(float)
    work["adx14"] = dx.ewm(alpha=1 / 14, adjust=False).mean().astype(float)
    return work


def _safe_number(value: Any, digits: int = 2) -> float | None:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(n) or math.isinf(n):
        return None
    return round(n, digits)


def _describe_trend_strength(adx: float) -> str:
    if adx >= 50:
        return "Rất mạnh"
    if adx >= 25:
        return "Mạnh"
    if adx >= 20:
        return "Trung bình"
    return "Yếu"


def _pivot_levels(high_price: float, low_price: float, close_price: float) -> tuple[float, float, float, float, float]:
    high_price = float(high_price or 0)
    low_price = float(low_price or 0)
    close_price = float(close_price or 0)
    if high_price <= 0 or low_price <= 0 or close_price <= 0:
        pivot = close_price
        support1 = close_price
        resistance1 = close_price
        support2 = close_price
        resistance2 = close_price
    else:
        pivot = (high_price + low_price + close_price) / 3
        support1 = (2 * pivot) - high_price
        resistance1 = (2 * pivot) - low_price
        support2 = pivot - (high_price - low_price)
        resistance2 = pivot + (high_price - low_price)
    return round(pivot, 2), round(support1, 2), round(resistance1, 2), round(support2, 2), round(resistance2, 2)


def _pivot_from_recent(df: pd.DataFrame | None, fallback_high: float, fallback_low: float, fallback_close: float, window: int = 10) -> tuple[float, float, float, float, float]:
    if df is None or df.empty:
        return _pivot_levels(fallback_high, fallback_low, fallback_close)
    recent = df.tail(window)
    if recent.empty:
        return _pivot_levels(fallback_high, fallback_low, fallback_close)
    high_price = float(recent["high"].mean() or fallback_high)
    low_price = float(recent["low"].mean() or fallback_low)
    close_price = float(recent["close"].mean() or fallback_close)
    return _pivot_levels(high_price, low_price, close_price)


def _dedupe_levels(levels: list[float], price: float, tolerance_pct: float = 0.35) -> list[float]:
    clean: list[float] = []
    tolerance = max(price * tolerance_pct / 100, 0.01)
    for level in sorted([float(x) for x in levels if x and x > 0]):
        if not clean or abs(level - clean[-1]) > tolerance:
            clean.append(level)
    return [round(x, 2) for x in clean]


def _strongest_levels(levels: list[float], price: float, side: str, atr: float, limit: int = 5) -> list[float]:
    """Pick hard S/R zones, not the nearest noisy ticks.

    A strong level is a price where many independent signals cluster together.
    We ignore levels too close to current price, then score clusters by:
    - number of signals inside one ATR-based zone
    - enough distance from current price to be actionable
    """
    raw = [float(x) for x in levels if x and x > 0]
    if not raw:
        return []
    min_gap = max(price * 0.025, atr * 0.85, 0.01)
    zone = max(price * 0.010, atr * 0.55, 0.01)
    if side == "support":
        pool = [x for x in raw if x < price - min_gap]
    else:
        pool = [x for x in raw if x > price + min_gap]
    if not pool:
        pool = [x for x in raw if x < price] if side == "support" else [x for x in raw if x > price]
    clusters: list[dict[str, float]] = []
    for level in sorted(pool):
        placed = False
        for cluster in clusters:
            if abs(level - cluster["center"]) <= zone:
                cluster["sum"] += level
                cluster["count"] += 1
                cluster["center"] = cluster["sum"] / cluster["count"]
                placed = True
                break
        if not placed:
            clusters.append({"center": level, "sum": level, "count": 1})
    scored: list[tuple[float, float]] = []
    for cluster in clusters:
        center = cluster["center"]
        distance_pct = abs(price - center) / price if price else 0
        distance_score = min(distance_pct / 0.08, 1.0)
        score = cluster["count"] * 10 + distance_score * 3
        scored.append((score, center))
    strongest = [center for _, center in sorted(scored, key=lambda item: item[0], reverse=True)]
    if side == "support":
        ordered = sorted(strongest, reverse=True)
    else:
        ordered = sorted(strongest)
    return [round(x, 2) for x in ordered[:limit]]


def _swing_levels(df: pd.DataFrame, window: int = 5, lookback: int = 180) -> tuple[list[float], list[float]]:
    if df is None or df.empty or len(df) < window * 2 + 1:
        return [], []
    work = df.tail(lookback).reset_index(drop=True)
    supports: list[float] = []
    resistances: list[float] = []
    for i in range(window, len(work) - window):
        low = float(work.loc[i, "low"])
        high = float(work.loc[i, "high"])
        low_slice = work.loc[i - window:i + window, "low"].astype(float)
        high_slice = work.loc[i - window:i + window, "high"].astype(float)
        if low <= float(low_slice.min()):
            supports.append(low)
        if high >= float(high_slice.max()):
            resistances.append(high)
    return supports, resistances


def _volume_levels(df: pd.DataFrame, price: float, bins: int = 10, lookback: int = 180) -> list[float]:
    if df is None or df.empty or "volume" not in df.columns or price <= 0:
        return []
    work = df.tail(lookback).dropna(subset=["close", "volume"])
    if work.empty:
        return []
    low = float(work["low"].min())
    high = float(work["high"].max())
    if high <= low:
        return []
    step = (high - low) / bins
    buckets: dict[int, float] = {}
    for _, row in work.iterrows():
        idx = min(bins - 1, max(0, int((float(row["close"]) - low) / step)))
        buckets[idx] = buckets.get(idx, 0.0) + float(row.get("volume") or 0)
    top = sorted(buckets.items(), key=lambda item: item[1], reverse=True)[:4]
    return [low + (idx + 0.5) * step for idx, _ in top]


def _atr_value(df: pd.DataFrame | None, fallback_price: float) -> float:
    if df is None or df.empty or len(df) < 15:
        return max(fallback_price * 0.015, 0.01)
    work = df.tail(30).copy()
    high = work["high"].astype(float)
    low = work["low"].astype(float)
    close = work["close"].astype(float)
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = float(tr.tail(14).mean() or fallback_price * 0.015)
    return max(atr, fallback_price * 0.003, 0.01)


def _vwap_value(df: pd.DataFrame | None, lookback: int = 60) -> float | None:
    if df is None or df.empty or "volume" not in df.columns:
        return None
    work = df.tail(lookback).dropna(subset=["close", "volume"])
    volume_sum = float(work["volume"].astype(float).sum()) if not work.empty else 0.0
    if volume_sum <= 0:
        return None
    typical = (work["high"].astype(float) + work["low"].astype(float) + work["close"].astype(float)) / 3
    return round(float((typical * work["volume"].astype(float)).sum() / volume_sum), 2)


def _donchian_levels(df: pd.DataFrame | None, window: int = 20) -> dict[str, Any]:
    if df is None or df.empty or len(df) < 5:
        return {"high": None, "low": None, "mid": None, "structure": "Không đủ dữ liệu"}
    work = df.tail(max(window, 5)).copy()
    high = round(float(work["high"].astype(float).max()), 2)
    low = round(float(work["low"].astype(float).min()), 2)
    mid = round((high + low) / 2, 2)
    structure = "Sideway"
    if len(df) >= window * 2:
        recent = df.tail(window)
        previous = df.tail(window * 2).head(window)
        recent_high = float(recent["high"].max())
        recent_low = float(recent["low"].min())
        prev_high = float(previous["high"].max())
        prev_low = float(previous["low"].min())
        if recent_high > prev_high and recent_low > prev_low:
            structure = "Cấu trúc tăng"
        elif recent_high < prev_high and recent_low < prev_low:
            structure = "Cấu trúc giảm"
    return {"high": high, "low": low, "mid": mid, "structure": structure}


def _build_support_resistance(price: float, df: pd.DataFrame | None, pivot: float, s1: float, r1: float, s2: float, r2: float, ma20: float, ma50: float, ma200: float) -> dict[str, Any]:
    # Rule-based, no-AI formula. Keep it cheap: only use the latest candles and compute each signal once.
    candidates_support = [s1, s2, pivot, ma20, ma50, ma200]
    candidates_resistance = [r1, r2, pivot, ma20, ma50, ma200]
    if df is not None and not df.empty:
        recent = df.tail(180)
        swing_s, swing_r = _swing_levels(recent, window=5, lookback=180)
        volume_levels = _volume_levels(recent, price, bins=10, lookback=180)
        vwap = _vwap_value(recent, lookback=80)
        donchian = _donchian_levels(recent, window=55)
        candidates_support.extend(swing_s)
        candidates_resistance.extend(swing_r)
        candidates_support.extend(volume_levels)
        candidates_resistance.extend(volume_levels)
        if vwap:
            candidates_support.append(vwap)
            candidates_resistance.append(vwap)
        for level in (donchian.get("low"), donchian.get("mid"), donchian.get("high")):
            if level:
                candidates_support.append(float(level))
                candidates_resistance.append(float(level))
        high = float(recent["high"].max())
        low = float(recent["low"].min())
        if high > low:
            fib_levels = [high - (high - low) * x for x in (0.382, 0.5, 0.618)]
            candidates_support.extend(fib_levels)
            candidates_resistance.extend(fib_levels)
    atr = _atr_value(df, price)
    all_support_levels = _dedupe_levels(candidates_support, price)
    all_resistance_levels = _dedupe_levels(candidates_resistance, price)
    supports = _strongest_levels(candidates_support, price, "support", atr, limit=5)
    resistances = _strongest_levels(candidates_resistance, price, "resistance", atr, limit=5)
    if not supports:
        supports = [round(price - atr * 1.5, 2), round(price - atr * 2.5, 2)]
    if not resistances:
        resistances = [round(price + atr * 1.5, 2), round(price + atr * 2.5, 2)]
    near_support = supports[0]
    next_support = supports[1] if len(supports) > 1 else round(near_support - atr, 2)
    near_resistance = resistances[0]
    next_resistance = resistances[1] if len(resistances) > 1 else round(near_resistance + atr, 2)
    support_zone = [round(near_support - atr * 0.25, 2), round(near_support + atr * 0.25, 2)]
    resistance_zone = [round(near_resistance - atr * 0.25, 2), round(near_resistance + atr * 0.25, 2)]
    status = "Trong vùng giao dịch"
    active_support = near_support
    active_resistance = near_resistance
    if price < near_support:
        status = "Dưới hỗ trợ gần"
        active_support = next_support
    elif price > near_resistance:
        status = "Vượt kháng cự gần"
        active_resistance = next_resistance
    elif abs(price - near_support) <= max(atr * 0.25, price * 0.005):
        status = "Sát hỗ trợ gần"
    elif abs(price - near_resistance) <= max(atr * 0.25, price * 0.005):
        status = "Sát kháng cự gần"
    vwap = _vwap_value(df)
    donchian = _donchian_levels(df, window=55)
    return {
        "supports": supports,
        "resistances": resistances,
        "nearSupport": near_support,
        "nextSupport": next_support,
        "nearResistance": near_resistance,
        "nextResistance": next_resistance,
        "activeSupport": active_support,
        "activeResistance": active_resistance,
        "supportZone": support_zone,
        "resistanceZone": resistance_zone,
        "srStatus": status,
        "atr": round(atr, 2),
        "vwap": vwap,
        "donchianHigh": donchian.get("high"),
        "donchianLow": donchian.get("low"),
        "donchianMid": donchian.get("mid"),
        "marketStructure": donchian.get("structure"),
    }


def _build_strategy(price: float, support: float, resistance: float, trend: str, strength: str, rsi: float, macd: float, signal: float) -> tuple[str, float | None, float | None]:
    buy_price = round(support, 2) if support else None
    sell_price = round(resistance, 2) if resistance else None
    buy_text = f"{buy_price:.2f}" if buy_price is not None else "-"
    sell_text = f"{sell_price:.2f}" if sell_price is not None else "-"
    if trend == "Tăng":
        action = f"Cổ phiếu đang tăng, sức mạnh xu hướng {strength.lower()}. Canh mua khi lùi về hỗ trợ {buy_text} và ưu tiên chốt lời/bán khi lên kháng cự {sell_text}."
        if strength in {"Mạnh", "Rất mạnh"} and macd > signal and rsi < 70:
            action += " Có thể múc thăm dò tại vùng hỗ trợ nếu giá phản ứng tốt."
    elif trend == "Giảm":
        action = f"Cổ phiếu đang giảm, sức mạnh xu hướng {strength.lower()}. Hạn chế mua đuổi; chỉ cân nhắc múc thăm dò quanh hỗ trợ {buy_text} nếu xuất hiện tín hiệu hồi, và canh bán/giảm tỷ trọng gần kháng cự {sell_text}."
    else:
        action = f"Cổ phiếu đang đi ngang, sức mạnh xu hướng {strength.lower()}. Có thể mua gần hỗ trợ {buy_text} và bán gần kháng cự {sell_text}."
    return action, buy_price, sell_price


def _cluster_price_zones(levels: list[float] | None, atr: float, limit: int = 2) -> list[tuple[float, float]]:
    raw = sorted([float(x) for x in (levels or []) if x and x > 0])
    if not raw:
        return []
    gap = max(atr * 0.55, raw[-1] * 0.008, 0.1)
    clusters: list[list[float]] = []
    for level in raw:
        if not clusters or level - clusters[-1][-1] > gap:
            clusters.append([level])
        else:
            clusters[-1].append(level)
    zones = [(round(min(c), 1), round(max(c), 1)) for c in clusters]
    return zones[:limit]


def _zone_text(zones: list[tuple[float, float]], label: str) -> str:
    if not zones:
        return f"{label} -"
    parts = []
    for low, high in zones:
        if abs(high - low) < 0.05:
            parts.append(f"{low:.1f}")
        else:
            parts.append(f"{low:.1f}-{high:.1f}")
    return f"{label} " + "; ".join(parts)


def _effective_trend(raw_trend: str, rsi: float, vwap: float | None, price: float, structure: str | None, macd: float = 0, signal: float = 0) -> tuple[str, str]:
    structure_text = (structure or "").lower()
    below_vwap = bool(vwap and price < vwap)
    neutral_rsi = 45 <= rsi <= 55
    macd_negative = macd < signal
    if below_vwap and macd_negative and rsi < 45:
        return "Giảm", "giá dưới VWAP, MACD yếu và RSI dưới 45"
    if below_vwap and neutral_rsi and ("sideway" in structure_text or "tích" in structure_text or not structure_text):
        return "Đi ngang/tích lũy", "giá dưới VWAP, RSI quanh 50, cấu trúc chưa xác nhận xu hướng"
    if raw_trend == "Tăng" and below_vwap:
        return "Đi ngang/tích lũy", "giá dưới VWAP nên chưa xác nhận xu hướng tăng rõ"
    return raw_trend, ""


def _price_zone_state(price: float, rsi: float, bb_percent: float | None, donchian_high: float | None, donchian_low: float | None, vwap: float | None) -> str:
    near_donchian_low = bool(donchian_low and price <= donchian_low * 1.03)
    near_donchian_high = bool(donchian_high and price >= donchian_high * 0.97)
    below_vwap = bool(vwap and price < vwap)
    above_vwap = bool(vwap and price > vwap)
    if rsi <= 30 or (bb_percent is not None and bb_percent <= 0.08) or near_donchian_low:
        return "Quá bán"
    if rsi >= 70 or (bb_percent is not None and bb_percent >= 0.92) or near_donchian_high:
        return "Quá mua"
    if 30 < rsi <= 40 or (bb_percent is not None and bb_percent <= 0.2 and below_vwap):
        return "Gần quá bán"
    if 60 <= rsi < 70 or (bb_percent is not None and bb_percent >= 0.8 and above_vwap):
        return "Gần quá mua"
    return "Trung tính"


def _volume_state(volume_ratio: float | None, price: float, support: float, resistance: float, atr: float) -> str:
    ratio = float(volume_ratio or 1)
    near_support = abs(price - support) <= max(atr * 0.6, price * 0.02)
    near_resistance = abs(price - resistance) <= max(atr * 0.6, price * 0.02)
    if near_support and ratio >= 1.4:
        return "Volume lớn tại hỗ trợ"
    if near_support and ratio < 0.75:
        return "Cạn cung tại hỗ trợ"
    if near_resistance and ratio > 1.4:
        return "Áp lực bán mạnh tại kháng cự"
    if near_resistance and ratio < 0.75:
        return "Volume bé tại kháng cự"
    if ratio >= 1.5:
        return "Volume xác nhận mạnh"
    if ratio <= 0.7:
        return "Volume thấp"
    return "Volume trung bình"


def _setup_type(price: float, support: float, resistance: float, atr: float, zone_state: str, effective_trend: str, volume_state: str) -> str:
    near_support = abs(price - support) <= max(atr * 0.6, price * 0.012)
    breakout = price > resistance and "Volume xác nhận" in volume_state
    falling_knife = effective_trend.startswith("Giảm") and zone_state not in {"Quá bán", "Gần quá bán"}
    if zone_state in {"Quá mua", "Gần quá mua"}:
        return "Tránh mua vùng quá mua"
    if falling_knife:
        return "Tránh bắt dao rơi"
    if near_support:
        return "Mua hồi về hỗ trợ"
    if breakout:
        return "Mua breakout"
    return "Chờ xác nhận"


def _signal_score(effective_trend: str, strength: str, zone_state: str, volume_state: str, setup: str, risk_reward: float) -> dict[str, Any]:
    trend_score = 0
    if effective_trend.startswith("Tăng"):
        trend_score = 2 if strength in {"Mạnh", "Rất mạnh"} else 1
    elif effective_trend == "Đi ngang/tích lũy":
        trend_score = 1
    momentum_score = 2 if zone_state in {"Quá bán", "Gần quá bán", "Trung tính"} else 0 if zone_state == "Quá mua" else 1
    volume_score = 2 if "xác nhận mạnh" in volume_state.lower() or "Cạn cung" in volume_state else 1 if "trung bình" in volume_state.lower() else 0
    price_score = 2 if setup in {"Mua hồi về hỗ trợ", "Mua breakout"} and risk_reward >= 1.5 else 1 if risk_reward >= 1.2 else 0
    total = min(10, trend_score + momentum_score + volume_score + price_score)
    return {"total": total, "trend": trend_score, "momentum": momentum_score, "volume": volume_score, "price": price_score}


def _smart_stop_loss(entry_price: float, support_levels: list[float] | None, atr: float, max_loss_pct: float = 6.0) -> tuple[float, str]:
    ordered_levels = sorted([float(x) for x in (support_levels or []) if x and x > 0], reverse=True)
    levels = [x for x in ordered_levels if x < entry_price]
    if not levels:
        return round(max(entry_price - atr * 0.8, 0), 1), "ATR"
    max_loss_price = entry_price * (1 - max_loss_pct / 100)
    buffer = max(atr * 0.15, entry_price * 0.003)
    candidates: list[tuple[float, str, float]] = []
    for level in levels[:3]:
        support_idx = ordered_levels.index(level) + 1
        stop = round(max(level - buffer, 0), 1)
        loss_pct = (entry_price - stop) / entry_price * 100 if entry_price else 100
        if stop >= max_loss_price and loss_pct <= max_loss_pct:
            candidates.append((stop, f"dưới hỗ trợ {support_idx}", loss_pct))
    if candidates:
        # Choose the stop whose risk is closest to 6% but does not exceed it.
        stop, reason, loss_pct = sorted(candidates, key=lambda item: abs(max_loss_pct - item[2]))[0]
        return stop, f"{reason}, rủi ro {loss_pct:.1f}%"
    fallback = round(max(levels[0] - atr * 0.35, 0), 1)
    if fallback < max_loss_price:
        fallback = round(max_loss_price, 1)
    return fallback, "giới hạn rủi ro 6%"


def _build_rule_recommendation(price: float, support: float, resistance: float, next_support: float, next_resistance: float, trend: str, strength: str, rsi: float, macd: float, signal: float, vwap: float | None, structure: str | None, atr: float, support_levels: list[float] | None = None, resistance_levels: list[float] | None = None, bb_percent: float | None = None, donchian_high: float | None = None, donchian_low: float | None = None, volume_ratio: float | None = None, return_meta: bool = False) -> str | dict[str, Any]:
    support_zones_all = _cluster_price_zones(support_levels or [support, next_support], atr, limit=10)
    support_zones = list(reversed(support_zones_all))[:1]
    resistance_zones = _cluster_price_zones(resistance_levels or [resistance, next_resistance], atr, limit=1)
    main_support_low, main_support_high = support_zones[0] if support_zones else (round(max(support - atr * 0.3, 0), 1), round(support + atr * 0.3, 1))
    main_resistance_low, main_resistance_high = resistance_zones[0] if resistance_zones else (round(max(resistance - atr * 0.25, 0), 1), round(resistance + atr * 0.25, 1))
    planned_entry = round((main_support_low + main_support_high) / 2, 1)
    stop_loss, stop_reason = _smart_stop_loss(planned_entry, support_levels or [support, next_support], atr, max_loss_pct=6.0)
    confirm_price = round(max(main_resistance_high, vwap or 0), 1)
    effective_trend, trend_reason = _effective_trend(trend, rsi, vwap, price, structure, macd, signal)
    momentum_ok = macd >= signal and rsi < 65
    below_vwap = bool(vwap and price < vwap)
    structure_text = structure or "chưa rõ cấu trúc"
    zone_state = _price_zone_state(price, rsi, bb_percent, donchian_high, donchian_low, vwap)
    volume_state = _volume_state(volume_ratio, price, main_support_high, main_resistance_high, atr)
    setup = _setup_type(price, main_support_high, main_resistance_high, atr, zone_state, effective_trend, volume_state)
    risk = max(planned_entry - stop_loss, 0.01)
    reward = max(float(next_resistance or main_resistance_high) - planned_entry, 0.0)
    risk_reward = round(reward / risk, 2) if risk else 0
    score = _signal_score(effective_trend, strength, zone_state, volume_state, setup, risk_reward)
    strong_trend = strength in {"Mạnh", "Rất mạnh"}
    if zone_state == "Quá mua" or setup == "Tránh mua vùng quá mua":
        action = "Bán/giảm tỷ trọng"
    elif setup == "Tránh bắt dao rơi":
        action = "Quan sát"
    elif risk_reward < 1.5 and setup in {"Mua hồi về hỗ trợ", "Mua breakout"}:
        action = "Quan sát"
    elif zone_state == "Quá bán" and effective_trend.startswith("Giảm") and not strong_trend:
        action = "Quan sát hồi kỹ thuật"
    elif zone_state == "Quá bán" and not effective_trend.startswith("Giảm"):
        action = "Khuyến mua thăm dò"
    elif effective_trend == "Đi ngang/tích lũy":
        action = "Quan sát"
    elif effective_trend.startswith("Tăng") and strong_trend and zone_state not in {"Gần quá mua", "Quá mua"}:
        action = "Khuyến mua"
    elif effective_trend.startswith("Giảm") and strong_trend:
        action = "Bán/giảm tỷ trọng"
    else:
        action = "Quan sát"
    vwap_text = "trên VWAP" if vwap and price >= vwap else "dưới VWAP" if vwap else "không có VWAP"
    trend_sentence = f"Trạng thái hiện tại: {effective_trend}, lực xu hướng {strength.lower()}."
    if trend_reason:
        trend_sentence += " Chưa xác nhận xu hướng."
    target_text = f"{next_resistance:.1f}"
    if resistance_levels and len(resistance_levels) > 1:
        target_text = f"{float(resistance_levels[1]):.1f}"
    trade_sentence = f"Mua chỉ khi về vùng hỗ trợ hoặc vượt xác nhận {confirm_price:.1f}."
    if action == "Quan sát":
        trade_sentence = f"Quan sát, chỉ mua khi về vùng hỗ trợ hoặc vượt xác nhận {confirm_price:.1f}."
    elif action == "Quan sát hồi kỹ thuật":
        trade_sentence = f"Quan sát hồi kỹ thuật, chưa mua đuổi; chỉ mua nếu giữ được hỗ trợ và vượt xác nhận {confirm_price:.1f}."
    elif action.startswith("Khuyến mua"):
        trade_sentence = f"{action} quanh hỗ trợ hoặc khi vượt xác nhận {confirm_price:.1f}."
    elif action.startswith("Bán"):
        trade_sentence = f"Không mua mới; nếu đang giữ thì canh hồi về kháng cự {main_resistance_high:.1f} để bán/giảm tỷ trọng."
    conclusion = (
        f"{trend_sentence} "
        f"{_zone_text(support_zones, 'Hỗ trợ')}. "
        f"{_zone_text(resistance_zones, 'Kháng cự')}. "
        f"{trade_sentence} "
        f"Cắt lỗ dưới {stop_loss:.1f}. "
        f"Mục tiêu kế tiếp {target_text}."
    )
    meta = {"recommendation": conclusion, "setupType": setup, "volumeState": volume_state, "signalScore": score["total"], "scoreBreakdown": score, "riskReward": risk_reward, "effectiveTrend": effective_trend, "action": action}
    return meta if return_meta else conclusion


def _calc_technical(last_price: float, ref_price: float, open_price: float, high_price: float, low_price: float, avg_price: float, history_df: pd.DataFrame | None = None) -> dict[str, Any]:
    pivot_day, support_day, resistance_day, support_day_2, resistance_day_2 = _pivot_levels(high_price, low_price, last_price)
    pivot_week, support_week, resistance_week, support_week_2, resistance_week_2 = _pivot_levels(high_price, low_price, last_price)
    pivot_month, support_month, resistance_month, support_month_2, resistance_month_2 = _pivot_levels(high_price, low_price, last_price)

    daily_raw = _to_ohlc(history_df, "day") if history_df is not None and not history_df.empty else pd.DataFrame()
    weekly_raw = _to_ohlc(history_df, "week") if history_df is not None and not history_df.empty else pd.DataFrame()
    monthly_raw = _to_ohlc(history_df, "month") if history_df is not None and not history_df.empty else pd.DataFrame()

    if history_df is None or history_df.empty or len(daily_raw) < 35:
        momentum = ((last_price - ref_price) / ref_price * 100) if ref_price else 0
        rsi14 = max(0.0, min(100.0, 50.0 + momentum * 8))
        macd = last_price - (avg_price or last_price)
        signal = macd * 0.82
        histogram = macd - signal
        ma20 = avg_price or last_price
        ma50 = ma20 * 0.985
        ma200 = ma20 * 0.955
        adx14 = abs(momentum) * 3
        plus_di = max(momentum, 0) * 2 + 20
        minus_di = max(-momentum, 0) * 2 + 20
        bb_upper = last_price * 1.04
        bb_lower = last_price * 0.96
        bb_percent = 0.5
        volume_ratio = 1.0
    else:
        daily = _compute_indicators(daily_raw)
        row = daily.iloc[-1]
        rsi14 = float(row.get("rsi14") or 50)
        macd = float(row.get("macd") or 0)
        signal = float(row.get("signal") or 0)
        histogram = float(row.get("histogram") or 0)
        ma20 = float(row.get("ma20") or last_price)
        ma50 = float(row.get("ma50") or ma20)
        ma200 = float(row.get("ma200") or ma50)
        adx14 = float(row.get("adx14") or 0)
        plus_di = float(row.get("plusDi") or 0)
        minus_di = float(row.get("minusDi") or 0)
        bb_upper = float(row.get("bbUpper") or last_price)
        bb_lower = float(row.get("bbLower") or last_price)
        bb_percent = float(row.get("bbPercent") or 0.5)
        volume_ratio = float(row.get("volumeRatio") or 1.0)
        pivot_day, support_day, resistance_day, support_day_2, resistance_day_2 = _pivot_from_recent(daily_raw, high_price, low_price, last_price, 10)
        pivot_week, support_week, resistance_week, support_week_2, resistance_week_2 = _pivot_from_recent(weekly_raw, high_price, low_price, last_price, 10)
        pivot_month, support_month, resistance_month, support_month_2, resistance_month_2 = _pivot_from_recent(monthly_raw, high_price, low_price, last_price, 10)

    sr_day = _build_support_resistance(last_price, daily_raw, pivot_day, support_day, resistance_day, support_day_2, resistance_day_2, ma20, ma50, ma200)
    sr_week = _build_support_resistance(last_price, weekly_raw, pivot_week, support_week, resistance_week, support_week_2, resistance_week_2, ma20, ma50, ma200)
    sr_month = _build_support_resistance(last_price, monthly_raw, pivot_month, support_month, resistance_month, support_month_2, resistance_month_2, ma20, ma50, ma200)

    support_day = sr_day["activeSupport"]
    resistance_day = sr_day["activeResistance"]
    support_week = sr_week["activeSupport"]
    resistance_week = sr_week["activeResistance"]
    support_month = sr_month["activeSupport"]
    resistance_month = sr_month["activeResistance"]

    trend = "Tăng" if last_price > ma20 and macd > signal and plus_di >= minus_di else "Giảm" if last_price < ma20 and macd < signal and minus_di > plus_di else "Trung tính"
    strength = _describe_trend_strength(adx14)
    strategy, buy_price, sell_price = _build_strategy(last_price, support_day, resistance_day, trend, strength, rsi14, macd, signal)
    week_strategy, buy_price_week, sell_price_week = _build_strategy(last_price, support_week, resistance_week, trend, strength, rsi14, macd, signal)
    month_strategy, buy_price_month, sell_price_month = _build_strategy(last_price, support_month, resistance_month, trend, strength, rsi14, macd, signal)
    recommendation_meta = _build_rule_recommendation(last_price, support_day, resistance_day, sr_day["nextSupport"], sr_day["nextResistance"], trend, strength, rsi14, macd, signal, sr_day.get("vwap"), sr_day.get("marketStructure"), sr_day["atr"], sr_day["supports"], sr_day["resistances"], bb_percent, sr_day.get("donchianHigh"), sr_day.get("donchianLow"), volume_ratio, True)
    recommendation = recommendation_meta["recommendation"]
    recommendation_week = _build_rule_recommendation(last_price, support_week, resistance_week, sr_week["nextSupport"], sr_week["nextResistance"], trend, strength, rsi14, macd, signal, sr_week.get("vwap"), sr_week.get("marketStructure"), sr_week["atr"], sr_week["supports"], sr_week["resistances"], bb_percent, sr_week.get("donchianHigh"), sr_week.get("donchianLow"), volume_ratio)
    recommendation_month = _build_rule_recommendation(last_price, support_month, resistance_month, sr_month["nextSupport"], sr_month["nextResistance"], trend, strength, rsi14, macd, signal, sr_month.get("vwap"), sr_month.get("marketStructure"), sr_month["atr"], sr_month["supports"], sr_month["resistances"], bb_percent, sr_month.get("donchianHigh"), sr_month.get("donchianLow"), volume_ratio)

    return {
        "rsi14": _safe_number(rsi14, 2),
        "relativeStrength": _safe_number(rsi14, 2),
        "macd": _safe_number(macd, 3),
        "signal": _safe_number(signal, 3),
        "histogram": _safe_number(histogram, 3),
        "adx14": _safe_number(adx14, 2),
        "plusDi": _safe_number(plus_di, 2),
        "minusDi": _safe_number(minus_di, 2),
        "ma20": _safe_number(ma20, 2),
        "ma50": _safe_number(ma50, 2),
        "ma200": _safe_number(ma200, 2),
        "bbUpper": _safe_number(bb_upper, 1),
        "bbLower": _safe_number(bb_lower, 1),
        "bbPercent": _safe_number(bb_percent, 2),
        "zoneState": _price_zone_state(last_price, rsi14, bb_percent, sr_day.get("donchianHigh"), sr_day.get("donchianLow"), sr_day.get("vwap")),
        "volumeRatio": _safe_number(volume_ratio, 2),
        "volumeState": recommendation_meta.get("volumeState"),
        "setupType": recommendation_meta.get("setupType"),
        "signalScore": recommendation_meta.get("signalScore"),
        "riskReward": recommendation_meta.get("riskReward"),
        "effectiveTrend": recommendation_meta.get("effectiveTrend"),
        "action": recommendation_meta.get("action"),
        "scoreBreakdown": recommendation_meta.get("scoreBreakdown"),
        "pivotDay": _safe_number(pivot_day, 2),
        "supportDay": _safe_number(support_day, 2),
        "resistanceDay": _safe_number(resistance_day, 2),
        "supportDay2": _safe_number(support_day_2, 2),
        "resistanceDay2": _safe_number(resistance_day_2, 2),
        "pivotWeek": _safe_number(pivot_week, 2),
        "supportWeek": _safe_number(support_week, 2),
        "resistanceWeek": _safe_number(resistance_week, 2),
        "supportWeek2": _safe_number(support_week_2, 2),
        "resistanceWeek2": _safe_number(resistance_week_2, 2),
        "pivotMonth": _safe_number(pivot_month, 2),
        "supportMonth": _safe_number(support_month, 2),
        "resistanceMonth": _safe_number(resistance_month, 2),
        "supportMonth2": _safe_number(support_month_2, 2),
        "resistanceMonth2": _safe_number(resistance_month_2, 2),
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
        "supportLevelsWeek": [round(float(x), 1) for x in sr_week["supports"]],
        "resistanceLevelsWeek": [round(float(x), 1) for x in sr_week["resistances"]],
        "activeSupportWeek": _safe_number(sr_week["activeSupport"], 1),
        "activeResistanceWeek": _safe_number(sr_week["activeResistance"], 1),
        "srStatusWeek": sr_week["srStatus"],
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
        "vwapWeek": _safe_number(sr_week.get("vwap"), 1),
        "donchianHighWeek": _safe_number(sr_week.get("donchianHigh"), 1),
        "donchianLowWeek": _safe_number(sr_week.get("donchianLow"), 1),
        "donchianMidWeek": _safe_number(sr_week.get("donchianMid"), 1),
        "marketStructureWeek": sr_week.get("marketStructure"),
        "vwapMonth": _safe_number(sr_month.get("vwap"), 1),
        "donchianHighMonth": _safe_number(sr_month.get("donchianHigh"), 1),
        "donchianLowMonth": _safe_number(sr_month.get("donchianLow"), 1),
        "donchianMidMonth": _safe_number(sr_month.get("donchianMid"), 1),
        "marketStructureMonth": sr_month.get("marketStructure"),
        "open": _safe_number(open_price, 2),
        "high": _safe_number(high_price, 2),
        "low": _safe_number(low_price, 2),
        "reference": _safe_number(ref_price, 2),
        "avg": _safe_number(avg_price, 2),
        "trend": trend,
        "trendStrength": strength,
        "strategy": strategy,
        "recommendation": recommendation,
        "buyPrice": _safe_number(buy_price, 2),
        "sellPrice": _safe_number(sell_price, 2),
        "buyPriceWeek": _safe_number(buy_price_week, 2),
        "sellPriceWeek": _safe_number(sell_price_week, 2),
        "buyPriceMonth": _safe_number(buy_price_month, 2),
        "sellPriceMonth": _safe_number(sell_price_month, 2),
        "strategyWeek": week_strategy,
        "strategyMonth": month_strategy,
        "recommendationWeek": recommendation_week,
        "recommendationMonth": recommendation_month,
    }


def _load_history(symbol: str) -> pd.DataFrame | None:
    if Quote is None:
        return None
    try:
        df = Quote(symbol=symbol, source="VCI").history(start="2024-01-01", end=_now_iso()[:10], interval="1D")
        if not isinstance(df, pd.DataFrame) or df.empty:
            return None
        rename_map = {
            "datetime": "time",
            "date": "time",
            "Date": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
        work = df.rename(columns=rename_map).copy()
        required = ["time", "open", "high", "low", "close"]
        if any(col not in work.columns for col in required):
            return None
        if "volume" not in work.columns:
            work["volume"] = 0
        work = work[required + ["volume"]].dropna().reset_index(drop=True)
        return work
    except Exception:
        return None


def _mock_item(symbol: str) -> dict[str, Any]:
    seed = sum(ord(c) for c in symbol)
    base_price = 20.0 + (seed % 120)
    change_pct = round((((seed % 9) - 4) * 0.41), 2)
    last_price = round(base_price * (1 + change_pct / 100), 2)
    volume = 50000 * max(1, (seed % 20) + 1)
    open_price = round(last_price * 0.995, 2)
    low_price = round(last_price * 0.98, 2)
    high_price = round(last_price * 1.02, 2)
    avg_price = round((open_price + low_price + high_price + last_price) / 4, 2)
    history_df = _load_history(symbol)
    return {
        "ticker": symbol,
        "price": last_price,
        "changePct": change_pct,
        "volume": volume,
        "technical": _calc_technical(last_price, base_price, open_price, high_price, low_price, avg_price, history_df),
        "type": "stock",
        "source": "fallback-local",
    }


def _fetch_symbol(symbol: str, include_history: bool = True) -> dict[str, Any] | None:
    try:
        url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}"
        resp = httpx.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None
        item = data[0]

        last_price = float(item.get("lastPrice") or 0)
        ref_price = float(item.get("r") or 0)
        change_pct = (((last_price - ref_price) / ref_price) * 100) if ref_price else 0
        raw_volume = item.get("totalVolume")
        if raw_volume in (None, "", 0, "0"):
            # VPS `lot` is board-lot quantity; convert to shares for display.
            raw_volume = float(item.get("lot") or item.get("lastVolume") or item.get("nnBuy") or 0) * 10
        volume = int(float(raw_volume or 0))
        low_price = float(item.get("lowPrice") or last_price or ref_price or 0)
        high_price = float(item.get("highPrice") or last_price or ref_price or 0)
        open_price = float(item.get("openPrice") or ref_price or last_price or 0)
        avg_price = float(item.get("avePrice") or last_price or 0)
        history_df = _load_history(symbol) if include_history else None
        return {
            "ticker": symbol,
            "price": round(last_price, 2),
            "changePct": round(change_pct, 2),
            "volume": volume,
            "technical": _calc_technical(last_price, ref_price, open_price, high_price, low_price, avg_price, history_df) if include_history else {},
            "type": "stock",
            "source": "vps",
        }
    except Exception:
        return None


def get_market_symbol(symbol: str, force_refresh: bool = False) -> dict[str, Any]:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("Symbol is required")
    now = monotonic()
    cached = _symbol_detail_cache.get(normalized)
    if cached and not force_refresh and (now - cached[0]) < SYMBOL_CACHE_TTL_SECONDS:
        return cached[1]
    item = _fetch_symbol(normalized, include_history=True) or _mock_item(normalized)
    _symbol_detail_cache[normalized] = (now, item)
    return item


def get_symbol_catalog(query: str = "", limit: int = 50) -> list[dict[str, str]]:
    global _symbol_cache
    if not _symbol_cache and Listing is not None:
        try:
            df = Listing().all_symbols()
            if isinstance(df, pd.DataFrame) and not df.empty:
                _symbol_cache = [
                    {
                        "symbol": str(row.get("symbol") or "").upper(),
                        "name": str(row.get("organ_name") or "").strip(),
                    }
                    for _, row in df.iterrows()
                    if str(row.get("symbol") or "").strip()
                ]
        except Exception:
            _symbol_cache = []
    items = _symbol_cache
    q = query.strip().lower()
    if q:
        items = [item for item in items if q in item["symbol"].lower() or q in item["name"].lower()]
    return items[:limit]


def refresh_market_cache() -> list[dict[str, Any]]:
    global _market_cache, _last_updated, _last_market_refresh_at
    items: list[dict[str, Any]] = []
    for ticker in DEFAULT_TICKERS:
        item = _fetch_symbol(ticker, include_history=False) or _mock_item(ticker)
        _symbol_detail_cache[ticker] = (monotonic(), item)
        items.append(item)
    _market_cache = items
    _last_updated = _now_iso()
    _last_market_refresh_at = monotonic()
    return _market_cache


def get_market_cache(force_refresh: bool = False) -> dict[str, Any]:
    now = monotonic()
    is_stale = not _market_cache or (now - _last_market_refresh_at) >= MARKET_CACHE_TTL_SECONDS
    if force_refresh or is_stale:
        refresh_market_cache()
    return {
        "updatedAt": _last_updated,
        "items": _market_cache,
        "cached": not (force_refresh or is_stale),
        "ttlSeconds": MARKET_CACHE_TTL_SECONDS,
    }
