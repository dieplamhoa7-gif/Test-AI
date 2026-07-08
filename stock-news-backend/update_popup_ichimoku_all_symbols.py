from __future__ import annotations

import json
import sys
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from vnstock import Quote

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PUBLIC_DATA = ROOT / "firebase_public" / "data"
TZ = timezone(timedelta(hours=7))
HIST = DATA / "vn100_history_2025_06_2026_05_cache.json"
V3 = DATA / "v3_full_indicator_cache_v2.json"
OUT_FILES = [
    DATA / "market_data.json",
    PUBLIC_DATA / "market_data.json",
    PUBLIC_DATA / "market_watch.json",
]
REQUEST_DELAY_SECONDS = 3.6


def _num(v: Any) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _round2(v: Any) -> float | None:
    n = _num(v)
    return round(n, 2) if n is not None else None


def _clean_rows_from_df(df: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if df is None or getattr(df, "empty", True):
        return rows
    df = df.sort_values("time")
    for _, r in df.iterrows():
        row = {
            "time": str(r.get("time")),
            "open": _num(r.get("open")),
            "high": _num(r.get("high")),
            "low": _num(r.get("low")),
            "close": _num(r.get("close")),
            "volume": _num(r.get("volume")) or 0,
        }
        if None not in [row["open"], row["high"], row["low"], row["close"]]:
            rows.append(row)
    return rows


def _aggregate(rows: list[dict[str, Any]], frame: str) -> list[dict[str, Any]]:
    buckets: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for r in rows:
        t = str(r.get("time") or r.get("date") or "")[:10]
        if not t:
            continue
        if frame == "week":
            y, w, _ = datetime.fromisoformat(t).isocalendar()
            key = f"{y}-W{w:02d}"
        elif frame == "month":
            key = t[:7]
        else:
            key = t
        if key not in buckets:
            buckets[key] = {"time": t, "open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"], "volume": r.get("volume") or 0}
        else:
            b = buckets[key]
            b["high"] = max(float(b["high"]), float(r["high"]))
            b["low"] = min(float(b["low"]), float(r["low"]))
            b["close"] = r["close"]
            b["time"] = t
            b["volume"] = (b.get("volume") or 0) + (r.get("volume") or 0)
    return list(buckets.values())


def _ma(rows: list[dict[str, Any]], n: int) -> float | None:
    closes = [_num(r.get("close")) for r in rows]
    closes = [c for c in closes if c is not None]
    if len(closes) < n:
        return None
    return _round2(sum(closes[-n:]) / n)


