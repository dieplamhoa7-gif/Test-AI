from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from vnstock import Listing, Quote, Trading

try:
    import ml_core12_group_combo_search as core12
except Exception:
    core12 = None

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PUBLIC = ROOT / "firebase_public" / "data"
TZ = timezone(timedelta(hours=7))
START = "2025-01-01"
MAX_WORKERS = 1
REQUEST_DELAY_SECONDS = 3.3
TOP_N = 200


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



def calc_core12(sym: str, df: pd.DataFrame) -> dict[str, Any]:
    cfg_path = DATA / "core12_group_combo_config.json"
    if not cfg_path.exists():
        return {"available": False, "reason": "missing core12 config"}
    try:
        if core12 is None:
            return {"available": False, "reason": "core12 module unavailable"}
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")).get("selected", {})
        sector = core12.sg(sym)
        tasks: dict[str, Any] = {}
        basic = None
        for task in ["RS", "D1A", "D1S"]:
            use_sector = sector if sector in cfg and task in cfg.get(sector, {}) else ("ALL" if task in cfg.get("ALL", {}) else None)
            if not use_sector:
                continue
            rec = cfg[use_sector][task]
            indicators = rec.get("indicators") or []
            params_map = rec.get("indicatorParams") or {}
            values: dict[str, Any] = {}
            signals = []
            pos = neg = neu = 0
            for ind in indicators:
                if ind == "SR_CLUSTER":
                    if basic is None:
                        basic = calc_indicators(df)
                    price = sf(df.close.iloc[-1]) or 0
                    supports = basic.get("supportLevelsDay") or []
                    resistances = basic.get("resistanceLevelsDay") or []
                    s1 = supports[0] if supports else None
                    r1 = resistances[0] if resistances else None
                    near_s = bool(s1 and price <= s1 * 1.018)
                    broken = bool(s1 and price < s1 * 0.992)
                    sig = 1 if near_s and not broken else (-1 if broken else 0)
                    values[ind] = {"nearSupport": near_s, "supportBroken": broken, "S1": s1, "R1": r1}
                else:
                    out = core12.calc(df, ind, params_map.get(ind, []) or [], {})
                    last = {k: round_or_none(v.iloc[-1], 4) if hasattr(v, "iloc") else None for k, v in out.items()}
                    values[ind] = last
                    score = 0
                    for k, v in last.items():
                        x = sf(v)
                        if x is None:
                            continue
                        kl = k.lower()
                        if any(a in kl for a in ["dist", "cloud_pos", "slope", "hist", "trix", "roc", "mom", "spread", "tk"]):
                            score += 1 if x > 0 else (-1 if x < 0 else 0)
                        elif "rsi" in kl:
                            score += 1 if 40 <= x <= 70 else (-1 if x < 35 else 0)
                        elif "mfi" in kl or "cmf" in kl:
                            score += 1 if x >= 45 else -1
                        elif "dir" in kl:
                            score += 1 if x > 0 else -1
                    sig = 1 if score > 0 else (-1 if score < 0 else 0)
                pos += 1 if sig > 0 else 0
                neg += 1 if sig < 0 else 0
                neu += 1 if sig == 0 else 0
                signals.append({"indicator": ind, "signal": sig})
            total = max(1, pos + neg + neu)
            tasks[task] = {
                "sectorGroup": sector,
                "configSector": use_sector,
                "indicators": indicators,
                "model": rec.get("model"),
                "mode": rec.get("mode"),
                "avgPrecision": rec.get("avgPrecision"),
                "avgRecall": rec.get("avgRecall"),
                "positive": pos,
                "negative": neg,
                "neutral": neu,
                "score": round((pos - neg) / total * 100, 2),
                "signals": signals,
                "values": values,
            }
        return {"available": True, "sectorGroup": sector, "tasks": tasks}
    except Exception as exc:
        return {"available": False, "reason": str(exc)[:180]}

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


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = ["_".join([str(x) for x in col if str(x) != ""]).strip("_") for col in df.columns]
    return df


