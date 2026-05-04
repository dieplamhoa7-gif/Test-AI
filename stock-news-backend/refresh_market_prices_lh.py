import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.market_data import _fetch_symbol
from vnstock import Quote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PUBLIC_DATA = ROOT / 'firebase_public' / 'data'
MARKET_DATA_FILES = [DATA / 'market_data.json', PUBLIC_DATA / 'market_data.json']
MARKET_WATCH_FILES = [PUBLIC_DATA / 'market_watch.json']
MARKET_OVERVIEW_FILES = [DATA / 'market_overview.json', PUBLIC_DATA / 'market_overview.json']
DEFAULT_WATCH = {'MWG', 'FPT', 'HPG', 'SSI'}
TZ = timezone(timedelta(hours=7))


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def symbol_of(item):
    return str(item.get('ticker') or item.get('symbol') or '').upper().strip()


def update_item(item, quote):
    price = quote.get('price')
    if price is None:
        return False
    changed = False
    for key, val in {
        'price': quote.get('price'),
        'refPrice': quote.get('refPrice'),
        'changePct': quote.get('changePct'),
        'volume': quote.get('volume'),
        'lowPrice': quote.get('lowPrice'),
        'highPrice': quote.get('highPrice'),
        'openPrice': quote.get('openPrice'),
        'avgPrice': quote.get('avgPrice'),
    }.items():
        if val is not None and item.get(key) != val:
            item[key] = val
            changed = True
    tech = item.setdefault('technical', {})
    for key in ['price', 'changePct', 'volume']:
        if item.get(key) is not None:
            tech[key] = item.get(key)
    return changed


def refresh_indices(now: str):
    specs = [('VNINDEX', 'VN-Index'), ('HNXINDEX', 'HNX-Index'), ('UPCOMINDEX', 'UPCOM-Index')]
    out = []
    for sym, label in specs:
        try:
            df = Quote(symbol=sym, source='VCI').history(start='2026-05-01', end=datetime.now(TZ).strftime('%Y-%m-%d'), interval='1m')
            if df is None or df.empty or len(df) < 2:
                continue
            df = df.sort_values('time')
            last = df.iloc[-1]
            day = df[df['time'].astype(str).str.slice(0, 10) == str(last.get('time'))[:10]]
            first = day.iloc[0] if not day.empty else df.iloc[-2]
            close = float(last.get('close') or 0)
            ref = float(first.get('open') or df.iloc[-2].get('close') or close)
            change = close - ref
            change_pct = (change / ref * 100) if ref else 0
            out.append({'symbol': sym, 'label': label, 'close': round(close, 2), 'change': round(change, 2), 'changePct': round(change_pct, 2), 'volume': int(float(last.get('volume') or 0)), 'time': str(last.get('time') or '')})
        except Exception as exc:
            print('index failed', sym, exc, flush=True)
    payload = {'updatedAt': now, 'items': out, 'cached': False, 'ttlSeconds': 60, 'source': 'vnstock-index-1m-output'}
    for path in MARKET_OVERVIEW_FILES:
        write_json(path, payload)
    return len(out)


def main():
    src = PUBLIC_DATA / 'market_data.json'
    if not src.exists():
        src = DATA / 'market_data.json'
    payload = load_json(src)
    items = payload.get('items', payload) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise SystemExit('market_data items not found')

    updated = 0
    errors = []
    for item in items:
        sym = symbol_of(item)
        if not sym:
            continue
        try:
            quote_item = _fetch_symbol(sym, include_history=False)
            if quote_item and update_item(item, quote_item):
                updated += 1
        except Exception as exc:
            errors.append({'symbol': sym, 'error': str(exc)[:160]})

    now = datetime.now(TZ).isoformat(timespec='seconds')
    if isinstance(payload, dict):
        payload['updatedAt'] = now
        payload['priceUpdatedAt'] = now
        payload['priceSource'] = 'vps-live-light-cache'
        payload['priceRefreshNote'] = 'Only price/change/volume refreshed. R/S and technical indicators remain precomputed output.'
        payload['priceRefreshErrors'] = errors[:20]
    else:
        payload = {'items': items, 'updatedAt': now, 'priceUpdatedAt': now, 'priceSource': 'vps-live-light-cache', 'priceRefreshErrors': errors[:20]}

    for path in MARKET_DATA_FILES:
        write_json(path, payload)

    watch_items = [x for x in items if symbol_of(x) in DEFAULT_WATCH]
    watch_payload = {'items': watch_items, 'source': 'firebase-static-watch-price-cache', 'updatedAt': now, 'priceUpdatedAt': now}
    for path in MARKET_WATCH_FILES:
        write_json(path, watch_payload)

    index_count = refresh_indices(now)
    print(json.dumps({'updated': updated, 'errors': len(errors), 'indexUpdated': index_count, 'priceUpdatedAt': now}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
