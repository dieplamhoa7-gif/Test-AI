from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path
from urllib.parse import quote_plus

from map_snapshot import MapPoint, haversine_km


def chrome_path() -> str | None:
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if Path(p).exists():
            return p
    return None


def _clean_query_name(name: str) -> str:
    n = (name or "").strip()
    n = re.sub(r"^(dự\s*án|du\s*an|khu\s+vực|khu\s+vuc)\s+", "", n, flags=re.I).strip()
    for pat in [
        r"\s+hạng\s+.*$", r"\s+hang\s+.*$", r"\s+gần\s+.*$", r"\s+gan\s+.*$",
        r"\s+tại\s+.*$", r"\s+tai\s+.*$", r"\s+ở\s+.*$", r"\s+o\s+.*$",
        r"\s+Quận\s+\d+.*$", r"\s+Quan\s+\d+.*$", r"\s+TP\.?\s*Hồ\s+Chí\s+Minh.*$",
    ]:
        n2 = re.sub(pat, "", n, flags=re.I).strip(" -–,;")
        if n2 and len(n2) >= 3:
            n = n2
    return n



def _norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _score_place_name(query_name: str, place_name: str) -> int:
    q = _norm(query_name)
    p = _norm(place_name)
    q_tokens = [t for t in q.split() if len(t) >= 3]
    score = 0
    if q and q in p:
        score += 100
    score += sum(18 for t in q_tokens if t in p)
    good = ["apartment", "residence", "riverside", "gold", "view", "masteri", "millennium", "saigon", "royal", "can ho", "toa nha"]
    score += sum(4 for t in good if t in p)
    bad = ["cinema", "lotte", "office", "saigon office", "travel", "tour", "agency", "cafe", "coffee", "restaurant", "spa", "shop", "store", "gym", "school", "bank"]
    score -= sum(60 for t in bad if t in p)
    return score


def _coords_from_place_href(href: str):
    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", href or "")
    if m:
        return float(m.group(1)), float(m.group(2))
    return None

def _coords_from_url(url: str, prefer_place: bool = True):
    # Google Maps URL can contain viewport coords (@lat,lng) and true place coords (!3dlat!4dlng).
    # For pins, prefer !3d/!4d because @ is often just the camera/viewport center.
    m_place = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url or "")
    if prefer_place and m_place:
        return float(m_place.group(1)), float(m_place.group(2)), "place"
    m_view = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+),", url or "")
    if m_view:
        return float(m_view.group(1)), float(m_view.group(2)), "viewport"
    if m_place:
        return float(m_place.group(1)), float(m_place.group(2)), "place"
    return None


