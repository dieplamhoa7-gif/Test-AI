from __future__ import annotations
"""
LH2 v6 - Leader Momentum Breakout, expanded indicators + anchored walk-forward.

Cß║úi tiß║┐n so vß╗¢i v4/v5:
  * Bß╗Ö chß╗ë b├ío mß╗ƒ rß╗Öng: th├¬m ADX14, RSI14, ATR%, distance-from-MA (extension),
    MACD hist, Bollinger-width percentile (squeeze), nearHigh252, MA50 alignment,
    market regime (index > MA50), v├á RS-RANK percentile (xß║┐p hß║íng momentum
    cross-sectional theo ng├áy) thay cho band RS tuyß╗çt ─æß╗æi phß╗Ñ thuß╗Öc regime.
  * Walk-forward kiß╗âu anchored: tß╗æi ╞░u tr├¬n IS (2023-2024), kiß╗âm chß╗⌐ng OOS
    (2025-2026). Backtest in ra IS / OOS / FULL ri├¬ng ─æß╗â lß╗Ö overfit thß║¡t sß╗▒.
  * Exit tham sß╗æ h├│a: classic target/stop + failure-exit, hoß║╖c ATR trailing.

Kß║╛T LUß║¼N QUAN TRß╗îNG (─æ├ú chß╗⌐ng minh bß║▒ng grid search >300k tß╗ò hß╗úp):
  Mß╗Ñc ti├¬u winrate > 70% V├Ç avg return > 5% ─Éß╗ÆNG THß╗£I l├á KH├öNG ─Éß║áT ─É╞»ß╗óC mß╗Öt
  c├ích bß╗ün vß╗»ng (>= ~12 lß╗çnh) tr├¬n VN100 2023-2026 ß╗ƒ khung long-only breakout.
  Trß║ºn WR ß╗ƒ >=20 lß╗çnh chß╗ë ~65-67%; con sß╗æ 75%/6.2% cß╗ºa v5 chß╗ë l├á 12 lß╗çnh
  (small-sample, hß║ºu hß║┐t r╞íi v├áo s├│ng t─âng 2023) -> overfit, 0 lß╗çnh 2025-2026.
  v6 chß╗ìn cß║Ñu h├¼nh ROBUST nhß║Ñt (d╞░╞íng cß║ú IS lß║½n OOS) thay v├¼ ├⌐p mß╗Öt con sß╗æ ß║úo.

C├ích chß║íy:
  python build_lh2_v6.py                 # preset mß║╖c ─æß╗ïnh = BALANCED
  python build_lh2_v6.py --preset HIGH_FREQ
File data cß║ºn c├│ cß║ính script (hoß║╖c trong ./data/): vn100_history_from_2023.json
"""
import json, argparse
from pathlib import Path
import numpy as np
import pandas as pd

# ----------------------------- config -----------------------------------
HERE = Path(__file__).resolve().parent
def find_data() -> Path:
    for p in (HERE / "vn100_history_from_2023.json",
              HERE / "data" / "vn100_history_from_2023.json"):
        if p.exists():
            return p
    raise FileNotFoundError("Kh├┤ng t├¼m thß║Ñy vn100_history_from_2023.json cß║ính script hoß║╖c trong ./data/")

FEE = 0.5          # ph├¡ + slippage round-trip, %/lß╗çnh
MIN_HOLD = 3       # sß╗æ phi├¬n tß╗æi thiß╗âu tr╞░ß╗¢c khi cho stop/target khß╗¢p
HORIZON = 60       # sß╗æ phi├¬n tß╗æi ─æa quan s├ít sau entry
START = pd.Timestamp("2023-01-01")
END   = pd.Timestamp("2026-06-01")
IS_END = pd.Timestamp("2025-01-01")   # in-sample: 2023-2024 ; out-of-sample: 2025+

# Mß╗ùi preset gß╗ôm bß╗Ö lß╗ìc entry + cß║Ñu h├¼nh exit. Tß║Ñt cß║ú ng╞░ß╗íng ─æ╞░ß╗úc t├¼m bß║▒ng
# random search tr├¬n IS rß╗ôi kiß╗âm OOS (xem README_LH2_V6.md).
PRESETS = {
    # ROBUST mß║╖c ─æß╗ïnh: ~24 lß╗çnh, FULL WR ~58% / avg ~4.0%, d╞░╞íng cß║ú IS lß║½n OOS.
    "BALANCED": dict(
        entry=dict(rsRank=70, volLo=1.8, volHi=2.5, obv=0.9, vwap=0.6, breadth=55,
                   rangePos=0.90, adx=20, rsiLo=50, rsiHi=100, ext=99, nearHigh=0.95,
                   regime=False, trend=False, macd=False, squeeze=1.0),
        exit=dict(target=1.12, stop=0.95, follow=1.03, trailAtr=0.0, trailArm=99.0, maxHold=60),
    ),
    # Nhiß╗üu lß╗çnh h╞ín (~68), WR OOS cao h╞ín (~65%) nh╞░ng avg thß║Ñp (~1.4%): ╞░u ti├¬n tß║ºn suß║Ñt.
    "HIGH_FREQ": dict(
        entry=dict(rsRank=50, volLo=1.8, volHi=3.0, obv=0.3, vwap=0.6, breadth=55,
                   rangePos=0.0, adx=30, rsiLo=50, rsiHi=100, ext=99, nearHigh=0.95,
                   regime=True, trend=False, macd=True, squeeze=1.0),
        exit=dict(target=1.10, stop=0.96, follow=0.99, trailAtr=2.0, trailArm=1.04, maxHold=45),
    ),
}

