from __future__ import annotations

"""Final 28.07.2026 guard for LHINVT data refreshes.

This guard intentionally does NOT restore from old backup/version folders.
It validates that the canonical deploy payload exists in firebase_public and
that data refreshes have not removed the approved frontend entry points.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "firebase_public"
REQUIRED_FRONTEND = [
    "stocks.html",
    "stock-report.html",
    "cw.html",
    "warrants.html",
    "macro.html",
    "news-page.html",
    "account.html",
]
REQUIRED_DATA = [
    "data/app_version.json",
    "data/strategy_results_cache.json",
    "data/strategy_matrix_cache.json",
]
FORBIDDEN_ROOT_DIRS = [
    "final_backup_17.7.2026",
    "tmp_stock_report_versions",
    "_trash_old_cache_20260717_155803",
    "_recovery_engine_20260708",
]


def main() -> None:
    missing = [str(PUBLIC / rel) for rel in REQUIRED_FRONTEND + REQUIRED_DATA if not (PUBLIC / rel).exists()]
    if missing:
        raise SystemExit("Missing canonical LHINVT files:\n" + "\n".join(missing))
    old_dirs = [name for name in FORBIDDEN_ROOT_DIRS if (ROOT / name).exists()]
    if old_dirs:
        raise SystemExit("Old version folders must stay out of canonical repo root: " + ", ".join(old_dirs))
    print("LHINVT final 28.07.2026 guard OK: canonical firebase_public payload present; no old root version folders.")


if __name__ == "__main__":
    main()
