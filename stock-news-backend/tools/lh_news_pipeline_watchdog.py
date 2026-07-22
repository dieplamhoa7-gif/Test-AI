"""Self-healing watchdog for the LHINVT news publishing pipeline.

Runs frequently during market hours.  It only starts the refresh task when the
published news cache is stale, and records a small health report for operations.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, time, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "logs" / "news_pipeline_health.json"
TASK_NAME = "LHINVT Continuous News Refresh"
MAX_AGE_MINUTES = 35
ACTIVE_START, ACTIVE_END = time(7, 30), time(18, 35)


def now_local() -> datetime:
    return datetime.now().astimezone()


def in_window(now: datetime) -> bool:
    return now.weekday() < 5 and ACTIVE_START <= now.time() <= ACTIVE_END


def fetch_updated_at() -> datetime:
    url = "https://lhinvt.web.app/data/news_cache.json?watchdog=" + str(int(datetime.now().timestamp()))
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "LHINVT-news-watchdog/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.load(response)
    if isinstance(data, dict):
        raw = data.get("updatedAt") or data.get("createdAt")
    else:
        # Some legacy cache builds publish a bare list. In that case the
        # HTTP Last-Modified header is the authoritative publication time.
        raw = response.headers.get("Last-Modified")
        if raw:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(raw)
    if not raw:
        raise RuntimeError("published news cache has no updatedAt or Last-Modified")
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def task_state() -> str:
    command = ["powershell", "-NoProfile", "-Command", f"(Get-ScheduledTask -TaskName '{TASK_NAME}').State"]
    return subprocess.check_output(command, text=True, encoding="utf-8", errors="replace", timeout=30).strip()


def start_task() -> None:
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-ScheduledTask -TaskName '{TASK_NAME}'"], check=True, timeout=30)


def save(report: dict) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    now = now_local()
    report = {"checkedAt": now.isoformat(), "windowActive": in_window(now), "status": "OK"}
    if not in_window(now):
        report["status"] = "OUTSIDE_WINDOW"
        save(report)
        return 0
    try:
        updated = fetch_updated_at()
        age_minutes = round((datetime.now(timezone.utc) - updated.astimezone(timezone.utc)).total_seconds() / 60, 1)
        state = task_state()
        report.update({"publishedUpdatedAt": updated.isoformat(), "ageMinutes": age_minutes, "taskState": state})
        if age_minutes > MAX_AGE_MINUTES and state.lower() != "running":
            start_task()
            report.update({"status": "RECOVERY_STARTED", "reason": f"published cache stale ({age_minutes} min)"})
        elif age_minutes > MAX_AGE_MINUTES:
            report.update({"status": "WARN_RUNNING_STALE", "reason": f"refresh task still running; cache age {age_minutes} min"})
    except Exception as exc:
        report.update({"status": "FAIL", "error": str(exc)})
    save(report)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] not in {"FAIL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
