"""Coordinate-aware fallback source links when search engines throttle/captcha.

This is only a safety net: it must still respect the user's input location.
It ranks known comparable areas/projects by distance from the input lat/lng and
only emits links inside a local radius.
"""
from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from scraper import Listing


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


# Approximate anchors for common Thu Duc / nearby comparables.
# Kept deliberately small; this is fallback evidence, not the valuation engine.
_PROJECT_CATALOG = [
    {
        "name": "Vạn Phúc City",
        "lat": 10.8266,
        "lng": 106.7139,
        "links": {
            "Batdongsan.com.vn": [
                ("Mua bán Shophouse Khu đô thị Vạn Phúc City", "https://batdongsan.com.vn/ban-shophouse-nha-pho-thuong-mai-khu-do-thi-van-phuc-city"),
                ("Nhà đất bán Khu đô thị Vạn Phúc City", "https://batdongsan.com.vn/nha-dat-ban-khu-do-thi-van-phuc-city"),
            ],
            "Guland.vn": [
                ("Khu đô thị Vạn Phúc City", "https://guland.vn/du-an/khu-do-thi-van-phuc-city"),
            ],
        },
    },
    {
        "name": "Him Lam Phú Đông",
        "lat": 10.8589,
        "lng": 106.7517,
        "links": {
            "Guland.vn": [
                ("Him Lam Phú Đông", "https://guland.vn/du-an/him-lam-phu-dong"),
                ("Khu dân cư Him Lam Phú Đông", "https://guland.vn/du-an/khu-dan-cu-him-lam-phu-dong"),
            ],
            "Batdongsan.com.vn": [
                ("Mua bán Him Lam Phú Đông", "https://batdongsan.com.vn/nha-dat-ban-him-lam-phu-dong"),
            ],
        },
    },
    {
        "name": "Phạm Văn Đồng - Thủ Đức",
        "lat": 10.8335,
        "lng": 106.7378,
        "links": {
            "Batdongsan.com.vn": [
                ("Mua bán Shophouse, nhà phố đường Phạm Văn Đồng, Thủ Đức", "https://batdongsan.com.vn/ban-shophouse-nha-pho-thuong-mai-duong-pham-van-dong-71"),
                ("Mua bán nhà mặt tiền đường Phạm Văn Đồng, Thủ Đức", "https://batdongsan.com.vn/ban-nha-mat-pho-duong-pham-van-dong-71"),
            ],
        },
    },
    {
        "name": "Linh Đông",
        "lat": 10.8470,
        "lng": 106.7400,
        "links": {
            "Batdongsan.com.vn": [
                ("Mua bán nhà đất phường Linh Đông", "https://batdongsan.com.vn/nha-dat-ban-phuong-linh-dong"),
            ],
        },
    },
    {
        "name": "Hiệp Bình Phước",
        "lat": 10.8485,
        "lng": 106.7236,
        "links": {
            "Batdongsan.com.vn": [
                ("Mua bán nhà đất phường Hiệp Bình Phước", "https://batdongsan.com.vn/nha-dat-ban-phuong-hiep-binh-phuoc"),
            ],
        },
    },
]


def fallback_source_links_by_location(lat: float, lng: float, radius_km: float = 5.0, limit: int = 5) -> dict[str, list[Listing]]:
    ranked = []
    for item in _PROJECT_CATALOG:
        dist = _haversine_km(lat, lng, item["lat"], item["lng"])
        if dist <= radius_km:
            ranked.append((dist, item))
    ranked.sort(key=lambda x: x[0])
    buckets: dict[str, list[Listing]] = {}
    for dist, item in ranked[:limit]:
        for source, links in item["links"].items():
            for title, url in links:
                buckets.setdefault(source, []).append(
                    Listing(source, f"{item['name']} (~{dist:.1f}km) - {title}", url=url)
                )
    return buckets


def fallback_source_links(project_names: list[str], lat: float | None = None, lng: float | None = None) -> dict[str, list[Listing]]:
    """Backward-compatible fallback.

    Prefer coordinate-aware fallback when lat/lng is provided. The old name-based
    behavior is retained only if caller lacks coordinates.
    """
    if lat is not None and lng is not None:
        return fallback_source_links_by_location(float(lat), float(lng))

    wanted = {(name or "").strip().lower() for name in project_names if (name or "").strip()}
    buckets: dict[str, list[Listing]] = {}
    for item in _PROJECT_CATALOG:
        low = item["name"].lower()
        if not any(w in low or low in w for w in wanted):
            continue
        for source, links in item["links"].items():
            for title, url in links:
                buckets.setdefault(source, []).append(Listing(source, f"{item['name']} - {title}", url=url))
    return buckets
