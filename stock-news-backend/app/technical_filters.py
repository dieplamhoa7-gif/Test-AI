from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic
from typing import Any

from app.market_data import get_market_symbol

TECHNICAL_UNIVERSE = [
    "FPT", "MWG", "HPG", "SSI", "VCI", "VND", "HCM", "MBS", "TCB", "MBB",
    "ACB", "CTG", "BID", "VPB", "STB", "VIB", "VHM", "VIC", "VRE", "KDH",
    "DXG", "NVL", "KBC", "GEX", "GVR", "PNJ", "VNM", "MSN", "SAB", "GAS",
    "PLX", "PVD", "PVS", "DGC", "DCM", "DPM", "HSG", "NKG", "DIG", "CEO",
    "VTP", "CTR", "REE", "PC1", "SZC", "BCM", "HDG", "KSB", "ANV", "VHC",
]

CACHE_TTL_SECONDS = 10 * 60
_cache: dict[tuple[int, int], tuple[float, dict[str, Any]]] = {}


def _norm(text: Any) -> str:
    return str(text or "").strip().lower()


def _pct_distance(price: float, level: float) -> float | None:
    if price <= 0 or level <= 0:
        return None
    return abs(price - level) / price * 100


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _build_trade_plan(price: float, support: float, resistance: float, atr: float, reward_reference: float = 0) -> dict[str, Any] | None:
    if price <= 0 or support <= 0 or resistance <= 0:
        return None
    atr_pad = 0.5 * atr if atr > 0 else price * 0.015
    stop_loss = max(support - atr_pad, price * 0.9)
    target = resistance if resistance > price else price * 1.03
    if reward_reference and reward_reference > target:
        target = reward_reference
    if stop_loss >= price:
        stop_loss = support * 0.99
    risk_pct = (price - stop_loss) / price * 100
    reward_pct = (target - price) / price * 100
    rr = reward_pct / risk_pct if risk_pct > 0 else 0
    return {
        "entryZone": [round(min(price, support * 1.03), 2), round(price, 2)],
        "stopLoss": round(stop_loss, 2),
        "target": round(target, 2),
        "riskPct": round(risk_pct, 2),
        "rewardPct": round(reward_pct, 2),
        "riskReward": round(rr, 2),
    }


