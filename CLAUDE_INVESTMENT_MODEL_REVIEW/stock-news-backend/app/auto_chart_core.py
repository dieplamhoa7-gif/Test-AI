"""
auto_chart_core — Pivot detection, auto trendlines, multi-source S/R levels.

Module nền tảng cho hệ thống tự động vẽ trendline / hỗ trợ-kháng cự / mẫu hình.
Mục tiêu: chạy được trên DataFrame OHLC (columns: time, open, high, low, close, volume)
và trả dict Python sẵn sàng cho lớp formatter TradingView Lightweight Charts.

Tác giả: Claude (Anthropic) — phiên bản đầu, code tiếng Việt comment để anh review.

Cấu trúc:
  - find_pivots(df, window=5): fractal pivots high/low
  - atr(df, n=14)
  - TrendlineDetector: tự động vẽ trendline tăng/giảm
  - SRLevelDetector: S/R đa lớp (pivot, volume profile, MA, round number, Fib)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import math
import numpy as np
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, n: int = 14) -> float:
    """ATR cuối kỳ. Dùng để buffer cho mọi check breakdown/breakout."""
    if df is None or df.empty or len(df) < n + 1:
        return max(float(df["close"].iloc[-1] if len(df) else 1) * 0.015, 0.01)
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    tr = pd.concat([(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1 / n, adjust=False).mean().iloc[-1])


def _to_unix(ts) -> int:
    """Chuyển pandas Timestamp → unix seconds (TradingView Lightweight Charts cần)."""
    if isinstance(ts, (int, np.integer)):
        return int(ts)
    return int(pd.Timestamp(ts).timestamp())


def _merge_parallel_lines(lines: list, atr_val: float,
                          slope_rel_tol: float = 0.25,
                          end_dist_atr: float = 2.5) -> list:
    """
    Gộp các trendline cùng type có hướng & độ dốc tương đồng + endpoint gần nhau.
    Greedy: sort theo score giảm, mỗi line mới chỉ giữ nếu chưa có line nào trong
    danh sách giữ "đủ song song và gần" với nó.

    Tiêu chí "tương đồng":
      - Cùng type (uptrend/uptrend hoặc downtrend/downtrend)
      - |Δslope| / |avg_slope| ≤ slope_rel_tol (mặc định 25%) HOẶC
        |Δslope| ≤ atr_val * 0.003 (slope cực nhỏ thì so tuyệt đối)
      - Khoảng cách value tại điểm cuối (extension) ≤ end_dist_atr × ATR

    Trong mỗi cluster, giữ line có score cao nhất.
    """
    if not lines:
        return []
    # Sort by score desc — line tốt nhất đứng đầu
    sorted_lines = sorted(lines, key=lambda l: l.score, reverse=True)
    kept = []
    for tl in sorted_lines:
        s1 = tl.slope_per_bar
        # Lấy giá trị tại điểm cuối (anchor thứ 2) làm reference
        v1_end = tl.points[-1]["value"]
        t1_end = tl.points[-1]["time"]
        merged = False
        for kp in kept:
            if kp.type != tl.type:
                continue
            s2 = kp.slope_per_bar
            v2_end = kp.points[-1]["value"]
            t2_end = kp.points[-1]["time"]
            avg_slope = (abs(s1) + abs(s2)) / 2
            slope_diff = abs(s1 - s2)
            # Slope tương đồng?
            slope_similar = (slope_diff <= avg_slope * slope_rel_tol) or (slope_diff <= atr_val * 0.003)
            # Endpoint gần?  (project tới cùng thời điểm để so cho công bằng)
            # Chọn thời điểm chung = max(t1_end, t2_end), project line kia về đó
            if t1_end >= t2_end:
                # project kp ra t1_end
                bars_extend = (t1_end - t2_end) / (24 * 3600 * 7)   # approx, đơn vị bar tuần
                v2_at_t1 = v2_end + s2 * bars_extend
                end_dist = abs(v1_end - v2_at_t1)
            else:
                bars_extend = (t2_end - t1_end) / (24 * 3600 * 7)
                v1_at_t2 = v1_end + s1 * bars_extend
                end_dist = abs(v2_end - v1_at_t2)
            endpoint_close = end_dist <= end_dist_atr * atr_val
            if slope_similar and endpoint_close:
                merged = True
                break
        if not merged:
            kept.append(tl)
    return kept


def find_pivots(df: pd.DataFrame, window: int = 5) -> tuple[list[dict], list[dict]]:
    """
    Fractal pivot detection: 1 nến là pivot HIGH nếu high của nó ≥ high của window nến
    trái và window nến phải. Tương tự cho LOW. Window mặc định 5 ≈ pivot "swing".

    Trả 2 list dict: pivots_high, pivots_low — mỗi dict {idx, time, price}.
    """
    if df is None or df.empty or len(df) < window * 2 + 1:
        return [], []
    highs, lows = [], []
    h_arr = df["high"].astype(float).values
    l_arr = df["low"].astype(float).values
    t_arr = df["time"].values
    n = len(df)
    for i in range(window, n - window):
        hi = h_arr[i]
        if hi >= h_arr[i - window:i].max() and hi >= h_arr[i + 1:i + window + 1].max():
            highs.append({"idx": i, "time": _to_unix(t_arr[i]), "price": float(hi)})
        lo = l_arr[i]
        if lo <= l_arr[i - window:i].min() and lo <= l_arr[i + 1:i + window + 1].min():
            lows.append({"idx": i, "time": _to_unix(t_arr[i]), "price": float(lo)})
    return highs, lows


# ─────────────────────────────────────────────────────────────────────────────
# Trendline detector
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Trendline:
    type: str                # "uptrend" | "downtrend"
    points: list[dict]       # 2 anchor points {time, value}
    slope_per_bar: float     # slope (giá / bar)
    touches: int             # số pivot chạm vào line (trong tolerance ATR)
    length_bars: int
    r_squared: float
    valid: bool              # chưa bị phá vỡ ≥ 1.5 ATR
    score: float
    touch_points: list[dict] | None = None
    reversal_confirmed: bool = False
    id: str = ""


class TrendlineDetector:
    """
    Tự động vẽ trendline tăng/giảm bằng cách quét tổ hợp 2 pivot làm anchor,
    sau đó đếm số pivot khác chạm vào line (trong tolerance ATR), filter theo
    R² (độ thẳng) và validity (chưa bị break ≥ 1.5 ATR).

    Mục tiêu: trả về tối đa N trendline có score cao nhất cho cả uptrend và downtrend.
    """

    def __init__(self, atr_tol_mult: float = 0.6, min_touches: int = 3,
                 min_length_bars: int = 20, max_lines_per_side: int = 4,
                 lookback_bars: int = 240,
                 merge_slope_rel_tol: float = 0.25,
                 merge_end_dist_atr: float = 2.5):
        self.atr_tol_mult = atr_tol_mult
        self.min_touches = min_touches
        self.min_length_bars = min_length_bars
        self.max_lines_per_side = max_lines_per_side   # mở rộng để frontend còn dữ liệu mà gộp/lọc
        self.lookback_bars = lookback_bars
        self.merge_slope_rel_tol = merge_slope_rel_tol
        self.merge_end_dist_atr = merge_end_dist_atr

    def _line_value_at(self, p1, p2, idx):
        """Giá của line tại bar idx, tính từ 2 anchor points (p1, p2 dạng dict idx/price)."""
        if p2["idx"] == p1["idx"]:
            return p1["price"]
        slope = (p2["price"] - p1["price"]) / (p2["idx"] - p1["idx"])
        return p1["price"] + slope * (idx - p1["idx"])

    def _score_line(self, p1, p2, pivots, all_close, atr_val, kind):
        """
        Đánh giá 1 cặp pivot anchor:
          - touches: số pivot khác (cùng loại) chạm line trong tolerance ATR
          - r²: chất lượng fit
          - validity: bao nhiêu nến đóng cửa phá line ≥ 1.5 ATR (uptrend: close < line; downtrend: close > line)
        """
        if p2["idx"] - p1["idx"] < self.min_length_bars:
            return None
        slope = (p2["price"] - p1["price"]) / (p2["idx"] - p1["idx"])
        # Filter slope vô lý (>10%/bar)
        avg_price = (p1["price"] + p2["price"]) / 2
        if abs(slope) > avg_price * 0.10:
            return None
        tol = atr_val * self.atr_tol_mult
        # touches: pivot cùng loại nằm trong tol
        touches_pivots = []
        for p in pivots:
            if p["idx"] < p1["idx"] or p["idx"] > p2["idx"]:
                continue
            v_line = self._line_value_at(p1, p2, p["idx"])
            if abs(p["price"] - v_line) <= tol:
                touches_pivots.append(p)
        touches = len(touches_pivots)
        if touches < self.min_touches:
            return None
        touch_points = [{"idx": int(p["idx"]), "time": p.get("time"), "price": round(float(p["price"]), 2)} for p in touches_pivots]
        reversal_confirmed = touches >= 4
        if touches == 3:
            checks = []
            for p in touches_pivots:
                idx = int(p["idx"])
                if idx + 3 >= len(all_close):
                    checks.append(False)
                    continue
                c0 = float(all_close[idx])
                c3 = float(all_close[idx + 3])
                # Support touch must bounce in next 3 bars; resistance touch must reject in next 3 bars.
                if kind == "uptrend":
                    checks.append(c3 > c0 + 0.25 * atr_val)
                else:
                    checks.append(c3 < c0 - 0.25 * atr_val)
            reversal_confirmed = bool(checks) and all(checks)
        # r²: fit lại bằng OLS qua các touch pivot để đo độ thẳng
        if len(touches_pivots) >= 2:
            xs = np.array([p["idx"] for p in touches_pivots], float)
            ys = np.array([p["price"] for p in touches_pivots], float)
            slope_fit, intercept = np.polyfit(xs, ys, 1)
            ss_res = float(((ys - (slope_fit * xs + intercept)) ** 2).sum())
            ss_tot = float(((ys - ys.mean()) ** 2).sum())
            r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        else:
            r2 = 0.0
        # Validity: đếm số nến trong [p1.idx, last_idx] đóng cửa phá line ≥ 1.5 ATR
        last_idx = len(all_close) - 1
        breaks = 0
        for i in range(p1["idx"], last_idx + 1):
            v_line = self._line_value_at(p1, p2, i)
            c = float(all_close[i])
            if kind == "uptrend" and c < v_line - 1.5 * atr_val:
                breaks += 1
            if kind == "downtrend" and c > v_line + 1.5 * atr_val:
                breaks += 1
        valid = breaks <= 1  # cho phép 1 lần thủng tạm thời (false break)
        length = p2["idx"] - p1["idx"]
        score = (touches * 14) + (r2 * 30) + (math.log1p(length) * 6) - (breaks * 18)
        return {
            "slope": slope,
            "touches": touches,
            "r2": r2,
            "length": length,
            "breaks": breaks,
            "valid": valid,
            "score": score,
            "touch_points": touch_points,
            "reversal_confirmed": reversal_confirmed,
        }

    def detect(self, df: pd.DataFrame) -> list[Trendline]:
        if df is None or df.empty or len(df) < self.min_length_bars + 10:
            return []
        df = df.tail(self.lookback_bars).reset_index(drop=True)
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        atr_val = atr(df, 14)
        highs, lows = find_pivots(df, window=5)
        close_arr = df["close"].astype(float).values
        time_arr = df["time"].values

        results = []

        # Uptrend lines: nối 2 pivot LOW (LL → HL hoặc HL → HL)
        for i in range(len(lows)):
            for j in range(i + 1, len(lows)):
                p1, p2 = lows[i], lows[j]
                if p2["price"] <= p1["price"]:
                    continue   # uptrend đòi hỏi higher low
                eval_res = self._score_line(p1, p2, lows, close_arr, atr_val, "uptrend")
                if eval_res is None:
                    continue
                results.append(("uptrend", p1, p2, eval_res))

        # Downtrend lines: nối 2 pivot HIGH (lower highs)
        for i in range(len(highs)):
            for j in range(i + 1, len(highs)):
                p1, p2 = highs[i], highs[j]
                if p2["price"] >= p1["price"]:
                    continue
                eval_res = self._score_line(p1, p2, highs, close_arr, atr_val, "downtrend")
                if eval_res is None:
                    continue
                results.append(("downtrend", p1, p2, eval_res))

        # Dedupe + pick top per side
        trendlines = []
        for kind in ("uptrend", "downtrend"):
            kind_results = [r for r in results if r[0] == kind]
            kind_results.sort(key=lambda x: x[3]["score"], reverse=True)
            picked = []
            for _, p1, p2, ev in kind_results:
                # Dedupe: nếu line mới quá giống line đã pick (cùng anchor ±5 bar) → bỏ
                dup = False
                for pp1, pp2 in picked:
                    if abs(pp1["idx"] - p1["idx"]) <= 5 and abs(pp2["idx"] - p2["idx"]) <= 5:
                        dup = True
                        break
                if dup:
                    continue
                picked.append((p1, p2))
                # Extend p2 đến nến cuối cùng (project trendline tới hiện tại)
                last_idx = len(close_arr) - 1
                slope = (p2["price"] - p1["price"]) / (p2["idx"] - p1["idx"])
                extended_value = p1["price"] + slope * (last_idx - p1["idx"])
                trendlines.append(Trendline(
                    type=kind,
                    points=[
                        {"time": _to_unix(time_arr[p1["idx"]]), "value": round(p1["price"], 2)},
                        {"time": _to_unix(time_arr[last_idx]), "value": round(extended_value, 2)},
                    ],
                    slope_per_bar=float(slope),
                    touches=ev["touches"],
                    length_bars=ev["length"],
                    r_squared=round(ev["r2"], 3),
                    valid=ev["valid"],
                    score=round(ev["score"], 2),
                    touch_points=ev.get("touch_points", []),
                    reversal_confirmed=bool(ev.get("reversal_confirmed", False)),
                    id=f"{kind}_{len(trendlines)+1}",
                ))
                if len(picked) >= self.max_lines_per_side:
                    break
        return trendlines


# ─────────────────────────────────────────────────────────────────────────────
# S/R Level detector — đa lớp + cluster scoring
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SRLevel:
    type: str          # "support" | "resistance"
    price: float
    zone: list         # [low, high]
    sources: list      # ["swing_low", "ma50", "volume_node", ...]
    touches: int       # số pivot rớt vào zone
    confidence: float  # 0-100
    touch_points: list[dict] | None = None
    reversal_confirmed: bool = False
    id: str = ""


class SRLevelDetector:
    """
    S/R đa lớp:
      - swing_low / swing_high từ pivot fractal
      - volume_node: high-volume bins từ volume profile
      - ma_anchor: MA20, MA50, MA200
      - round_number: 5/10/50/100… tùy magnitude giá
      - fibonacci: 0.236 / 0.382 / 0.5 / 0.618 / 0.786 từ swing leg gần nhất

    Sau đó cluster các candidate theo zone width (= 0.6 ATR), tính confidence
    theo số source + số touch + độ gần giá hiện tại.
    """

    def __init__(self, lookback_bars: int = 240, zone_atr_mult: float = 0.6,
                 vol_profile_bins: int = 20, max_levels_per_side: int = 6):
        self.lookback_bars = lookback_bars
        self.zone_atr_mult = zone_atr_mult
        self.vol_profile_bins = vol_profile_bins
        self.max_levels_per_side = max_levels_per_side

    def _round_levels(self, price: float, atr_val: float) -> list[float]:
        """Tâm lý: round numbers (5, 10, 50, 100…) tùy magnitude."""
        if price <= 0:
            return []
        step = 1
        if price < 5:    step = 0.5
        elif price < 20: step = 1
        elif price < 50: step = 2
        elif price < 100: step = 5
        elif price < 500: step = 10
        else:            step = 25
        lo = price * 0.85
        hi = price * 1.15
        out = []
        x = math.floor(lo / step) * step
        while x <= hi:
            if abs(x - price) > atr_val * 0.3:  # bỏ level dính giá hiện tại
                out.append(float(round(x, 2)))
            x += step
        return out

    def _ma_levels(self, df: pd.DataFrame) -> dict[str, float]:
        c = df["close"].astype(float)
        out = {}
        if len(c) >= 20:
            out["ma20"] = float(c.rolling(20).mean().iloc[-1])
        if len(c) >= 50:
            out["ma50"] = float(c.rolling(50).mean().iloc[-1])
        if len(c) >= 200:
            out["ma200"] = float(c.rolling(200).mean().iloc[-1])
        return out

    def _fib_levels(self, df: pd.DataFrame) -> list[tuple[float, str]]:
        """Fib từ swing leg lớn nhất trong lookback (high → low gần nhất hoặc ngược lại)."""
        if len(df) < 30:
            return []
        h = df["high"].astype(float)
        l = df["low"].astype(float)
        hi_idx = int(h.idxmax())
        lo_idx = int(l.idxmin())
        if hi_idx == lo_idx:
            return []
        hi = float(h.iloc[hi_idx])
        lo = float(l.iloc[lo_idx])
        rng = hi - lo
        if rng <= 0:
            return []
        ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
        out = []
        # Nếu high muộn hơn low → leg up → fib retracement xuống
        if hi_idx > lo_idx:
            for r in ratios:
                out.append((hi - rng * r, f"fib_{int(r*1000)/10}"))
        else:
            for r in ratios:
                out.append((lo + rng * r, f"fib_{int(r*1000)/10}"))
        return out

    def _volume_profile_nodes(self, df: pd.DataFrame) -> list[float]:
        """Tìm các bin có volume cao nhất → likely S/R zones."""
        if "volume" not in df.columns or len(df) < 30:
            return []
        lo = float(df["low"].min())
        hi = float(df["high"].max())
        if hi <= lo:
            return []
        bins = self.vol_profile_bins
        step = (hi - lo) / bins
        bucket_vol = np.zeros(bins)
        for _, row in df.iterrows():
            mid = (float(row["high"]) + float(row["low"])) / 2
            idx = min(bins - 1, max(0, int((mid - lo) / step)))
            bucket_vol[idx] += float(row.get("volume") or 0)
        # Top 5 bin
        top_idx = np.argsort(bucket_vol)[::-1][:5]
        return [round(lo + (i + 0.5) * step, 2) for i in top_idx if bucket_vol[i] > 0]

    def detect(self, df: pd.DataFrame) -> list[SRLevel]:
        if df is None or df.empty or len(df) < 30:
            return []
        df = df.tail(self.lookback_bars).reset_index(drop=True).copy()
        df["time"] = pd.to_datetime(df["time"])
        for c in ["open", "high", "low", "close", "volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        price = float(df["close"].iloc[-1])
        atr_val = atr(df, 14)
        zone_w = atr_val * self.zone_atr_mult

        highs, lows = find_pivots(df, window=5)

        # Candidates: (price_value, source_tag)
        candidates: list[tuple[float, str]] = []
        for p in lows:
            candidates.append((p["price"], "swing_low"))
        for p in highs:
            candidates.append((p["price"], "swing_high"))
        for v in self._volume_profile_nodes(df):
            candidates.append((v, "volume_node"))
        for name, v in self._ma_levels(df).items():
            candidates.append((v, name))
        for v in self._round_levels(price, atr_val):
            candidates.append((v, "round_number"))
        for v, tag in self._fib_levels(df):
            candidates.append((v, tag))

        # Cluster: gom các candidate có |Δ| ≤ zone_w/2 lại thành 1 zone
        candidates.sort(key=lambda x: x[0])
        clusters = []
        for v, src in candidates:
            if not clusters or abs(v - clusters[-1]["center"]) > zone_w / 2:
                clusters.append({"center": v, "values": [v], "sources": [src]})
            else:
                clusters[-1]["values"].append(v)
                clusters[-1]["sources"].append(src)
                clusters[-1]["center"] = float(np.mean(clusters[-1]["values"]))

        # Confidence: số nguồn unique × 12 + số touch + max 30 cho gần giá
        results = []
        for cl in clusters:
            center = cl["center"]
            sources_unique = list(dict.fromkeys(cl["sources"]))
            zone_lo = round(center - zone_w / 2, 2)
            zone_hi = round(center + zone_w / 2, 2)
            # Decide support vs resistance theo vị trí so với giá hiện tại
            kind = "support" if center <= price else "resistance"
            # Touches: support dùng low chạm zone, resistance dùng high chạm zone
            if kind == "support":
                touch_idx = [int(i) for i in np.where((df["low"] <= zone_hi) & (df["low"] >= zone_lo))[0]]
                touch_points = [{"idx": i, "time": _to_unix(df["time"].iloc[i]), "price": round(float(df["low"].iloc[i]), 2)} for i in touch_idx]
            else:
                touch_idx = [int(i) for i in np.where((df["high"] <= zone_hi) & (df["high"] >= zone_lo))[0]]
                touch_points = [{"idx": i, "time": _to_unix(df["time"].iloc[i]), "price": round(float(df["high"].iloc[i]), 2)} for i in touch_idx]
            touches = len(touch_idx)
            reversal_confirmed = touches >= 4
            if touches == 3:
                checks = []
                close_arr = df["close"].astype(float).values
                for i in touch_idx:
                    if i + 3 >= len(close_arr):
                        checks.append(False)
                        continue
                    c0 = float(close_arr[i])
                    c3 = float(close_arr[i + 3])
                    if kind == "support":
                        checks.append(c3 > c0 + 0.20 * atr_val)
                    else:
                        checks.append(c3 < c0 - 0.20 * atr_val)
                reversal_confirmed = bool(checks) and all(checks)
            dist_pct = abs(price - center) / price * 100
            dist_score = max(0, 30 - dist_pct * 3)  # gần giá hơn → điểm cao hơn
            conf = (
                len(sources_unique) * 12
                + min(touches, 10) * 2
                + dist_score
            )
            conf = float(min(100, max(0, conf)))
            results.append(SRLevel(
                type=kind,
                price=round(center, 2),
                zone=[zone_lo, zone_hi],
                sources=sources_unique[:5],
                touches=touches,
                confidence=round(conf, 1),
                touch_points=touch_points,
                reversal_confirmed=reversal_confirmed,
                id="",
            ))

        # Sort theo confidence, pick top N mỗi side
        supports = sorted([r for r in results if r.type == "support"],
                          key=lambda x: x.confidence, reverse=True)[:self.max_levels_per_side]
        resistances = sorted([r for r in results if r.type == "resistance"],
                             key=lambda x: x.confidence, reverse=True)[:self.max_levels_per_side]
        # Assign id sau khi pick
        final = []
        for i, r in enumerate(supports, 1):
            r.id = f"support_{i}"
            final.append(r)
        for i, r in enumerate(resistances, 1):
            r.id = f"resistance_{i}"
            final.append(r)
        return final
