"""Web search + basic listing extraction with real source URLs.

Uses DuckDuckGo HTML search as a lightweight discovery layer, then optional page fetch/extract.
"""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from unicodedata import normalize

import httpx

from ai_search_planner import SearchTarget
from scraper import Listing, SearchCriteria

SOURCE_DOMAINS = {
    "Batdongsan.com.vn": "batdongsan.com.vn",
    "Guland.vn": "guland.vn",
    "Alonhadat.com.vn": "alonhadat.com.vn",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"


@dataclass
class SearchHit:
    source: str
    project: str
    title: str
    url: str
    snippet: str = ""


def _clean_ddg_url(href: str) -> str:
    href = unescape(href or "")
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        if qs.get("uddg"):
            return unquote(qs["uddg"][0])
    return href


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s or "").replace("  ", " ").strip()


async def ddg_search(query: str, max_results: int = 8) -> list[tuple[str, str, str]]:
    url = "https://duckduckgo.com/html/?q=" + quote_plus(query)
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        html = r.text
    results: list[tuple[str, str, str]] = []
    # DDG html result block
    blocks = re.findall(r'<div class="result results_links.*?</div>\s*</div>', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'<a rel="nofollow" class="result__a".*?</a>', html, flags=re.S)
    for block in blocks:
        m = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
        if not m:
            continue
        href = _clean_ddg_url(m.group(1))
        title = _strip_tags(unescape(m.group(2)))
        sn = ""
        sm = re.search(r'<a class="result__snippet"[^>]*>(.*?)</a>', block, flags=re.S) or re.search(r'<div class="result__snippet"[^>]*>(.*?)</div>', block, flags=re.S)
        if sm:
            sn = _strip_tags(unescape(sm.group(1)))
        if href.startswith("http"):
            results.append((title, href, sn))
        if len(results) >= max_results:
            break
    return results


