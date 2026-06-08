"""Fetch/parse Vietnam market valuation, sector indices, and breadth data.

Public/free first:
- Sector indices from VnDirect dchart public endpoint (daily OHLCV).
- Advance/decline breadth from archived Pinetree Morning Brief raw text where available.
- VNIndex P/E is intentionally source-pluggable; no reliable free public historical API
  was confirmed yet. Manual/paid FiinProX or future public endpoint can be added.

This module does not bypass logins/paywalls.
"""
from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests
import os

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "market_valuation_breadth"
PINETREE_RAW = ROOT / "data" / "pinetree_archive" / "raw"

SECTOR_CODES = {
    "banking_index": "VNFIN",          # finance/banking proxy; VNFINLEAD also fetched below
    "banking_lead_index": "VNFINLEAD",
    "realty_index": "VNREAL",
    "industrial_index": "VNIND",
}


def _get_json(url: str, timeout: int = 30) -> dict:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_vndirect_dchart(symbol: str, start: str = "2022-01-01", end: Optional[str] = None) -> List[dict]:
    """Fetch daily OHLCV from VnDirect dchart API."""
    start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc) if end else datetime.now(timezone.utc)
    params = {
        "symbol": symbol,
        "resolution": "D",
        "from": int(start_dt.timestamp()),
        "to": int(end_dt.timestamp()) + 86400,
    }
    url = "https://dchart-api.vndirect.com.vn/dchart/history?" + urlencode(params)
    data = _get_json(url)
    if data.get("s") not in (None, "ok", "no_data") and not data.get("t"):
        raise RuntimeError(f"VnDirect dchart unexpected response for {symbol}: {data}")
    rows = []
    for i, ts in enumerate(data.get("t", [])):
        rows.append({
            "date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(),
            "symbol": symbol,
            "open": data.get("o", [None] * 0)[i] if i < len(data.get("o", [])) else None,
            "high": data.get("h", [None] * 0)[i] if i < len(data.get("h", [])) else None,
            "low": data.get("l", [None] * 0)[i] if i < len(data.get("l", [])) else None,
            "close": data.get("c", [None] * 0)[i] if i < len(data.get("c", [])) else None,
            "volume": data.get("v", [None] * 0)[i] if i < len(data.get("v", [])) else None,
            "source": "vndirect_dchart_public",
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
        })
    return rows


def build_sector_indices(start: str = "2022-01-01") -> List[dict]:
    out = []
    for name, code in SECTOR_CODES.items():
        rows = fetch_vndirect_dchart(code, start=start)
        for r in rows:
            r["series"] = name
        out.extend(rows)
        time.sleep(0.2)
    return out


# Pinetree text has many variants/encoding states. Keep regex permissive.
ADV_PATTERNS = [
    re.compile(r"(?:số\s*mã\s*tăng|ma\s*tang|mã\s*tăng)\D{0,30}(\d{1,4})", re.I),
    re.compile(r"(\d{1,4})\s*(?:mã|ma)\s*tăng", re.I),
]
DEC_PATTERNS = [
    re.compile(r"(?:số\s*mã\s*giảm|ma\s*giam|mã\s*giảm)\D{0,30}(\d{1,4})", re.I),
    re.compile(r"(\d{1,4})\s*(?:mã|ma)\s*giảm", re.I),
]
UNCH_PATTERNS = [
    re.compile(r"(?:tham\s*chiếu|đứng\s*giá|không\s*đổi|khong\s*doi)\D{0,30}(\d{1,4})", re.I),
]


def _first_int(patterns: Iterable[re.Pattern], text: str) -> Optional[int]:
    for pat in patterns:
        m = pat.search(text)
        if m:
            try:
                return int(m.group(1).replace(",", ""))
            except Exception:
                pass
    return None


def _vietstock_token(session: requests.Session) -> str:
    html = session.get("https://finance.vietstock.vn/ket-qua-giao-dich", timeout=30).text
    m = re.search(r"name=__RequestVerificationToken[^>]*value=([^\s>]+)", html)
    return m.group(1) if m else ""


def _parse_ms_date(s: str) -> Optional[str]:
    m = re.search(r"/Date\((\d+)\)/", str(s))
    if not m:
        return None
    return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc).date().isoformat()