def pick_col(df: pd.DataFrame, *names: str) -> str | None:
    lower = {str(c).lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    for c in df.columns:
        lc = str(c).lower()
        if any(name.lower() in lc for name in names):
            return c
    return None


def top_market_cap_rows(listing: pd.DataFrame) -> list[dict[str, Any]]:
    base = listing[["symbol", "exchange", "organ_name"]].drop_duplicates("symbol").copy()
    records: list[dict[str, Any]] = []
    symbols = base["symbol"].astype(str).str.upper().tolist()
    meta = {str(r["symbol"]).upper(): r for r in base.to_dict("records")}
    trading = Trading(source="VCI")
    for start in range(0, len(symbols), 50):
        chunk = symbols[start:start + 50]
        try:
            board = flatten_columns(trading.price_board(chunk))
            sym_col = pick_col(board, "listing_symbol", "symbol")
            share_col = pick_col(board, "listing_listed_share", "listed_share")
            price_col = pick_col(board, "match_match_price", "match_price")
            ref_col = pick_col(board, "listing_ref_price", "reference_price", "ref_price")
            if not sym_col or not share_col:
                continue
            for _, row in board.iterrows():
                sym = str(row.get(sym_col) or "").upper().strip()
                if not sym or sym not in meta:
                    continue
                shares = sf(row.get(share_col)) or 0
                price = sf(row.get(price_col)) or sf(row.get(ref_col)) or 0
                market_cap = shares * price
                rec = dict(meta[sym])
                rec["listedShare"] = int(shares) if shares else None
                rec["marketCap"] = market_cap
                records.append(rec)
        except Exception as exc:
            print("price_board chunk failed", chunk[:3], str(exc)[:120], flush=True)
    if len(records) < TOP_N:
        print(f"market-cap board only returned {len(records)} rows; falling back to listing order for missing names", flush=True)
        seen = {r["symbol"] for r in records}
        for r in base.to_dict("records"):
            if r["symbol"] not in seen:
                rec = dict(r)
                rec["marketCap"] = 0
                records.append(rec)
    records.sort(key=lambda r: sf(r.get("marketCap")) or 0, reverse=True)
    return records[:TOP_N]


def fetch_symbol(row: dict[str, Any], end: str) -> tuple[str, dict[str, Any] | None, str | None]:
    sym = str(row["symbol"]).upper().strip()
    try:
        time.sleep(REQUEST_DELAY_SECONDS)
        df = Quote(symbol=sym, source="VCI").history(start=START, end=end, interval="1D")
        if df is None or df.empty or len(df) < 30:
            return sym, None, "missing/short history"
        df = df.rename(columns={"time": "time"})
        out = {"symbol": sym, "exchange": row.get("exchange"), "organName": row.get("organ_name"), "marketCap": round_or_none(row.get("marketCap"), 0), "listedShare": row.get("listedShare")}
        out.update(calc_indicators(df))
        out["core12"] = calc_core12(sym, df)
        return sym, out, None
    except Exception as exc:
        return sym, None, str(exc)[:180]


def main() -> None:
    end = datetime.now(TZ).strftime("%Y-%m-%d")
    listing = Listing().symbols_by_exchange()
    listing = listing[(listing["type"] == "stock") & (listing["exchange"].isin(["HOSE", "HNX"]))]
    rows = top_market_cap_rows(listing)
    items: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for i, row in enumerate(rows, 1):
        sym, item, err = fetch_symbol(row, end)
        if item:
            items.append(item)
        else:
            errors.append({"symbol": sym, "error": err or "unknown"})
        if i % 20 == 0 or i == len(rows):
            print(f"processed {i}/{len(rows)} items={len(items)} errors={len(errors)}", flush=True)
    items.sort(key=lambda x: (x.get("exchange") or "", x.get("symbol") or ""))
    now = datetime.now(TZ).isoformat(timespec="seconds")
    payload = {"updatedAt": now, "source": "vnstock-vci-eod-top200-marketcap-hose-hnx", "universeRule": "Top 200 HOSE+HNX by market cap from VCI price board after 15:15 ICT", "topN": TOP_N, "start": START, "end": end, "count": len(items), "items": items, "errors": errors[:200], "errorCount": len(errors)}
    for path in [DATA / "eod_top200_marketcap_hose_hnx.json", PUBLIC / "eod_top200_marketcap_hose_hnx.json", DATA / "eod_all_stocks_hose_hnx.json", PUBLIC / "eod_all_stocks_hose_hnx.json"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"updatedAt": now, "symbols": len(rows), "items": len(items), "errors": len(errors)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
