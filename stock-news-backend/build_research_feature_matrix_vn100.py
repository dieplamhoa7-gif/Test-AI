#!/usr/bin/env python3
"""Build VN100 research feature matrix for LH Investment quant training.

MIT finance skill principles:
- features at date t use only data up to t;
- future returns are labels only;
- chronological data; no random split;
- output JSON for downstream regression/PCA/backtest.

Inputs:
  data/vn100_history_from_2023.json
  data/chart_patterns_cache.json (latest snapshot merged as current pattern context)

Outputs:
  data/research_feature_matrix_vn100.json
  firebase_public/data/research_feature_matrix_vn100.json
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PUBLIC_DATA = ROOT / "firebase_public" / "data"


def r(x: Any, nd: int = 4) -> Any:
    try:
        if x is None or pd.isna(x) or math.isinf(float(x)):
            return None
        return round(float(x), nd)
    except Exception:
        return None


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev).abs(),
        (df["low"] - prev).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False, min_periods=n).mean()


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    c = df["close"]
    df["ret5"] = c.pct_change(5)
    df["ret20"] = c.pct_change(20)
    df["ret60"] = c.pct_change(60)
    df["sma20"] = c.rolling(20).mean()
    df["sma50"] = c.rolling(50).mean()
    df["sma200"] = c.rolling(200).mean()
    df["ma20Slope20"] = df["sma20"].pct_change(20)
    df["ma50Slope20"] = df["sma50"].pct_change(20)
    df["priceVsMa20Pct"] = c / df["sma20"] - 1
    df["priceVsMa50Pct"] = c / df["sma50"] - 1
    df["rsi14"] = rsi(c, 14)
    df["ema12"] = ema(c, 12)
    df["ema26"] = ema(c, 26)
    df["macd"] = df["ema12"] - df["ema26"]
    df["macdSignal"] = ema(df["macd"], 9)
    df["macdHist"] = df["macd"] - df["macdSignal"]
    df["macdHistSlope3"] = df["macdHist"] - df["macdHist"].shift(3)
    df["atr14"] = atr(df, 14)
    df["atrPct"] = df["atr14"] / c
    df["realizedVol20"] = df["close"].pct_change().rolling(20).std() * (252 ** 0.5)
    df["volMa20"] = df["volume"].rolling(20).mean()
    df["volumeRatio20"] = df["volume"] / df["volMa20"]
    # Bollinger width
    std20 = c.rolling(20).std()
    df["bbWidth20"] = (4 * std20) / df["sma20"]
    # Future labels (not features)
    for h in [5, 10, 20, 60]:
        df[f"futureReturn{h}d"] = c.shift(-h) / c - 1
        future_min = pd.concat([c.shift(-i) for i in range(1, h+1)], axis=1).min(axis=1)
        future_max = pd.concat([c.shift(-i) for i in range(1, h+1)], axis=1).max(axis=1)
        df[f"futureMaxDrawdown{h}d"] = future_min / c - 1
        df[f"futureMaxRunup{h}d"] = future_max / c - 1
    return df


def market_regime(row: pd.Series) -> str:
    if pd.isna(row.get("sma50")) or pd.isna(row.get("sma200")):
        return "unknown"
    if row["close"] > row["sma50"] > row["sma200"]:
        return "bullish"
    if row["close"] < row["sma50"] < row["sma200"]:
        return "bearish"
    return "sideway"


def vol_regime(atr_pct: Any) -> str:
    if atr_pct is None or pd.isna(atr_pct):
        return "unknown"
    if atr_pct >= 0.045:
        return "high"
    if atr_pct <= 0.02:
        return "low"
    return "normal"


def load_history() -> Dict[str, List[dict]]:
    payload = json.loads((DATA / "vn100_history_from_2023.json").read_text(encoding="utf-8"))
    return {sym: obj.get("rows", []) for sym, obj in payload.get("symbols", {}).items() if isinstance(obj, dict)}


def load_patterns() -> dict:
    p = DATA / "chart_patterns_cache.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("symbols", {})


def nearest_levels(pattern: dict, close: float) -> dict:
    levels = ((pattern or {}).get("summary") or {}).get("keyLevels") or {}
    sups = [float(x) for x in levels.get("supports", []) if x is not None and float(x) < close]
    ress = [float(x) for x in levels.get("resistances", []) if x is not None and float(x) > close]
    sup = max(sups) if sups else None
    res = min(ress) if ress else None
    return {
        "nearestSupport": r(sup, 3),
        "nearestResistance": r(res, 3),
        "distSupportPct": r((close / sup - 1) if sup else None, 4),
        "distResistancePct": r((res / close - 1) if res else None, 4),
    }


def build_row(sym: str, row: pd.Series, pattern: dict | None) -> dict:
    close = float(row["close"])
    summary = (pattern or {}).get("summary") or {}
    ptop = ((pattern or {}).get("topPatterns") or [{}])[0] if pattern else {}
    lv = nearest_levels(pattern or {}, close)
    return {
        "symbol": sym,
        "date": row["date"].strftime("%Y-%m-%d"),
        "close": r(close, 3),
        "labels": {
            "futureReturn5d": r(row.get("futureReturn5d"), 4),
            "futureReturn10d": r(row.get("futureReturn10d"), 4),
            "futureReturn20d": r(row.get("futureReturn20d"), 4),
            "futureReturn60d": r(row.get("futureReturn60d"), 4),
            "futureMaxDrawdown20d": r(row.get("futureMaxDrawdown20d"), 4),
            "futureMaxRunup20d": r(row.get("futureMaxRunup20d"), 4),
            "hitTarget6Pct20d": bool((row.get("futureMaxRunup20d") or 0) >= 0.06) if not pd.isna(row.get("futureMaxRunup20d")) else None,
        },
        "trend": {
            "ret5": r(row.get("ret5"), 4),
            "ret20": r(row.get("ret20"), 4),
            "ret60": r(row.get("ret60"), 4),
            "ma20Slope20": r(row.get("ma20Slope20"), 4),
            "ma50Slope20": r(row.get("ma50Slope20"), 4),
            "priceVsMa20Pct": r(row.get("priceVsMa20Pct"), 4),
            "priceVsMa50Pct": r(row.get("priceVsMa50Pct"), 4),
        },
        "momentum": {
            "rsi14": r(row.get("rsi14"), 2),
            "macdHist": r(row.get("macdHist"), 4),
            "macdHistSlope3": r(row.get("macdHistSlope3"), 4),
        },
        "volume": {
            "volume": r(row.get("volume"), 0),
            "volumeRatio20": r(row.get("volumeRatio20"), 3),
        },
        "volatility": {
            "atrPct": r(row.get("atrPct"), 4),
            "realizedVol20": r(row.get("realizedVol20"), 4),
            "bbWidth20": r(row.get("bbWidth20"), 4),
            "volRegime": vol_regime(row.get("atrPct")),
        },
        "sr": lv,
        "pattern": {
            "bias": summary.get("bias"),
            "biasStrength": r(summary.get("biasStrength"), 2),
            "bullScore": r(summary.get("bullScore"), 2),
            "bearScore": r(summary.get("bearScore"), 2),
            "patternCount": (pattern or {}).get("patternCount"),
            "topPattern": ptop.get("type"),
            "topPatternDirection": ptop.get("direction"),
            "topPatternScore": r(ptop.get("score"), 2),
        },
        "market": {
            "symbolRegime": market_regime(row),
        },
    }


def main() -> int:
    history = load_history()
    patterns = load_patterns()
    rows_out = []
    errors = {}
    per_symbol = {}
    for sym, rows in sorted(history.items()):
        try:
            df = pd.DataFrame(rows).rename(columns={"time": "date"})
            df["date"] = pd.to_datetime(df["date"])
            for c in ["open", "high", "low", "close", "volume"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna(subset=["date", "open", "high", "low", "close"]).sort_values("date").reset_index(drop=True)
            df = add_features(df)
            valid = df[df["sma200"].notna()].copy()
            # Keep weekly-ish sample count manageable: every 5th row plus latest 260 rows; enough for research JSON.
            sampled = valid.iloc[::5].copy()
            tail = valid.tail(260)
            sampled = pd.concat([sampled, tail]).drop_duplicates(subset=["date"]).sort_values("date")
            prows = []
            for _, row in sampled.iterrows():
                item = build_row(sym, row, patterns.get(sym))
                rows_out.append(item)
                prows.append(item)
            per_symbol[sym] = {"rows": len(prows), "start": prows[0]["date"] if prows else None, "end": prows[-1]["date"] if prows else None}
            print(sym, len(prows))
        except Exception as e:
            errors[sym] = f"{type(e).__name__}: {e}"
            print(sym, "ERROR", errors[sym])

    payload = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": "data/vn100_history_from_2023.json + data/chart_patterns_cache.json",
        "method": "MIT finance feature matrix: past-only features, future-return labels, no random split",
        "count": len(rows_out),
        "symbolCount": len(per_symbol),
        "errorCount": len(errors),
        "perSymbol": per_symbol,
        "rows": rows_out,
        "errors": errors,
        "note": "Research/training dataset. Future labels are for evaluation only, not live features.",
    }
    for out in [DATA / "research_feature_matrix_vn100.json", PUBLIC_DATA / "research_feature_matrix_vn100.json"]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
