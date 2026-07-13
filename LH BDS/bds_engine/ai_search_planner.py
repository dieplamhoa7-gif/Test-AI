"""AI-assisted search planning for BĐS comparable listings."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import re

from ai_client import NineRouterClient
from scraper import PROPERTY_TYPE_LABELS, FEATURE_LABELS, MDSDD_LABELS, SearchCriteria, ProjectsResult



def _city_from_area(area: str) -> str:
    text = (area or '').lower()
    if 'hà nội' in text or 'ha noi' in text:
        return 'Hà Nội'
    if 'đà nẵng' in text or 'da nang' in text:
        return 'Đà Nẵng'
    return 'Hồ Chí Minh'

def _clean_project_name(name: str) -> str:
    name = re.sub(r'\s+', ' ', str(name or '')).strip(' ,-')
    # Remove trailing city/admin context so keyword can be exactly: project + city.
    patterns = [
        r'\s+(?:phường|phuong|xã|xa|quận|quan|huyện|huyen|thành phố|thanh pho|tp\.?|tỉnh|tinh)\b.*$',
        r'\s+(?:hồ chí minh|ho chi minh|hà nội|ha noi|đà nẵng|da nang)\s*$',
    ]
    for pat in patterns:
        name = re.sub(pat, '', name, flags=re.I).strip(' ,-')
    return name or str(name or '').strip()

def _dedupe_city_keyword(project: str, city: str) -> str:
    project = _clean_project_name(project)
    c = str(city or '').strip()
    low = project.lower()
    if c and c.lower() in low:
        return project
    # Avoid repeated HCMC variants.
    if re.search(r'(hồ chí minh|ho chi minh|tp\.?\s*hcm|tphcm)', low, re.I):
        return project
    return f'{project} {c}'.strip()

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
        "Bắt buộc ưu tiên keyword dạng: tên dự án sạch + thành phố. "
        "Không bịa giá/link. Chỉ lập kế hoạch search. Trả JSON hợp lệ."
    )
    user = f"""Tiêu chí định giá:
- Tọa độ: {criteria.lat}, {criteria.lng}
- Loại tài sản: {PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)}
- MĐSDĐ: {MDSDD_LABELS.get(criteria.mdsdd, criteria.mdsdd) if criteria.mdsdd else 'không yêu cầu'}
- Đặc tính: {FEATURE_LABELS.get(criteria.feature, criteria.feature) if criteria.feature else 'không yêu cầu'}
- Khu vực: {projects.area_description}
- Dự án/khu vực comparable: {project_names}

Tạo keywords để tìm tin rao thật. Quy tắc bắt buộc:
- AI đã chọn 5 dự án/khu vực comparable trước; keyword search Playwright trên Batdongsan phải ưu tiên "Tên dự án + thành phố".
- Tên dự án phải sạch, không kèm lại phường/quận/thành phố nếu đã có field area.
- Không tạo keyword bị lặp thành phố, ví dụ cấm "Phường Phú Thuận Thành phố Hồ Chí Minh Thành phố Hồ Chí Minh".
- Mỗi target 2-4 keyword là đủ; keyword đầu tiên phải là "Tên dự án + thành phố".

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
        ex = [str(x).strip().lower() for x in item.get("exclude_keywords", []) or [] if str(x).strip()]
        project = _clean_project_name(str(item.get("project", "")).strip())
        area = str(item.get("area", "") or projects.area_description or "")
        city = _city_from_area(area)
        raw_kws = [str(x).strip() for x in item.get("keywords", []) or [] if str(x).strip()]
        kws = [_dedupe_city_keyword(project, city)]
        for kw in raw_kws:
            ck = _dedupe_city_keyword(kw, city)
            if ck.lower() not in {x.lower() for x in kws}:
                kws.append(ck)
        if project and kws:
            out.append(SearchTarget(project=project, area=area, keywords=kws[:4], exclude_keywords=ex[:8]))
    return out[:6] or fallback_search_targets(criteria, projects)


def fallback_search_targets(criteria: SearchCriteria, projects: ProjectsResult) -> list[SearchTarget]:
    """Keyword fallback khi AI timeout."""
    ptype = PROPERTY_TYPE_LABELS.get(criteria.property_type, criteria.property_type)
    area = projects.area_description
    city = _city_from_area(area)
    out: list[SearchTarget] = []
    for p in projects.projects[:5]:
        name = _clean_project_name(str(p.get("name", "")).strip())
        if not name:
            continue
        kws = [
            _dedupe_city_keyword(name, city),
            f"bán {ptype} {name}",
            f"{name} {ptype}",
        ]
        # Preserve order while deduping.
        dedup=[]
        for kw in kws:
            ck=_dedupe_city_keyword(kw, city)
            if ck.lower() not in {x.lower() for x in dedup}:
                dedup.append(ck)
        out.append(SearchTarget(project=name, area=area, keywords=dedup[:4], exclude_keywords=["tuyển dụng", "wiki", "tin tức"]))
    return out
