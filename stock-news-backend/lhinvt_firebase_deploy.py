from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / "lhinvt_firebase_deploy.log"
ACCOUNT = os.environ.get("LHINVT_FIREBASE_ACCOUNT", "lamhoabb1@gmail.com")
PROJECT = os.environ.get("LHINVT_FIREBASE_PROJECT", "security-1c731")
SITE = os.environ.get("LHINVT_FIREBASE_SITE", "lhinvt")
CONFIG = os.environ.get("LHINVT_FIREBASE_CONFIG", "firebase.lhinvt.deploy.json")


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list[str], timeout: int = 120, check: bool = True) -> subprocess.CompletedProcess[str]:
    log("RUN " + " ".join(cmd))
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if p.stdout:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(p.stdout)
        sys.stdout.buffer.write(p.stdout.encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    if check and p.returncode:
        raise SystemExit(f"Command failed {p.returncode}: {' '.join(cmd)}")
    return p


def main() -> None:
    firebase = shutil.which("firebase") or shutil.which("firebase.cmd") or "firebase.cmd"
    log(f"START LHINVT Firebase deploy account={ACCOUNT} project={PROJECT} site={SITE}")

    # Permanent freshness guard for Model3/web data:
    # every deploy must republish canonical data/market_data.json to firebase_public
    # and rebuild the SQLite DB used by Model3. If this fails, do not deploy a stale site.
    run([sys.executable, "sync_model3_public_data.py"], timeout=300, check=True)
    # Permanent no-rollback guards: every deploy path must preserve the
    # final 28.07.2026 canonical firebase_public payload; no old backup fallback.
    run([sys.executable, "verify_lh_final_version_lock.py"], timeout=60, check=True)
    run([sys.executable, "verify_lh_final_frontend_markers.py"], timeout=60, check=True)

    login = run([firebase, "login:list"], timeout=60, check=False)
    if ACCOUNT not in (login.stdout or ""):
        raise SystemExit(
            f"Firebase account {ACCOUNT} is not logged in on this machine. "
            f"Run `firebase login:add {ACCOUNT}` interactively once, then rerun."
        )

    projects = run([firebase, "projects:list", "--account", ACCOUNT], timeout=120, check=False)
    if projects.returncode or PROJECT not in (projects.stdout or ""):
        raise SystemExit(
            f"Firebase account {ACCOUNT} cannot access project {PROJECT}. "
            f"Token may be expired or account lacks permission. Re-auth with `firebase login:add {ACCOUNT}`."
        )

    sites = run([firebase, "hosting:sites:list", "--project", PROJECT, "--account", ACCOUNT], timeout=120, check=False)
    if sites.returncode or SITE not in (sites.stdout or ""):
        raise SystemExit(
            f"Firebase project {PROJECT} does not show hosting site {SITE} for account {ACCOUNT}."
        )

    run(
        [
            firebase,
            "deploy",
            "--account",
            ACCOUNT,
            "--project",
            PROJECT,
            "--config",
            CONFIG,
            "--only",
            f"hosting:{SITE}",
        ],
        timeout=900,
        check=True,
    )
    log("DONE LHINVT Firebase deploy")


if __name__ == "__main__":
    main()

