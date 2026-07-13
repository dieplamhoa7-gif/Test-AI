"""Best-effort Chrome rendered crawler for BDS prices.

Uses installed Chrome headless to render/search pages when raw HTTP is blocked
by Cloudflare. This is not guaranteed to bypass CAPTCHA, but it behaves closer
to a real browser than httpx/requests.
"""
from __future__ import annotations

import asyncio
import html
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

from scraper import Listing, SearchCriteria


def _chrome_path() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def _strip_tags(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


PRICE_RE = re.compile(r"(?P<num>\d{1,3}(?:[\.,]\d{1,2})?)\s*(?P<unit>tỷ|ty|triệu/m²|triệu/m2|triệu|tr/m²|tr/m2)", re.I)
URL_RE = re.compile(r"https?://(?:www\.)?(?:batdongsan\.com\.vn|guland\.vn|alonhadat\.com\.vn)[^\s\"'<>]+", re.I)


def _parse_price_tokens(text: str) -> list[tuple[float | None, float | None, str]]:
    out = []
    for m in PRICE_RE.finditer(text):
        raw = m.group('num').replace(',', '.')
        try:
            val = float(raw)
        except Exception:
            continue
        unit = m.group('unit').lower()
        if 'tỷ' in unit or unit == 'ty':
            out.append((val, None, m.group(0)))
        elif 'triệu/m' in unit or 'tr/m' in unit:
            out.append((None, val, m.group(0)))
        elif 'triệu' in unit:
            # avoid treating small fees as property price; keep as ppm-ish only if plausible high
            if val >= 20:
                out.append((None, val, m.group(0)))
    return out


async def chrome_dump_dom(url: str, timeout: int = 35) -> str:
    chrome = _chrome_path()
    if not chrome:
        return ""
    user_data = tempfile.mkdtemp(prefix="bds-chrome-")
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={user_data}",
        "--window-size=1365,1600",
        "--dump-dom",
        url,
    ]
    def run():
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
            return (cp.stdout or '') + '\n' + (cp.stderr or '')
        except Exception:
            return ''
    return await asyncio.to_thread(run)


async def browser_price_buckets(criteria: SearchCriteria, projects, max_projects: int = 4) -> dict[str, list[Listing]]:
    names = [p.get('name','') for p in projects.projects if p.get('name')][:max_projects]
    if not names:
        return {}
    buckets: dict[str, list[Listing]] = {}
    kind = {
        'shophouse': 'shophouse nhà phố thương mại',
        'nha': 'nhà mặt tiền',
        'dat': 'đất',
        'chungcu': 'căn hộ',
        'khoxuong': 'kho xưởng',
    }.get(criteria.property_type, criteria.property_type)
    domains = [
        ('Batdongsan.com.vn', 'batdongsan.com.vn'),
        ('Guland.vn', 'guland.vn'),
        ('Alonhadat.com.vn', 'alonhadat.com.vn'),
    ]
    for name in names:
        for source, domain in domains:
            q = f"site:{domain} {name} {kind} giá"
            # Google rendered search often exposes snippets even if source blocks raw HTTP.
            url = 'https://www.google.com/search?q=' + quote(q)
            dom = await chrome_dump_dom(url, timeout=30)
            text = _strip_tags(dom)
            if not text or any(x in text.lower() for x in ['unusual traffic', 'captcha', 'verify you are human']):
                continue
            urls = []
            for u in URL_RE.findall(dom):
                u = html.unescape(u).split('&')[0]
                if domain in u and u not in urls:
                    urls.append(u)
            prices = _parse_price_tokens(text)
            if not prices and not urls:
                continue
            # create at most 2 browser evidence listings per project/source
            for i, (pt, ppm, token) in enumerate(prices[:2] or [(None, None, 'có link nguồn')]):
                buckets.setdefault(source, []).append(Listing(
                    source=source,
                    title=f"[browser] {name} - {token}",
                    price_total=pt,
                    price_per_m2=ppm,
                    url=urls[0] if urls else '',
                ))
    return buckets
