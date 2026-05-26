from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any
import json
import sqlite3

from app.market_data import _fetch_quote


def _fetch_quotes_batch(symbols: list[str]) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for symbol in symbols:
        normalized = str(symbol or "").strip().upper()
        if not normalized:
            continue
        quote = _fetch_quote(normalized)
        if quote:
            quotes[normalized] = quote
    return quotes

CACHE_TTL_SECONDS = 15 * 60
_cache: dict[tuple[int, int], tuple[float, dict[str, Any]]] = {}


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_target_price(target: Any, reference_price: float = 0) -> float:
    """Normalize analyst target prices to VND/share.

    Some scraped rows miss one trailing zero (for example 14,800 instead of
    148,000). Only correct when the x10 value is plausible versus the current
    market price to avoid touching genuinely low targets.
    """
    try:
        value = float(target or 0)
    except Exception:
        return 0.0
    try:
        price = float(reference_price or 0)
    except Exception:
        price = 0.0
    if price > 0 and value > 0 and value < price * 0.45 and price * 0.8 <= value * 10 <= price * 3.5:
        value *= 10
    return value


def _load_report_rows() -> list[dict[str, Any]]:
    root = _root()
    json_path = root / "report_signal_mvp" / "all_report_signals.json"
    db_path = root / "report_signal_mvp" / "all_report_signals.db"
    rows: list[dict[str, Any]] = []
    if db_path.exists():
        try:
            con = sqlite3.connect(db_path)
            con.row_factory = sqlite3.Row
            rows = [dict(r) for r in con.execute("select * from report_signals_all where target_price is not null and target_price > 0")]
            con.close()
        except Exception:
            rows = []
    if not rows and json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            rows = [r for r in data if float(r.get("target_price") or 0) > 0]
        except Exception:
            rows = []
    return rows


def top_target_upside(limit: int = 20, max_symbols: int = 80, force_refresh: bool = False) -> dict[str, Any]:
    limit = max(1, min(int(limit or 20), 50))
    max_symbols = max(limit, min(int(max_symbols or 80), 200))
    key = (limit, max_symbols)
    now = monotonic()
    cached = _cache.get(key)
    if cached and not force_refresh and (now - cached[0]) < CACHE_TTL_SECONDS:
        payload = dict(cached[1])
        payload["cached"] = True
        return payload

    rows = _load_report_rows()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        target = float(row.get("target_price") or 0)
        if not symbol or target <= 0:
            continue
        grouped[symbol].append(row)

    # Rank by number of reports first so batch quote calls stay small and useful.
    candidates = sorted(grouped.keys(), key=lambda s: (len(grouped[s]), max(float(r.get("target_price") or 0) for r in grouped[s])), reverse=True)[:max_symbols]
    quotes = _fetch_quotes_batch(candidates)
    items: list[dict[str, Any]] = []
    for symbol in candidates:
        quote = quotes.get(symbol)
        raw_price = float((quote or {}).get("price") or 0)
        if raw_price <= 0:
            continue
        reports = grouped[symbol]
        raw_targets = [float(r.get("target_price") or 0) for r in reports if float(r.get("target_price") or 0) > 0]
        if not raw_targets:
            continue
        # VPS quotes are usually in thousand VND while analyst targets are VND/share.
        rough_avg_target = sum(raw_targets) / len(raw_targets)
        price = raw_price * 1000 if rough_avg_target > raw_price * 100 else raw_price
        targets = [normalize_target_price(target, price) for target in raw_targets]
        avg_target = sum(targets) / len(targets)
        upside_pct = (avg_target - price) / price * 100
        dated_reports = sorted(reports, key=lambda r: str(r.get("report_date") or ""), reverse=True)
        latest = dated_reports[0]
        latest_target = float(latest.get("target_price") or 0)
        latest_target = normalize_target_price(latest_target, price)
        recent_cutoff = str(latest.get("report_date") or "")[:7]
        recent_targets = []
        for r in reports:
            if str(r.get("report_date") or "")[:7] == recent_cutoff:
                t = float(r.get("target_price") or 0)
                t = normalize_target_price(t, price)
                if t > 0:
                    recent_targets.append(t)
        recent_avg_target = sum(recent_targets) / len(recent_targets) if recent_targets else latest_target
        brokers = sorted({str(r.get("broker") or r.get("source") or "").strip() for r in reports if str(r.get("broker") or r.get("source") or "").strip()})
        items.append({
            "symbol": symbol,
            "price": round(price, 2),
            "rawQuotePrice": round(raw_price, 2),
            "avgTargetPrice": round(avg_target, 2),
            "recentAvgTargetPrice": round(recent_avg_target, 2),
            "latestTargetPrice": round(latest_target, 2),
            "upsidePct": round(upside_pct, 2),
            "recentUpsidePct": round(((recent_avg_target - price) / price * 100), 2) if price else None,
            "latestUpsidePct": round(((latest_target - price) / price * 100), 2) if price else None,
            "reportCount": len(targets),
            "latestReportDate": latest.get("report_date"),
            "latestTitle": latest.get("title"),
            "latestUrl": latest.get("url"),
            "brokers": brokers[:6],
        })
    items.sort(key=lambda x: x["upsidePct"], reverse=True)
    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "items": items[:limit],
        "totalCandidates": len(items),
        "limit": limit,
        "cached": False,
        "ttlSeconds": CACHE_TTL_SECONDS,
    }
    _cache[key] = (now, payload)
    return payload
