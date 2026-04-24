from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.market_data import get_market_cache, get_market_symbol, get_symbol_catalog

app = FastAPI(title="Hoa Investment Market API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "service": "market"}


@app.get("/market-data")
def market_data():
    data = get_market_cache()
    return data["items"]


@app.get("/market-data/{symbol}")
def market_symbol(symbol: str):
    return get_market_symbol(symbol)


@app.get("/market-symbols")
def market_symbols(query: str = Query(default=""), limit: int = Query(default=20, ge=1, le=100)):
    return get_symbol_catalog(query=query, limit=limit)
