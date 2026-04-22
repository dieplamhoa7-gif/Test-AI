import os
import re
from datetime import datetime
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "8"))
MIN_FULLTEXT_LENGTH = int(os.getenv("MIN_FULLTEXT_LENGTH", "280"))

SOURCE_CONFIG = {
    "cafef": {
        "rss": [
            "https://cafef.vn/thi-truong-chung-khoan.rss",
            "https://cafef.vn/doanh-nghiep.rss",
        ],
        "homepage": "https://cafef.vn/",
    },
    "vietstock": {
        "rss": [
            "https://vietstock.vn/rss/chung-khoan.rss",
            "https://vietstock.vn/rss/doanh-nghiep.rss",
        ],
        "homepage": "https://vietstock.vn/",
    },
}


def _now_iso():
    return datetime.utcnow().isoformat() + "Z"


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    }
    with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def _extract_article_text(html: str, source: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    selectors = {
        "cafef": [
            ".detail-content p",
            ".contentdetail p",
            ".knc-content p",
            "article p",
        ],
        "vietstock": [
            ".pContent p",
            ".content-news-detail p",
            ".m-b-20 p",
            "article p",
        ],
    }

    texts = []
    for selector in selectors.get(source, ["article p", "main p", "p"]):
        nodes = soup.select(selector)
        if nodes:
            texts = [_clean_text(node.get_text(" ")) for node in nodes]
            texts = [t for t in texts if len(t) > 40]
            if texts:
                break

    if not texts:
        texts = [_clean_text(node.get_text(" ")) for node in soup.find_all("p")]
        texts = [t for t in texts if len(t) > 40]

    article_text = "\n".join(texts)
    return article_text[:8000].strip()


def fetch_full_text(url: str, source: str) -> str:
    try:
        html = _fetch(url)
        return _extract_article_text(html, source)
    except Exception:
        return ""


def enrich_item_content(item: dict) -> dict:
    full_text = _clean_text(item.get("fullText") or "")
    if len(full_text) < MIN_FULLTEXT_LENGTH and item.get("url"):
        fetched_text = fetch_full_text(item["url"], item.get("source", ""))
        if fetched_text:
            full_text = fetched_text

    if full_text:
        item["fullText"] = full_text
    else:
        item["fullText"] = ""

    item["snippet"] = _clean_text(item.get("snippet") or "")
    return item


def _parse_rss_items(xml_text: str, source: str, limit: int) -> list[dict]:
    items = []
    soup = BeautifulSoup(xml_text, "xml")
    for item in soup.find_all("item")[:limit]:
        title = _clean_text(item.title.text if item.title else "")
        link = _clean_text(item.link.text if item.link else "")
        pub_date = _clean_text(item.pubDate.text if item.pubDate else "")
        desc = _clean_text(item.description.text if item.description else "")

        if not title or not link:
            continue

        items.append(
            {
                "source": source,
                "title": title,
                "url": link,
                "published_at": pub_date,
                "snippet": desc[:300],
                "fullText": desc,
                "fetched_at": _now_iso(),
            }
        )

    return items


def parse_cafef_homepage(html: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for a in soup.select("a"):
        href = a.get("href", "")
        title = _clean_text(a.get_text(" "))
        if not href or not title:
            continue
        if "/" not in href or len(title) < 25:
            continue
        if href.startswith("/"):
            href = "https://cafef.vn" + href
        if "cafef.vn" not in urlparse(href).netloc:
            continue
        results.append(
            {
                "source": "cafef",
                "title": title,
                "url": href,
                "published_at": "",
                "snippet": "",
                "fullText": "",
                "fetched_at": _now_iso(),
            }
        )
        if len(results) >= limit:
            break
    return results


def parse_vietstock_homepage(html: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for a in soup.select("a"):
        href = a.get("href", "")
        title = _clean_text(a.get_text(" "))
        if not href or not title:
            continue
        if len(title) < 25:
            continue
        if href.startswith("/"):
            href = "https://vietstock.vn" + href
        if "vietstock.vn" not in urlparse(href).netloc:
            continue
        results.append(
            {
                "source": "vietstock",
                "title": title,
                "url": href,
                "published_at": "",
                "snippet": "",
                "fullText": "",
                "fetched_at": _now_iso(),
            }
        )
        if len(results) >= limit:
            break
    return results


def collect_news(limit: int = 10) -> list[dict]:
    collected: list[dict] = []
    per_source_limit = min(MAX_ARTICLES_PER_SOURCE, max(1, limit // 2 + 1))

    for source, cfg in SOURCE_CONFIG.items():
        source_items = []
        for rss_url in cfg["rss"]:
            try:
                xml = _fetch(rss_url)
                source_items.extend(_parse_rss_items(xml, source=source, limit=per_source_limit))
            except Exception:
                continue

        if not source_items:
            try:
                html = _fetch(cfg["homepage"])
                if source == "cafef":
                    source_items = parse_cafef_homepage(html, per_source_limit)
                else:
                    source_items = parse_vietstock_homepage(html, per_source_limit)
            except Exception:
                source_items = []

        collected.extend(source_items[:per_source_limit])

    seen = set()
    dedup = []
    for item in collected:
        key = item.get("url")
        if not key or key in seen:
            continue
        seen.add(key)
        dedup.append(enrich_item_content(item))

    return dedup[:limit]
