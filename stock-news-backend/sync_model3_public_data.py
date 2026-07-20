from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PUBLIC_DATA = ROOT / "firebase_public" / "data"
MARKET_SRC = DATA / "market_data.json"
MARKET_DST = PUBLIC_DATA / "market_data.json"
APP_VERSION_PATHS = [DATA / "app_version.json", PUBLIC_DATA / "app_version.json"]
DB = DATA / "lhinvt_stock_chart.db"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_date(value: Any) -> str:
    text = str(value or "")[:10]
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return text
    return ""


def max_item_date(obj: Any) -> str:
    items = obj.get("items") if isinstance(obj, dict) else obj
    dates = []
    for item in items or []:
        if isinstance(item, dict):
            d = parse_date(item.get("latestCandleDate") or item.get("date") or item.get("tradingDate"))
            if d:
                dates.append(d)
    return max(dates) if dates else ""


def sync_market_data() -> dict[str, Any]:
    if not MARKET_SRC.exists():
        raise SystemExit(f"Missing source market data: {MARKET_SRC}")
    src = read_json(MARKET_SRC)
    src_date = parse_date(src.get("latestTradingDate")) or max_item_date(src)
    if not src_date:
        raise SystemExit("Source market_data.json has no latestTradingDate/date; refusing to publish")

    # Copy canonical generated market data to public payload. This prevents build_firebase_cache_site.py
    # or restored backup folders from leaving stale public data behind.
    write_json(MARKET_DST, src)

    now = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")
    for p in APP_VERSION_PATHS:
        v = read_json(p) if p.exists() else {}
        v.update({
            "marketDataRefresh": f"market-data-{now[:10].replace('-', '')}",
            "model3DataFlow": "sync_model3_public_data.py: data/market_data.json -> firebase_public/data/market_data.json; build_lhinvt_stock_chart_db.py",
            "model3DataAsOf": src_date,
            "model3DataUpdatedAt": src.get("updatedAt") or src.get("priceUpdatedAt") or now,
            "model3FreshnessGuard": "deploy must fail if public market_data is older than canonical data/market_data.json",
        })
        write_json(p, v)
    return {"items": len(src.get("items") or []), "latestTradingDate": src_date, "updatedAt": src.get("updatedAt")}


def rebuild_db() -> dict[str, Any]:
    script = ROOT / "build_lhinvt_stock_chart_db.py"
    if not script.exists():
        return {"skipped": "missing build_lhinvt_stock_chart_db.py"}
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    if not DB.exists():
        raise SystemExit("DB rebuild did not produce data/lhinvt_stock_chart.db")
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute("select count(*) n, max(latest_date) latest_date, max(updated_at) updated_at from symbols").fetchone()
        return dict(row)
    finally:
        con.close()


def verify() -> dict[str, Any]:
    src = read_json(MARKET_SRC)
    dst = read_json(MARKET_DST)
    src_date = parse_date(src.get("latestTradingDate")) or max_item_date(src)
    dst_date = parse_date(dst.get("latestTradingDate")) or max_item_date(dst)
    if not dst_date or dst_date < src_date:
        raise SystemExit(f"Public market data stale: public={dst_date}, source={src_date}")
    if len(dst.get("items") or []) < 50:
        raise SystemExit(f"Public market_data item count too low: {len(dst.get('items') or [])}")
    return {"sourceDate": src_date, "publicDate": dst_date, "publicItems": len(dst.get("items") or [])}


def main() -> None:
    synced = sync_market_data()
    db = rebuild_db()
    checked = verify()
    print(json.dumps({"ok": True, "synced": synced, "db": db, "verify": checked}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