# ----------------------------- helpers -----------------------------------
def f(v, d=0.0):
    try:
        if v is None or pd.isna(v):
            return d
        return float(v)
    except Exception:
        return d

def r(v, n=2):
    try:
        return round(float(v), n)
    except Exception:
        return None

def wilder(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()

def atomic(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

# ----------------------------- indicators --------------------------------
def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df.close.astype(float); h = df.high.astype(float)
    l = df.low.astype(float);   v = df.volume.astype(float)
    df["ma20"] = c.rolling(20).mean(); df["ma50"] = c.rolling(50).mean()
    df["ret20"] = c.pct_change(20, fill_method=None) * 100
    df["vol20"] = v.rolling(20).mean(); df["volRatio"] = v / df["vol20"].replace(0, np.nan)
    df["high20_prev"] = h.rolling(20).max().shift(1)
    df["high50_prev"] = h.rolling(50).max().shift(1)
    df["high252"] = h.rolling(252).max()
    df["rangePos60"] = (c - l.rolling(60).min()) / (h.rolling(60).max() - l.rolling(60).min()).replace(0, np.nan)
    direction = c.diff().fillna(0).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    df["obv"] = (direction * v).cumsum()
    df["obvSlope20"] = df["obv"].diff(20) / df["obv"].abs().rolling(60).mean().replace(0, np.nan)
    tp = (h + l + c) / 3
    df["vwap20"] = (tp * v).rolling(20).sum() / v.rolling(20).sum().replace(0, np.nan)
    df["vwapSlope5"] = df["vwap20"].diff(5) / df["vwap20"].shift(5) * 100
    # RSI14
    d = c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
    rs = wilder(up, 14) / wilder(dn, 14).replace(0, np.nan)
    df["rsi14"] = 100 - 100 / (1 + rs)
    # ATR14 + extension
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    atr = wilder(tr, 14); df["atr14"] = atr; df["atrPct"] = atr / c * 100
    df["distMa20Atr"] = (c - df["ma20"]) / atr.replace(0, np.nan)
    # ADX14
    upMove = h.diff(); dnMove = -l.diff()
    plusDM = ((upMove > dnMove) & (upMove > 0)) * upMove
    minusDM = ((dnMove > upMove) & (dnMove > 0)) * dnMove
    pdi = 100 * wilder(plusDM, 14) / atr.replace(0, np.nan)
    mdi = 100 * wilder(minusDM, 14) / atr.replace(0, np.nan)
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    df["adx14"] = wilder(dx, 14)
    # MACD histogram
    ema12 = c.ewm(span=12, adjust=False).mean(); ema26 = c.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26; sig = macd.ewm(span=9, adjust=False).mean()
    df["macdHist"] = macd - sig
    # Bollinger width percentile (squeeze)
    std20 = c.rolling(20).std()
    df["bbWidth"] = (2 * std20) / df["ma20"].replace(0, np.nan) * 100
    df["bbWidthPct"] = df["bbWidth"].rolling(120).rank(pct=True)
    df["nearHigh252"] = c / df["high252"].replace(0, np.nan)
    return df

def load(src: Path):
    data = json.loads(src.read_text(encoding="utf-8")).get("symbols", {})
    out = {}
    for sym, o in data.items():
        rows = o.get("rows") or []
        if len(rows) < 260:
            continue
        df = pd.DataFrame(rows); df["time"] = pd.to_datetime(df["time"])
        for cc in ["open", "high", "low", "close", "volume"]:
            df[cc] = pd.to_numeric(df[cc], errors="coerce")
        out[sym] = enrich(df.sort_values("time").reset_index(drop=True))
    return out

def market(hist):
    closes = [df[["time", "close"]].rename(columns={"close": s}).set_index("time")
              for s, df in hist.items()]
    close = pd.concat(closes, axis=1).sort_index()
    ret = close.pct_change(fill_method=None)
    idx = (1 + ret.mean(axis=1).fillna(0)).cumprod() * 1000
    idxMa50 = idx.rolling(50).mean()
    mkt = pd.DataFrame({
        "mktRet20": idx.pct_change(20, fill_method=None) * 100,
        "breadth": (close > close.rolling(20).mean()).sum(axis=1) / close.count(axis=1) * 100,
        "regime": (idx > idxMa50).astype(int),
    })
    ret20 = pd.concat([df[["time", "ret20"]].rename(columns={"ret20": s}).set_index("time")
                       for s, df in hist.items()], axis=1).sort_index()
    rsRank = ret20.rank(axis=1, pct=True) * 100   # percentile momentum cross-sectional
    return mkt, rsRank

# ----------------------------- signal & exit -----------------------------
def passes(row, rs_rank, breadth, regime, e) -> bool:
    breakout = f(row.close) > f(row.high20_prev) or f(row.close) > f(row.high50_prev)
    if not breakout:
        return False
    ok = (rs_rank >= e["rsRank"]
          and e["volLo"] <= f(row.volRatio) <= e["volHi"]
          and f(row.obvSlope20) >= e["obv"]
          and f(row.vwapSlope5) >= e["vwap"]
          and breadth >= e["breadth"]
          and f(row.rangePos60) >= e["rangePos"]
          and f(row.adx14) >= e["adx"]
          and e["rsiLo"] <= f(row.rsi14) <= e["rsiHi"]
          and f(row.distMa20Atr) <= e["ext"]
          and f(row.nearHigh252) >= e["nearHigh"])
    if not ok:
        return False
    if e["regime"] and regime != 1:
        return False
    if e["trend"] and not (f(row.close) >= f(row.ma50) and f(row.ma20) >= f(row.ma50)):
        return False
    if e["macd"] and f(row.macdHist) < 0:
        return False
    if e["squeeze"] < 1 and not (f(row.bbWidthPct) <= e["squeeze"]):
        return False
    return True

def sim_exit(df, i, x):
    if i + 1 >= len(df):
        return None
    entry = f(df.iloc[i + 1].close)
    if entry <= 0:
        return None
    tgt = entry * x["target"]; stp = entry * x["stop"]
    zone = max(f(df.iloc[i].high20_prev), f(df.iloc[i].high50_prev))
    atr = f(df.iloc[i + 1].atr14, f(df.iloc[i].atr14))
    fut = df.iloc[i + 2:i + 2 + HORIZON]
    peak = entry
    for n, (_, row) in enumerate(fut.iterrows(), 1):
        if n > x["maxHold"]:
            break
        c = f(row.close); hi = f(row.high); lo = f(row.low)
        if hi > peak:
            peak = hi
        # failure exit (cß║»t sß╗¢m khi breakout hß╗Ång)
        if n >= 3 and c < entry * x["follow"] and (c < zone or c < f(row.ma20) or c < f(row.vwap20)):
            return {"netPnlPct": r((c / entry - 1) * 100 - FEE), "holdSessions": n,
                    "exitDate": str(row.time.date()), "exitType": "failure_exit"}
        if n < MIN_HOLD:
            continue
        if x["trailAtr"] > 0 and peak >= entry * x["trailArm"]:
            ts = peak - x["trailAtr"] * atr
            if lo <= ts:
                return {"netPnlPct": r((ts / entry - 1) * 100 - FEE), "holdSessions": n,
                        "exitDate": str(row.time.date()), "exitType": "atr_trail"}
        if lo <= stp:
            return {"netPnlPct": r((x["stop"] - 1) * 100 - FEE), "holdSessions": n,
                    "exitDate": str(row.time.date()), "exitType": "stop"}
        if hi >= tgt:
            return {"netPnlPct": r((x["target"] - 1) * 100 - FEE), "holdSessions": n,
                    "exitDate": str(row.time.date()), "exitType": "target"}
    if fut.empty:
        return None
    last = fut.iloc[min(x["maxHold"], len(fut)) - 1]
    return {"netPnlPct": r((f(last.close) / entry - 1) * 100 - FEE),
            "holdSessions": int(min(x["maxHold"], len(fut))),
            "exitDate": str(last.time.date()), "exitType": "timeout"}

def summary(rows):
    n = len(rows)
    vals = [f(x.get("netPnlPct")) for x in rows]
    w = sum(v > 0 for v in vals)
    return {"trades": n, "wins": w, "losses": n - w,
            "winRatePct": r(w / n * 100) if n else 0,
            "avgNetPnlPct": r(sum(vals) / n) if n else 0,
            "sumNetPnlPct": r(sum(vals)),
            "avgHold": r(sum(f(x.get("holdSessions")) for x in rows) / n) if n else 0}

# ----------------------------- main backtest -----------------------------
def run(preset_name: str):
    preset = PRESETS[preset_name]
    e, x = preset["entry"], preset["exit"]
    src = find_data()
    hist = load(src)
    mkt, rsRank = market(hist)
    # market lookups by date (nhanh h╞ín .loc trong v├▓ng lß║╖p)
    mret = mkt["mktRet20"].to_dict(); mbr = mkt["breadth"].to_dict(); mreg = mkt["regime"].to_dict()
    trades, today = [], []
    candidates = 0
    for sym, df in hist.items():
        n = len(df)
        # arrays cß╗Öt (tr├ính iloc trong hot-loop)
        A = {c: df[c].to_numpy() for c in df.columns if c != "time"}
        times = df["time"].to_numpy()
        rr_sym = rsRank[sym].reindex(df["time"]).to_numpy() if sym in rsRank.columns else np.full(n, np.nan)
        used = -1
        for i in range(200, n - HORIZON - 2):
            if i <= used:
                continue
            date = df["time"].iloc[i]
            if date < START or date >= END or date not in mret:
                continue
            row = type("R", (), {c: A[c][i] for c in A})()  # row-like vß╗¢i thuß╗Öc t├¡nh cß╗Öt
            rrank = f(rr_sym[i]); br = f(mbr[date]); reg = int(mreg[date])
            if not passes(row, rrank, br, reg, e):
                continue
            candidates += 1
            ex = sim_exit(df, i, x)
            if not ex:
                continue
            rs = f(A["ret20"][i]) - f(mret[date])
            trades.append({**ex, "symbol": sym, "signalDate": str(pd.Timestamp(date).date()),
                           "entryDate": str(pd.Timestamp(times[i + 1]).date()),
                           "entry": r(A["close"][i + 1]),
                           "scores": {"rsRankPct": r(rrank), "rel20Pct": r(rs),
                                      "volumeRatio": r(A["volRatio"][i]), "obvSlope20": r(A["obvSlope20"][i], 4),
                                      "vwapSlope5": r(A["vwapSlope5"][i]), "adx14": r(A["adx14"][i]),
                                      "rsi14": r(A["rsi14"][i]), "breadth": r(br),
                                      "nearHigh252": r(A["nearHigh252"][i]), "rangePos60": r(A["rangePos60"][i])}})
            used = i + ex["holdSessions"] + 1
        # scan phi├¬n mß╗¢i nhß║Ñt
        i = n - 1
        date = df["time"].iloc[i]
        if date in mret:
            row = type("R", (), {c: A[c][i] for c in A})()
            rrank = f(rr_sym[i]); br = f(mbr[date]); reg = int(mreg[date])
            if passes(row, rrank, br, reg, e):
                today.append({"symbol": sym, "date": str(pd.Timestamp(date).date()), "close": r(A["close"][i]),
                              "action": f"LH2_V6_{preset_name}_BUY_CANDIDATE",
                              "scores": {"rsRankPct": r(rrank), "volumeRatio": r(A["volRatio"][i]),
                                         "adx14": r(A["adx14"][i]), "rsi14": r(A["rsi14"][i]), "breadth": r(br)}})

    is_rows  = [t for t in trades if pd.Timestamp(t["signalDate"]) < IS_END]
    oos_rows = [t for t in trades if pd.Timestamp(t["signalDate"]) >= IS_END]
    windows = {"2023": ("2023-01-01", "2024-01-01"), "2024": ("2024-01-01", "2025-01-01"),
               "2025": ("2025-01-01", "2026-01-01"), "2026_ytd": ("2026-01-01", "2026-07-01")}
    res = {"status": "completed", "preset": preset_name, "params": preset,
           "candidates": candidates,
           "walkForward": {"IS_2023_2024": summary(is_rows),
                           "OOS_2025_2026": summary(oos_rows),
                           "FULL_2023_now": summary(trades)},
           "byYear": {k: summary([t for t in trades
                                  if pd.Timestamp(a) <= pd.Timestamp(t["signalDate"]) < pd.Timestamp(b)])
                      for k, (a, b) in windows.items()},
           "trades": trades}
    out = HERE / f"lh2_v6_{preset_name.lower()}_backtest.json"
    scan = HERE / f"lh2_v6_{preset_name.lower()}_today_scan.json"
    atomic(out, res)
    atomic(scan, {"status": "completed", "count": len(today), "signals": today})
    print(json.dumps({"preset": preset_name, "candidates": candidates,
                      "walkForward": res["walkForward"], "byYear": res["byYear"],
                      "todayCount": len(today)}, ensure_ascii=False, indent=2))
    print(f"\n[saved] {out.name} , {scan.name}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="BALANCED", choices=list(PRESETS))
    run(ap.parse_args().preset)
