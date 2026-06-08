from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from app.warrants.service import (
    _covered_warrant_symbols,
    _infer_underlying,
    _is_active_warrant,
    _quote_warrant,
    _static_map,
    enrich_warrant,
)

OUT_PATH = Path("firebase_public/data/warrants_data.json")
VERSION_PATH = Path("firebase_public/data/app_version.json")
MAX_WORKERS = 24


def build_item(sym: str, static: dict[str, dict]) -> dict | None:
    base = static.get(sym, {})
    quote = _quote_warrant(sym) or {"code": sym, "source": "vnstock-list"}
    merged = {**base, **quote}
    merged.setdefault("underlying", base.get("underlying") or _infer_underlying(sym))
    enriched = enrich_warrant(merged)
    return enriched if _is_active_warrant(enriched) else None


def main() -> None:
    symbols = _covered_warrant_symbols()
    static = _static_map()
    items: list[dict] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(build_item, sym, static): sym for sym in symbols}
        for future in as_completed(futures):
            try:
                item = future.result()
                if item:
                    items.append(item)
            except Exception as exc:
                print(f"skip {futures[future]}: {exc}")

    items.sort(key=lambda x: str(x.get("code") or ""))
    updated_at = datetime.now().isoformat()
    payload = {
        "items": items,
        "count": len(items),
        "source": "vps-realtime-scheduled-refresh",
        "updatedAt": updated_at,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    version_payload = {}
    if VERSION_PATH.exists():
        try:
            version_payload = json.loads(VERSION_PATH.read_text(encoding="utf-8"))
        except Exception:
            version_payload = {}
    version_payload["warrants"] = "warrant-realtime-" + datetime.now().strftime("%Y%m%d%H%M")
    VERSION_PATH.write_text(json.dumps(version_payload, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"refreshed {len(items)}/{len(symbols)} warrants at {updated_at}")


if __name__ == "__main__":
    main()
