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


async def find_nearby_projects(client: NineRouterClient, criteria: SearchCriteria) -> ProjectsResult:
    """Dùng AI để xác định khu vực và liệt kê 5 dự án/khu vực comparable."""
    segment = getattr(criteria, "segment", None)
    system = (
        "Bạn là chuyên gia bất động sản Việt Nam, am hiểu các dự án, khu dân cư, đường phố. "
        "Khi nhận toạ độ GPS, bạn xác định chính xác vị trí (phường, quận, thành phố), rồi liệt kê "
        "5 dự án/khu vực phù hợp tiêu chí người dùng để dùng làm tham chiếu định giá."
    )
    user = (
        f"Toạ độ: {criteria.lat}, {criteria.lng}\n"
        f"Ngữ cảnh vị trí đã quy đổi sơ bộ: {getattr(criteria, 'location_context', {})}\n"
        f"Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}\n"
        f"MĐSDĐ: {MDSDD_LABELS.get(criteria.mdsdd) if criteria.mdsdd else 'không yêu cầu'}\n"
        f"Đặc tính: {FEATURE_LABELS.get(criteria.feature) if criteria.feature else 'không yêu cầu'}\n"
        f"Phân khúc nếu có: {segment or 'không yêu cầu'}\n"
        f"Giao dịch: {getattr(criteria, 'transaction', 'buy')}\n\n"
        "Hãy:\n"
        "1. Xác định khu vực (đường/trục đường gần nhất, phường, quận, thành phố/tỉnh) của toạ độ này.\n"
        "2. Khi chọn dự án, chỉ chọn dự án/khu vực nằm trong đúng quận/huyện của toạ độ, trừ khi ghi rõ lý do khoảng cách rất gần.\n"
        "3. Với mỗi dự án, bắt buộc tạo 1 dòng keyword tìm kiếm ngắn gọn theo dạng: Tên dự án + Quận/Huyện + Thành phố. "
        "Ví dụ: 'RiverGate Residence Quận 4 TP Hồ Chí Minh'. Không thêm mô tả hạng/gần đường vào keyword.\n"
        "4. Chọn bán kính tìm kiếm phù hợp mật độ dự án khu vực (1-5 km).\n"
        "5. Liệt kê 5 dự án/khu vực có thể dùng tham chiếu định giá; ưu tiên dự án có nhiều tin rao trên "
        "Batdongsan.com.vn, Guland.vn, Alonhadat.com.vn.\n"
        "6. Mỗi dự án kèm metadata ngắn: chủ đầu tư (developer), quy mô (scale), năm vận hành/bàn giao "
        "(operation_year), tình trạng bàn giao (handover_status).\n\n"
        "Trả về JSON đúng schema:\n"
        "{\n"
        '  "area": "Phường ..., Quận ..., TP ...",\n'
        '  "radius_km": <số>,\n'
        '  "projects": [\n'
        '     {"name": "Tên dự án sạch, không kèm quận/thành phố",\n'
        '      "search_keyword": "Tên dự án + Quận/Huyện + Thành phố để search, ví dụ RiverGate Residence Quận 4 TP Hồ Chí Minh",\n'
        '      "developer": "CĐT hoặc \'Khu vực/không có CĐT đơn nhất\'",\n'
        '      "scale": "vd \'198 ha\' hoặc \'4 block ~1.000 căn\'",\n'
        '      "operation_year": "năm bàn giao hoặc \'đang kiểm chứng\'",\n'
        '      "handover_status": "đã bàn giao/chưa bàn giao/đang triển khai/không áp dụng",\n'
        '      "type_hint": "...", "note": "..."}\n'
        "     ... (đúng 5 phần tử)\n"
        "  ]\n"
        "}\n\n"
        "Quy tắc: không để trống search_keyword/developer/scale/operation_year/handover_status; "
        "không chắc thì ghi 'đang kiểm chứng', không bịa chi tiết. "
        "Tuyệt đối không trả name kiểu 'Phường ... Thành phố ...' hoặc name đã kèm thành phố; "
        "phần quận/thành phố chỉ đưa vào search_keyword. Nếu toạ độ ở Quận 4 thì search_keyword phải có Quận 4, không được dùng TP Thủ Đức."
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
        loc = getattr(criteria, "location_context", {}) or {}
        district = loc.get("district") if isinstance(loc, dict) else ""
        city = (loc.get("city") or loc.get("province")) if isinstance(loc, dict) else ""
        search_keyword = str(p.get("search_keyword") or "").strip()
        if not search_keyword:
            search_keyword = " ".join(x for x in [clean_name, district, city or "TP Hồ Chí Minh"] if x)
        norm.append({
            "name": clean_name,
            "search_keyword": search_keyword,
            "developer": p.get("developer") or "CĐT đang kiểm chứng",
            "scale": p.get("scale") or "quy mô đang kiểm chứng",
            "operation_year": p.get("operation_year") or "đang kiểm chứng",
            "handover_status": p.get("handover_status") or "đang kiểm chứng",
            "type_hint": p.get("type_hint") or "",
            "note": p.get("note") or "",
        })
    norm = [p for p in norm if p["name"]]
    return ProjectsResult(area_description=str(data.get("area") or _loc_str(criteria)), projects=norm)


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
    return ProjectsResult(area_description=area, projects=projects[:5])
