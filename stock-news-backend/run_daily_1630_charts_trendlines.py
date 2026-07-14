from __future__ import annotations
import os, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / 'logs'; LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / 'daily_1630_charts_trendlines.log'

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
        safe_stdout = p.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        sys.stdout.buffer.write(safe_stdout.encode('utf-8', errors='replace'))
        sys.stdout.buffer.flush()
    if p.returncode: raise SystemExit(f'Command failed {p.returncode}: {cmd}')

def main():
    py=sys.executable
    log('START 16:30 stock charts + trendlines')
    steps=[
        [py,'refresh_vn100_history_for_core12.py'],
        [py,'patch_market_latest_history.py'],
        [py,'patch_chart_files_latest_history.py'],
        [py,'publish_vn100_history_for_frontend.py'],
        # patch_frontend_extend_trendlines.py targets an older stocks.html pattern.
        # update_popup_ichimoku_all_symbols.py is too heavy for the daily deploy
        # path and can hold the whole chart update hostage; run it separately only
        # when that feature specifically changes.
        [py,'patch_market_latest_history.py'],
        [py,'patch_chart_files_latest_history.py'],
        [py,'publish_vn100_history_for_frontend.py'],
        [py,'build_lhinvt_stock_chart_db.py'],
    ]
    for s in steps: run(s, timeout=2400)
    run([py,'lhinvt_firebase_deploy.py'], timeout=1200)
    run([py,'verify_lhinvt_live_fresh.py'], timeout=120)
    run([py,'lhinvt_deploy_notify.py','1630_charts_trendlines','success'], timeout=60)
    log('DONE 16:30 stock charts + trendlines')

if __name__=='__main__': main()
