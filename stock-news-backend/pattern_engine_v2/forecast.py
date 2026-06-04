"""
forecast.py — Dự báo giá: trend regression (log close) + ATR band + scenarios.
Research-only. Chỉ dùng dữ liệu QUÁ KHỨ (<= ngày cuối) để fit.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import timedelta

try:
    from sklearn.linear_model import LinearRegression
    HAS_SK = True
except Exception:
    HAS_SK = False


def forecast(df, horizon=20, fit_window=60, k=0.9):
    close = df["close"].values
    n = len(df)
    w = min(fit_window, n)
    y = np.log(close[-w:])
    x = np.arange(w).reshape(-1, 1)

    if HAS_SK:
        model = LinearRegression().fit(x, y)
        slope = model.coef_[0]
        intercept = model.intercept_
    else:
        slope, intercept = np.polyfit(np.arange(w), y, 1)

    atr = df["atr20"].iloc[-1]
    if pd.isna(atr):
        atr = close[-1] * 0.03

    # tần suất ngày để sinh ngày tương lai
    gap = int(df["date"].diff().dropna().dt.days.median())
    last_date = df["date"].iloc[-1]
    last_close = float(close[-1])

    points = []
    for step in range(1, horizon + 1):
        # Neo vào GIÁ THỰC TẾ cuối (không phải giá trị mô hình tại điểm cuối — giá thực
        # có thể lệch khỏi đường regression). Cộng dồn drift đã damping từ last_close.
        # Damping bước hiệu dụng (dưới-tuyến tính): eff = step^0.6.
        eff = step ** 0.6
        val = last_close * float(np.exp(slope * eff))
        band = k * atr * np.sqrt(step)
        fdate = last_date + timedelta(days=gap * step)
        points.append({
            "time": fdate.strftime("%Y-%m-%d"),
            "value": round(val, 2),
            "lower": round(val - band, 2),
            "upper": round(val + band, 2),
        })

    # CAGR ước lượng theo slope
    per_bar = np.exp(slope) - 1
    return {
        "method": "linear_regression_log_close_atr_band",
        "horizonBars": horizon,
        "fitWindow": w,
        "points": points,
        "perBarDrift": round(per_bar * 100, 3),
        "note": "Research-only probabilistic baseline, not financial advice",
    }


def build_scenarios(df, patterns, fc):
    """Tổng hợp kịch bản. Đảm bảo thứ tự logic: bearish <= base <= bullish."""
    close = df["close"].iloc[-1]
    base_target = fc["points"][-1]["value"]

    bull_targets, bear_targets = [], []
    for p in patterns:
        lv = p.get("levels", {})
        if p["direction"] == "bullish" and lv.get("target") and lv["target"] > close:
            bull_targets.append((lv["target"], p["type"], p["score"]))
        if p["direction"] == "bearish" and lv.get("target") and lv["target"] < close:
            bear_targets.append((lv["target"], p["type"], p["score"]))
    bull_targets.sort(key=lambda t: -t[2])
    bear_targets.sort(key=lambda t: -t[2])

    scen = {"base": {"target": base_target,
                     "reason": f"{fc['horizonBars']}-bar trend regression (damped)"}}

    # Bullish: lấy max giữa base và pattern bullish target mạnh nhất
    if bull_targets:
        cand = bull_targets[0]
        bull_val = max(cand[0], base_target)
        reason = cand[1] + " target" if cand[0] >= base_target else "regression drift"
    else:
        bull_val = round(max(base_target, close * 1.08), 2)
        reason = "upside theo drift + ATR"
    scen["bullish"] = {"target": round(bull_val, 2), "reason": reason}

    # Bearish: lấy min giữa pattern bearish target và nearest support
    sups = [p["levels"].get("support") for p in patterns
            if p.get("levels", {}).get("support") and p["levels"]["support"] < close]
    nearest_sup = max(sups) if sups else round(close * 0.92, 2)
    if bear_targets:
        bear_val = min(bear_targets[0][0], nearest_sup)
        reason_b = bear_targets[0][1] + " target" if bear_targets[0][0] <= nearest_sup else "nearest support"
    else:
        bear_val = nearest_sup
        reason_b = "nearest support / ATR risk"
    scen["bearish"] = {"target": round(bear_val, 2), "reason": reason_b}

    # Sanity cuối: ép thứ tự bearish <= base <= bullish
    scen["bearish"]["target"] = min(scen["bearish"]["target"], base_target)
    scen["bullish"]["target"] = max(scen["bullish"]["target"], base_target)
    return scen
