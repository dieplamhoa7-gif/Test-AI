# -*- coding: utf-8 -*-
"""Quick local Wyckoff-style support/reclaim baseline for VN100 cache.

Purpose: run a measurable baseline before wiring deeper Wyckoff scoring into the
local web chart. Uses only past candles for zone construction, enters next open.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "vn100_history_2025_06_2026_05_cache.json"
OUT = ROOT / "data" / "wyckoff_sr_vn100_local_backtest.json"
FEE_PCT = 0.5
LOOKBACK = 140
MAX_HOLD = 20
STOP_PCT = -5.0
TARGET_PCT = 10.0


def avg(vals):
    return sum(vals) / len(vals) if vals else 0.0


def pivot_lows(rows):
    out = []
    for i in range(2, len(rows) - 2):
        low = float(rows[i].get("low") or 0)
        if all(low < float(rows[j].get("low") or 0) for j in range(i - 2, i + 3) if j != i):
            out.append((i, low))
    return out


def support_zones(rows):
    if len(rows) < 40:
        return []
    ranges = [abs(float(r.get("high") or 0) - float(r.get("low") or 0)) for r in rows]
    avg_range = avg(ranges)
    avg_vol = avg([float(r.get("volume") or 0) for r in rows])
    pivots = pivot_lows(rows)
    clusters = []
    for idx, price in pivots:
        found = None
        for c in clusters:
            if abs(price / max(0.0001, c["center"]) - 1) < 0.012:
                found = c
                break
        if found:
            found["items"].append((idx, price))
            found["center"] = avg([p for _, p in found["items"]])
        else:
            clusters.append({"center": price, "items": [(idx, price)]})
    zones = []
    for c in clusters:
        price = c["center"]
        tol = max(avg_range * 0.45, price * 0.006)
        touches = 0
        vol_sum = 0.0
        reaction_sum = 0.0
        breaks = 0
        last_touch = -99
        for i, r in enumerate(rows):
            lo = float(r.get("low") or 0)
            hi = float(r.get("high") or 0)
            op = float(r.get("open") or 0)
            cl = float(r.get("close") or 0)
            if abs(lo - price) <= tol and i - last_touch >= 3:
                touches += 1
                last_touch = i
                vol_sum += float(r.get("volume") or 0)
                after = rows[i + 1 : min(len(rows), i + 6)]
                if after:
                    reaction_sum += max(0.0, max(float(x.get("high") or price) for x in after) - price)
            if min(op, cl) < price - tol:
                breaks += 1
        if touches < 3:
            continue
        avg_touch_vol = vol_sum / touches if touches else 0
        avg_reaction = reaction_sum / touches if touches else 0
        touch_score = min(40, touches * 8)
        volume_score = min(22, (avg_touch_vol / max(1, avg_vol)) * 11)
        reaction_score = min(22, (avg_reaction / max(0.001, avg_range)) * 11)
        break_penalty = min(45, breaks * 9)
        strength = touch_score + volume_score + reaction_score - break_penalty
        if strength >= 40 and breaks <= max(3, int(touches * 0.65)):
            zones.append({"price": round(price, 2), "touches": touches, "breaks": breaks, "strength": round(strength, 2)})
    return sorted(zones, key=lambda x: x["strength"], reverse=True)


def vol_ma(rows, i, n=20):
    start = max(0, i - n)
    vals = [float(r.get("volume") or 0) for r in rows[start:i]]
    return avg(vals)


def is_spring_reclaim(row, support, avg_vol20):
    low = float(row.get("low") or 0)
    close = float(row.get("close") or 0)
    open_ = float(row.get("open") or 0)
    vol = float(row.get("volume") or 0)
    price = support["price"]
    # Shake below/into support then reclaim above it, preferably green or lower wick.
    return (
        low <= price * 1.004
        and low >= price * 0.965
        and close >= price * 1.002
        and close >= open_ * 0.995
        and vol >= avg_vol20 * 0.85
    )


def is_volume_dry_test(row, support, avg_vol20):
    low = float(row.get("low") or 0)
    close = float(row.get("close") or 0)
    open_ = float(row.get("open") or 0)
    vol = float(row.get("volume") or 0)
    price = support["price"]
    return (
        abs(low / price - 1) <= 0.012
        and close > open_
        and close >= price
        and vol <= avg_vol20 * 0.95
    )


def backtest_symbol(symbol, rows, variant):
    trades = []
    i = LOOKBACK
    while i < len(rows) - MAX_HOLD - 1:
        hist = rows[i - LOOKBACK : i]
        zones = support_zones(hist)[:5]
        if not zones:
            i += 1
            continue
        row = rows[i]
        close = float(row.get("close") or 0)
        candidates = [z for z in zones if abs(close / z["price"] - 1) <= 0.10]
        if not candidates:
            i += 1
            continue
        support = sorted(candidates, key=lambda z: abs(close / z["price"] - 1))[0]
        vma = vol_ma(rows, i, 20)
        signal = False
        if variant == "spring_reclaim":
            signal = is_spring_reclaim(row, support, vma)
        elif variant == "dry_test_reclaim":
            signal = is_volume_dry_test(row, support, vma)
        elif variant == "combined":
            signal = is_spring_reclaim(row, support, vma) or is_volume_dry_test(row, support, vma)
        if not signal:
            i += 1
            continue
        entry_i = i + 1
        entry = float(rows[entry_i].get("open") or rows[entry_i].get("close") or 0)
        if entry <= 0:
            i += 1
            continue
        exit_i = min(len(rows) - 1, entry_i + MAX_HOLD)
        exit_price = float(rows[exit_i].get("close") or entry)
        reason = "time"
        for j in range(entry_i, min(len(rows), entry_i + MAX_HOLD + 1)):
            hi = float(rows[j].get("high") or 0)
            lo = float(rows[j].get("low") or 0)
            if (lo / entry - 1) * 100 <= STOP_PCT:
                exit_i, exit_price, reason = j, entry * (1 + STOP_PCT / 100), "stop"
                break
            if (hi / entry - 1) * 100 >= TARGET_PCT:
                exit_i, exit_price, reason = j, entry * (1 + TARGET_PCT / 100), "target"
                break
        pnl = (exit_price / entry - 1) * 100 - FEE_PCT
        trades.append({
            "symbol": symbol,
            "entryDate": rows[entry_i].get("time"),
            "exitDate": rows[exit_i].get("time"),
            "entry": round(entry, 2),
            "exit": round(exit_price, 2),
            "pnl": round(pnl, 2),
            "hold": exit_i - entry_i,
            "reason": reason,
            "support": support,
        })
        i = exit_i + 1
    return trades


def summarize(trades):
    if not trades:
        return {"n": 0, "winRate": 0, "avgPnl": 0, "sumPnl": 0, "avgHold": 0}
    wins = [t for t in trades if t["pnl"] > 0]
    return {
        "n": len(trades),
        "winRate": round(len(wins) / len(trades) * 100, 2),
        "avgPnl": round(mean(t["pnl"] for t in trades), 2),
        "sumPnl": round(sum(t["pnl"] for t in trades), 2),
        "avgHold": round(mean(t["hold"] for t in trades), 1),
    }


def main():
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    symbols = data.get("symbols", {})
    variants = ["spring_reclaim", "dry_test_reclaim", "combined"]
    result = {"variants": {}, "params": {"lookback": LOOKBACK, "maxHold": MAX_HOLD, "targetPct": TARGET_PCT, "stopPct": STOP_PCT, "feePct": FEE_PCT}}
    for variant in variants:
        all_trades = []
        for symbol, payload in symbols.items():
            rows = payload.get("rows", []) if isinstance(payload, dict) else []
            rows = [r for r in rows if all(k in r for k in ("open", "high", "low", "close"))]
            if len(rows) < LOOKBACK + MAX_HOLD + 5:
                continue
            all_trades.extend(backtest_symbol(symbol, rows, variant))
        result["variants"][variant] = {"summary": summarize(all_trades), "trades": all_trades[:300]}
        print(variant, result["variants"][variant]["summary"])
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
