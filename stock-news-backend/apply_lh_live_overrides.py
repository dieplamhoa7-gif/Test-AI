from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'final_backup_17.7.2026'

# This script used to restore HTML from git HEAD and strategy data from
# data/live_overrides. That became a rollback vector when HEAD/overrides drifted.
# Keep it as a safe compatibility shim: if an older pipeline calls it, restore
# only the canonical 17/07 final backup payloads Hòa Đại ka approved.
CANONICAL_FILES = [
    'firebase_public/index.html',
    'firebase_public/stocks.html',
    'firebase_public/data/app_version.json',
    'firebase_public/data/strategy_results_cache.json',
    'firebase_public/data/strategy_matrix_cache.json',
    'data/app_version.json',
    'data/strategy_results_cache.json',
    'data/strategy_matrix_cache.json',
]


def main() -> None:
    if not BACKUP.exists():
        raise SystemExit(f'Missing canonical backup: {BACKUP}')
    for rel in CANONICAL_FILES:
        src = BACKUP / rel
        dst = ROOT / rel
        if not src.exists():
            raise SystemExit(f'Missing backup file: {src}')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print('restored', rel)
    print('LH live output guard applied: canonical final_backup_17.7.2026 restored; CW/news files left untouched.')


if __name__ == '__main__':
    main()
