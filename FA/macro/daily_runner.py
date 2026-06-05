"""
Daily Macro Runner v2 — LH Investment
======================================
Orchestrator chạy mỗi sáng, tổng hợp từ tất cả fetchers:

  Pinetree Morning Brief  →  rates + FX + global indices + VN market + news
  VCB FX XML              →  tỷ giá chính xác (fallback/supplement)
  yfinance                →  VIX, DXY, US10Y, Brent, Gold realtime
  VN Market (SSI/DNSE/VnDirect) → VNINDEX OHLCV, foreign flow
  SBV Rates               →  lãi suất liên NH (multi-source fallback)
  World Bank (weekly)     →  GDP, CPI, FDI annual context

Output: FA/data/history/YYYY-MM-DD.json  +  console report

Usage:
    python macro/daily_runner.py
    python macro/daily_runner.py --date 2026-06-05 --report
    python macro/daily_runner.py --skip-worldbank     # bỏ qua World Bank (chậm)
    python macro/daily_runner.py --only-pinetree       # chỉ Pinetree + score
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from macro.fetchers import pinetree as pinetree_fetcher
from macro.fetchers import yfinance_global as yf_fetcher
from macro.fetchers import vcb_fx
from macro.fetchers import vnstock_market
from macro.fetchers import sbv_rates
from macro.fetchers import sbv_omo
from macro.fetchers import sbv_liquidity
from macro.fetchers import fiinprox_excel
from macro.fetchers import tradingeconomics_browser
from macro.fetchers import pinetree_archive
from macro.scoring import regime_score as scorer
from macro.storage import macro_history as history

# World Bank fetch weekly only (data is slow-moving)
_WORLDBANK_CACHE_DAYS = 7


def _should_fetch_worldbank() -> bool:
    """Only fetch WB if no cached data from the past week."""
    try:
        hist_dir = Path(__file__).resolve().parents[1] / "data" / "history"
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=_WORLDBANK_CACHE_DAYS)
        for f in sorted(hist_dir.glob("????.??.??.json"), reverse=True):
            d = datetime.strptime(f.stem, "%Y-%m-%d").date()
            if d >= cutoff:
                snap = json.loads(f.read_text(encoding="utf-8"))
                if snap.get("worldbank", {}).get("data"):
                    return False  # Recent WB data exists
    except Exception:
        pass
    return True


def run(
    d: date | None = None,
    skip_yfinance: bool = False,
    skip_worldbank: bool = False,
    only_pinetree: bool = False,
) -> dict[str, Any]:
    d = d or date.today()
    ts = lambda: datetime.now().strftime("%H:%M:%S")

    snapshot: dict[str, Any] = {
        "date": str(d),
        "fetchedAt": datetime.now().isoformat(),
        "schemaVersion": "2.0",
    }

    # ── 1. Pinetree Morning Brief ─────────────────────────────────────
    print(f"[{ts()}] Fetching Pinetree {d} ...")
    pinetree_data: dict = {}
    try:
        pinetree_data = pinetree_fetcher.fetch(d)
        snapshot["pinetreeStatus"] = "ok"
        n_metrics = sum(1 for v in pinetree_data.values()
                        if isinstance(v, dict) and v.get("value") is not None)
        print(f"  ✓ Pinetree: {n_metrics} metrics, {len(pinetree_data.get('newsHeadlines',[]))} headlines")
    except Exception as e:
        snapshot["pinetreeStatus"] = "error"
        snapshot["pinetreeError"] = str(e)
        print(f"  ✗ Pinetree failed: {e}")
    snapshot["pinetree"] = pinetree_data

    if only_pinetree:
        score_result = scorer.compute(pinetree_data, {})
        snapshot.update(score_result)
        path = history.save(snapshot, d)
        print(f"[{ts()}] Saved → {path}")
        return snapshot

    # ── 2. VCB FX ─────────────────────────────────────────────────────
    print(f"[{ts()}] Fetching VCB FX rates ...")
    vcb_data: dict = {}
    try:
        vcb_data = vcb_fx.fetch()
        rates_ok = sum(1 for v in vcb_data.values()
                       if isinstance(v, dict) and v.get("sell") is not None)
        print(f"  ✓ VCB FX: {rates_ok} pairs")
    except Exception as e:
        vcb_data = {"error": str(e)}
        print(f"  ✗ VCB FX failed: {e}")
    snapshot["vcbFx"] = vcb_data

    # ── 3. yfinance global ────────────────────────────────────────────
    global_data: dict = {}
    if not skip_yfinance:
        print(f"[{ts()}] Fetching yfinance global ...")
        try:
            yf_result = yf_fetcher.fetch_core()
            global_data = yf_result.get("data", {})
            ok_count = sum(1 for v in global_data.values() if v.get("value") is not None)
            print(f"  ✓ yfinance: {ok_count}/{len(global_data)} tickers")
        except Exception as e:
            global_data = {}
            print(f"  ✗ yfinance failed: {e}")
    snapshot["global"] = global_data

    # ── 4. VN Market (SSI/DNSE/VnDirect/vnstock) ─────────────────────
    print(f"[{ts()}] Fetching VN market data ...")
    vn_market: dict = {}
    try:
        vn_market = vnstock_market.fetch()
        if vn_market.get("vnindex", {}).get("value"):
            v = vn_market["vnindex"]
            print(f"  ✓ VNINDEX: {v['value']} ({v.get('change1d_pct', '?'):+.2f}%)"
                  if v.get("change1d_pct") is not None else f"  ✓ VNINDEX: {v['value']}")
        else:
            print(f"  ↘ VN market: {vn_market.get('status', 'no data')}")
    except Exception as e:
        vn_market = {"error": str(e)}
        print(f"  ✗ VN market failed: {e}")
    snapshot["vnMarket"] = vn_market

    # ── 5. SBV rates ──────────────────────────────────────────────────
    print(f"[{ts()}] Fetching SBV/interbank rates ...")
    sbv_data: dict = {}
    try:
        sbv_data = sbv_rates.fetch()
        on = sbv_data.get("overnight") or sbv_data.get("vnd", {}).get("overnight")
        print(f"  ✓ SBV rates: overnight={on}%" if on else f"  ↘ SBV rates: {sbv_data.get('source','?')}")
    except Exception as e:
        sbv_data = {"error": str(e)}
        print(f"  ✗ SBV rates failed: {e}")
    snapshot["sbvRates"] = sbv_data

    # ── 5b. SBV OMO (Nghiệp vụ thị trường mở) ────────────────────────
    print(f"[{ts()}] Fetching SBV OMO ...")
    omo_data: dict = {}
    try:
        omo_data = sbv_omo.fetch()
        net = omo_data.get("totalNetBn")
        omo_type = omo_data.get("omoType", "?")
        if net is not None:
            direction = "BƠM" if net > 0 else "HÚT"
            print(f"  ✓ OMO [{omo_data.get('date','?')}]: {direction} ròng {abs(net):,.2f} tỷ @ {omo_data.get('omoRate','?')}%")
        else:
            print(f"  ↘ OMO: {omo_data.get('status','?')}")
    except Exception as e:
        omo_data = {"error": str(e)}
        print(f"  ✗ OMO failed: {e}")
    snapshot["omoData"] = omo_data

    # ── 5c. SBV liquidity full pack: OMO + tín phiếu + policy + interbank ─
    print(f"[{ts()}] Fetching SBV liquidity full pack ...")
    try:
        liq = sbv_liquidity.fetch(headless=False)
        sbv_liquidity.save(liq)
        snapshot["sbvLiquidity"] = liq
        s = liq.get("summary", {})
        print(f"  ✓ SBV liquidity: RR issue={s.get('reverseRepoIssueBn')} tỷ, T-bill issue={s.get('tbillIssueBn')}, total net={s.get('totalLiquidityNetBn')} tỷ")
    except Exception as e:
        snapshot["sbvLiquidity"] = {"status": "error", "error": str(e)[:200]}
        print(f"  ✗ SBV liquidity full pack failed: {e}")

    # ── 5d. Pinetree archive crawl/update (public morning brief history) ─
    print(f"[{ts()}] Updating Pinetree Morning Brief archive ...")
    try:
        # Initial full crawl is stored under data/pinetree_archive. Daily job only checks newest pages.
        pa = pinetree_archive.crawl(max_pages=3, sleep_s=0.05, incremental=True)
        snapshot["pinetreeArchive"] = pa
        print(f"  ✓ Pinetree archive: {pa.get('postsFetched',0)} posts, {pa.get('rowCount',0)} rows")
    except Exception as e:
        snapshot["pinetreeArchive"] = {"status": "error", "error": str(e)[:200]}
        print(f"  ✗ Pinetree archive failed: {e}")

    # ── 5e. FiinProX manual Excel import (paid/manual source fallback) ───
    print(f"[{ts()}] Importing FiinProX Excel macro timeline ...")
    try:
        fiin = fiinprox_excel.fetch()
        fiin_paths = fiinprox_excel.save_unified(fiin)
        snapshot["fiinproxExcel"] = {
            "status": fiin.get("status"),
            "fileCount": fiin.get("fileCount"),
            "rowCount": fiin.get("rowCount"),
            "indicatorCount": fiin.get("indicatorCount"),
            "outputs": fiin_paths,
            "errors": fiin.get("errors"),
        }
        print(f"  ✓ FiinProX: {fiin.get('rowCount',0)} rows, {fiin.get('indicatorCount',0)} indicators")
    except Exception as e:
        snapshot["fiinproxExcel"] = {"status": "error", "error": str(e)[:200]}
        print(f"  ✗ FiinProX import failed: {e}")

    # ── 6. World Bank (weekly cache) ──────────────────────────────────
    if not skip_worldbank and _should_fetch_worldbank():
        print(f"[{ts()}] Fetching World Bank annual indicators ...")
        try:
            from macro.fetchers import worldbank_macro
            wb_data = worldbank_macro.fetch(years=5)
            n_indicators = len(wb_data.get("data", {}))
            print(f"  ✓ World Bank: {n_indicators} indicators")
            snapshot["worldbank"] = wb_data
        except Exception as e:
            print(f"  ✗ World Bank failed: {e}")
    elif skip_worldbank:
        print(f"[{ts()}] World Bank: skipped")
    else:
        print(f"[{ts()}] World Bank: using cached data (< {_WORLDBANK_CACHE_DAYS} days old)")

    # ── 6b. TradingEconomics visible browser scrape (no login/sub bypass) ─
    print(f"[{ts()}] Fetching TradingEconomics visible macro pages ...")
    try:
        te_data = tradingeconomics_browser.fetch(headless=True)
        te_path = tradingeconomics_browser.save(te_data)
        snapshot["tradingEconomicsVisible"] = {
            "status": te_data.get("status"),
            "count": len(te_data.get("data", {})),
            "out": te_path,
            "errors": te_data.get("errors"),
            "note": te_data.get("note"),
        }
        print(f"  ✓ TradingEconomics visible: {len(te_data.get('data',{}))} pages")
    except Exception as e:
        snapshot["tradingEconomicsVisible"] = {"status": "error", "error": str(e)[:200]}
        print(f"  ✗ TradingEconomics visible failed: {e}")

    # ── 7. Merge best FX & global into scoring input ──────────────────
    # Priority: Pinetree > VCB (FX) > yfinance (global)
    merged_pinetree = dict(pinetree_data)

    # Override FX from VCB if more precise
    for key, vcb_key in [("usdVnd", "usdVnd"), ("eurVnd", "eurVnd"), ("cnyVnd", "cnyVnd")]:
        vcb_val = vcb_data.get(vcb_key, {}).get("sell")
        if vcb_val and not merged_pinetree.get(key, {}).get("value"):
            merged_pinetree[key] = {"value": vcb_val, "change1d": None, "ytd": None, "source": "vcb"}

    # Override global with yfinance when available
    yf_map = {
        "vix":   "vix",
        "sp500": "sp500",
        "brent": "brent",
        "gold":  "gold",
        "us10y": "us10y",
        "dxy":   "dxy",
    }
    for yf_key, pinetree_key in yf_map.items():
        yf_val = global_data.get(yf_key, {})
        if yf_val.get("value") is not None:
            merged_pinetree[pinetree_key] = {
                "value": yf_val["value"],
                "change1d": yf_val.get("change1d_pct"),
                "ytd": None,
                "source": "yfinance",
            }

    # Override interbank overnight from SBV if available
    ib_overnight = sbv_data.get("overnight")
    if ib_overnight and not merged_pinetree.get("interbankOvernight", {}).get("value"):
        merged_pinetree["interbankOvernight"] = {
            "value": ib_overnight,
            "change1d": sbv_data.get("change1d_bps"),
            "ytd": sbv_data.get("ytd_bps"),
            "source": sbv_data.get("source"),
        }

    # ── 8. Score ──────────────────────────────────────────────────────
    score_result = scorer.compute(merged_pinetree, global_data)
    snapshot.update(score_result)
    snapshot["mergedPinetree"] = merged_pinetree

    # ── 9. Save ───────────────────────────────────────────────────────
    path = history.save(snapshot, d)
    print(f"[{ts()}] ✓ Saved → {path}")

    return snapshot


# ── Console report ───────────────────────────────────────────────────────
def print_report(s: dict) -> None:
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"

    print(f"\n{'='*65}")
    print(f"  {BOLD}TÓM TẮT VĨ MÔ  —  {s.get('date','N/A')}{RESET}")
    print(f"{'='*65}")

    score = s.get("macroScore", "?")
    phase = s.get("phase", "?")
    # Color by regime
    color = GREEN if score and float(score) >= 65 else YELLOW if float(score) >= 50 else RED
    print(f"  Macro score : {color}{BOLD}{score} / 100{RESET}")
    print(f"  Regime      : {BOLD}{phase}{RESET}")
    print(f"  Market view : {s.get('marketView','?')}")

    print(f"\n  {BOLD}COMPONENT SCORES:{RESET}")
    comps = s.get("components", {})
    weights = s.get("weights", {})
    for k, v in comps.items():
        sc = v["score"]
        wt = weights.get(k, 0)
        bar_len = int(sc / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        c = GREEN if sc >= 60 else YELLOW if sc >= 45 else RED
        notes = " | ".join(v["notes"]) if v["notes"] else "—"
        print(f"    {k:<14} {c}{sc:5.1f}{RESET} ({wt:.0%}) [{bar}]  {notes}")

    # Key data
    pt = s.get("mergedPinetree") or s.get("pinetree", {})
    gl = s.get("global", {})
    vn = s.get("vnMarket", {})

    def _v(d, key):
        if isinstance(d.get(key), dict):
            return d[key].get("value")
        return d.get(key)

    def fmt(v, suffix=""):
        return f"{v:,.2f}{suffix}" if v is not None else "N/A"

    print(f"\n  {BOLD}KEY METRICS:{RESET}")
    print(f"    Liên NH overnight : {CYAN}{fmt(_v(pt,'interbankOvernight'), '%')}{RESET}")
    print(f"    Tiết kiệm 12T     : {fmt(_v(pt,'deposit12m'), '%')}")
    print(f"    USD/VND           : {fmt(_v(pt,'usdVnd'))}")
    print(f"    VNINDEX           : {fmt(_v(pt,'vnindex') or _v(vn.get('vnindex',{}),'value'))}")
    print(f"    Khối ngoại        : {fmt(_v(pt,'foreignNetBuyBn'))} tỷ")
    print(f"    VIX               : {fmt(gl.get('vix',{}).get('value') or _v(pt,'vix'))}")
    print(f"    S&P500 1D%        : {fmt(gl.get('sp500',{}).get('change1d_pct'), '%')}")
    print(f"    Brent             : {fmt(gl.get('brent',{}).get('value') or _v(pt,'brent'), ' USD/bbl')}")
    print(f"    DXY               : {fmt(gl.get('dxy',{}).get('value'))}")
    print(f"    US10Y             : {fmt(gl.get('us10y',{}).get('value'), '%')}")

    # News headlines
    headlines = pt.get("newsHeadlines", [])
    if headlines:
        print(f"\n  {BOLD}TIN TỨC HÔM NAY:{RESET}")
        for h in headlines[:5]:
            print(f"    • {h[:90]}")

    # OMO
    omo = s.get("omoData", {})
    if omo.get("totalNetBn") is not None:
        net = omo["totalNetBn"]
        direction = f"{GREEN}BƠM{RESET}" if net > 0 else f"{RED}HÚT{RESET}"
        print(f"\n  {BOLD}OMO THỊ TRƯỜNG MỞ [{omo.get('date','?')}]:{RESET}")
        print(f"    NHNN {direction} ròng: {abs(net):,.2f} tỷ đồng")
        print(f"    Lãi suất OMO: {omo.get('omoRate','?')}%/năm")
        print(f"    Signal: {omo.get('omoSignal','')}")
        for t in omo.get("transactions", []):
            print(f"    → {t['type'].upper()} {t['tenor']}: {t['volumeBn']:,.2f} tỷ @ {t['rate']}%")

    # SBV term structure
    sbv = s.get("sbvRates", {})
    vnd_rates = sbv.get("vnd", {})
    if vnd_rates:
        print(f"\n  {BOLD}LÃI SUẤT LIÊN NH (SBV PDF — tuần {sbv.get('weekRange','?')}):{RESET}")
        for tenor, val in vnd_rates.items():
            if val is not None and not tenor.startswith("overnight_"):
                print(f"    VND {tenor:<8}: {val}%/năm")

    # Warnings
    warnings = s.get("warnings", [])
    if warnings:
        print(f"\n  {YELLOW}WARNINGS:{RESET}")
        for w in warnings:
            print(f"    ⚠  {w}")

    print(f"\n  {BOLD}[Tài liệu phân tích nội bộ — không phải lời khuyên đầu tư]{RESET}")
    print(f"{'='*65}\n")


# ── Entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="LH Investment — Daily Macro Runner v2")
    ap.add_argument("--date",            help="YYYY-MM-DD (default: today)")
    ap.add_argument("--report",          action="store_true", help="Print report to terminal")
    ap.add_argument("--skip-yfinance",   action="store_true")
    ap.add_argument("--skip-worldbank",  action="store_true")
    ap.add_argument("--only-pinetree",   action="store_true", help="Only Pinetree + score (fastest)")
    args = ap.parse_args()

    from datetime import datetime as _dt
    run_date = _dt.strptime(args.date, "%Y-%m-%d").date() if args.date else None
    snapshot = run(
        run_date,
        skip_yfinance=args.skip_yfinance,
        skip_worldbank=args.skip_worldbank,
        only_pinetree=args.only_pinetree,
    )

    if args.report:
        print_report(snapshot)
    else:
        # Print compact summary (no raw data)
        compact = {k: v for k, v in snapshot.items()
                   if k not in ("pinetree", "mergedPinetree", "global", "vcbFx",
                                "vnMarket", "sbvRates", "worldbank")}
        print(json.dumps(compact, ensure_ascii=False, indent=2))
