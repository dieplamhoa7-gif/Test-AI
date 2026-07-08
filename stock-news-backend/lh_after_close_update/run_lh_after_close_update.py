from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], timeout: int | None = None) -> None:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    print("RUN", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True, timeout=timeout)


def main() -> None:
    py = sys.executable
    run([py, "run_after_close_output_lh.py"], timeout=3600)
    run([py, "verify_lh_final_frontend_markers.py"], timeout=120)
    run([py, "lh_after_close_update/verify_no_old_version_regression.py"], timeout=120)


if __name__ == "__main__":
    main()
