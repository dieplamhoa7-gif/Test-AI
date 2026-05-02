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
    indicator_cache = read_json(DATA / "v3_full_indicator_cache_v2.json", {})
    indicator_by_symbol: dict[str, dict[str, Any]] = {}
    for row in indicator_cache.get("items", []) if isinstance(indicator_cache, dict) else []:
        sym = str(row.get("ticker") or row.get("symbol") or "").upper()
        if sym:
            indicator_by_symbol[sym] = row

    items = []
    for row in rs.get("items", []) if isinstance(rs, dict) else []:
        sym = str(row.get("ticker") or row.get("symbol") or "").upper()
        if not sym:
            continue
        detail = dict(row)
        detail["ticker"] = sym
        detail["symbol"] = sym
        detail["technical"] = {
            "trend": detail.get("trend") or detail.get("marketStructureDay") or "-",
            "ma20": detail.get("ma20") or detail.get("ma20Anchor"),
            "ma50": detail.get("ma50") or detail.get("ma50Anchor"),
            "ma200": detail.get("ma200") or detail.get("ma200Anchor"),
            "activeSupportDay": detail.get("activeSupportDay") or detail.get("supportDay"),
            "nextSupportDay": detail.get("nextSupportDay") or detail.get("supportDay2"),
            "activeResistanceDay": detail.get("activeResistanceDay") or detail.get("resistanceDay"),
            "nextResistanceDay": detail.get("nextResistanceDay") or detail.get("resistanceDay2"),
            "supportDay": detail.get("supportDay"),
            "resistanceDay": detail.get("resistanceDay"),
        }
        irow = indicator_by_symbol.get(sym) or {}
        indicators = irow.get("indicators") if isinstance(irow, dict) else {}
        if isinstance(indicators, dict):
            indicator_fields = {
                "rsi14": indicators.get("rsi14"),
                "adx14": indicators.get("adx14"),
                "plusDi": indicators.get("plusDi"),
                "minusDi": indicators.get("minusDi"),
                "bbUpper": indicators.get("bbUpper"),
                "bbLower": indicators.get("bbLower"),
                "bbMiddle": indicators.get("bbMiddle"),
                "bbPercent": indicators.get("bbPercent"),
            }
            detail["technical"] = {**(detail.get("technical") or {}), **{k: v for k, v in indicator_fields.items() if v is not None}}
        srow = by_symbol.get(sym) or {}
        if srow:
            detail["technical"] = {**(detail.get("technical") or {}), **(srow.get("technical") or {})}
            for key in ["price", "changePct", "volume", "strategySignals", "rsi14", "adx14", "plusDi", "minusDi", "bbUpper", "bbLower", "bbMiddle", "bbPercent", "setupType", "recommendation"]:
                if key in srow and srow[key] is not None:
                    detail[key] = srow[key]
                    detail["technical"][key] = srow[key]
        items.append(detail)
    return {"items": items, "count": len(items), "source": "firebase-static-cache"}


def _infer_underlying_from_warrant(code: str) -> str:
    text = str(code or "").upper().strip()
    if text.startswith("C") and len(text) >= 4:
        return text[1:4]
    return ""


def build_warrants_cache() -> dict[str, Any]:
    """Build a broad static warrant catalog for Firebase without live quoting."""
    static_payload = read_json(WARRANTS / "warrants_static.json", {"items": []})
    static_items = static_payload.get("items", []) if isinstance(static_payload, dict) else []
    catalog_payload = read_json(WARRANTS / "warrant_catalog.json", {"items": []})
    catalog_items = catalog_payload.get("items", []) if isinstance(catalog_payload, dict) else []
    by_code: dict[str, dict[str, Any]] = {}
    for item in static_items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "").upper().strip()
        if not code:
            continue
        if item.get("daysLeft") is not None and float(item.get("daysLeft") or 0) <= 0:
            continue
        row = dict(item)
        row["code"] = code
        row.setdefault("underlying", _infer_underlying_from_warrant(code))
        by_code[code] = row
    for item in catalog_items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "").upper().strip()
        if not code:
            continue
        row = {**dict(item), **by_code.get(code, {})}
        row["code"] = code
        row.setdefault("underlying", item.get("underlying") or _infer_underlying_from_warrant(code))
        row.setdefault("source", item.get("source") or "warrant-catalog-cache")
        by_code[code] = row
    valid = sorted(by_code.values(), key=lambda x: (str(x.get("underlying") or ""), str(x.get("code") or "")))
    return {"items": valid, "count": len(valid), "source": "firebase-static-cache"}

def build_fundamental_cache() -> dict[str, Any]:
    reports = read_json(DATA / "all_report_signals.json", [])
    if isinstance(reports, dict):
        reports = reports.get("items", [])
    return {"items": reports if isinstance(reports, list) else [], "source": "firebase-static-cache"}


