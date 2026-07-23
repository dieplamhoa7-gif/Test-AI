from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parent
DATA = BASE / "data"
HISTORY = DATA / "history"
OUT = DATA / "macro_data_hub"
WEB_MACRO_DIR = WORKSPACE / "Vi mo"
WEB_DATA_DIR = WEB_MACRO_DIR / "data" / "macro_data_hub"


def load_latest_snapshot() -> tuple[Path, dict[str, Any]]:
    files = sorted(HISTORY.glob("????-??-??.json"), reverse=True)
    if not files:
        raise FileNotFoundError(f"No history snapshots in {HISTORY}")
    p = files[0]
    return p, json.loads(p.read_text(encoding="utf-8"))


def val(obj: Any, *keys: str) -> Any:
    cur = obj
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    if isinstance(cur, dict) and "value" in cur:
        return cur.get("value")
    return cur


def add(rows: list[dict[str, Any]], dataset: str, indicator: str, value: Any, unit: str = "", source: str = "", as_of: str = "", status: str = "ok", note: str = ""):
    rows.append({
        "dataset": dataset,
        "indicator": indicator,
        "value": value,
        "unit": unit,
        "source": source,
        "asOf": as_of,
        "status": status if value is not None else "missing",
        "note": note,
    })


def main() -> dict[str, Any]:
    snap_path, d = load_latest_snapshot()
    snap_date = d.get("date") or snap_path.stem
    fetched_at = d.get("fetchedAt") or datetime.now().isoformat()
    rows: list[dict[str, Any]] = []

    pt = d.get("mergedPinetree") or d.get("pinetree") or {}
    for name, unit in [
        ("interbankOvernight", "%"), ("deposit12m", "%"), ("govBond5y", "%"), ("govBond10y", "%"),
        ("usdVnd", "VND"), ("eurVnd", "VND"), ("cnyVnd", "VND"),
        ("vnindex", "pts"), ("hnx", "pts"), ("vn30", "pts"), ("upcom", "pts"),
        ("foreignNetBuyBn", "bn VND"), ("marketTurnoverBn", "bn VND"),
        ("vix", "pts"), ("brent", "USD/bbl"), ("gold", "USD/oz"),
    ]:
        add(rows, "pinetree_daily", name, val(pt, name), unit, pt.get("source", "Pinetree Morning Brief"), snap_date)

    vcb = d.get("vcbFx") or {}
    for pair in ["usdVnd", "eurVnd", "cnyVnd", "jpyVnd", "gbpVnd", "krwVnd", "sgdVnd", "audVnd"]:
        fx = vcb.get(pair) or {}
        add(rows, "vcb_fx", pair + ".buy", fx.get("buy"), "VND", "VCB XML", vcb.get("datetime", snap_date))
        add(rows, "vcb_fx", pair + ".sell", fx.get("sell"), "VND", "VCB XML", vcb.get("datetime", snap_date))

    glob = d.get("global") or {}
    for k, unit in [("vix","pts"),("sp500","pts"),("nasdaq","pts"),("us10y","%"),("dxy","pts"),("brent","USD/bbl"),("gold","USD/oz")]:
        g = glob.get(k) or {}
        add(rows, "global_markets", k, g.get("value"), unit, g.get("source", "Yahoo Chart"), g.get("asOf", snap_date))
        add(rows, "global_markets", k + ".change1d_pct", g.get("change1d_pct"), "%", g.get("source", "Yahoo Chart"), g.get("asOf", snap_date))

    sbv = d.get("sbvLiquidity") or {}
    summary = sbv.get("summary") or {}
    for k in ["reverseRepoIssueBn", "reverseRepoMaturityBn", "reverseRepoOutstandingBn", "reverseRepoNetBn", "tbillIssueBn", "tbillMaturityBn", "tbillOutstandingBn", "tbillNetBn", "totalLiquidityNetBn"]:
        add(rows, "sbv_liquidity", k, summary.get(k), "bn VND", "SBV", summary.get("date", snap_date), note="OMO + T-bill liquidity pack")
    add(rows, "sbv_liquidity", "omoRate", summary.get("omoRate"), "%", "SBV", summary.get("date", snap_date))
    add(rows, "sbv_liquidity", "discountRate", summary.get("discountRate"), "%", "SBV", summary.get("date", snap_date))
    add(rows, "sbv_liquidity", "refinancingRate", summary.get("refinancingRate"), "%", "SBV", summary.get("date", snap_date))

    rates = d.get("sbvRates") or sbv.get("interbankRates") or {}
    for currency in ["vnd", "usd"]:
        for tenor, value in (rates.get(currency) or {}).items():
            add(rows, "sbv_interbank", f"{currency}.{tenor}", value, "%", rates.get("source", "SBV/Pinetree fallback"), rates.get("weekRange") or snap_date, rates.get("status", "ok"))

    wb = (d.get("worldbank") or {}).get("data") or {}
    for k, item in wb.items():
        add(rows, "worldbank", k, item.get("latest"), "", "World Bank", item.get("latestYear", ""), note=item.get("indicatorCode", ""))

    te = d.get("tradingEconomicsVisible") or {}
    add(rows, "tradingeconomics_visible", "page_count", te.get("count"), "pages", "TradingEconomics public visible", snap_date, te.get("status", ""), te.get("note", ""))

    # Tổng cục Hải quan: public rendered table for monthly trade statistics.
    customs = d.get("customsTrade") or {}
    for k, item in (customs.get("rows") or {}).items():
        add(rows, "customs_trade", k, item.get("value"), customs.get("unit", "bn USD"), customs.get("source", "Tổng cục Hải quan Việt Nam"), customs.get("period", snap_date), customs.get("status", "ok"), f"changePrevPct={item.get('changePrevPct')}")

    fiin = d.get("fiinproxExcel") or {}
    add(rows, "fiinprox_excel", "rowCount", fiin.get("rowCount"), "rows", "FiinProX Excel", snap_date, fiin.get("status", ""))
    add(rows, "fiinprox_excel", "indicatorCount", fiin.get("indicatorCount"), "indicators", "FiinProX Excel", snap_date, fiin.get("status", ""))

    OUT.mkdir(parents=True, exist_ok=True)
    latest = {
        "status": "ok",
        "snapshot": str(snap_path),
        "date": snap_date,
        "fetchedAt": fetched_at,
        "generatedAt": datetime.now().isoformat(),
        "datasets": len({r["dataset"] for r in rows}),
        "indicators": len(rows),
        "rows": rows,
    }
    latest_json = json.dumps(latest, ensure_ascii=False, indent=2)
    (OUT / "latest.json").write_text(latest_json, encoding="utf-8")
    with (OUT / "latest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    (OUT / f"macro_data_hub_{snap_date}.json").write_text(latest_json, encoding="utf-8")

    # Mirror to the static macro web folder so the website can always fetch the
    # same latest database without reading internal FA paths. If a deploy job
    # publishes `Vi mo/`, these files go online with the web assets.
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DATA_DIR / "latest.json").write_text(latest_json, encoding="utf-8")
    with (WEB_DATA_DIR / "latest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    (WEB_DATA_DIR / f"macro_data_hub_{snap_date}.json").write_text(latest_json, encoding="utf-8")

    manifest = {
        "status": "ok",
        "latest": "data/macro_data_hub/latest.json",
        "latestCsv": "data/macro_data_hub/latest.csv",
        "date": snap_date,
        "generatedAt": latest["generatedAt"],
        "datasets": latest["datasets"],
        "indicators": latest["indicators"],
    }
    (WEB_MACRO_DIR / "macro_data_hub_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"status":"ok","datasets":latest["datasets"],"indicators":latest["indicators"],"out":str(OUT),"webOut":str(WEB_DATA_DIR)}, ensure_ascii=False))
    return latest


if __name__ == "__main__":
    main()
