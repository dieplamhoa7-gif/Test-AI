from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / 'news_refresh_deploy_lh.log'


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
        with LOG.open('a', encoding='utf-8') as f:
            f.write(p.stdout)
        print(p.stdout, end='', flush=True)
    if p.returncode:
        raise SystemExit(f'Command failed {p.returncode}: {cmd}')


def main() -> None:
    py = sys.executable
    log('START LHINVT news refresh + deploy')
    run([py, 'refresh_news_cache_lh.py'], timeout=900)
    # Keep EN cache fresh enough for English toggle without making the news job too slow.
    run([py, 'build_news_translate_cache.py', '--limit', '80', '--sleep', '0.05'], timeout=1200)
    run([py, 'build_firebase_cache_site.py'], timeout=300)
    run([py, 'verify_news_freshness.py'], timeout=60)
    run([py, 'verify_lh_final_version_lock.py'], timeout=60)
    firebase_bin = shutil.which('firebase') or shutil.which('firebase.cmd') or 'firebase.cmd'
    run([firebase_bin, 'deploy', '--project', 'security-1c731', '--config', 'firebase.lhinvt.deploy.json', '--only', 'hosting:lhinvt'], timeout=900)
    log('DONE LHINVT news refresh + deploy')


if __name__ == '__main__':
    main()
