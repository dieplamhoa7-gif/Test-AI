from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.market_data import _load_history, _compute_indicators
from app.ml_smart_money_features import anchored_vwap_features, donchian_smart_money_structure
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE
from app.ml_support_model import FEATURE_COLUMNS

OUT = Path("data/ml/support_rebound_dataset.csv")
META = Path("data/ml/support_rebound_dataset_meta.json")
OUT.parent.mkdir(parents=True, exist_ok=True)


def n(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except Exception:
        return default


def pct(a: float, b: float) -> float:
    return (a / b - 1.0) * 100.0 if b else 0.0


def ichimoku_state(df: pd.DataFrame) -> dict[str, Any]:
    h = pd.to_numeric(df.high, errors="coerce")
    l = pd.to_numeric(df.low, errors="coerce")
    c = pd.to_numeric(df.close, errors="coerce")
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    a = ((ten + kij) / 2).shift(26)
    b = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    price = n(c.iloc[-1]); av = n(a.iloc[-1]); bv = n(b.iloc[-1])
    top = max(av, bv) if av and bv else 0.0
    bottom = min(av, bv) if av and bv else 0.0
    if top and price > top:
        state = 1
        dist = pct(price, top)
    elif bottom and price < bottom:
        state = -1
        dist = pct(price, bottom)
    elif top and bottom:
        state = 0
        dist = 0.0
    else:
        state = 0
        dist = 0.0
    return {"cloudStateNum": state, "cloudDistancePct": dist, "cloudThicknessPct": pct(top, bottom) if bottom else 0.0}


def future_labels(df: pd.DataFrame, idx: int, support: float, entry: float, horizon: int = 10) -> dict[str, Any]:
    fut = df.iloc[idx + 1: idx + 1 + horizon]
    if fut.empty or len(fut) < min(5, horizon):
        return {}
    high = pd.to_numeric(fut.high, errors="coerce")
    low = pd.to_numeric(fut.low, errors="coerce")
    close0 = entry
    max_ret = (float(high.max()) / close0 - 1) * 100 if close0 else 0
    min_ret = (float(low.min()) / close0 - 1) * 100 if close0 else 0
    close_ret = (float(fut.close.iloc[-1]) / close0 - 1) * 100 if close0 else 0
    target_hit = bool(max_ret >= 5.0)
    stop_hit = bool(min_ret <= -4.0)
    breakdown = bool((pd.to_numeric(fut.close, errors="coerce") < support * 0.99).any()) if support else False
    support_hold = not breakdown
    rebound = bool(target_hit and (not stop_hit or high.idxmax() < low.idxmin()))
    return {
        "return10d": round(close_ret, 4),
        "maxReturn10d": round(max_ret, 4),
        "maxDrawdown10d": round(min_ret, 4),
        "supportHold10d": 1 if support_hold else 0,
        "rebound5BeforeStop4_10d": 1 if rebound else 0,
        "breakdown10d": 1 if breakdown else 0,
    }


def build_rows_for_symbol(sym: str, max_rows: int = 520) -> list[dict[str, Any]]:
    df = _load_history(sym)
    if df is None or df.empty:
        return []
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.sort_values("time").reset_index(drop=True)
    if len(df) < 180:
        return []
    ind = _compute_indicators(df.copy())
    rows: list[dict[str, Any]] = []
    start = max(90, len(df) - max_rows - 12)
    end = len(df) - 11
    for i in range(start, end):
        hist = df.iloc[: i + 1].copy()
        last = hist.iloc[-1]
        price = n(last.close)
        if not price:
            continue
        try:
            rs = calc_rs_levels_only(price, n(last.open), n(last.open), n(last.high), n(last.low), price, hist)
        except Exception:
            continue
        rowi = ind.iloc[i]
        support = n(rs.get("activeSupportDay") or rs.get("supportDay"))
        resistance = n(rs.get("activeResistanceDay") or rs.get("resistanceDay"))
        support_zone = rs.get("supportZoneDay") if isinstance(rs.get("supportZoneDay"), list) else [support, support]
        ichi = ichimoku_state(hist)
        vwap = anchored_vwap_features(hist)
        smc = donchian_smart_money_structure(hist, 20)
        ma20 = n(rowi.get("ma20")); ma50 = n(rowi.get("ma50"))
        bb_upper = n(rowi.get("bbUpper")); bb_lower = n(rowi.get("bbLower"))
        macd_hist = n(rowi.get("histogram"))
        macd_hist_prev = n(ind.iloc[max(0, i - 3)].get("histogram"))
        rsi = n(rowi.get("rsi14"), 50)
        rsi_prev = n(ind.iloc[max(0, i - 5)].get("rsi14"), rsi)
        atr = n(rs.get("atr"), price * 0.03)
        labels = future_labels(df, i, support, price, 10)
        if not labels:
            continue
        feat = {
            "symbol": sym,
            "date": str(last.time.date()),
            "price": round(price, 4),
            "support": round(support, 4),
            "resistance": round(resistance, 4),
            "distanceToSupportPct": pct(price, support) if support else 0,
            "distanceToResistancePct": pct(resistance, price) if resistance else 0,
            "supportZoneWidthPct": pct(n(support_zone[-1]), n(support_zone[0])) if n(support_zone[0]) else 0,
            "rsi14": rsi,
            "rsiSlope5": rsi - rsi_prev,
            "macdHist": macd_hist,
            "macdHistSlope3": macd_hist - macd_hist_prev,
            "bbPercent": n(rowi.get("bbPercent"), 0.5),
            "bbWidthPct": pct(bb_upper, bb_lower) if bb_lower else 0,
            "adx14": n(rowi.get("adx14")),
            "plusMinusDiDiff": n(rowi.get("plusDi")) - n(rowi.get("minusDi")),
            "ma20DistancePct": pct(price, ma20) if ma20 else 0,
            "ma50DistancePct": pct(price, ma50) if ma50 else 0,
            "atrPct": atr / price * 100 if price else 0,
            "volumeRatio": n(rowi.get("volumeRatio"), 1),
            "roc20": pct(price, n(df.iloc[i - 20].close)) if i >= 20 else 0,
            "cloudDistancePct": ichi["cloudDistancePct"],
            "cloudThicknessPct": ichi["cloudThicknessPct"],
            "cloudStateNum": ichi["cloudStateNum"],
            "vwapDistancePct": pct(price, n(vwap.get("vwap"))) if vwap.get("available") and n(vwap.get("vwap")) else 0,
            "vwapSlopePct5": n(vwap.get("vwapSlopePct5")),
            "vwapZ": n(vwap.get("vwapZ")),
            "donchianPositionPct": n(smc.get("positionPct"), 50),
            "donchianZoneNum": -1 if smc.get("zone") == "discount" else 1 if smc.get("zone") == "premium" else 0,
            "liquiditySweepLow": 1 if smc.get("liquiditySweepLow") else 0,
            "liquiditySweepHigh": 1 if smc.get("liquiditySweepHigh") else 0,
        }
        feat.update(labels)
        rows.append(feat)
    return rows


def main():
    all_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for sym in [str(x).upper() for x in TECHNICAL_UNIVERSE if str(x).strip()]:
        try:
            rows = build_rows_for_symbol(sym)
            all_rows.extend(rows)
            print(sym, "rows", len(rows), flush=True)
        except Exception as exc:
            errors.append({"symbol": sym, "error": repr(exc)})
            print(sym, "ERR", repr(exc), flush=True)
    df = pd.DataFrame(all_rows)
    if not df.empty:
        cols = ["symbol", "date", "price", "support", "resistance"] + FEATURE_COLUMNS + ["return10d", "maxReturn10d", "maxDrawdown10d", "supportHold10d", "rebound5BeforeStop4_10d", "breakdown10d"]
        df = df[[c for c in cols if c in df.columns]]
        df.to_csv(OUT, index=False, encoding="utf-8")
    meta = {"createdAt": datetime.now().isoformat(), "rows": int(len(df)), "symbols": int(df.symbol.nunique()) if not df.empty else 0, "errors": errors, "featureColumns": FEATURE_COLUMNS}
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
