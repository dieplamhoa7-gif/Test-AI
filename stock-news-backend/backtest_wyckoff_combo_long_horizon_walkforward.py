# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from wyckoff_features import snapshots_for_rows

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "vn100_history_from_2023.json"
OUT = ROOT / "data" / "wyckoff_combo_long_horizon_walkforward.json"
HORIZONS = [10, 20, 40]
MIN_ROWS = 120
TRAIN_MIN = 18000
TEST_MIN = 6000
SPLITS = ["2024-01-01", "2024-07-01", "2025-01-01", "2025-07-01", "2026-01-01"]
BASE_FEATURES = [
    "springScore", "upthrustScore", "sosScore", "sowScore", "dryTestScore",
    "absorptionScore", "distributionScore", "markupReadinessScore",
    "markdownReadinessScore", "rangeContinuationScore",
    "close_pos", "vol_rel20", "range_rel20", "ret_1d", "ret_3d", "ret_5d",
    "range_width_pct",
]
COMBO_FEATURES = BASE_FEATURES + [
    "rsi14", "rsi14_slope3", "atr14_pct", "atr14_slope3", "vol_z20", "vol_slope3"
]


def load_symbols() -> dict:
    return (json.loads(DATA.read_text(encoding='utf-8')).get('symbols') or {})


def forward_stats(rows: list[dict], idx: int, horizon: int) -> dict:
    if idx + horizon >= len(rows):
        return {}
    close = float(rows[idx]['close'])
    fut = rows[idx + 1: idx + horizon + 1]
    if close <= 0 or not fut:
        return {}
    end_close = float(fut[-1]['close'])
    highs = [float(r['high']) for r in fut]
    lows = [float(r['low']) for r in fut]
    ret = end_close / close - 1.0
    max_up = max(highs) / close - 1.0
    max_down = min(lows) / close - 1.0
    return {
        'ret': ret,
        'max_up': max_up,
        'max_down': max_down,
        'label_markup': 1 if (ret > 0.06 and max_down > -0.06) else 0,
        'label_markdown': 1 if (ret < -0.06 or max_down < -0.08) else 0,
        'label_range': 1 if (abs(ret) < 0.03 and max_up < 0.05 and max_down > -0.05) else 0,
    }


def enrich_rows(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows).copy()
    for c in ['open', 'high', 'low', 'close', 'volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.sort_values('time').reset_index(drop=True)
    df['rsi14'] = RSIIndicator(df['close'], window=14).rsi()
    df['rsi14_slope3'] = df['rsi14'] - df['rsi14'].shift(3)
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    df['atr14_pct'] = atr / df['close']
    df['atr14_slope3'] = df['atr14_pct'] - df['atr14_pct'].shift(3)
    vma20 = df['volume'].rolling(20).mean()
    vstd20 = df['volume'].rolling(20).std()
    df['vol_z20'] = (df['volume'] - vma20) / vstd20.replace(0, np.nan)
    df['vol_slope3'] = (df['volume'] / vma20.replace(0, np.nan)) - (df['volume'].shift(3) / vma20.shift(3).replace(0, np.nan))
    return df


def build_panel() -> list[dict]:
    panel = []
    for symbol, payload in load_symbols().items():
        rows = (payload or {}).get('rows') or []
        if len(rows) < MIN_ROWS:
            continue
        df = enrich_rows(rows)
        snaps = snapshots_for_rows(rows, symbol=symbol, lookback=60, min_bars=80)
        by_time = {str(r.get('time')): i for i, r in enumerate(rows)}
        for snap in snaps:
            t = str(snap.get('time'))
            idx = by_time.get(t)
            if idx is None:
                continue
            bar = snap.get('bar') or {}
            tr = snap.get('range') or {}
            scores = snap.get('scores') or {}
            rec = {
                'symbol': symbol,
                'time': t,
                'bias': scores.get('bias') or 'neutral',
                'close_pos': float(bar.get('close_pos') or 0),
                'vol_rel20': float(bar.get('vol_rel20') or 0),
                'range_rel20': float(bar.get('range_rel20') or 0),
                'ret_1d': float(bar.get('ret_1d') or 0),
                'ret_3d': float(bar.get('ret_3d') or 0),
                'ret_5d': float(bar.get('ret_5d') or 0),
                'range_width_pct': float(tr.get('width_pct') or 0),
                'rsi14': float(df.iloc[idx].get('rsi14') or 0),
                'rsi14_slope3': float(df.iloc[idx].get('rsi14_slope3') or 0),
                'atr14_pct': float(df.iloc[idx].get('atr14_pct') or 0),
                'atr14_slope3': float(df.iloc[idx].get('atr14_slope3') or 0),
                'vol_z20': float(df.iloc[idx].get('vol_z20') or 0),
                'vol_slope3': float(df.iloc[idx].get('vol_slope3') or 0),
            }
            for f in [
                'springScore','upthrustScore','sosScore','sowScore','dryTestScore',
                'absorptionScore','distributionScore','markupReadinessScore',
                'markdownReadinessScore','rangeContinuationScore'
            ]:
                rec[f] = float(scores.get(f) or 0)
            ok = True
            for h in HORIZONS:
                fs = forward_stats(rows, idx, h)
                if not fs:
                    ok = False
                    break
                for k, v in fs.items():
                    rec[f'h{h}_{k}'] = v
            if ok:
                panel.append(rec)
    return sorted(panel, key=lambda x: (x['time'], x['symbol']))


def build_model() -> Pipeline:
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('logreg', LogisticRegression(max_iter=1200, class_weight='balanced')),
    ])


