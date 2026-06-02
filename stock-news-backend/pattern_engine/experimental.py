"""
experimental.py — Tier 3: harmonic, Elliott, Smart Money, Wyckoff.

CẢNH BÁO: Các detector ở đây là HEURISTIC GẦN ĐÚNG, không phải chuẩn vàng.
- Harmonic: chỉ check tỷ lệ Fibonacci với dung sai rộng trên 5 pivot gần nhất.
- Elliott: chỉ "gợi ý" cấu trúc 5 sóng, KHÔNG khẳng định wave count.
- Smart Money: BOS/CHoCH/FVG/Order Block theo định nghĩa cơ học đơn giản;
  vốn dành cho intraday/daily nên trên nến tuần chỉ mang tính tham khảo.
- Wyckoff: phân loại phase rất thô dựa range + volume.

Mọi output gắn tier=3, confidence trần = "low" và note có chữ "experimental".
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .core import split_pivots, fit_line, line_val, pct
from .chart_patterns import _pattern, _pt


def _exp(df, typ, direction, score, levels, lines, note, status="active", idx=None):
    p = _pattern(df, typ, direction, 3, min(score, 60), levels, lines, status,
                 "[experimental] " + note, idx=idx)
    p["confidence"] = "low"  # trần cứng cho tier 3
    return p


# =====================================================================
# HARMONIC (Gartley / Bat / Butterfly / Crab / AB=CD)
# =====================================================================
_HARMONIC = {
    # name: (AB retr range, BC range, CD/AB or XD extension range)
    "gartley":   {"AB": (0.50, 0.71), "BC": (0.38, 0.89), "XD": (0.75, 0.82)},
    "bat":       {"AB": (0.38, 0.50), "BC": (0.38, 0.89), "XD": (0.85, 0.92)},
    "butterfly": {"AB": (0.71, 0.81), "BC": (0.38, 0.89), "XD": (1.21, 1.41)},
    "crab":      {"AB": (0.38, 0.62), "BC": (0.38, 0.89), "XD": (1.58, 1.70)},
}


def harmonic(df, pivots):
    """Lấy 5 pivot xen kẽ gần nhất làm X-A-B-C-D, check tỷ lệ Fib với dung sai rộng."""
    out = []
    if len(pivots) < 5:
        return out
    # 5 pivot cuối, yêu cầu xen kẽ high/low
    last5 = pivots[-5:]
    kinds = [p["kind"] for p in last5]
    if len(set(kinds[i] != kinds[i+1] for i in range(4))) != 1:
        # không xen kẽ hoàn hảo -> vẫn thử nhưng hạ điểm
        pass
    X, A, B, C, D = [p["value"] for p in last5]
    XA = A - X
    AB = B - A
    BC = C - B
    CD = D - C
    if XA == 0 or AB == 0 or BC == 0:
        return out
    ab_retr = abs(AB / XA)
    bc_retr = abs(BC / AB)
    xd_ext = abs((D - X) / XA) if XA else 0
    direction = "bullish" if last5[-1]["kind"] == "low" else "bearish"
    for name, r in _HARMONIC.items():
        ok_ab = r["AB"][0] - 0.05 <= ab_retr <= r["AB"][1] + 0.05
        ok_bc = r["BC"][0] - 0.05 <= bc_retr <= r["BC"][1] + 0.05
        ok_xd = r["XD"][0] - 0.10 <= xd_ext <= r["XD"][1] + 0.10
        if ok_ab and ok_bc and ok_xd:
            lines = [{"name": "XABCD", "type": "polyline",
                      "points": [_pt(df, p, lbl)["points"][0]
                                 for p, lbl in zip(last5, ["X","A","B","C","D"])]}]
            out.append(_exp(df, f"harmonic-{name}", direction, 52,
                            {"prz": round(D, 2)}, lines,
                            f"{name.title()} pattern: AB={ab_retr:.2f} BC={bc_retr:.2f} XD={xd_ext:.2f}",
                            idx=last5[-1]["index"]))
    return out


# =====================================================================
# ELLIOTT WAVE (chỉ gợi ý cấu trúc 5 sóng đẩy)
# =====================================================================
def elliott(df, pivots):
    """Heuristic: 6 pivot gần nhất tạo dạng đẩy 1-2-3-4-5 nếu xu hướng nhất quán."""
    out = []
    if len(pivots) < 6:
        return out
    last6 = pivots[-6:]
    vals = [p["value"] for p in last6]
    # uptrend impulse: dãy higher highs / higher lows tổng thể tăng
    diffs = np.diff(vals)
    up = vals[-1] > vals[0] and vals[2] > vals[0] and vals[4] > vals[2]
    down = vals[-1] < vals[0] and vals[2] < vals[0] and vals[4] < vals[2]
    if up:
        out.append(_exp(df, "elliott-impulse-up", "bullish", 48, {},
                        [{"name": "wave-12345", "type": "polyline",
                          "points": [_pt(df, p, f"w{i}")["points"][0] for i, p in enumerate(last6)]}],
                        "Gợi ý 5 sóng đẩy tăng (chưa xác nhận wave count)",
                        idx=last6[-1]["index"]))
    elif down:
        out.append(_exp(df, "elliott-impulse-down", "bearish", 48, {},
                        [{"name": "wave-12345", "type": "polyline",
                          "points": [_pt(df, p, f"w{i}")["points"][0] for i, p in enumerate(last6)]}],
                        "Gợi ý 5 sóng đẩy giảm (chưa xác nhận wave count)",
                        idx=last6[-1]["index"]))
    return out


# =====================================================================
# SMART MONEY: BOS / CHoCH / FVG / Order Block
# =====================================================================
def smart_money(df, pivots, lookback=40):
    out = []
    n = len(df)
    highs, lows = split_pivots(pivots)
    close = df["close"].iloc[-1]

    # BOS / CHoCH: so sánh swing gần nhất
    rh = [p for p in highs if p["index"] >= n - lookback]
    rl = [p for p in lows if p["index"] >= n - lookback]
    if len(rh) >= 2 and close > rh[-1]["value"]:
        out.append(_exp(df, "bos-bullish", "bullish", 52,
                        {"level": round(rh[-1]["value"], 2)},
                        [{"name": "BOS", "type": "horizontal", "points": [
                            {"time": df["date"].iloc[rh[-1]["index"]].strftime("%Y-%m-%d"), "value": round(rh[-1]["value"], 2)},
                            {"time": df["date"].iloc[-1].strftime("%Y-%m-%d"), "value": round(rh[-1]["value"], 2)}]}],
                        f"Phá đỉnh swing {rh[-1]['value']:.1f} — break of structure tăng"))
    if len(rl) >= 2 and close < rl[-1]["value"]:
        out.append(_exp(df, "bos-bearish", "bearish", 52,
                        {"level": round(rl[-1]["value"], 2)}, [],
                        f"Thủng đáy swing {rl[-1]['value']:.1f} — break of structure giảm"))

    # FVG (Fair Value Gap): 3 nến, gap giữa nến 1 và nến 3
    h, l = df["high"].values, df["low"].values
    for i in range(max(2, n - 15), n):
        if l[i] > h[i-2]:  # bullish FVG
            out.append(_exp(df, "fvg-bullish", "bullish", 48,
                            {"gapLow": round(float(h[i-2]), 2), "gapHigh": round(float(l[i]), 2)},
                            [], f"Khoảng trống giá tăng {h[i-2]:.1f}-{l[i]:.1f}", idx=i))
        elif h[i] < l[i-2]:  # bearish FVG
            out.append(_exp(df, "fvg-bearish", "bearish", 48,
                            {"gapLow": round(float(h[i]), 2), "gapHigh": round(float(l[i-2]), 2)},
                            [], f"Khoảng trống giá giảm {h[i]:.1f}-{l[i-2]:.1f}", idx=i))

    # Order Block: nến giảm cuối trước một xung tăng mạnh (bullish OB), và ngược lại
    o, c = df["open"].values, df["close"].values
    for i in range(max(1, n - 20), n - 1):
        impulse = (c[i+1] - c[i]) / c[i] if c[i] else 0
        if c[i] < o[i] and impulse > 0.05:  # nến đỏ rồi bật mạnh
            out.append(_exp(df, "order-block-bullish", "bullish", 46,
                            {"obLow": round(float(l[i]), 2), "obHigh": round(float(h[i]), 2)},
                            [], f"Order block tăng tại {l[i]:.1f}-{h[i]:.1f}", idx=i))
        elif c[i] > o[i] and impulse < -0.05:
            out.append(_exp(df, "order-block-bearish", "bearish", 46,
                            {"obLow": round(float(l[i]), 2), "obHigh": round(float(h[i]), 2)},
                            [], f"Order block giảm tại {l[i]:.1f}-{h[i]:.1f}", idx=i))
    return out


# =====================================================================
# WYCKOFF PHASE (phân loại thô)
# =====================================================================
def wyckoff(df, lookback=30):
    seg = df.iloc[-lookback:]
    close = df["close"].iloc[-1]
    rng_pct = (seg["high"].max() - seg["low"].min()) / close
    slope = np.polyfit(np.arange(len(seg)), seg["close"].values, 1)[0] / close
    vol_trend = seg["volume"].iloc[-10:].mean() / seg["volume"].iloc[:10].mean() if len(seg) >= 20 else 1
    out = []
    if rng_pct < 0.20 and abs(slope) < 0.002:
        # sideway -> accumulation hay distribution tùy vị trí so với MA dài
        prior = df["close"].iloc[-lookback-20:-lookback].mean() if len(df) > lookback+20 else close
        if close >= prior:
            out.append(_exp(df, "wyckoff-accumulation", "bullish", 50,
                            {"support": round(float(seg["low"].min()), 2),
                             "resistance": round(float(seg["high"].max()), 2)}, [],
                            f"Vùng tích lũy: range {rng_pct*100:.0f}%, đi ngang"))
        else:
            out.append(_exp(df, "wyckoff-distribution", "bearish", 50,
                            {"support": round(float(seg["low"].min()), 2),
                             "resistance": round(float(seg["high"].max()), 2)}, [],
                            f"Vùng phân phối: range {rng_pct*100:.0f}%, đi ngang"))
    return out
