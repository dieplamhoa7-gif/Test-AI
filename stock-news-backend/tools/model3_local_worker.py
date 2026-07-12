#!/usr/bin/env python
"""Local Model3 worker for LHINVT hybrid Render flow.

Render keeps the public API/job state. This worker runs on the local PC near the
9router/keypoint gateway, claims queued jobs, runs the real Model3 workflow, and
uploads DOCX/status back to Render. It is designed to be launched by a Windows
Scheduled Task/watchdog, so it exits cleanly on errors and can be restarted.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_RENDER_BASE = "https://lh-realestate-browser-backend.onrender.com"
DEFAULT_OUT_DIR = ROOT / "outputs" / "model3"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def log(msg: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def request_json(method: str, url: str, token: str, **kwargs: Any) -> dict[str, Any]:
    headers = kwargs.pop("headers", {}) or {}
    headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, url, headers=headers, timeout=kwargs.pop("timeout", 60), **kwargs)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} {url}: {r.text[:1000]}")
    return r.json()


def post_status(base: str, token: str, job_id: str, **payload: Any) -> None:
    try:
        request_json("POST", f"{base}/pipeline/model3/worker/{job_id}/status", token, json=payload, timeout=30)
    except Exception as exc:  # noqa: BLE001
        log(f"WARN status update failed: {exc}")


def latest_docx(ticker: str, before: set[Path], out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [p for p in out_dir.glob("*.docx") if p not in before and ticker.upper() in p.name.upper()]
    if not files:
        files = [p for p in out_dir.glob(f"*{ticker.upper()}*.docx")]
    return max(files, key=lambda p: p.stat().st_mtime, default=None)


def detect_partial(logs: list[str], state: dict[str, Any]) -> bool:
    text = "\n".join(logs)
    feed = state.get("feed", []) if isinstance(state, dict) else []
    for item in feed:
        if isinstance(item, dict):
            text += "\n" + str(item.get("content", ""))
    low = text.lower()
    markers = [
        "http 502", "502 bad gateway", "provider lỗi/timeout", "provider loi/timeout",
        "fallback nội bộ", "fallback noi bo", "provider codex bị timeout", "provider kiro bị timeout",
        "grok_news_failed", "ai_provider_failed", "mock",
    ]
    if env("MODEL3_ALLOW_NEWS_FALLBACK_CLEAN", "").lower() not in {"1", "true", "yes"}:
        markers += ["public-web news fallback", "grok_provider_unavailable"]
    return any(m in low for m in markers)


def run_job(base: str, token: str, job: dict[str, Any], out_dir: Path) -> None:
    job_id = str(job["job_id"])
    ticker = re.sub(r"[^A-Z0-9]", "", str(job.get("ticker", "")).upper())[:8]
    if not ticker:
        raise RuntimeError("missing ticker")

    logs: list[str] = []
    before = set(out_dir.glob("*.docx")) if out_dir.exists() else set()

    def progress(msg: str) -> None:
        s = str(msg)[-1000:]
        logs.append(s)
        log(f"{job_id} {s}")
        post_status(base, token, job_id, status="running_external", log=s)

    post_status(base, token, job_id, status="running_external", progress=5, log=f"Local worker bắt đầu chạy Model3 {ticker}")

    from app.pipeline_api import _market_data_freshness_gate  # type: ignore
    from hybrid_agent_framework import run_model3_workflow  # type: ignore

    _market_data_freshness_gate(ticker, progress)
    task = (
        f"model3 {ticker} full web export: Codex TA research, Kiro News, UTF-8 cleaner trước, "
        "không Gemini, 3-5 tin trực tiếp 2026, PTKT LHInvestment, full technical fundamental strategy risk, "
        "xuất DOCX hoàn chỉnh cho NotebookLM"
    )
    state = run_model3_workflow(task, progress)
    docx = latest_docx(ticker, before, out_dir)
    if not docx or not docx.exists():
        raise RuntimeError(f"Không tìm thấy DOCX sau khi chạy Model3 cho {ticker}")

    partial = detect_partial(logs, state if isinstance(state, dict) else {})
    post_status(base, token, job_id, status="uploading_external", progress=95, log=f"Uploading DOCX {docx.name}; partial_quality={partial}")
    with docx.open("rb") as f:
        files = {"file": (docx.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"partial_quality": "true" if partial else "false"}
        r = requests.post(f"{base}/pipeline/model3/worker/{job_id}/upload", headers={"Authorization": f"Bearer {token}"}, files=files, data=data, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"upload failed HTTP {r.status_code}: {r.text[:1000]}")
    log(f"{job_id} uploaded {docx.name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=env("MODEL3_RENDER_BASE", DEFAULT_RENDER_BASE).rstrip("/"))
    ap.add_argument("--token", default=env("MODEL3_WORKER_TOKEN"))
    ap.add_argument("--out-dir", default=env("PIPELINE_MODEL3_OUT_DIR", str(DEFAULT_OUT_DIR)))
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--sleep", type=int, default=int(env("MODEL3_WORKER_SLEEP", "20") or "20"))
    args = ap.parse_args()
    if not args.token:
        raise SystemExit("Missing MODEL3_WORKER_TOKEN env/arg")
    out_dir = Path(args.out_dir)

    while True:
        try:
            nxt = request_json("GET", f"{args.base}/pipeline/model3/worker/next", args.token, timeout=45)
            job = nxt if nxt.get("job_id") else nxt.get("job")
            if job and job.get("job_id"):
                run_job(args.base, args.token, job, out_dir)
            elif args.once:
                return 0
            else:
                time.sleep(args.sleep)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR {type(exc).__name__}: {exc}")
            # If a job was already claimed, status update is handled inside run_job where possible.
            if args.once:
                return 2
            time.sleep(max(args.sleep, 30))


if __name__ == "__main__":
    raise SystemExit(main())
