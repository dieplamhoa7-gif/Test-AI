from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic
from typing import Any

from app.market_data import get_market_symbol

V3_UNIVERSE = ["FPT", "MWG", "SSI", "VCI", "HCM", "MBB", "TCB", "VPB", "MSN", "LPB", "TPB", "VRE", "CTD", "VIX", "VCG", "VHC"]
SHAKEOUT_UNIVERSE = ["MSN", "FPT", "LPB", "TPB", "VPB", "VRE", "SSI", "LCG", "AAA", "APH", "BIC", "CTD", "FIT", "HHS", "HPX", "HT1", "MIG", "QCG", "SJS", "VCG", "VHC", "VIX", "GIL", "HDC", "EVF"]
CACHE_TTL_SECONDS = 30 * 60
_cache: tuple[float, dict[str, Any]] | None = None


def _f(v: Any) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _round(v: float, d: int = 2) -> float:
    return round(float(v), d)


def _v3_candidate(item: dict[str, Any]) -> dict[str, Any] | None:
    sym = str(item.get("ticker") or "").upper()
    price = _f(item.get("price"))
    tech = item.get("technical") or {}
    if not sym or price <= 0 or not tech:
        return None
    support = _f(tech.get("activeSupportDay") or tech.get("supportDay"))
    resistance = _f(tech.get("activeResistanceDay") or tech.get("resistanceDay"))
    ma20 = _f(tech.get("ma20")); ma50 = _f(tech.get("ma50"))
    rsi = _f(tech.get("rsi14")); hist = _f(tech.get("histogram")); vol = _f(tech.get("volumeRatio")); adx = _f(tech.get("adx14"))
    plus = _f(tech.get("plusDi")); minus = _f(tech.get("minusDi"))
    if support <= 0 or resistance <= price:
        return None
    near_support = abs(price - support) / price * 100
    risk = (price - support * 0.985) / price * 100
    target = price + max(price - support * 0.985, 0)  # 1R
    reward = (target - price) / price * 100
    trend_ok = (price >= ma20 > 0 and (ma50 <= 0 or ma20 >= ma50 * 0.97)) or plus >= minus
    momentum_ok = hist >= -0.5 and 30 <= rsi <= 62
    volume_ok = vol <= 1.6
    if not (near_support <= 3.5 and risk <= 6 and reward > 0 and trend_ok and momentum_ok and volume_ok):
        return None
    score = 60
    score += max(0, 18 - near_support * 4)
    score += 8 if hist >= 0 else 3
    score += 6 if plus >= minus else 0
    score += 5 if adx >= 15 else 0
    score += 4 if vol <= 1.1 else 0
    return {
        "symbol": sym,
        "strategy": "V3 Target 1R",
        "action": "Canh mua tại hỗ trợ",
        "price": _round(price),
        "entry": f"{_round(support,2)} - {_round(price,2)}",
        "stopLoss": _round(support * 0.985, 2),
        "target": _round(target, 2),
        "riskPct": _round(risk),
        "rewardPct": _round(reward),
        "rankScore": _round(score),
        "reason": f"Gần hỗ trợ {near_support:.1f}%, RSI {rsi:.1f}, MACD hist {hist:.2f}, volume {vol:.2f}",
    }


def _shakeout_candidate(item: dict[str, Any]) -> dict[str, Any] | None:
    sym = str(item.get("ticker") or "").upper()
    price = _f(item.get("price"))
    tech = item.get("technical") or {}
    support = _f(tech.get("activeSupportDay") or tech.get("supportDay"))
    if not sym or price <= 0 or support <= 0:
        return None
    break_pct = (support - price) / support * 100
    if break_pct < 2 or break_pct > 4:
        return None
    rsi = _f(tech.get("rsi14")); vol = _f(tech.get("volumeRatio")); hist = _f(tech.get("histogram"))
    if rsi < 20 or vol > 2.4:
        return None
    target = price * 1.06
    stop = price * 0.96
    score = 75 + (4 - abs(3 - break_pct) * 4) + (5 if 25 <= rsi <= 45 else 0) + (3 if vol <= 1.3 else 0)
    return {
        "symbol": sym,
        "strategy": "Mua rũ Target +6%",
        "action": "Mua phiên kế tiếp nếu không có tin xấu/breakdown thị trường",
        "price": _round(price),
        "entry": "Phiên kế tiếp",
        "stopLoss": _round(stop, 2),
        "target": _round(target, 2),
        "breakSupportPct": _round(break_pct),
        "rankScore": _round(score),
        "reason": f"Đóng cửa thủng support {break_pct:.1f}%, RSI {rsi:.1f}, volume {vol:.2f}, hist {hist:.2f}",
    }


def current_strategy_recommendations(max_symbols: int = 60, force_refresh: bool = False) -> dict[str, Any]:
    global _cache
    now = monotonic()
    if _cache and not force_refresh and now - _cache[0] < CACHE_TTL_SECONDS:
        payload = dict(_cache[1])
        payload["cached"] = True
        return payload
    symbols = list(dict.fromkeys((V3_UNIVERSE + SHAKEOUT_UNIVERSE)[:max_symbols]))
    v3: list[dict[str, Any]] = []
    shakeout: list[dict[str, Any]] = []
    errors: list[str] = []
    for sym in symbols:
        try:
            item = get_market_symbol(sym, force_refresh=force_refresh)
            c1 = _v3_candidate(item)
            if c1:
                v3.append(c1)
            c2 = _shakeout_candidate(item)
            if c2:
                shakeout.append(c2)
        except Exception:
            errors.append(sym)
    v3.sort(key=lambda x: x.get("rankScore", 0), reverse=True)
    shakeout.sort(key=lambda x: x.get("rankScore", 0), reverse=True)
    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "criteria": [
            "Chỉ hiện kết quả/tín hiệu hiện tại; không hiển thị công thức tính chi tiết",
            "Không lấy danh sách thắng quá khứ làm khuyến nghị mua",
            "Cuối phiên tính lại cache R/S; cuối ngày kiểm tra backtest để xem công thức còn khả dụng",
        ],
        "strategies": [
            {"id": "v3", "name": "Chiến lược 1: Mua tại điểm hỗ trợ", "items": v3[:12]},
            {"id": "shakeout", "name": "Chiến lược 2: Mua khi cổ phiếu rũ", "items": shakeout[:12]},
        ],
        "total": len(v3) + len(shakeout),
        "errors": errors,
        "cached": False,
    }
    _cache = (now, payload)
    return payload
