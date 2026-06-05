from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def main() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = LOG_DIR / f"daily_macro_update_{today}.log"
    status_path = ROOT / "data" / "daily_macro_update_status.json"
    status_path.parent.mkdir(exist_ok=True)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Avoid accidental headless block on TradingEconomics: daily_runner uses headed browser for TE deep/visible scrape when configured.

    cmd = [sys.executable, "macro/daily_runner.py", "--date", today, "--report"]
    started = datetime.now().isoformat()
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"Daily macro update started: {started}\n")
        log.write(f"Command: {' '.join(cmd)}\n\n")
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, text=True, stdout=log, stderr=subprocess.STDOUT)

    finished = datetime.now().isoformat()
    status = {
        "date": today,
        "startedAt": started,
        "finishedAt": finished,
        "returnCode": proc.returncode,
        "status": "ok" if proc.returncode == 0 else "error",
        "logPath": str(log_path),
        "historyCandidates": [str(p) for p in sorted((ROOT / "data" / "history").glob(f"{today}*.json"))],
        "tradingEconomicsLatest": str(ROOT / "data" / "tradingeconomics_visible_latest.json"),
        "tradingEconomicsDeep": str(ROOT / "data" / "tradingeconomics_deep_scrape_latest.json"),
        "unifiedMacroTimeline": str(ROOT / "data" / "unified_macro" / "macro_timeline_unified.csv"),
    }
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
