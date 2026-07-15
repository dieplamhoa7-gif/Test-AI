from __future__ import annotations
import os, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / 'logs'; LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / 'daily_1545_strategy_refresh.log'


def log(msg: str):
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def run(cmd: list[str], timeout: int | None = None):
    log('RUN ' + ' '.join(cmd))
    env = os.environ.copy()
    env.setdefault('PYTHONUTF8', '1')
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        encoding='utf-8',
        errors='replace',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if p.stdout:
        with LOG.open('a', encoding='utf-8') as f:
            f.write(p.stdout)
        safe_stdout = p.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        sys.stdout.buffer.write(safe_stdout.encode('utf-8', errors='replace'))
        sys.stdout.buffer.flush()
    if p.returncode:
        raise SystemExit(f'Command failed {p.returncode}: {cmd}')


def main():
    py = sys.executable
    log('START 15:45 strategy refresh')
    steps = [
        [py, 'patch_market_latest_history.py'],
        [py, 'build_lh_canonical_indicators_daily.py'],
        [py, 'build_strategy_results_from_indicator_cache.py'],
        [py, 'build_lhinvt_stock_chart_db.py'],
    ]
    for s in steps:
        run(s, timeout=900)
    run([py, 'lhinvt_firebase_deploy.py'], timeout=1200)
    run([py, 'lhinvt_deploy_notify.py', '1545_strategy_refresh', 'success'], timeout=60)
    log('DONE 15:45 strategy refresh')


if __name__ == '__main__':
    main()
