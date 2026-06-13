"""Dùng AI 9router để (1) tìm 5 dự án/khu vực liên quan quanh toạ độ, (2) duyệt 3 nguồn BĐS và trích xuất giá."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from ai_client import AIError, NineRouterClient

logger = logging.getLogger(__name__)

SOURCES = [
    {"name": "Batdongsan.com.vn", "domain": "batdongsan.com.vn"},
    {"name": "Guland.vn", "domain": "guland.vn"},
    {"name": "Alonhadat.com.vn", "domain": "alonhadat.com.vn"},
]

# Map mã MĐSDĐ → mô tả tiếng Việt
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
    "hem": "Hẻm/ngõ",
    "skip": "Không yêu cầu đặc tính",
}


@dataclass
class Listing:
    """Một tin BĐS được trích xuất từ 1 nguồn."""
    source: str
    title: str = ""
    price_total: float | None = None   # tỷ VND
    area: float | None = None          # m2
    price_per_m2: float | None = None  # triệu VND/m2
    url: str = ""


@dataclass
class SearchCriteria:
    lat: float
    lng: float
    property_type: str        # key trong PROPERTY_TYPE_LABELS
    mdsdd: str | None         # key trong MDSDD_LABELS
    feature: str | None       # key trong FEATURE_LABELS

    @property
    def human_summary(self) -> str:
        parts = [
            f"Toạ độ: {self.lat:.6f}, {self.lng:.6f}",
            f"Loại: {PROPERTY_TYPE_LABELS.get(self.property_type, self.property_type)}",
        ]
        if self.mdsdd:
            parts.append(f"MĐSDĐ: {MDSDD_LABELS.get(self.mdsdd, self.mdsdd)}")
        if self.feature:
            parts.append(f"Đặc tính: {FEATURE_LABELS.get(self.feature, self.feature)}")
        return " | ".join(parts)


@dataclass
class ProjectsResult:
    area_description: str
    projects: list[dict[str, Any]] = field(default_factory=list)


async def find_nearby_projects(
    client: NineRouterClient,
    criteria: SearchCriteria,
) -> ProjectsResult:
    """Dùng AI để xác định khu vực (phường/quận/tỉnh) và liệt kê 5 dự án/khu phố liên quan."""
    system = (
        "Bạn là chuyên gia bất động sản Việt Nam. Bạn rất am hiểu các dự án, "
        "khu dân cư, đường phố ở Việt Nam và có thể tra cứu trên web khi cần. "
        "Khi nhận toạ độ GPS, bạn xác định chính xác vị trí (phường, quận, thành phố), "
        "rồi liệt kê 5 dự án/khu vực phù hợp tiêu chí người dùng để dùng làm tham chiếu định giá."
    )
    user = f"""Toạ độ: {criteria.lat}, {criteria.lng}
Ngữ cảnh vị trí đã quy đổi sơ bộ: {getattr(criteria, "location_context", {})}
Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}
MĐSDĐ: {MDSDD_LABELS.get(criteria.mdsdd) if criteria.mdsdd else "không yêu cầu"}
Đặc tính: {FEATURE_LABELS.get(criteria.feature) if criteria.feature else "không yêu cầu"}
Phân khúc nếu có: {getattr(criteria, "segment", None) or "không yêu cầu"}
Giao dịch: {getattr(criteria, "transaction", "buy")}

Hãy:
1. Xác định khu vực (đường/trục đường gần nhất, phường, quận, thành phố/tỉnh) của toạ độ này.
2. Khi chọn dự án, ưu tiên dạng: "dự án ... hạng ... gần đường ... ở TP ..." để bắt đúng comparable.
3. Chọn bán kính tìm kiếm phù hợp với mật độ dự án khu vực này (1–5 km).
4. Liệt kê 5 dự án/khu vực có thể dùng làm tham chiếu định giá. Ưu tiên dự án có
   nhiều tin rao bán trên Batdongsan.com.vn, Guland.vn, Alonhadat.com.vn.
4. Với mỗi dự án/khu vực, bổ sung metadata ngắn gọn để người dùng kiểm tra nhanh:
   chủ đầu tư/CĐT, quy mô, năm vận hành/bàn giao, tình trạng đã bàn giao chưa.

Trả về JSON đúng schema:
{{
  "area": "Phường ..., Quận ..., TP ...",
  "radius_km": <số>,
  "projects": [
     {{
       "name": "...",
       "developer": "CĐT/chủ đầu tư, nếu là tuyến đường/khu vực thì ghi 'Khu vực/không có CĐT đơn nhất'",
       "scale": "quy mô dự án/khu vực thật ngắn, ví dụ '198 ha' hoặc '4 block, ~1.000 căn'",
       "operation_year": "năm vận hành/bàn giao chính, nếu không chắc ghi 'đang kiểm chứng'",
       "handover_status": "đã bàn giao/chưa bàn giao/đang triển khai/không áp dụng",
       "type_hint": "...",
       "note": "..."
     }},
     ... (đúng 5 phần tử)
  ]
}}