def _ichimoku(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if len(rows) < 52:
        return None
    highs = [_num(r.get("high")) for r in rows]
    lows = [_num(r.get("low")) for r in rows]
    close = _num(rows[-1].get("close"))
    if close is None or any(v is None for v in highs[-52:] + lows[-52:]):
        return None
    tenkan = (max(highs[-9:]) + min(lows[-9:])) / 2
    kijun = (max(highs[-26:]) + min(lows[-26:])) / 2
    span_a = (tenkan + kijun) / 2
    span_b = (max(highs[-52:]) + min(lows[-52:])) / 2
    top = max(span_a, span_b)
    bottom = min(span_a, span_b)
    state = "above_cloud" if close > top else ("below_cloud" if close < bottom else "in_cloud")
    return {"cloudTop": _round2(top), "cloudBottom": _round2(bottom), "ichimokuState": state, "tenkan": _round2(tenkan), "kijun": _round2(kijun)}


def _load_symbols() -> list[str]:
    symbols: set[str] = set()
    for p in [PUBLIC_DATA / "market_data.json", DATA / "market_data.json"]:
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for item in d.get("items", []):
            sym = str(item.get("symbol") or item.get("ticker") or "").upper().strip()
            if sym:
                symbols.add(sym)
    return sorted(symbols)


def _day_from_v3() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not V3.exists():
        return out
    d = json.loads(V3.read_text(encoding="utf-8"))
    for item in d.get("items", []):
        sym = str(item.get("symbol") or item.get("ticker") or "").upper().strip()
        ichi = (item.get("indicators") or {}).get("ichimoku") or {}
        if not sym or not ichi:
            continue
        top = ichi.get("cloudTop") if ichi.get("cloudTop") is not None else max(ichi.get("senkouSpanA") or 0, ichi.get("senkouSpanB") or 0)
        bottom = ichi.get("cloudBottom") if ichi.get("cloudBottom") is not None else min(ichi.get("senkouSpanA") or 0, ichi.get("senkouSpanB") or 0)
        out[sym] = {"cloudTop": _round2(top), "cloudBottom": _round2(bottom), "ichimokuState": ichi.get("state") or ichi.get("ichimokuState") or "", "tenkan": _round2(ichi.get("tenkan")), "kijun": _round2(ichi.get("kijun"))}
    return out


def _history_rows() -> dict[str, list[dict[str, Any]]]:
    if not HIST.exists():
        return {}
    d = json.loads(HIST.read_text(encoding="utf-8"))
    return {str(sym).upper(): obj.get("rows") or [] for sym, obj in (d.get("symbols") or {}).items()}


def _fetch_with_retry(sym: str, start: str, end: str, interval: str, attempts: int = 4) -> list[dict[str, Any]]:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            df = Quote(symbol=sym, source="VCI").history(start=start, end=end, interval=interval)
            return _clean_rows_from_df(df)
        except Exception as exc:
            last_exc = exc
            wait = 65 if "rate" in str(exc).lower() or "limit" in str(exc).lower() else 10 * attempt
            print(f"{sym} {interval} retry {attempt}/{attempts} after {wait}s: {str(exc)[:120]}", flush=True)
            time.sleep(wait)
    raise RuntimeError(str(last_exc) if last_exc else "fetch failed")


def _fetch_daily_long(sym: str, end: str) -> list[dict[str, Any]]:
    return _fetch_with_retry(sym, "2018-01-01", end, "1D")


def _fetch_hourly(sym: str, end: str) -> list[dict[str, Any]]:
    return _fetch_with_retry(sym, "2026-05-01", end, "1H")


def _apply_frame(tech: dict[str, Any], suffix: str, vals: dict[str, Any]) -> None:
    tech[f"cloudTop{suffix}"] = vals["cloudTop"]
    tech[f"cloudBottom{suffix}"] = vals["cloudBottom"]
    tech[f"ichimokuState{suffix}"] = vals["ichimokuState"]
    tech[f"tenkan{suffix}"] = vals["tenkan"]
    tech[f"kijun{suffix}"] = vals["kijun"]
    for extra_key in [f"ma20{suffix}", f"ma50{suffix}"]:
        if vals.get(extra_key) is not None:
            tech[extra_key] = vals[extra_key]


def main() -> None:
    end = datetime.now(TZ).strftime("%Y-%m-%d")
    symbols = _load_symbols()
    day_map = _day_from_v3()
    hist_map = _history_rows()
    calc: dict[str, dict[str, dict[str, Any]]] = {}
    errors: list[dict[str, str]] = []
    for i, sym in enumerate(symbols, 1):
        calc[sym] = {}
        if sym in day_map:
            calc[sym]["Day"] = day_map[sym]
        rows = hist_map.get(sym) or []
        week = _ichimoku(_aggregate(rows, "week")) if rows else None
        if week:
            calc[sym]["Week"] = week
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            hour = _ichimoku(_fetch_hourly(sym, end))
            if hour:
                calc[sym]["Hour"] = hour
        except Exception as exc:
            errors.append({"symbol": sym, "frame": "Hour", "error": str(exc)[:180]})
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            month_rows = _aggregate(_fetch_daily_long(sym, end), "month")
            month = _ichimoku(month_rows)
            if month:
                calc[sym]["Month"] = month
                ma20m = _ma(month_rows, 20)
                ma50m = _ma(month_rows, 50)
                if ma20m is not None:
                    calc[sym]["Month"]["ma20Month"] = ma20m
                if ma50m is not None:
                    calc[sym]["Month"]["ma50Month"] = ma50m
        except Exception as exc:
            errors.append({"symbol": sym, "frame": "Month", "error": str(exc)[:180]})
        print(f"{i}/{len(symbols)} {sym} frames={sorted(calc[sym].keys())}", flush=True)

    summary: dict[str, Any] = {"symbols": len(symbols), "errors": errors, "files": {}}
    for p in OUT_FILES:
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        counts = {"Day": 0, "Hour": 0, "Week": 0, "Month": 0}
        for item in d.get("items", []):
            sym = str(item.get("symbol") or item.get("ticker") or "").upper().strip()
            frames = calc.get(sym) or {}
            if not frames:
                continue
            tech = item.setdefault("technical", {})
            if "Day" in frames:
                for k, v in frames["Day"].items():
                    if v not in (None, ""):
                        tech[k] = v
                counts["Day"] += 1
            for suffix in ["Hour", "Week", "Month"]:
                if suffix in frames:
                    _apply_frame(tech, suffix, frames[suffix])
                    counts[suffix] += 1
        d["popupIndicatorUpdatedAt"] = datetime.now(TZ).isoformat(timespec="seconds")
        d["popupIndicatorNote"] = "Updated popup Ichimoku cloud/state/Tenkan/Kijun for Day/Hour/Week/Month from evidence OHLC caches/VCI. Missing frames are not fabricated."
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["files"][str(p.relative_to(ROOT))] = counts
    out_path = DATA / "popup_ichimoku_update_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
