import json, sys, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'firebase_public'/'data'
LOCK=ROOT/'data'/'live_strategy_lock'
BACKUP=ROOT/'final_backup_17.7.2026'/'firebase_public'/'data'

# Strategy/app payload lock. If data/live_strategy_lock exists, it is the
# current user-approved live strategy payload (e.g. today's 4-strategy run).
# Otherwise we fall back to final_backup_17.7.2026. This prevents rollbacks while
# still allowing Hòa Đại ka to explicitly promote a new strategy payload.
REQUIRED_STRATEGY_IDS={'b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom','lh4'}
FILES=['app_version.json','strategy_results_cache.json','strategy_matrix_cache.json']

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_dir():
    return LOCK if LOCK.exists() else BACKUP

def check_local():
    errors=[]; info={'lockSource': str(source_dir())}
    srcdir=source_dir()
    for name in FILES:
        src=srcdir/name; dst=PUBLIC/name
        if not src.exists():
            errors.append(f'missing lock source {src}')
            continue
        if not dst.exists():
            errors.append(f'missing public file {dst}')
            continue
        expected=sha(src); actual=sha(dst)
        info[f'firebase_public/data/{name}']=actual
        info[f'expected/{name}']=expected
        if actual!=expected:
            errors.append(f'firebase_public/data/{name} sha mismatch: {actual} expected {expected} from {srcdir}')
    sr=PUBLIC/'strategy_results_cache.json'
    if sr.exists():
        d=load(sr)
        ids={s.get('id') for s in d.get('strategies',[])}
        info['strategy_ids']=sorted(ids)
        if ids!=REQUIRED_STRATEGY_IDS:
            errors.append(f'strategy ids mismatch: {sorted(ids)} expected {sorted(REQUIRED_STRATEGY_IDS)}')
        info['strategy_updatedAt']=d.get('updatedAt')
        info['strategy_marketLatestTradingDate']=d.get('marketLatestTradingDate')
    mt=PUBLIC/'strategy_matrix_cache.json'
    if mt.exists():
        d=load(mt)
        info['matrix_updatedAt']=d.get('updatedAt')
        info['buyCount']=d.get('buyCount')
        info['watchCount']=d.get('watchCount')
    return errors, info

if __name__=='__main__':
    errs,info=check_local()
    print(json.dumps({'ok':not errs,'errors':errs,'info':info},ensure_ascii=False,indent=2))
    sys.exit(1 if errs else 0)
