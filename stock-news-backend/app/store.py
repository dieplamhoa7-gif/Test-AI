import json
import os
from pathlib import Path
from typing import List, Dict

from pymongo import MongoClient, DESCENDING

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "news_cache.json"
MAX_NEWS_ITEMS = 100
MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DB = os.getenv("MONGODB_DB", "hoa_investment")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "news_cache")


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _mongo_collection():
    if not MONGODB_URI:
        return None
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return client[MONGODB_DB][MONGODB_COLLECTION]


def _dedupe(items: List[Dict]) -> List[Dict]:
    deduped = []
    seen = set()
    for item in items:
        key = item.get("url") or f"{item.get('title','')}|{item.get('published_at','')}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:MAX_NEWS_ITEMS]


def load_news() -> List[Dict]:
    collection = _mongo_collection()
    if collection is not None:
        try:
            items = list(collection.find({}, {"_id": 0}).sort("saved_at", DESCENDING).limit(MAX_NEWS_ITEMS))
            return _dedupe(items)
        except Exception:
            pass

    _ensure_dir()
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return _dedupe(data)
    except Exception:
        return []
    return []


def save_news(items: List[Dict]) -> List[Dict]:
    deduped = _dedupe(items)

    collection = _mongo_collection()
    if collection is not None:
        try:
            collection.delete_many({})
            docs = []
            for idx, item in enumerate(deduped):
                doc = dict(item)
                doc["saved_at"] = idx
                docs.append(doc)
            if docs:
                collection.insert_many(docs)
            return deduped
        except Exception:
            pass

    _ensure_dir()
    DATA_FILE.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
    return deduped


def merge_news(new_items: List[Dict]) -> List[Dict]:
    existing = load_news()
    combined = list(new_items) + existing
    return save_news(combined)
