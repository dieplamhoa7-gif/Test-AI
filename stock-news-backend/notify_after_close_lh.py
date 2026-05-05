from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DEFAULT_CHAT_ID = "5780893485"


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def tg_send(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("LH_AFTER_CLOSE_TELEGRAM_CHAT_ID", DEFAULT_CHAT_ID).strip()
    if not token or not chat_id:
        print(json.dumps({"sent": False, "reason": "missing TELEGRAM_BOT_TOKEN or chat_id"}, ensure_ascii=False), flush=True)
        return False
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data=payload, timeout=25) as r:
            ok = 200 <= r.status < 300
            print(json.dumps({"sent": ok, "status": r.status}, ensure_ascii=False), flush=True)
            return ok
    except Exception as exc:
        print(json.dumps({"sent": False, "error": repr(exc)}, ensure_ascii=False), flush=True)
        return False


def fmt_symbols(items: list[Any], limit: int = 12) -> str:
    syms: list[str] = []
    for item in items or []:
        if isinstance(item, str):
            sym = item
        elif isinstance(item, dict):
            sym = str(item.get("symbol") or item.get("ticker") or "")
        else:
            sym = ""
        sym = sym.strip().upper()
        if sym and sym not in syms:
            syms.append(sym)
    if not syms:
        return "-"
    more = len(syms) - limit
    out = ", ".join(syms[:limit])
    return out + (f" +{more}" if more > 0 else "")


def strategy_line(st: dict[str, Any]) -> str:
    sid = str(st.get("id") or st.get("name") or "strategy")
    label = {
        "b4_trend_pullback": "Trend Pullback",
        "shakeout_breakdown_rebound": "Shakeout",
        "clean_split_a_bottom": "Support Rebound",
    }.get(sid, sid)
    buy = st.get("buy") or []
    watch = st.get("watchlist") or st.get("watch") or []
    rejects = st.get("rejects") or st.get("rejectTop") or []
    reject_count = st.get("rejectCount", len(rejects) if isinstance(rejects, list) else 0)
    return f"- {label}: BUY {len(buy)} | WATCH {len(watch)} ({fmt_symbols(watch)}) | REJECT {reject_count}"


def summarize_log(log_path: Path) -> str:
    if not log_path.exists():
        return "Không thấy log sau phiên."
    text = log_path.read_text(encoding="utf-8", errors="replace")[-12000:]
    if "DONE after-close output-only pipeline" in text:
        return "Pipeline hoàn tất."
    m = re.findall(r"Command failed[^\n]+", text)
    if m:
        return "Pipeline lỗi: " + m[-1][:220]
    return "Pipeline đã chạy nhưng chưa thấy dòng DONE trong log."


def build_message(status: str = "success") -> str:
    rs = load_json(DATA / "rs_levels_vn100_cache.json", {})
    strat = load_json(DATA / "strategy_results_cache.json", {})
    market = load_json(DATA / "market_overview.json", {})
    strategies = strat.get("strategies") or []
    rs_count = rs.get("count") or len(rs.get("items") or [])
    rs_errors = rs.get("errorCount") or len(rs.get("errors") or [])
    updated = strat.get("createdAt") or strat.get("updatedAt") or datetime.now().isoformat(timespec="seconds")
    market_updated = market.get("updatedAt") or market.get("priceUpdatedAt") or "-"
    lines = [
        "LHInvestment sau phiên",
        "",
        f"Trạng thái: {'HOÀN TẤT' if status == 'success' else 'CÓ LỖI'}",
        f"R/S VN100: {rs_count} mã, errors {rs_errors}",
        f"Strategy updated: {updated}",
        f"Market overview: {market_updated}",
        "",
        "3 chiến lược:",
    ]
    if strategies:
        lines.extend(strategy_line(st) for st in strategies)
    else:
        lines.append("- Chưa có strategy cache.")
    lines.extend([
        "",
        "Link: https://lhinvestment.web.app/stocks?v=" + datetime.now().strftime("%H%M"),
        "",
        "Anh xem thông báo này rồi order em bước tiếp theo. Em không cần theo dõi tiếp.",
    ])
    return "\n".join(lines)


def main() -> None:
    status = (os.getenv("LH_AFTER_CLOSE_STATUS") or "success").strip().lower()
    if status not in {"success", "error"}:
        status = "success"
    msg = build_message(status)
    tg_send(msg)


if __name__ == "__main__":
    main()