def fetch_vietstock_vnindex_valuation(start: str = "2022-01-01") -> tuple[List[dict], List[dict]]:
    """Fetch VNINDEX PE/PB/PS from Vietstock public valuation chart endpoint.

    Returns (daily_rows, monthly_rows). Monthly rows use last available trading day
    of each month to avoid look-ahead within the month-end snapshot.
    """
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.vietstock.vn/",
        "X-Requested-With": "XMLHttpRequest",
    })
    token = _vietstock_token(s)
    if not token:
        return [], []
    r = s.post(
        "https://finance.vietstock.vn/Data/Valuation_GetRatiosMarketIndexForChart",
        data={"stockCode": "VNINDEX", "duration": "ALL", "__RequestVerificationToken": token},
        timeout=60,
    )
    if "application/json" not in (r.headers.get("content-type") or ""):
        return [], []
    payload = json.loads(r.content.decode("utf-8-sig"))
    rows = []
    for x in payload.get("data", []):
        d = _parse_ms_date(x.get("TradingDate"))
        if not d or d < start:
            continue
        rows.append({
            "date": d,
            "symbol": x.get("StockCode") or "VNINDEX",
            "vnindex_pe": x.get("PE"),
            "vnindex_pb": x.get("PB"),
            "vnindex_ps": x.get("PS"),
            "frequency": "daily",
            "source": "vietstock_finance_valuation_public",
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
        })
    rows = sorted(rows, key=lambda r: r["date"])
    monthly_last: OrderedDict[str, dict] = OrderedDict()
    for r in rows:
        ym = r["date"][:7]
        monthly_last[ym] = r
    monthly = []
    for ym, r in monthly_last.items():
        mrow = dict(r)
        mrow["month"] = ym
        mrow["frequency"] = "monthly_last_trading_day"
        monthly.append(mrow)
    return rows, monthly


def fetch_vietstock_breadth_for_date(session: requests.Session, token: str, date: str, exchange_cat: int = 1) -> Optional[dict]:
    """Fetch one-day HOSE breadth from Vietstock public trading-stat endpoint.

    Endpoint mirrors the visible finance.vietstock.vn/ket-qua-giao-dich page.
    It returns all stocks when pageSize is large; no login/paywall bypass.
    date accepts ISO YYYY-MM-DD.
    """
    yyyy, mm, dd = date.split("-")
    stocks = []
    idx = {}
    pages = 1
    page = 1
    while page <= pages:
        payload = {
            "catID": exchange_cat,  # 1=HOSE, 2=HNX, 3=UPCoM, 4=VN30, 5=HNX30 in site JS
            "date": f"{dd}/{mm}/{yyyy}",
            "page": page,
            "pageSize": 200,
            "__RequestVerificationToken": token,
        }
        r = session.post("https://finance.vietstock.vn/data/KQGDThongKeGiaPaging", data=payload, timeout=45)
        if "application/json" not in (r.headers.get("content-type") or ""):
            return None
        data = json.loads(r.content.decode("utf-8-sig"))
        if not isinstance(data, list) or len(data) < 3 or not isinstance(data[2], list):
            # Vietstock currently returns `{}` for page > 1 on this public endpoint.
            # Keep page-1 sample instead of failing the whole day.
            if stocks:
                break
            return None
        if data and data[0] and not idx:
            idx = data[0][0]
        stocks.extend(data[2])
        try:
            pages = int(data[-1][0]) if isinstance(data[-1], list) and data[-1] else page
        except Exception:
            pages = page
        page += 1
    if not stocks:
        return None
    adv = dec = unch = ref = 0
    for s in stocks:
        ch = (s.get("ChangeColor") or s.get("ChangeImage") or "").lower()
        change = s.get("Change")
        if ch == "up" or (isinstance(change, (int, float)) and change > 0):
            adv += 1
        elif ch == "down" or (isinstance(change, (int, float)) and change < 0):
            dec += 1
        else:
            unch += 1
    return {
        "date": date,
        "exchange": "HOSE",
        "advance_count": adv,
        "decline_count": dec,
        "unchanged_count": unch,
        "total_count": len(stocks),
        "ad_ratio": (adv / dec) if dec else None,
        "ad_spread": adv - dec,
        "vnindex_close": idx.get("CloseIndex"),
        "vnindex_change": idx.get("Change"),
        "vnindex_pct_change": idx.get("PerChange"),
        "coverage_note": "public endpoint currently exposes page 1 reliably; treat as partial breadth sample until full pagination/source is solved",
        "source": "vietstock_finance_kqgd_public",
        "parserVersion": "market_valuation_breadth_v2",
    }


