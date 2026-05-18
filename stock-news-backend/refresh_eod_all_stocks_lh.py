from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from vnstock import Listing, Quote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PUBLIC = ROOT / "firebase_public" / "data"
TZ = timezone(timedelta(hours=7))
START = "2025-01-01"
MAX_WORKERS = 8


def sf(v: Any) -> float | None:
    try:
        if v is None or v == "":
            return None
        x = float(v)
        if pd.isna(x):
            return None
        return x
    except Exception:
        return None


def round_or_none(v: Any, n: int = 2):
    x = sf(v)
    return round(x, n) if x is not None else None


def calc_indicators(df: pd.DataFrame) -> dict[str, Any]:
    d = df.copy().sort_values("time").reset_index(drop=True)
    for c in ["open", "high", "low", "close", "volume"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    close, high, low, vol = d.close, d.high, d.low, d.volume
    ma = lambda n: close.rolling(n).mean()
    std20 = close.rolling(20).std(ddof=1)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi14 = 100 - 100 / (1 + gain / loss.replace(0, float("nan")))
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0)
    minus_dm = down.where((down > up) & (down > 0), 0)
    atr_ewm = tr.ewm(alpha=1 / 14, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr_ewm
    minus_di = 100 * minus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr_ewm
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di)) * 100
    adx14 = dx.ewm(alpha=1 / 14, adjust=False).mean()

    price = sf(close.iloc[-1]) or 0
    levels = []
    for i in range(2, len(d) - 2):
        if i < len(d) - 160:
            continue
        if low.iloc[i] <= low.iloc[i - 2 : i + 3].min():
            levels.append(("S", float(low.iloc[i]), str(d.iloc[i].time)[:10]))
        if high.iloc[i] >= high.iloc[i - 2 : i + 3].max():
            levels.append(("R", float(high.iloc[i]), str(d.iloc[i].time)[:10]))
    supports = sorted([x for x in levels if x[0] == "S" and x[1] < price * 1.01], key=lambda x: abs(price - x[1]))[:8]
    resistances = sorted([x for x in levels if x[0] == "R" and x[1] > price * 0.99], key=lambda x: abs(x[1] - price))[:8]
    last = d.iloc[-1]
    prev_close = sf(close.iloc[-2]) if len(d) >= 2 else None
    change_pct = ((price / prev_close - 1) * 100) if prev_close else None
    return {
        "date": str(pd.to_datetime(last.time).date()),
        "open": round_or_none(last.open),
        "high": round_or_none(last.high),
        "low": round_or_none(last.low),
        "close": round_or_none(price),
        "price": round_or_none(price),
        "volume": int(sf(last.volume) or 0),
        "changePct": round_or_none(change_pct),
        "ma10": round_or_none(ma(10).iloc[-1]),
        "ma20": round_or_none(ma(20).iloc[-1]),
        "ma50": round_or_none(ma(50).iloc[-1]),
        "ma100": round_or_none(ma(100).iloc[-1]),
        "ma200": round_or_none(ma(200).iloc[-1]),
        "bbUpper": round_or_none(ma(20).iloc[-1] + 2 * std20.iloc[-1]),
        "bbMid": round_or_none(ma(20).iloc[-1]),
        "bbLower": round_or_none(ma(20).iloc[-1] - 2 * std20.iloc[-1]),
        "rsi14": round_or_none(rsi14.iloc[-1]),
        "macd": round_or_none(macd.iloc[-1], 4),
        "macdSignal": round_or_none(macd_signal.iloc[-1], 4),
        "macdHist": round_or_none((macd - macd_signal).iloc[-1], 4),
        "adx14": round_or_none(adx14.iloc[-1]),
        "plusDI": round_or_none(plus_di.iloc[-1]),
        "minusDI": round_or_none(minus_di.iloc[-1]),
        "atr14": round_or_none(atr14.iloc[-1]),
        "avgVol20": int(sf(vol.rolling(20).mean().iloc[-1]) or 0),
        "supportLevelsDay": [round(x[1], 2) for x in supports],
        "resistanceLevelsDay": [round(x[1], 2) for x in resistances],
        "supportSources": supports,
        "resistanceSources": resistances,
    }


def fetch_symbol(row: dict[str, Any], end: str) -> tuple[str, dict[str, Any] | None, str | None]:
    sym = str(row["symbol"]).upper().strip()
    try:
        df = Quote(symbol=sym, source="VCI").history(start=START, end=end, interval="1D")
        if df is None or df.empty or len(df) < 30:
            return sym, None, "missing/short history"
        df = df.rename(columns={"time": "time"})
        out = {"symbol": sym, "exchange": row.get("exchange"), "organName": row.get("organ_name")}
        out.update(calc_indicators(df))
        return sym, out, None
    except Exception as exc:
        return sym, None, str(exc)[:180]


def main() -> None:
    end = datetime.now(TZ).strftime("%Y-%m-%d")
    listing = Listing().symbols_by_exchange()
    listing = listing[(listing["type"] == "stock") & (listing["exchange"].isin(["HOSE", "HNX"]))]
    rows = listing[["symbol", "exchange", "organ_name"]].drop_duplicates("symbol").to_dict("records")
    items: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_symbol, r, end): r for r in rows}
        for i, fut in enumerate(as_completed(futures), 1):
            sym, item, err = fut.result()
            if item:
                items.append(item)
            else:
                errors.append({"symbol": sym, "error": err or "unknown"})
            if i % 50 == 0:
                print(f"processed {i}/{len(rows)} items={len(items)} errors={len(errors)}", flush=True)
            time.sleep(0.02)
    items.sort(key=lambda x: (x.get("exchange") or "", x.get("symbol") or ""))
    now = datetime.now(TZ).isoformat(timespec="seconds")
    payload = {"updatedAt": now, "source": "vnstock-vci-eod-all-hose-hnx", "start": START, "end": end, "count": len(items), "items": items, "errors": errors[:200], "errorCount": len(errors)}
    for path in [DATA / "eod_all_stocks_hose_hnx.json", PUBLIC / "eod_all_stocks_hose_hnx.json"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"updatedAt": now, "symbols": len(rows), "items": len(items), "errors": len(errors)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
