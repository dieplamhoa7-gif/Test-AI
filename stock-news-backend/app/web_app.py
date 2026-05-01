from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sqlite3
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.services.scraper import collect_news
from app.services.summarizer import enrich_news_with_ai
from app.store import load_news, merge_news
from app.fundamental_filters import normalize_target_price, top_target_upside
from app.market_data import get_index_overview, get_market_cache, get_market_symbol, get_symbol_catalog
from app.report_sources import load_cached_24hmoney_reports
from app.technical_filters import top_technical_setups
from app.strategy_recommendations import current_strategy_recommendations
from app.warrants.service import get_warrants_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        pass


app = FastAPI(title="Hoa Investment Web", version="0.1.0", lifespan=lifespan)
APP_ASSET_VERSION = "2026-04-29-warrant-suggest-v4"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hoa-investment.onrender.com",
        "https://hoa-investment.web.app",
        "https://hoa-investment.firebaseapp.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["Content-Type"],
)

REFRESH_INTERVAL = timedelta(minutes=15)
SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,12}$")
_rate_buckets: dict[str, list[float]] = {}
RATE_LIMIT_WINDOW = 60.0
RATE_LIMIT_MAX = 180
_last_refresh_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith(("/.env", "/.git", "/admin", "/wp-", "/php", "/cgi-bin")):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    now = monotonic()
    ip = _client_ip(request)
    bucket = [t for t in _rate_buckets.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
    if len(bucket) >= RATE_LIMIT_MAX:
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)
    bucket.append(now)
    _rate_buckets[ip] = bucket
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-App-Version"] = APP_ASSET_VERSION
    connect_sources = "'self'"
    if MARKET_API_BASE.startswith("https://"):
        connect_sources += f" {MARKET_API_BASE}"
    response.headers["Content-Security-Policy"] = f"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src {connect_sources}; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if path in {"/", "/stocks", "/warrants", "/news-page"} or path.startswith(("/stocks/", "/warrants/")):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    elif path.startswith(("/market-data", "/warrants-data")):
        response.headers["Cache-Control"] = "public, max-age=15, stale-while-revalidate=30"
    elif path.startswith(("/fundamental-signals", "/news")):
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"
    else:
        response.headers["Cache-Control"] = "public, max-age=300"
    return response


def _clean_symbol(symbol: str) -> str:
    value = str(symbol or "").strip().upper()
    if not SYMBOL_RE.fullmatch(value):
        raise HTTPException(status_code=400, detail="Invalid symbol")
    return value


def _refresh_news_if_needed(force: bool = False, limit: int = 20) -> list[dict]:
    global _last_refresh_at

    cached_items = load_news()
    now = _utcnow()
    should_refresh = force or not cached_items or _last_refresh_at is None or (now - _last_refresh_at) >= REFRESH_INTERVAL

    if should_refresh:
        try:
            raw_items = collect_news(limit=min(limit, 20))
            if raw_items:
                try:
                    fresh_items = enrich_news_with_ai(raw_items)
                except Exception:
                    fresh_items = raw_items
                if fresh_items:
                    cached_items = merge_news(fresh_items)
                    _last_refresh_at = now
        except Exception:
            if cached_items:
                return cached_items
            raise

    return cached_items


class SummarizeResponse(BaseModel):
    total_items: int
    summary: str
    items: list[dict]


MARKET_API_BASE = os.getenv("MARKET_API_BASE", "").rstrip("/")
from app.dashboard_template import DASHBOARD_HTML


def _dashboard_response():
    html = DASHBOARD_HTML.replace("__MARKET_API_BASE__", MARKET_API_BASE)
    return HTMLResponse(html)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return _dashboard_response()


@app.get("/stocks", response_class=HTMLResponse)
def stocks_page():
    return _dashboard_response()


@app.get("/stocks/{symbol}", response_class=HTMLResponse)
def stock_detail_page(symbol: str):
    _clean_symbol(symbol)
    return _dashboard_response()


@app.get("/warrants", response_class=HTMLResponse)
def warrants_page():
    return _dashboard_response()


@app.get("/warrants/{symbol}", response_class=HTMLResponse)
def warrant_detail_page(symbol: str):
    _clean_symbol(symbol)
    return _dashboard_response()


@app.get("/news-page", response_class=HTMLResponse)
def news_page():
    return _dashboard_response()


@app.head("/")
def dashboard_head():
    return HTMLResponse("")


@app.get("/health")
def health():
    return {"ok": True, "service": "web"}


@app.head("/health")
def health_head():
    return HTMLResponse("")


@app.get("/market-overview")
def market_overview(refresh: bool = Query(default=False)):
    return get_index_overview(force_refresh=refresh)


@app.get("/market-data")
def market_data(refresh: bool = Query(default=False)):
    return get_market_cache(force_refresh=refresh)


@app.get("/market-data/{symbol}")
def market_symbol(symbol: str, refresh: bool = Query(default=False)):
    return get_market_symbol(_clean_symbol(symbol), force_refresh=refresh)



@app.get("/market-symbols")
def market_symbols(query: str = Query(default="", max_length=20), limit: int = Query(default=20, ge=1, le=30)):
    return get_symbol_catalog(query=query[:20], limit=limit)


