from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[1] / "data"


def _num(text: Any) -> float | None:
    if text is None:
        return None
    s = str(text).strip().replace("%", "").replace(",", "")
    try:
        return float(s)
    except Exception:
        return None


def _fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 LHInvestment macro local"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw.decode("utf-8", errors="ignore")


def pinetree_url(d: date | None = None) -> str:
    d = d or date.today()
    return f"https://pinetree.vn/post/{d:%Y%m%d}/ban-tin-sang-{d:%d-%m-%Y}/"


def strip_html(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


def find_metric(text: str, label: str) -> dict[str, Any]:
    # Pinetree pattern is label, value, then optional 1D/YTD lines. Some rows say "1D 1.62%", others "1D (bps) 246".
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    low = label.lower()
    for i, line in enumerate(lines):
        if line.lower() != low:
            continue
        value = _num(lines[i + 1]) if i + 1 < len(lines) else None
        change1d = None
        ytd = None
        for j in range(i + 2, min(i + 8, len(lines))):
            m1 = re.match(r"1D(?:\s*\((?:bps|%)\))?\s*([\d,\.\-]+)%?$", lines[j], re.I)
            my = re.match(r"YTD(?:\s*\((?:bps|%)\))?\s*([\d,\.\-]+)%?$", lines[j], re.I)
            if m1:
                change1d = _num(m1.group(1))
            if my:
                ytd = _num(my.group(1))
        return {"value": value, "change1d": change1d, "ytd": ytd}
    return {"value": None, "change1d": None, "ytd": None}


def parse_pinetree(text: str, url: str = "") -> dict[str, Any]:
    return {
        "source": "Pinetree Morning Brief",
        "url": url,
        "interbankOvernight": find_metric(text, "Lãi suất liên NH"),
        "deposit12m": find_metric(text, "Lãi suất tiết kiệm 12T"),
        "govBond5y": find_metric(text, "TPCP - 5 năm"),
        "govBond10y": find_metric(text, "TPCP - 10 năm"),
        "usdVnd": find_metric(text, "USD/VND"),
        "eurVnd": find_metric(text, "EUR/VND"),
        "cnyVnd": find_metric(text, "CNY/VND"),
        "sp500": find_metric(text, "S&P500"),
        "nasdaq": find_metric(text, "NASDAQ"),
        "vix": find_metric(text, "VIX"),
        "brent": find_metric(text, "Dầu Brent ($/thùng)"),
        "gold": find_metric(text, "Vàng ($/ounce)"),
        "vnindex": find_metric(text, "VN-INDEX"),
        "foreignNetBuyBn": find_metric(text, "GT mua ròng NĐTNN (tỷ)"),
        "marketTurnoverBn": find_metric(text, "Tổng GTGD (tỷ)"),
    }


def score_macro(m: dict[str, Any]) -> dict[str, Any]:
    components: dict[str, dict[str, Any]] = {}

    ib = m["interbankOvernight"]
    ib_rate = ib.get("value")
    ib_chg = ib.get("change1d")
    liquidity = 50
    notes = []
    if ib_rate is not None:
        if ib_rate >= 6: liquidity -= 18; notes.append("Lãi suất liên NH cao")
        elif ib_rate <= 3: liquidity += 12; notes.append("Lãi suất liên NH thấp")
    if ib_chg is not None:
        if ib_chg >= 100: liquidity -= 15; notes.append("Liên NH tăng sốc trong ngày")
        elif ib_chg <= -50: liquidity += 8; notes.append("Liên NH hạ nhiệt")
    components["liquidity"] = {"score": max(0, min(100, liquidity)), "notes": notes}

    fx = 50; notes=[]
    usd = m["usdVnd"]
    if usd.get("change1d") is not None:
        if usd["change1d"] >= 0.3: fx -= 18; notes.append("USD/VND tăng mạnh")
        elif usd["change1d"] <= -0.2: fx += 8; notes.append("Tỷ giá hạ nhiệt")
    if usd.get("ytd") is not None:
        if usd["ytd"] >= 3: fx -= 12; notes.append("Áp lực tỷ giá YTD cao")
    components["fx"] = {"score": max(0, min(100, fx)), "notes": notes}

    rates = 50; notes=[]
    dep = m["deposit12m"].get("value")
    y10 = m["govBond10y"].get("value")
    if dep is not None:
        if dep >= 6: rates -= 12; notes.append("Lãi suất tiết kiệm cao")
        elif dep <= 5: rates += 8; notes.append("Lãi suất tiết kiệm thấp")
    if y10 is not None:
        if y10 >= 4.5: rates -= 10; notes.append("TPCP 10Y tăng/neo cao")
        elif y10 <= 3.5: rates += 8; notes.append("TPCP 10Y thấp")
    components["rates"] = {"score": max(0, min(100, rates)), "notes": notes}

    global_risk = 50; notes=[]
    sp1d = m["sp500"].get("change1d")
    vix = m["vix"].get("value")
    brent1d = m["brent"].get("change1d")
    if sp1d is not None:
        if sp1d >= 0.7: global_risk += 10; notes.append("Mỹ risk-on")
        elif sp1d <= -1: global_risk -= 12; notes.append("Mỹ risk-off")
    if vix is not None:
        if vix >= 25: global_risk -= 18; notes.append("VIX cao")
        elif vix <= 18: global_risk += 8; notes.append("VIX thấp")
    if brent1d is not None and brent1d >= 3:
        global_risk -= 8; notes.append("Dầu tăng gây áp lực CPI")
    components["globalRisk"] = {"score": max(0, min(100, global_risk)), "notes": notes}

    market_flow = 50; notes=[]
    foreign = m["foreignNetBuyBn"].get("value")
    vn1d = m["vnindex"].get("change1d")
    turnover = m["marketTurnoverBn"].get("value")
    if foreign is not None:
        if foreign <= -1000: market_flow -= 15; notes.append("Khối ngoại bán ròng mạnh")
        elif foreign >= 500: market_flow += 10; notes.append("Khối ngoại mua ròng")
    if vn1d is not None:
        if vn1d >= 0.7: market_flow += 8; notes.append("VNINDEX tăng tốt")
        elif vn1d <= -1: market_flow -= 10; notes.append("VNINDEX giảm mạnh")
    if turnover is not None and turnover >= 20000:
        market_flow += 4; notes.append("Thanh khoản thị trường cao")
    components["marketFlow"] = {"score": max(0, min(100, market_flow)), "notes": notes}

    weights = {"liquidity": .30, "fx": .20, "rates": .15, "globalRisk": .15, "marketFlow": .20}
    total = round(sum(components[k]["score"] * w for k, w in weights.items()), 2)
    if total >= 65:
        phase = "Mở rộng / Risk-on"
        view = "Ưu tiên cổ phiếu dẫn dắt, có thể tăng tỷ trọng theo tín hiệu PTKT."
    elif total >= 50:
        phase = "Trung tính - hồi phục chọn lọc"
        view = "Chọn lọc mã khỏe, mua từng phần ở hỗ trợ, tránh mua đuổi."
    elif total >= 40:
        phase = "Cuối chu kỳ / Phòng thủ"
        view = "Giảm tỷ trọng, ưu tiên tiền mặt, chỉ mua setup xác suất cao."
    else:
        phase = "Co hẹp / Risk-off"
        view = "Bảo toàn vốn, hạn chế giải ngân mới."
    return {"macroScore": total, "phase": phase, "marketView": view, "components": components, "weights": weights}


def build(date_str: str | None = None) -> dict[str, Any]:
    d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    url = pinetree_url(d)
    html = _fetch(url)
    text = strip_html(html)
    parsed = parse_pinetree(text, url)
    score = score_macro(parsed)
    payload = {"createdAt": datetime.now().isoformat(), "date": str(d), "status": "local-test", "data": parsed, **score}
    DATA.mkdir(exist_ok=True)
    (DATA / "macro_cycle_local.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    args = ap.parse_args()
    print(json.dumps(build(args.date), ensure_ascii=False, indent=2))
