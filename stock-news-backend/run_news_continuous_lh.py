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

# NOTE 2026-07-27:
# This scheduled task still lives in the legacy backend directory, but the
# approved LHINVT frontend now lives in render_backend_work/stock-news-backend.
# Never deploy this legacy firebase_public folder: it contains old index/stocks
# HTML and caused https://lhinvt.web.app/ to roll back at 09:34.
ROOT = Path(__file__).resolve().parent
CANONICAL_ROOT = Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\render_backend_work\stock-news-backend')
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


def run(cmd: list[str], timeout: int | None = None, cwd: Path | None = None) -> None:
    workdir = cwd or ROOT
    log('RUN ' + ' '.join(cmd) + f' [cwd={workdir}]')
    env = os.environ.copy()
    env.setdefault('PYTHONUTF8', '1')
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    p = subprocess.run(cmd, cwd=workdir, env=env, text=True, encoding='utf-8', errors='replace', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
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


def copy_news_to_canonical() -> None:
    for name in ['news_cache.json', 'news_cache_en.json']:
        src = ROOT / 'data' / name
        if not src.exists():
            log(f'WARN missing {src}; skip copy')
            continue
        for dst in [ROOT / 'firebase_public' / 'data' / name, CANONICAL_ROOT / 'data' / name, CANONICAL_ROOT / 'firebase_public' / 'data' / name]:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            log(f'COPIED {src} -> {dst}')


def sync_legacy_html_from_canonical() -> None:
    # Defense-in-depth: even if somebody accidentally deploys legacy ROOT later,
    # it should no longer publish the old frontend.
    for rel in ['index.html', 'stocks.html', 'news-page.html', 'stock-report.html']:
        src = CANONICAL_ROOT / 'firebase_public' / rel
        dst = ROOT / 'firebase_public' / rel
        if src.exists() and dst.exists():
            shutil.copyfile(src, dst)
            log(f'SYNCED legacy HTML {dst} from canonical')


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
        log('START continuous news refresh - canonical deploy protected')
        run([py, 'refresh_news_cache_lh.py'], timeout=900, cwd=ROOT)
        copy_news_to_canonical()
        sync_legacy_html_from_canonical()
        # Verify and deploy ONLY from canonical backend so scheduled news refresh
        # cannot roll LHINVT frontend back to legacy HTML.
        news_verify_root = CANONICAL_ROOT if (CANONICAL_ROOT / 'verify_news_freshness.py').exists() else ROOT
        run([py, 'verify_news_freshness.py'], timeout=60, cwd=news_verify_root)
        run([py, 'verify_lh_final_version_lock.py'], timeout=60, cwd=CANONICAL_ROOT)
        run([py, 'verify_lh_final_frontend_markers.py'], timeout=60, cwd=CANONICAL_ROOT)
        firebase_bin = shutil.which('firebase') or shutil.which('firebase.cmd') or 'firebase.cmd'
        run([firebase_bin, 'deploy', '--project', 'security-1c731', '--config', 'firebase.lhinvt.deploy.json', '--only', 'hosting:lhinvt'], timeout=900, cwd=CANONICAL_ROOT)
        log('DONE continuous news refresh - canonical deploy protected')
    finally:
        try:
            LOCK.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == '__main__':
    main()
