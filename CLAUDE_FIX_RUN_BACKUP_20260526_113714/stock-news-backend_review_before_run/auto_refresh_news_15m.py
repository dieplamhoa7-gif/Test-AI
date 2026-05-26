import subprocess
import sys
import time
from datetime import datetime

INTERVAL_SECONDS = 15 * 60

COMMANDS = [
    [sys.executable, 'refresh_news_cache_lh.py'],
    [sys.executable, 'build_news_translate_cache.py', '--limit', '80'],
    [sys.executable, 'build_news_archive_report.py'],
    [sys.executable, 'safe_firebase_deploy.py'],
]


def run_once():
    print(f'[{datetime.now().isoformat(timespec="seconds")}] refresh cycle start', flush=True)
    for cmd in COMMANDS:
        print('$ ' + ' '.join(cmd), flush=True)
        subprocess.run(cmd, check=True)
    print(f'[{datetime.now().isoformat(timespec="seconds")}] refresh cycle done', flush=True)


def main():
    while True:
        try:
            run_once()
        except Exception as exc:
            print(f'refresh cycle failed: {exc}', flush=True)
        time.sleep(INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