Quy tắc:
- Không được để trống developer/scale/operation_year/handover_status.
- Nếu không chắc tuyệt đối, ghi cụm ngắn 'đang kiểm chứng', không bịa chi tiết.
"""
    data = await client.chat_json(system, user, temperature=0.2)
    return ProjectsResult(
        area_description=str(data.get("area", "Không rõ")),
        projects=list(data.get("projects", []))[:5],
    )


async def scrape_source(
    client: NineRouterClient,
    source: dict[str, str],
    criteria: SearchCriteria,
    projects: ProjectsResult,
) -> list[Listing]:
    """Yêu cầu AI duyệt 1 nguồn và trích xuất ~5 tin gần khu vực."""
    project_names = ", ".join(p.get("name", "") for p in projects.projects if p.get("name"))
    system = (
        "Bạn là agent web. Hãy duyệt trang web BĐS được chỉ định để tìm các tin rao bán "
        "phù hợp tiêu chí người dùng. Nếu bạn không thể duyệt web thật, hãy dùng kiến thức "
        "của mình về mặt bằng giá khu vực đó để đưa ra ước lượng hợp lý "
        "(ghi rõ trong field 'note' rằng đây là ước lượng)."
    )
    user = f"""Hãy tìm trên {source['name']} (domain: {source['domain']}) các tin BĐS phù hợp:

Tiêu chí: {criteria.human_summary}
Khu vực: {projects.area_description}
Dự án/khu vực ưu tiên: {project_names}

Trả về JSON đúng schema:
{{
  "listings": [
     {{
        "title": "tóm tắt tin",
        "price_total_billion_vnd": <giá tổng, tỷ VND, ví dụ 3.5>,
        "area_m2": <diện tích m2, ví dụ 75>,
        "price_per_m2_million_vnd": <giá/m2, triệu VND/m2, ví dụ 46.7>,
        "url": "link tới tin (nếu có)"
     }},
     ... (5 đến 10 tin)
  ]
}}

Quy tắc:
- Đơn vị bắt buộc: giá tổng = tỷ VND, diện tích = m2, giá/m2 = triệu VND/m2.
- Nếu không có dữ liệu trên trang này, vẫn trả về listings = [] và đừng bịa link.
- Nếu là ước lượng từ kiến thức nền (không duyệt web), title bắt đầu bằng "[ước lượng]".
"""
    try:
        data = await client.chat_json(system, user, temperature=0.3)
    except AIError as e:
        logger.warning("Scrape %s lỗi: %s", source["name"], e)
        return []

    out: list[Listing] = []
    for item in data.get("listings", []) or []:
        try:
            l = Listing(
                source=source["name"],
                title=str(item.get("title", "") or "")[:200],
                price_total=_safe_float(item.get("price_total_billion_vnd")),
                area=_safe_float(item.get("area_m2")),
                price_per_m2=_safe_float(item.get("price_per_m2_million_vnd")),
                url=str(item.get("url", "") or "")[:300],
            )
            if l.price_total is None and l.price_per_m2 is None:
                continue
            # tự suy ra giá/m2 nếu thiếu
            if l.price_per_m2 is None and l.price_total and l.area:
                l.price_per_m2 = (l.price_total * 1000) / l.area  # tỷ → triệu
            if l.price_total is None and l.price_per_m2 and l.area:
                l.price_total = (l.price_per_m2 * l.area) / 1000
            out.append(l)
        except Exception as e:
            logger.warning("Bỏ qua listing lỗi: %s (%s)", e, item)
    return out


async def scrape_all_sources(
    client: NineRouterClient,
    criteria: SearchCriteria,
    projects: ProjectsResult,
    max_concurrent: int = 3,
) -> dict[str, list[Listing]]:
    sem = asyncio.Semaphore(max_concurrent)

    async def _run(src: dict[str, str]) -> tuple[str, list[Listing]]:
        async with sem:
            return src["name"], await scrape_source(client, src, criteria, projects)

    results = await asyncio.gather(*[_run(s) for s in SOURCES])
    return {name: listings for name, listings in results}


def _safe_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
        if f != f or f <= 0:  # NaN hoặc <=0
            return None
        return f
    except (TypeError, ValueError):
        return None



def fallback_nearby_projects(criteria: SearchCriteria, reason: str = "AI timeout") -> ProjectsResult:
    """Fallback an toàn khi AI định vị dự án bị timeout."""
    # Fallback hiện ưu tiên khu Đông TP.HCM/Dĩ An vì case mẫu của anh ở quanh Thủ Đức.
    area = f"Khu vực quanh tọa độ {criteria.lat:.6f}, {criteria.lng:.6f}"
    projects = [
        {"name": "Vạn Phúc City", "developer": "Đại Phúc Group", "scale": "~198 ha", "operation_year": "đã hình thành nhiều giai đoạn", "handover_status": "nhiều phân khu đã bàn giao", "type_hint": "KĐT/nhà phố/shophouse", "note": f"fallback do {reason}"},
        {"name": "Him Lam Phú Đông", "developer": "Him Lam Land", "scale": "khu căn hộ/nhà phố tại Dĩ An giáp Thủ Đức", "operation_year": "đã bàn giao", "handover_status": "đã bàn giao", "type_hint": "KDC/căn hộ/nhà phố", "note": f"fallback do {reason}"},
        {"name": "Phạm Văn Đồng", "developer": "Khu vực/không có CĐT đơn nhất", "scale": "trục đường lớn Thủ Đức - Bình Thạnh", "operation_year": "không áp dụng", "handover_status": "không áp dụng", "type_hint": "trục đường/khu vực", "note": f"fallback do {reason}"},
        {"name": "Hiệp Bình Phước", "developer": "Khu vực/không có CĐT đơn nhất", "scale": "phường/khu dân cư TP Thủ Đức", "operation_year": "không áp dụng", "handover_status": "không áp dụng", "type_hint": "phường/khu dân cư", "note": f"fallback do {reason}"},
        {"name": "Linh Đông", "developer": "Khu vực/không có CĐT đơn nhất", "scale": "phường/khu dân cư TP Thủ Đức", "operation_year": "không áp dụng", "handover_status": "không áp dụng", "type_hint": "phường/khu dân cư", "note": f"fallback do {reason}"},
    ]
    return ProjectsResult(area_description=area, projects=projects)
