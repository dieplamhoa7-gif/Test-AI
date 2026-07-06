from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PUBLIC_DATA = ROOT / 'firebase_public' / 'data'
OVERRIDES = DATA / 'live_overrides'

HTML_FILES = [
    'firebase_public/index.html',
    'firebase_public/stocks.html',
    'firebase_public/news-page.html',
    'firebase_public/warrants.html',
    'firebase_public/cw.html',
]

LH4_FILES = [
    'strategy_matrix_cache.json',
    'strategy_results_cache.json',
]


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def restore_html_from_head() -> None:
    # The live frontend is curated/reviewed. Output jobs may update JSON data,
    # but must never rewrite HTML/JS back to an older generated template.
    existing = [p for p in HTML_FILES if (ROOT / p).exists()]
    if existing:
        run(['git', 'checkout', '--', *[f'stock-news-backend/{p}' for p in existing]], ROOT.parent)


def restore_lh4_strategy_payload() -> None:
    # LH4 is the live strategy contract. If generic strategy builders run, put
    # the reviewed LH4-compatible payload back before commit/deploy.
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    for name in LH4_FILES:
        src = OVERRIDES / name
        if not src.exists():
            raise FileNotFoundError(f'Missing canonical LH4 override payload: {src}')
        shutil.copy2(src, DATA / name)
        shutil.copy2(src, PUBLIC_DATA / name)


def main() -> None:
    restore_html_from_head()
    restore_lh4_strategy_payload()
    print('LH live output guard applied: HTML restored from HEAD; LH4 strategy payload preserved.')


if __name__ == '__main__':
    main()
