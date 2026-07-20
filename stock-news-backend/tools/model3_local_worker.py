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
import shutil
import sqlite3
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
    safe = str(msg).encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    try:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), safe, flush=True)
    except UnicodeEncodeError:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), safe.encode("ascii", errors="replace").decode("ascii"), flush=True)


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


def sync_canonical_data(ticker: str, progress) -> None:
    """Ensure the runtime worker clone uses the canonical fresh LHINVT data.

    The Render/local-worker setup runs from render_backend_work, while the daily
    data pipeline writes canonical files in workspace/stock-news-backend.  If we
    do not sync here, web exports can silently fall back to stale cache files.
    """
    canonical = Path(env("MODEL3_CANONICAL_ROOT", r"C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend"))
    if not canonical.exists():
        raise RuntimeError(f"MODEL3 canonical root missing: {canonical}")
    pairs = [
        (canonical / "data" / "lhinvt_stock_chart.db", ROOT / "data" / "lhinvt_stock_chart.db"),
        (canonical / "data" / "market_data.json", ROOT / "data" / "market_data.json"),
        (canonical / "data" / "v3_full_indicator_cache_v2.json", ROOT / "data" / "v3_full_indicator_cache_v2.json"),
        (canonical / "data" / "lh_canonical_indicators_daily.json", ROOT / "data" / "lh_canonical_indicators_daily.json"),
        (canonical / "data" / "strategy_results_cache.json", ROOT / "data" / "strategy_results_cache.json"),
    ]
    for src, dst in pairs:
        if not src.exists():
            raise RuntimeError(f"canonical data missing: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        if (not dst.exists()) or src.stat().st_mtime > dst.stat().st_mtime or src.stat().st_size != dst.stat().st_size:
            shutil.copy2(src, dst)
            progress(f"Synced canonical data: {src.name}")

    db = ROOT / "data" / "lhinvt_stock_chart.db"
    con = sqlite3.connect(db)
    try:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "select latest_date, latest_close, latest_volume, updated_at from symbols where symbol=?",
            (ticker.upper(),),
        ).fetchone()
    finally:
        con.close()
    if not row:
        raise RuntimeError(f"fresh DB has no symbol row for {ticker}")
    latest_date = str(row["latest_date"] or "")
    updated_at = str(row["updated_at"] or "")
    # Hard guard against the known restored/stale cache path.
    if latest_date < "2026-07-17":
        raise RuntimeError(f"stale Model3 DB for {ticker}: latest_date={latest_date}, updated_at={updated_at}")
    progress(
        f"Canonical DB OK: {ticker} close={row['latest_close']}, volume={row['latest_volume']}, "
        f"date={latest_date}, updated_at={updated_at}"
    )


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

    sync_canonical_data(ticker, progress)

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
    uploaded_job = r.json()
    log(f"{job_id} uploaded {docx.name}")

    wants_notebook = any(
        str(s.get("key")) == "notebooklm" and str(s.get("status")) != "skipped"
        for s in (job.get("sections") or [])
        if isinstance(s, dict)
    )
    if wants_notebook:
        try:
            progress("NotebookLM: đang tạo notebook/slides từ DOCX...")
            from model3_notebooklm import create_presentation_from_docx  # type: ignore

            nb = create_presentation_from_docx(str(docx), title=f"{ticker} Model3 NotebookLM Web Export")
            result = dict((uploaded_job.get("result") or {}) if isinstance(uploaded_job, dict) else {})
            result["notebooklm"] = nb
            if isinstance(nb, dict):
                pdf = nb.get("slide_pdf")
                notebook_id = nb.get("notebook_id")
                if pdf:
                    pdf_path = Path(str(pdf))
                    if pdf_path.exists():
                        try:
                            with pdf_path.open("rb") as pf:
                                files = {"file": (pdf_path.name, pf, "application/pdf")}
                                data = {"artifact_kind": "notebooklm_pdf"}
                                rr = requests.post(f"{base}/pipeline/model3/worker/{job_id}/upload", headers={"Authorization": f"Bearer {token}"}, files=files, data=data, timeout=180)
                            if rr.status_code < 400:
                                # Render's older upload endpoint stores the file even if it treats every
                                # upload as a DOCX. Preserve the original Word result and expose this
                                # second file explicitly as fallback/NotebookLM PDF.
                                result["notebooklm_pdf_name"] = pdf_path.name
                                result["notebooklm_pdf_url"] = f"/pipeline/model3/file/{pdf_path.name}"
                            else:
                                result["notebooklm_pdf_upload_error"] = rr.text[:500]
                        except Exception as exc:
                            result["notebooklm_pdf_upload_error"] = str(exc)[-500:]
                    result.setdefault("notebooklm_pdf_url", f"/pipeline/model3/file/{pdf_path.name}")
                if notebook_id:
                    result["notebooklm_url"] = f"https://notebooklm.google.com/notebook/{notebook_id}"
            sections = uploaded_job.get("sections") or job.get("sections") or []
            agents = uploaded_job.get("agents") or job.get("agents") or {}
            for sec in sections:
                if isinstance(sec, dict) and sec.get("key") == "notebooklm":
                    sec["status"] = "done"
            if isinstance(agents, dict):
                agents["NotebookLM"] = "done"
            post_status(base, token, job_id, status="done", progress=100, result=result, sections=sections, agents=agents, log="NotebookLM export xong")
            log(f"{job_id} NotebookLM export done")
        except Exception as exc:  # noqa: BLE001
            err = str(exc)[-1500:]
            result = dict((uploaded_job.get("result") or {}) if isinstance(uploaded_job, dict) else {})
            sections = uploaded_job.get("sections") or job.get("sections") or []
            agents = uploaded_job.get("agents") or job.get("agents") or {}
            fallback_ok = False
            try:
                progress("NotebookLM loi/quota; dang tao bao cao fallback tu DOCX...")
                from model3_fallback_report import create_fallback_report_from_docx  # type: ignore

                fb = create_fallback_report_from_docx(str(docx), title=f"{ticker} Model3 fallback report")
                result["notebooklm"] = {"ok": False, "fallback_used": True, "error": err}
                result["notebooklm_error"] = err
                result["fallback_report"] = fb
                pdf = fb.get("slide_pdf") or fb.get("pdf_path")
                if pdf:
                    pdf_path = Path(str(pdf))
                    if pdf_path.exists():
                        try:
                            with pdf_path.open("rb") as pf:
                                files = {"file": (pdf_path.name, pf, "application/pdf")}
                                data = {"artifact_kind": "notebooklm_pdf"}
                                rr = requests.post(f"{base}/pipeline/model3/worker/{job_id}/upload", headers={"Authorization": f"Bearer {token}"}, files=files, data=data, timeout=180)
                            if rr.status_code < 400:
                                result["notebooklm_pdf_name"] = pdf_path.name
                                result["notebooklm_pdf_url"] = f"/pipeline/model3/file/{pdf_path.name}"
                                result["fallback_pdf_url"] = result["notebooklm_pdf_url"]
                            else:
                                result["fallback_upload_error"] = rr.text[:500]
                        except Exception as up_exc:
                            result["fallback_upload_error"] = str(up_exc)[-500:]
                html_path = fb.get("html_path") if isinstance(fb, dict) else None
                if html_path:
                    result["fallback_html_path"] = str(html_path)
                fallback_ok = True
            except Exception as fb_exc:  # noqa: BLE001
                result["notebooklm"] = None
                result["notebooklm_error"] = err
                result["fallback_error"] = str(fb_exc)[-1000:]
            for sec in sections:
                if isinstance(sec, dict) and sec.get("key") == "notebooklm":
                    sec["status"] = "done" if fallback_ok else "error"
            if isinstance(agents, dict):
                agents["NotebookLM"] = "fallback" if fallback_ok else "error"
            msg = "NotebookLM loi/quota; da tao bao cao fallback" if fallback_ok else f"NotebookLM export lỗi: {err}"
            post_status(base, token, job_id, status="done", progress=100, result=result, sections=sections, agents=agents, log=msg)
            log(f"{job_id} NotebookLM export failed; fallback_ok={fallback_ok}: {err}")


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
