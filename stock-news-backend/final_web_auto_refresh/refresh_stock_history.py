from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from vnstock import Quote

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = DATA / "vn100_history_2025_06_2026_05_cache.json"
V3 = DATA / "v3_full_indicator_cache_v2.json"
RS = DATA / "rs_levels_vn100_cache.json"
TZ = timezone(timedelta(hours=7))
START = "2024-01-01"
REQUEST_DELAY_SECONDS = 3.3


def load_symbols() -> list[str]:
    symbols: set[str] = set()
    for path in [V3, RS]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items") if isinstance(data, dict) else data
        if isinstance(items, dict):
            symbols.update(str(s).upper() for s in items.keys())
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("symbol"):
                    symbols.add(str(item["symbol"]).upper())
    if not symbols and OUT.exists():
        data = json.loads(OUT.read_text(encoding="utf-8"))
        symbols.update(str(s).upper() for s in (data.get("symbols") or {}).keys())
    return sorted(symbols)


def clean_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    df = df.copy().sort_values("time").reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        rows.append({
            "time": str(pd.to_datetime(r["time"]).date()),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "volume": float(r["volume"]),
        })
    return rows


def main() -> None:
    end = datetime.now(TZ).strftime("%Y-%m-%d")
    symbols = load_symbols()
    old: dict[str, Any] = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8")).get("symbols") or {}
        except Exception:
            old = {}
    payload = {
        "createdAt": datetime.now(TZ).isoformat(timespec="seconds"),
        "start": START,
        "end": end,
        "source": "vnstock-vci-history-refresh-for-core12",
        "symbols": dict(old),
        "errors": [],
    }
    for i, sym in enumerate(symbols, 1):
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            df = Quote(symbol=sym, source="VCI").history(start=START, end=end, interval="1D")
            if df is None or df.empty or len(df) < 60:
                raise RuntimeError("missing/short history")
            rows = clean_rows(df)
            payload["symbols"][sym] = {"rows": rows}
            last = rows[-1]
            print(f"{i}/{len(symbols)} {sym} OK {last['time']} close={last['close']} vol={last['volume']}", flush=True)
        except Exception as exc:
            payload["errors"].append({"symbol": sym, "error": str(exc)[:180]})
            print(f"{i}/{len(symbols)} {sym} ERROR {exc}", flush=True)
    payload["count"] = len(payload["symbols"])
    payload["errorCount"] = len(payload["errors"])
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUT), "count": payload["count"], "errorCount": payload["errorCount"], "end": end}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
