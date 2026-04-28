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
from app.services.summarizer import enrich_news_with_ai, summarize_news
from app.store import load_news, merge_news
from app.market_data import get_index_overview, get_market_cache, get_market_symbol, get_symbol_catalog
from app.warrants.service import get_warrants_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        pass


app = FastAPI(title="Hoa Investment Web", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hoa-investment.onrender.com",
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
_summary_cache: dict[tuple[int, int], dict] = {}
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
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    response.headers["Cache-Control"] = "no-store" if path.startswith(("/market-data", "/warrants-data", "/fundamental-signals")) else "public, max-age=60"
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
from app.news_light_template import NEWS_HTML
from app.warrants_light_template import WARRANTS_HTML


def _dashboard_response():
    html = DASHBOARD_HTML.replace("__MARKET_API_BASE__", MARKET_API_BASE)
    return HTMLResponse(html)


def _news_response():
    return HTMLResponse(NEWS_HTML)


def _warrants_response():
    return HTMLResponse(WARRANTS_HTML)


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
    return _warrants_response()


@app.get("/warrants/{symbol}", response_class=HTMLResponse)
def warrant_detail_page(symbol: str):
    _clean_symbol(symbol)
    return _warrants_response()


@app.get("/news-page", response_class=HTMLResponse)
def news_page():
    return _news_response()


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


@app.get("/fundamental-signals/{symbol}")
def fundamental_signals(symbol: str, limit: int = Query(default=8, ge=1, le=12)):
    """Read weekly analyst-report signal cache produced by report_signal_mvp.

    Expected source file: ../report_signal_mvp/all_report_signals.json
    This endpoint is local/cache-only; it does not scrape in request path.
    """
    data_path = Path(__file__).resolve().parents[2] / "report_signal_mvp" / "all_report_signals.json"
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
    items.sort(key=lambda r: str(r.get("report_date") or ""), reverse=True)
    return {
        "symbol": wanted,
        "items": items[:limit_n],
        "total": len(items),
        "updatedAt": updated_at,
        "status": "ok" if updated_at else "missing",
    }


@app.get("/news")
def news(limit: int = Query(default=5, ge=1, le=30), page: int = Query(default=1, ge=1, le=200), refresh: bool = Query(default=False)):
    # Runtime web path is cache-only to avoid slow scraping or abuse on public deploy.
    items = load_news()
    start = (page - 1) * limit
    end = start + limit
    return {"total_items": len(items), "items": items[start:end], "page": page, "limit": limit, "cached": True}


@app.get("/summarize", response_model=SummarizeResponse)
def summarize(limit: int = Query(default=5, ge=1, le=20), max_chars: int = Query(default=1200, ge=300, le=2500), refresh: bool = Query(default=False)):
    key = (limit, max_chars)
    if not refresh and key in _summary_cache:
        return _summary_cache[key]
    # Cache-only; do not scrape realtime from summarize endpoint.
    items = load_news()[:limit]
    summary = summarize_news(items, max_chars=max_chars)
    payload = {"total_items": len(items), "summary": summary, "items": items}
    _summary_cache[key] = payload
    return payload
