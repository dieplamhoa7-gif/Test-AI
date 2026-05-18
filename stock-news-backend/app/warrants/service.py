from __future__ import annotations

from datetime import datetime
from time import monotonic
from pathlib import Path
from typing import Any
import json

import httpx

try:
    from vnstock import Listing
except Exception:  # pragma: no cover
    Listing = None

DATA_PATH = Path(__file__).resolve().parent / "warrants_static.json"
CATALOG_PATH = Path(__file__).resolve().parent / "warrant_catalog.json"
CACHE_TTL_SECONDS = 180
DETAIL_CACHE_TTL_SECONDS = 60
_cache: dict[str, Any] | None = None
_cache_at = 0.0
_detail_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace(",", ""))
    except Exception:
        return None


def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def _parse_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"
    return text or None


def _days_left(value: Any) -> int | None:
    text = _parse_date(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return max(0, (datetime.strptime(text, fmt).date() - datetime.now().date()).days)
        except Exception:
            pass
    return None


def _parse_ratio(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    if ":" in text:
        text = text.split(":", 1)[0]
    return _num(text)


def _quote_warrant(symbol: str) -> dict[str, Any] | None:
    try:
        url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}"
        resp = httpx.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None
        item = data[0]
        last = _num(item.get("lastPrice"))
        ref = _num(item.get("r"))
        bid = _num(str(item.get("g1") or "").split("|")[0])
        ask = _num(str(item.get("g4") or "").split("|")[0])
        # VPS board prices are in thousand VND for both stocks and covered warrants.
        for_name_prices = ["last", "ref", "bid", "ask"]
        if last is not None and last < 1000:
            last *= 1000
        if ref is not None and ref < 1000:
            ref *= 1000
        if bid is not None and bid < 1000:
            bid *= 1000
        if ask is not None and ask < 1000:
            ask *= 1000
        change_pct = _num(item.get("changePc"))
        change = (last - ref) if last is not None and ref is not None else None
        spread_pct = ((ask - bid) / bid * 100) if bid and ask and bid > 0 else None
        raw_volume = _num(item.get("lot")) or _num(item.get("lastVolume")) or 0
        volume = int(raw_volume * 10)
        exercise_price = _num(item.get("CWExcersisePrice"))
        # VPS CW exercise price is usually in thousand VND; normalize to VND.
        if exercise_price and exercise_price < 1000:
            exercise_price *= 1000
        return {
            "code": str(item.get("sym") or symbol).upper(),
            "lastPrice": last,
            "refPrice": ref,
            "change": _round(change),
            "changePct": _round(change_pct),
            "bid": bid,
            "ask": ask,
            "spreadPct": _round(spread_pct),
            "volume": volume,
            "ceiling": ((_num(item.get("c")) or 0) * 1000) if (_num(item.get("c")) or 0) < 1000 else _num(item.get("c")),
            "floor": ((_num(item.get("f")) or 0) * 1000) if (_num(item.get("f")) or 0) < 1000 else _num(item.get("f")),
            "openPrice": ((_num(item.get("openPrice")) or 0) * 1000) if (_num(item.get("openPrice")) or 0) < 1000 else _num(item.get("openPrice")),
            "highPrice": ((_num(item.get("highPrice")) or 0) * 1000) if (_num(item.get("highPrice")) or 0) < 1000 else _num(item.get("highPrice")),
            "lowPrice": ((_num(item.get("lowPrice")) or 0) * 1000) if (_num(item.get("lowPrice")) or 0) < 1000 else _num(item.get("lowPrice")),
            "maturityDate": _parse_date(item.get("CWMaturityDate")),
            "lastTradingDate": _parse_date(item.get("CWLastTradingDate")),
            "exercisePrice": exercise_price,
            "conversionRatio": _parse_ratio(item.get("CWExerciseRatio")),
            "listedShare": _num(item.get("CWListedShare")),
            "source": "vnstock-vps",
        }
    except Exception:
        return None


def _covered_warrant_symbols() -> list[str]:
    if CATALOG_PATH.exists():
        try:
            payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            return [str(item.get("code") or "").upper().strip() for item in payload.get("items", []) if str(item.get("code") or "").strip() and _is_active_warrant(item)]
        except Exception:
            pass
    if Listing is None:
        return []
    try:
        series = Listing().all_covered_warrant()
        return [str(x).upper().strip() for x in series.tolist() if str(x).strip()]
    except Exception:
        return []


def _is_active_warrant(row: dict[str, Any]) -> bool:
    days_left = _num(row.get("daysLeft"))
    if days_left is None:
        days_left = _days_left(row.get("lastTradingDate") or row.get("maturityDate"))
    # Clear expired/matured warrants from runtime data/search/list.
    return days_left is None or days_left > 0


def _static_map() -> dict[str, dict[str, Any]]:
    if not DATA_PATH.exists():
        return {}
    try:
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return {str(item.get("code") or "").upper(): item for item in payload.get("items", []) if _is_active_warrant(item)}
    except Exception:
        return {}


def _infer_underlying(code: str) -> str:
    # Common VN covered warrant code: C + underlying + issue suffix, e.g. CMWG2511.
    text = str(code or "").upper()
    if text.startswith("C") and len(text) >= 4:
        return text[1:4]
    return ""


def enrich_warrant(row: dict[str, Any]) -> dict[str, Any]:
    underlying = str(row.get("underlying") or "").upper().strip()
    underlying_price = None
    if underlying:
        try:
            resp = httpx.get(f"https://bgapidatafeed.vps.com.vn/getliststockdata/{underlying}", timeout=3, headers={"User-Agent": "Mozilla/5.0"})
            data = resp.json()
            if isinstance(data, list) and data:
                underlying_price = _num(data[0].get("lastPrice"))
                if underlying_price and underlying_price < 1000:
                    underlying_price *= 1000
        except Exception:
            underlying_price = None
    if underlying_price is None:
        underlying_price = _num(row.get("underlyingPrice"))
    fair_value = _num(row.get("fairValue"))
    last_price = _num(row.get("lastPrice"))
    bid_price = _num(row.get("bid"))
    ask_price = _num(row.get("ask"))
    ref_price = _num(row.get("refPrice"))
    # Some newly listed / inactive intraday warrants report lastPrice=0 although
    # bid/ask/ref and contract terms are available. For static analysis, use a
    # deterministic board-price fallback instead of showing empty derived fields.
    if last_price is not None and last_price > 0:
        market_price = last_price
    elif bid_price and ask_price:
        market_price = (bid_price + ask_price) / 2
    elif ref_price and ref_price > 0:
        market_price = ref_price
    else:
        market_price = fair_value
    exercise_price = _num(row.get("exercisePrice"))
    conversion_ratio = _num(row.get("conversionRatio")) or 1
    # Always derive remaining days from live contract dates when available.
    # Static caches may carry stale daysLeft values from the day they were built.
    days_left = _days_left(row.get("lastTradingDate") or row.get("maturityDate"))
    if days_left is None:
        days_left = _num(row.get("daysLeft"))
    # Covered warrant formulas for Vietnamese CW:
    # Intrinsic value per CW = max(0, underlying - exercise) / conversion_ratio.
    # Breakeven underlying price = exercise + market_price * conversion_ratio.
    breakeven = _num(row.get("breakeven"))
    if exercise_price and market_price and conversion_ratio:
        breakeven = exercise_price + market_price * conversion_ratio

    intrinsic_value = None
    time_value = None
    moneyness_pct = None
    moneyness = str(row.get("moneyness") or "").upper().strip() or None
    breakeven_gap_pct = None
    premium_pct = None
    breakeven_gap_value = None
    required_daily_gain = None
    required_daily_gain_pct = None
    leverage = None
    effective_gearing = None
    risk_level = "Trung bình"
    signal = "Theo dõi"
    note: list[str] = []

    if underlying_price and exercise_price and conversion_ratio:
        intrinsic_value = max(0.0, (underlying_price - exercise_price) / conversion_ratio)
        if market_price is not None:
            time_value = market_price - intrinsic_value
            leverage = underlying_price / (market_price * conversion_ratio) if market_price > 0 else None
            effective_gearing = leverage
        moneyness_pct = (underlying_price / exercise_price - 1) * 100 if exercise_price else None
        if moneyness_pct is not None:
            if abs(moneyness_pct) <= 2:
                moneyness = "ATM"
            elif moneyness_pct > 2:
                moneyness = "ITM"
            else:
                moneyness = "OTM"

    if underlying_price and breakeven:
        breakeven_gap = breakeven - underlying_price
        breakeven_gap_value = breakeven_gap
        breakeven_gap_pct = breakeven_gap / underlying_price * 100
        premium_pct = breakeven_gap_pct
        if days_left and days_left > 0:
            required_daily_gain = breakeven_gap / days_left
            required_daily_gain_pct = breakeven_gap_pct / days_left

    if days_left is not None:
        if days_left <= 20:
            risk_level = "Cao"
            note.append("Sắp đáo hạn, time decay mạnh")
        elif days_left <= 45:
            risk_level = "Trung bình cao"
            note.append("Thời gian còn lại ngắn")

    if moneyness_pct is not None:
        if moneyness_pct < -8:
            risk_level = "Rất cao"
            signal = "Tránh nếu không có sóng mạnh"
            note.append("Đang OTM xa")
        elif moneyness_pct < 0:
            signal = "Chỉ phù hợp trading ngắn"
            note.append("Đang OTM")
        elif moneyness_pct > 8 and (days_left or 999) > 30:
            signal = "Tương đối tốt"
            note.append("ITM và còn thời gian")
        elif moneyness_pct > 0:
            signal = "Có thể theo dõi"
            note.append("Đang ITM")

    spread_pct = _num(row.get("spreadPct"))
    if spread_pct is not None:
        if spread_pct > 8:
            note.append("Spread rộng, thanh khoản rủi ro")
        elif spread_pct <= 3:
            note.append("Spread tương đối tốt")

    if breakeven_gap_pct is not None:
        if breakeven_gap_pct > 10:
            risk_level = "Rất cao"
            note.append("Cần cổ phiếu cơ sở tăng mạnh mới hòa vốn")
        elif breakeven_gap_pct > 5:
            note.append("Khoảng cách hòa vốn khá xa")
        elif breakeven_gap_pct <= 0:
            note.append("Giá cơ sở đang trên/vùng hòa vốn")

    enriched = dict(row)
    enriched.update(
        {
            "underlyingPrice": _round(underlying_price),
            "fairValue": _round(fair_value),
            "marketPrice": _round(market_price),
            "breakeven": _round(breakeven),
            "leverage": _round(leverage),
            "effectiveGearing": _round(effective_gearing),
            "daysLeft": int(days_left) if days_left is not None else None,
            "intrinsicValue": _round(intrinsic_value),
            "timeValue": _round(time_value),
            "moneyness": moneyness,
            "moneynessPct": _round(moneyness_pct),
            "breakevenGap": _round(breakeven_gap_value),
            "breakevenGapPct": _round(breakeven_gap_pct),
            "premiumPct": _round(premium_pct),
            "requiredDailyGain": _round(required_daily_gain),
            "requiredDailyGainPct": _round(required_daily_gain_pct, 3),
            "riskLevel": risk_level,
            "advancedSignal": signal,
            "analysisNote": "; ".join(dict.fromkeys(note)) or "Chưa có cảnh báo đặc biệt",
        }
    )
    return enriched


def get_warrants_data(force_refresh: bool = False, symbols: list[str] | None = None) -> dict[str, Any]:
    """Return covered-warrant data.

    Fast mode (symbols=None): return VNStock warrant catalog quickly without quoting all symbols.
    Detail mode (symbols=[...]): quote/enrich only requested symbols.
    """
    global _cache, _cache_at
    now = monotonic()
    want = [str(x).upper().strip() for x in (symbols or []) if str(x).strip()]
    static = _static_map()

    if want and not force_refresh:
        key = ",".join(want)
        cached = _detail_cache.get(key)
        if cached and (now - cached[0]) < DETAIL_CACHE_TTL_SECONDS:
            payload = dict(cached[1])
            payload["cached"] = True
            return payload

    if not want and _cache and not force_refresh and (now - _cache_at) < CACHE_TTL_SECONDS:
        return _cache

    all_symbols = _covered_warrant_symbols()
    source_symbols = want or all_symbols
    items: list[dict[str, Any]] = []
    for sym in source_symbols:
        base = static.get(sym, {})
        if want:
            quote = _quote_warrant(sym) or {"code": sym, "source": "vnstock-list"}
            merged = {**base, **quote}
        else:
            # Fast catalog mode: do not quote every warrant; search only needs code/underlying.
            merged = {**base, "code": sym, "source": base.get("source") or "vnstock-list"}
        merged.setdefault("underlying", base.get("underlying") or _infer_underlying(sym))
        enriched = enrich_warrant(merged) if want else merged
        if not _is_active_warrant(enriched):
            continue
        items.append(enriched)

    # Include uploaded static items missing from VNStock list.
    if not want:
        existing = {str(item.get("code") or "").upper() for item in items}
        for code, item in static.items():
            if code and code not in existing and _is_active_warrant(item):
                items.append(item)

    payload = {"updatedAt": datetime.now().isoformat(), "items": items, "cached": False, "ttlSeconds": CACHE_TTL_SECONDS, "detailMode": bool(want)}
    if want:
        _detail_cache[",".join(want)] = (now, payload)
    else:
        _cache = payload
        _cache_at = now
    return payload