def eval_split(panel: list[dict], split_date: str, horizon: int, target: str, features: list[str]) -> dict:
    label_col = f'h{horizon}_{target}'
    train = [x for x in panel if x['time'] < split_date]
    test = [x for x in panel if x['time'] >= split_date]
    if len(train) < TRAIN_MIN or len(test) < TEST_MIN:
        return {'split': split_date, 'skipped': 'insufficient_rows', 'trainRows': len(train), 'testRows': len(test)}
    Xtr = np.array([[x.get(f, 0.0) for f in features] for x in train], dtype=float)
    ytr = np.array([int(x[label_col]) for x in train], dtype=int)
    Xte = np.array([[x.get(f, 0.0) for f in features] for x in test], dtype=float)
    yte = np.array([int(x[label_col]) for x in test], dtype=int)
    if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
        return {'split': split_date, 'skipped': 'single_class', 'trainRows': len(train), 'testRows': len(test)}
    model = build_model()
    model.fit(Xtr, ytr)
    ptr = model.predict_proba(Xtr)[:, 1]
    pte = model.predict_proba(Xte)[:, 1]
    pred = (pte >= 0.5).astype(int)
    lr = model.named_steps['logreg']
    coefs = {f: round(float(c), 4) for f, c in zip(features, lr.coef_[0])}
    top_long = sorted(coefs.items(), key=lambda kv: kv[1], reverse=True)[:8]
    top_short = sorted(coefs.items(), key=lambda kv: kv[1])[:8]
    order = np.argsort(-pte)
    rank_stats = {}
    for k in [50, 100, 300]:
        kk = min(k, len(order))
        idxs = order[:kk]
        items = [test[i] for i in idxs]
        rank_stats[f'top{kk}'] = {
            'n': kk,
            'avgRetPct': round(mean(x[f'h{horizon}_ret'] for x in items) * 100, 2),
            'hitRatePct': round(mean(int(x[label_col]) for x in items) * 100, 2),
            'avgMaxUpPct': round(mean(x[f'h{horizon}_max_up'] for x in items) * 100, 2),
            'avgMaxDownPct': round(mean(x[f'h{horizon}_max_down'] for x in items) * 100, 2),
        }
    return {
        'split': split_date,
        'trainRows': len(train),
        'testRows': len(test),
        'trainPositiveRatePct': round(float(ytr.mean() * 100), 2),
        'testPositiveRatePct': round(float(yte.mean() * 100), 2),
        'trainAUC': round(float(roc_auc_score(ytr, ptr)), 4),
        'testAUC': round(float(roc_auc_score(yte, pte)), 4),
        'precision': round(float(precision_score(yte, pred, zero_division=0)), 4),
        'recall': round(float(recall_score(yte, pred, zero_division=0)), 4),
        'f1': round(float(f1_score(yte, pred, zero_division=0)), 4),
        'topPositiveFeatures': top_long,
        'topNegativeFeatures': top_short,
        'rankedOOS': rank_stats,
    }


def aggregate(valid_splits: list[dict]) -> dict:
    if not valid_splits:
        return {'nSplits': 0}
    keys = ['trainAUC', 'testAUC', 'precision', 'recall', 'f1']
    out = {'nSplits': len(valid_splits)}
    for k in keys:
        vals = [s[k] for s in valid_splits if k in s]
        out[f'avg_{k}'] = round(float(mean(vals)), 4)
        out[f'min_{k}'] = round(float(min(vals)), 4)
        out[f'max_{k}'] = round(float(max(vals)), 4)
    return out


def run_family(panel: list[dict], features: list[str]) -> dict:
    result = {}
    for h in HORIZONS:
        result[f'h{h}'] = {}
        for target in ['label_markup', 'label_markdown', 'label_range']:
            splits = [eval_split(panel, s, h, target, features) for s in SPLITS]
            valid = [s for s in splits if 'testAUC' in s]
            result[f'h{h}'][target] = {'splits': splits, 'summary': aggregate(valid)}
    return result


def main() -> None:
    panel = build_panel()
    out = {
        'rows': len(panel),
        'baseFeatures': BASE_FEATURES,
        'comboFeatures': COMBO_FEATURES,
        'base': run_family(panel, BASE_FEATURES),
        'combo': run_family(panel, COMBO_FEATURES),
    }
    comparison = {}
    for h in HORIZONS:
        comparison[f'h{h}'] = {}
        for target in ['label_markup', 'label_markdown', 'label_range']:
            b = out['base'][f'h{h}'][target]['summary']
            c = out['combo'][f'h{h}'][target]['summary']
            comparison[f'h{h}'][target] = {
                'base_testAUC': b.get('avg_testAUC'),
                'combo_testAUC': c.get('avg_testAUC'),
                'delta_testAUC': round((c.get('avg_testAUC') or 0) - (b.get('avg_testAUC') or 0), 4),
                'base_f1': b.get('avg_f1'),
                'combo_f1': c.get('avg_f1'),
                'delta_f1': round((c.get('avg_f1') or 0) - (b.get('avg_f1') or 0), 4),
            }
    out['comparison'] = comparison
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'rows': len(panel), 'output': str(OUT), 'comparison': comparison}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