async def geocode_projects_google_maps(criteria, projects, timeout_sec: int = 75) -> list[MapPoint]:
    """Geocode project pins by searching Google Maps, not AI-estimating coordinates."""
    chrome = chrome_path()
    if not chrome:
        return []
    from playwright.async_api import async_playwright

    loc = getattr(criteria, "location_context", {}) or {}
    district = loc.get("district") if isinstance(loc, dict) else None
    city = loc.get("city") if isinstance(loc, dict) else "TP Hồ Chí Minh"
    origin_lat, origin_lng = criteria.lat, criteria.lng
    names = [(p.get("name") or "").strip() for p in projects.projects[:5] if p.get("name")]
    if not names:
        return []

    out: list[MapPoint] = []
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=os.environ.get("BDS_GMAPS_PROFILE") or str(Path.home() / "AppData" / "Local" / "LHBDS_GoogleMaps_Profile"),
            executable_path=chrome,
            headless=True,
            viewport={"width": 1200, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            for raw_name in names:
                qname = _clean_query_name(raw_name)
                query = " ".join(x for x in [qname, district, city] if x)
                url = "https://www.google.com/maps/search/" + quote_plus(query)
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    await page.wait_for_timeout(6000)
                    # Prefer actual place result links. Search URL @lat,lng is only viewport center.
                    links = await page.locator('a[href*="/maps/place/"]').evaluate_all("""
                        els => els.slice(0,20).map(a => ({
                            name: a.getAttribute('aria-label') || a.innerText || '',
                            href: a.href || ''
                        }))
                    """)
                    candidates = []
                    for link in links:
                        pname = (link.get('name') or '').strip()
                        href = link.get('href') or ''
                        coords2 = _coords_from_place_href(href)
                        if not pname or not coords2:
                            continue
                        sc = _score_place_name(qname, pname)
                        candidates.append((sc, pname, coords2))
                    candidates.sort(reverse=True, key=lambda x: x[0])
                    if candidates and candidates[0][0] >= 65:
                        sc, pname, (lat, lng) = candidates[0]
                        dist = haversine_km(origin_lat, origin_lng, lat, lng)
                        if dist <= 8.0:
                            out.append(MapPoint(raw_name[:80], lat, lng, note=f"Google Maps result: {pname}; q={query}; score={sc}; dist={dist:.2f}km"))
                        continue
                    # Direct exact place pages sometimes contain !3d/!4d in page.url; accept only place coords.
                    coords = _coords_from_url(page.url)
                    if coords:
                        lat, lng, kind = coords
                        if kind == "place":
                            dist = haversine_km(origin_lat, origin_lng, lat, lng)
                            if dist <= 8.0:
                                out.append(MapPoint(raw_name[:80], lat, lng, note=f"Google Maps direct place: {query}; dist={dist:.2f}km"))
                except Exception:
                    continue
        finally:
            await ctx.close()
    return out[:5]


def geocode_projects_google_maps_sync(criteria, projects, timeout_sec: int = 75) -> list[MapPoint]:
    return asyncio.run(geocode_projects_google_maps(criteria, projects, timeout_sec=timeout_sec))


async def geocode_names_nominatim(criteria, names: list[str], max_dist_km: float = 8.0) -> list[MapPoint]:
    """Fallback geocoder qua OpenStreetMap Nominatim (HTTP thuan, khong can Chrome).

    Dung khi Google Maps headless bi chan/khong tra toa do, de map van co pin du an.
    Chi nhan ket qua trong ban kinh hop ly quanh toa do goc de tranh trung ten khac vung.
    """
    import httpx

    loc = getattr(criteria, "location_context", {}) or {}
    district = loc.get("district") if isinstance(loc, dict) else None
    city = loc.get("city") or loc.get("province") if isinstance(loc, dict) else "TP Ho Chi Minh"
    origin_lat, origin_lng = criteria.lat, criteria.lng
    out: list[MapPoint] = []
    headers = {
        "User-Agent": "LHRealEstate-RnD/1.0 (contact: lh-bds-rnd)",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    }
    d = 0.12
    viewbox = f"{origin_lng - d},{origin_lat + d},{origin_lng + d},{origin_lat - d}"
    try:
        async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as client:
            for raw_name in names:
                qname = _clean_query_name(raw_name)
                if not qname:
                    continue
                query = ", ".join(x for x in [qname, district, city] if x)
                params = {
                    "q": query,
                    "format": "jsonv2",
                    "limit": "5",
                    "countrycodes": "vn",
                    "viewbox": viewbox,
                    "bounded": "1",
                }
                try:
                    r = await client.get("https://nominatim.openstreetmap.org/search", params=params)
                    if r.status_code >= 400:
                        continue
                    results = r.json() or []
                except Exception:
                    continue
                best = None
                best_score = -1
                for item in results:
                    try:
                        lat = float(item.get("lat"))
                        lng = float(item.get("lon"))
                    except Exception:
                        continue
                    dist = haversine_km(origin_lat, origin_lng, lat, lng)
                    if dist > max_dist_km:
                        continue
                    sc = _score_place_name(qname, item.get("display_name") or "") - dist
                    if sc > best_score:
                        best_score = sc
                        best = (lat, lng, dist, item.get("display_name") or "")
                if best:
                    lat, lng, dist, dname = best
                    out.append(MapPoint(raw_name[:80], lat, lng, note=f"Nominatim: {dname[:80]}; dist={dist:.2f}km"))
                await asyncio.sleep(1.1)
    except Exception:
        return out
    return out
