"""
chart_patterns.py — Mẫu hình giá rule-based (tái dựng 08/07/2026 sau sự cố mất file).

Nâng cấp theo yêu cầu:
- Double/Triple top-bottom: mỗi đỉnh/đáy phải là CỰC TRỊ CỦA MỘT KHOẢNG THỜI GIAN
  (cao/thấp nhất trong ±SIG_WIN phiên), neo vào nến cực trị thật, neckline chuẩn,
  status theo lịch sử (forming/watch/confirmed/failed).
- Trendline + S/R: chấm điểm theo số lần chạm, phản ứng sau chạm, độ mới, vi phạm;
  GỘP các đường slope tương đương thành 1 đường uy tín nhất; giữ tối đa 3 đường/phía
  (bước build lọc tổng 4-6 đường điểm cao nhất).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .core import split_pivots, fit_line, line_val, pct, clamp

SIG_WIN = 10  # đỉnh/đáy của mẫu double/triple phải là cực trị trong ±SIG_WIN phiên


def _last_date(df):
    return df["date"].iloc[-1].strftime("%Y-%m-%d")


def _target_sane(target, close, max_move=0.35):
    return target > 0 and pct(target, close) <= max_move


def _d(df, idx):
    return df["date"].iloc[int(max(0, min(len(df) - 1, idx)))].strftime("%Y-%m-%d")


def _conf(score):
    if score >= 70:
        return "high"
    if score >= 58:
        return "medium"
    return "low"


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


# =====================================================================
# 1. SUPPORT / RESISTANCE ZONES  (tier 1)
# =====================================================================
def support_resistance(df, pivots):
    """Vùng hỗ trợ/kháng cự: gom mọi pivot vào vùng ATR, chấm điểm theo
    số lần test (cách nhau >=5 phiên), thời gian tồn tại, phản ứng sau test,
    volume xác nhận, role-flip; xuất thành VÙNG zoneLow-zoneHigh."""
    close = float(df["close"].iloc[-1])
    atr = float(df["atr20"].iloc[-1])
    n = len(df)
    high_a = df["high"].values
    low_a = df["low"].values
    volr = df["vol_ratio"].fillna(1.0).values
    tol = max(atr * 0.6, close * 0.01)
    min_sep = 5

    allp = sorted(pivots, key=lambda p: p["value"])
    used = [False] * len(allp)
    clusters = []
    for i, p in enumerate(allp):
        if used[i]:
            continue
        grp = [p]; used[i] = True
        for j in range(i + 1, len(allp)):
            if not used[j] and abs(allp[j]["value"] - np.mean([g["value"] for g in grp])) <= tol:
                grp.append(allp[j]); used[j] = True
        if len(grp) >= 2:
            clusters.append(grp)

    out = []
    for grp in clusters:
        grp = sorted(grp, key=lambda p: p["index"])
        level = float(np.mean([x["value"] for x in grp]))
        if pct(level, close) > 0.30:
            continue
        tests = []
        for x in grp:
            if not tests or x["index"] - tests[-1]["index"] >= min_sep:
                tests.append(x)
        touches = len(tests)
        if touches < 2:
            continue
        role = "support" if level <= close else "resistance"
        reacts, volrs = [], []
        for x in tests:
            i0 = x["index"]; i1 = min(n, i0 + 11)
            if i1 - i0 < 3:
                continue
            if role == "support":
                reacts.append((float(np.max(high_a[i0:i1])) / max(x["value"], 1e-9) - 1) * 100)
            else:
                reacts.append((1 - float(np.min(low_a[i0:i1])) / max(x["value"], 1e-9)) * 100)
            volrs.append(float(volr[i0]))
        avg_react = float(np.mean(reacts)) if reacts else 0.0
        avg_volr = float(np.mean(volrs)) if volrs else 1.0
        span_bars = tests[-1]["index"] - tests[0]["index"]
        try:
            span_days = int((tests[-1]["date"] - tests[0]["date"]).days)
        except Exception:
            span_days = span_bars
        kinds = {x["kind"] for x in grp}
        role_flip = len(kinds) == 2

        score = 30.0
        score += min(touches * 8, 32)
        score += min(span_bars / n * 30, 12)
        score += clamp(avg_react * 1.8, 0, 14)
        score += 7 if avg_volr >= 1.2 else 0
        score += 7 if role_flip else 0
        score -= min(pct(close, level) * 90, 22)
        score = clamp(score)
        if score < 35:
            continue

        z_lo, z_hi = round(level - tol, 2), round(level + tol, 2)
        t_first = _d(df, tests[0]["index"])
        note = (f"{'Hỗ trợ' if role == 'support' else 'Kháng cự'} {z_lo}–{z_hi}: "
                f"{touches} lần test · tồn tại {span_days} ngày · phản ứng TB "
                f"{'+' if role == 'support' else '-'}{abs(avg_react):.1f}% · volume {avg_volr:.1f}x"
                + (" · role-flip" if role_flip else ""))
        out.append({
            "type": f"{role}-cluster", "category": "level", "tier": 1,
            "direction": "bullish" if role == "support" else "bearish",
            "time": _last_date(df), "price": round(close, 2),
            "score": round(score, 1),
            "confidence": _conf(score), "status": "active",
            "levels": {role: round(level, 2), "zoneLow": z_lo, "zoneHigh": z_hi},
            "lines": [
                {"name": "zone-low", "type": "horizontal", "points": [
                    {"time": t_first, "value": z_lo}, {"time": _last_date(df), "value": z_lo}]},
                {"name": "zone-high", "type": "horizontal", "points": [
                    {"time": t_first, "value": z_hi}, {"time": _last_date(df), "value": z_hi}]},
            ],
            "evidence": {"touches": touches, "spanDays": span_days,
                         "avgReactionPct": round(avg_react, 1),
                         "avgVolRatio": round(avg_volr, 2), "roleFlip": role_flip,
                         "notes": note,
                         "touchPoints": [{"time": _d(df, x["index"]),
                                          "value": round(x["value"], 2)} for x in tests][:10]},
        })
    sups = sorted([p for p in out if p["type"] == "support-cluster"], key=lambda p: -p["score"])[:2]
    ress = sorted([p for p in out if p["type"] == "resistance-cluster"], key=lambda p: -p["score"])[:2]
    return sups + ress


# =====================================================================
# 2. TRENDLINES — nhiều ứng viên, chấm điểm, gộp slope tương tự  (tier 1)
# =====================================================================
def trendlines(df, pivots):
    highs, lows = split_pivots(pivots)
    out = []
    n_df = len(df)
    atr_last = float(df["atr20"].iloc[-1])
    tol = atr_last * 0.6
    high_a = df["high"].values
    low_a = df["low"].values
    for plist, role, direction in [(lows, "support-trendline", "bullish"),
                                   (highs, "resistance-trendline", "bearish")]:
        if len(plist) < 3:
            continue
        cands = []
        for a in range(len(plist)):
            for b in range(a + 1, len(plist)):
                if plist[b]["index"] - plist[a]["index"] < 8:
                    continue
                slope, icpt = fit_line([plist[a]["index"], plist[b]["index"]],
                                       [plist[a]["value"], plist[b]["value"]])
                touch_pts, viol = [], 0
                for p in plist:
                    pred = line_val(slope, icpt, p["index"])
                    if abs(p["value"] - pred) <= tol:
                        touch_pts.append(p)
                    elif (role.startswith("support") and p["value"] < pred - tol) or \
                         (role.startswith("resistance") and p["value"] > pred + tol):
                        viol += 1
                touches = len(touch_pts)
                if touches < 3:
                    continue
                if touch_pts[-1]["index"] < n_df - 120:
                    continue  # đường "chết", không còn điểm chạm gần đây
                xs = [p["index"] for p in touch_pts]
                ys = [p["value"] for p in touch_pts]
                slope, icpt = np.polyfit(xs, ys, 1)
                # ĐẾM LẠI trên đường đã refit (tránh đường trôi khỏi điểm chạm)
                touch_pts, viol = [], 0
                for p in plist:
                    pred = line_val(slope, icpt, p["index"])
                    if abs(p["value"] - pred) <= tol:
                        touch_pts.append(p)
                    elif (role.startswith("support") and p["value"] < pred - tol) or \
                         (role.startswith("resistance") and p["value"] > pred + tol):
                        viol += 1
                touches = len(touch_pts)
                if touches < 3 or touch_pts[-1]["index"] < n_df - 120:
                    continue
                # đường phải LIÊN QUAN tới giá hiện tại (giá trị tại phiên cuối gần close)
                close_now = float(df["close"].iloc[-1])
                if abs(line_val(slope, icpt, n_df - 1) - close_now) / close_now > 0.12:
                    continue
                # PHẢN ỨNG SAU CHẠM: % giá bật khỏi đường trong 10 phiên
                reacts = []
                for p in touch_pts:
                    i0 = p["index"]; i1 = min(n_df, i0 + 11)
                    if i1 - i0 < 3:
                        continue
                    if role.startswith("support"):
                        reacts.append((float(np.max(high_a[i0:i1])) / max(p["value"], 1e-9) - 1) * 100)
                    else:
                        reacts.append((1 - float(np.min(low_a[i0:i1])) / max(p["value"], 1e-9)) * 100)
                avg_react = float(np.mean(reacts)) if reacts else 0.0
                recency = touch_pts[-1]["index"] / n_df
                score = clamp(28 + touches * 9 - viol * 7
                              + min(max(avg_react, 0) * 1.6, 12) + recency * 12)
                cands.append({"slope": float(slope), "icpt": float(icpt),
                              "touch_pts": touch_pts, "touches": touches,
                              "viol": viol, "avg_react": avg_react, "score": float(score)})
        # GỘP đường có slope gần giống nhau & giá hiện tại gần nhau -> giữ đường uy tín nhất
        cands.sort(key=lambda c: -c["score"])
        kept = []
        for c in cands:
            merged = False
            for k in kept:
                same_slope = abs(c["slope"] - k["slope"]) <= max(abs(k["slope"]) * 0.35,
                                                                 atr_last * 0.02)
                v_c = line_val(c["slope"], c["icpt"], n_df - 1)
                v_k = line_val(k["slope"], k["icpt"], n_df - 1)
                if same_slope and abs(v_c - v_k) <= atr_last * 1.2:
                    k["merged"] += 1
                    merged = True
                    break
            if not merged:
                c["merged"] = 0
                kept.append(c)
        for c in kept[:3]:  # tối đa 3 đường mỗi phía; build lọc tổng 4-6 đường
            touch_pts = c["touch_pts"]
            p0 = touch_pts[0]
            x_end = n_df - 1
            score = clamp(c["score"] + min(c["merged"] * 3, 9))
            sign = "+" if role.startswith("support") else "-"
            note = (f"Trendline {c['touches']} chạm, {c['viol']} vi phạm, "
                    f"phản ứng TB {sign}{abs(c['avg_react']):.1f}%"
                    + (f" · gộp {c['merged']} đường tương tự" if c["merged"] else ""))
            out.append({
                "type": role, "category": "trendline", "tier": 1, "direction": direction,
                "time": _last_date(df), "price": round(float(df["close"].iloc[-1]), 2),
                "score": round(score, 1), "confidence": _conf(score), "status": "active",
                "lines": [{"name": role, "type": "diagonal", "points": [
                    {"time": _d(df, p0["index"]),
                     "value": round(line_val(c["slope"], c["icpt"], p0["index"]), 2)},
                    {"time": _d(df, x_end),
                     "value": round(line_val(c["slope"], c["icpt"], x_end), 2)}]}],
                "evidence": {"touches": c["touches"], "violations": c["viol"],
                             "avgReactionPct": round(c["avg_react"], 1),
                             "mergedLines": c["merged"],
                             "notes": note,
                             "touchPoints": [{"time": _d(df, p["index"]),
                                              "value": round(p["value"], 2)}
                                             for p in touch_pts][:8]},
            })
    return out


# =====================================================================
# 3. DOUBLE / TRIPLE TOP-BOTTOM  (tier 1)
# =====================================================================
def double_patterns(df, pivots, max_span=None, target_max_move=0.35, recent_bars=120):
    highs, lows = split_pivots(pivots)
    close = float(df["close"].iloc[-1])
    atr = float(df["atr20"].iloc[-1])
    n = len(df)
    if max_span is None:
        max_span = min(60, n)
    else:
        max_span = min(max_span, n)
    out = []

    rsi = df["rsi14"].fillna(50).values
    vol = df["volume"].values
    volr = df["vol_ratio"].fillna(1.0).values
    low_arr = df["low"].values
    high_arr = df["high"].values
    close_arr = df["close"].values
    n_recent = recent_bars  # pivot cuối phải nằm trong recent_bars phiên gần nhất

    def _prior_trend(i0, direction, back=30, min_move=0.05):
        """Mẫu đảo chiều phải có XU HƯỚNG TRƯỚC ĐÓ: 2 đáy sau sóng giảm, 2 đỉnh sau sóng tăng."""
        j = max(0, i0 - back)
        chg = close_arr[i0] / max(close_arr[j], 1e-9) - 1
        return chg <= -min_move if direction == "down" else chg >= min_move

    def _breakout_quality(bi, neckline, is_bottom):
        """Volume lúc phá neckline + retest thành công trong 15 phiên sau."""
        bvol = float(volr[bi]) if 0 <= bi < n else 1.0
        retested = False
        for k in range(bi + 1, min(n, bi + 16)):
            if is_bottom:
                if low_arr[k] <= neckline * 1.01 and close_arr[k] > neckline:
                    retested = True
                    break
            else:
                if high_arr[k] >= neckline * 0.99 and close_arr[k] < neckline:
                    retested = True
                    break
        return bvol, retested

    def _neck_pivots(i0, i1, kind):
        seg = df.iloc[i0 + 1:i1]
        if seg.empty:
            return None
        col = "high" if kind == "high" else "low"
        idx = seg[col].idxmax() if kind == "high" else seg[col].idxmin()
        return int(idx), float(df[col].iloc[idx])

    def _snap(i, kind, rad=3):
        """Neo pivot vào NẾN CỰC TRỊ thật (lặp tới hội tụ); trường hợp trôi xa
        sẽ bị chặn bởi giới hạn cứng lệch đỉnh/đáy <= max(1.2*ATR, 3%)."""
        j = int(i)
        for _ in range(6):
            a, b = max(0, j - rad), min(n, j + rad + 1)
            seg = df.iloc[a:b]
            k = int(seg["low"].idxmin()) if kind == "low" else int(seg["high"].idxmax())
            if k == j:
                break
            j = k
        if kind == "low":
            return j, float(df["low"].iloc[j])
        return j, float(df["high"].iloc[j])

    def _significant(ix, v, kind, win=SIG_WIN):
        """Đỉnh/đáy phải là CỰC TRỊ CỦA MỘT KHOẢNG THỜI GIAN ±win phiên."""
        a, b = max(0, ix - win), min(n, ix + win + 1)
        if kind == "low":
            return float(low_arr[a:b].min()) >= v - 1e-9
        return float(high_arr[a:b].max()) <= v + 1e-9

    def _extreme_quality(ix, v, kind, win=SIG_WIN):
        """Quality gate cho 2/3 đỉnh-đáy: pivot phải nổi bật so với vùng lân cận,
        không chỉ là nhiễu sát giá. Trả về prominence theo giá và ATR."""
        a, b = max(0, ix - win), min(n, ix + win + 1)
        local_atr = max(float(df["atr20"].iloc[ix]) if pd.notna(df["atr20"].iloc[ix]) else atr, atr * 0.6)
        if kind == "low":
            left_high = float(high_arr[a:ix + 1].max()) if ix >= a else float(high_arr[ix])
            right_high = float(high_arr[ix:b].max()) if b > ix else float(high_arr[ix])
            prom = min(left_high - v, right_high - v)
        else:
            left_low = float(low_arr[a:ix + 1].min()) if ix >= a else float(low_arr[ix])
            right_low = float(low_arr[ix:b].min()) if b > ix else float(low_arr[ix])
            prom = min(v - left_low, v - right_low)
        min_prom = max(local_atr * 0.55, close * 0.008)
        return prom >= min_prom, prom, prom / max(local_atr, 1e-9)

    def _shape_quality(grp, vals, necks, is_bottom):
        """Chấm chất lượng hình học: symmetry thời gian, độ đều vùng đỉnh/đáy,
        neckline đủ sâu/cao, và điểm chạm phải có prominence."""
        span = grp[-1]["index"] - grp[0]["index"]
        gaps = [b["index"] - a["index"] for a, b in zip(grp[:-1], grp[1:])]
        if gaps and max(gaps) > 3.2 * max(min(gaps), 1):
            return False, ["khoảng cách các điểm chạm lệch quá nhiều"]
        spread = max(vals) - min(vals)
        tol = max(atr * 1.10, float(np.mean(vals)) * 0.026)
        reasons = []
        if spread > tol:
            return False, [f"độ lệch điểm chạm {spread:.2f} > ngưỡng {tol:.2f}"]
        q = [_extreme_quality(g["index"], g["value"], "low" if is_bottom else "high") for g in grp]
        if not all(x[0] for x in q):
            reasons.append("cảnh báo: đỉnh/đáy nổi bật yếu")
        avg_prom_atr = float(np.mean([x[2] for x in q]))
        if avg_prom_atr < 0.65:
            reasons.append("cảnh báo: prominence dưới chuẩn")
        neck_depths = []
        for k, (ni, nv) in enumerate(necks):
            if is_bottom:
                neck_depths.append(nv - max(grp[k]["value"], grp[k + 1]["value"]))
            else:
                neck_depths.append(min(grp[k]["value"], grp[k + 1]["value"]) - nv)
        if neck_depths and min(neck_depths) < max(atr * 1.05, close * 0.018):
            reasons.append("cảnh báo: neckline tách biệt chưa mạnh")
        reasons.append(f"prominence TB {avg_prom_atr:.1f} ATR")
        reasons.append(f"span {span} phiên")
        return True, reasons

    # ---- Double / Triple BOTTOM ----
    for combo, name in [(2, "double-bottom"), (3, "triple-bottom")]:
        for i in range(len(lows) - combo + 1):
            raw = lows[i:i + combo]
            snapped = [_snap(x["index"], "low") for x in raw]
            idxs = [s[0] for s in snapped]
            vals = [s[1] for s in snapped]
            if len(set(idxs)) < combo or idxs != sorted(idxs):
                continue
            if any(b - a < 5 for a, b in zip(idxs[:-1], idxs[1:])):
                continue
            grp = [{"index": ix, "value": v} for ix, v in zip(idxs, vals)]
            span = grp[-1]["index"] - grp[0]["index"]
            spread = max(vals) - min(vals)
            if spread > max(atr * 1.2, min(vals) * 0.03):
                continue
            zone_ok = (min(x.get("zhi", 1e18) for x in raw) -
                       max(x.get("zlo", -1e18) for x in raw)) >= 0
            if not zone_ok and spread > max(atr * 1.0, min(vals) * 0.025):
                continue
            if span < 8 or span > max_span:
                continue
            if grp[-1]["index"] < n - n_recent:
                continue
            # mỗi đáy phải là đáy CỦA MỘT KHOẢNG THỜI GIAN (±SIG_WIN phiên)
            if not all(_significant(g["index"], g["value"], "low") for g in grp):
                continue
            # mẫu ĐẢO CHIỀU TĂNG phải xuất hiện sau sóng GIẢM
            if not _prior_trend(grp[0]["index"], "down"):
                continue
            necks = []
            ok = True
            for a, b in zip(grp[:-1], grp[1:]):
                nk = _neck_pivots(a["index"], b["index"], "high")
                if nk is None or nk[1] - max(a["value"], b["value"]) < max(atr * 1.2, close * 0.02):
                    ok = False
                    break
                necks.append(nk)
            if not ok:
                continue
            quality_ok, quality_notes = _shape_quality(grp, vals, necks, True)
            if not quality_ok:
                continue
            quality_penalty = 6 * sum(1 for x in quality_notes if x.startswith("cảnh báo"))
            # xác nhận chuẩn: phải vượt ĐỈNH HỒI CAO NHẤT giữa các đáy
            neckline = float(max(v for _, v in necks))
            support = float(np.mean(vals))
            target = neckline + (neckline - support)
            if not _target_sane(target, close, target_max_move):
                continue
            invalid_lv = round(min(vals) - atr, 2)
            # status theo LỊCH SỬ sau khi mẫu hoàn tất
            post = df["close"].values[grp[-1]["index"] + 1:]
            i_break = next((k for k, v in enumerate(post) if v > neckline), None)
            i_bust = next((k for k, v in enumerate(post) if v < invalid_lv), None)
            if i_bust is not None and (i_break is None or i_bust < i_break):
                status = "failed"
            elif i_break is not None:
                status = "confirmed"
            elif close >= neckline * 0.97:
                status = "watch"
            else:
                status = "forming"
            b1, b2 = grp[0], grp[-1]
            vol_dry = vol[b2["index"]] < vol[b1["index"]] * 0.85
            rsi_div = b2["value"] <= b1["value"] * 1.005 and rsi[b2["index"]] > rsi[b1["index"]] + 2
            bvol = None
            retested = False
            if status == "confirmed" and i_break is not None:
                bvol, retested = _breakout_quality(grp[-1]["index"] + 1 + i_break, neckline, True)
            score = 48 + combo * 4 + (12 if status == "confirmed" else 6 if status == "watch" else 0)
            score += 5 if vol_dry else 0
            score += 5 if rsi_div else 0
            if bvol is not None:
                score += 6 if bvol >= 1.2 else -4  # xác nhận MẠNH cần volume khi phá neckline
            score += 5 if retested else 0
            score -= quality_penalty
            score -= quality_penalty
            if status == "failed":
                score *= 0.5
            score = clamp(score)
            shape = []
            for k2, g in enumerate(grp):
                shape.append({"time": _d(df, g["index"]), "value": round(g["value"], 2)})
                if k2 < len(necks):
                    shape.append({"time": _d(df, necks[k2][0]), "value": round(necks[k2][1], 2)})
            extras = []
            extras.extend(quality_notes)
            if vol_dry:
                extras.append("vol đáy sau giảm")
            if rsi_div:
                extras.append("RSI phân kỳ dương")
            if bvol is not None:
                extras.append(f"phá neckline vol {bvol:.1f}x ({'mạnh' if bvol >= 1.2 else 'yếu'})")
            if retested:
                extras.append("đã retest neckline thành công")
            p = _pattern(df, name, "bullish", 1, score,
                         {"support": round(support, 2), "neckline": round(neckline, 2),
                          "target": round(target, 2), "stop": invalid_lv},
                         [{"name": "shape", "type": "diagonal", "points": shape},
                          {"name": "neckline", "type": "horizontal", "points": [
                              {"time": _d(df, grp[0]["index"]), "value": round(neckline, 2)},
                              {"time": _last_date(df), "value": round(neckline, 2)}]}],
                         status,
                         f"{combo} đáy ~{support:.1f} (đáy {2 * SIG_WIN + 1} phiên), neckline {neckline:.1f}"
                         + (" · " + " · ".join(extras) if extras else ""))
            p["evidence"]["touchPoints"] = [{"time": _d(df, g["index"]),
                                             "value": round(g["value"], 2)} for g in grp]
            p["evidence"]["neckline"] = round(neckline, 2)
            p["evidence"]["confirmation"] = round(neckline, 2)
            p["evidence"]["invalidLevel"] = invalid_lv
            p["evidence"]["patternStatus"] = status
            if bvol is not None:
                p["evidence"]["breakoutVolRatio"] = round(bvol, 2)
                p["evidence"]["retested"] = retested
            out.append(p)

    # ---- Double / Triple TOP ----
    for combo, name in [(2, "double-top"), (3, "triple-top")]:
        for i in range(len(highs) - combo + 1):
            raw = highs[i:i + combo]
            snapped = [_snap(x["index"], "high") for x in raw]
            idxs = [s[0] for s in snapped]
            vals = [s[1] for s in snapped]
            if len(set(idxs)) < combo or idxs != sorted(idxs):
                continue
            if any(b - a < 5 for a, b in zip(idxs[:-1], idxs[1:])):
                continue
            grp = [{"index": ix, "value": v} for ix, v in zip(idxs, vals)]
            span = grp[-1]["index"] - grp[0]["index"]
            spread = max(vals) - min(vals)
            if spread > max(atr * 1.2, min(vals) * 0.03):
                continue
            zone_ok = (min(x.get("zhi", 1e18) for x in raw) -
                       max(x.get("zlo", -1e18) for x in raw)) >= 0
            if not zone_ok and spread > max(atr * 1.0, min(vals) * 0.025):
                continue
            if span < 8 or span > max_span:
                continue
            if grp[-1]["index"] < n - n_recent:
                continue
            if not all(_significant(g["index"], g["value"], "high") for g in grp):
                continue
            # mẫu ĐẢO CHIỀU GIẢM phải xuất hiện sau sóng TĂNG
            if not _prior_trend(grp[0]["index"], "up"):
                continue
            necks = []
            ok = True
            for a, b in zip(grp[:-1], grp[1:]):
                nk = _neck_pivots(a["index"], b["index"], "low")
                if nk is None or min(a["value"], b["value"]) - nk[1] < max(atr * 1.2, close * 0.02):
                    ok = False
                    break
                necks.append(nk)
            if not ok:
                continue
            quality_ok, quality_notes = _shape_quality(grp, vals, necks, False)
            if not quality_ok:
                continue
            quality_penalty = 6 * sum(1 for x in quality_notes if x.startswith("cảnh báo"))
            # xác nhận chuẩn: phải thủng ĐÁY HỒI THẤP NHẤT giữa các đỉnh
            neckline = float(min(v for _, v in necks))
            resistance = float(np.mean(vals))
            target = neckline - (resistance - neckline)
            if not _target_sane(target, close, target_max_move):
                continue
            invalid_lv = round(max(vals) + atr, 2)
            post = df["close"].values[grp[-1]["index"] + 1:]
            i_break = next((k for k, v in enumerate(post) if v < neckline), None)
            i_bust = next((k for k, v in enumerate(post) if v > invalid_lv), None)
            if i_bust is not None and (i_break is None or i_bust < i_break):
                status = "failed"
            elif i_break is not None:
                status = "confirmed"
            elif close <= neckline * 1.03:
                status = "watch"
            else:
                status = "forming"
            bvol = None
            retested = False
            if status == "confirmed" and i_break is not None:
                bvol, retested = _breakout_quality(grp[-1]["index"] + 1 + i_break, neckline, False)
            score = 48 + combo * 4 + (12 if status == "confirmed" else 6 if status == "watch" else 0)
            if bvol is not None:
                score += 6 if bvol >= 1.2 else -4
            score += 5 if retested else 0
            if status == "failed":
                score *= 0.5
            score = clamp(score)
            shape = []
            for k2, g in enumerate(grp):
                shape.append({"time": _d(df, g["index"]), "value": round(g["value"], 2)})
                if k2 < len(necks):
                    shape.append({"time": _d(df, necks[k2][0]), "value": round(necks[k2][1], 2)})
            p = _pattern(df, name, "bearish", 1, score,
                         {"resistance": round(resistance, 2), "neckline": round(neckline, 2),
                          "target": round(target, 2), "stop": invalid_lv},
                         [{"name": "shape", "type": "diagonal", "points": shape},
                          {"name": "neckline", "type": "horizontal", "points": [
                              {"time": _d(df, grp[0]["index"]), "value": round(neckline, 2)},
                              {"time": _last_date(df), "value": round(neckline, 2)}]}],
                         status,
                         f"{combo} đỉnh ~{resistance:.1f} (đỉnh {2 * SIG_WIN + 1} phiên), neckline {neckline:.1f}"
                         + (" · " + " · ".join(quality_notes) if quality_notes else "")
                         + (f" · phá neckline vol {bvol:.1f}x ({'mạnh' if bvol >= 1.2 else 'yếu'})" if bvol is not None else "")
                         + (" · đã retest neckline" if retested else ""))
            p["evidence"]["touchPoints"] = [{"time": _d(df, g["index"]),
                                             "value": round(g["value"], 2)} for g in grp]
            p["evidence"]["neckline"] = round(neckline, 2)
            p["evidence"]["confirmation"] = round(neckline, 2)
            p["evidence"]["invalidLevel"] = invalid_lv
            p["evidence"]["patternStatus"] = status
            if bvol is not None:
                p["evidence"]["breakoutVolRatio"] = round(bvol, 2)
                p["evidence"]["retested"] = retested
            out.append(p)

    # khử double là tập con của triple cùng hướng; khử mẫu cùng loại chồng lấn
    trip_sets: dict = {}
    for p in out:
        if p["type"].startswith("triple"):
            trip_sets.setdefault(p["direction"], []).append(
                {t["time"] for t in p["evidence"]["touchPoints"]})

    def _is_sub_double(p):
        if not p["type"].startswith("double"):
            return False
        pts = {t["time"] for t in p["evidence"]["touchPoints"]}
        return any(pts <= s for s in trip_sets.get(p["direction"], []))

    out = [p for p in out if not _is_sub_double(p)]
    best: dict = {}
    for p in sorted(out, key=lambda x: -(x.get("score") or 0)):
        pts = {t["time"] for t in p["evidence"]["touchPoints"]}
        dup = False
        for q_pts in best.get(p["type"], []):
            if len(pts & q_pts) >= max(1, len(pts) - 1):
                dup = True
                break
        if not dup:
            best.setdefault(p["type"], []).append(pts)
        p["_dup"] = dup
    out = [p for p in out if not p.pop("_dup", False)]
    return out


# =====================================================================
# 4. HEAD & SHOULDERS  (tier 2)
# =====================================================================
def head_shoulders(df, pivots, recent_bars=120):
    highs, lows = split_pivots(pivots)
    atr = float(df["atr20"].iloc[-1])
    close = float(df["close"].iloc[-1])
    close_arr = df["close"].values
    n = len(df)
    out = []
    for plist, name, direction, kind in [
            (highs, "head-shoulders", "bearish", "high"),
            (lows, "inverse-head-shoulders", "bullish", "low")]:
        for i in range(len(plist) - 2):
            ls, hd, rs = plist[i], plist[i + 1], plist[i + 2]
            if kind == "high":
                if not (hd["value"] > ls["value"] and hd["value"] > rs["value"]):
                    continue
            else:
                if not (hd["value"] < ls["value"] and hd["value"] < rs["value"]):
                    continue
            if pct(ls["value"], rs["value"]) > 0.05:
                continue
            if rs["index"] < n - recent_bars:
                continue
            # CÂN XỨNG THỜI GIAN: 2 nửa mẫu không lệch quá 2.5 lần
            d1 = hd["index"] - ls["index"]
            d2 = rs["index"] - hd["index"]
            if min(d1, d2) < 3 or max(d1, d2) > 2.5 * min(d1, d2):
                continue
            # XU HƯỚNG TRƯỚC MẪU: H&S đỉnh cần sóng tăng trước, VĐV ngược cần sóng giảm
            j0 = max(0, ls["index"] - 30)
            chg = close_arr[ls["index"]] / max(close_arr[j0], 1e-9) - 1
            if kind == "high" and chg < 0.05:
                continue
            if kind == "low" and chg > -0.05:
                continue
            seg = df.iloc[ls["index"]:rs["index"] + 1]
            neckline = float(seg["low"].min()) if kind == "high" else float(seg["high"].max())
            height = abs(hd["value"] - neckline)
            if height < atr * 1.5:
                continue
            target = neckline - height if kind == "high" else neckline + height
            if not _target_sane(target, close):
                continue
            # status theo LỊCH SỬ: vượt lại đầu (bust) trước khi phá neckline -> mẫu hỏng, bỏ
            post = df["close"].values[rs["index"] + 1:]
            if kind == "high":
                i_bust = next((k for k, v in enumerate(post) if v > hd["value"]), None)
                i_brk = next((k for k, v in enumerate(post) if v < neckline), None)
            else:
                i_bust = next((k for k, v in enumerate(post) if v < hd["value"]), None)
                i_brk = next((k for k, v in enumerate(post) if v > neckline), None)
            if i_bust is not None:
                continue  # giá đã vượt lại "đầu" sau khi mẫu hình thành -> mẫu chết, không vẽ
            status = "confirmed" if i_brk is not None else "forming"
            score = clamp(52 + (10 if status == "confirmed" else 0))
            shape = [{"time": _d(df, p["index"]), "value": round(p["value"], 2)}
                     for p in (ls, hd, rs)]
            p = _pattern(df, name, direction, 2, score,
                         {"neckline": round(neckline, 2), "target": round(target, 2)},
                         [{"name": "shape", "type": "diagonal", "points": shape},
                          {"name": "neckline", "type": "horizontal", "points": [
                              {"time": _d(df, ls["index"]), "value": round(neckline, 2)},
                              {"time": _last_date(df), "value": round(neckline, 2)}]}],
                         status, "Vai-đầu-vai" + (" ngược" if kind == "low" else "") +
                         f", neckline {neckline:.1f}")
            p["evidence"]["touchPoints"] = shape
            p["evidence"]["patternStatus"] = status
            out.append(p)
            break
    return out


# =====================================================================
# 5. TRIANGLE / WEDGE / CHANNEL  (tier 2)
# =====================================================================
def triangle_wedge_channel(df, pivots, lookback=40):
    n = len(df)
    if n < lookback + 5:
        return []
    seg_h = df["high"].values[-lookback:]
    seg_l = df["low"].values[-lookback:]
    x = np.arange(lookback)
    su, iu = np.polyfit(x, seg_h, 1)
    sl, il = np.polyfit(x, seg_l, 1)
    close = float(df["close"].iloc[-1])
    atr = float(df["atr20"].iloc[-1])
    rel_u = su * lookback / max(close, 1e-9)
    rel_l = sl * lookback / max(close, 1e-9)
    flat = 0.02
    typ = None
    if rel_u < -flat and rel_l > flat:
        typ, direction = "symmetrical-triangle", "neutral"
    elif abs(rel_u) <= flat and rel_l > flat:
        typ, direction = "ascending-triangle", "bullish"
    elif rel_u < -flat and abs(rel_l) <= flat:
        typ, direction = "descending-triangle", "bearish"
    elif rel_u < -flat and rel_l < -flat:
        typ, direction = ("falling-wedge", "bullish") if rel_u < rel_l else ("down-channel", "bearish")
    elif rel_u > flat and rel_l > flat:
        typ, direction = ("rising-wedge", "bearish") if rel_l > rel_u else ("up-channel", "bullish")
    if typ is None:
        return []
    i0 = n - lookback
    score = clamp(50 + 8)
    vn = typ.replace("-", " ")
    return [_pattern(df, typ, direction, 2, score, {},
                     [{"name": "upper", "type": "diagonal", "points": [
                         {"time": _d(df, i0), "value": round(float(iu), 2)},
                         {"time": _d(df, n - 1), "value": round(float(iu + su * (lookback - 1)), 2)}]},
                      {"name": "lower", "type": "diagonal", "points": [
                          {"time": _d(df, i0), "value": round(float(il), 2)},
                          {"time": _d(df, n - 1), "value": round(float(il + sl * (lookback - 1)), 2)}]}],
                     "active", f"{vn} trên {lookback} phiên gần nhất")]


# =====================================================================
# 6-12. CÁC DETECTOR PHỤ (tier 2/3)
# =====================================================================
def darvas_box(df, lookback=30):
    n = len(df)
    if n < lookback:
        return []
    seg = df.iloc[-lookback:]
    hi, lo = float(seg["high"].max()), float(seg["low"].min())
    close = float(df["close"].iloc[-1])
    if (hi - lo) / max(close, 1e-9) > 0.10:
        return []
    return [_pattern(df, "darvas-box", "neutral", 2, 50,
                     {"support": round(lo, 2), "resistance": round(hi, 2)},
                     [{"name": "box-top", "type": "horizontal", "points": [
                         {"time": _d(df, n - lookback), "value": round(hi, 2)},
                         {"time": _last_date(df), "value": round(hi, 2)}]},
                      {"name": "box-bottom", "type": "horizontal", "points": [
                          {"time": _d(df, n - lookback), "value": round(lo, 2)},
                          {"time": _last_date(df), "value": round(lo, 2)}]}],
                     "active", f"Hộp Darvas {lo:.1f}-{hi:.1f}")]


def cup_handle(df, pivots, lookback=60):
    return []  # hiếm & nhiễu trên khung ngày VN — tạm tắt sau tái dựng


def rounding(df, lookback=40):
    return []


def flags(df, pole=10, flag_max=12):
    n = len(df)
    if n < pole + flag_max + 5:
        return []
    c = df["close"].values
    move = (c[-flag_max] / c[-flag_max - pole] - 1)
    cons = (max(c[-flag_max:]) - min(c[-flag_max:])) / max(c[-1], 1e-9)
    if move > 0.10 and cons < 0.05:
        return [_pattern(df, "bull-flag", "bullish", 2, 55, {},
                         [], "active", f"Cờ tăng: cột +{move*100:.0f}%, tích lũy hẹp")]
    if move < -0.10 and cons < 0.05:
        return [_pattern(df, "bear-flag", "bearish", 2, 55, {},
                         [], "active", f"Cờ giảm: cột {move*100:.0f}%, tích lũy hẹp")]
    return []


def spring_upthrust(df, pivots, lookback=40):
    n = len(df)
    if n < lookback + 5:
        return []
    seg = df.iloc[-lookback:-5]
    sup = float(seg["low"].min()); res = float(seg["high"].max())
    out = []
    last5 = df.iloc[-5:]
    volr = df["vol_ratio"].fillna(1.0).values
    for k in range(n - 5, n):
        r = df.iloc[k]
        if r["low"] < sup * 0.995 and r["close"] > sup:
            out.append(_pattern(df, "spring-shakeout", "bullish", 2,
                                58 if volr[k] < 1 else 52,
                                {"support": round(sup, 2)},
                                [{"name": "support", "type": "horizontal", "points": [
                                    {"time": _d(df, n - lookback), "value": round(sup, 2)},
                                    {"time": _last_date(df), "value": round(sup, 2)}]}],
                                "active",
                                f"Thủng hỗ trợ {sup:.1f} rồi đóng cửa trên, volume "
                                + ("thấp" if volr[k] < 1 else "cao"), idx=k))
            break
    for k in range(n - 5, n):
        r = df.iloc[k]
        if r["high"] > res * 1.005 and r["close"] < res:
            out.append(_pattern(df, "upthrust-bull-trap", "bearish", 2, 55,
                                {"resistance": round(res, 2)},
                                [{"name": "resistance", "type": "horizontal", "points": [
                                    {"time": _d(df, n - lookback), "value": round(res, 2)},
                                    {"time": _last_date(df), "value": round(res, 2)}]}],
                                "active", f"Vượt {res:.1f} giả rồi đóng cửa dưới", idx=k))
            break
    return out


def gaps(df, recent_bars=20):
    return []


def vsa_signals(df, recent_bars=15):
    n = len(df)
    out = []
    volr = df["vol_ratio"].fillna(1.0).values
    spread = (df["high"] - df["low"]).values
    atr = df["atr20"].fillna(0).values
    c = df["close"].values
    o = df["open"].values
    for k in range(max(1, n - recent_bars), n):
        if volr[k] >= 2.5 and spread[k] >= 1.5 * atr[k]:
            direction = "bearish" if c[k] > o[k] else "bullish"
            out.append(_pattern(df, "volume-climax", direction, 3, 50, {}, [],
                                "active", f"Cao trào volume {volr[k]:.1f}x", idx=k))
            break
    return out


def indicator_patterns(df, pivots, lookback=40):
    out = []
    n = len(df)
    c = df["close"].values
    rsi = df["rsi14"].fillna(50).values
    lows_i = [p for p in pivots if p["kind"] == "low" and p["index"] >= n - lookback]
    if len(lows_i) >= 2:
        a, b = lows_i[-2], lows_i[-1]
        if b["value"] < a["value"] * 1.002 and rsi[b["index"]] > rsi[a["index"]] + 3:
            out.append(_pattern(df, "bullish-rsi-divergence", "bullish", 2, 56, {},
                                [], "active", "Giá đáy thấp hơn nhưng RSI cao hơn", idx=b["index"]))
    highs_i = [p for p in pivots if p["kind"] == "high" and p["index"] >= n - lookback]
    if len(highs_i) >= 2:
        a, b = highs_i[-2], highs_i[-1]
        if b["value"] > a["value"] * 0.998 and rsi[b["index"]] < rsi[a["index"]] - 3:
            out.append(_pattern(df, "bearish-rsi-divergence", "bearish", 2, 56, {},
                                [], "active", "Giá đỉnh cao hơn nhưng RSI thấp hơn", idx=b["index"]))
    sma20 = df["sma20"].values
    sma50 = df["sma50"].values
    if n > 51 and not (np.isnan(sma20[-1]) or np.isnan(sma50[-1])):
        if sma20[-2] <= sma50[-2] and sma20[-1] > sma50[-1]:
            out.append(_pattern(df, "golden-cross", "bullish", 2, 58, {}, [],
                                "active", "MA20 cắt lên MA50"))
        if sma20[-2] >= sma50[-2] and sma20[-1] < sma50[-1]:
            out.append(_pattern(df, "death-cross", "bearish", 2, 58, {}, [],
                                "active", "MA20 cắt xuống MA50"))
    return out