def build_fundamental_top_upside(reports: list[dict[str, Any]], market_items: list[dict[str, Any]]) -> dict[str, Any]:
    prices = {str(x.get("ticker") or x.get("symbol") or "").upper(): float(x.get("price") or 0) for x in market_items if isinstance(x, dict)}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in reports:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("symbol") or "").upper().strip()
        target = float(row.get("target_price") or 0)
        if not sym or target <= 0:
            continue
        grouped.setdefault(sym, []).append(row)
    out = []
    for sym, rows in grouped.items():
        targets = [float(r.get("target_price") or 0) for r in rows if float(r.get("target_price") or 0) > 0]
        if not targets:
            continue
        avg = sum(targets) / len(targets)
        price = prices.get(sym, 0)
        # market prices are in thousand VND while report targets are VND; normalize display fields to VND.
        price_vnd = price * 1000 if 0 < price < 1000 else price
        upside = ((avg / price_vnd - 1) * 100) if price_vnd > 0 else None
        latest = sorted(rows, key=lambda r: str(r.get("report_date") or ""), reverse=True)[0]
        out.append({
            "symbol": sym,
            "price": round(price_vnd, 0) if price_vnd else None,
            "avgTargetPrice": round(avg, 0),
            "upsidePct": round(upside, 1) if upside is not None else None,
            "reportCount": len(rows),
            "latestReportDate": latest.get("report_date"),
            "latestTitle": latest.get("title"),
            "name": latest.get("title"),
        })
    out.sort(key=lambda x: (x.get("upsidePct") is None, -(x.get("upsidePct") or -9999), x.get("symbol") or ""))
    return {"items": out[:50], "source": "firebase-static-cache"}


