import json
from pathlib import Path
from typing import List, Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "news_cache.json"
MAX_NEWS_ITEMS = 100


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_news() -> List[Dict]:
    _ensure_dir()
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data[:MAX_NEWS_ITEMS]
    except Exception:
        return []
    return []


def save_news(items: List[Dict]) -> List[Dict]:
    _ensure_dir()
    deduped = []
    seen = set()
    for item in items:
        key = item.get("url") or f"{item.get('title','')}|{item.get('published_at','')}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    deduped = deduped[:MAX_NEWS_ITEMS]
    DATA_FILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
    return deduped


def merge_news(new_items: List[Dict]) -> List[Dict]:
    existing = load_news()
    combined = list(new_items) + existing
    return save_news(combined)
