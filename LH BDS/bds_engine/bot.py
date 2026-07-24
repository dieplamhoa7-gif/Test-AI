"""R&D helper functions (REBUILT 2026-07-11 sau khi file gốc bị xóa nhầm).

rd_api_server.py / web_valuation_api.* import từ đây:
    resolve_location_context, build_ai_estimate_buckets,
    build_project_price_report, build_valuation_points

Ngoài ra giữ cmd_start/cmd_gia/on_callback dạng stub để cloud_app.py còn import được
(không dùng cho luồng web R&D qua rd_api_server).
"""
from __future__ import annotations

import asyncio
import logging
import math
import re
import unicodedata
from typing import Any

import httpx

from scraper import Listing, SearchCriteria, ProjectsResult, PROPERTY_TYPE_LABELS
from map_snapshot import MapPoint, haversine_km
from valuation_map import ValuationMapPoint

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Location context (reverse geocode)                                          #
# --------------------------------------------------------------------------- #
def _norm_ascii(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower().strip()


async def resolve_location_context(client, criteria: SearchCriteria) -> dict[str, Any]:
    """Reverse-geocode tọa độ -> dict vị trí (OSM Nominatim + Overpass nearest road/POI).

    Không phụ thuộc AI để tránh lỗi khi 9router down. Trả dict với các key mà
    web_valuation_api dùng: display_name, road, street, ward, suburb, district,
    city, province, postcode, nearest_road, nearest_pois, nearby_radius_m, search_hint.
    """
    lat, lng = criteria.lat, criteria.lng
    headers = {
        "User-Agent": "LHRealEstate-RnD/1.0 (contact: lh-bds-rnd)",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    }
    ctx: dict[str, Any] = {}
    try:
        async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as c:
            r = await c.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lng, "format": "jsonv2", "zoom": "18", "addressdetails": "1"},
            )
            if r.status_code < 400:
                j = r.json() or {}
                a = j.get("address", {}) or {}
                road = a.get("road") or a.get("pedestrian") or a.get("residential") or ""
                ward = a.get("suburb") or a.get("quarter") or a.get("ward") or a.get("village") or ""
                district = a.get("city_district") or a.get("county") or a.get("district") or ""
                raw_city = a.get("city") or a.get("town") or ""
                state = a.get("state") or a.get("province") or ""
                city = raw_city or state
                # Nominatim may return "Thành phố Thủ Đức" as city for HCMC
                # coordinates. For search keywords, city must be the province-level
                # city (TP Hồ Chí Minh); Thu Duc belongs in district scope only.
                city_l = str(city or "").lower()
                state_l = str(state or "").lower()
                if "thủ đức" in city_l or "thu duc" in city_l:
                    if state and ("hồ chí minh" in state_l or "ho chi minh" in state_l or "hcm" in state_l):
                        city = state
                    else:
                        city = "TP Hồ Chí Minh"
                ctx = {
                    "display_name": j.get("display_name") or "",
                    "road": road,
                    "street": road,
                    "ward": ward,
                    "suburb": ward,
                    "district": district,
                    "city": city,
                    "province": city,
                    "postcode": a.get("postcode") or "",
                }
    except Exception as e:
        logger.warning("Nominatim reverse lỗi: %s", e)

    # Overpass: nearest road name + POIs (bán kính 350m).
    radius = 350
    try:
        q = (
            f"[out:json][timeout:15];("
            f"way(around:{radius},{lat},{lng})[highway][name];"
            f"node(around:{radius},{lat},{lng})[amenity][name];"
            f");out center 30;"
        )
        async with httpx.AsyncClient(headers=headers, timeout=25) as c:
            r = await c.post("https://overpass-api.de/api/interpreter", data={"data": q})
            if r.status_code < 400:
                els = (r.json() or {}).get("elements", [])
                roads = []
                pois = []
                for el in els:
                    name = (el.get("tags", {}) or {}).get("name")
                    if not name:
                        continue
                    if "center" in el:
                        elat, elng = el["center"]["lat"], el["center"]["lon"]
                    elif "lat" in el:
                        elat, elng = el["lat"], el["lon"]
                    else:
                        continue
                    dist = haversine_km(lat, lng, elat, elng) * 1000.0
                    tags = el.get("tags", {}) or {}
                    if tags.get("highway"):
                        roads.append({"name": name, "highway": tags.get("highway"), "distance_m": dist})
                    elif tags.get("amenity"):
                        pois.append({"name": name, "amenity": tags.get("amenity"), "distance_m": dist})
                roads.sort(key=lambda x: x["distance_m"])
                pois.sort(key=lambda x: x["distance_m"])
                if roads:
                    ctx["nearest_road"] = roads[0]
                    ctx.setdefault("road", roads[0]["name"])
                    ctx.setdefault("street", roads[0]["name"])
                ctx["nearest_pois"] = pois[:5]
                ctx["nearby_radius_m"] = radius
    except Exception as e:
        logger.warning("Overpass lỗi: %s", e)

    parts = [ctx.get("road"), ctx.get("ward"), ctx.get("district"), ctx.get("city")]
    ctx["search_hint"] = ", ".join(str(x) for x in parts if x) or ctx.get("display_name", "")
    if not ctx.get("display_name"):
        ctx["display_name"] = ctx["search_hint"] or f"{lat}, {lng}"
    return ctx


