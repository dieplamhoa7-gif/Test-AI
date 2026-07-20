# -*- coding: utf-8 -*-
"""Deploy an toàn cho LHInvestment (tái dựng 08/07/2026).

Chống deploy đè DATA CŨ lên web live:
1. Mặc định: tải data live về local TRỪ KHI local mới hơn (so app_version).
2. --no-sync: bỏ qua bước sync (dùng khi local chắc chắn mới nhất).
3. firebase deploy --only hosting, verify lại sau deploy.

Dùng: python deploy_lh_safe.py [--no-sync] [--sync-only]
"""
from __future__ import annotations
import json
import subprocess
import sys
import urllib.request
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

LIVE = "https://lhinvt.web.app"
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "firebase_public" / "data"


def fetch(path: str, timeout: int = 40) -> bytes | None:
    url = f"{LIVE}{path}?ts={datetime.now().strftime('%H%M%S%f')}"
    try:
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
        if body.lstrip()[:1] in (b"<",):
            return None
        return body
    except Exception:
        return None


def list_local_data_files() -> list[str]:
    return ["/data/" + p.relative_to(DATA_DIR).as_posix() for p in DATA_DIR.rglob("*.json")]


def list_live_chart_files() -> list[str]:
    body = fetch("/data/charts/index.json")
    if not body:
        return []
    try:
        idx = json.loads(body)
    except Exception:
        return []
    items = idx.get("items") or idx.get("symbols") or []
    out = ["/data/charts/index.json"]
    for it in items:
        sym = it.get("symbol") if isinstance(it, dict) else it
        if sym:
            out.append(f"/data/charts/{sym}.json")
    return out


def _version(body: bytes | None) -> str:
    try:
        return json.loads(body).get("warrants", "") if body else ""
    except Exception:
        return ""


def sync_from_live() -> None:
    live_v = _version(fetch("/data/app_version.json"))
    local_p = DATA_DIR / "app_version.json"
    local_v = _version(local_p.read_bytes()) if local_p.exists() else ""
    if local_v and live_v and local_v >= live_v:
        print(f"Local ({local_v}) >= live ({live_v}) — KHÔNG kéo data cũ từ live về.")
        return
    paths = sorted(set(list_local_data_files() + list_live_chart_files()))
    print(f"Sync {len(paths)} data file(s) từ live về local...")
    updated = 0

    def one(path: str):
        nonlocal updated
        body = fetch(path)
        if body is None:
            return
        dest = DATA_DIR / path[len("/data/"):]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_bytes() != body:
            dest.write_bytes(body)
            updated += 1

    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(one, paths))
    print(f"  -> cập nhật {updated} file.")


def verify_final_payload() -> None:
    verifier = ROOT / "verify_lh_final_version_lock.py"
    if not verifier.exists():
        sys.exit("Thiếu verify_lh_final_version_lock.py — dừng deploy để tránh đẩy nhầm schema.")
    spec = importlib.util.spec_from_file_location("verify_lh_final_version_lock", verifier)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    errors, info = mod.check_local()
    if errors:
        print(json.dumps({"ok": False, "errors": errors, "info": info}, ensure_ascii=False, indent=2))
        sys.exit("LH final version lock FAILED — không deploy.")
    print("LH final version lock OK:", json.dumps(info, ensure_ascii=False))


def deploy() -> None:
    verify_final_payload()
    frontend = ROOT / "verify_lh_final_frontend_markers.py"
    if frontend.exists():
        subprocess.run([sys.executable, str(frontend)], cwd=str(ROOT), check=True)
    print("Chạy firebase deploy đúng target lhinvt ...")
    cmd = ["firebase", "deploy", "--only", "hosting:lhinvt", "--project", "security-1c731", "--config", "firebase.lhinvt.deploy.json"]
    r = subprocess.run(cmd, cwd=str(ROOT), shell=(sys.platform == "win32"))
    if r.returncode != 0:
        sys.exit(f"Deploy thất bại (exit {r.returncode}).")


def main() -> None:
    if not DATA_DIR.exists():
        sys.exit(f"Không thấy {DATA_DIR}")
    if "--no-sync" not in sys.argv:
        sync_from_live()
    if "--sync-only" in sys.argv:
        print("Chỉ sync, không deploy (--sync-only).")
        return
    deploy()
    print("Live app_version sau deploy:", _version(fetch("/data/app_version.json")))
    print("Hoàn tất.")


if __name__ == "__main__":
    main()
