from __future__ import annotations

"""Safe compatibility shim for older LHINVT update jobs.

Final 28.07.2026 rule: the canonical frontend is the current firebase_public/*
payload. Data refreshes must not restore HTML or pull from archived old version
folders. If data/live_strategy_lock exists, only the approved strategy JSON files
are refreshed from it; otherwise this script is intentionally a no-op.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "data" / "live_strategy_lock"
PUBLIC_DATA = ROOT / "firebase_public" / "data"
DATA = ROOT / "data"
STRATEGY_JSON = [
    "app_version.json",
    "strategy_results_cache.json",
    "strategy_matrix_cache.json",
]


def main() -> None:
    if not LOCK.exists():
        print("No data/live_strategy_lock found; keeping current canonical firebase_public payload unchanged.")
        return
    for name in STRATEGY_JSON:
        src = LOCK / name
        if not src.exists():
            raise SystemExit(f"Missing approved strategy lock file: {src}")
        for dst_root in (PUBLIC_DATA, DATA):
            dst = dst_root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print("updated", dst.relative_to(ROOT))
    print("LH live output guard applied from data/live_strategy_lock; frontend HTML left untouched.")


if __name__ == "__main__":
    main()
