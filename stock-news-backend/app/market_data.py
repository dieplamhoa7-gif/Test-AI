from __future__ import annotations

from datetime import datetime, timezone
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

_market_cache: list[dict[str, Any]] = []
_symbol_cache: list[dict[str, str]] = []
_last_updated: str | None = None


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


def _build_strategy(price: float, support: float, resistance: float, trend: str, strength: str, rsi: float, macd: float, signal: float) -> tuple[str, float | None, float | None]:
    buy_price = round(support, 2) if support else None
    sell_price = round(resistance, 2) if resistance else None
    if trend == "Tăng":
        action = f"Cổ phiếu đang tăng, sức mạnh xu hướng {strength.lower()}. Canh mua khi lùi về hỗ trợ {buy_price:.2f} và ưu tiên chốt lời/bán khi lên kháng cự {sell_price:.2f}."
        if strength in {"Mạnh", "Rất mạnh"} and macd > signal and rsi < 70:
            action += " Có thể múc thăm dò tại vùng hỗ trợ nếu giá phản ứng tốt."
    elif trend == "Giảm":
        action = f"Cổ phiếu đang giảm, sức mạnh xu hướng {strength.lower()}. Hạn chế mua đuổi; chỉ cân nhắc múc thăm dò quanh hỗ trợ {buy_price:.2f} nếu xuất hiện tín hiệu hồi, và canh bán/giảm tỷ trọng gần kháng cự {sell_price:.2f}."
    else:
        action = f"Cổ phiếu đang đi ngang, sức mạnh xu hướng {strength.lower()}. Có thể mua gần hỗ trợ {buy_price:.2f} và bán gần kháng cự {sell_price:.2f}."
    return action, buy_price, sell_price


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
        pivot_day, support_day, resistance_day, support_day_2, resistance_day_2 = _pivot_from_recent(daily_raw, high_price, low_price, last_price, 10)
        pivot_week, support_week, resistance_week, support_week_2, resistance_week_2 = _pivot_from_recent(weekly_raw, high_price, low_price, last_price, 10)
        pivot_month, support_month, resistance_month, support_month_2, resistance_month_2 = _pivot_from_recent(monthly_raw, high_price, low_price, last_price, 10)

    trend = "Tăng" if last_price > ma20 and macd > signal and plus_di >= minus_di else "Giảm" if last_price < ma20 and macd < signal and minus_di > plus_di else "Trung tính"
    strength = _describe_trend_strength(adx14)
    strategy, buy_price, sell_price = _build_strategy(last_price, support_day, resistance_day, trend, strength, rsi14, macd, signal)

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
        "open": _safe_number(open_price, 2),
        "high": _safe_number(high_price, 2),
        "low": _safe_number(low_price, 2),
        "reference": _safe_number(ref_price, 2),
        "avg": _safe_number(avg_price, 2),
        "trend": trend,
        "trendStrength": strength,
        "strategy": strategy,
        "buyPrice": _safe_number(buy_price, 2),
        "sellPrice": _safe_number(sell_price, 2),
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


def _fetch_symbol(symbol: str) -> dict[str, Any] | None:
    try:
        url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}"
        resp = httpx.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None
        item = data[0]

        last_price = float(item.get("lastPrice") or 0)
        ref_price = float(item.get("r") or 0)
        change_pct = (((last_price - ref_price) / ref_price) * 100) if ref_price else 0
        volume = int(float(item.get("lot") or item.get("totalVolume") or item.get("nnBuy") or 0))
        low_price = float(item.get("lowPrice") or last_price or ref_price or 0)
        high_price = float(item.get("highPrice") or last_price or ref_price or 0)
        open_price = float(item.get("openPrice") or ref_price or last_price or 0)
        avg_price = float(item.get("avePrice") or last_price or 0)
        history_df = _load_history(symbol)
        return {
            "ticker": symbol,
            "price": round(last_price, 2),
            "changePct": round(change_pct, 2),
            "volume": volume,
            "technical": _calc_technical(last_price, ref_price, open_price, high_price, low_price, avg_price, history_df),
            "type": "stock",
            "source": "vps",
        }
    except Exception:
        return None


def get_market_symbol(symbol: str) -> dict[str, Any]:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("Symbol is required")
    return _fetch_symbol(normalized) or _mock_item(normalized)


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
    global _market_cache, _last_updated
    items: list[dict[str, Any]] = []
    for ticker in DEFAULT_TICKERS:
        item = _fetch_symbol(ticker)
        items.append(item or _mock_item(ticker))
    _market_cache = items
    _last_updated = _now_iso()
    return _market_cache


def get_market_cache() -> dict[str, Any]:
    if not _market_cache:
        refresh_market_cache()
    return {
        "updatedAt": _last_updated,
        "items": _market_cache,
    }
