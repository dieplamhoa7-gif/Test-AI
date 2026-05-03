import base64, json, os, time, urllib.parse, urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'firebase_public' / 'data'
MARKET = DATA / 'market_data.json'
COOLDOWN_SECONDS = int(os.getenv('ALERT_COOLDOWN_SECONDS', '21600'))
SUPPORT_BREAK = float(os.getenv('SUPPORT_BREAK_PCT', '0.995'))
SUPPORT_TOUCH = float(os.getenv('SUPPORT_TOUCH_PCT', '1.005'))
RESIST_TOUCH = float(os.getenv('RESIST_TOUCH_PCT', '0.995'))
RESIST_BREAK = float(os.getenv('RESIST_BREAK_PCT', '1.005'))


def f(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def load_market() -> dict[str, dict[str, Any]]:
    data = json.loads(MARKET.read_text(encoding='utf-8'))
    items = data.get('items', data) if isinstance(data, dict) else data
    out = {}
    for item in items:
        sym = str(item.get('ticker') or item.get('symbol') or '').upper()
        if sym:
            out[sym] = item
    return out


def tg_send(chat_id: str, text: str) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token or not chat_id:
        return False
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode()
    try:
        with urllib.request.urlopen(url, data=payload, timeout=20) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print('telegram failed', chat_id, e, flush=True)
        return False


def build_rules(sym: str, item: dict[str, Any]):
    tech = item.get('technical') or {}
    price = f(item.get('price') or tech.get('price') or tech.get('lastClose'))
    support = f(tech.get('activeSupportDay') or tech.get('supportDay') or tech.get('support'))
    resist = f(tech.get('activeResistanceDay') or tech.get('resistanceDay') or tech.get('resistance'))
    if not price:
        return []
    alerts = []
    if support:
        if price < support * SUPPORT_BREAK:
            alerts.append(('support_break', f'{sym} gãy hỗ trợ: giá {price:.2f} < hỗ trợ {support:.2f}'))
        elif price <= support * SUPPORT_TOUCH:
            alerts.append(('support_touch', f'{sym} chạm/gần hỗ trợ: giá {price:.2f}, hỗ trợ {support:.2f}'))
    if resist:
        if price > resist * RESIST_BREAK:
            alerts.append(('resistance_break', f'{sym} vượt kháng cự: giá {price:.2f} > kháng cự {resist:.2f}'))
        elif price >= resist * RESIST_TOUCH:
            alerts.append(('resistance_touch', f'{sym} chạm/gần kháng cự: giá {price:.2f}, kháng cự {resist:.2f}'))
    return [{'symbol': sym, 'type': t, 'message': m, 'price': price, 'support': support, 'resistance': resist} for t, m in alerts]


def init_firestore():
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        raw = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', '').strip()
        raw_b64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_B64', '').strip()
        if raw_b64:
            info = json.loads(base64.b64decode(raw_b64).decode('utf-8'))
            firebase_admin.initialize_app(credentials.Certificate(info))
        elif raw:
            info = json.loads(raw)
            firebase_admin.initialize_app(credentials.Certificate(info))
        else:
            firebase_admin.initialize_app()
    return firestore.client(), firestore


def main():
    db, firestore = init_firestore()
    market = load_market()
    now = int(time.time())
    sent = created = skipped = 0
    for user_doc in db.collection('users').stream():
        uid = user_doc.id
        user = user_doc.to_dict() or {}
        tg = str(user.get('telegramChatId') or '').strip()
        notify = user.get('notifyEnabled', True) is not False
        wl = list(db.collection('users').document(uid).collection('watchlist').where('enabled', '==', True).stream())
        for w in wl:
            sym = str((w.to_dict() or {}).get('symbol') or w.id).upper()
            item = market.get(sym)
            if not item:
                continue
            for alert in build_rules(sym, item):
                key = f"{sym}_{alert['type']}"
                state_ref = db.collection('users').document(uid).collection('alert_state').document(key)
                state = state_ref.get().to_dict() if state_ref.get().exists else {}
                last = int(state.get('lastSentEpoch') or 0)
                if now - last < COOLDOWN_SECONDS:
                    skipped += 1
                    continue
                payload = {**alert, 'createdAt': firestore.SERVER_TIMESTAMP, 'sentTelegram': False}
                if notify and tg:
                    text = 'LHInvestment Alert\n\n' + alert['message'] + '\n\nDữ liệu tham khảo, không phải khuyến nghị mua bán.'
                    payload['sentTelegram'] = tg_send(tg, text)
                    sent += int(payload['sentTelegram'])
                db.collection('users').document(uid).collection('alerts').add(payload)
                state_ref.set({'lastSentEpoch': now, 'lastType': alert['type'], 'lastMessage': alert['message'], 'updatedAt': firestore.SERVER_TIMESTAMP}, merge=True)
                created += 1
    print(json.dumps({'created': created, 'sentTelegram': sent, 'skippedCooldown': skipped}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
