from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date, datetime, timedelta

LIVE_BASE = "https://lhinvt.web.app/data"
TODAY_DATE = date.today()
TODAY = TODAY_DATE.isoformat()
# Intraday runs before EOD close will still have the previous trading session
# as latestTradingDate/chart candle, while priceUpdatedAt/updatedAt must be today.
MAX_TRADING_DATE_LAG_DAYS = 5
MAX_WARRANT_AGE_HOURS = 30
MAX_MARKET_UPDATE_AGE_HOURS = 8


def fetch_json(path: str):
    url = f"{LIVE_BASE}/{path}?ts={int(datetime.now().timestamp())}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except Exception:
        return None


def assert_recent_trading_date(errors: list[str], label: str, value: str | None) -> None:
    d = parse_date(value)
    if not d:
        errors.append(f"{label} invalid latestTradingDate={value}")
        return
    lag = (TODAY_DATE - d).days
    if lag < 0 or lag > MAX_TRADING_DATE_LAG_DAYS:
        errors.append(f"{label} latestTradingDate={value} lag_days={lag} max={MAX_TRADING_DATE_LAG_DAYS}")


def assert_recent_update(errors: list[str], label: str, value: str | None, max_hours: int = MAX_MARKET_UPDATE_AGE_HOURS) -> None:
    dt = parse_dt(value)
    if not dt:
        errors.append(f"{label} invalid updatedAt={value}")
        return
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    if now - dt > timedelta(hours=max_hours):
        errors.append(f"{label} stale updatedAt={value}")


def main() -> None:
    errors: list[str] = []

    market = fetch_json("market_data.json")
    assert_recent_trading_date(errors, "market", market.get("latestTradingDate"))
    assert_recent_update(errors, "market", market.get("priceUpdatedAt") or market.get("updatedAt"))
    if int(market.get("count") or len(market.get("items") or []) or 0) < 50:
        errors.append(f"market count too low: {market.get('count') or len(market.get('items') or [])}")

    history = fetch_json("vn100_history_from_2023.json")
    assert_recent_trading_date(errors, "history", history.get("latestTradingDate"))
    if int(history.get("count") or 0) < 100:
        errors.append(f"history count too low: {history.get('count')}")

    warrants = fetch_json("warrants_data.json")
    if warrants.get("source") != "vps-realtime-scheduled-refresh":
        errors.append(f"warrants source={warrants.get('source')}")
    if int(warrants.get("count") or 0) < 200:
        errors.append(f"warrants count too low: {warrants.get('count')}")
    wdt = parse_dt(warrants.get("updatedAt"))
    if not wdt:
        errors.append(f"warrants invalid updatedAt={warrants.get('updatedAt')}")
    else:
        now = datetime.now(wdt.tzinfo) if wdt.tzinfo else datetime.now()
        if now - wdt > timedelta(hours=MAX_WARRANT_AGE_HOURS):
            errors.append(f"warrants stale updatedAt={warrants.get('updatedAt')}")

    news = fetch_json("news_cache.json")
    news_count = len(news) if isinstance(news, list) else len(news.get("items") or [])
    if news_count < 100:
        errors.append(f"news count too low: {news_count}")

    fpt = fetch_json("charts/FPT_day.json")
    assert_recent_trading_date(errors, "FPT chart", fpt.get("latestTradingDate"))

    if errors:
        print("LHINVT LIVE FRESHNESS FAIL")
        for err in errors:
            print("-", err)
        raise SystemExit(1)

    print("LHINVT LIVE FRESHNESS OK", {
        "date": TODAY,
        "marketUpdatedAt": market.get("updatedAt"),
        "historyUpdatedAt": history.get("updatedAt"),
        "warrantsUpdatedAt": warrants.get("updatedAt"),
        "newsCount": news_count,
    })


if __name__ == "__main__":
    main()
