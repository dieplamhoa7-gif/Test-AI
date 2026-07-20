from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'final_backup_17.7.2026'
LOCK = ROOT / 'data' / 'live_strategy_lock'

# This script used to restore HTML from git HEAD and strategy data from
# data/live_overrides. That became a rollback vector when HEAD/overrides drifted.
# Keep it as a safe compatibility shim: if an older pipeline calls it, restore
# only the current user-approved lock (data/live_strategy_lock), falling back to
# the canonical 17/07 final backup.
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
    source_root = LOCK if LOCK.exists() else BACKUP
    if not source_root.exists():
        raise SystemExit(f'Missing canonical strategy source: {source_root}')
    for rel in CANONICAL_FILES:
        if source_root == LOCK and rel.endswith('.json'):
            lock_rel = rel.replace('firebase_public/data/', '').replace('data/', '')
            src = LOCK / lock_rel
        else:
            src = BACKUP / rel
        dst = ROOT / rel
        if not src.exists():
            raise SystemExit(f'Missing backup file: {src}')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print('restored', rel)
    print(f'LH live output guard applied from {source_root}; CW/news files left untouched.')


if __name__ == '__main__':
    main()
