import json, sys, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent

# Canonical DATA baseline: final_backup_17.7.2026, generated around 16:01.
# This intentionally locks strategy/app payloads to the backup Hòa Đại ka asked for.
# News and CW realtime caches are allowed to change; strategy/app/matrix are not.
REQUIRED_STRATEGY_IDS={'b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom','lh4'}
REQUIRED_UPDATED_AT='2026-07-17T16:01:03.515131'
REQUIRED_SHA={
    'firebase_public/data/app_version.json':'82d086c3cb3ffeb9a23dd150adec5f31c781378dc961c45e730fea70570554a7',
    'firebase_public/data/strategy_results_cache.json':'68253b140ef7143678f3ad1a8323b870b0ab5838c7afd1b45513f38b51ca61eb',
    'firebase_public/data/strategy_matrix_cache.json':'ab03841ab33d97100bddb5fe91946e6446d81e2610d687aed1c66fd92ace7400',
}
FILES=list(REQUIRED_SHA)

def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def check_local():
    errors=[]; info={}
    for f,expected in REQUIRED_SHA.items():
        path=ROOT/f
        if not path.exists():
            errors.append(f'missing {f}')
            continue
        actual=sha(f)
        info[f]=actual
        if actual!=expected:
            errors.append(f'{f} sha mismatch: {actual} expected {expected} (must match final_backup_17.7.2026)')
    sr=ROOT/'firebase_public/data/strategy_results_cache.json'
    if sr.exists():
        d=load(Path('firebase_public/data/strategy_results_cache.json'))
        ids={s.get('id') for s in d.get('strategies',[])}
        info['strategy_ids']=sorted(ids)
        if ids!=REQUIRED_STRATEGY_IDS:
            errors.append(f'strategy ids mismatch: {sorted(ids)} expected {sorted(REQUIRED_STRATEGY_IDS)}')
        info['strategy_updatedAt']=d.get('updatedAt')
        if d.get('updatedAt')!=REQUIRED_UPDATED_AT:
            errors.append(f'strategy updatedAt mismatch: {d.get("updatedAt")} expected {REQUIRED_UPDATED_AT}')
    mt=ROOT/'firebase_public/data/strategy_matrix_cache.json'
    if mt.exists():
        d=load(Path('firebase_public/data/strategy_matrix_cache.json'))
        info['matrix_updatedAt']=d.get('updatedAt')
        if d.get('updatedAt')!=REQUIRED_UPDATED_AT:
            errors.append(f'matrix updatedAt mismatch: {d.get("updatedAt")} expected {REQUIRED_UPDATED_AT}')
    return errors, info

if __name__=='__main__':
    errs,info=check_local()
    print(json.dumps({'ok':not errs,'errors':errs,'info':info},ensure_ascii=False,indent=2))
    sys.exit(1 if errs else 0)
