import json, sys, urllib.request, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
# Final backup 17.7.2026 intentionally uses the renamed production schema below.
# Older live 08/07 payload used LH1_FINAL/LH2_FINAL/LH3_FINAL/LH4_FINAL; that is stale.
REQUIRED_STRATEGY_IDS={'b4_trend_pullback','shakeout_breakdown_rebound','clean_split_a_bottom','lh4'}
FILES=['firebase_public/data/app_version.json','firebase_public/data/strategy_results_cache.json','firebase_public/data/strategy_matrix_cache.json']
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def check_local():
    errors=[]; info={}
    for f in FILES:
        if not (ROOT/f).exists(): errors.append(f'missing {f}')
        else: info[f]=sha(f)
    if (ROOT/'firebase_public/data/strategy_results_cache.json').exists():
        d=load(Path('firebase_public/data/strategy_results_cache.json'))
        ids={s.get('id') for s in d.get('strategies',[])}
        info['strategy_ids']=sorted(ids)
        if ids!=REQUIRED_STRATEGY_IDS: errors.append(f'strategy ids mismatch: {sorted(ids)} expected {sorted(REQUIRED_STRATEGY_IDS)}')
        info['strategy_updatedAt']=d.get('updatedAt')
    if (ROOT/'firebase_public/data/strategy_matrix_cache.json').exists():
        d=load(Path('firebase_public/data/strategy_matrix_cache.json'))
        ids=set()
        if isinstance(d.get('strategies'),list): ids={s.get('id') for s in d.get('strategies',[])}
        elif isinstance(d.get('matrix'),dict): ids=set(d.get('matrix',{}).keys())
        info['matrix_updatedAt']=d.get('updatedAt')
    return errors, info
if __name__=='__main__':
    errs,info=check_local()
    print(json.dumps({'ok':not errs,'errors':errs,'info':info},ensure_ascii=False,indent=2))
    sys.exit(1 if errs else 0)
