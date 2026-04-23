from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

DEFAULT_TICKERS = ["VNINDEX", "VN30", "FPT", "HPG", "SSI", "VCB", "VIC"]
DEFAULT_CW_TICKERS = ["CFPT2314", "CHPG2401", "CVPB2402"]
USER_AGENT = "Mozilla/5.0"

_market_cache: list[dict[str, Any]] = []
_last_updated: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_item(symbol: str, is_cw: bool = False) -> dict[str, Any]:
    base_price = 100.0 + len(symbol)
    change_pct = round(((len(symbol) % 5) - 2) * 0.73, 2)
    last_price = round(base_price * (1 + change_pct / 100), 2)
    volume = 100000 * max(1, len(symbol))
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
            "rsi14": round(45 + (len(symbol) % 20), 2),
            "macd": round((len(symbol) % 7) * 0.11, 2),
            "signal": round((len(symbol) % 5) * 0.09, 2),
            "ma20": round(sum(chart) / len(chart), 2),
        },
        "type": "cw" if is_cw else "stock",
        "source": "fallback",
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
    urls = [
        f"https://price.tpbs.com.vn/api/SymbolApi/getStockQuote?symbol={symbol}",
        f"https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}",
    ]
    headers = {"User-Agent": USER_AGENT}

    for url in urls:
        try:
            with httpx.Client(timeout=5.0, headers=headers, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                if isinstance(data, list) and data:
                    data = data[0]
                if not isinstance(data, dict):
                    continue

                price = data.get("matchPrice") or data.get("lastPrice") or data.get("close") or data.get("price")
                change_pct = data.get("changePc") or data.get("percentChange") or data.get("changePercent") or 0
                volume = data.get("totalVolume") or data.get("nmVolume") or data.get("volume") or 0
                if price is None:
                    continue

                last_price = float(price)
                chart = [round(last_price * x, 2) for x in (0.97, 0.99, 1.0, 1.01, 1.02)]
                return {
                    "ticker": symbol,
                    "price": last_price,
                    "changePct": round(float(change_pct), 2),
                    "volume": int(float(volume)),
                    "chart": chart,
                    "technical": {
                        "rsi14": None,
                        "macd": None,
                        "signal": None,
                        "ma20": round(sum(chart) / len(chart), 2),
                    },
                    "type": "stock",
                    "source": url,
                }
        except Exception:
            continue
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