def _classify_setup(item: dict[str, Any]) -> dict[str, Any] | None:
    """Short, practical PTKT rule.

    Backtests showed S/R is most useful as a map, especially resistance warnings.
    Support is only actionable when trend/momentum confirmation is present.
    """
    symbol = str(item.get("ticker") or "").upper()
    price = _safe_float(item.get("price"))
    tech = item.get("technical") or {}
    if not symbol or price <= 0 or not tech:
        return None

    trend = str(tech.get("effectiveTrend") or tech.get("trend") or "")
    trend_l = _norm(trend)
    strength = str(tech.get("trendStrength") or "")
    volume_state = str(tech.get("volumeState") or "")
    volume_l = _norm(volume_state)
    zone = str(tech.get("zoneState") or "")
    zone_l = _norm(zone)
    structure = str(tech.get("marketStructureDay") or "")
    action = str(tech.get("action") or "")
    vol_ratio = _safe_float(tech.get("volumeRatio"))
    rsi = _safe_float(tech.get("rsi14"))
    macd_hist = _safe_float(tech.get("histogram"))
    adx = _safe_float(tech.get("adx14"))
    plus_di = _safe_float(tech.get("plusDi"))
    minus_di = _safe_float(tech.get("minusDi"))
    ma20 = _safe_float(tech.get("ma20"))
    ma50 = _safe_float(tech.get("ma50"))
    atr = _safe_float(tech.get("atr"))
    support = _safe_float(tech.get("activeSupportDay") or tech.get("supportDay"))
    resistance = _safe_float(tech.get("activeResistanceDay") or tech.get("resistanceDay"))
    near_support = _pct_distance(price, support)
    near_resistance = _pct_distance(price, resistance)
    support_meta = tech.get("supportStrengthDay") or {}
    resistance_meta = tech.get("resistanceStrengthDay") or {}
    support_score = _safe_float(support_meta.get("score"))
    resistance_score = _safe_float(resistance_meta.get("score"))
    # Fallback for the stable market_data.py: if experimental S/R score is not
    # available, approximate a lightweight score from distance, trend and context
    # so the UI still has candidates without depending on heavy experimental code.
    if support_score <= 0 and near_support is not None:
        support_score = max(0.0, 72 - near_support * 8)
        if price >= ma50 > 0:
            support_score += 8
        if 38 <= rsi <= 60:
            support_score += 6
        if macd_hist >= 0:
            support_score += 4
        if vol_ratio <= 1.1:
            support_score += 4
    if resistance_score <= 0 and near_resistance is not None:
        resistance_score = max(0.0, 72 - near_resistance * 8)
        if rsi >= 58:
            resistance_score += 8
        if vol_ratio >= 1.2:
            resistance_score += 5
        if "quá mua" in zone_l:
            resistance_score += 6

    if support <= 0 or resistance <= 0:
        return None

    above_ma20 = ma20 > 0 and price >= ma20
    above_ma50 = ma50 > 0 and price >= ma50
    uptrend = "tăng" in trend_l or (above_ma20 and (ma50 <= 0 or ma20 >= ma50 * 0.98)) or plus_di > minus_di
    strong_downtrend = ma20 > 0 and ma50 > 0 and price < ma20 and price < ma50 and minus_di > plus_di and adx >= 20
    strong_volume = vol_ratio >= 1.3 or "mạnh" in volume_l or "xác nhận" in volume_l
    quiet_volume = vol_ratio <= 1.0 or "thấp" in volume_l or "cạn cung" in volume_l
    near_support_ok = near_support is not None and near_support <= 3.0
    near_resistance_ok = near_resistance is not None and near_resistance <= 2.5
    macd_ok = macd_hist >= 0

    next_resistance = _safe_float(tech.get("nextResistanceDay") or tech.get("resistanceDay2"))
    plan = _build_trade_plan(price, support, resistance, atr, next_resistance)
    if not plan:
        return None

    setup_group = ""
    priority = 0
    rank = 0.0
    reason_parts: list[str] = []
    warning: list[str] = []

    # 1) Highest confidence from backtest: resistance warning / take-profit area.
    if near_resistance_ok and resistance_score >= 68 and (rsi >= 56 or "quá mua" in zone_l or strong_volume):
        setup_group = "Kháng cự mạnh - cân nhắc chốt lời/né mua đuổi"
        priority = 5
        rank = 88 + min(resistance_score, 100) / 10
        reason_parts = ["gần kháng cự", "R/S score cao", "RSI/volume cho thấy dễ bị từ chối"]
        warning = ["Không mua đuổi; chỉ mua tiếp nếu breakout kèm volume xác nhận"]
    # 2) Buy setup: support is only a watch/buy zone with confirmation.
    elif near_support_ok and support_score >= 68 and uptrend and not strong_downtrend and macd_ok and rsi >= 38 and quiet_volume and plan["riskReward"] >= 1.15 and plan["riskPct"] <= 7.5:
        setup_group = "Hỗ trợ có xác nhận - canh mua thăm dò"
        priority = 4
        rank = 78 + min(support_score, 100) / 12
        reason_parts = ["gần hỗ trợ", "xu hướng không xấu", "MACD/RSI xác nhận", "volume điều chỉnh thấp"]
    # 3) Breakout is watch-only unless volume confirms.
    elif near_resistance_ok and uptrend and strong_volume and price >= resistance * 0.995:
        setup_group = "Breakout có volume - theo dõi mua khi giữ nền"
        priority = 3
        rank = 74
        reason_parts = ["sát/vượt kháng cự", "volume xác nhận", "xu hướng ủng hộ"]
        warning = ["Đợi giữ được vùng breakout, tránh mua nếu rút chân xuống dưới kháng cự"]
    else:
        return None

    if plan["riskReward"] >= 1.5:
        rank += 4
        reason_parts.append("RR chấp nhận")
    if plan["riskPct"] <= 4.0:
        rank += 3
        reason_parts.append("cắt lỗ ngắn")
    if adx >= 18 and plus_di > minus_di and setup_group.startswith("Hỗ trợ"):
        rank += 2
        reason_parts.append("ADX/DI ủng hộ")

    return {
        "symbol": symbol,
        "price": round(price, 2),
        "changePct": item.get("changePct"),
        "setupGroup": setup_group,
        "entryZone": plan["entryZone"],
        "stopLoss": plan["stopLoss"],
        "target": plan["target"],
        "riskPct": plan["riskPct"],
        "rewardPct": plan["rewardPct"],
        "riskReward": plan["riskReward"],
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "supportScore": round(support_score, 2),
        "resistanceScore": round(resistance_score, 2),
        "nearSupportPct": _round(near_support),
        "nearResistancePct": _round(near_resistance),
        "trend": trend,
        "trendStrength": strength,
        "marketStructure": structure,
        "setupType": str(tech.get("setupType") or ""),
        "volumeState": volume_state,
        "volumeRatio": round(vol_ratio, 2),
        "zoneState": zone,
        "rsi14": round(rsi, 2),
        "macdHistogram": round(macd_hist, 4),
        "adx14": round(adx, 2),
        "plusDi": round(plus_di, 2),
        "minusDi": round(minus_di, 2),
        "rankScore": round(rank, 2),
        "priority": priority,
        "reason": ", ".join(dict.fromkeys(reason_parts)),
        "warning": "; ".join(warning),
        "action": action,
    }


def top_technical_setups(limit: int = 20, max_symbols: int = 50, force_refresh: bool = False) -> dict[str, Any]:
    limit = max(1, min(int(limit or 20), 50))
    max_symbols = max(limit, min(int(max_symbols or 50), len(TECHNICAL_UNIVERSE)))
    key = (limit, max_symbols)
    now = monotonic()
    cached = _cache.get(key)
    if cached and not force_refresh and (now - cached[0]) < CACHE_TTL_SECONDS:
        payload = dict(cached[1])
        payload["cached"] = True
        return payload

    items: list[dict[str, Any]] = []
    for symbol in TECHNICAL_UNIVERSE[:max_symbols]:
        try:
            item = get_market_symbol(symbol, force_refresh=force_refresh)
            classified = _classify_setup(item)
            if classified:
                items.append(classified)
        except Exception:
            continue

    items.sort(key=lambda x: (x.get("priority", 0), x.get("rankScore", 0), x.get("riskReward") or 0), reverse=True)
    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "items": items[:limit],
        "totalCandidates": len(items),
        "limit": limit,
        "cached": False,
        "criteria": [
            "PTKT dùng R/S làm bản đồ, không dùng hỗ trợ làm tín hiệu mua độc lập",
            "Ưu tiên cảnh báo kháng cự mạnh: không mua đuổi/cân nhắc chốt lời từng phần",
            "Hỗ trợ chỉ canh mua thăm dò khi có xác nhận MACD/RSI, xu hướng không xấu và volume điều chỉnh thấp",
            "Breakout chỉ theo dõi khi có volume xác nhận và giữ được vùng vượt cản",
            "Loại nếu thiếu hỗ trợ/kháng cự rõ, RR < 1.2 hoặc risk > 7%",
        ],
        "ttlSeconds": CACHE_TTL_SECONDS,
    }
    _cache[key] = (now, payload)
    return payload
