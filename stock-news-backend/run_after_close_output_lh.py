from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / "after_close_output_lh.log"


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list[str], *, timeout: int | None = None) -> None:
    log("RUN " + " ".join(cmd))
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    p = subprocess.run(cmd, cwd=ROOT, env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if p.stdout:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(p.stdout)
        print(p.stdout, end="", flush=True)
    if p.returncode != 0:
        raise SystemExit(f"Command failed {p.returncode}: {' '.join(cmd)}")


def main() -> None:
    py = sys.executable
    today = datetime.now()
    # Daily after-close keeps runtime controlled: R/S + indicators + 3 strategies on VN100 only.
    # Full HSX R/S is heavier; run only when LH_WEEKLY_HSX=1, normally via a separate weekly/manual job.
    weekly_hsx = today.weekday() == 0 and os.environ.get('LH_WEEKLY_HSX') == '1'  # Monday only when explicitly enabled
    log("START after-close output-only pipeline")
    log(f"Mode: daily VN100 strategies; weekly_hsx={weekly_hsx}")
    steps = []
    if weekly_hsx:
        steps.append([py, "run_rs_levels_hsx_all_safe.py"])
    else:
        log("Skip run_rs_levels_hsx_all_safe.py (weekly Monday only)")
    steps.extend([
        [py, "run_rs_levels_vn100_safe.py"],
        [py, "build_v3_full_indicator_cache_v2.py"],
        [py, "scan_v3_b4_bullish_divergence_current_signals.py"],
        [py, "scan_v3_clean_split_a2_b2_current_signals.py"],
        [py, "scan_shakeout_current_cache.py"],
        [py, "tmp_build_strategy_results_from_canonical.py"],
        [py, "refresh_market_prices_lh.py"],
        [py, "build_firebase_cache_site.py"],
    ])
    for step in steps:
        run(step)

    git_root = ROOT.parent
    add_cmd = ["git", "add", "-f",
         "stock-news-backend/data/rs_levels_hsx_all_cache.json",
         "stock-news-backend/data/rs_levels_vn100_cache.json",
         "stock-news-backend/data/rs_levels_only_cache.json",
         "stock-news-backend/data/v3_full_indicator_cache_v2.json",
         "stock-news-backend/data/v3_b4_bullish_divergence_current_signals.json",
         "stock-news-backend/data/v3_clean_split_a2_b2_current_signals.json",
         "stock-news-backend/data/shakeout_rebound_current_signals.json",
         "stock-news-backend/data/strategy_results_cache.json",
         "stock-news-backend/data/market_data.json",
         "stock-news-backend/data/market_overview.json",
         "stock-news-backend/firebase_public/data/market_data.json",
         "stock-news-backend/firebase_public/data/market_watch.json",
         "stock-news-backend/firebase_public/data/market_overview.json",
         "stock-news-backend/firebase_public/data/strategy_results_cache.json",
         "stock-news-backend/firebase_public/data/strategy_matrix_cache.json",
         "stock-news-backend/firebase_public/data/market_symbols.json",
         "stock-news-backend/firebase_public/stocks.html",
         "stock-news-backend/firebase_public/news-page.html",
         "stock-news-backend/firebase_public/warrants.html",
         "stock-news-backend/firebase_public/index.html"]
    log("RUN " + " ".join(add_cmd))
    subprocess.run(add_cmd, cwd=git_root, check=True)
    # Commit only when there is staged output difference.
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=git_root)
    if diff.returncode != 0:
        log("RUN git commit -m Auto refresh LH after-close outputs")
        subprocess.run(["git", "commit", "-m", "Auto refresh LH after-close outputs"], cwd=git_root, check=True)
        log("RUN git push origin master")
        subprocess.run(["git", "push", "origin", "master"], cwd=git_root, check=True)
    else:
        log("No output changes to commit")

    run(["firebase", "deploy", "--only", "hosting", "--project", "lhinvestment"], timeout=600)
    log("DONE after-close output-only pipeline")


if __name__ == "__main__":
    main()
