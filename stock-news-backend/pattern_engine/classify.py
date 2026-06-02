"""
classify.py — Phân loại, hòa giải (reconcile) và xếp ưu tiên pattern.

Mục tiêu "tự động phân biệt và gán":
1. dedup: gộp pattern cùng loại+hướng, giữ điểm cao nhất.
2. confluence: pattern cùng hướng nằm gần cùng vùng giá -> cộng điểm hợp lưu.
3. conflict: phát hiện tín hiệu mâu thuẫn (bull vs bear cùng vùng/cùng thời điểm).
4. recency weighting: pattern gần hiện tại quan trọng hơn pattern cũ.
5. priority: sắp xếp theo điểm tổng hợp; gán nhãn vai trò (primary/supporting/context).
"""
from __future__ import annotations
import numpy as np


CATEGORY_WEIGHT = {
    "chart-pattern": 1.0,
    "level": 0.9,
    "trendline": 0.9,
    "candlestick": 0.5,   # nến đơn lẻ ít trọng số hơn mẫu hình giá
}

TIER_WEIGHT = {1: 1.0, 2: 0.8, 3: 0.5}   # tier 3 experimental giảm trọng số


def classify_and_rank(patterns, df):
    """Trả về (ranked_patterns, conflicts, summary_extra)."""
    close = float(df["close"].iloc[-1])
    n = len(df)

    # 1) dedup theo (type, direction)
    best = {}
    for p in patterns:
        key = (p["type"], p["direction"])
        if key not in best or p["score"] > best[key]["score"]:
            best[key] = p
    pats = list(best.values())

    # 2) tính điểm tổng hợp (composite) cho mỗi pattern
    for p in pats:
        idx = p.get("_idx", n - 1)
        recency = (idx + 1) / n            # 0..1, gần hiện tại -> cao
        cat_w = CATEGORY_WEIGHT.get(p["category"], 0.7)
        tier_w = TIER_WEIGHT.get(p.get("tier", 1), 0.7)
        active_bonus = 1.1 if p.get("status") == "active" else (1.0 if p.get("status") == "forming" else 0.85)
        comp = p["score"] * cat_w * tier_w * (0.6 + 0.4 * recency) * active_bonus
        p["_composite"] = round(comp, 1)

    # 3) confluence: cộng điểm khi nhiều pattern cùng hướng tụ quanh một vùng giá
    _apply_confluence(pats, close)

    # 4) phát hiện conflict
    conflicts = _detect_conflicts(pats, close)

    # 5) xếp hạng + gán vai trò
    pats.sort(key=lambda x: -x["_composite_final"])
    for i, p in enumerate(pats):
        if i < 3 and p["_composite_final"] >= 45:
            p["role"] = "primary"
        elif p["_composite_final"] >= 30:
            p["role"] = "supporting"
        else:
            p["role"] = "context"

    extra = {
        "conflicts": conflicts,
        "primaryCount": sum(1 for p in pats if p.get("role") == "primary"),
        "rankingMethod": "composite = score × category_w × tier_w × recency × status, + confluence",
    }
    return pats, conflicts, extra


def _apply_confluence(pats, close):
    """Pattern cùng hướng có mức giá then chốt gần nhau -> mỗi cái +confluence bonus."""
    # thu thập mức giá đại diện cho từng pattern
    def key_level(p):
        lv = p.get("levels", {})
        for k in ("neckline", "resistance", "support", "target"):
            if lv.get(k):
                return lv[k]
        return p.get("price", close)

    tol = close * 0.03
    for p in pats:
        p["_confluence"] = 0
        lvl = key_level(p)
        partners = 0
        for q in pats:
            if q is p or q["direction"] != p["direction"]:
                continue
            if abs(key_level(q) - lvl) <= tol:
                partners += 1
        p["_confluence"] = min(partners, 4) * 4    # tối đa +16
        p["_composite_final"] = round(p["_composite"] + p["_confluence"], 1)
        if partners >= 2:
            p.setdefault("evidence", {})["confluence"] = f"{partners} tín hiệu cùng hướng hội tụ quanh {lvl:.1f}"


def _detect_conflicts(pats, close):
    """Tìm cặp tín hiệu mâu thuẫn THỰC SỰ.

    Bỏ qua: cặp support vs resistance (cluster/trendline) — chúng là khung giá
    cùng tồn tại bình thường, KHÔNG phải mâu thuẫn. Chỉ tính khi ít nhất một bên
    là MẪU HÌNH giá hoặc nến đảo chiều cho tín hiệu hành động ngược nhau.
    """
    FRAME = {"support-cluster", "resistance-cluster",
             "support-trendline", "resistance-trendline"}

    strong = [p for p in pats if p["_composite_final"] >= 35 and p["direction"] in ("bullish", "bearish")]
    bulls = [p for p in strong if p["direction"] == "bullish"]
    bears = [p for p in strong if p["direction"] == "bearish"]
    conflicts = []
    for b in bulls:
        for s in bears:
            # cả hai đều là khung giá -> không phải mâu thuẫn
            if b["type"] in FRAME and s["type"] in FRAME:
                continue
            both_active = b.get("status") == "active" and s.get("status") == "active"
            close_score = abs(b["_composite_final"] - s["_composite_final"]) < 20
            if both_active and close_score:
                conflicts.append({
                    "bullish": b["type"], "bullScore": b["_composite_final"],
                    "bearish": s["type"], "bearScore": s["_composite_final"],
                    "note": "Tín hiệu tăng và giảm cùng mạnh, cùng đang hiệu lực — cân nhắc chờ xác nhận.",
                })
    seen = set(); uniq = []
    for c in conflicts:
        k = (c["bullish"], c["bearish"])
        if k not in seen:
            seen.add(k); uniq.append(c)
    return uniq[:5]


def make_bias(pats):
    """Tính bias tổng hợp dùng composite_final thay vì score thô."""
    bull = sum(p["_composite_final"] for p in pats if p["direction"] == "bullish")
    bear = sum(p["_composite_final"] for p in pats if p["direction"] == "bearish")
    if bull > bear * 1.25:
        bias = "bullish"
    elif bear > bull * 1.25:
        bias = "bearish"
    else:
        bias = "neutral"
    # độ tin cậy của bias: chênh lệch càng lớn càng chắc
    total = bull + bear
    strength = round(abs(bull - bear) / total * 100, 1) if total else 0
    return bias, round(bull, 1), round(bear, 1), strength
