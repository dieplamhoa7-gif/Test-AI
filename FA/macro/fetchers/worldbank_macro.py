"""
Fetcher: World Bank / DBnomics — Slow macro indicators (monthly/quarterly/annual)
Dữ liệu: GDP growth, CPI, FDI inflows, trade balance, credit-to-GDP, current account.

Note: World Bank cập nhật chậm (1–3 tháng lag), dùng cho context dài hạn, không cho daily signal.
Cài: pip install wbgapi
"""
from __future__ import annotations

import json
import urllib.request
from datetime import date
from typing import Any

SOURCE_NAME = "World Bank Macro"
PARSER_VERSION = "worldbank_v1"

# World Bank indicator codes
INDICATORS = {
    "gdpGrowthPct":     "NY.GDP.MKTP.KD.ZG",   # GDP growth % annual
    "cpiInflation":     "FP.CPI.TOTL.ZG",        # CPI inflation % annual
    "fdiNetInflows":    "BX.KLT.DINV.CD.WD",     # FDI net inflows USD
    "currentAccount":   "BN.CAB.XOKA.CD",         # Current account USD
    "creditPrivate":    "FS.AST.PRVT.GD.ZS",     # Domestic credit to private sector % GDP
    "broadMoney":       "FM.LBL.BMNY.GD.ZS",     # Broad money % GDP
    "exports":          "NE.EXP.GNFS.ZS",         # Exports % GDP
    "imports":          "NE.IMP.GNFS.ZS",         # Imports % GDP
    "remittances":      "BX.TRF.PWKR.CD.DT",     # Personal remittances USD
}

VN_ISO = "VN"


def _fetch_worldbank_http(indicator_code: str, start_year: int, end_year: int) -> dict[str, float | None]:
    """Fetch World Bank directly via public JSON API, no wbgapi dependency."""
    url = (
        f"https://api.worldbank.org/v2/country/{VN_ISO}/indicator/{indicator_code}"
        f"?format=json&per_page=100&date={start_year}:{end_year}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "LHInvestment/macro-worldbank"})
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.loads(r.read().decode("utf-8", errors="ignore"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list) else []
    ts: dict[str, float | None] = {}
    for row in rows:
        yr = str(row.get("date"))
        val = row.get("value")
        ts[yr] = round(float(val), 4) if val is not None else None
    return dict(sorted(ts.items()))


def fetch(years: int = 8) -> dict[str, Any]:
    """
    Fetch World Bank annual indicators for Vietnam.
    Uses official HTTP API directly to avoid wbgapi compatibility issues.
    """
    end_year = date.today().year
    start_year = end_year - years
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}

    for key, indicator_code in INDICATORS.items():
        try:
            ts = _fetch_worldbank_http(indicator_code, start_year, end_year)
            if not ts:
                errors[key] = "no data"
                continue
            latest_val = None
            latest_yr = None
            for yr in sorted(ts.keys(), reverse=True):
                if ts[yr] is not None:
                    latest_val = ts[yr]
                    latest_yr = yr
                    break
            results[key] = {
                "latest": latest_val,
                "latestYear": latest_yr,
                "timeSeries": ts,
                "indicatorCode": indicator_code,
            }
        except Exception as e:
            errors[key] = str(e)[:160]

    return {
        "source": SOURCE_NAME,
        "parserVersion": "worldbank_http_v2",
        "country": "Vietnam",
        "fetchedAt": date.today().isoformat(),
        "note": "Annual data, lag 1–12 months. Use for long-term context only.",
        "data": results,
        "errors": errors if errors else None,
    }
