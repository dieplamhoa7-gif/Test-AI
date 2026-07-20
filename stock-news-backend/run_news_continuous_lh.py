from __future__ import annotations

import os
import shutil
import subprocess
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
from datetime import datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / 'news_continuous_lh.log'
LOCK = LOG_DIR / 'news_continuous_lh.lock'

ACTIVE_START = time(7, 30)
ACTIVE_END = time(18, 30)


def log(msg: str) -> None:
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def run(cmd: list[str], timeout: int | None = None) -> None:
    log('RUN ' + ' '.join(cmd))
    env = os.environ.copy()
    env.setdefault('PYTHONUTF8', '1')
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    p = subprocess.run(cmd, cwd=ROOT, env=env, text=True, encoding='utf-8', errors='replace', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if p.stdout:
        print(p.stdout, end='', flush=True)
        with LOG.open('a', encoding='utf-8') as f:
            f.write(p.stdout)
    if p.returncode:
        raise SystemExit(f'Command failed {p.returncode}: {cmd}')


def should_run_now() -> bool:
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    return ACTIVE_START <= now.time() <= ACTIVE_END


def main() -> None:
    if '--force' not in sys.argv and not should_run_now():
        log('SKIP outside active weekday window')
        return
    if LOCK.exists():
        try:
            age = datetime.now().timestamp() - LOCK.stat().st_mtime
            if age < 3600:
                log(f'SKIP previous run still locked age={age:.0f}s')
                return
        except Exception:
            pass
    LOCK.write_text(str(os.getpid()), encoding='utf-8')
    try:
        py = sys.executable
        log('START continuous news refresh')
        run([py, 'refresh_news_cache_lh.py'], timeout=900)
        run([py, 'build_firebase_cache_site.py'], timeout=300)
        run([py, 'verify_news_freshness.py'], timeout=60)
        run([py, 'verify_lh_final_version_lock.py'], timeout=60)
        run([py, 'verify_lh_final_frontend_markers.py'], timeout=60)
        firebase_bin = shutil.which('firebase') or shutil.which('firebase.cmd') or 'firebase.cmd'
        run([firebase_bin, 'deploy', '--project', 'security-1c731', '--config', 'firebase.lhinvt.deploy.json', '--only', 'hosting:lhinvt'], timeout=900)
        log('DONE continuous news refresh')
    finally:
        try:
            LOCK.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == '__main__':
    main()
