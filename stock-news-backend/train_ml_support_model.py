from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.ml_support_model import train_logistic_gd, save_model, FEATURE_COLUMNS

DATASET = Path("data/ml/support_rebound_dataset.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)
MODEL_SUPPORT = MODEL_DIR / "support_hold_model.pkl"
MODEL_REBOUND = MODEL_DIR / "support_rebound_model.pkl"
REPORT = Path("data/ml/support_model_report.json")
REPORT.parent.mkdir(parents=True, exist_ok=True)


def temporal_metrics(df: pd.DataFrame, target: str, model_path: Path) -> dict:
    # Lightweight honest-ish split: train older 80%, test latest 20% by date.
    from app.ml_support_model import load_model
    model = load_model(str(model_path))
    d = df.dropna(subset=[target]).sort_values("date").copy()
    if len(d) < 50:
        return {"rows": len(d), "warning": "too_few_rows"}
    cut = int(len(d) * 0.8)
    test = d.iloc[cut:].copy()
    p = model.predict_proba(test)
    y = test[target].astype(float).to_numpy()
    acc = float(((p >= 0.5) == (y >= 0.5)).mean())
    brier = float(((p - y) ** 2).mean())
    return {"testRowsLatest20Pct": int(len(test)), "accuracy": round(acc, 4), "brier": round(brier, 4), "positiveRateTest": round(float(y.mean()), 4)}


def main():
    df = pd.read_csv(DATASET)
    for c in FEATURE_COLUMNS:
        if c not in df.columns:
            df[c] = 0
    support_model = train_logistic_gd(df, "supportHold10d")
    rebound_model = train_logistic_gd(df, "rebound5BeforeStop4_10d")
    save_model(support_model, str(MODEL_SUPPORT))
    save_model(rebound_model, str(MODEL_REBOUND))
    report = {
        "createdAt": datetime.now().isoformat(),
        "dataset": str(DATASET),
        "featureColumns": FEATURE_COLUMNS,
        "supportHoldModel": support_model.train_meta,
        "reboundModel": rebound_model.train_meta,
        "supportHoldLatest20Pct": temporal_metrics(df, "supportHold10d", MODEL_SUPPORT),
        "reboundLatest20Pct": temporal_metrics(df, "rebound5BeforeStop4_10d", MODEL_REBOUND),
        "note": "Local baseline ML. Use for probability/ranking support only; not standalone buy/sell advice.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
