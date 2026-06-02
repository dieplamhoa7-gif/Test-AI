"""
chart_patterns.py — Mẫu hình giá rule-based (Tier 1 & 2).

Mỗi detector trả list dict theo schema thống nhất, có thêm khóa `tier`:
  tier 1 = detect đáng tin trên dữ liệu này
  tier 2 = detect được nhưng nhạy tham số

Tất cả pattern dùng pivot/indicator đã tính từ core.py, không nhìn dữ liệu tương lai.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .core import split_pivots, fit_line, line_val, pct, clamp


def _last_date(df):
    return df["date"].iloc[-1].strftime("%Y-%m-%d")


def _target_sane(target, close, max_move=0.35):
    """Loại target phi thực tế: cách giá hiện tại quá max_move (35%) hoặc <= 0.
    Measured-move quá xa thường là artefact của pivot ghép sai, không dùng được."""
    return target > 0 and pct(target, close) <= max_move


def _d(df, idx):
    return df["date"].iloc[idx].strftime("%Y-%m-%d")


# =====================================================================
# 1. SUPPORT / RESISTANCE CLUSTERS  (tier 1)
# =====================================================================
def support_resistance(df, pivots):
    highs, lows = split_pivots(pivots)
    close = df["close"].iloc[-1]
    atr = df["atr20"].iloc[-1]
    tol = max(atr * 0.75, close * 0.012)
    out = []
    for kind, plist, role in [("low", lows, "support"), ("high", highs, "resistance")]:
        used = [False] * len(plist)
        for i, p in enumerate(plist):
            if used[i]:
                continue
            cluster = [p]
            used[i] = True
            for j in range(i + 1, len(plist)):
                if not used[j] and abs(plist[j]["value"] - p["value"]) <= tol:
                    cluster.append(plist[j]); used[j] = True
            if len(cluster) < 2:
                continue
            level = float(np.mean([x["value"] for x in cluster]))
            # bỏ cluster quá xa giá hiện tại (>30%) — không phải mốc giao dịch hữu ích
            if pct(level, close) > 0.30:
                continue
            touches = len(cluster)
            recency = max(x["index"] for x in cluster) / len(df)
            dist_pen = pct(close, level) * 100
            score = clamp(40 + touches * 12 + recency * 15 - dist_pen)
            if score <= 5:
                continue
            out.append({
                "type": f"{role}-cluster", "category": "level", "tier": 1,
                "direction": "bullish" if role == "support" else "bearish",
                "time": _last_date(df), "price": round(close, 2),
                "score": round(score, 1),
                "confidence": _conf(score), "status": "active",
                "levels": {role: round(level, 2), "zoneLow": round(level - tol, 2),
                           "zoneHigh": round(level + tol, 2)},
                "lines": [{"name": role, "type": "horizontal", "points": [
                    {"time": _d(df, min(x["index"] for x in cluster)), "value": round(level, 2)},
                    {"time": _last_date(df), "value": round(level, 2)}]}],
                "evidence": {"touches": touches, "notes": f"{touches} pivot chạm vùng {role}"},
            })
    return out


# =====================================================================
# 2. TRENDLINES  (tier 1)
# =====================================================================
def trendlines(df, pivots):
    highs, lows = split_pivots(pivots)
    out = []
    for plist, role, direction in [(lows, "support-trendline", "bullish"),
                                    (highs, "resistance-trendline", "bearish")]:
        if len(plist) < 2:
            continue
        best = None
        for a in range(len(plist)):
            for b in range(a + 1, len(plist)):
                if plist[b]["index"] - plist[a]["index"] < 8:
                    continue
                slope, icpt = fit_line([plist[a]["index"], plist[b]["index"]],
                                       [plist[a]["value"], plist[b]["value"]])
                touches, viol = 0, 0
                tol = df["atr20"].iloc[-1] * 0.6
                for p in plist:
                    pred = line_val(slope, icpt, p["index"])
                    if abs(p["value"] - pred) <= tol:
                        touches += 1
                    elif (role.startswith("support") and p["value"] < pred - tol) or \
                         (role.startswith("resistance") and p["value"] > pred + tol):
                        viol += 1
                if touches >= 3 and (best is None or touches - viol > best[0]):
                    best = (touches - viol, slope, icpt, plist[a], touches, viol)
        if best:
            _, slope, icpt, p0, touches, viol = best
            x_end = len(df) - 1
            score = clamp(45 + touches * 10 - viol * 8)
            out.append({
                "type": role, "category": "trendline", "tier": 1, "direction": direction,
                "time": _last_date(df), "price": round(df["close"].iloc[-1], 2),
                "score": round(score, 1), "confidence": _conf(score), "status": "active",
                "lines": [{"name": role, "type": "diagonal", "points": [
                    {"time": _d(df, p0["index"]), "value": round(line_val(slope, icpt, p0["index"]), 2)},
                    {"time": _d(df, x_end), "value": round(line_val(slope, icpt, x_end), 2)}]}],
                "evidence": {"touches": touches, "violations": viol,
                             "notes": f"Trendline {touches} chạm, {viol} vi phạm"},
            })
    return out


# =====================================================================
# 3. DOUBLE BOTTOM / TOP, TRIPLE  (tier 1)
# =====================================================================
def double_patterns(df, pivots):
    highs, lows = split_pivots(pivots)
    close = df["close"].iloc[-1]
    atr = df["atr20"].iloc[-1]
    n = len(df)
    max_span = min(60, n)  # 2 đỉnh/đáy không cách nhau quá max_span bar
    out = []

    # Double / Triple Bottom — chỉ ghép pivot LIÊN TIẾP
    for combo, name in [(2, "double-bottom"), (3, "triple-bottom")]:
        for i in range(len(lows) - combo + 1):
            grp = lows[i:i + combo]
            vals = [x["value"] for x in grp]
            span = grp[-1]["index"] - grp[0]["index"]
            if max(vals) - min(vals) > min(vals) * 0.05:  # các đáy phải ngang nhau ~5%
                continue
            if span < 8 or span > max_span:  # đủ tách nhưng không quá xa
                continue
            seg = df.iloc[grp[0]["index"]:grp[-1]["index"] + 1]
            neckline = float(seg["high"].max())
            support = float(np.mean(vals))
            if neckline <= support:
                continue
            target = neckline + (neckline - support)
            # sanity: target không được cách giá hiện tại quá 60%
            if not _target_sane(target, close):
                continue
            active = close > support * 0.97
            score = clamp(50 + (combo - 1) * 8 + (10 if close > neckline else 0))
            out.append(_pattern(df, name, "bullish", 1, score,
                                 {"support": round(support, 2), "neckline": round(neckline, 2),
                                  "target": round(target, 2), "stop": round(support - atr, 2)},
                                 _markers(df, grp, "bottom") +
                                 [{"name": "neckline", "type": "horizontal", "points": [
                                     {"time": _d(df, grp[0]["index"]), "value": round(neckline, 2)},
                                     {"time": _last_date(df), "value": round(neckline, 2)}]}],
                                 "active" if active else "forming",
                                 f"{combo} đáy ~{support:.1f}, neckline {neckline:.1f}"))

    # Double / Triple Top — chỉ ghép pivot LIÊN TIẾP
    for combo, name in [(2, "double-top"), (3, "triple-top")]:
        for i in range(len(highs) - combo + 1):
            grp = highs[i:i + combo]
            vals = [x["value"] for x in grp]
            span = grp[-1]["index"] - grp[0]["index"]
            if max(vals) - min(vals) > min(vals) * 0.05:
                continue
            if span < 8 or span > max_span:
                continue
            seg = df.iloc[grp[0]["index"]:grp[-1]["index"] + 1]
            neckline = float(seg["low"].min())
            resistance = float(np.mean(vals))
            if neckline >= resistance:
                continue
            target = neckline - (resistance - neckline)
            if not _target_sane(target, close):
                continue
            score = clamp(50 + (combo - 1) * 8 + (10 if close < neckline else 0))
            out.append(_pattern(df, name, "bearish", 1, score,
                                 {"resistance": round(resistance, 2), "neckline": round(neckline, 2),
                                  "target": round(target, 2), "stop": round(resistance + atr, 2)},
                                 _markers(df, grp, "top") +
                                 [{"name": "neckline", "type": "horizontal", "points": [
                                     {"time": _d(df, grp[0]["index"]), "value": round(neckline, 2)},
                                     {"time": _last_date(df), "value": round(neckline, 2)}]}],
                                 "active" if close < resistance * 1.03 else "forming",
                                 f"{combo} đỉnh ~{resistance:.1f}, neckline {neckline:.1f}"))
    return out


# =====================================================================
# 4. HEAD & SHOULDERS + INVERSE  (tier 2)
# =====================================================================
def head_shoulders(df, pivots):
    highs, lows = split_pivots(pivots)
    atr = df["atr20"].iloc[-1]
    close = df["close"].iloc[-1]
    out = []
    # H&S top: 3 highs liên tiếp, head cao nhất
    for i in range(len(highs) - 2):
        ls, hd, rs = highs[i], highs[i + 1], highs[i + 2]
        if not (hd["value"] > ls["value"] and hd["value"] > rs["value"]):
            continue
        if pct(ls["value"], rs["value"]) > 0.08:
            continue
        mids = [p for p in lows if ls["index"] < p["index"] < rs["index"]]
        if len(mids) < 2:
            continue
        neckline = float(np.mean([p["value"] for p in mids[:2]]))
        target = neckline - (hd["value"] - neckline)
        score = clamp(48 + (8 if close < neckline else 0))
        out.append(_pattern(df, "head-shoulders", "bearish", 2, score,
                             {"neckline": round(neckline, 2), "target": round(target, 2),
                              "stop": round(hd["value"] + atr, 2)},
                             [_pt(df, ls, "left_shoulder"), _pt(df, hd, "head"), _pt(df, rs, "right_shoulder"),
                              {"name": "neckline", "type": "horizontal", "points": [
                                  {"time": _d(df, ls["index"]), "value": round(neckline, 2)},
                                  {"time": _last_date(df), "value": round(neckline, 2)}]}],
                             "active" if close < neckline else "forming",
                             "Vai-đầu-vai, đảo chiều giảm"))
    # Inverse H&S: 3 lows, head thấp nhất
    for i in range(len(lows) - 2):
        ls, hd, rs = lows[i], lows[i + 1], lows[i + 2]
        if not (hd["value"] < ls["value"] and hd["value"] < rs["value"]):
            continue
        if pct(ls["value"], rs["value"]) > 0.08:
            continue
        mids = [p for p in highs if ls["index"] < p["index"] < rs["index"]]
        if len(mids) < 2:
            continue
        neckline = float(np.mean([p["value"] for p in mids[:2]]))
        target = neckline + (neckline - hd["value"])
        score = clamp(48 + (8 if close > neckline else 0))
        out.append(_pattern(df, "inverse-head-shoulders", "bullish", 2, score,
                             {"neckline": round(neckline, 2), "target": round(target, 2),
                              "stop": round(hd["value"] - atr, 2)},
                             [_pt(df, ls, "left_shoulder"), _pt(df, hd, "head"), _pt(df, rs, "right_shoulder"),
                              {"name": "neckline", "type": "horizontal", "points": [
                                  {"time": _d(df, ls["index"]), "value": round(neckline, 2)},
                                  {"time": _last_date(df), "value": round(neckline, 2)}]}],
                             "active" if close > neckline else "forming",
                             "Vai-đầu-vai ngược, đảo chiều tăng"))
    return out


# =====================================================================
# 5. TRIANGLE / WEDGE / CHANNEL  (tier 2) — phân tích N bar gần nhất
# =====================================================================
def triangle_wedge_channel(df, pivots, lookback=40):
    n = len(df)
    start = max(0, n - lookback)
    highs = [p for p in pivots if p["kind"] == "high" and p["index"] >= start]
    lows = [p for p in pivots if p["kind"] == "low" and p["index"] >= start]
    if len(highs) < 2 or len(lows) < 2:
        return []
    sh, ih = fit_line([p["index"] for p in highs], [p["value"] for p in highs])
    sl, il = fit_line([p["index"] for p in lows], [p["value"] for p in lows])
    close = df["close"].iloc[-1]
    rng = df["close"].iloc[start:].mean()
    nh = sh / rng  # slope chuẩn hóa
    nl = sl / rng
    flat = 0.0008  # ngưỡng "gần ngang" theo % / bar

    typ = direction = None
    if abs(nh) < flat and nl > flat:
        typ, direction = "ascending-triangle", "bullish"
    elif abs(nl) < flat and nh < -flat:
        typ, direction = "descending-triangle", "bearish"
    elif nh < -flat and nl > flat:
        typ, direction = "symmetrical-triangle", "neutral"
    elif nh < -flat and nl < -flat and abs(nh - nl) < flat:
        typ, direction = "falling-wedge", "bullish"
    elif nh > flat and nl > flat and abs(nh - nl) < flat:
        typ, direction = "rising-wedge", "bearish"
    elif nh > flat and nl > flat:
        typ, direction = "up-channel", "bullish"
    elif nh < -flat and nl < -flat:
        typ, direction = "down-channel", "bearish"
    elif nh < -flat and nl > flat:
        typ, direction = "symmetrical-triangle", "neutral"
    if typ is None:
        return []

    x0, x1 = start, n - 1
    upper = [{"time": _d(df, x0), "value": round(line_val(sh, ih, x0), 2)},
             {"time": _d(df, x1), "value": round(line_val(sh, ih, x1), 2)}]
    lower = [{"time": _d(df, x0), "value": round(line_val(sl, il, x0), 2)},
             {"time": _d(df, x1), "value": round(line_val(sl, il, x1), 2)}]
    up_now = line_val(sh, ih, x1)
    lo_now = line_val(sl, il, x1)
    measured = up_now + (up_now - lo_now) if direction == "bullish" else lo_now - (up_now - lo_now)
    score = clamp(46 + min(len(highs) + len(lows), 8) * 3)
    return [_pattern(df, typ, direction, 2, score,
                     {"resistance": round(up_now, 2), "support": round(lo_now, 2),
                      "target": round(measured, 2)},
                     [{"name": "upper", "type": "diagonal", "points": upper},
                      {"name": "lower", "type": "diagonal", "points": lower}],
                     "active",
                     f"{typ.replace('-', ' ')} trên {lookback} phiên gần nhất")]


# =====================================================================
# 6. RECTANGLE / DARVAS BOX / FLAT BASE  (tier 1)
# =====================================================================
def darvas_box(df, lookback=30):
    seg = df.iloc[-lookback:]
    box_high = float(seg["high"].max())
    box_low = float(seg["low"].min())
    close = df["close"].iloc[-1]
    if (box_high - box_low) / close > 0.16:
        return []
    vr = df["vol_ratio"].iloc[-1]
    breakout = close > box_high * 0.995 and pd.notna(vr) and vr > 1.3
    direction = "bullish" if breakout else "neutral"
    score = clamp(48 + (15 if breakout else 0))
    target = box_high + (box_high - box_low)
    return [_pattern(df, "darvas-box", direction, 1, score,
                     {"resistance": round(box_high, 2), "support": round(box_low, 2),
                      "target": round(target, 2), "stop": round(box_low, 2)},
                     [{"name": "box-top", "type": "horizontal", "points": [
                         {"time": _d(df, len(df) - lookback), "value": round(box_high, 2)},
                         {"time": _last_date(df), "value": round(box_high, 2)}]},
                      {"name": "box-bottom", "type": "horizontal", "points": [
                          {"time": _d(df, len(df) - lookback), "value": round(box_low, 2)},
                          {"time": _last_date(df), "value": round(box_low, 2)}]}],
                     "active",
                     f"Nền hẹp {lookback} phiên, biên {box_low:.1f}-{box_high:.1f}"
                     + (" — breakout volume" if breakout else ""))]


# =====================================================================
# 7. CUP & HANDLE + INVERSE  (tier 2)
# =====================================================================
def cup_handle(df, pivots, lookback=60):
    n = len(df)
    if n < 30:
        return []
    start = max(0, n - lookback)
    seg = df.iloc[start:]
    out = []
    # Cup: left rim cao, bottom giữa, right rim hồi về gần left rim
    left_rim_idx = seg["high"].idxmax() if seg["high"].iloc[:len(seg)//3].size else None
    # tìm bottom là min toàn đoạn
    bottom_idx = int(seg["low"].idxmin())
    left_part = df.iloc[start:bottom_idx]
    right_part = df.iloc[bottom_idx:n]
    if len(left_part) >= 5 and len(right_part) >= 5:
        left_rim = float(left_part["high"].max())
        right_rim = float(right_part["high"].max())
        bottom = float(df["low"].iloc[bottom_idx])
        depth = (left_rim - bottom) / left_rim
        recovery = right_rim / left_rim
        close = df["close"].iloc[-1]
        if 0.10 <= depth <= 0.50 and recovery >= 0.80:
            neckline = max(left_rim, right_rim)
            target = neckline + (neckline - bottom)
            breakout = close > neckline * 0.98
            score = clamp(45 + (12 if breakout else 0))
            li = int(left_part["high"].idxmax())
            ri = int(right_part["high"].idxmax())
            out.append(_pattern(df, "cup-handle", "bullish", 2, score,
                                 {"neckline": round(neckline, 2), "target": round(target, 2),
                                  "support": round(bottom, 2), "stop": round(bottom, 2)},
                                 [{"name": "left_rim", "type": "point", "points": [{"time": _d(df, li), "value": round(left_rim, 2)}]},
                                  {"name": "bottom", "type": "point", "points": [{"time": _d(df, bottom_idx), "value": round(bottom, 2)}]},
                                  {"name": "right_rim", "type": "point", "points": [{"time": _d(df, ri), "value": round(right_rim, 2)}]},
                                  {"name": "neckline", "type": "horizontal", "points": [
                                      {"time": _d(df, li), "value": round(neckline, 2)},
                                      {"time": _last_date(df), "value": round(neckline, 2)}]}],
                                 "active" if breakout else "forming",
                                 f"Cốc sâu {depth*100:.0f}%, hồi {recovery*100:.0f}% miệng cốc"))
    return out


# =====================================================================
# 8. ROUNDING TOP / BOTTOM  (tier 2)
# =====================================================================
def rounding(df, lookback=40):
    seg = df["close"].iloc[-lookback:].reset_index(drop=True)
    if len(seg) < 20:
        return []
    x = np.arange(len(seg))
    a, b, c = np.polyfit(x, seg.values, 2)
    out = []
    curve = a * len(seg) ** 2  # độ cong
    r2 = 1 - np.sum((seg.values - (a*x*x+b*x+c))**2) / np.sum((seg.values - seg.mean())**2)
    if r2 < 0.5:
        return []
    if a > 0:  # lõm lên -> rounding bottom
        out.append(_pattern(df, "rounding-bottom", "bullish", 2, clamp(45 + r2*20),
                            {"support": round(float(seg.min()), 2)}, [], "forming",
                            f"Đáy cong, R²={r2:.2f}"))
    elif a < 0:
        out.append(_pattern(df, "rounding-top", "bearish", 2, clamp(45 + r2*20),
                            {"resistance": round(float(seg.max()), 2)}, [], "forming",
                            f"Đỉnh cong, R²={r2:.2f}"))
    return out


# =====================================================================
# 9. BULL/BEAR FLAG  (tier 2)
# =====================================================================
def flags(df, pole=10, flag_max=12):
    n = len(df)
    if n < pole + flag_max + 2:
        return []
    out = []
    close = df["close"].values
    # tìm impulse trong pole bar kết thúc ~flag_max bar trước
    for flag_len in range(5, flag_max + 1):
        p_end = n - flag_len - 1
        p_start = p_end - pole
        if p_start < 0:
            continue
        move = (close[p_end] - close[p_start]) / close[p_start]
        flag_seg = df.iloc[p_end:n]
        flag_range = (flag_seg["high"].max() - flag_seg["low"].min()) / close[p_end]
        if move >= 0.10 and flag_range < 0.08:  # bull flag
            target = close[n-1] + (close[p_end] - close[p_start])
            out.append(_pattern(df, "bull-flag", "bullish", 2, clamp(50 + move*40),
                                {"target": round(target, 2), "support": round(float(flag_seg["low"].min()), 2)},
                                [{"name": "pole", "type": "diagonal", "points": [
                                    {"time": _d(df, p_start), "value": round(close[p_start], 2)},
                                    {"time": _d(df, p_end), "value": round(close[p_end], 2)}]}],
                                "active", f"Cờ tăng: xung lực +{move*100:.0f}%"))
            break
        elif move <= -0.10 and flag_range < 0.08:  # bear flag
            target = close[n-1] - (close[p_start] - close[p_end])
            out.append(_pattern(df, "bear-flag", "bearish", 2, clamp(50 + abs(move)*40),
                                {"target": round(target, 2), "resistance": round(float(flag_seg["high"].max()), 2)},
                                [{"name": "pole", "type": "diagonal", "points": [
                                    {"time": _d(df, p_start), "value": round(close[p_start], 2)},
                                    {"time": _d(df, p_end), "value": round(close[p_end], 2)}]}],
                                "active", f"Cờ giảm: xung lực {move*100:.0f}%"))
            break
    return out


# =====================================================================
# 10. SPRING / SHAKEOUT + UPTHRUST (false breakout)  (tier 2)
# =====================================================================
def spring_upthrust(df, pivots, lookback=40):
    highs, lows = split_pivots(pivots)
    recent = df.iloc[-3:]
    close = df["close"].iloc[-1]
    vr = df["vol_ratio"].iloc[-1]
    out = []
    # support gần nhất
    sup_levels = [p["value"] for p in lows if p["index"] >= len(df) - lookback]
    res_levels = [p["value"] for p in highs if p["index"] >= len(df) - lookback]
    if sup_levels:
        sup = min(sup_levels, key=lambda v: abs(v - close))
        if (recent["low"] < sup * 0.99).any() and close > sup and pd.notna(vr) and vr > 1.1:
            out.append(_pattern(df, "spring-shakeout", "bullish", 2, clamp(55 + (vr-1)*15),
                                {"support": round(sup, 2), "stop": round(float(recent["low"].min()), 2)},
                                [{"name": "support", "type": "horizontal", "points": [
                                    {"time": _d(df, len(df)-lookback), "value": round(sup, 2)},
                                    {"time": _last_date(df), "value": round(sup, 2)}]}],
                                "active", f"Thủng hỗ trợ {sup:.1f} rồi đóng cửa trên, volume cao"))
    if res_levels:
        res = min(res_levels, key=lambda v: abs(v - close))
        if (recent["high"] > res * 1.01).any() and close < res and pd.notna(vr) and vr > 1.1:
            out.append(_pattern(df, "upthrust-bull-trap", "bearish", 2, clamp(55 + (vr-1)*15),
                                {"resistance": round(res, 2), "stop": round(float(recent["high"].max()), 2)},
                                [{"name": "resistance", "type": "horizontal", "points": [
                                    {"time": _d(df, len(df)-lookback), "value": round(res, 2)},
                                    {"time": _last_date(df), "value": round(res, 2)}]}],
                                "active", f"Vượt kháng cự {res:.1f} rồi đóng cửa dưới (bull trap)"))
    return out


# =====================================================================
# 11. GAP DETECTION  (tier 1 cho daily; weekly thường ít gap) 
# =====================================================================
def gaps(df, recent_bars=20):
    out = []
    o, h, l, c = (df[x].values for x in ["open", "high", "low", "close"])
    atr = df["atr20"].bfill().values
    n = len(df)
    for i in range(max(1, n - recent_bars), n):
        gap_up = l[i] > h[i - 1]
        gap_down = h[i] < l[i - 1]
        if not (gap_up or gap_down):
            continue
        size = (l[i] - h[i-1]) if gap_up else (l[i-1] - h[i])
        if atr[i] and size < atr[i] * 0.3:
            continue
        direction = "bullish" if gap_up else "bearish"
        out.append(_pattern(df, "gap", direction, 1, 50.0,
                            {"gapFrom": round(float(h[i-1] if gap_up else l[i-1]), 2),
                             "gapTo": round(float(l[i] if gap_up else h[i]), 2)},
                            [], "completed",
                            f"{'Gap up' if gap_up else 'Gap down'} ~{size:.2f}", idx=i))
    return out


# =====================================================================
# 12. VSA / VOLUME SIGNALS  (tier 2)
# =====================================================================
def vsa_signals(df, recent_bars=15):
    out = []
    n = len(df)
    o, h, l, c, v = (df[x].values for x in ["open","high","low","close","volume"])
    vr = df["vol_ratio"].values
    for i in range(max(1, n - recent_bars), n):
        if pd.isna(vr[i]):
            continue
        rng = h[i] - l[i]
        body = abs(c[i] - o[i])
        spread_ratio = body / rng if rng else 0
        # No Demand: tăng nhẹ, volume thấp
        if c[i] > c[i-1] and vr[i] < 0.7 and spread_ratio < 0.4:
            out.append(_pattern(df, "no-demand", "bearish", 2, 50.0, {}, [], "completed",
                                "Tăng yếu, volume thấp — cầu yếu", idx=i))
        # No Supply
        elif c[i] < c[i-1] and vr[i] < 0.7 and spread_ratio < 0.4:
            out.append(_pattern(df, "no-supply", "bullish", 2, 50.0, {}, [], "completed",
                                "Giảm yếu, volume thấp — cung cạn", idx=i))
        # Climax / Stopping volume: volume rất cao + biên rộng
        elif vr[i] > 2.0 and rng > df["atr20"].iloc[i] * 1.3:
            d = "bearish" if c[i] > o[i] else "bullish"
            out.append(_pattern(df, "volume-climax", d, 2, 55.0, {}, [], "completed",
                                "Cao trào volume — khả năng đảo chiều", idx=i))
    return out


# =====================================================================
# 13. INDICATOR PATTERNS: RSI divergence, MACD cross, MA cross  (tier 1)
# =====================================================================
def indicator_patterns(df, pivots, lookback=40):
    out = []
    n = len(df)
    close = df["close"]
    rsi = df["rsi14"]
    highs, lows = split_pivots(pivots)
    recent_lows = [p for p in lows if p["index"] >= n - lookback][-2:]
    recent_highs = [p for p in highs if p["index"] >= n - lookback][-2:]

    # Bullish RSI divergence: giá đáy thấp hơn, RSI đáy cao hơn
    if len(recent_lows) == 2:
        a, b = recent_lows
        if b["value"] < a["value"] and rsi.iloc[b["index"]] > rsi.iloc[a["index"]]:
            out.append(_pattern(df, "bullish-rsi-divergence", "bullish", 1, 58.0, {}, [], "active",
                                f"Giá đáy thấp hơn nhưng RSI tăng ({rsi.iloc[a['index']]:.0f}→{rsi.iloc[b['index']]:.0f})"))
    if len(recent_highs) == 2:
        a, b = recent_highs
        if b["value"] > a["value"] and rsi.iloc[b["index"]] < rsi.iloc[a["index"]]:
            out.append(_pattern(df, "bearish-rsi-divergence", "bearish", 1, 58.0, {}, [], "active",
                                f"Giá đỉnh cao hơn nhưng RSI giảm ({rsi.iloc[a['index']]:.0f}→{rsi.iloc[b['index']]:.0f})"))

    # MACD cross (gần nhất trong recent_bars)
    hist = df["macd_hist"]
    for i in range(n - 5, n):
        if i < 1:
            continue
        if hist.iloc[i-1] < 0 <= hist.iloc[i]:
            out.append(_pattern(df, "macd-bullish-cross", "bullish", 1, 54.0, {}, [], "active",
                                "MACD cắt lên signal", idx=i))
        elif hist.iloc[i-1] > 0 >= hist.iloc[i]:
            out.append(_pattern(df, "macd-bearish-cross", "bearish", 1, 54.0, {}, [], "active",
                                "MACD cắt xuống signal", idx=i))

    # MA golden/death cross
    s20, s50 = df["sma20"], df["sma50"]
    for i in range(n - 5, n):
        if i < 1 or pd.isna(s50.iloc[i]) or pd.isna(s50.iloc[i-1]):
            continue
        if s20.iloc[i-1] <= s50.iloc[i-1] and s20.iloc[i] > s50.iloc[i]:
            out.append(_pattern(df, "golden-cross", "bullish", 1, 56.0, {}, [], "active",
                                "SMA20 cắt lên SMA50", idx=i))
        elif s20.iloc[i-1] >= s50.iloc[i-1] and s20.iloc[i] < s50.iloc[i]:
            out.append(_pattern(df, "death-cross", "bearish", 1, 56.0, {}, [], "active",
                                "SMA20 cắt xuống SMA50", idx=i))

    # RSI overbought/oversold (trạng thái hiện tại)
    r = rsi.iloc[-1]
    if pd.notna(r):
        if r >= 70:
            out.append(_pattern(df, "rsi-overbought", "bearish", 1, 50.0, {}, [], "active",
                                f"RSI={r:.0f} quá mua"))
        elif r <= 30:
            out.append(_pattern(df, "rsi-oversold", "bullish", 1, 50.0, {}, [], "active",
                                f"RSI={r:.0f} quá bán"))
    return out


# =====================================================================
# Helpers tạo schema
# =====================================================================
def _pattern(df, typ, direction, tier, score, levels, lines, status, note, idx=None):
    i = idx if idx is not None else len(df) - 1
    row = df.iloc[i]
    return {
        "type": typ, "category": "chart-pattern", "tier": tier, "direction": direction,
        "time": row["date"].strftime("%Y-%m-%d"), "price": round(float(row["close"]), 2),
        "score": round(float(score), 1), "confidence": _conf(score), "status": status,
        "levels": levels, "lines": lines,
        "evidence": {"volumeRatio": round(float(df["vol_ratio"].iloc[i]), 2)
                     if pd.notna(df["vol_ratio"].iloc[i]) else None,
                     "notes": note},
        "_idx": int(i),
    }


def _markers(df, grp, role):
    return [{"name": role, "type": "point",
             "points": [{"time": _d(df, p["index"]), "value": round(p["value"], 2)}]} for p in grp]


def _pt(df, p, role):
    return {"name": role, "type": "point",
            "points": [{"time": _d(df, p["index"]), "value": round(p["value"], 2)}]}


def _conf(score):
    if score >= 70:
        return "high"
    if score >= 58:
        return "medium"
    return "low"
