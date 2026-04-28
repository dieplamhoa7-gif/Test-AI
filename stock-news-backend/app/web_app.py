from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REFRESH_INTERVAL = timedelta(minutes=15)
_summary_cache: dict[tuple[int, int], dict] = {}
_last_refresh_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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


@app.get("/warrants", response_class=HTMLResponse)
def warrants_page():
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
    return get_market_symbol(symbol, force_refresh=refresh)


@app.get("/market-symbols")
def market_symbols(query: str = Query(default=""), limit: int = Query(default=20, ge=1, le=100)):
    return get_symbol_catalog(query=query, limit=limit)


@app.get("/warrants-data")
def warrants_data(symbols: str = Query(default=""), refresh: bool = Query(default=False)):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    return get_warrants_data(force_refresh=refresh, symbols=symbol_list or None)


@app.get("/fundamental-signals/{symbol}")
def fundamental_signals(symbol: str, limit: int = Query(default=8, ge=1, le=30)):
    """Read weekly analyst-report signal cache produced by report_signal_mvp.

    Expected source file: ../report_signal_mvp/all_report_signals.json
    This endpoint is local/cache-only; it does not scrape in request path.
    """
    data_path = Path(__file__).resolve().parents[2] / "report_signal_mvp" / "all_report_signals.json"
    if not data_path.exists():
        return {"symbol": symbol.upper(), "items": [], "updatedAt": None, "status": "missing"}
    try:
        rows = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"symbol": symbol.upper(), "items": [], "updatedAt": None, "status": "error", "error": str(exc)}
    wanted = symbol.upper()
    limit_n = int(limit) if not hasattr(limit, "default") else int(limit.default)
    items = [r for r in rows if str(r.get("symbol", "")).upper() == wanted]
    items.sort(key=lambda r: str(r.get("report_date") or ""), reverse=True)
    stat = data_path.stat()
    return {
        "symbol": wanted,
        "items": items[:limit_n],
        "total": len(items),
        "updatedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "status": "ok",
    }


@app.get("/news")
def news(limit: int = Query(default=20, ge=1, le=300), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=limit)
    return {"total_items": len(items), "items": items[:limit]}


@app.get("/summarize", response_model=SummarizeResponse)
def summarize(limit: int = Query(default=20, ge=1, le=300), max_chars: int = Query(default=2200, ge=300, le=6000), refresh: bool = Query(default=False)):
    key = (limit, max_chars)
    if not refresh and key in _summary_cache:
        return _summary_cache[key]
    items = _refresh_news_if_needed(force=refresh, limit=limit)[:limit]
    summary = summarize_news(items, max_chars=max_chars)
    payload = {"total_items": len(items), "summary": summary, "items": items}
    _summary_cache[key] = payload
    return payload
