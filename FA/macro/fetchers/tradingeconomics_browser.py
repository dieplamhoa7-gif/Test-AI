"""
Browser fetcher: TradingEconomics visible Vietnam macro pages
=============================================================

Uses Playwright/Chromium like a normal browser to read visible public page data.
It does NOT bypass login/subscription. CSV Download requires subscription; this
fetcher only extracts public visible summary tables/news/value on each page.

Outputs latest visible values for indicators such as:
- interbank-rate, interest-rate, money-supply-m0/m1/m2
- inflation-cpi, retail-sales-yoy, foreign-direct-investment
- industrial-production, balance-of-trade, manufacturing-pmi
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SOURCE_NAME = "TradingEconomics visible browser pages"
PARSER_VERSION = "te_browser_visible_v1"

BASE_URL = "https://tradingeconomics.com/vietnam"
PAGES: dict[str, str] = {
    "interbankRate": "interbank-rate",
    "interestRate": "interest-rate",
    "moneySupplyM0": "money-supply-m0",
    "moneySupplyM1": "money-supply-m1",
    "moneySupplyM2": "money-supply-m2",
    "inflationCpi": "inflation-cpi",
    "inflationRateMom": "inflation-rate-mom",
    "retailSalesYoy": "retail-sales-yoy",
    "foreignDirectInvestment": "foreign-direct-investment",
    "industrialProduction": "industrial-production",
    "balanceOfTrade": "balance-of-trade",
    "manufacturingPmi": "manufacturing-pmi",
    "foreignExchangeReserves": "foreign-exchange-reserves",
}


def _num(s: Any) -> float | None:
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").strip())
    except Exception:
        return None


def _parse_tables(tables: list[list[list[str]]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    main: dict[str, Any] = {}
    related: list[dict[str, Any]] = []
    for table in tables:
        if not table:
            continue
        header = [h.strip() for h in table[0]]
        # Main stats table: Actual Previous Highest Lowest Dates Unit Frequency
        if "Actual" in header and "Previous" in header:
            row = table[1] if len(table) > 1 else []
            for k, v in zip(header, row):
                main[k.lower()] = v
            main["actualValue"] = _num(main.get("actual"))
            main["previousValue"] = _num(main.get("previous"))
        # Related table: Related Last Previous Unit Reference
        if "Related" in header and "Last" in header:
            for row in table[1:]:
                if len(row) >= 5:
                    related.append({
                        "indicator": row[0],
                        "last": _num(row[1]),
                        "previous": _num(row[2]),
                        "unit": row[3],
                        "reference": row[4],
                    })
    return main, related


def fetch_one(page, key: str, slug: str, timeout_ms: int = 25000) -> dict[str, Any]:
    url = f"{BASE_URL}/{slug}"
    page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    # Give chart/table scripts a moment. Use fixed short wait; no sensitive action.
    page.wait_for_timeout(1800)
    payload = page.evaluate("""() => {
      const title = document.querySelector('h1')?.innerText || document.title;
      const h2 = document.querySelector('h2')?.innerText || '';
      const tables = [...document.querySelectorAll('table')].map(table =>
        [...table.querySelectorAll('tr')].map(tr =>
          [...tr.querySelectorAll('th,td')].map(td => td.innerText.trim()).filter(Boolean)
        ).filter(r => r.length)
      );
      const body = document.body.innerText.slice(0, 3000);
      return {url: location.href, title, h2, tables, body};
    }""")
    main, related = _parse_tables(payload.get("tables", []))
    return {
        "key": key,
        "slug": slug,
        "url": payload.get("url", url),
        "title": payload.get("title"),
        "summary": payload.get("h2"),
        "actual": main.get("actualValue"),
        "previous": main.get("previousValue"),
        "unit": main.get("unit"),
        "reference": main.get("reference") or main.get("dates"),
        "frequency": main.get("frequency"),
        "stats": main,
        "related": related,
        "parserVersion": PARSER_VERSION,
    }


def fetch(pages: dict[str, str] | None = None, headless: bool = True) -> dict[str, Any]:
    pages = pages or PAGES
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"source": SOURCE_NAME, "status": "not_installed", "install": "pip install playwright && python -m playwright install chromium"}

    results: dict[str, Any] = {}
    errors: dict[str, str] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            viewport={"width": 1366, "height": 900},
        )
        page = context.new_page()
        for key, slug in pages.items():
            try:
                results[key] = fetch_one(page, key, slug)
            except Exception as e:
                errors[key] = str(e)[:220]
        browser.close()

    return {
        "source": SOURCE_NAME,
        "parserVersion": PARSER_VERSION,
        "fetchedAt": datetime.now().isoformat(),
        "status": "ok" if results else "error",
        "data": results,
        "errors": errors or None,
        "note": "Visible public page data only; CSV/history download requires TradingEconomics subscription/login.",
    }


def _append_visible_history_csv(result: dict[str, Any], root: Path) -> None:
    import csv
    csv_path = root / "data" / "tradingeconomics_visible_history.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["fetchedDate", "key", "indicator", "value", "previous", "unit", "reference", "frequency", "url"]
    fetched_date = (result.get("fetchedAt") or "")[:10]
    existing = set()
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("fetchedDate"), r.get("key"), r.get("indicator")))
    rows = []
    for key, item in (result.get("data") or {}).items():
        if item.get("actual") is not None:
            rows.append({"fetchedDate": fetched_date, "key": key, "indicator": item.get("title") or key, "value": item.get("actual"), "previous": item.get("previous"), "unit": item.get("unit"), "reference": item.get("reference"), "frequency": item.get("frequency"), "url": item.get("url")})
        for rel in item.get("related") or []:
            if rel.get("last") is not None:
                rows.append({"fetchedDate": fetched_date, "key": key + ".related", "indicator": rel.get("indicator"), "value": rel.get("last"), "previous": rel.get("previous"), "unit": rel.get("unit"), "reference": rel.get("reference"), "frequency": "related_visible", "url": item.get("url")})
    write_header = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            w.writeheader()
        for r in rows:
            ident = (str(r.get("fetchedDate")), str(r.get("key")), str(r.get("indicator")))
            if ident not in existing:
                w.writerow(r)


def save(result: dict[str, Any], out_path: str | Path | None = None) -> str:
    root = Path(__file__).resolve().parents[2]
    out = Path(out_path) if out_path else root / "data" / "tradingeconomics_visible_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    # Also keep dated snapshot + append-only visible history CSV for daily accumulation.
    d = (result.get("fetchedAt") or "")[:10] or "unknown-date"
    hist = root / "data" / "tradingeconomics_history" / f"{d}.json"
    hist.parent.mkdir(parents=True, exist_ok=True)
    hist.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    _append_visible_history_csv(result, root)
    return str(out)


if __name__ == "__main__":
    res = fetch(headless=True)
    path = save(res)
    print(json.dumps({"status": res.get("status"), "count": len(res.get("data", {})), "errors": res.get("errors"), "out": path}, ensure_ascii=False, indent=2))
