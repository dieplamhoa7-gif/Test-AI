from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import math
import pickle

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "distanceToSupportPct",
    "distanceToResistancePct",
    "supportZoneWidthPct",
    "rsi14",
    "rsiSlope5",
    "macdHist",
    "macdHistSlope3",
    "bbPercent",
    "bbWidthPct",
    "adx14",
    "plusMinusDiDiff",
    "ma20DistancePct",
    "ma50DistancePct",
    "atrPct",
    "volumeRatio",
    "roc20",
    "cloudDistancePct",
    "cloudThicknessPct",
    "cloudStateNum",
    "vwapDistancePct",
    "vwapSlopePct5",
    "vwapZ",
    "donchianPositionPct",
    "donchianZoneNum",
    "liquiditySweepLow",
    "liquiditySweepHigh",
]


def _num(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except Exception:
        return default


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -35, 35)
    return 1.0 / (1.0 + np.exp(-z))


@dataclass
class StandardScalerLite:
    mean_: np.ndarray
    scale_: np.ndarray

    @classmethod
    def fit(cls, x: np.ndarray) -> "StandardScalerLite":
        mean = np.nanmean(x, axis=0)
        scale = np.nanstd(x, axis=0)
        scale = np.where(scale < 1e-9, 1.0, scale)
        return cls(mean, scale)

    def transform(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        x = np.where(np.isfinite(x), x, self.mean_)
        return (x - self.mean_) / self.scale_


@dataclass
class LogisticModelLite:
    feature_columns: list[str]
    scaler: StandardScalerLite
    weights: np.ndarray
    bias: float
    train_meta: dict[str, Any]

    def predict_proba(self, rows: list[dict[str, Any]] | pd.DataFrame) -> np.ndarray:
        if isinstance(rows, pd.DataFrame):
            x = rows[self.feature_columns].to_numpy(dtype=float)
        else:
            x = np.array([[_num(r.get(c)) for c in self.feature_columns] for r in rows], dtype=float)
        xs = self.scaler.transform(x)
        return _sigmoid(xs @ self.weights + self.bias)

    def top_drivers(self, row: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
        x = np.array([[_num(row.get(c)) for c in self.feature_columns]], dtype=float)
        xs = self.scaler.transform(x)[0]
        contrib = xs * self.weights
        order = np.argsort(np.abs(contrib))[::-1][:limit]
        return [
            {"feature": self.feature_columns[int(i)], "contribution": round(float(contrib[int(i)]), 4), "value": round(_num(row.get(self.feature_columns[int(i)])), 4)}
            for i in order
        ]


def train_logistic_gd(df: pd.DataFrame, target: str, *, l2: float = 0.03, lr: float = 0.05, epochs: int = 1200) -> LogisticModelLite:
    work = df.dropna(subset=[target]).copy()
    x = work[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=float)
    y = work[target].astype(float).to_numpy()
    scaler = StandardScalerLite.fit(x)
    xs = scaler.transform(x)
    w = np.zeros(xs.shape[1], dtype=float)
    b = 0.0
    n = max(1, len(y))
    for _ in range(epochs):
        p = _sigmoid(xs @ w + b)
        err = p - y
        grad_w = (xs.T @ err) / n + l2 * w
        grad_b = float(err.mean())
        w -= lr * grad_w
        b -= lr * grad_b
    pred = _sigmoid(xs @ w + b)
    acc = float(((pred >= 0.5) == (y >= 0.5)).mean()) if len(y) else 0.0
    brier = float(np.mean((pred - y) ** 2)) if len(y) else 0.0
    meta = {
        "target": target,
        "rows": int(len(y)),
        "positiveRate": round(float(y.mean()), 4) if len(y) else None,
        "trainAccuracyInSample": round(acc, 4),
        "trainBrierInSample": round(brier, 4),
        "model": "LogisticModelLite gradient descent; local baseline only",
    }
    return LogisticModelLite(FEATURE_COLUMNS, scaler, w, b, meta)


def save_model(model: LogisticModelLite, path: str) -> None:
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load_model(path: str) -> LogisticModelLite:
    with open(path, "rb") as f:
        return pickle.load(f)