def fetch_vietstock_breadth_history(dates: Iterable[str]) -> List[dict]:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.vietstock.vn/ket-qua-giao-dich",
        "X-Requested-With": "XMLHttpRequest",
    })
    token = _vietstock_token(s)
    rows = []
    if not token:
        return rows
    for d in dates:
        try:
            row = fetch_vietstock_breadth_for_date(s, token, d)
            if row:
                rows.append(row)
        except Exception:
            pass
        time.sleep(float(os.environ.get("VIETSTOCK_BREADTH_SLEEP", "0.03")))
    return rows


def parse_pinetree_breadth(raw_dir: Path = PINETREE_RAW) -> List[dict]:
    rows = []
    if not raw_dir.exists():
        return rows
    for path in sorted(raw_dir.glob("*.txt")):
        date = path.stem[:10]
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        adv = _first_int(ADV_PATTERNS, text)
        dec = _first_int(DEC_PATTERNS, text)
        unch = _first_int(UNCH_PATTERNS, text)
        if adv is None and dec is None:
            continue
        ratio = (adv / dec) if adv is not None and dec not in (None, 0) else None
        spread = (adv - dec) if adv is not None and dec is not None else None
        rows.append({
            "date": date,
            "advance_count": adv,
            "decline_count": dec,
            "unchanged_count": unch,
            "ad_ratio": ratio,
            "ad_spread": spread,
            "source": "pinetree_morning_brief_raw_parse",
            "source_file": str(path.relative_to(ROOT)),
            "parserVersion": "market_valuation_breadth_v1",
        })
    return rows


def write_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sector_rows = build_sector_indices("2022-01-01")
    valuation_daily_rows, valuation_monthly_rows = fetch_vietstock_vnindex_valuation("2022-01-01")
    # Use VNFIN dates as a trading-day calendar for public Vietstock breadth backfill.
    calendar_dates = sorted({r["date"] for r in sector_rows if r.get("series") == "banking_index"})
    start_filter = os.environ.get("MARKET_BREADTH_START")
    if start_filter:
        calendar_dates = [d for d in calendar_dates if d >= start_filter]
    vietstock_breadth_rows = fetch_vietstock_breadth_history(calendar_dates)
    pinetree_breadth_rows = parse_pinetree_breadth()
    write_csv(DATA_DIR / "sector_indices_vndirect_daily.csv", sector_rows)
    write_csv(DATA_DIR / "vnindex_valuation_vietstock_daily.csv", valuation_daily_rows)
    write_csv(DATA_DIR / "vnindex_pe_pb_vietstock_monthly.csv", valuation_monthly_rows)
    write_csv(DATA_DIR / "market_breadth_vietstock_daily.csv", vietstock_breadth_rows)
    write_csv(DATA_DIR / "market_breadth_pinetree_daily.csv", pinetree_breadth_rows)
    summary = {
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "sectorRows": len(sector_rows),
        "sectorSeries": SECTOR_CODES,
        "sectorDateMin": min((r["date"] for r in sector_rows), default=None),
        "sectorDateMax": max((r["date"] for r in sector_rows), default=None),
        "breadthRows": len(vietstock_breadth_rows),
        "breadthDateMin": min((r["date"] for r in vietstock_breadth_rows), default=None),
        "breadthDateMax": max((r["date"] for r in vietstock_breadth_rows), default=None),
        "pinetreeBreadthRows": len(pinetree_breadth_rows),
        "vnindexPeMonthly": {
            "status": "ok_public_vietstock",
            "rows": len(valuation_monthly_rows),
            "dateMin": min((r["date"] for r in valuation_monthly_rows), default=None),
            "dateMax": max((r["date"] for r in valuation_monthly_rows), default=None),
            "targetFields": ["date", "month", "vnindex_pe", "vnindex_pb", "source", "frequency"],
            "notes": "Monthly value is last available trading day of each month from Vietstock valuation chart endpoint.",
        },
        "outputs": {
            "sectorIndices": str(DATA_DIR / "sector_indices_vndirect_daily.csv"),
            "vnindexValuationDaily": str(DATA_DIR / "vnindex_valuation_vietstock_daily.csv"),
            "vnindexPePbMonthly": str(DATA_DIR / "vnindex_pe_pb_vietstock_monthly.csv"),
            "marketBreadth": str(DATA_DIR / "market_breadth_vietstock_daily.csv"),
            "marketBreadthPinetreeFallback": str(DATA_DIR / "market_breadth_pinetree_daily.csv"),
        },
    }
    (DATA_DIR / "market_valuation_breadth_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
