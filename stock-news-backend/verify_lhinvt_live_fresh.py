from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date, datetime, timedelta

LIVE_BASE = "https://lhinvt.web.app/data"
TODAY = date.today().isoformat()
MAX_WARRANT_AGE_HOURS = 30


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


def main() -> None:
    errors: list[str] = []

    market = fetch_json("market_data.json")
    if market.get("latestTradingDate") != TODAY:
        errors.append(f"market latestTradingDate={market.get('latestTradingDate')} expected={TODAY}")
    if int(market.get("count") or 0) < 50:
        errors.append(f"market count too low: {market.get('count')}")

    history = fetch_json("vn100_history_from_2023.json")
    if history.get("latestTradingDate") != TODAY:
        errors.append(f"history latestTradingDate={history.get('latestTradingDate')} expected={TODAY}")
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
    if fpt.get("latestTradingDate") != TODAY:
        errors.append(f"FPT chart latestTradingDate={fpt.get('latestTradingDate')} expected={TODAY}")

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
