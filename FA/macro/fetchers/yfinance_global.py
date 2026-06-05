"""
Fetcher: Global market data via yfinance
Dữ liệu: VIX, S&P500, NASDAQ, DJIA, DXY, US10Y, Brent, WTI, Gold, Silver,
         MSCI EM proxy, regional Asia indices.
Cài: pip install yfinance
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import date, timedelta
from typing import Any

SOURCE_NAME = "yfinance Global Markets"
PARSER_VERSION = "yfinance_v2"

# Ticker map: schema_key → Yahoo Finance ticker
TICKER_MAP: dict[str, str] = {
    # Risk
    "vix":        "^VIX",
    # US equities
    "sp500":      "^GSPC",
    "nasdaq":     "^IXIC",
    "djia":       "^DJI",
    "russell2000":"^RUT",
    # US rates
    "us10y":      "^TNX",
    "us2y":       "^IRX",
    # Dollar
    "dxy":        "DX-Y.NYB",
    # Commodities
    "brent":      "BZ=F",
    "wti":        "CL=F",
    "gold":       "GC=F",
    "silver":     "SI=F",
    "copper":     "HG=F",
    # Asia
    "nikkei":     "^N225",
    "hang_seng":  "^HSI",
    "sse":        "000001.SS",   # Shanghai Composite
    "kospi":      "^KS11",
    # EM
    "eem":        "EEM",          # iShares MSCI EM ETF
    # Crypto proxy (optional)
    "btc":        "BTC-USD",
}


def _safe_float(val: Any) -> float | None:
    try:
        f = float(val)
        return None if f != f else round(f, 6)  # NaN → None
    except Exception:
        return None


def _from_closes(key: str, sym: str, closes: list[float], dates: list[str]) -> dict[str, Any] | None:
    closes = [c for c in closes if c is not None]
    if not closes:
        return None
    val = _safe_float(closes[-1])
    chg = None
    if len(closes) >= 2 and closes[-2]:
        chg = _safe_float(round(((closes[-1] - closes[-2]) / closes[-2]) * 100, 4))
    chg1w = None
    if len(closes) >= 5 and closes[-5]:
        chg1w = _safe_float(round(((closes[-1] - closes[-5]) / closes[-5]) * 100, 4))
    return {"value": val, "change1d_pct": chg, "change1w_pct": chg1w, "ticker": sym, "asOf": dates[-1] if dates else "", "source": "yahoo_chart"}


def _fetch_yahoo_chart(sym: str, lookback_days: int) -> tuple[list[float], list[str]]:
    end = int(time.time())
    start = end - max(lookback_days, 10) * 86400
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={start}&period2={end}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 LHInvestment/yahoo-chart"})
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.loads(r.read().decode("utf-8", errors="ignore"))
    result = payload.get("chart", {}).get("result", [None])[0]
    if not result:
        return [], []
    timestamps = result.get("timestamp", []) or []
    quote = (result.get("indicators", {}).get("quote", [{}]) or [{}])[0]
    closes = quote.get("close", []) or []
    dates = [date.fromtimestamp(ts).isoformat() for ts in timestamps]
    return closes, dates


def fetch(tickers: list[str] | None = None, lookback_days: int = 10) -> dict[str, Any]:
    """
    Fetch latest close + 1D % change.
    Uses yfinance when available, then falls back to Yahoo chart HTTP API.
    """
    target = {k: v for k, v in TICKER_MAP.items() if tickers is None or k in tickers}
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}

    yf = None
    try:
        import yfinance as yf_mod
        yf = yf_mod
    except Exception:
        yf = None

    end = date.today() + timedelta(days=1)
    start = date.today() - timedelta(days=lookback_days)

    for key, sym in target.items():
        # 1) yfinance library
        if yf is not None:
            try:
                df = yf.download(sym, start=start, end=end, progress=False, auto_adjust=True, threads=False)
                if df is not None and not df.empty and "Close" in df:
                    closes_series = df["Close"].dropna()
                    closes = [_safe_float(x) for x in closes_series.tolist()]
                    dates = [str(x.date()) if hasattr(x, "date") else str(x)[:10] for x in closes_series.index]
                    row = _from_closes(key, sym, closes, dates)
                    if row and row.get("value") is not None:
                        row["source"] = "yfinance"
                        results[key] = row
                        continue
            except Exception as e:
                errors[key] = "yfinance: " + str(e)[:100]

        # 2) direct Yahoo chart fallback
        try:
            closes, dates = _fetch_yahoo_chart(sym, lookback_days)
            row = _from_closes(key, sym, closes, dates)
            if row and row.get("value") is not None:
                results[key] = row
            else:
                errors[key] = errors.get(key, "") + "; yahoo_chart: no data"
        except Exception as e:
            errors[key] = errors.get(key, "") + "; yahoo_chart: " + str(e)[:120]

    return {
        "source": SOURCE_NAME,
        "parserVersion": "yfinance_yahoochart_v3",
        "fetchedDate": str(date.today()),
        "data": results,
        "errors": errors if errors else None,
    }


def fetch_core() -> dict[str, Any]:
    """Fetch chỉ các tickers quan trọng nhất (nhanh hơn)."""
    CORE = ["vix", "sp500", "nasdaq", "us10y", "dxy", "brent", "gold"]
    return fetch(tickers=CORE)
