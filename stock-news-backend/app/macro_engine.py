from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class MacroInput:
    vnindex_change_pct: float = 0.0
    breadth_pct: float | None = None
    usd_vnd_change_pct: float | None = None
    rate_trend: str | None = None  # easing / neutral / tightening
    inflation_yoy: float | None = None
    credit_growth_ytd: float | None = None
    pmi: float | None = None
    global_risk: str | None = None  # risk_on / neutral / risk_off


def _num(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def macro_score(inp: MacroInput) -> dict[str, Any]:
    """Return a transparent 0-100 macro regime score.

    This is a decision overlay, not a standalone buy/sell signal.
    Higher score means the macro/market environment allows larger risk budget.
    """
    components: dict[str, float] = {}

    # Market momentum proxy, available daily from current market overview.
    chg = _num(inp.vnindex_change_pct)
    components["marketMomentum"] = _clamp(50 + chg * 18)

    # Breadth: optional % advancing symbols. Neutral if missing.
    breadth = inp.breadth_pct
    components["breadth"] = _clamp(_num(breadth, 50.0)) if breadth is not None else 50.0

    # FX pressure: weaker VND is usually risk-off for local equities.
    fx = inp.usd_vnd_change_pct
    components["fx"] = _clamp(55 - _num(fx, 0.0) * 20) if fx is not None else 50.0

    rate = (inp.rate_trend or "neutral").lower()
    components["rates"] = 70.0 if rate == "easing" else 35.0 if rate == "tightening" else 50.0

    # Vietnam inflation comfort zone: too high hurts rates/valuation, too low can imply weak demand.
    if inp.inflation_yoy is None:
        components["inflation"] = 50.0
    else:
        cpi = _num(inp.inflation_yoy)
        components["inflation"] = 75.0 if 1.5 <= cpi <= 4.0 else 55.0 if 0.5 <= cpi < 1.5 or 4.0 < cpi <= 5.0 else 30.0

    if inp.credit_growth_ytd is None:
        components["credit"] = 50.0
    else:
        credit = _num(inp.credit_growth_ytd)
        components["credit"] = 70.0 if credit >= 8 else 58.0 if credit >= 4 else 40.0

    if inp.pmi is None:
        components["pmi"] = 50.0
    else:
        pmi = _num(inp.pmi)
        components["pmi"] = _clamp(50 + (pmi - 50) * 4)

    gr = (inp.global_risk or "neutral").lower()
    components["globalRisk"] = 70.0 if gr == "risk_on" else 35.0 if gr == "risk_off" else 50.0

    weights = {
        "marketMomentum": 0.22,
        "breadth": 0.14,
        "fx": 0.10,
        "rates": 0.14,
        "inflation": 0.12,
        "credit": 0.10,
        "pmi": 0.08,
        "globalRisk": 0.10,
    }
    score = round(sum(components[k] * weights[k] for k in weights), 2)
    if score >= 68:
        regime = "risk_on"
        label = "Thuận lợi"
        allocation = "Có thể nâng tỷ trọng, ưu tiên cổ phiếu khỏe hơn VNIndex."
    elif score >= 45:
        regime = "neutral"
        label = "Trung tính"
        allocation = "Giữ tỷ trọng vừa phải, mua từng phần tại hỗ trợ/xác nhận."
    else:
        regime = "risk_off"
        label = "Phòng thủ"
        allocation = "Giảm tỷ trọng, ưu tiên tiền mặt và chỉ mua tín hiệu rất rõ."
    return {
        "score": score,
        "regime": regime,
        "label": label,
        "allocationHint": allocation,
        "components": {k: round(v, 2) for k, v in components.items()},
        "weights": weights,
        "note": "Macro score là lớp lọc môi trường; quyết định cuối vẫn cần kết hợp PTKT, R/S, định giá và quản trị rủi ro.",
    }


def stock_macro_decision(base_signal_score: float | None, macro: dict[str, Any]) -> dict[str, Any]:
    base = _num(base_signal_score, 50.0)
    ms = _num(macro.get("score"), 50.0)
    combined = round(base * 0.72 + ms * 0.28, 2)
    regime = macro.get("regime") or "neutral"
    if regime == "risk_off" and combined >= 70:
        action = "Theo dõi/mua nhỏ"
        reason = "Tín hiệu mã tốt nhưng vĩ mô đang phòng thủ, không nên giải ngân mạnh."
    elif combined >= 72 and regime != "risk_off":
        action = "Có thể mua từng phần"
        reason = "Tín hiệu kỹ thuật tốt và môi trường vĩ mô không cản trở."
    elif combined >= 55:
        action = "Theo dõi chờ xác nhận"
        reason = "Điểm tổng hợp trung bình, ưu tiên điểm mua an toàn gần hỗ trợ."
    else:
        action = "Chưa mua"
        reason = "Điểm tổng hợp thấp hoặc môi trường chưa thuận lợi."
    return {"combinedScore": combined, "action": action, "reason": reason}


def build_macro_payload(market_overview: dict[str, Any] | None = None, manual: dict[str, Any] | None = None) -> dict[str, Any]:
    manual = manual or {}
    items = (market_overview or {}).get("items") or []
    vn = next((x for x in items if str(x.get("symbol") or x.get("label") or "").upper() in {"VNINDEX", "VN-INDEX"}), None)
    inp = MacroInput(
        vnindex_change_pct=_num((vn or {}).get("changePct"), 0.0),
        breadth_pct=manual.get("breadthPct"),
        usd_vnd_change_pct=manual.get("usdVndChangePct"),
        rate_trend=manual.get("rateTrend"),
        inflation_yoy=manual.get("inflationYoy"),
        credit_growth_ytd=manual.get("creditGrowthYtd"),
        pmi=manual.get("pmi"),
        global_risk=manual.get("globalRisk"),
    )
    result = macro_score(inp)
    return {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": "macro_engine_v1_static_cache",
        "input": asdict(inp),
        **result,
    }
