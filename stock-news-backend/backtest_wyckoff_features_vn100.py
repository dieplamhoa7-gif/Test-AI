# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from wyckoff_features import snapshots_for_rows

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "vn100_history_from_2023.json"
OUT = ROOT / "data" / "wyckoff_feature_backtest_vn100.json"
HORIZONS = [3, 5, 10]
THRESHOLDS = [55, 65, 75]
TOPK = [20, 50, 100]
FEATURES = [
    "springScore",
    "upthrustScore",
    "sosScore",
    "sowScore",
    "dryTestScore",
    "absorptionScore",
    "distributionScore",
    "markupReadinessScore",
    "markdownReadinessScore",
    "rangeContinuationScore",
]


def load_symbols() -> dict:
    return (json.loads(DATA.read_text(encoding="utf-8")).get("symbols") or {})


def forward_stats(rows: list[dict], idx: int, horizon: int) -> dict:
    if idx + horizon >= len(rows):
        return {}
    close = float(rows[idx]["close"])
    fut = rows[idx + 1 : idx + horizon + 1]
    if close <= 0 or not fut:
        return {}
    end_close = float(fut[-1]["close"])
    highs = [float(r["high"]) for r in fut]
    lows = [float(r["low"]) for r in fut]
    ret = end_close / close - 1.0
    max_up = max(highs) / close - 1.0
    max_down = min(lows) / close - 1.0
    return {
        "ret": ret,
        "max_up": max_up,
        "max_down": max_down,
        "label_up": 1 if (ret > 0.03 and max_down > -0.05) else 0,
        "label_down": 1 if (ret < -0.03 or max_down < -0.06) else 0,
        "label_range": 1 if (abs(ret) < 0.02 and max_up < 0.04 and max_down > -0.04) else 0,
    }


def build_panel() -> list[dict]:
    panel = []
    for symbol, payload in load_symbols().items():
        rows = (payload or {}).get("rows") or []
        if len(rows) < 120:
            continue
        snaps = snapshots_for_rows(rows, symbol=symbol, lookback=60, min_bars=80)
        by_time = {str(r.get("time")): i for i, r in enumerate(rows)}
        for snap in snaps:
            t = str(snap.get("time"))
            idx = by_time.get(t)
            if idx is None:
                continue
            rec = {
                "symbol": symbol,
                "time": t,
                "close": float(snap.get("close") or 0),
                "bias": ((snap.get("scores") or {}).get("bias") or "neutral"),
            }
            scores = snap.get("scores") or {}
            for f in FEATURES:
                rec[f] = float(scores.get(f) or 0)
            ok = True
            for h in HORIZONS:
                fs = forward_stats(rows, idx, h)
                if not fs:
                    ok = False
                    break
                for k, v in fs.items():
                    rec[f"h{h}_{k}"] = v
            if ok:
                panel.append(rec)
    return panel


def summarize_subset(items: list[dict], horizon: int, mode: str) -> dict:
    if not items:
        return {"n": 0}
    rets = [x[f"h{horizon}_ret"] for x in items]
    wins = [r for r in rets if r > 0]
    if mode == "up":
        hit = [x[f"h{horizon}_label_up"] for x in items]
    elif mode == "down":
        hit = [x[f"h{horizon}_label_down"] for x in items]
    else:
        hit = [x[f"h{horizon}_label_range"] for x in items]
    return {
        "n": len(items),
        "avgRetPct": round(mean(rets) * 100, 2),
        "medianRetPct": round(sorted(rets)[len(rets)//2] * 100, 2),
        "winRatePct": round(len(wins) / len(items) * 100, 2),
        "hitRatePct": round(mean(hit) * 100, 2),
        "avgMaxUpPct": round(mean(x[f"h{horizon}_max_up"] for x in items) * 100, 2),
        "avgMaxDownPct": round(mean(x[f"h{horizon}_max_down"] for x in items) * 100, 2),
    }


def evaluate_thresholds(panel: list[dict]) -> dict:
    out = {}
    for feat in FEATURES:
        out[feat] = {}
        direction = "down" if feat in {"upthrustScore", "sowScore", "distributionScore", "markdownReadinessScore"} else ("range" if feat == "rangeContinuationScore" else "up")
        for horizon in HORIZONS:
            out[feat][f"h{horizon}"] = {}
            for th in THRESHOLDS:
                subset = [x for x in panel if x[feat] >= th]
                out[feat][f"h{horizon}"][f">={th}"] = summarize_subset(subset, horizon, direction)
    return out


def evaluate_topk(panel: list[dict]) -> dict:
    out = {}
    for feat in FEATURES:
        out[feat] = {}
        reverse = True
        direction = "down" if feat in {"upthrustScore", "sowScore", "distributionScore", "markdownReadinessScore"} else ("range" if feat == "rangeContinuationScore" else "up")
        for horizon in HORIZONS:
            out[feat][f"h{horizon}"] = {}
            ranked = sorted(panel, key=lambda x: x[feat], reverse=reverse)
            for k in TOPK:
                subset = ranked[: min(k, len(ranked))]
                out[feat][f"h{horizon}"][f"top{k}"] = summarize_subset(subset, horizon, direction)
    return out


def bias_summary(panel: list[dict]) -> dict:
    out = {}
    for b in ["markup", "markdown", "range", "neutral"]:
        items = [x for x in panel if x["bias"] == b]
        out[b] = {f"h{h}": summarize_subset(items, h, "up" if b == "markup" else ("down" if b == "markdown" else "range")) for h in HORIZONS}
    return out


def pick_highlights(results: dict) -> dict:
    highlights = {"up": [], "down": [], "range": []}
    for feat in FEATURES:
        direction = "down" if feat in {"upthrustScore", "sowScore", "distributionScore", "markdownReadinessScore"} else ("range" if feat == "rangeContinuationScore" else "up")
        for horizon in HORIZONS:
            for bucket, stat in (results["thresholds"][feat][f"h{horizon}"]).items():
                if stat.get("n", 0) >= 30:
                    highlights[direction].append({"feature": feat, "horizon": horizon, "bucket": bucket, **stat})
            for bucket, stat in (results["topk"][feat][f"h{horizon}"]).items():
                if stat.get("n", 0) >= 20:
                    highlights[direction].append({"feature": feat, "horizon": horizon, "bucket": bucket, **stat})
    highlights["up"] = sorted(highlights["up"], key=lambda x: (x["hitRatePct"], x["avgRetPct"]), reverse=True)[:12]
    highlights["down"] = sorted(highlights["down"], key=lambda x: (x["hitRatePct"], -x["avgRetPct"]), reverse=True)[:12]
    highlights["range"] = sorted(highlights["range"], key=lambda x: (x["hitRatePct"], -abs(x["avgRetPct"])), reverse=True)[:12]
    return highlights


def main() -> None:
    panel = build_panel()
    results = {
        "rows": len(panel),
        "thresholds": evaluate_thresholds(panel),
        "topk": evaluate_topk(panel),
        "biasSummary": bias_summary(panel),
    }
    results["highlights"] = pick_highlights(results)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "rows": results["rows"],
        "output": str(OUT),
        "upTop": results["highlights"]["up"][:3],
        "downTop": results["highlights"]["down"][:3],
        "rangeTop": results["highlights"]["range"][:3],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
