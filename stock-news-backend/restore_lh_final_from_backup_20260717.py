from pathlib import Path
import shutil, json, sys
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
# add restore marker to app_version public and data without breaking existing fields
for rel in ['firebase_public/data/app_version.json','data/app_version.json']:
    p=ROOT/rel
    d=json.loads(p.read_text(encoding='utf-8'))
    d['restoredFrom']='final_backup_17.7.2026'
    d['restoreReason']='Lock LH final web payload to verified 17.7.2026 backup; prevent schema drift.'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    print('marked',rel)