@app.get("/warrants-data")
def warrants_data(symbols: str = Query(default="", max_length=160), refresh: bool = Query(default=False)):
    symbol_list = [_clean_symbol(s) for s in symbols.split(",")[:12] if s.strip()]
    return get_warrants_data(force_refresh=refresh, symbols=symbol_list or None)


@app.get("/fundamental-top-upside")
def fundamental_top_upside(limit: int = Query(default=20, ge=1, le=50), max_symbols: int = Query(default=80, ge=20, le=200), refresh: bool = Query(default=False)):
    return top_target_upside(limit=limit, max_symbols=max_symbols, force_refresh=refresh)


@app.get("/technical-top-setups")
def technical_top_setups(limit: int = Query(default=20, ge=1, le=50), max_symbols: int = Query(default=50, ge=10, le=50), refresh: bool = Query(default=False)):
    return top_technical_setups(limit=limit, max_symbols=max_symbols, force_refresh=refresh)


@app.get("/strategy-results-cache")
def strategy_results_cache():
    cache_path = Path(__file__).resolve().parents[1] / "data" / "strategy_results_cache.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"updatedAt": None, "strategies": [], "note": "missing cache"}


@app.get("/strategy-matrix-cache")
def strategy_matrix_cache():
    cache_path = Path(__file__).resolve().parents[1] / "data" / "strategy_matrix_cache.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"updatedAt": None, "columns": [], "rows": [], "note": "missing strategy matrix cache"}


@app.get("/strategy-recommendations")
def strategy_recommendations(max_symbols: int = Query(default=60, ge=10, le=80), refresh: bool = Query(default=False)):
    return current_strategy_recommendations(max_symbols=max_symbols, force_refresh=refresh)


@app.get("/fundamental-signals/{symbol}")
def fundamental_signals(symbol: str, limit: int = Query(default=50, ge=1, le=80)):
    """Read weekly analyst-report signal cache produced by report_signal_mvp.

    Expected source file: ../report_signal_mvp/all_report_signals.json
    This endpoint is local/cache-only; it does not scrape in request path.
    """
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / "report_signal_mvp" / "all_report_signals.json",
        root.parent / "report_signal_mvp" / "all_report_signals.json",
    ]
    data_path = next((p for p in candidates if p.exists()), candidates[0])
    wanted = _clean_symbol(symbol)
    limit_n = int(limit) if not hasattr(limit, "default") else int(limit.default)
    items: list[dict] = []
    updated_at = None
    if data_path.exists():
        try:
            rows = json.loads(data_path.read_text(encoding="utf-8"))
            items = [r for r in rows if str(r.get("symbol", "")).upper() == wanted]
            updated_at = datetime.fromtimestamp(data_path.stat().st_mtime, tz=timezone.utc).isoformat()
        except Exception:
            items = []
    # Prefer SQLite fallback when JSON is stale/partial. This restored MWG/SSI rows.
    if not items:
        db_path = data_path.with_name("all_report_signals.db")
        if db_path.exists():
            try:
                con = sqlite3.connect(db_path)
                con.row_factory = sqlite3.Row
                rows = con.execute("select * from report_signals_all where upper(symbol)=? order by report_date desc limit ?", (wanted, limit_n)).fetchall()
                items = [dict(r) for r in rows]
                con.close()
                updated_at = datetime.fromtimestamp(db_path.stat().st_mtime, tz=timezone.utc).isoformat()
            except Exception:
                items = []
    reports_path = root / "data" / "24hmoney_reports.json"
    report_rows = load_cached_24hmoney_reports(reports_path)
    existing_keys = {str(r.get("source_url") or r.get("url") or r.get("title") or "").lower() for r in items}
    for report in report_rows:
        symbols = [str(s).upper() for s in report.get("symbols") or []]
        if wanted not in symbols and str(report.get("symbol", "")).upper() != wanted:
            continue
        key = str(report.get("url") or report.get("title") or "").lower()
        if key in existing_keys:
            continue
        existing_keys.add(key)
        items.append({
            "symbol": wanted,
            "report_date": report.get("report_date"),
            "title": report.get("title"),
            "source": report.get("source") or "24HMoney",
            "source_url": report.get("url"),
            "url": report.get("url"),
            "summary": report.get("summary"),
            "recommendation": "Báo cáo phân tích",
            "provider": "24HMoney",
        })
    items.sort(key=lambda r: str(r.get("report_date") or ""), reverse=True)
    quote_price = 0.0
    try:
        quote_res = get_market_symbol(wanted, force_refresh=False)
        quote_price = float((quote_res or {}).get("price") or 0)
        if 0 < quote_price < 1000:
            quote_price *= 1000
    except Exception:
        quote_price = 0.0
    if quote_price > 0:
        for row in items:
            for key in ("target_price", "buy_low", "buy_high", "stop_loss"):
                if row.get(key) not in (None, ""):
                    normalized_value = normalize_target_price(row.get(key), quote_price)
                    if normalized_value > 0:
                        row[key] = normalized_value
    return {
        "symbol": wanted,
        "items": items[:limit_n],
        "total": len(items),
        "updatedAt": updated_at,
        "status": "ok" if updated_at else "missing",
    }


@app.get("/news")
def news(limit: int = Query(default=5, ge=1, le=30), page: int = Query(default=1, ge=1, le=200), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=min(limit, 20))
    start = (page - 1) * limit
    end = start + limit
    return {"total_items": len(items), "items": items[start:end], "page": page, "limit": limit, "cached": not refresh}