# --------------------------------------------------------------------------- #
# AI price estimate buckets (chỉ dùng khi không có mẫu giá thật)              #
# --------------------------------------------------------------------------- #
async def build_ai_estimate_buckets(client, criteria: SearchCriteria, projects: ProjectsResult) -> dict[str, list[Listing]]:
    is_rent = getattr(criteria, "transaction", "buy") == "rent"
    is_rent_chungcu = is_rent and getattr(criteria, "rent_subtype", "") == "rent_chungcu"
    unit = "triệu/căn/tháng" if is_rent_chungcu else ("triệu/m²/tháng" if is_rent else "triệu/m²")
    names = [p.get("name", "") for p in (projects.projects or [])[:5] if p.get("name")]
    system = (
        "Bạn là chuyên gia thẩm định giá BĐS. Đưa khoảng giá thị trường ước lượng gần đây cho "
        "từng dự án/khu vực. Đây là ƯỚC LƯỢNG, không phải tin rao thật; không bịa URL."
    )
    user = (
        f"Khu vực: {projects.area_description}\n"
        f"Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}\n"
        f"Giao dịch: {'thuê' if is_rent else 'mua bán'}\n"
        f"Dự án/khu vực: {', '.join(names) or 'theo khu vực'}\n\n"
        f"Trả JSON: {{\"estimates\": [{{\"project\": \"...\", \"price_per_m2\": <số {unit}>, "
        "\"low\": <số>, \"high\": <số>}}]}}."
    )
    try:
        data = await client.chat_json(system, user, temperature=0.2)
    except Exception as e:
        logger.warning("build_ai_estimate_buckets lỗi: %s", e)
        return {}
    buckets: dict[str, list[Listing]] = {}
    for item in (data or {}).get("estimates", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        try:
            ppm = float(str(item.get("price_per_m2")).replace(",", "."))
        except Exception:
            continue
        proj = str(item.get("project") or projects.area_description)
        buckets.setdefault("AI estimate", []).append(
            Listing(source="AI estimate", title=f"[ước lượng] {proj}", price_per_m2=ppm, url="")
        )
    return buckets


# --------------------------------------------------------------------------- #
# Report                                                                      #
# --------------------------------------------------------------------------- #
def _median(vals: list[float]) -> float | None:
    vals = sorted(v for v in vals if isinstance(v, (int, float)))
    if not vals:
        return None
    n = len(vals)
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2


async def build_project_price_report(client, criteria: SearchCriteria, projects: ProjectsResult, buckets: dict) -> str:
    """Báo cáo giá theo dự án/khu vực (chủ yếu deterministic từ mẫu thật)."""
    is_rent = getattr(criteria, "transaction", "buy") == "rent"
    is_rent_chungcu = is_rent and getattr(criteria, "rent_subtype", "") == "rent_chungcu"
    unit = "triệu/căn/tháng" if is_rent_chungcu else ("triệu/m²/tháng" if is_rent else "triệu/m²")
    lines = ["📍 *Định giá theo dự án/khu vực comparable*", "", f"Khu vực: {projects.area_description}", ""]
    all_ppm: list[float] = []
    for i, p in enumerate(projects.projects[:5], 1):
        name = p.get("name") or f"Comparable {i}"
        rows = []
        for src, listings in (buckets or {}).items():
            for l in listings or []:
                title = (getattr(l, "title", "") or "").lower()
                if name.lower() in title or name.lower() in str(src).lower():
                    rows.append(l)
        ppms = [getattr(l, "price_per_m2", None) for l in rows if getattr(l, "price_per_m2", None)]
        ppms = [x for x in ppms if x]
        lines.append(f"{i}. {name}")
        lines.append(f"   - CĐT: {p.get('developer', 'đang kiểm chứng')}; quy mô: {p.get('scale', 'đang kiểm chứng')}")
        if ppms:
            med = _median(ppms)
            all_ppm.extend(ppms)
            lines.append(f"   - Giá ref median: ~{med:.1f} {unit} ({len(ppms)} mẫu; {min(ppms):.1f}-{max(ppms):.1f})")
            urls = [getattr(l, "url", "") for l in rows if getattr(l, "url", "")][:2]
            for u in urls:
                lines.append(f"     {u}")
        else:
            lines.append("   - Chưa có mẫu giá khớp nguồn thật cho dự án này.")
        lines.append("")
    if all_ppm:
        med = _median(all_ppm)
        lines.append(f"➡️ Mặt bằng giá tham chiếu khu vực: ~{med:.1f} {unit} (median {len(all_ppm)} mẫu).")
    else:
        lines.append("➡️ Chưa thu thập được mẫu giá thật đủ tin cậy; cần kiểm chứng thủ công/mở rộng từ khóa.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Valuation map points                                                         #
# --------------------------------------------------------------------------- #
def _fmt_price_range(vals: list[float], unit: str) -> str:
    vals = [v for v in (vals or []) if isinstance(v, (int, float)) and v > 0]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    if abs(hi - lo) < 1e-9:
        return f"{lo:.1f} {unit}"
    return f"{lo:.1f}-{hi:.1f} {unit}"


def _listing_project_match(project_name: str, title: str) -> bool:
    pn = _norm_ascii(project_name)
    tt = _norm_ascii(title)
    if not pn:
        return False
    if pn in tt:
        return True
    stop = {"can", "ho", "du", "an", "khu", "vuc", "chung", "cu", "toa", "block", "tp", "quan", "phuong"}
    toks = [t for t in re.findall(r"[a-z0-9]+", pn) if len(t) >= 3 and t not in stop]
    if not toks:
        return False
    hits = sum(1 for t in toks if t in tt)
    return hits >= max(1, min(2, len(toks)))


def build_valuation_points(projects, map_points: list[MapPoint], buckets: dict, transaction: str = "buy") -> list[ValuationMapPoint]:
    """Gắn dữ liệu giá trung bình vào tọa độ dự án để vẽ map."""
    all_rows = []
    for source, listings in buckets.items():
        for l in listings:
            all_rows.append((source, l))

    out: list[ValuationMapPoint] = []
    is_rent = (transaction == "rent")
    for mp in map_points:
        scoped = [
            (src, l) for src, l in all_rows
            if "::" in src and src.split("::", 1)[1].strip().lower() == mp.name.strip().lower()
        ]
        matched = scoped or [(src, l) for src, l in all_rows if _listing_project_match(mp.name, l.title)]
        matched = [(src, l) for src, l in matched if getattr(l, "url", "") and src != "AI estimate"]
        prices = [l.price_total for _, l in matched if l.price_total]
        ppms = [l.price_per_m2 for _, l in matched if l.price_per_m2]
        sources = sorted({src.split("::", 1)[0] for src, _ in matched})
        avg_ppm = (sum(ppms) / len(ppms)) if ppms else None
        avg_price = (sum(prices) / len(prices)) if prices else None
        if is_rent:
            if avg_price:
                price_label = f"TB {avg_price*1000:.1f} triệu/tháng"
                if avg_ppm:
                    price_label += f" | {avg_ppm:.2f} triệu/m²/tháng"
            elif avg_ppm:
                price_label = f"TB {avg_ppm:.2f} triệu/m²/tháng"
            else:
                price_label = "chưa có mẫu thuê khớp"
            price_range = _fmt_price_range([p*1000 for p in prices], "triệu/tháng") if prices else ""
        else:
            price_label = f"TB {avg_ppm:.0f} tr/m²" if avg_ppm else "chưa có mẫu giá khớp"
            price_range = _fmt_price_range(prices, "tỷ")
        out.append(ValuationMapPoint(
            name=mp.name,
            lat=mp.lat,
            lng=mp.lng,
            price_per_m2=avg_ppm,
            price_label=price_label,
            price_range=price_range,
            sample_count=len(matched) if matched else None,
            source=", ".join(sources) if sources else "chưa có mẫu khớp",
            note="; ".join(sorted({(l.url or "") for _, l in matched if l.url})[:2])
        ))
    return out


# --------------------------------------------------------------------------- #
# Telegram stubs (giữ cloud_app.py import được; luồng web dùng rd_api_server) #
# --------------------------------------------------------------------------- #
async def cmd_start(update, context):  # pragma: no cover
    raise NotImplementedError("Telegram bot handlers không được rebuild; dùng rd_api_server cho web R&D.")


async def cmd_gia(update, context):  # pragma: no cover
    raise NotImplementedError("Telegram bot handlers không được rebuild; dùng rd_api_server cho web R&D.")


async def on_callback(update, context):  # pragma: no cover
    raise NotImplementedError("Telegram bot handlers không được rebuild; dùng rd_api_server cho web R&D.")
