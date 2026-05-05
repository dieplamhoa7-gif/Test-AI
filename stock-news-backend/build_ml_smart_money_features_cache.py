from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.market_data import _load_history
from app.ml_smart_money_features import build_ml_features
from app.technical_filters import TECHNICAL_UNIVERSE

OUT = Path("data/ml_smart_money_features_cache.json")
TMP = Path("data/ml_smart_money_features_cache.partial.json")
SLEEP_EVERY = 18
SLEEP_SECONDS = 65
MIN_HISTORY = 90


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def save(path: Path, items, errors):
    payload = {
        "createdAt": datetime.now().isoformat(),
        "universe": "VN100 / TECHNICAL_UNIVERSE",
        "method": "Local ML feature cache: VWAP [YinYangAlgorithms-inspired] + ICT Donchian Smart Money Structure. Output-only, no frontend formulas/model.",
        "count": len(items),
        "errorCount": len(errors),
        "items": items,
        "errors": errors,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_symbol(sym: str):
    df = _load_history(sym)
    if df is None or df.empty:
        return None, "missing_history"
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.sort_values("time").reset_index(drop=True)
    if len(df) < MIN_HISTORY:
        return None, f"insufficient_history_{len(df)}"
    last = df.iloc[-1]
    features = build_ml_features(df)
    return {
        "symbol": sym,
        "date": str(last["time"].date()),
        "price": round(float(last["close"]), 2),
        "features": features,
    }, None


def main():
    partial = load_json(TMP, {})
    items = partial.get("items") or []
    errors = partial.get("errors") or []
    done = {x.get("symbol") for x in items} | {x.get("symbol") for x in errors}
    universe = [str(x).strip().upper() for x in TECHNICAL_UNIVERSE if str(x).strip()]
    calls = 0
    print("ML smart-money universe", len(universe), "already done", len(done), flush=True)
    for sym in universe:
        if sym in done:
            print(sym, "SKIP", flush=True)
            continue
        if calls and calls % SLEEP_EVERY == 0:
            print("sleep", SLEEP_SECONDS, "seconds for rate limit", flush=True)
            time.sleep(SLEEP_SECONDS)
        try:
            item, err = run_symbol(sym)
            calls += 1
            if item:
                items.append(item)
                f = item["features"]
                print(sym, "OK", f.get("mlFeatureScore"), f.get("vwapYinYang", {}).get("regime"), f.get("ictDonchian20", {}).get("structure"), flush=True)
            else:
                errors.append({"symbol": sym, "error": err})
                print(sym, "ERR", err, flush=True)
        except Exception as exc:
            errors.append({"symbol": sym, "error": repr(exc)})
            print(sym, "ERR", repr(exc), flush=True)
        save(TMP, items, errors)
    save(OUT, items, errors)
    print("saved", OUT, "count", len(items), "errors", len(errors), flush=True)


if __name__ == "__main__":
    main()
