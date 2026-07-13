from __future__ import annotations
import os, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / 'logs'; LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / 'daily_1530_prices_indicators_cw.log'

def log(msg: str):
    line=f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f: f.write(line+'\n')

def run(cmd: list[str], timeout: int|None=None):
    log('RUN '+ ' '.join(cmd))
    env=os.environ.copy(); env.setdefault('PYTHONUTF8','1'); env.setdefault('PYTHONIOENCODING','utf-8')
    p=subprocess.run(cmd,cwd=ROOT,env=env,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    if p.stdout:
        with LOG.open('a', encoding='utf-8') as f: f.write(p.stdout)
        print(p.stdout,end='',flush=True)
    if p.returncode: raise SystemExit(f'Command failed {p.returncode}: {cmd}')

def main():
    py=sys.executable
    log('START 15:30 prices + indicators + CW (NO R/S)')
    # No run_rs_levels_* here by design: keep job light.
    steps=[
        [py,'build_v3_full_indicator_cache_v2.py'],
        [py,'build_weekly_indicators_vn100_cache.py'],
        [py,'build_monthly_indicators_vn100_cache.py'],
        [py,'refresh_market_prices_lh.py'],
        [py,'refresh_warrants_cache_lh.py'],
        [py,'build_firebase_cache_site.py'],
        [py,'patch_market_latest_history.py'],
        [py,'publish_vn100_history_for_frontend.py'],
        [py,'build_lhinvt_stock_chart_db.py'],
    ]
    for s in steps: run(s, timeout=1800)
    # Hard guard: never deploy LHINVT if covered-warrant data fell back to
    # stale firebase-static-cache or carries stale daysLeft values.
    run([py,'verify_lhinvt_warrants_fresh.py'], timeout=120)
    firebase=shutil.which('firebase') or shutil.which('firebase.cmd') or 'firebase.cmd'
    run([firebase,'deploy','--project','security-1c731','--config','firebase.lhinvt.json','--only','hosting'], timeout=600)
    run([py,'lhinvt_deploy_notify.py','1530_prices_indicators_cw','success'], timeout=60)
    log('DONE 15:30 prices + indicators + CW')

if __name__=='__main__': main()
