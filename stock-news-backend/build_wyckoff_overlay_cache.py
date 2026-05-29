# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

from wyckoff_features import latest_snapshot

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "vn100_history_from_2023.json"
OUT = ROOT / "firebase_public" / "data" / "wyckoff_overlay_cache.json"


def main() -> None:
    symbols = (json.loads(DATA.read_text(encoding="utf-8")).get("symbols") or {})
    payload = {"symbols": {}, "count": 0}
    for symbol, obj in symbols.items():
        rows = (obj or {}).get("rows") or []
        if len(rows) < 30:
            continue
        try:
            payload["symbols"][symbol] = latest_snapshot(rows, symbol=symbol, lookback=60)
        except Exception:
            continue
    payload["count"] = len(payload["symbols"])
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUT), "count": payload["count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
