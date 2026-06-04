#!/usr/bin/env python3
"""Build chart pattern cache for LH Investment charts.

Uses the local rule-based pattern engine copied from tmp_claude_pattern_pack_v2
(`pattern_engine_v2/chart_patterns.py`) and optionally merges TradingPatternScanner
results if that library is installed later.

Inputs:
  stock-news-backend/data/vn100_history_from_2023.json

Outputs:
  stock-news-backend/data/chart_patterns_cache.json
  stock-news-backend/firebase_public/data/chart_patterns_cache.json

Research-only. No frontend/deploy changes.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pattern_engine_v2.analyze import analyze  # noqa: E402


def _finite(x: Any) -> Any:
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, dict):
        return {k: _finite(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_finite(v) for v in x]
    return x


def _load_history(path: Path) -> Dict[str, List[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    symbols = payload.get("symbols", {})
    out: Dict[str, List[dict]] = {}
    for sym, obj in symbols.items():
        rows = obj.get("rows") if isinstance(obj, dict) else None
        if rows:
            out[sym.upper()] = rows
    return out


def _rows_to_df(rows: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    rename = {"time": "date"}
    df = df.rename(columns=rename)
    needed = ["date", "open", "high", "low", "close", "volume"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"missing OHLCV columns: {missing}")
    df = df[needed].copy()
    df["date"] = pd.to_datetime(df["date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["date", "open", "high", "low", "close"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _top_patterns(patterns: List[dict], limit: int = 12) -> List[dict]:
    compact = []
    for p in patterns[:limit]:
        compact.append({
            "type": p.get("type"),
            "category": p.get("category"),
            "direction": p.get("direction"),
            "tier": p.get("tier"),
            "role": p.get("role"),
            "status": p.get("status"),
            "confidence": p.get("confidence"),
            "score": p.get("score"),
            "composite": p.get("composite") or p.get("_composite_final"),
            "time": p.get("time"),
            "price": p.get("price"),
            "levels": p.get("levels", {}),
            "evidence": p.get("evidence", {}),
            "lines": p.get("lines", [])[:4],
        })
    return compact


def _try_trading_pattern_scanner(df: pd.DataFrame) -> dict:
    """Optional hook. TradingPatternScanner is not required for the cache build.

    Package APIs vary across forks, so this intentionally reports availability and
    can be expanded after the exact package is installed/pinned.
    """
    for mod_name in ("tradingpattern", "TradingPatternScanner", "tradingpatterns"):
        try:
            mod = importlib.import_module(mod_name)
            return {
                "available": True,
                "module": mod_name,
                "note": "module import ok; scanner adapter not pinned yet",
                "moduleFile": getattr(mod, "__file__", None),
            }
        except Exception:
            continue
    return {
        "available": False,
        "module": None,
        "note": "TradingPatternScanner/tradingpattern not installed; used pattern_engine_v2 only",
    }


def analyze_symbol(sym: str, rows: List[dict], include_experimental: bool) -> dict:
    df = _rows_to_df(rows)
    if len(df) < 80:
        raise ValueError(f"not enough bars: {len(df)}")
    result = analyze(df, symbol=sym, include_experimental=include_experimental)
    tps = _try_trading_pattern_scanner(df)
    summary = result.get("summary", {})
    return _finite({
        "symbol": sym,
        "timeframe": result.get("timeframe"),
        "bars": result.get("bars"),
        "period": result.get("period"),
        "lastClose": result.get("lastClose"),
        "engineFlags": result.get("engineFlags"),
        "tradingPatternScanner": tps,
        "summary": summary,
        "topPatterns": _top_patterns(result.get("patterns", []), limit=12),
        "patternCount": len(result.get("patterns", [])),
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default=str(ROOT / "data" / "vn100_history_from_2023.json"))
    ap.add_argument("--symbols", default="", help="Comma-separated symbols. Default: all symbols in history file.")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of symbols for quick tests.")
    ap.add_argument("--include-experimental", action="store_true", help="Include low-confidence experimental patterns.")
    ap.add_argument("--out", default=str(ROOT / "data" / "chart_patterns_cache.json"))
    ap.add_argument("--public-out", default=str(ROOT / "firebase_public" / "data" / "chart_patterns_cache.json"))
    args = ap.parse_args()

    history = _load_history(Path(args.history))
    wanted = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    symbols = wanted or sorted(history)
    if args.limit and args.limit > 0:
        symbols = symbols[: args.limit]

    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    for i, sym in enumerate(symbols, 1):
        rows = history.get(sym)
        if not rows:
            errors[sym] = "symbol not found in history"
            continue
        try:
            results[sym] = analyze_symbol(sym, rows, include_experimental=args.include_experimental)
            print(f"[{i}/{len(symbols)}] {sym}: {results[sym]['summary'].get('bias')} {results[sym]['patternCount']} patterns")
        except Exception as e:
            errors[sym] = f"{type(e).__name__}: {e}"
            print(f"[{i}/{len(symbols)}] {sym}: ERROR {errors[sym]}")

    payload = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": str(Path(args.history).relative_to(ROOT) if Path(args.history).is_relative_to(ROOT) else args.history),
        "engine": "pattern_engine_v2.chart_patterns + optional TradingPatternScanner hook",
        "count": len(results),
        "errorCount": len(errors),
        "symbols": results,
        "errors": errors,
        "note": "Research-only pattern cache; not financial advice.",
    }

    for out in [Path(args.out), Path(args.public_out)]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {out}")
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
