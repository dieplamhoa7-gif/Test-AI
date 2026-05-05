from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.market_data import _load_history, _compute_indicators
from app.ml_smart_money_features import anchored_vwap_features, donchian_smart_money_structure
from app.ml_support_model import load_model, FEATURE_COLUMNS
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE
from build_ml_support_dataset import n, pct, ichimoku_state

MODEL_SUPPORT = Path("models/support_hold_model.pkl")
MODEL_REBOUND = Path("models/support_rebound_model.pkl")
OUT = Path("data/ml_predictions_cache.json")
PUBLIC_OUT = Path("firebase_public/data/ml_predictions_cache.json")
OUT.parent.mkdir(parents=True, exist_ok=True)
PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)


RS_CACHE = Path("data/rs_levels_vn100_cache.json")
IND_CACHE = Path("data/v3_full_indicator_cache_v2.json")


def load_cache_items(path: Path) -> dict[str, dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {str(x.get("symbol") or "").upper(): x for x in data.get("items", []) if isinstance(x, dict)}
    except Exception:
        return {}


def build_today_features(sym: str, rs_by_symbol: dict[str, dict[str, Any]], ind_by_symbol: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    rs = rs_by_symbol.get(sym) or {}
    ind_row = ind_by_symbol.get(sym) or {}
    indicators = ind_row.get("indicators") if isinstance(ind_row.get("indicators"), dict) else {}
    price = n(rs.get("price") or ind_row.get("price"))
    if not price:
        return None
    support = n(rs.get("activeSupportDay") or rs.get("supportDay")); resistance = n(rs.get("activeResistanceDay") or rs.get("resistanceDay"))
    support_zone = rs.get("supportZoneDay") if isinstance(rs.get("supportZoneDay"), list) else [support, support]
    ichi_raw = indicators.get("ichimoku") if isinstance(indicators.get("ichimoku"), dict) else {}
    cloud_top = n(ichi_raw.get("cloudTop")); cloud_bottom = n(ichi_raw.get("cloudBottom")); ichi_state = str(ichi_raw.get("state") or "")
    ichi = {"cloudStateNum": 1 if ichi_state == "above_cloud" else -1 if ichi_state == "below_cloud" else 0, "cloudDistancePct": pct(price, cloud_top) if ichi_state == "above_cloud" and cloud_top else pct(price, cloud_bottom) if ichi_state == "below_cloud" and cloud_bottom else 0, "cloudThicknessPct": pct(cloud_top, cloud_bottom) if cloud_bottom else 0}
    vwap_raw = indicators.get("mlSmartMoney", {}).get("vwapYinYang") if isinstance(indicators.get("mlSmartMoney"), dict) else None
    smc_raw = indicators.get("mlSmartMoney", {}).get("ictDonchian20") if isinstance(indicators.get("mlSmartMoney"), dict) else None
    if not vwap_raw or not smc_raw:
        # Fallback to light values from indicator/RS cache only; no API fetch.
        vwap_raw = {"vwap": rs.get("vwapDay"), "vwapSlopePct5": 0, "vwapZ": 0, "regime": "unknown"}
        smc_raw = {"positionPct": 50, "zone": "equilibrium", "structure": rs.get("marketStructureDay") or "range", "liquiditySweepLow": False, "liquiditySweepHigh": False}
    ma20 = n(indicators.get("ma20") or rs.get("ma20Anchor")); ma50 = n(indicators.get("ma50") or rs.get("ma50Anchor")); bb_upper = n(indicators.get("bbUpper")); bb_lower = n(indicators.get("bbLower"))
    macd_hist = n(indicators.get("histogram")); macd_hist_prev = macd_hist
    rsi = n(indicators.get("rsi14"), 50); rsi_prev = rsi
    atr = n(rs.get("atr"), price * 0.03)
    feat = {
        "symbol": sym, "date": str(rs.get('date') or ind_row.get('date') or ''), "price": round(price, 4), "support": round(support, 4), "resistance": round(resistance, 4),
        "distanceToSupportPct": pct(price, support) if support else 0,
        "distanceToResistancePct": pct(resistance, price) if resistance else 0,
        "supportZoneWidthPct": pct(n(support_zone[-1]), n(support_zone[0])) if n(support_zone[0]) else 0,
        "rsi14": rsi, "rsiSlope5": rsi - rsi_prev, "macdHist": macd_hist, "macdHistSlope3": macd_hist - macd_hist_prev,
        "bbPercent": n(indicators.get("bbPercent"), 0.5), "bbWidthPct": pct(bb_upper, bb_lower) if bb_lower else 0,
        "adx14": n(indicators.get("adx14")), "plusMinusDiDiff": n(indicators.get("plusDi")) - n(indicators.get("minusDi")),
        "ma20DistancePct": pct(price, ma20) if ma20 else 0, "ma50DistancePct": pct(price, ma50) if ma50 else 0,
        "atrPct": atr / price * 100 if price else 0, "volumeRatio": n(indicators.get("volumeRatio"), 1), "roc20": 0,
        "cloudDistancePct": ichi["cloudDistancePct"], "cloudThicknessPct": ichi["cloudThicknessPct"], "cloudStateNum": ichi["cloudStateNum"],
        "vwapDistancePct": pct(price, n(vwap_raw.get("vwap"))) if n(vwap_raw.get("vwap")) else 0,
        "vwapSlopePct5": n(vwap_raw.get("vwapSlopePct5")), "vwapZ": n(vwap_raw.get("vwapZ")),
        "donchianPositionPct": n(smc_raw.get("positionPct"), 50), "donchianZoneNum": -1 if smc_raw.get("zone") == "discount" else 1 if smc_raw.get("zone") == "premium" else 0,
        "liquiditySweepLow": 1 if smc_raw.get("liquiditySweepLow") else 0, "liquiditySweepHigh": 1 if smc_raw.get("liquiditySweepHigh") else 0,
        "vwapRegime": vwap_raw.get("regime"), "smartMoneyStructure": smc_raw.get("structure"), "smartMoneyZone": smc_raw.get("zone"),
    }
    return feat


def confidence(p1: float, p2: float) -> str:
    edge = abs(p1 - 0.5) + abs(p2 - 0.5)
    return "high" if edge >= 0.45 else "medium" if edge >= 0.25 else "low"


def main():
    support_model = load_model(str(MODEL_SUPPORT))
    rebound_model = load_model(str(MODEL_REBOUND))
    items = []
    errors = []
    rs_by_symbol = load_cache_items(RS_CACHE)
    ind_by_symbol = load_cache_items(IND_CACHE)
    universe = list(rs_by_symbol.keys()) or [str(x).upper() for x in TECHNICAL_UNIVERSE if str(x).strip()]
    for sym in universe:
        try:
            feat = build_today_features(sym, rs_by_symbol, ind_by_symbol)
            if not feat:
                errors.append({"symbol": sym, "error": "missing_features"}); continue
            p_hold = float(support_model.predict_proba([feat])[0])
            p_rebound = float(rebound_model.predict_proba([feat])[0])
            breakdown = 1.0 - p_hold
            ml_score = round((p_hold * 0.45 + p_rebound * 0.45 + max(0, min(1, (feat.get("distanceToResistancePct", 0) / max(feat.get("distanceToSupportPct", 0.01), 0.01))) ) * 0.10) * 100, 2)
            drivers = support_model.top_drivers(feat, 3) + rebound_model.top_drivers(feat, 3)
            items.append({
                "symbol": sym, "date": feat["date"], "price": feat["price"], "support": feat["support"], "resistance": feat["resistance"],
                "supportHoldProb": round(p_hold, 4), "reboundProb10d": round(p_rebound, 4), "breakdownRisk10d": round(breakdown, 4),
                "mlScore": ml_score, "confidence": confidence(p_hold, p_rebound), "topDrivers": drivers,
                "context": {"vwapRegime": feat.get("vwapRegime"), "smartMoneyStructure": feat.get("smartMoneyStructure"), "smartMoneyZone": feat.get("smartMoneyZone")},
            })
            print(sym, ml_score, round(p_hold, 3), round(p_rebound, 3), flush=True)
        except Exception as exc:
            errors.append({"symbol": sym, "error": repr(exc)})
            print(sym, "ERR", repr(exc), flush=True)
    items.sort(key=lambda x: x.get("mlScore", 0), reverse=True)
    payload = {"createdAt": datetime.now().isoformat(), "method": "Local baseline Support Hold/Rebound ML predictions; output-only.", "count": len(items), "errorCount": len(errors), "items": items, "errors": errors}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUT), "count": len(items), "errors": len(errors), "top": [(x['symbol'], x['mlScore']) for x in items[:10]]}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
