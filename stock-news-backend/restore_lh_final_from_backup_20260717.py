from pathlib import Path
import shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'final_backup_17.7.2026'
FILES=[
 'firebase_public/data/strategy_results_cache.json',
 'firebase_public/data/strategy_matrix_cache.json',
 'firebase_public/data/app_version.json',
 'data/strategy_results_cache.json',
 'data/strategy_matrix_cache.json',
 'data/app_version.json',
]
for rel in FILES:
    src=BACKUP/rel; dst=ROOT/rel
    if not src.exists(): raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src,dst)
    print('restored',rel)
print('restored exact final_backup_17.7.2026 payloads; no mutation applied')
