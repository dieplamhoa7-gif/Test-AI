import json
import os
import re
from pathlib import Path
from typing import List, Dict
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pymongo import MongoClient, DESCENDING

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "news_cache.json"
MAX_NEWS_ITEMS = 500
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


def _clean_key_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or " ")
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = re.sub(r"[^\w\s%+.-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
        scheme = (parsed.scheme or "https").lower()
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if netloc.startswith("m."):
            netloc = netloc[2:]
        path = re.sub(r"/{2,}", "/", parsed.path or "/")
        path = re.sub(r"/(amp|amp/)$", "", path, flags=re.I).rstrip("/") or "/"
        keep_query = []
        for k, v in parse_qsl(parsed.query, keep_blank_values=False):
            lk = k.lower()
            if lk.startswith("utm_") or lk in {"fbclid", "gclid", "zarsrc", "output", "amp", "ref", "source"}:
                continue
            keep_query.append((k, v))
        return urlunparse((scheme, netloc, path, "", urlencode(keep_query, doseq=True), ""))
    except Exception:
        return raw.split("#", 1)[0].split("?", 1)[0].rstrip("/")


def _dedupe_key(item: Dict) -> str:
    return item.get("dedupe_key") or (f"url:{_canonical_url(item.get('url') or '')}" if item.get("url") else "") or (f"title:{_clean_key_text(item.get('title') or '')}" if item.get("title") else "") or f"fallback:{item.get('source','')}|{item.get('published_at','')}"


def _dedupe(items: List[Dict]) -> List[Dict]:
    deduped = []
    seen = set()
    for item in items:
        key = _dedupe_key(item)
        if key in seen:
            continue
        item = dict(item)
        item.setdefault("canonical_url", _canonical_url(item.get("url") or ""))
        item.setdefault("dedupe_key", key)
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