def patch_html_for_firebase(html: str) -> str:
    """Patch dashboard to call Firebase static JSON directly.

    Avoid overriding window.fetch; direct URLs are simpler and safer on mobile.
    """
    html = html.replace("const API_BASE = '';", "const API_BASE = '';")
    html = html.replace("const MARKET_API_BASE = '';", "const MARKET_API_BASE = '';")
    replacements = {
        "`${API_BASE}/market-overview?ts=${Date.now()}`": "`/data/market_overview.json?ts=${Date.now()}`",
        "`${API_BASE}/warrants-data?ts=${Date.now()}`": "`/data/warrants_data.json?ts=${Date.now()}`",
        "`${API_BASE}/warrants-data?symbols=${encodeURIComponent(code)}&ts=${Date.now()}`": "`/data/warrants_data.json?ts=${Date.now()}`",
        "`${API_BASE}/warrants-data?symbols=${encodeURIComponent(warrantWatchSymbols.join(','))}&ts=${Date.now()}`": "`/data/warrants_data.json?ts=${Date.now()}`",
        "`${API_BASE}/strategy-matrix-cache?ts=${Date.now()}`": "`/data/strategy_matrix_cache.json?ts=${Date.now()}`",
        "`${API_BASE}/strategy-results-cache?ts=${Date.now()}`": "`/data/strategy_results_cache.json?ts=${Date.now()}`",
        "`${API_BASE}/fundamental-top-upside?limit=50&max_symbols=200&ts=${Date.now()}`": "`/data/fundamental_top_upside.json?ts=${Date.now()}`",
        "`${MARKET_API_BASE || API_BASE}/market-data?refresh=${refreshFlag}&ts=${Date.now()}`": "`/data/market_watch.json?ts=${Date.now()}`",
        "`${API_BASE}/news?limit=${limit}&lang=${currentLang}`": "`/data/${currentLang === 'en' ? 'news_cache_en.json' : 'news_cache.json'}?limit=${limit}&ts=${Date.now()}`",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    # Replace functions that need endpoint logic with local-cache lookups.
    html = re.sub(
        r"async function refreshStockDetail\(symbol\) \{.*?\n    async function openStockSymbol",
        """async function refreshStockDetail(symbol) { const normalized = (symbol || '').trim().toUpperCase(); if (!normalized) return; const existing = marketItems.find(x => String(x.ticker || x.symbol || '').toUpperCase() === normalized); if (existing) { if (activeDetailTicker === normalized) openDetail(normalized); return existing; } const res = await fetch(`/data/market_data.json?ts=${Date.now()}`, { cache: 'no-store' }); if (!res.ok) throw new Error('market cache'); const payload = await res.json(); marketItems = Array.isArray(payload.items) ? payload.items : []; const item = marketItems.find(x => String(x.ticker || x.symbol || '').toUpperCase() === normalized); if (!item) throw new Error('Not found'); if (activeDetailTicker === normalized) openDetail(normalized); return item; }\n    async function openStockSymbol""",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"async function searchStockCatalog\(\) \{.*?\n    async function addStockToWatchlist",
        """async function searchStockCatalog() { const q = (elements.stockSearchInput.value || '').trim().toUpperCase(); selectedSymbol = ''; if (!q) { elements.stockSuggest.classList.remove('open'); elements.stockSuggest.innerHTML = ''; return; } try { const res = await fetch('/data/market_symbols.json', { cache: 'default' }); if (!res.ok) return; const rows = await res.json(); const items = rows.filter(item => String(item.symbol||'').includes(q) || String(item.name||'').toUpperCase().includes(q)).slice(0, 50); elements.stockSuggest.innerHTML = items.map(item => `<div class=\"search-option\" data-symbol=\"${escapeHtml(item.symbol)}\"><strong>${escapeHtml(item.symbol)}</strong><span>${escapeHtml(item.name || '')}</span></div>`).join(''); elements.stockSuggest.classList.toggle('open', items.length > 0); elements.stockSuggest.querySelectorAll('[data-symbol]').forEach(option => option.addEventListener('click', async () => { selectedSymbol = option.dataset.symbol; elements.stockSearchInput.value = selectedSymbol; elements.stockSuggest.classList.remove('open'); await openStockSymbol(selectedSymbol); })); } catch (_) {} }\n    async function addStockToWatchlist""",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"async function addStockToWatchlist\(symbolOverride = ''\) \{.*?\n    function removeStockFromWatchlist",
        """async function addStockToWatchlist(symbolOverride = '') { const symbol = (symbolOverride || selectedSymbol || elements.stockSearchInput.value || '').trim().toUpperCase(); if (!symbol) return; try { await refreshStockDetail(symbol); if (!watchSymbols.includes(symbol)) watchSymbols.unshift(symbol); renderMarket({ items: marketItems, updatedAt: new Date().toISOString() }); elements.stockSearchInput.value = ''; selectedSymbol = ''; elements.stockSuggest.classList.remove('open'); elements.stockSuggest.innerHTML = ''; } catch (_) { elements.marketStatus.textContent = `Khong tim thay ma ${symbol}`; } finally { elements.stockSearchBtn.textContent = L('add'); } }\n    function removeStockFromWatchlist""",
        html,
        flags=re.S,
    )
    return html


def build_html() -> None:
    dashboard = extract_raw_py_string((APP / "dashboard_template.py").read_text(encoding="utf-8"), "DASHBOARD_HTML")
    dashboard = patch_html_for_firebase(dashboard)
    # Keep HTML small: use file logo instead of huge inline base64.
    import re
    dashboard = re.sub(r'src="data:image/jpeg;base64,[^"]+"', 'src="/assets/lh-logo.jpg"', dashboard)
    # Firebase ultra-light startup: load only data needed for the current static page.
    light_load = """async function loadData(isAutoRefresh = false, forceRefresh = false) { elements.apiStatus.textContent = 'Cache'; let hasAnyData = Boolean(marketItems.length || allItems.length); const tab = pageToTab(); if (tab === 'news') { try { const newsRes = await fetch(`/data/${currentLang === 'en' ? 'news_cache_en.json' : 'news_cache.json'}?ts=${Date.now()}`, { cache: 'no-store' }); if (newsRes.ok) { const newsData = await newsRes.json(); allItems = Array.isArray(newsData.items) ? newsData.items : (Array.isArray(newsData) ? newsData : []); currentPage = 1; applyFilters(); hasAnyData = true; } } catch (_) { elements.statusText.innerHTML = '<span class="error">Loi tai tin tuc.</span>'; elements.newsList.innerHTML = '<div class="empty error">Khong the tai tin tuc luc nay.</div>'; } elements.apiStatus.textContent = hasAnyData ? 'Online' : 'Offline'; return; } if (tab === 'warrants') { await loadWarrants(); elements.apiStatus.textContent = warrantItems.length ? 'Online' : 'Offline'; return; } try { const marketRes = await fetch(`/data/market_watch.json?ts=${Date.now()}`, { cache: 'no-store' }); if (marketRes.ok) { const marketData = await marketRes.json(); renderMarket(marketData); writeLocalCache('hoa.market.cache', marketData); hasAnyData = true; } } catch (_) { elements.marketStatus.textContent = 'Khong tai duoc watchlist'; } elements.apiStatus.textContent = hasAnyData ? 'Online' : 'Offline'; }"""
    dashboard = re.sub(r"async function loadData\(isAutoRefresh = false, forceRefresh = false\) \{.*?\n    elements\.tabs\.forEach", light_load + "\n    elements.tabs.forEach", dashboard, flags=re.S)
    dashboard = dashboard.replace("applyLanguage(currentLang); renderCategories(); hydrateFromLocalCache(); loadData(); loadWarrants(); setTimeout(loadIndexOverview, 300);", "applyLanguage(currentLang); renderCategories(); loadData(); setTimeout(loadIndexOverview, 300);")
    (PUBLIC / "assets").mkdir(exist_ok=True)
    logo = DATA / "assets" / "lh-logo.jpg"
    if logo.exists():
        shutil.copyfile(logo, PUBLIC / "assets" / "lh-logo.jpg")
    for name in ["index.html", "stocks.html", "news-page.html", "warrants.html"]:
        (PUBLIC / name).write_text(dashboard, encoding="utf-8")


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

    market = build_market_cache()
    write_json(PUBLIC_DATA / "market_data.json", market)
    default_watch = {"MWG", "FPT", "HPG", "SSI"}
    write_json(PUBLIC_DATA / "market_watch.json", {"items": [x for x in market["items"] if str(x.get("ticker") or x.get("symbol") or "").upper() in default_watch], "source": "firebase-static-watch-cache"})
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
    write_json(PUBLIC_DATA / "fundamental_top_upside.json", build_fundamental_top_upside(fundamental.get("items", []), market.get("items", [])))
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
