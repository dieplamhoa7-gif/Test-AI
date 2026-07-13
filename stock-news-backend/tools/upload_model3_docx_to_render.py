#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import requests

DEFAULT_BASE = "https://lh-realestate-browser-backend.onrender.com"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create/finish a Model3 Render job from an existing DOCX.")
    ap.add_argument("docx", help="Local DOCX path to upload")
    ap.add_argument("--ticker", default="", help="Ticker; inferred from filename if omitted")
    ap.add_argument("--base", default=os.getenv("MODEL3_RENDER_BASE", DEFAULT_BASE).rstrip("/"))
    ap.add_argument("--token", default=os.getenv("MODEL3_WORKER_TOKEN", ""))
    ap.add_argument("--partial", action="store_true")
    args = ap.parse_args()
    token = args.token.strip()
    if not token:
        raise SystemExit("Missing MODEL3_WORKER_TOKEN env or --token")
    docx = Path(args.docx)
    if not docx.exists():
        raise SystemExit(f"Missing DOCX: {docx}")
    ticker = re.sub(r"[^A-Z0-9]", "", (args.ticker or docx.name.split("-")[2] if len(docx.name.split("-")) > 2 else "").upper())[:8]
    if not ticker:
        raise SystemExit("Missing --ticker")

    # Create a queued external job through the public endpoint, then claim it via worker/next and upload.
    r = requests.post(f"{args.base}/pipeline/model3/export", json={"ticker": ticker, "notebooklm": False}, timeout=60)
    r.raise_for_status()
    job = r.json()
    job_id = job.get("job_id") or job.get("id")
    if not job_id:
        raise SystemExit(f"Could not get job_id from: {job}")
    headers = {"Authorization": f"Bearer {token}"}
    # Claim if server is in external-worker mode. Ignore if another worker status is returned.
    try:
        requests.get(f"{args.base}/pipeline/model3/worker/next", headers=headers, timeout=30)
    except Exception:
        pass
    with docx.open("rb") as f:
        files = {"file": (docx.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"partial_quality": "true" if args.partial else "false"}
        up = requests.post(f"{args.base}/pipeline/model3/worker/{job_id}/upload", headers=headers, files=files, data=data, timeout=180)
    if up.status_code >= 400:
        raise SystemExit(f"upload failed HTTP {up.status_code}: {up.text[:2000]}")
    print(up.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
