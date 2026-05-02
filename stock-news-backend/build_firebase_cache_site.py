"""Build Firebase Hosting static cache site.

Architecture target:
- Local machine builds PTKT/R-S/indicator/strategy caches into data/*.json.
- Render can keep updating news caches separately.
- Firebase Hosting serves frontend + cache JSON only; no heavy runtime.

This script exports endpoint-compatible static JSON files and patches the dashboard
HTML with a tiny fetch adapter so existing frontend code can keep using paths like
/market-data, /news?lang=en, /warrants-data while Firebase serves local files.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "firebase_public"
DATA = ROOT / "data"
APP = ROOT / "app"
WARRANTS = APP / "warrants"

PUBLIC_DATA = PUBLIC / "data"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def extract_raw_py_string(text: str, var_name: str) -> str:
    marker = f"{var_name} = r'''"
    start = text.index(marker) + len(marker)
    end = text.rindex("'''")
    return text[start:end]


def build_market_cache() -> dict[str, Any]:
    rs = read_json(DATA / "rs_levels_hsx_all_cache.json", {})
    strategy = read_json(DATA / "strategy_results_cache.json", {})
    strategy_items = strategy.get("items") if isinstance(strategy, dict) else []
    by_symbol: dict[str, dict[str, Any]] = {}
    for row in strategy_items or []:
        sym = str(row.get("ticker") or row.get("symbol") or "").upper()
        if sym:
            by_symbol[sym] = row

    items = []
    for row in rs.get("items", []) if isinstance(rs, dict) else []:
        sym = str(row.get("ticker") or row.get("symbol") or "").upper()
        if not sym:
            continue
        detail = dict(row)
        detail["ticker"] = sym
        detail["symbol"] = sym
        srow = by_symbol.get(sym) or {}
        if srow:
            detail["technical"] = {**(detail.get("technical") or {}), **(srow.get("technical") or {})}
            for key in ["price", "changePct", "volume", "strategySignals", "rsi14", "macd", "signal", "histogram", "volumeRatio", "roc20", "bbPercent", "setupType", "recommendation"]:
                if key in srow and srow[key] is not None:
                    detail[key] = srow[key]
        items.append(detail)
    return {"items": items, "count": len(items), "source": "firebase-static-cache"}


def build_warrants_cache() -> dict[str, Any]:
    static_payload = read_json(WARRANTS / "warrants_static.json", {"items": []})
    items = static_payload.get("items", []) if isinstance(static_payload, dict) else []
    valid = []
    for item in items:
        if not item.get("code") or not item.get("maturityDate"):
            continue
        if item.get("daysLeft") is None or float(item.get("daysLeft") or 0) <= 0:
            continue
        if item.get("underlyingPrice") is None or item.get("exercisePrice") is None:
            continue
        if not any(k in item for k in ["marketPrice", "lastPrice", "fairValue"]):
            continue
        valid.append(item)
    return {"items": valid, "count": len(valid), "source": "firebase-static-cache"}


def build_fundamental_cache() -> dict[str, Any]:
    reports = read_json(DATA / "all_report_signals.json", [])
    if isinstance(reports, dict):
        reports = reports.get("items", [])
    return {"items": reports if isinstance(reports, list) else [], "source": "firebase-static-cache"}


def patch_html_for_firebase(html: str) -> str:
    # Keep API bases relative and intercept old endpoint fetches to static JSON files.
    html = html.replace("const API_BASE = '';", "const API_BASE = '';")
    html = html.replace("const MARKET_API_BASE = '';", "const MARKET_API_BASE = '';")
    adapter = r'''
    // Firebase static-cache adapter: maps old API endpoints to local JSON files.
    (function installFirebaseStaticFetch(){
      const nativeFetch = window.fetch.bind(window);
      function jsonResponse(obj){ return new Response(JSON.stringify(obj), {status:200, headers:{'content-type':'application/json; charset=utf-8'}}); }
      async function loadJson(path){ const r = await nativeFetch(path, {cache:'no-store'}); if(!r.ok) throw new Error(path); return r.json(); }
      window.fetch = async function(input, init){
        const raw = String(input && input.url ? input.url : input);
        let u; try { u = new URL(raw, location.origin); } catch(_) { return nativeFetch(input, init); }
        const p = u.pathname;
        if (p === '/news') return nativeFetch(`/data/${(u.searchParams.get('lang')||'vi').startsWith('en') ? 'news_cache_en.json' : 'news_cache.json'}`, init);
        if (p === '/market-data') return nativeFetch('/data/market_data.json', init);
        if (p.startsWith('/market-data/')) { const sym=decodeURIComponent(p.split('/').pop()).toUpperCase(); const all=await loadJson('/data/market_data.json'); const item=(all.items||[]).find(x=>String(x.symbol||x.ticker||'').toUpperCase()===sym); return item ? jsonResponse(item) : jsonResponse({detail:'Not found', symbol:sym}); }
        if (p === '/market-symbols') {
          const q=(u.searchParams.get('query')||'').toUpperCase(); const limit=Number(u.searchParams.get('limit')||50);
          const rows=await loadJson('/data/market_symbols.json');
          return jsonResponse(rows.filter(x => String(x.symbol||'').includes(q) || String(x.name||'').toUpperCase().includes(q)).slice(0,limit));
        }
        if (p === '/warrants-data') return nativeFetch('/data/warrants_data.json', init);
        if (p === '/strategy-results-cache') return nativeFetch('/data/strategy_results_cache.json', init);
        if (p === '/strategy-matrix-cache') return nativeFetch('/data/strategy_matrix_cache.json', init);
        if (p === '/rs-levels-cache') return nativeFetch('/data/rs_levels_hsx_all_cache.json', init);
        if (p === '/market-overview') return nativeFetch('/data/market_overview.json', init);
        if (p === '/fundamental-top-upside') return nativeFetch('/data/fundamental_top_upside.json', init);
        if (p.startsWith('/fundamental-signals/')) {
          const sym=decodeURIComponent(p.split('/').pop()).toUpperCase(); const all=await loadJson('/data/fundamental_signals.json');
          const items=(all.items||[]).filter(x => String(x.symbol||x.ticker||'').toUpperCase()===sym).slice(0,50);
          return jsonResponse({symbol:sym, items, status:'firebase-static-cache'});
        }
        return nativeFetch(input, init);
      };
    })();
'''
    return html.replace("    const AUTO_REFRESH_MS = 15 * 60 * 1000;", "    const AUTO_REFRESH_MS = 15 * 60 * 1000;" + adapter)


def build_html() -> None:
    dashboard = extract_raw_py_string((APP / "dashboard_template.py").read_text(encoding="utf-8"), "DASHBOARD_HTML")
    dashboard = patch_html_for_firebase(dashboard)
    for name in ["index.html", "stocks.html", "news-page.html", "warrants.html"]:
        (PUBLIC / name).write_text(dashboard, encoding="utf-8")


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

    market = build_market_cache()
    write_json(PUBLIC_DATA / "market_data.json", market)
    symbols = []
    for item in market["items"]:
        sym = str(item.get("symbol") or item.get("ticker") or "").upper()
        if not sym:
            continue
        symbols.append({"symbol": sym, "name": item.get("name") or item.get("companyName") or sym})
    write_json(PUBLIC_DATA / "market_symbols.json", symbols)

    for src, dst in [
        (DATA / "news_cache.json", PUBLIC_DATA / "news_cache.json"),
        (DATA / "news_cache_en.json", PUBLIC_DATA / "news_cache_en.json"),
        (DATA / "strategy_results_cache.json", PUBLIC_DATA / "strategy_results_cache.json"),
        (DATA / "strategy_matrix_cache.json", PUBLIC_DATA / "strategy_matrix_cache.json"),
        (DATA / "rs_levels_hsx_all_cache.json", PUBLIC_DATA / "rs_levels_hsx_all_cache.json"),
    ]:
        if src.exists():
            shutil.copyfile(src, dst)

    write_json(PUBLIC_DATA / "warrants_data.json", build_warrants_cache())
    fundamental = build_fundamental_cache()
    write_json(PUBLIC_DATA / "fundamental_signals.json", fundamental)
    write_json(PUBLIC_DATA / "fundamental_top_upside.json", {"items": fundamental.get("items", [])[:50], "source": "firebase-static-cache"})
    write_json(PUBLIC_DATA / "market_overview.json", {"items":[
        {"symbol":"VNINDEX","label":"VN-Index","close":1040.0,"change":0,"changePct":0},
        {"symbol":"HNXINDEX","label":"HNX-Index","close":0,"change":0,"changePct":0},
        {"symbol":"UPCOM","label":"UPCOM","close":0,"change":0,"changePct":0},
    ], "source":"firebase-static-cache"})

    build_html()
    print(f"Built Firebase static cache site: {PUBLIC}")
    print(f"market symbols: {len(symbols)}")
    print(f"files: {sum(1 for _ in PUBLIC.rglob('*') if _.is_file())}")


if __name__ == "__main__":
    main()
