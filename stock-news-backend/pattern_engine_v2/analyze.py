"""
analyze.py — Bộ não trung tâm của engine (tái dựng 08/07/2026).
Pipeline: load -> timeframe -> config -> indicators -> pivots -> detect -> rank -> forecast.
"""
from __future__ import annotations
from datetime import datetime, timezone

from .core import load_data, add_indicators, find_pivots, infer_timeframe, HAS_TALIB, HAS_SCIPY
from .config import build_config
from .candlesticks import detect_candlesticks
from . import chart_patterns as cp
from . import experimental as ex
from .peak_bottom_v2 import detect_double_triple_v2
from .forecast import forecast, build_scenarios
from .classify import classify_and_rank, make_bias


def detect_all(df, pivots, cfg, include_experimental=True):
    P = []
    P += detect_candlesticks(df, recent_bars=cfg.recent_candles)
    P += cp.support_resistance(df, pivots)
    P += cp.trendlines(df, pivots)
    P += cp.double_patterns(df, pivots, max_span=cfg.double_max_span,
                            target_max_move=cfg.target_max_move)
    P += detect_double_triple_v2(df, pivots, recent_bars=max(160, cfg.recent_signals * 4),
                                 max_span=max(cfg.double_max_span, 160))
    P += cp.head_shoulders(df, pivots)
    P += cp.triangle_wedge_channel(df, pivots, lookback=cfg.lb_triangle)
    P += cp.darvas_box(df, lookback=cfg.lb_darvas)
    P += cp.cup_handle(df, pivots, lookback=cfg.lb_cup)
    P += cp.rounding(df, lookback=cfg.lb_rounding)
    P += cp.flags(df, pole=cfg.flag_pole, flag_max=cfg.flag_max)
    P += cp.spring_upthrust(df, pivots, lookback=cfg.lb_smc)
    P += cp.gaps(df, recent_bars=cfg.recent_signals + 5)
    P += cp.vsa_signals(df, recent_bars=cfg.recent_signals)
    P += cp.indicator_patterns(df, pivots, lookback=cfg.lb_triangle)
    if include_experimental:
        P += ex.harmonic(df, pivots)
        P += ex.elliott(df, pivots)
        P += ex.smart_money(df, pivots, lookback=cfg.lb_smc)
        P += ex.wyckoff(df, lookback=cfg.lb_darvas)
    return P


def analyze(csv_or_df, symbol="STOCK", include_experimental=True):
    if hasattr(csv_or_df, "columns"):
        df = csv_or_df.copy()
    else:
        df = load_data(csv_or_df)

    tf = infer_timeframe(df)
    cfg = build_config(tf, len(df))
    df = add_indicators(df)
    pivots = find_pivots(df, distance=cfg.pivot_distance, prom_mult=cfg.pivot_prom_mult)

    raw = detect_all(df, pivots, cfg, include_experimental)
    ranked, conflicts, extra = classify_and_rank(raw, df)
    bias, bull_w, bear_w, strength = make_bias(ranked)

    fc = forecast(df, horizon=cfg.fc_horizon, fit_window=cfg.fc_fit_window)
    scenarios = build_scenarios(df, ranked, fc)

    close = round(float(df["close"].iloc[-1]), 2)
    primary = [p for p in ranked if p.get("role") == "primary"]
    supporting = [p for p in ranked if p.get("role") == "supporting"]

    sups = sorted({round(p["levels"]["support"], 2) for p in ranked
                   if p.get("levels", {}).get("support") and p["levels"]["support"] < close},
                  reverse=True)
    ress = sorted({round(p["levels"]["resistance"], 2) for p in ranked
                   if p.get("levels", {}).get("resistance") and p["levels"]["resistance"] > close})

    result = {
        "symbol": symbol,
        "timeframe": tf,
        "bars": len(df),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "period": [df["date"].iloc[0].strftime("%Y-%m-%d"), df["date"].iloc[-1].strftime("%Y-%m-%d")],
        "lastClose": close,
        "engineFlags": {"talib": HAS_TALIB, "scipy": HAS_SCIPY},
        "config": {
            "pivotDistance": cfg.pivot_distance, "lbTriangle": cfg.lb_triangle,
            "lbCup": cfg.lb_cup, "fcHorizon": cfg.fc_horizon, "notes": cfg.notes,
        },
        "patterns": [_clean(p) for p in ranked],
        "forecast": {**fc, "scenarios": scenarios},
        "summary": {
            "bias": bias, "biasStrength": strength,
            "bullScore": bull_w, "bearScore": bear_w,
            "primarySignals": [_brief(p) for p in primary],
            "supportingSignals": [_brief(p) for p in supporting[:6]],
            "conflicts": conflicts,
            "keyLevels": {"supports": sups[:4], "resistances": ress[:4]},
            "note": "Research-only, not financial advice",
        },
        "_df": df, "_pivots": pivots, "_ranked": ranked, "_fc": fc,
        "_scenarios": scenarios, "_cfg": cfg,
    }
    return result


def _clean(p):
    return {k: v for k, v in p.items() if not k.startswith("_")}


def _brief(p):
    lv = p.get("levels", {})
    return {
        "type": p["type"], "direction": p["direction"], "role": p.get("role"),
        "tier": p.get("tier"), "confidence": p["confidence"],
        "score": p["score"], "composite": p.get("_composite_final"),
        "status": p["status"], "target": lv.get("target"),
        "note": p.get("evidence", {}).get("notes", ""),
    }
