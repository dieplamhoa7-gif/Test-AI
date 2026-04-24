from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.services.scraper import collect_news
from app.services.summarizer import enrich_news_with_ai, summarize_news
from app.store import load_news, merge_news


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


@app.get("/", response_class=HTMLResponse)
def dashboard():
    html = DASHBOARD_HTML.replace("__MARKET_API_BASE__", MARKET_API_BASE)
    return HTMLResponse(html)


@app.head("/")
def dashboard_head():
    return HTMLResponse("")


@app.get("/health")
def health():
    return {"ok": True, "service": "web"}


@app.head("/health")
def health_head():
    return HTMLResponse("")


@app.get("/news")
def news(limit: int = Query(default=20, ge=1, le=300), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=limit)
    return {"total_items": len(items), "items": items[:limit]}


@app.get("/summarize", response_model=SummarizeResponse)
def summarize(limit: int = Query(default=20, ge=1, le=100), max_chars: int = Query(default=2200, ge=300, le=6000), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=limit)[:limit]
    summary = summarize_news(items, max_chars=max_chars)
    return {"total_items": len(items), "summary": summary, "items": items}
