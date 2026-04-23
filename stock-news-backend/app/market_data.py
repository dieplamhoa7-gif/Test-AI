from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

DEFAULT_TICKERS = ["MWG", "FPT", "HPG", "SSI", "VCB", "VIC"]
DEFAULT_CW_TICKERS = ["CFPT2314", "CHPG2401", "CVPB2402"]

_market_cache: list[dict[str, Any]] = []
_last_updated: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _calc_technical(last_price: float, ref_price: float, open_price: float, high_price: float, low_price: float, avg_price: float) -> dict[str, Any]:
    momentum = ((last_price - ref_price) / ref_price * 100) if ref_price else 0
    base_ma = avg_price or last_price
    support_day = low_price if low_price else min(last_price, ref_price or last_price)
    resistance_day = high_price if high_price else max(last_price, ref_price or last_price)
    support_week = round(support_day * 0.985, 2)
    resistance_week = round(resistance_day * 1.015, 2)
    support_month = round(support_day * 0.965, 2)
    resistance_month = round(resistance_day * 1.03, 2)
    trend = "Tăng" if last_price > ref_price else "Giảm" if last_price < ref_price else "Trung tính"
    return {
        "rsi14": round(max(0.0, min(100.0, 50.0 + momentum * 8)), 2),
        "relativeStrength": round(max(0.0, min(100.0, 50.0 + momentum * 8)), 2),
        "macd": round(last_price - base_ma, 2),
        "signal": round((last_price - base_ma) * 0.82, 2),
        "histogram": round((last_price - base_ma) * 0.18, 2),
        "ma20": round(base_ma, 2),
        "ma50": round(base_ma * 0.985, 2),
        "ma200": round(base_ma * 0.955, 2),
        "supportDay": round(support_day, 2),
        "resistanceDay": round(resistance_day, 2),
        "supportWeek": support_week,
        "resistanceWeek": resistance_week,
        "supportMonth": support_month,
        "resistanceMonth": resistance_month,
        "open": round(open_price, 2) if open_price else None,
        "high": round(high_price, 2) if high_price else None,
        "low": round(low_price, 2) if low_price else None,
        "reference": round(ref_price, 2) if ref_price else None,
        "avg": round(avg_price, 2) if avg_price else None,
        "trend": trend,
        "strategy": "Canh mua ở hỗ trợ, chốt lời gần kháng cự" if trend == "Tăng" else "Ưu tiên quan sát, bán khi hồi lên kháng cự",
    }


def _mock_item(symbol: str, is_cw: bool = False) -> dict[str, Any]:
    seed = sum(ord(c) for c in symbol)
    base_price = 20.0 + (seed % 120)
    change_pct = round((((seed % 9) - 4) * 0.41), 2)
    last_price = round(base_price * (1 + change_pct / 100), 2)
    volume = 50000 * max(1, (seed % 20) + 1)
    open_price = round(last_price * 0.995, 2)
    low_price = round(last_price * 0.98, 2)
    high_price = round(last_price * 1.02, 2)
    avg_price = round((open_price + low_price + high_price + last_price) / 4, 2)
    item = {
        "ticker": symbol,
        "price": last_price,
        "changePct": change_pct,
        "volume": volume,
        "technical": _calc_technical(last_price, base_price, open_price, high_price, low_price, avg_price),
        "type": "cw" if is_cw else "stock",
        "source": "fallback-local",
    }
    if is_cw:
        item.update(
            {
                "underlyingTicker": symbol[1:4] if len(symbol) >= 4 else None,
                "underlyingPrice": round(last_price * 1.18, 2),
                "expiryDate": "2026-12-31",
                "conversionRatio": "2:1",
                "breakevenPrice": round(last_price * 1.12, 2),
            }
        )
    return item


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
        return {
            "ticker": symbol,
            "price": round(last_price, 2),
            "changePct": round(change_pct, 2),
            "volume": volume,
            "technical": _calc_technical(last_price, ref_price, open_price, high_price, low_price, avg_price),
            "type": "stock",
            "source": "vps",
        }
    except Exception:
        return None


def refresh_market_cache() -> list[dict[str, Any]]:
    global _market_cache, _last_updated
    items: list[dict[str, Any]] = []
    for ticker in DEFAULT_TICKERS:
        item = _fetch_symbol(ticker)
        items.append(item or _mock_item(ticker))
    for ticker in DEFAULT_CW_TICKERS:
        items.append(_mock_item(ticker, is_cw=True))
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