def _domain_ok(url: str, domain: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    return domain.lower() in netloc


def _looks_listing(url: str) -> bool:
    u = url.lower()
    return not any(x in u for x in ["/login", "facebook.com", "youtube.com"])


def _location_ok(text: str, target: SearchTarget) -> bool:
    t = (text or "").lower()
    # Ưu tiên TP.HCM + các cụm địa danh đã gặp trong hệ LH BDS.
    # Trước đây danh sách này thiên về Thủ Đức/Dĩ An nên tọa độ Bình Hưng - Bình Chánh
    # dễ rơi khỏi discovery/fallback dù search ngoài ra Lovera Vista.
    positive = ["thủ đức", "thu duc", "hiệp bình", "hiep binh", "linh đông", "linh dong", "dĩ an", "di an", "bình dương", "binh duong", "tp.hcm", "hồ chí minh", "ho chi minh", "vạn phúc", "van phuc", "him lam phú đông", "him lam phu dong", "bình hưng", "binh hung", "bình chánh", "binh chanh", "nguyễn văn linh", "nguyen van linh", "lovera vista", "mizuki", "saigon mia", "trung sơn", "trung son", "nam sài gòn", "nam sai gon"]
    negative = ["bắc từ liêm", "bac tu liem", "cổ nhuế", "co nhue", "hà nội", "ha noi", "nam từ liêm", "nam tu liem"]
    if any(n in t for n in negative):
        return False
    # Nếu không dính địa danh xấu, cho qua; AI/project grouping sẽ lọc tiếp.
    return True


def _transaction_ok(text: str, criteria: SearchCriteria | None = None) -> bool:
    t = (text or "").lower()
    # Hiện valuation ưu tiên giá bán; cho thuê chỉ giữ nếu không còn gì khác ở bước future.
    if "cho thuê" in t or "sang nhượng" in t:
        return False
    return True


async def discover_real_source_links(targets: list[SearchTarget], per_source_limit: int = 5) -> dict[str, list[SearchHit]]:
    out: dict[str, list[SearchHit]] = {name: [] for name in SOURCE_DOMAINS}
    seen: set[str] = set()
    tasks = []
    meta = []
    for target in targets:
        for source, domain in SOURCE_DOMAINS.items():
            for kw in target.keywords[:4]:
                q = f'site:{domain} {kw}'
                tasks.append(ddg_search(q, max_results=5))
                meta.append((target, source, domain))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for (target, source, domain), res in zip(meta, results):
        if isinstance(res, Exception):
            continue
        for title, url, snippet in res:
            if url in seen or not _domain_ok(url, domain) or not _looks_listing(url):
                continue
            text = (title + " " + snippet + " " + url).lower()
            if any(ex in text for ex in target.exclude_keywords):
                continue
            if not _location_ok(text, target):
                continue
            if not _transaction_ok(text):
                continue
            seen.add(url)
            out[source].append(SearchHit(source=source, project=target.project, title=title[:220], url=url[:500], snippet=snippet[:300]))
            if len(out[source]) >= per_source_limit:
                break
    return out


def listings_from_search_hits(hits_by_source: dict[str, list[SearchHit]]) -> dict[str, list[Listing]]:
    buckets: dict[str, list[Listing]] = {}
    for source, hits in hits_by_source.items():
        buckets[source] = [Listing(source=source, title=h.title, url=h.url) for h in hits]
    return buckets


def _slug_vi(text: str) -> str:
    s = normalize('NFD', str(text or ''))
    s = ''.join(ch for ch in s if not re.match(r'[\u0300-\u036f]', ch))
    s = s.replace('đ', 'd').replace('Đ', 'D').lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


async def discover_batdongsan_evidence_links(targets: list[SearchTarget], per_target_limit: int = 2) -> dict[str, list[Listing]]:
    """Fast evidence layer for comparable flow.

    Playwright price scraping can return numeric samples without reliable source URLs,
    and DDG discovery can timeout. This function first tries DDG restricted to
    batdongsan.com.vn, then always adds deterministic Batdongsan search/category URLs
    per project so the report has an evidence trail instead of empty evidence.
    """
    bucket: list[Listing] = []
    seen: set[str] = set()
    for target in (targets or [])[:6]:
        project = (target.project or '').strip()
        if not project:
            continue
        # 1) Real indexed results from DDG, short timeout handled by caller.
        for kw in (target.keywords or [project])[:2]:
            q = f'site:batdongsan.com.vn {kw}'
            try:
                rows = await ddg_search(q, max_results=per_target_limit)
            except Exception:
                rows = []
            for title, url, snippet in rows:
                if url in seen or not _domain_ok(url, 'batdongsan.com.vn') or not _looks_listing(url):
                    continue
                text = (title + ' ' + snippet + ' ' + url).lower()
                if any(ex in text for ex in target.exclude_keywords):
                    continue
                if not _transaction_ok(text):
                    continue
                seen.add(url)
                bucket.append(Listing('Batdongsan.com.vn', f'{project} - {title[:180]}', url=url[:500]))
        # 2) Deterministic Batdongsan search/category evidence URL. It is not a fake listing;
        # it is a reproducible source-search page for manual verification when indexed links are absent.
        slug = _slug_vi(project)
        deterministic = []
        # Category URL: can show project page/listings/prices when Batdongsan has that slug.
        # This is acceptable as category-level evidence, but still weaker than a parsed listing URL.
        if slug:
            deterministic.append(('Batdongsan.com.vn [category-evidence]', f'{project} - Batdongsan căn hộ bán (category; kiểm chứng được giá nếu trang tồn tại)', f'https://batdongsan.com.vn/ban-can-ho-chung-cu-{slug}'))
        # Search URL: manual verification only. It must not be treated as price evidence.
        deterministic.append(('Batdongsan.com.vn [manual-check-only]', f'{project} - Batdongsan search (manual-check; không dùng làm evidence giá)', 'https://batdongsan.com.vn/tim-kiem?keyword=' + quote_plus(project)))
        for source_label, title, url in deterministic:
            if url not in seen:
                seen.add(url)
                bucket.append(Listing(source_label, title, url=url))
    return {'Batdongsan.com.vn': bucket} if bucket else {}


def merge_listing_buckets(primary: dict[str, list[Listing]], evidence: dict[str, list[Listing]]) -> dict[str, list[Listing]]:
    merged: dict[str, list[Listing]] = {k: list(v) for k, v in primary.items()}
    for source, evs in evidence.items():
        bucket = merged.setdefault(source, [])
        existing_urls = {l.url for l in bucket if l.url}
        for ev in evs:
            if ev.url and ev.url not in existing_urls:
                # Keep as evidence-only listing; price may be filled later by AI/report from search snippet/page extraction
                bucket.append(ev)
                existing_urls.add(ev.url)
    return merged
