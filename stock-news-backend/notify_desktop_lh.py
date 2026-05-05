from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime


def notify(title: str, message: str) -> None:
    # Best-effort Windows desktop notice. Works even without extra packages.
    # 1) Try msg.exe to current user/session.
    user = os.getenv("USERNAME") or os.getenv("USER") or "*"
    text = f"{title}\n\n{message}"
    try:
        subprocess.run(["msg", user, "/TIME:60", text], timeout=10, check=False)
        print("desktop notify via msg.exe", flush=True)
        return
    except Exception as exc:
        print("msg.exe notify failed", repr(exc), flush=True)

    # 2) Fallback: PowerShell popup. May only show in interactive session.
    ps = (
        "Add-Type -AssemblyName PresentationFramework;"
        f"[System.Windows.MessageBox]::Show({text!r}, {title!r}) | Out-Null"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], timeout=20, check=False)
        print("desktop notify via powershell messagebox", flush=True)
    except Exception as exc:
        print("powershell notify failed", repr(exc), flush=True)


def main() -> None:
    status = (os.getenv("LH_AFTER_CLOSE_STATUS") or "success").lower().strip()
    detail = os.getenv("LH_AFTER_CLOSE_DETAIL", "").strip()
    now = datetime.now().strftime("%H:%M %d/%m")
    if status == "success":
        title = "LHInvestment: chạy sau phiên xong"
        message = detail or f"R/S + 3 chiến lược + deploy đã hoàn tất lúc {now}. Anh xem web rồi order em bước tiếp."
    elif status == "error":
        title = "LHInvestment: pipeline bị lỗi"
        message = detail or f"Task sau phiên bị lỗi lúc {now}. Anh gọi em xử lý khi cần."
    elif status == "timeout":
        title = "LHInvestment: pipeline có thể bị đơ"
        message = detail or f"Task chạy quá lâu / timeout lúc {now}. Anh gọi em kiểm tra khi cần."
    else:
        title = "LHInvestment notice"
        message = detail or f"Trạng thái: {status} lúc {now}"
    notify(title, message)


if __name__ == "__main__":
    main()
