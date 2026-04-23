from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from vnstock import Vnstock
except Exception:
    Vnstock = None

DEFAULT_TICKERS = ["MWG", "FPT", "HPG", "SSI", "VCB", "VIC"]
DEFAULT_CW_TICKERS = ["CFPT2314", "CHPG2401", "CVPB2402"]

_market_cache: list[dict[str, Any]] = []
_last_updated: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_item(symbol: str, is_cw: bool = False) -> dict[str, Any]:
    seed = sum(ord(c) for c in symbol)
    base_price = 20.0 + (seed % 120)
    change_pct = round((((seed % 9) - 4) * 0.41), 2)
    last_price = round(base_price * (1 + change_pct / 100), 2)
    volume = 50000 * max(1, (seed % 20) + 1)
    chart = [
        round(last_price * 0.97, 2),
        round(last_price * 0.99, 2),
        round(last_price, 2),
        round(last_price * 1.01, 2),
        round(last_price * 1.02, 2),
    ]
    item = {
        "ticker": symbol,
        "price": last_price,
        "changePct": change_pct,
        "volume": volume,
        "chart": chart,
        "technical": {
            "rsi14": None,
            "macd": None,
            "signal": None,
            "ma20": round(sum(chart) / len(chart), 2),
        },
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
    if Vnstock is None:
        return None
    try:
        stock = Vnstock().stock(symbol=symbol, source="KBS")
        intraday = stock.quote.intraday()
        if intraday is None or intraday.empty:
            return None

        latest = intraday.iloc[0]
        closes = intraday["price"].astype(float).head(20).tolist()
        ref_price = closes[-1] if closes else float(latest["price"])
        last_price = float(latest["price"])
        change_pct = round(((last_price - ref_price) / ref_price) * 100, 2) if ref_price else 0.0
        volume = int(intraday["volume"].astype(float).sum())
        chart = [round(x, 2) for x in list(reversed(closes[:20]))][-20:]
        if not chart:
            chart = [round(last_price, 2)]

        return {
            "ticker": symbol,
            "price": round(last_price, 2),
            "changePct": change_pct,
            "volume": volume,
            "chart": chart,
            "technical": {
                "rsi14": None,
                "macd": None,
                "signal": None,
                "ma20": round(sum(chart) / len(chart), 2),
            },
            "type": "stock",
            "source": "vnstock:KBS",
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
