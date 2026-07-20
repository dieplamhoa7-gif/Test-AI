from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "unified_macro"


def _num(v: Any) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip().replace(",", "")
    try:
        return float(s)
    except Exception:
        return None


def _add(rows: list[dict[str, Any]], *, date: str, category: str, indicator: str, value: Any,
         source: str, source_file: str, frequency: str = "daily", unit: str | None = None,
         note: str | None = None) -> None:
    fv = _num(value)
    if fv is None:
        return
    rows.append({
        "date": date,
        "category": category,
        "indicator": indicator,
        "value": fv,
        "unit": unit or "",
        "frequency": frequency,
        "source_file": source_file,
        "sheet": "public_auto",
        "orientation": "api_or_scrape",
        "source": source,
        "note": note or "",
        "parserVersion": "public_macro_timeline_v1",
    })


def build(snapshot: dict[str, Any], existing_fiin: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build an auditable public-source macro timeline for daily automation.

    FiinProX is treated as optional/manual backfill. If it has rows, we preserve those rows
    through fiinprox_excel.save_unified before appending public rows. If it has no rows, this
    still writes a useful timeline from public/free replacement sources.
    """
    d = str(snapshot.get("date") or datetime.now().date())
    fetched = snapshot.get("fetchedAt") or datetime.now().isoformat()
    rows: list[dict[str, Any]] = []

    # Pinetree / merged daily market macro pack
    pt = snapshot.get("mergedPinetree") or snapshot.get("pinetree") or {}
    pt_map = {
        "interbankOvernight": ("rates", "Liên NH overnight", "%"),
        "deposit12m": ("rates", "Lãi suất tiết kiệm 12T", "%"),
        "usdVnd": ("fx", "USD/VND", "VND"),
        "eurVnd": ("fx", "EUR/VND", "VND"),
        "cnyVnd": ("fx", "CNY/VND", "VND"),
        "vnindex": ("market", "VNINDEX", "index"),
        "foreignNetBuyBn": ("market", "Khối ngoại mua ròng", "bn VND"),
        "marketTurnoverBn": ("market", "GTGD thị trường", "bn VND"),
        "vix": ("global_risk", "VIX", "index"),
        "brent": ("global_risk", "Brent", "USD/bbl"),
        "dxy": ("global_risk", "DXY", "index"),
        "us10y": ("global_risk", "US10Y", "%"),
    }
    for key, (cat, name, unit) in pt_map.items():
        item = pt.get(key)
        val = item.get("value") if isinstance(item, dict) else item
        src = item.get("source") if isinstance(item, dict) else None
        _add(rows, date=d, category=cat, indicator=name, value=val, unit=unit,
             source=src or "Pinetree/merged public macro", source_file="daily_snapshot")

    # VCB FX full pack
    for pair, item in (snapshot.get("vcbFx") or {}).items():
        if isinstance(item, dict):
            _add(rows, date=d, category="fx", indicator=f"{pair} sell", value=item.get("sell"), unit="VND",
                 source="Vietcombank public XML", source_file="vcb_fx_xml")

    # SBV rates / liquidity / OMO
    sbv = snapshot.get("sbvRates") or {}
    for tenor, val in (sbv.get("vnd") or {}).items():
        _add(rows, date=d, category="rates", indicator=f"SBV interbank VND {tenor}", value=val, unit="%",
             source=sbv.get("source") or "SBV public", source_file="sbv_rates")
    omo = snapshot.get("omoData") or {}
    _add(rows, date=omo.get("date") or d, category="liquidity_omo", indicator="OMO net injection/withdrawal", value=omo.get("totalNetBn"), unit="bn VND",
         source="SBV public OMO", source_file="sbv_omo")
    liq = snapshot.get("sbvLiquidity") or {}
    for k, name in {"reverseRepoIssueBn":"Reverse repo issue", "tbillIssueBn":"T-bill issue", "totalLiquidityNetBn":"Total SBV liquidity net"}.items():
        _add(rows, date=d, category="liquidity_omo", indicator=name, value=(liq.get("summary") or {}).get(k), unit="bn VND",
             source="SBV public liquidity pages", source_file="sbv_liquidity")

    # Customs trade
    ct = snapshot.get("customsTrade") or {}
    period = ct.get("period") or d
    for key, item in (ct.get("rows") or {}).items():
        val = item.get("value") if isinstance(item, dict) else item
        label = item.get("label") if isinstance(item, dict) else key
        _add(rows, date=period, category="trade_bop", indicator=f"Customs {label}", value=val, unit=ct.get("unit") or "bn USD",
             frequency="monthly", source=ct.get("source") or "Vietnam Customs public", source_file="customs_trade")

    # TradingEconomics visible pages
    te_file = ROOT / "data" / "tradingeconomics_visible_latest.json"
    try:
        te = json.loads(te_file.read_text(encoding="utf-8"))
        for key, item in (te.get("data") or {}).items():
            _add(rows, date=d, category="macro_growth_inflation", indicator=item.get("title") or key, value=item.get("actual"),
                 unit=item.get("unit"), frequency=item.get("frequency") or "visible", source="TradingEconomics visible public scrape",
                 source_file="tradingeconomics_visible_latest", note=item.get("url"))
    except Exception:
        pass

    # De-duplicate
    seen = set(); unique = []
    for r in rows:
        key = (r["date"], r["category"], r["indicator"], r["value"], r["source"])
        if key not in seen:
            seen.add(key); unique.append(r)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "macro_timeline_public_auto.csv"
    json_path = OUT_DIR / "macro_timeline_public_auto.json"
    fields = ["date","category","indicator","value","unit","frequency","source_file","sheet","orientation","source","note","parserVersion"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(unique)
    payload = {"source":"Public/free replacement sources", "fetchedAt":fetched, "status":"ok" if unique else "no_rows", "rowCount":len(unique), "rows":unique}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": payload["status"], "rowCount": len(unique), "csv": str(csv_path), "json": str(json_path)}
