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
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
    breadth_rows = parse_pinetree_breadth()
    write_csv(DATA_DIR / "sector_indices_vndirect_daily.csv", sector_rows)
    write_csv(DATA_DIR / "market_breadth_pinetree_daily.csv", breadth_rows)
    summary = {
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "sectorRows": len(sector_rows),
        "sectorSeries": SECTOR_CODES,
        "sectorDateMin": min((r["date"] for r in sector_rows), default=None),
        "sectorDateMax": max((r["date"] for r in sector_rows), default=None),
        "breadthRows": len(breadth_rows),
        "breadthDateMin": min((r["date"] for r in breadth_rows), default=None),
        "breadthDateMax": max((r["date"] for r in breadth_rows), default=None),
        "vnindexPeMonthly": {
            "status": "missing_public_source_not_confirmed",
            "needed": True,
            "targetFields": ["date", "vnindex_pe", "vnindex_pb", "source", "frequency"],
            "notes": "No reliable free public historical VNIndex P/E API confirmed yet. Add FiinProX export parser or vetted public endpoint when found.",
        },
        "outputs": {
            "sectorIndices": str(DATA_DIR / "sector_indices_vndirect_daily.csv"),
            "marketBreadth": str(DATA_DIR / "market_breadth_pinetree_daily.csv"),
        },
    }
    (DATA_DIR / "market_valuation_breadth_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
