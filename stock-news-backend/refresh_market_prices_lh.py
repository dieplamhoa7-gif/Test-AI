import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.market_data import _fetch_symbol

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PUBLIC_DATA = ROOT / 'firebase_public' / 'data'
MARKET_DATA_FILES = [DATA / 'market_data.json', PUBLIC_DATA / 'market_data.json']
MARKET_WATCH_FILES = [PUBLIC_DATA / 'market_watch.json']
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

    print(json.dumps({'updated': updated, 'errors': len(errors), 'priceUpdatedAt': now}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
