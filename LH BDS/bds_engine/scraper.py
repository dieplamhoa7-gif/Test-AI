"""R&D core data models + AI comparable discovery.

REBUILT 2026-07-11 sau khi file gốc bị xóa nhầm. Giữ đúng interface mà
web_valuation_api.* và rd_api_server.py đang import:
    SearchCriteria, ProjectsResult, Listing,
    find_nearby_projects, scrape_all_sources, fallback_nearby_projects

Nhiệm vụ:
1) find_nearby_projects: dùng AI 9router chọn 5 dự án/khu vực comparable quanh tọa độ.
2) scrape_all_sources: dùng AI trích mẫu giá tham khảo từ 3 nguồn (bổ trợ; giá real
   chính lấy qua Playwright ở playwright_bds_scraper).
3) fallback_nearby_projects: khi AI lỗi/timeout, tạo khung comparable evidence-only
   bám theo geocode (không bịa dự án).
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from ai_client import AIError, NineRouterClient

logger = logging.getLogger(__name__)

SOURCES = [
    {"name": "Batdongsan.com.vn", "domain": "batdongsan.com.vn"},
    {"name": "Guland.vn", "domain": "guland.vn"},
    {"name": "Alonhadat.com.vn", "domain": "alonhadat.com.vn"},
]

MDSDD_LABELS = {
    "ODT": "Đất ở đô thị (ODT)",
    "ONT": "Đất ở nông thôn (ONT)",
    "TMD": "Đất thương mại dịch vụ (TMD)",
    "SKC": "Đất cơ sở sản xuất kinh doanh (SKC)",
    "CLN": "Đất trồng cây lâu năm (CLN)",
    "NN": "Đất nông nghiệp (NN)",
}

PROPERTY_TYPE_LABELS = {
    "dat": "Đất",
    "nha": "Nhà phố/Nhà riêng",
    "chungcu": "Căn hộ chung cư",
    "khoxuong": "Kho/Xưởng",
    "shophouse": "Shophouse/Mặt bằng",
}

FEATURE_LABELS = {
    "mattien": "Mặt tiền (đường lớn)",
    "cango": "Căn góc / 2 mặt tiền",
    "corner": "Căn góc / 2 mặt tiền",
    "hem": "Hẻm/ngõ",
    "skip": "Không yêu cầu đặc tính",
}


@dataclass
class SearchCriteria:
    lat: float
    lng: float
    property_type: str = "chungcu"
    mdsdd: str | None = None
    feature: str = "skip"
    transaction: str = "buy"
    rent_subtype: str | None = None
    segment: str | None = None
    location_context: dict = field(default_factory=dict)
    human_summary: str = ""


@dataclass
class Listing:
    source: str
    title: str = ""
    price_total: float | None = None       # tỷ đồng (mua) hoặc quy ước (thuê)
    area: float | None = None              # m2
    price_per_m2: float | None = None       # triệu/m2 (mua) hoặc triệu/m2/tháng (thuê)
    url: str = ""


@dataclass
class ProjectsResult:
    area_description: str
    projects: list = field(default_factory=list)
    excluded_comparables: list = field(default_factory=list)


def _loc_str(criteria: SearchCriteria) -> str:
    loc = getattr(criteria, "location_context", {}) or {}
    parts = [loc.get(k) for k in ("road", "ward", "suburb", "district", "city", "province")]
    parts = [str(p) for p in parts if p]
    return ", ".join(dict.fromkeys(parts)) or f"quanh {criteria.lat:.6f}, {criteria.lng:.6f}"


def _requested_project_name(criteria: SearchCriteria) -> str:
    """Extract an explicit project/query name from user payload.

    Coordinates often reverse-geocode to a road/ward. If the user typed a
    project name (e.g. Lovera Vista), keep it as the first comparable instead
    of falling back to generic geocode scopes only.
    """
    chunks = []
    for attr in ("project_name", "project", "text", "address", "human_summary"):
        v = getattr(criteria, attr, None)
        if isinstance(v, str) and v.strip():
            chunks.append(v.strip())
    loc = getattr(criteria, "location_context", {}) or {}
    for key in ("project", "project_name", "name", "query"):
        v = loc.get(key)
        if isinstance(v, str) and v.strip():
            chunks.append(v.strip())
    raw = " | ".join(chunks)
    # Prefer well-known project-like phrases; keep conservative to avoid using raw coordinates.
    known = ["Lovera Vista"]
    for name in known:
        if re.search(re.escape(name), raw, flags=re.I):
            return name
    m = re.search(r"\b([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){1,5})\b", raw)
    if not m:
        return ""
    name = m.group(1).strip()
    if re.search(r"^(Toa|Tọa|Nguyen|Nguyễn|Thanh|Thành|Phuong|Phường|Quan|Quận|Ho|Hồ|Chi|Chí|Minh)\b", name, flags=re.I):
        return ""
    if re.search(r"\d+\.\d+", name):
        return ""
    return name


def _explicit_project_candidate(name: str) -> dict:
    return {
        "name": name,
        "developer": "CĐT đang kiểm chứng",
        "scale": "quy mô đang kiểm chứng",
        "operation_year": "đang kiểm chứng",
        "handover_status": "đang kiểm chứng",
        "type_hint": "explicit_project",
        "note": "Tên dự án do người dùng nhập; ưu tiên search trực tiếp trước khi fallback geocode",
    }


async def find_nearby_projects(client: NineRouterClient, criteria: SearchCriteria) -> ProjectsResult:
    """Dùng AI để xác định khu vực và liệt kê 5 dự án/khu vực comparable."""
    segment = getattr(criteria, "segment", None)
    system = (
        "Bạn là chuyên gia bất động sản Việt Nam, am hiểu các dự án, khu dân cư, tòa nhà văn phòng, trung tâm thương mại và đường phố. "
        "Khi nhận toạ độ GPS, bạn chỉ dùng phường/quận/thành phố để định vị, rồi liệt kê đúng 5 dự án/tòa nhà/khu vực comparable "
        "tương đồng nhất để dùng tham chiếu định giá. Comparable phải là 5 tên dự án/tòa nhà thật nếu loại tài sản là căn hộ/chung cư hoặc văn phòng; không được trả lời bằng danh sách phường. Comparable phải gần tọa độ và tương đồng về loại tài sản, hạng/phân khúc, vị trí, khả năng khai thác và mặt bằng thị trường."
    )
    explicit_name = _requested_project_name(criteria)
    user = (
        f"Toạ độ: {criteria.lat}, {criteria.lng}\n"
        f"Ngữ cảnh vị trí đã quy đổi sơ bộ: {getattr(criteria, 'location_context', {})}\n"
        f"Tên dự án/từ khoá người dùng nhập nếu có: {explicit_name or getattr(criteria, 'human_summary', '') or 'không có'}\n"
        f"Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}\n"
        f"MĐSDĐ: {MDSDD_LABELS.get(criteria.mdsdd) if criteria.mdsdd else 'không yêu cầu'}\n"
        f"Đặc tính: {FEATURE_LABELS.get(criteria.feature) if criteria.feature else 'không yêu cầu'}\n"
        f"Phân khúc nếu có: {segment or 'không yêu cầu'}\n"
        f"Giao dịch: {getattr(criteria, 'transaction', 'buy')}\n\n"
        "Hãy:\n"
        "1. Xác định khu vực quanh tọa độ: đường/trục đường gần nhất, phường, quận, thành phố/tỉnh — chỉ để làm ngữ cảnh area, KHÔNG dùng phường/quận làm name comparable.\n"
        "2. Chọn đúng 5 comparable gần tọa độ nhất nhưng KHÔNG chỉ gần về địa lý; với căn hộ/chung cư/văn phòng phải ưu tiên tên dự án/tòa nhà thật, không trả 'Phường ...' làm comparable. Phải tương đồng theo thứ tự ưu tiên:\n"
        "   a) cùng loại tài sản/giao dịch (căn hộ thuê, văn phòng thuê, sàn thương mại thuê, căn hộ bán, đất/nhà phố...),\n"
        "   b) cùng hạng/phân khúc nếu có (A/B/C, cao cấp/trung cấp/bình dân; văn phòng hạng A/B/C; retail prime/neighborhood...),\n"
        "   c) cùng vị thế đô thị/trục kết nối/khu dân cư hoặc khu thương mại xung quanh,\n"
        "   d) cùng giai đoạn vận hành/bàn giao và chất lượng khai thác,\n"
        "   e) có khả năng tìm được tin rao/giá kiểm chứng trên Batdongsan.com.vn, Guland.vn, Alonhadat.com.vn.\n"
        "3. Chọn bán kính phù hợp mật độ thị trường: ưu tiên 1-3 km ở khu dày dự án, có thể mở 5-8 km nếu thiếu comparable cùng hạng.\n"
        "4. Không chọn dự án chỉ vì nổi tiếng nếu lệch hạng, quá xa, khác loại tài sản hoặc khác thị trường thuê/bán.\n"
        "5. Mỗi comparable kèm metadata ngắn: chủ đầu tư/đơn vị quản lý (developer), quy mô (scale), năm vận hành/bàn giao "
        "(operation_year), tình trạng bàn giao/khai thác (handover_status), và ghi chú vì sao tương đồng (note).\n\n"
        "Trả về JSON đúng schema:\n"
        "{\n"
        '  "area": "Phường ..., Quận ..., TP ...",\n'
        '  "radius_km": <số>,\n'
        '  "projects": [\n'
        '     {"name": "...", "developer": "CĐT hoặc \'Khu vực/không có CĐT đơn nhất\'",\n'
        '      "scale": "vd \'198 ha\' hoặc \'4 block ~1.000 căn\'",\n'
        '      "operation_year": "năm bàn giao hoặc \'đang kiểm chứng\'",\n'
        '      "handover_status": "đã bàn giao/chưa bàn giao/đang triển khai/không áp dụng",\n'
        '      "type_hint": "...", "note": "..."}\n'
        "     ... (đúng 5 phần tử)\n"
        "  ]\n"
        "}\n\n"
        "Quy tắc: không để trống developer/scale/operation_year/handover_status; "
        "không chắc thì ghi 'đang kiểm chứng', không bịa chi tiết. "
        "Name phải là tên dự án/tòa nhà/khu vực sạch, không trả name kiểu 'Phường ...', 'Quận ...', 'Thành phố ...' hoặc name đã kèm thành phố; tránh làm keyword search bị lặp thành phố. Nếu loại tài sản là rent_chungcu/chungcu/căn hộ, name bắt buộc là tên chung cư/dự án căn hộ thật. "
        "Nếu không đủ 5 dự án/tòa nhà đúng cùng loại trong bán kính gần, có thể dùng khu vực/tuyến đường comparable nhưng phải ghi rõ lý do trong note."
    )
    data = await client.chat_json(system, user, temperature=0.2)
    if not isinstance(data, dict):
        raise AIError("find_nearby_projects: AI không trả JSON hợp lệ")
    projects = list(data.get("projects", []))[:5]
    # Chuẩn hoá field, không để trống các key bắt buộc.
    norm = []
    for p in projects:
        if not isinstance(p, dict):
            continue
        raw_name = str(p.get("name") or "").strip()
        # Defensive cleanup: models sometimes still return names like
        # "dự án The Gold View hạng B gần đường Bến Vân Đồn" despite the prompt.
        # Keep only the clean project/area name; descriptive context stays in note/type_hint.
        clean_name = re.sub(r"^(dự\s*án|du\s*an|khu\s+vực|khu\s+vuc)\s+", "", raw_name, flags=re.I).strip()
        clean_name = re.sub(r"\s+(hạng|hang|gần|gan|tại|tai|ở|o)\s+.*$", "", clean_name, flags=re.I).strip(" -–,;")
        norm.append({
            "name": clean_name,
            "developer": p.get("developer") or "CĐT đang kiểm chứng",
            "scale": p.get("scale") or "quy mô đang kiểm chứng",
            "operation_year": p.get("operation_year") or "đang kiểm chứng",
            "handover_status": p.get("handover_status") or "đang kiểm chứng",
            "type_hint": p.get("type_hint") or "",
            "note": p.get("note") or "",
        })
    norm = [p for p in norm if p["name"]]
    if explicit_name and explicit_name.lower() not in {p["name"].lower() for p in norm}:
        norm.insert(0, _explicit_project_candidate(explicit_name))
    return ProjectsResult(area_description=str(data.get("area") or _loc_str(criteria)), projects=norm[:5])


def _num(x: Any) -> float | None:
    try:
        return float(str(x).replace(",", ".").strip())
    except Exception:
        return None


async def _scrape_one_source(client: NineRouterClient, source: dict, criteria: SearchCriteria,
                             projects: ProjectsResult) -> list[Listing]:
    """AI trích ~5 tin tham khảo gần khu vực cho 1 nguồn (bổ trợ, không thay Playwright)."""
    names = ", ".join(p.get("name", "") for p in (projects.projects or [])[:5] if p.get("name"))
    is_rent = getattr(criteria, "transaction", "buy") == "rent"
    system = (
        "Bạn là trợ lý dữ liệu BĐS. Dựa trên hiểu biết về mặt bằng giá thị trường gần đây, "
        "hãy đưa khoảng giá tham khảo cho khu vực/dự án được hỏi. "
        "KHÔNG bịa URL tin đăng. Nếu không chắc URL thật, để trống url."
    )
    unit = "triệu/m²/tháng" if is_rent else "triệu/m²"
    user = (
        f"Nguồn tham khảo: {source['name']} ({source['domain']})\n"
        f"Khu vực: {projects.area_description}\n"
        f"Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}\n"
        f"Giao dịch: {'thuê' if is_rent else 'mua bán'}\n"
        f"Các dự án/khu vực quan tâm: {names or 'theo khu vực'}\n\n"
        f"Trả JSON: {{\"listings\": [{{\"project\": \"tên dự án/khu vực\", \"price_per_m2\": <số {unit}>, "
        "\"area_m2\": <số hoặc null>, \"price_total\": <tỷ hoặc null>, \"url\": \"\", "
        "\"note\": \"nhãn [ước lượng] nếu không có tin thật\"}}]}. Tối đa 5 phần tử."
    )
    try:
        data = await client.chat_json(system, user, temperature=0.2)
    except Exception as e:
        logger.warning("scrape source %s lỗi: %s", source.get("name"), e)
        return []
    out: list[Listing] = []
    for item in (data or {}).get("listings", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        ppm = _num(item.get("price_per_m2"))
        total = _num(item.get("price_total"))
        area = _num(item.get("area_m2"))
        if not ppm and not total:
            continue
        title = f"[ước lượng {source['name']}] {item.get('project') or projects.area_description}"
        note = str(item.get("note") or "")
        if note:
            title += f" - {note}"
        out.append(Listing(
            source=f"{source['name']} [ước lượng]",
            title=title,
            price_total=total,
            area=area,
            price_per_m2=ppm,
            url=str(item.get("url") or ""),
        ))
    return out


async def scrape_all_sources(client: NineRouterClient, criteria: SearchCriteria, projects: ProjectsResult,
                             max_concurrent: int = 1) -> dict[str, list[Listing]]:
    """Trích mẫu giá tham khảo từ 3 nguồn (bổ trợ cho Playwright)."""
    sem = asyncio.Semaphore(max(1, int(max_concurrent or 1)))
    buckets: dict[str, list[Listing]] = {}

    async def run(src):
        async with sem:
            rows = await _scrape_one_source(client, src, criteria, projects)
            if rows:
                buckets[src["name"]] = rows

    await asyncio.gather(*(run(s) for s in SOURCES), return_exceptions=True)
    return buckets


def fallback_nearby_projects(criteria: SearchCriteria, reason: str = "") -> ProjectsResult:
    """Khung comparable evidence-only bám geocode khi AI lỗi/timeout. Không bịa dự án."""
    loc = getattr(criteria, "location_context", {}) or {}
    ward = loc.get("ward") or loc.get("suburb") or loc.get("phuong") or ""
    district = loc.get("district") or loc.get("county") or ""
    city = loc.get("city") or loc.get("province") or "TP Hồ Chí Minh"
    road = loc.get("road") or loc.get("street") or ""
    area = _loc_str(criteria)
    scopes = [
        " ".join(x for x in [road, ward, district, city] if x),
        " ".join(x for x in [ward, district, city] if x),
        " ".join(x for x in [district, city] if x),
    ]
    projects = []
    seen = set()
    explicit_name = _requested_project_name(criteria)
    if explicit_name:
        projects.append(_explicit_project_candidate(explicit_name))
        seen.add(explicit_name.lower())
    for sc in scopes:
        sc = sc.strip()
        if not sc or sc.lower() in seen:
            continue
        seen.add(sc.lower())
        projects.append({
            "name": sc,
            "developer": "Khu vực/không có CĐT đơn nhất (fallback geocode)",
            "scale": "tham chiếu theo khu vực/tuyến đường",
            "operation_year": "không áp dụng",
            "handover_status": "không áp dụng",
            "type_hint": "area",
            "note": f"fallback geocode-only ({reason})" if reason else "fallback geocode-only",
        })
    # Rental apartment must still render a 5-item comparable set even when AI times out.
    # Use local area scopes as explicit market comparables; backend/search later attaches evidence/price if available.
    if getattr(criteria, "transaction", "buy") == "rent" and getattr(criteria, "rent_subtype", "") == "rent_chungcu":
        base = [x for x in [road, ward, district, city] if x]
        more = [
            " ".join(x for x in [ward, district, city] if x),
            " ".join(x for x in [district, city] if x),
            f"Căn hộ cho thuê {district or city}".strip(),
            f"Chung cư cho thuê {city}".strip(),
            f"Thị trường căn hộ cho thuê quanh {criteria.lat:.5f},{criteria.lng:.5f}",
        ]
        for name in more:
            name = name.strip()
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            projects.append({
                "name": name,
                "developer": "Khu vực căn hộ cho thuê - cần kiểm chứng dự án cụ thể",
                "scale": "tham chiếu thị trường thuê căn hộ",
                "operation_year": "không áp dụng",
                "handover_status": "đang khai thác/cho thuê",
                "type_hint": "rent_apartment_area",
                "note": f"fallback rent_chungcu ({reason})" if reason else "fallback rent_chungcu",
            })
            if len(projects) >= 5:
                break
    return ProjectsResult(area_description=area, projects=projects[:5])
