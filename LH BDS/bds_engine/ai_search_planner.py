"""AI-assisted search planning for BĐS comparable listings."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai_client import NineRouterClient
from scraper import PROPERTY_TYPE_LABELS, FEATURE_LABELS, MDSDD_LABELS, SearchCriteria, ProjectsResult


@dataclass
class SearchTarget:
    project: str
    area: str = ""
    keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)


async def build_search_targets(client: NineRouterClient, criteria: SearchCriteria, projects: ProjectsResult) -> list[SearchTarget]:
    project_names = [p.get("name", "") for p in projects.projects if p.get("name")]
    system = (
        "Bạn là chuyên gia tìm kiếm dữ liệu bất động sản Việt Nam. "
        "Nhiệm vụ: tạo bộ keyword tối ưu để tìm tin rao thật trên Batdongsan, Guland, Alonhadat. "
        "Không bịa giá/link. Chỉ lập kế hoạch search. Trả JSON hợp lệ."
    )
    user = f"""Tiêu chí định giá:
- Tọa độ: {criteria.lat}, {criteria.lng}
- Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}
- MĐSDĐ: {MDSDD_LABELS.get(criteria.mdsdd, criteria.mdsdd) if criteria.mdsdd else 'không yêu cầu'}
- Đặc tính: {FEATURE_LABELS.get(criteria.feature, criteria.feature) if criteria.feature else 'không yêu cầu'}
- Khu vực: {projects.area_description}
- Dự án/khu vực comparable: {project_names}

Tạo keywords để tìm tin rao thật. Mỗi dự án/khu vực nên có 4-6 keyword gồm tên chính thức, tên biến thể, loại tài sản, phường/quận.

JSON schema:
{{
  "targets": [
    {{
      "project": "Tên dự án/khu vực",
      "area": "phường/quận/thành phố nếu biết",
      "keywords": ["..."],
      "exclude_keywords": ["..."]
    }}
  ]
}}
"""
    try:
        data: dict[str, Any] = await client.chat_json(system, user, temperature=0.15)
    except Exception:
        return fallback_search_targets(criteria, projects)
    out: list[SearchTarget] = []
    for item in data.get("targets", []) or []:
        kws = [str(x).strip() for x in item.get("keywords", []) or [] if str(x).strip()]
        ex = [str(x).strip().lower() for x in item.get("exclude_keywords", []) or [] if str(x).strip()]
        project = str(item.get("project", "")).strip()
        if project and kws:
            out.append(SearchTarget(project=project, area=str(item.get("area", "") or ""), keywords=kws[:6], exclude_keywords=ex[:8]))
    return out[:6] or fallback_search_targets(criteria, projects)


def fallback_search_targets(criteria: SearchCriteria, projects: ProjectsResult) -> list[SearchTarget]:
    """Keyword fallback khi AI timeout."""
    ptype = PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)
    area = projects.area_description
    out: list[SearchTarget] = []
    for p in projects.projects[:6]:
        name = str(p.get("name", "")).strip()
        if not name:
            continue
        kws = [
            f"{name} {ptype}",
            f"bán {ptype} {name}",
            f"{name} shophouse",
            f"{name} nhà phố thương mại",
            f"{name} mặt bằng kinh doanh",
            f"{name} {area}",
        ]
        out.append(SearchTarget(project=name, area=area, keywords=kws, exclude_keywords=["tuyển dụng", "wiki", "tin tức"]))
    return out
