from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FINAL_MARKERS = [
    "20260621-lh-final-chartfix-1936",
    "wyckoffDetailPane",
    "loadWyckoffMethod",
    "stockVolBox",
    "loadAutoChart",
    "Ichimoku",
]
FORBIDDEN_MARKERS = [
    "lh-market-indicator-fallback-renderer",
]
HTML_FILES = [
    ROOT / "firebase_public" / "stocks.html",
    ROOT / "firebase_public" / "index.html",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    build_script = (ROOT / "build_firebase_cache_site.py").read_text(encoding="utf-8", errors="replace")
    if "HARD-SKIPPED" not in build_script or "firebase_public HTML is canonical" not in build_script:
        fail("build_firebase_cache_site.py no longer hard-skips HTML; risk of old frontend rollback")
    if not re.search(r"def\s+build_html\s*\([^)]*\)\s*(?:->[\s\w.\[\]|]+)?\s*:[\s\S]{0,700}?return", build_script):
        fail("build_html() does not appear to return early")

    for path in HTML_FILES:
        if not path.exists():
            fail(f"missing {path}")
        s = path.read_text(encoding="utf-8", errors="replace")
        missing = [m for m in FINAL_MARKERS if m not in s]
        if missing:
            fail(f"{path.name} missing final markers: {missing}")
        bad = [m for m in FORBIDDEN_MARKERS if m in s]
        if bad:
            fail(f"{path.name} contains forbidden temporary fallback markers: {bad}")

    template = ROOT / "app" / "dashboard_template.py"
    if template.exists():
        ts = template.read_text(encoding="utf-8", errors="replace")
        missing = [m for m in FINAL_MARKERS[:4] if m not in ts]
        if missing:
            fail(f"dashboard_template.py appears stale, missing {missing}")

    print("LH no-old-version regression guard OK")


if __name__ == "__main__":
    main()
