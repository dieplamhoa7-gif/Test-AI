import json, os, urllib.parse, urllib.request


def tg(method: str, payload: dict | None = None):
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        raise SystemExit('missing TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{token}/{method}'
    data = urllib.parse.urlencode(payload or {}).encode() if payload is not None else None
    with urllib.request.urlopen(url, data=data, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def init_firestore():
    import base64
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


def main():
    db, firestore = init_firestore()
    ref = db.collection('bot_state').document('telegram_updates')
    snap = ref.get()
    state = snap.to_dict() if snap.exists else {}
    offset = int(state.get('offset') or 0)
    res = tg('getUpdates', {'offset': offset, 'timeout': 0, 'limit': 50, 'allowed_updates': json.dumps(['message'])})
    updates = res.get('result') or []
    max_id = offset - 1
    replied = 0
    for u in updates:
        update_id = int(u.get('update_id') or 0)
        max_id = max(max_id, update_id)
        msg = u.get('message') or {}
        chat = msg.get('chat') or {}
        chat_id = chat.get('id')
        text = str(msg.get('text') or '').strip().lower()
        if not chat_id:
            continue
        if text.startswith('/start') or 'id' in text or 'chat' in text or text in {'test', 'hello', 'hi'}:
            reply = (
                'LHInvestment Bot\n\n'
                f'Telegram chat ID của bạn là:\n{chat_id}\n\n'
                'Hãy copy số này và dán vào ô Telegram chat ID trên trang Account.\n'
                'Sau đó bấm Lưu thông tin.'
            )
            tg('sendMessage', {'chat_id': str(chat_id), 'text': reply})
            replied += 1
    if max_id >= offset:
        ref.set({'offset': max_id + 1, 'updatedAt': firestore.SERVER_TIMESTAMP}, merge=True)
    print(json.dumps({'updates': len(updates), 'replied': replied, 'nextOffset': max_id + 1 if updates else offset}, ensure_ascii=False))


if __name__ == '__main__':
    main()
