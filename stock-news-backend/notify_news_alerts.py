import base64, hashlib, json, os, time, urllib.parse, urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
NEWS_PATH = ROOT / 'firebase_public' / 'data' / 'news_cache.json'
MAX_NOTIFY = int(os.getenv('NEWS_NOTIFY_MAX', '10'))


def init_firestore():
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        raw_b64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_B64', '').strip()
        raw = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', '').strip()
        if raw_b64:
            info = json.loads(base64.b64decode(raw_b64).decode('utf-8'))
            firebase_admin.initialize_app(credentials.Certificate(info))
        elif raw:
            firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
        else:
            firebase_admin.initialize_app()
    return firestore.client(), firestore


def load_news() -> list[dict[str, Any]]:
    data = json.loads(NEWS_PATH.read_text(encoding='utf-8'))
    items = data.get('items', data) if isinstance(data, dict) else data
    return items if isinstance(items, list) else []


def news_id(item: dict[str, Any]) -> str:
    raw = str(item.get('url') or item.get('link') or item.get('title') or '') + '|' + str(item.get('published_at') or item.get('publishedAt') or '')
    return hashlib.sha1(raw.encode('utf-8', errors='ignore')).hexdigest()


def tg_send(chat_id: str, text: str) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token or not chat_id:
        return False
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text, 'disable_web_page_preview': 'true'}).encode()
    try:
        with urllib.request.urlopen(f'https://api.telegram.org/bot{token}/sendMessage', data=payload, timeout=20) as r:
            return 200 <= r.status < 300
    except Exception as exc:
        print('telegram news failed', chat_id, exc, flush=True)
        return False


def user_symbols(db, uid: str) -> set[str]:
    out = set()
    for doc in db.collection('users').document(uid).collection('watchlist').stream():
        d = doc.to_dict() or {}
        if d.get('enabled', True) is False:
            continue
        sym = str(d.get('symbol') or doc.id or '').upper().strip()
        if sym:
            out.add(sym)
    return out


def item_symbols(item: dict[str, Any]) -> set[str]:
    vals = []
    for key in ('symbols', 'tickers', 'relatedSymbols'):
        v = item.get(key)
        if isinstance(v, list):
            vals.extend(v)
        elif isinstance(v, str):
            vals.extend(v.replace(',', ' ').split())
    for key in ('symbol', 'ticker'):
        v = item.get(key)
        if v:
            vals.append(v)
    text = (str(item.get('title') or '') + ' ' + str(item.get('snippet') or '')).upper()
    # fallback: keep explicit all-caps 3-letter VN tickers in text, conservative only
    for token in text.replace('/', ' ').replace('-', ' ').replace(':', ' ').replace(',', ' ').split():
        token = ''.join(ch for ch in token if ch.isalnum()).upper()
        if 2 <= len(token) <= 5 and token.isalnum() and token.isupper():
            vals.append(token)
    return {str(x).upper().strip() for x in vals if str(x).strip()}


def build_message(item: dict[str, Any], matched: set[str]) -> str:
    title = str(item.get('title') or 'Tin mới').strip()
    source = str(item.get('source') or item.get('publisher') or '').strip()
    published = str(item.get('published_at') or item.get('publishedAt') or '').strip()
    snippet = str(item.get('summary') or item.get('snippet') or '').strip()
    url = str(item.get('url') or item.get('link') or '').strip()
    lines = ['LHInvestment News', '']
    if matched:
        lines.append('Mã liên quan: ' + ', '.join(sorted(matched)))
    lines.append(title[:350])
    meta = ' • '.join(x for x in [source, published] if x)
    if meta:
        lines.append(meta)
    if snippet:
        lines.extend(['', snippet[:500]])
    if url:
        lines.extend(['', url])
    lines.extend(['', 'Tin tức tham khảo, không phải khuyến nghị mua bán.'])
    return '\n'.join(lines)


def main():
    db, firestore = init_firestore()
    items = load_news()[:MAX_NOTIFY]
    state_ref = db.collection('bot_state').document('news_notifications')
    state_snap = state_ref.get()
    state = state_snap.to_dict() if state_snap.exists else {}
    sent_ids = set(state.get('sentIds') or [])
    new_items = [(news_id(x), x) for x in items if news_id(x) not in sent_ids]
    if not new_items:
        print(json.dumps({'newItems': 0, 'sentTelegram': 0}, ensure_ascii=False), flush=True)
        return
    sent = created = 0
    for user_doc in db.collection('users').stream():
        uid = user_doc.id
        user = user_doc.to_dict() or {}
        tg = str(user.get('telegramChatId') or '').strip()
        notify = user.get('newsNotifyEnabled', user.get('notifyEnabled', True)) is not False
        if not notify:
            continue
        symbols = user_symbols(db, uid)
        for nid, item in new_items:
            related = item_symbols(item)
            matched = symbols.intersection(related) if symbols else set()
            # If user has watchlist, only notify matched symbols. If no watchlist, skip to avoid spam.
            if symbols and not matched:
                continue
            payload = {'newsId': nid, 'title': item.get('title'), 'url': item.get('url') or item.get('link'), 'publishedAt': item.get('published_at') or item.get('publishedAt'), 'matchedSymbols': sorted(matched), 'createdAt': firestore.SERVER_TIMESTAMP, 'sentTelegram': False}
            if tg:
                payload['sentTelegram'] = tg_send(tg, build_message(item, matched))
                sent += int(payload['sentTelegram'])
            db.collection('users').document(uid).collection('news_alerts').document(nid).set(payload, merge=True)
            created += 1
    sent_ids = list(dict.fromkeys([nid for nid, _ in new_items] + list(sent_ids)))[:1000]
    state_ref.set({'sentIds': sent_ids, 'updatedAt': firestore.SERVER_TIMESTAMP, 'lastRunEpoch': int(time.time())}, merge=True)
    print(json.dumps({'newItems': len(new_items), 'created': created, 'sentTelegram': sent}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
