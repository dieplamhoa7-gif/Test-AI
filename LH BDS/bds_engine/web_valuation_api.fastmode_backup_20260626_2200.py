from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from typing import Any

try:
    from ftfy import fix_text as _ftfy_fix_text
except Exception:
    _ftfy_fix_text = None


def fix_vn_text(x):
    if not isinstance(x, str):
        return x
    # Keep already-good Vietnamese intact; repair common mojibake forms from
    # browser/geocoder/search results. Some old literals in this file are already
    # lossy (contain U+FFFD), so we also apply conservative domain replacements.
    try:
        x = x.encode('utf-8', 'replace').decode('utf-8', 'replace')
    except Exception:
        pass
    if _ftfy_fix_text:
        try:
            x = _ftfy_fix_text(x)
        except Exception:
            pass
    _domain = {
        'Ph����?ng': 'Phường', 'ph����?ng': 'phường', 'Ph���?ng': 'Phường', 'ph���?ng': 'phường',
        'Ph����': 'Phường', 'ph����': 'phường', 'Ph��?ng': 'Phường', 'ph��?ng': 'phường',
        'SA�i GA�n': 'Sài Gòn', 'SA�i': 'Sài', 'GA�n': 'Gòn',
        'ThA�nh ph��?': 'Thành phố', 'ThA�nh ph��`': 'Thành phố', 'ThA�nh ph��': 'Thành phố', 'ThA�nh': 'Thành',
        'Th�� �?��cc': 'Thủ Đức', 'Th�� �?��c': 'Thủ Đức', 'Th��': 'Thủ', '�?��cc': 'Đức', '�?��c': 'Đức',
        'H��? ChA- Minh': 'Hồ Chí Minh', 'ChA- Minh': 'Chí Minh',
        'LA� T��� Tr��?ng': 'Lý Tự Trọng', 'LA� T��� Tr��ng': 'Lý Tự Trọng',
        '�?ang': 'Đang', '�3 �?ang': 'Đang', '�?A�y': 'Đây', 'L��u A�': 'Lưu ý',
        'd???': '', '�??': '-', 'mA�': 'm²', 't���': 'tỷ', 'tri��?u': 'triệu', 'GiA�': 'Giá', 'giA�': 'giá',
        'bA�n': 'bán', 'BA�n': 'Bán', 'nhA�': 'nhà', 'NhA�': 'Nhà', '�?���t': 'đất', '�`���t': 'đất',
        'm���t ti��?n': 'mặt tiền', 'tr���c ti���p': 'trực tiếp', 'ki��?m ch��cng': 'kiểm chứng',
        'ngu��?n th��-t': 'nguồn thật', 'th��-t': 'thật', 'tA�n': 'tên', '�`����?ng': 'đường',
    }
    for _a, _b in _domain.items():
        x = x.replace(_a, _b)
    # Sau ftfy: vai tu Viet con sot "khoang trang gia" (à/ị... + space) hoac chua ghep dau.
    # Pho bien nhat: "Thà nh pho" phai la "Thành pho" (xuat hien o moi dia chi -> loi mojibake nang).
    _post_ftfy = {
        # tone/vowel families con sot sau ftfy (UTF-8 doc nham latin1)
        'á»±': 'ự', 'á»§': 'ủ', 'á»©': 'ứ', 'á»™': 'ộ', 'á»•': 'ổ', 'á»—': 'ỗ',
        'á» ': 'ở', 'á»Ÿ': 'ở', 'á»›': 'ớ', 'á»£': 'ợ', 'á»­': 'ử', 'á»¯': 'ữ',
        'á»‰': 'ỉ', 'á»‹': 'ị', 'á»…': 'ễ', 'á»ƒ': 'ể', 'á»‡': 'ệ', 'á»“': 'ồ',
        'á»‘': 'ố', 'á»•': 'ổ', 'á»?': 'ọ',
        'á»': 'ờ', 'á»': 'ở', 'á»': 'ớ', 'á»': 'ố', 'á»': 'ồ', 'á»§': 'ủ',
        'áº£': 'ả', 'áº¥': 'ấ', 'áº§': 'ầ', 'áº©': 'ẩ', 'áº«': 'ẫ', 'áº­': 'ậ',
        'áº¯': 'ắ', 'áº±': 'ằ', 'áº³': 'ẳ', 'áºµ': 'ẵ', 'áº·': 'ặ', 'áº¡': 'ạ',
        'áº¿': 'ế', 'áº½': 'ẽ', 'áº»': 'ẻ', 'áº¹': 'ẹ',
        'Æ°': 'ư', 'Æ¡': 'ơ', 'Ä‘': 'đ', 'Ä‘': 'đ',
        'Ãª': 'ê', 'Ã´': 'ô', 'Ã¢': 'â', 'Ã ': 'à', 'Ã¡': 'á', 'Ã­': 'í',
        'Ã³': 'ó', 'Ã²': 'ò', 'Ãº': 'ú', 'Ã¹': 'ù', 'Ã½': 'ý', 'Ã©': 'é', 'Ã¨': 'è',
        'CÄ': 'Că', 'cÄ': 'că', 'há»™': 'hộ', 'Há»™': 'Hộ',
        # tu pho bien bi chen khoang trang gia sau ftfy
        'Thà nh': 'Thành', 'thà nh': 'thành',
        'Thà nh phố': 'Thành phố', 'thà nh phố': 'thành phố',
        'Nhà  ': 'Nhà ', 'nhà  ': 'nhà ',
    }
    for _a, _b in _post_ftfy.items():
        x = x.replace(_a, _b)
    bad = chr(0xFFFD)
    replacements = {
        'ThÃ nh': 'Thành', 'thÃ nh': 'thành', 'phá»‘': 'phố', 'Há»“': 'Hồ', 'ChÃ­': 'Chí',
        'Phưá»?ng': 'Phường', 'phưá»?ng': 'phường', 'PhÆ°á»?ng': 'Phường', 'phÆ°á»?ng': 'phường',
        'Ngá»?c': 'Ngọc', 'ngá»?c': 'ngọc', 'CÆ°': 'Cư', 'cÆ°': 'cư', 'Ä?': 'Đ', 'Ä‘': 'đ',
        'á»?': 'ọ', 'á»“': 'ồ', 'á»‘': 'ố', 'á»‹': 'ị', 'á»‡': 'ệ', 'áº¿': 'ế', 'áº§': 'ầ', 'áº¡': 'ạ',
        'Ã¡': 'á', 'Ã ': 'à', 'Ã¢': 'â', 'Ã£': 'ã', 'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã­': 'í',
        'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ãº': 'ú', 'Ã¹': 'ù', 'Ã½': 'ý',
        'T?o': 'Tạo', 'D? li?u': 'Dữ liệu', 'd? li?u': 'dữ liệu', 'B?o': 'Báo', 'b?o': 'báo',
        'Phu?ng': 'Phường', 'phu?ng': 'phường', 'Qu?n': 'Quận', 'qu?n': 'quận', 'Huy?n': 'Huyện', 'huy?n': 'huyện',
        'Th?nh ph?': 'Thành phố', 'th?nh ph?': 'thành phố', 'gi?': 'giá', 'Gi?': 'Giá',
        'd? án': 'dự án', 'd? ?n': 'dự án', 'v? tr?': 'vị trí', 'ti?n ?ch': 'tiện ích',
        'h? t?ng': 'hạ tầng', 'ph?n tích': 'phân tích', 'ki?m ch?ng': 'kiểm chứng',
        'ngu?n': 'nguồn', 'd? xu?t': 'đề xuất', 'trung b?nh': 'trung bình', 'da g?m VAT': 'đã gồm VAT',
    }
    for a, b in replacements.items():
        x = x.replace(a, b)
    bad_replacements = {
        'Phư' + bad + 'ng': 'Phường', 'phư' + bad + 'ng': 'phường',
        'Qu' + bad + 'n': 'Quận', 'qu' + bad + 'n': 'quận',
        'Huy' + bad + 'n': 'Huyện', 'huy' + bad + 'n': 'huyện',
        'Th' + bad + 'nh phố': 'Thành phố', 'th' + bad + 'nh phố': 'thành phố',
        'Đ' + bad + 'ng': 'Đông', 'đ' + bad + 'ng': 'đông',
        'T' + bad + 'y': 'Tây', 't' + bad + 'y': 'tây',
        'B' + bad + 'o': 'Báo', 'b' + bad + 'o': 'báo', 'c' + bad + 'o': 'cáo',
        'gi' + bad: 'giá', 'Gi' + bad: 'Giá',
        'dữ li' + bad + 'u': 'dữ liệu', 'd' + bad + ' liệu': 'dữ liệu',
        'd' + bad + ' án': 'dự án', 'D' + bad + ' án': 'Dự án', 'dự ' + bad + 'n': 'dự án',
        'vị tr' + bad: 'vị trí', 'tiện ' + bad + 'ch': 'tiện ích', 'hạ t' + bad + 'ng': 'hạ tầng',
        'ph' + bad + 'n tích': 'phân tích', 'kiểm ch' + bad + 'ng': 'kiểm chứng',
        'ngu' + bad + 'n': 'nguồn', 'đề xu' + bad + 't': 'đề xuất',
        'trung b' + bad + 'nh': 'trung bình', 'đã g' + bad + 'm VAT': 'đã gồm VAT', 'so s' + bad + 'nh': 'so sánh',
    }
    for a, b in bad_replacements.items():
        x = x.replace(a, b)
    return x

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Ensure .env is loaded from this bot folder, not from caller cwd.
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BOT_DIR)
if BOT_DIR not in sys.path:
    sys.path.insert(0, BOT_DIR)
LOG_DIR = os.path.join(BOT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
JOB_ID = os.environ.get('BDS_JOB_ID', '')




def clean_for_json(obj):
    if isinstance(obj, str):
        return fix_vn_text(obj)
    if isinstance(obj, list):
        return [clean_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {clean_for_json(k): clean_for_json(v) for k, v in obj.items()}
    return obj


def extract_suggested_price_from_text(text: str) -> str:
    import re
    text = fix_vn_text(text or '')
    lines = [ln.strip() for ln in text.splitlines() if re.search(r'giá|triệu|tr/m|m²|m2', ln, re.I)]
    preferred = [ln for ln in lines if re.search(r'đề xuất|cơ sở|trung bình|bán ra|bàn giao', ln, re.I)]
    for ln in preferred + lines:
        m = re.search(r'\d+(?:[,.]\d+)?\s*(?:-|–|đến)?\s*\d*(?:[,.]\d+)?\s*(?:triệu|tr|tỷ|ty)\s*(?:/\s*m²|/m2|/m²)?', ln, re.I)
        if m:
            return fix_vn_text(m.group(0))
    return ''


def _now():
    return datetime.now().isoformat(timespec='seconds')


def write_progress(stage: str, message: str, warnings: list[str] | None = None):
    if not JOB_ID:
        return
    stage_messages = {
        'init': 'Đang nhận yêu cầu R&D và khởi tạo backend...',
        'resolve_location': 'Đang xác định vị trí/khu vực nghiên cứu...',
        'direct_street_search': 'Đang xác định tuyến đường và khu vực...',
        'find_comparables': 'Đang tìm khu vực/tài sản so sánh...',
        'discover_links': 'Đang tìm nguồn dữ liệu thị trường thật...',
        'scrape_sources': 'Đang scrape Batdongsan/Guland/Alonhadat...',
        # browser_street_queries intentionally uses the detailed message passed by
        # browser_direct_land_buckets(), so the UI shows the exact prioritized
        # Batdongsan search keywords: street -> ward/district/city.
        'browser_street_search': 'Chrome đang tìm tin rao trực tiếp trên Batdongsan...',
        'browser_buckets': 'Playwright đang tìm tin theo khu vực/tài sản so sánh...',
        'ai_support': 'Đang tổng hợp giá tham chiếu khi nguồn dữ liệu chưa đủ...',
        'build_report': 'Đang tổng hợp báo cáo R&D...',
        'render_map': 'Đang dựng bản đồ kiểm chứng...',
        'done': 'Hoàn tất báo cáo R&D thị trường.',
    }
    clean_msg = stage_messages.get(stage) or fix_vn_text(message)
    data = {'ok': True, 'jobId': JOB_ID, 'time': _now(), 'stage': stage, 'message': clean_msg, 'warnings': [fix_vn_text(w) for w in (warnings or [])]}
    tmp = os.path.join(LOG_DIR, f'bds_job_{JOB_ID}.tmp')
    final = os.path.join(LOG_DIR, f'bds_job_{JOB_ID}.json')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, final)


def log_error(stage: str, payload: dict[str, Any], error: Exception | str, fallback: str = '', ai_support: str = ''):
    err = str(error)
    rec = {'time': _now(), 'jobId': JOB_ID, 'stage': stage, 'payload': payload, 'error': err, 'fallback_used': fallback, 'ai_support': ai_support, 'source': 'web-rd'}
    with open(os.path.join(LOG_DIR, 'bds_valuation_errors.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    fix = classify_auto_fix(stage, err)
    if fix:
        with open(os.path.join(LOG_DIR, 'bds_auto_fixes.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'time': _now(), 'jobId': JOB_ID, 'stage': stage, **fix}, ensure_ascii=False) + '\n')


def classify_auto_fix(stage: str, err: str) -> dict[str, str] | None:
    low = (err or '').lower()
    if 'opening in existing browser session' in low or 'profile is already in use' in low:
        return {'fix_type': 'chrome_profile_isolation', 'status': 'applied_in_proxy', 'detail': 'Use per-job BDS_CHROME_PROFILE / BDS_GMAPS_PROFILE to avoid Chrome profile lock.'}
    if 'target page, context or browser has been closed' in low:
        return {'fix_type': 'browser_closed_recovery', 'status': 'runtime_recovery', 'detail': 'Continue final result with fallback map snapshot or without map; keep valuation report.'}
    if 'timeout' in low:
        return {'fix_type': 'timeout_recovery', 'status': 'runtime_recovery', 'detail': 'Continue with available buckets/fallback links/AI estimate with clear label.'}
    if 'unicodeencodeerror' in low or 'charmap' in low:
        return {'fix_type': 'utf8_stdout', 'status': 'applied_in_helper', 'detail': 'Force stdout/stderr UTF-8 in web_valuation_api.py.'}
    return None


async def ai_support_agent(ai, stage: str, payload: dict[str, Any], error: Exception | str, fallback: str, context: str = '') -> str:
    """Small AI support agent for web R&D failures.

    It does not fabricate scraped prices. It classifies the failure, suggests a safe
    fallback, and writes a user-facing note for the warnings panel.
    """
    system = (
        "Bạn là AI support agent cho web R&D định giá BĐS. "
        "Khi một stage lỗi, hãy phân loại nguyên nhân, đề xuất fallback an toàn, "
        "và viết ghi chú ngắn cho người dùng. Không được bịa giá, không được nói đã scrape được nếu chưa scrape. "
        "Trả lời tối đa 3 gạch đầu dòng tiếng Việt."
    )
    user = json.dumps({
        'stage': stage,
        'payload': payload,
        'error': str(error),
        'fallback': fallback,
        'context': context[:2000],
    }, ensure_ascii=False)
    try:
        note = await asyncio.wait_for(ai.chat(system, user, temperature=0.1), timeout=45)
        return (note or '').strip()[:1200]
    except Exception as e:
        return f"AI support agent không phản hồi ({type(e).__name__}); dùng fallback: {fallback}"

from ai_client import NineRouterClient, make_role_client
from ai_search_planner import build_search_targets, fallback_search_targets
from browser_search import discover_real_source_links, discover_batdongsan_evidence_links, listings_from_search_hits, merge_listing_buckets
from browser_crawler import browser_price_buckets
from playwright_bds_scraper import browser_true_buckets_async, scrape_batdongsan_playwright
from search_fallback import fallback_source_links
from config import load_settings
from map_snapshot import build_map_snapshot
from valuation_map import render_valuation_map_png
from google_maps_geocoder import geocode_projects_google_maps, geocode_names_nominatim
from scraper import SearchCriteria, ProjectsResult, find_nearby_projects, scrape_all_sources, fallback_nearby_projects
from bot import (
    resolve_location_context,
    build_ai_estimate_buckets,
    build_project_price_report,
    build_valuation_points,
)


def _make_clients():
    settings = load_settings()
    ai = NineRouterClient(settings.nineouter_api_key, settings.nineouter_base_url, settings.nineouter_model, timeout=settings.ai_timeout)
    ai_fast = make_role_client(ai, settings.fast_api_key, settings.fast_base_url, settings.fast_model, timeout=settings.ai_fast_timeout)
    ai_bds = make_role_client(ai, settings.bds_api_key, settings.bds_base_url, settings.bds_model, timeout=settings.ai_timeout)
    ai_report = make_role_client(ai, settings.report_api_key, settings.report_base_url, settings.report_model, timeout=settings.ai_timeout)
    return ai, ai_fast, ai_bds, ai_report


def extract_road(ctx: dict[str, Any]) -> str:
    import re
    road = ctx.get('road') or ctx.get('street') or ctx.get('nearest_road') or ''
    if isinstance(road, dict):
        road = road.get('name') or ''
    if road:
        return str(road).strip()
    hint = ctx.get('search_hint') or ctx.get('address') or ctx.get('display_name') or ''
    # Extract common Vietnamese street phrase from AI/geocode text.
    m = re.search(r'(?:đường|duong|mặt tiền|mat tien)\s+([^,;|]+)', str(hint), re.I)
    if m:
        return m.group(1).strip()
    return ''


def _area_from_context(ctx: dict[str, Any], criteria: SearchCriteria) -> str:
    ward = ctx.get('ward') or ctx.get('suburb') or ctx.get('phuong') or ''
    district = ctx.get('district') or ctx.get('county') or ctx.get('city_district') or ctx.get('city') or ''
    city = ctx.get('city') or ctx.get('province') or 'TP Hồ Chí Minh'
    parts = [x for x in [ward, district, city] if x]
    return ', '.join(parts) or f"khu vực quanh {criteria.lat:.6f}, {criteria.lng:.6f}"


def direct_land_projects(criteria: SearchCriteria) -> ProjectsResult:
    ctx = getattr(criteria, 'location_context', {}) or {}
    area = _area_from_context(ctx, criteria)
    road = extract_road(ctx)
    ward = ctx.get('ward') or ctx.get('suburb') or ctx.get('phuong') or area
    feature = getattr(criteria, 'feature', None) or 'skip'
    if criteria.property_type == 'dat':
        base = 'Đất'
    elif criteria.property_type == 'nha':
        base = 'Nhà phố/nhà riêng'
    elif criteria.property_type == 'shophouse':
        base = 'Shophouse/mặt bằng'
    elif criteria.property_type == 'khoxuong':
        base = 'Kho xưởng'
    else:
        base = 'Nhà đất'
    prefix = f"{base} mặt tiền" if feature == 'mattien' else (f"{base} hẻm/ngõ" if feature == 'hem' else base)
    names = []
    district = ctx.get('district') or ctx.get('county') or ctx.get('city_district') or ctx.get('city') or ''
    city = ctx.get('city') or ctx.get('province') or 'TP Hồ Chí Minh'
    road_scope = ' '.join(x for x in [road, ward, district, city] if x)
    if road:
        names.append(f"{prefix} {road_scope}")
        names.append(f"Nhà đất mặt tiền {road_scope}")
    names.extend([
        f"{prefix} {ward}",
        f"Nhà đất {ward}",
        f"{base} {area}",
        f"Bất động sản {area}",
    ])
    projects = []
    seen = set()
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            'name': name,
            'developer': 'Khu vực đất/nhà đất riêng lẻ - không có CĐT',
            'scale': 'tin rao đất theo khu vực/tuyến đường',
            'operation_year': 'không áp dụng',
            'delivered': 'không áp dụng',
        })
        if len(projects) >= 5:
            break
    return ProjectsResult(area_description=area, projects=projects)


def fallback_rent_apartment_projects(criteria: SearchCriteria, reason: str = 'fallback') -> ProjectsResult:
    """Fallback for rent_chungcu must stay apartment-first, not road/ward-first."""
    ctx = getattr(criteria, 'location_context', {}) or {}
    area = _area_from_context(ctx, criteria)
    ward = ctx.get('ward') or ctx.get('suburb') or ctx.get('phuong') or ''
    district = ctx.get('district') or ctx.get('county') or ctx.get('city_district') or ''
    city = ctx.get('city') or ctx.get('province') or 'TP Hồ Chí Minh'
    scopes = []
    for scope in [ward, district, area, city]:
        scope = str(scope or '').strip()
        if scope and scope.lower() not in {x.lower() for x in scopes}:
            scopes.append(scope)
    names = []
    for scope in scopes:
        names.extend([
            f"Căn hộ chung cư cho thuê {scope}",
            f"Chung cư cho thuê {scope}",
            f"Apartment cho thuê {scope}",
        ])
    names.extend([
        f"Căn hộ dịch vụ/chung cư cho thuê quanh {criteria.lat:.6f}, {criteria.lng:.6f}",
        f"Thị trường căn hộ cho thuê {city}",
    ])
    projects, seen = [], set()
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            'name': name,
            'developer': 'Khu/cụm căn hộ cho thuê - cần kiểm chứng dự án cụ thể',
            'scale': 'tham chiếu thị trường thuê căn hộ/chung cư',
            'operation_year': 'không áp dụng',
            'delivered': 'đang khai thác/cho thuê',
            'fallback_reason': reason,
        })
        if len(projects) >= 5:
            break
    return ProjectsResult(area_description=area, projects=projects)


def _project_line(i: int, p: dict[str, Any]) -> str:
    name = p.get('name') or '?'
    developer = p.get('developer') or p.get('investor') or p.get('chu_dau_tu') or 'CĐT đang kiểm chứng'
    scale = p.get('scale') or p.get('quy_mo') or p.get('size') or 'quy mô đang kiểm chứng'
    year = p.get('operation_year') or p.get('handover_year') or p.get('year') or p.get('nam_van_hanh') or 'năm vận hành đang kiểm chứng'
    delivered = p.get('delivered') or p.get('handover_status') or p.get('ban_giao') or 'tình trạng bàn giao đang kiểm chứng'
    return f" {i + 1}. {name} - {developer} - {scale} - {year} - {delivered}"


def _fmt_num(x, nd=0):
    try:
        return f"{float(x):,.{nd}f}".replace(',', '.')
    except Exception:
        return str(x)


def _median(vals: list[float]) -> float | None:
    vals = sorted(float(v) for v in vals if v is not None)
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    return vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2


def _location_appraisal_notes(criteria: SearchCriteria, projects: ProjectsResult) -> list[str]:
    loc = getattr(criteria, 'location_context', {}) or {}
    area = (projects.area_description or getattr(criteria, 'human_summary', '') or '').strip()
    district = loc.get('district') if isinstance(loc, dict) else ''
    ward = loc.get('ward') or loc.get('suburb') if isinstance(loc, dict) else ''
    street = loc.get('street') or loc.get('road') if isinstance(loc, dict) else ''
    low = (area + ' ' + str(district) + ' ' + str(street)).lower()
    notes = []
    if 'quận 4' in low or 'quan 4' in low or 'xóm chiếu' in low or 'xom chieu' in low:
        notes.extend([
            'Vị trí thuộc lõi đô thị Quận 4, nằm giữa Quận 1, Quận 7 và khu Nam; ưu thế chính là khoảng cách rất gần CBD nhưng mặt bằng giá thường thấp hơn nhóm lõi Quận 1.',
            'Kết nối chính qua các trục Bến Vân Đồn, Nguyễn Tất Thành, Hoàng Diệu, Khánh Hội; tiếp cận Quận 1 qua cầu Calmette/Ông Lãnh/Kênh Tẻ và đi Quận 7 qua trục Nguyễn Tất Thành - cầu Tân Thuận.',
            'Hạ tầng khu vực đã hình thành, mật độ dân cư cao; lợi thế là tiện ích đô thị sẵn có, bất lợi là áp lực giao thông giờ cao điểm và quỹ đất mới hạn chế.',
            'Tiện ích xung quanh gồm hệ thống thương mại - dịch vụ dọc Bến Vân Đồn/Khánh Hội/Nguyễn Tất Thành, trường học, y tế, chợ/khu ăn uống, bán kính di chuyển ngắn tới trung tâm Quận 1.',
            'Nguồn cung cạnh tranh trực tiếp là các dự án đã bàn giao quanh Bến Vân Đồn, Tôn Thất Thuyết, Nguyễn Tất Thành; tính thanh khoản phụ thuộc mạnh vào pháp lý sổ, chất lượng quản lý vận hành, view sông và khả năng cho thuê.',
        ])
    else:
        notes.extend([
            f'Vị trí nghiên cứu: {area or "khu vực mục tiêu"}. Cần xem xét trong tương quan với trung tâm hành chính - thương mại gần nhất, trục giao thông chính và bán kính tiện ích 1-3 km.',
            'Kết nối được đánh giá theo khả năng tiếp cận đường chính, thời gian di chuyển tới CBD/khu việc làm, và mức độ ùn tắc tại các nút giao trọng yếu.',
            'Hạ tầng - tiện ích cần kiểm tra gồm trường học, y tế, thương mại, công viên, bãi xe, giao thông công cộng và các dự án hạ tầng đang/chuẩn bị triển khai.',
            'Nguồn cung cạnh tranh gồm các dự án cùng phân khúc, cùng giai đoạn bàn giao và cùng bán kính thị trường; ưu tiên so sánh dự án đã bàn giao, pháp lý rõ và có thanh khoản thật.',
        ])
    return [x for x in notes if x]


def build_appraisal_summary(criteria: SearchCriteria, projects: ProjectsResult, buckets: dict) -> tuple[str, dict[str, Any]]:
    """Deterministic appraisal section restored for web fast-mode.

    Uses real Batdongsan/browser samples already collected, so it is fast and
    does not add another AI call. This complements the raw R&D price table with
    a valuation-style conclusion like the older report.
    """
    is_rent_chungcu = (getattr(criteria, 'transaction', 'buy') == 'rent' and getattr(criteria, 'rent_subtype', '') == 'rent_chungcu')
    project_rows = []
    all_ppm: list[float] = []
    all_totals: list[float] = []
    for p in (projects.projects or [])[:5]:
        name = (p.get('name') or '').strip()
        listings = []
        for key, rows in (buckets or {}).items():
            k = str(key).lower()
            if name and (name.lower() in k or k.endswith('::' + name.lower())):
                listings.extend(rows or [])
        ppms = [float(getattr(x, 'price_per_m2', 0) or 0) for x in listings if getattr(x, 'price_per_m2', None)]
        totals = [float(getattr(x, 'price', 0) or 0) for x in listings if getattr(x, 'price', None)]
        if is_rent_chungcu and totals:
            med_total = _median(totals) or 0
            project_rows.append({'name': name, 'median': med_total, 'min': min(totals), 'max': max(totals), 'n': len(totals), 'developer': p.get('developer') or '', 'scale': p.get('scale') or ''})
            all_totals.extend(totals)
            all_ppm.extend(ppms)
        elif ppms:
            med = _median(ppms)
            project_rows.append({'name': name, 'median': med, 'min': min(ppms), 'max': max(ppms), 'n': len(ppms), 'developer': p.get('developer') or '', 'scale': p.get('scale') or ''})
            all_ppm.extend(ppms)
    value_samples = all_totals if is_rent_chungcu else all_ppm
    if not value_samples:
        return ('', {})
    market_med = _median(value_samples) or 0
    low = market_med * 0.95
    high = market_med * 1.05
    unit = 'triệu/căn/tháng' if is_rent_chungcu else 'triệu/m²'
    selected = sorted(project_rows, key=lambda r: (abs((r.get('median') or market_med) - market_med), -r.get('n', 0)))[0] if project_rows else {}
    lines = [
        '',
        '🏦 *Báo cáo thẩm định giá sơ bộ*',
        '',
        f'- Phương pháp: so sánh trực tiếp từ {len(project_rows)} dự án comparable, {len(value_samples)} mẫu giá rao có nguồn Batdongsan/Playwright.',
        f'- Mặt bằng giá thị trường: khoảng {_fmt_num(min(value_samples),1)}–{_fmt_num(max(value_samples),1)} {unit}; median {_fmt_num(market_med,1)} {unit}.',
        f'- Khoảng giá đề xuất thận trọng cho sản phẩm mục tiêu: {_fmt_num(low,1)}–{_fmt_num(high,1)} {unit}.',
    ]
    if selected:
        lines.append(f'- Comparable neo chính: {selected["name"]} (~{_fmt_num(selected["median"],1)} {unit}, {selected["n"]} mẫu), sau đó đối chiếu với các dự án còn lại theo vị trí/quy mô/bàn giao.')
    lines.extend(['', '*Bảng comparable dùng cho thẩm định:*'])
    for i, r in enumerate(sorted(project_rows, key=lambda x: x.get('median') or 0, reverse=True), 1):
        lines.append(f'{i}. {r["name"]}: median ~{_fmt_num(r["median"],1)} {unit} ({r["n"]} mẫu; biên {_fmt_num(r["min"],1)}–{_fmt_num(r["max"],1)}).')
    lines.extend(['', '*Phân tích vị trí - hạ tầng - tiện ích:*'])
    for note in _location_appraisal_notes(criteria, projects):
        lines.append(f'- {note}')
    lines.extend([
        '',
        '*Phân tích thị trường và khả năng thanh khoản:*',
        '- Nhóm comparable được chọn theo tiêu chí cùng khu vực/quận, cùng loại hình căn hộ, đã vận hành hoặc có thị trường thứ cấp đủ dữ liệu; loại bỏ mẫu không khớp dự án hoặc thiếu giá/diện tích.',
        '- Các dự án có nhiều mẫu rao, giá tập trung và đường link kiểm chứng rõ được ưu tiên làm neo giá; dự án ít mẫu chỉ dùng để đối chiếu xu hướng, không dùng làm neo chính.',
        '- Thanh khoản tốt khi dự án có pháp lý rõ, phí quản lý hợp lý, tỷ lệ lấp đầy cao, vị trí thuận tiện cho thuê/ở thật và chênh lệch giá không vượt quá nhóm cạnh tranh trực tiếp.',
        '',
        '*Kết luận sơ bộ:*',
        f'- Nếu sản phẩm mục tiêu có chất lượng/vị trí tương đương nhóm trung vị, có thể lấy mốc {_fmt_num(market_med,1)} {unit} làm giá tham chiếu.',
        '- Nếu tầng/view/pháp lý/nội thất tốt hơn nhóm mẫu, xem xét cộng biên 3–7%; nếu bất lợi hơn, trừ 3–10%.',
        '- Đây là báo cáo sơ bộ từ giá rao thị trường; trước khi chốt giá cần kiểm chứng giao dịch thực tế, pháp lý căn hộ và tình trạng bàn giao.',
    ])
    summary = {
        'selected_comparable': selected.get('name'),
        'reference_price': round(market_med, 1),
        'reference_price_label': f'~{_fmt_num(market_med,1)} {unit}',
        'suggested_price_range': f'{_fmt_num(low,1)}–{_fmt_num(high,1)} {unit}',
        'sample_count': len(value_samples),
        'comparable_count': len(project_rows),
    }
    return '\n'.join(lines), summary


async def browser_direct_land_buckets(criteria: SearchCriteria, projects: ProjectsResult) -> dict:
    loc = getattr(criteria, 'location_context', {}) or {}
    area = projects.area_description
    road = extract_road(loc)
    ward = loc.get('ward') or loc.get('suburb') or loc.get('phuong') or ''
    district = loc.get('district') or loc.get('county') or loc.get('city_district') or ''
    queries = []
    city = loc.get('city') or loc.get('province') or 'TP Hồ Chí Minh'
    city_l = fix_vn_text(str(city or '')).lower()
    province = loc.get('province') or loc.get('state') or ''
    province_l = fix_vn_text(str(province or '')).lower()
    if 'thủ đức' in city_l or 'thu duc' in city_l:
        if province and ('hồ chí minh' in province_l or 'ho chi minh' in province_l or 'hcm' in province_l):
            city = province
        else:
            city = 'TP Hồ Chí Minh'
    def scope(*parts):
        out = []
        seen = set()
        for p in parts:
            p = fix_vn_text(str(p or '').strip())
            if not p:
                continue
            key = p.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
        return ' '.join(out)
    mode = getattr(criteria, 'transaction', 'buy') or 'buy'
    is_rent = mode == 'rent'
    ptype = (getattr(criteria, 'property_type', '') or '').lower()
    rent_subtype = (getattr(criteria, 'rent_subtype', '') or '').lower()
    feature = (getattr(criteria, 'feature', '') or '').lower()
    feature_terms = []
    if feature == 'mattien':
        feature_terms = ['mặt tiền']
    elif feature == 'corner':
        feature_terms = ['góc', '2 mặt tiền']
    elif feature == 'hem':
        feature_terms = ['hẻm', 'ngõ']
    # For land/townhouse/shophouse/commercial space, prioritize exact street +
    # ward/district/city from the coordinate and include product/feature terms.
    if ptype == 'dat':
        sale_terms = ['bán đất', 'bán đất mặt tiền', 'bán đất nền']
        rent_terms = ['cho thuê đất', 'cho thuê mặt bằng']
    elif ptype == 'nha':
        sale_terms = ['bán nhà mặt tiền', 'bán nhà phố', 'bán nhà riêng']
        rent_terms = ['cho thuê nhà mặt tiền', 'cho thuê nhà phố', 'cho thuê nhà riêng']
    elif ptype == 'shophouse':
        sale_terms = ['bán shophouse', 'bán nhà phố thương mại', 'bán mặt bằng kinh doanh']
        if rent_subtype == 'rent_vanphong':
            rent_terms = ['cho thuê văn phòng', 'cho thuê sàn văn phòng', 'văn phòng cho thuê', 'cho thuê tòa nhà văn phòng']
        elif rent_subtype == 'rent_santhuongmai':
            rent_terms = ['cho thuê sàn thương mại', 'cho thuê mặt bằng thương mại', 'cho thuê mặt bằng kinh doanh', 'cho thuê retail space']
        else:
            rent_terms = ['cho thuê shophouse', 'cho thuê mặt bằng kinh doanh', 'cho thuê nhà phố thương mại']
    elif ptype == 'chungcu':
        sale_terms = ['bán căn hộ chung cư', 'bán chung cư', 'mua bán căn hộ']
        if rent_subtype == 'rent_chungcu':
            rent_terms = ['cho thuê căn hộ chung cư', 'cho thuê chung cư', 'thuê căn hộ']
        else:
            rent_terms = ['cho thuê căn hộ chung cư', 'cho thuê chung cư']
    else:
        sale_terms = ['bán nhà đất mặt tiền', 'bán đất mặt tiền']
        rent_terms = ['cho thuê nhà đất mặt tiền', 'cho thuê mặt bằng']
    terms = rent_terms if is_rent else sale_terms
    if feature_terms:
        enriched = []
        for term in terms:
            enriched.append(term)
            for ft in feature_terms:
                if ft not in term:
                    enriched.append(f"{term} {ft}")
        terms = enriched
    road_scope = scope(road, ward, district, city)
    ward_scope = scope(ward, district, city)
    district_scope = scope(district, city)
    if road_scope:
        queries += [f"{term} {road_scope}" for term in terms]
    if ward_scope:
        queries += [f"{term} {ward_scope}" for term in terms[:2]]
    if district_scope and not road_scope:
        queries += [f"{term} {district_scope}" for term in terms[:2]]
    # Last fallback is still location-based, not generic project comparable.
    if area:
        queries.append((terms[0] + ' ' + area).strip())
    # de-duplicate while preserving priority order
    seen_q = set(); queries = [q for q in queries if q and not (q.lower() in seen_q or seen_q.add(q.lower()))]
    buckets = {}
    write_progress('browser_street_queries', ('Chrome search cho thuê ưu tiên đường/phường/quận: ' if is_rent else 'Chrome search bán ưu tiên đường/phường/quận: ') + ' | '.join(queries[:5]))
    for q in queries[:5]:
        try:
            rows = await scrape_batdongsan_playwright(q, limit=8, headless=False, mode=mode)
            if rows:
                buckets.setdefault('Batdongsan.com.vn', []).extend(rows)
                # Search -> collect data immediately; stop once the first precise
                # street/ward keywords produce enough usable rows to avoid drifting
                # into broader/fallback keywords.
                if len(buckets.get('Batdongsan.com.vn', [])) >= 8:
                    break
        except Exception:
            continue
    return buckets


def _filter_buckets_by_transaction(buckets: dict, is_rent: bool) -> dict:
    """Final transaction guard: never mix sale evidence into rent (or vice versa)."""
    filtered = {}
    for bucket_name, listings in (buckets or {}).items():
        kept = []
        for listing in listings or []:
            url = str(getattr(listing, 'url', '') or '').lower()
            title = fix_vn_text(str(getattr(listing, 'title', '') or '')).lower()
            blob = f"{url} {title}"
            if is_rent:
                if '/ban-' in url or '/nha-dat-ban' in url or '/ban-nha-' in url:
                    continue
                if url and '/cho-thue-' not in url:
                    continue
                if not url and not any(x in blob for x in ('cho thuê', 'cho thue', '/tháng', '/thang')):
                    continue
            else:
                if '/cho-thue-' in url or any(x in blob for x in ('cho thuê', 'cho thue', '/tháng', '/thang')):
                    continue
                if url and not ('/ban-' in url or '/nha-dat-ban' in url or '/ban-nha-' in url):
                    continue
            kept.append(listing)
        if kept:
            filtered[bucket_name] = kept
    return filtered


def _rd_ascii_blob(text: str) -> str:
    import unicodedata
    raw = fix_vn_text(str(text or '')).lower()
    no = ''.join(c for c in unicodedata.normalize('NFD', raw) if unicodedata.category(c) != 'Mn')
    return (raw + ' ' + no).lower()


def _filter_buckets_by_rent_subtype(buckets: dict, rent_subtype: str = '') -> dict:
    """Keep rent evidence aligned to the selected rental product.

    In particular, commercial floor / office rental must not be polluted by
    apartment/chung-cu rental listings, because unit economics differ and the
    UI should show ngàn/m²/tháng for commercial rent.
    """
    subtype = (rent_subtype or '').lower()
    if subtype not in {'rent_santhuongmai', 'rent_vanphong'}:
        return buckets
    reject = ('căn hộ', 'can ho', 'can-ho', 'chung cư', 'chung cu', 'chung-cu', 'apartment', 'studio', 'phòng ngủ', 'phong ngu', '1pn', '2pn', '3pn')
    if subtype == 'rent_santhuongmai':
        accept = ('sàn thương mại', 'san thuong mai', 'san-thuong-mai', 'mặt bằng', 'mat bang', 'mat-bang', 'shophouse', 'shop house', 'nhà phố thương mại', 'nha pho thuong mai', 'kinh doanh', 'retail', 'cửa hàng', 'cua hang')
    else:
        accept = ('văn phòng', 'van phong', 'van-phong', 'office', 'mặt bằng văn phòng', 'mat bang van phong', 'sàn văn phòng', 'san van phong')
    filtered = {}
    for bucket_name, listings in (buckets or {}).items():
        kept = []
        for listing in listings or []:
            url = str(getattr(listing, 'url', '') or '').lower()
            title = str(getattr(listing, 'title', '') or '')
            source = str(getattr(listing, 'source', '') or '')
            blob = _rd_ascii_blob(f"{url} {title} {source}")
            if any(x in blob for x in reject):
                continue
            if any(x in blob for x in accept) or 'cho-thue-van-phong' in url or 'cho-thue-sang-nhuong' in url or 'cho-thue-cua-hang' in url:
                kept.append(listing)
        if kept:
            filtered[bucket_name] = kept
    return filtered


def _rent_ppm_to_ngan_label(value: float | int | None, decimals: int = 0) -> str:
    try:
        v = float(value)
    except Exception:
        return ''
    if v <= 0:
        return ''
    # Internal parser stores rent price_per_m2 in triệu/m²/month. User-facing
    # commercial rent unit must be ngàn/m²/tháng.
    return f"{_fmt_num(v * 1000, decimals)} ngàn/m²/tháng"


def build_direct_land_report(projects: ProjectsResult, buckets: dict, is_rent: bool = False) -> str:
    buckets = _filter_buckets_by_transaction(buckets, is_rent)
    buckets = _filter_buckets_by_rent_subtype(buckets, getattr(criteria, 'rent_subtype', '') if is_rent else '')
    all_items = []
    for bucket_name, listings in (buckets or {}).items():
        for l in listings or []:
            ppm = getattr(l, 'price_per_m2', None)
            total = getattr(l, 'price_total', None)
            url = getattr(l, 'url', '')
            title = getattr(l, 'title', '')
            source = getattr(l, 'source', '') or 'Nguồn web'
            low = f"{source} {title} {url}".lower()
            if 'ước lượng' in low or 'uoc luong' in low or 'ai estimate' in low:
                continue
            if ppm or total or url:
                all_items.append({'bucket': bucket_name, 'ppm': ppm, 'total': total, 'url': url, 'title': title, 'source': source})
    lines = ['📍 *Định giá trực tiếp theo mẫu tin khu vực/tên đường*', '']
    if not all_items:
        return '\n'.join(lines + [
            'Chưa lấy được mẫu tin trực tiếp đủ tin cậy từ Batdongsan/Guland/Alonhadat.',
            'Kết luận: chưa có data giá real trực tiếp để định giá; cần kiểm tra thủ công hoặc mở rộng bán kính/từ khóa.',
        ])
    ppms = [x['ppm'] for x in all_items if isinstance(x.get('ppm'), (int, float)) and x.get('ppm') > 0]
    totals = [x['total'] for x in all_items if isinstance(x.get('total'), (int, float)) and x.get('total') > 0]
    def med(vals):
        vals = sorted(vals)
        if not vals: return None
        n = len(vals)
        return vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2
    if ppms:
        lines.append(f"- Số mẫu có giá/m²: {len(ppms)}")
        lines.append(f"- Giá thuê/m² median: ~{_rent_ppm_to_ngan_label(med(ppms),0)}" if is_rent else f"- Giá/m² median: ~{_fmt_num(med(ppms),0)} tr/m²")
        lines.append(f"- Biên giá thuê/m²: {_rent_ppm_to_ngan_label(min(ppms),0)}–{_rent_ppm_to_ngan_label(max(ppms),0)}" if is_rent else f"- Biên giá/m²: {_fmt_num(min(ppms),0)}–{_fmt_num(max(ppms),0)} tr/m²")
    elif totals:
        lines.append(f"- Số mẫu có giá tổng: {len(totals)}")
        lines.append(f"- Giá tổng median: ~{_fmt_num(med(totals),1)} tỷ")
    lines.append('')
    lines.append('*Mẫu tin/link kiểm chứng:*')
    for i, x in enumerate(all_items[:12], 1):
        desc = []
        if x.get('ppm'): desc.append(f"~{_rent_ppm_to_ngan_label(x['ppm'],0)}" if is_rent else f"~{_fmt_num(x['ppm'],0)} tr/m²")
        if x.get('total'): desc.append(f"~{_fmt_num(x['total'],1)} tỷ")
        suffix = (' — ' + ', '.join(desc)) if desc else ''
        lines.append(f" {i}) {x.get('source')}{suffix}")
        if x.get('title'):
            lines.append(f"    {x['title'][:180]}")
        if x.get('url'):
            lines.append(f"    {x['url']}")
    lines.append('')
    lines.append('Lưu ý: đây là mẫu tin rao trực tiếp theo tên đường/khu vực; cần kiểm chứng pháp lý, diện tích, mặt tiền/hẻm và trạng thái tin trước khi ra quyết định.')
    return '\n'.join(lines)


def clean_market_title(x: str) -> str:
    x = fix_vn_text(str(x or '')).strip()
    for token in ['[ước lượng Batdongsan.com.vn]', '[Ước lượng Batdongsan.com.vn]', '[ước lượng]', '[Ước lượng]', '[uoc luong Batdongsan.com.vn]', '[uoc luong]']:
        x = x.replace(token, '')
    return ' '.join(x.split(' - ')).strip(' -')[:220]


def is_estimated_listing(bucket_name: str, listing: Any) -> bool:
    url = getattr(listing, 'url', '') or ''
    title = fix_vn_text(getattr(listing, 'title', '') or '')
    source = fix_vn_text(getattr(listing, 'source', '') or '')
    blob = f"{bucket_name} {title} {source}".lower()
    return (not url) or ('ước lượng' in blob) or ('uoc luong' in blob) or ('ai estimate' in blob)


def summarize_price_samples(buckets: dict, limit: int = 20, require_url: bool = True) -> list[dict[str, Any]]:
    out = []
    seen = set()
    for bucket_name, listings in (buckets or {}).items():
        for l in listings or []:
            if require_url and is_estimated_listing(bucket_name, l):
                continue
            url = getattr(l, 'url', '') or ''
            title = clean_market_title(getattr(l, 'title', '') or '')
            key = url or title
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'bucket': clean_market_title(bucket_name),
                'title': title[:220],
                'source': clean_market_title(getattr(l, 'source', '') or ''),
                'price_total': getattr(l, 'price_total', None),
                'area_m2': getattr(l, 'area_m2', None),
                'price_per_m2': getattr(l, 'price_per_m2', None),
                'url': url,
            })
            if len(out) >= limit:
                return out
    return out



def direct_market_structured_fields(buckets: dict, is_rent: bool = False) -> dict[str, Any]:
    samples = summarize_price_samples(buckets, limit=20)
    ppms = [x.get('price_per_m2') for x in samples if isinstance(x.get('price_per_m2'), (int, float)) and x.get('price_per_m2') > 0]
    totals = [x.get('price_total') for x in samples if isinstance(x.get('price_total'), (int, float)) and x.get('price_total') > 0]
    def med(vals):
        vals = sorted(vals)
        if not vals:
            return None
        n = len(vals)
        return vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2
    median_ppm = med(ppms)
    investor = {}
    if median_ppm:
        if is_rent:
            investor['average_suggested_price'] = _rent_ppm_to_ngan_label(median_ppm,0)
            investor['suggested_price'] = investor['average_suggested_price']
            investor['reference_price_label'] = f"{_rent_ppm_to_ngan_label(median_ppm,0)} · {len(ppms)} mẫu Batdongsan"
        else:
            investor['average_suggested_price'] = f"{_fmt_num(median_ppm,0)} triệu/m²"
            investor['suggested_price'] = investor['average_suggested_price']
            investor['reference_price_label'] = f"{_fmt_num(median_ppm,0)} triệu/m² · {len(ppms)} mẫu Batdongsan"
        investor['confidence'] = 'Tạm đủ mẫu kiểm chứng' if len(ppms) >= 5 else 'Cần kiểm chứng thêm'
        investor['adjustment_bullets'] = [
            f"Đã đọc {len(samples)} mẫu tin trực tiếp từ nguồn web.",
            f"Có {len(ppms)} mẫu parse được giá/m².",
            (f"Biên giá thuê: {_rent_ppm_to_ngan_label(min(ppms),0)}–{_rent_ppm_to_ngan_label(max(ppms),0)}." if is_rent else f"Biên giá/m²: {_fmt_num(min(ppms),0)}–{_fmt_num(max(ppms),0)} triệu/m².") if ppms else '',
        ]
        investor['adjustment_bullets'] = [x for x in investor['adjustment_bullets'] if x]
        investor['price_rationale'] = 'Median từ mẫu giá trực tiếp; cần kiểm tra pháp lý, diện tích và vị trí trước khi chốt.'
    elif totals:
        if is_rent:
            investor['average_suggested_price'] = f"{_fmt_num(med(totals)*1000,1)} triệu/tài sản/tháng"
            investor['suggested_price'] = investor['average_suggested_price']
            investor['reference_price_label'] = f"{_fmt_num(med(totals)*1000,1)} triệu/tài sản/tháng · {len(totals)} mẫu có giá thuê tổng"
        else:
            investor['average_suggested_price'] = f"{_fmt_num(med(totals),1)} tỷ/tài sản"
            investor['suggested_price'] = investor['average_suggested_price']
            investor['reference_price_label'] = f"{_fmt_num(med(totals),1)} tỷ · {len(totals)} mẫu có giá tổng"
        investor['confidence'] = 'Cần kiểm chứng thêm'
    comps = []
    for idx, s in enumerate(samples[:5], 1):
        ppm = s.get('price_per_m2')
        total = s.get('price_total')
        label_parts = []
        if isinstance(ppm, (int, float)) and ppm > 0:
            label_parts.append(_rent_ppm_to_ngan_label(ppm,0) if is_rent else f"{_fmt_num(ppm,0)} triệu/m²")
        if isinstance(total, (int, float)) and total > 0:
            label_parts.append(f"{_fmt_num(total*1000,1)} triệu/tài sản/tháng" if is_rent else f"{_fmt_num(total,1)} tỷ")
        comps.append({
            'name': s.get('title') or f"Mẫu Batdongsan {idx}",
            'developer': s.get('source') or s.get('bucket') or 'Batdongsan.com.vn',
            'scale': s.get('url') or '',
            'confidence': 'Có link kiểm chứng' if s.get('url') else '',
            'ref_price_label': ' / '.join(label_parts) if label_parts else '',
            'ref_price_sample_count': 1,
            'ref_price_min': ppm,
            'ref_price_max': ppm,
            'ref_selection_rule': 'Mẫu tin trực tiếp theo keyword đường/phường/thành phố từ tọa độ.',
            'ref_evidences': [{
                'title': s.get('title') or '',
                'source': s.get('source') or s.get('bucket') or '',
                'price_per_m2': ppm,
                'reasons': ['mẫu trực tiếp'] + (['có link'] if s.get('url') else []),
                'url': s.get('url') or '',
            }],
        })
    return {
        'price_samples': samples,
        'price_sample_count': len(ppms),
        'sample_count': len(samples),
        'suggested_price_range': investor.get('reference_price_label') or '',
        'investor_summary': investor,
        'direct_comparables': comps,
    }


def market_summary_score(result: dict[str, Any]) -> dict[str, Any]:
    """Compute a simple 0-100 R&D summary score for UI display.

    This is not an investment recommendation; it is a data-quality/relevance score:
    higher means the report has more real samples, better direct evidence, and clearer
    comparable support.
    """
    sample_count = int(result.get('price_sample_count') or result.get('sample_count') or 0)
    comp_count = len(result.get('comparables') or [])
    confidence = str(result.get('confidence') or '').lower()
    score = 0
    reasons = []
    if sample_count >= 20:
        score += 45; reasons.append('nhiều mẫu giá thật')
    elif sample_count >= 10:
        score += 35; reasons.append('đủ mẫu giá tham chiếu')
    elif sample_count >= 5:
        score += 24; reasons.append('có một số mẫu giá')
    elif sample_count > 0:
        score += 12; reasons.append('mẫu giá còn mỏng')
    else:
        reasons.append('chưa parse được mẫu giá')
    if comp_count >= 5:
        score += 20; reasons.append('đủ comparable')
    elif comp_count >= 3:
        score += 14; reasons.append('có comparable hỗ trợ')
    elif comp_count > 0:
        score += 8; reasons.append('comparable còn ít')
    if 'cao' in confidence or 'high' in confidence:
        score += 20; reasons.append('độ tin cậy cao')
    elif 'trung' in confidence or 'medium' in confidence:
        score += 12; reasons.append('độ tin cậy trung bình')
    elif confidence:
        score += 6; reasons.append('có nhãn độ tin cậy')
    if result.get('map_png_base64') or result.get('map_url'):
        score += 5; reasons.append('có bản đồ kiểm chứng')
    if result.get('investor_summary'):
        score += 10; reasons.append('có tổng kết thẩm định')
    score = max(0, min(100, int(round(score))))
    if score >= 75:
        label = 'Tốt'
    elif score >= 50:
        label = 'Trung bình khá'
    elif score >= 30:
        label = 'Cần kiểm chứng thêm'
    else:
        label = 'Dữ liệu yếu'
    return {'score': score, 'label': label, 'reasons': reasons[:5]}


def rank_comparables_for_valuation(criteria: SearchCriteria, projects: ProjectsResult) -> list[dict[str, Any]]:
    """Rank comparable projects by relevance to the target coordinate for valuation."""
    loc = getattr(criteria, 'location_context', {}) or {}
    text_loc = ' '.join(str(loc.get(k) or '') for k in ['road', 'ward', 'suburb', 'district', 'city', 'address', 'display_name']).lower()
    view_hint = ' '.join(str(loc.get(k) or '') for k in ['view', 'river', 'waterfront', 'landmark', 'search_hint']).lower()
    ranked = []
    for idx, p in enumerate(projects.projects[:10]):
        score = 0.0
        reasons = []
        d = p.get('distance_km')
        if isinstance(d, (int, float)):
            if d <= 0.5:
                score += 35; reasons.append('rất gần tọa độ')
            elif d <= 1.0:
                score += 28; reasons.append('gần tọa độ')
            elif d <= 2.5:
                score += 18; reasons.append('cùng vùng so sánh')
            elif d <= 5.0:
                score += 8; reasons.append('cùng khu vực mở rộng')
            else:
                score -= 5; reasons.append('xa hơn vùng lõi')
        else:
            score += max(0, 18 - idx * 3); reasons.append('chưa có khoảng cách, xếp theo thứ tự tìm được')
        blob = ' '.join(str(p.get(k) or '') for k in ['name', 'type_hint', 'note', 'scale', 'developer']).lower()
        for kw, pts, label in [
            ('sông', 10, 'có yếu tố/khả năng hưởng view sông'), ('river', 10, 'có yếu tố/khả năng hưởng view sông'),
            ('đào trí', 7, 'gần trục Đào Trí/ven sông'), ('huỳnh tấn phát', 7, 'gần trục Huỳnh Tấn Phát'),
            ('nguyễn văn linh', 6, 'kết nối Nguyễn Văn Linh'), ('phú mỹ hưng', 6, 'hưởng hệ tiện ích khu Nam'),
            ('phú thuận', 5, 'cùng khu Phú Thuận'), ('quận 7', 4, 'cùng thị trường Quận 7'),
            ('bàn giao', 4, 'sản phẩm đã bàn giao/kiểm chứng vận hành'), ('cao cấp', 3, 'cùng/tiệm cận phân khúc cao hơn'),
        ]:
            if kw in blob or kw in text_loc or kw in view_hint:
                score += pts; reasons.append(label)
        p2 = dict(p)
        p2['valuation_score'] = round(score, 1)
        p2['valuation_reasons'] = list(dict.fromkeys(reasons))[:5]
        ranked.append(p2)
    ranked.sort(key=lambda x: x.get('valuation_score', 0), reverse=True)
    return ranked[:5]


async def ai_new_handover_sale_assessment(ai, criteria: SearchCriteria, projects: ProjectsResult, buckets: dict) -> str:
    samples = summarize_price_samples(buckets, limit=24)
    if not samples:
        return ''
    ranked = rank_comparables_for_valuation(criteria, projects)
    system = (
        'Bạn là chuyên gia thẩm định giá bất động sản 20 năm kinh nghiệm, chuyên định giá căn hộ cho chủ đầu tư. '
        'Hãy định giá theo phương pháp so sánh thị trường và điều chỉnh chuyên môn. '
        'Bắt buộc chọn dự án/khu vực so sánh phù hợp nhất với tọa độ mục tiêu dựa trên: khoảng cách, vị trí, tiện ích lân cận, hạ tầng khu vực, kết nối giao thông, view sông/thành phố, chất lượng sản phẩm, thương hiệu/chủ đầu tư, pháp lý/bàn giao và thanh khoản. '
        'Chỉ dùng các mẫu giá/listing và comparable được cung cấp; không bịa nguồn. '
        'Trình bày tiếng Việt cho chủ đầu tư, nêu rõ khoảng giá thấp - trung bình đề xuất - cao, giá đề xuất, và vì sao điều chỉnh tăng/giảm so với comparable gần nhất. '
        'Quy tắc VAT/bàn giao bắt buộc: tất cả giá bán đề xuất phải là giá đã gồm VAT. Nếu comparable chính hoặc mẫu giá là dự án đã bàn giao thì KHÔNG nhân thêm 1.1; nếu comparable/mẫu giá chưa bàn giao hoặc giá chưa VAT thì mới quy đổi nhân 1.1 để ra giá gồm VAT. Luôn ghi rõ "đã gồm VAT" trong kết luận giá. '
        'Nếu dữ liệu chưa đủ, vẫn đưa khung định giá thận trọng dựa trên mẫu thật đã có và ghi rõ độ tin cậy.'
    )
    user = json.dumps(clean_for_json({
        'asset_type': criteria.property_type,
        'segment': getattr(criteria, 'segment', None),
        'target_location': getattr(criteria, 'location_context', {}) or {},
        'area_description': projects.area_description,
        'ranked_comparables_for_valuation': ranked,
        'market_samples': samples,
        'valuation_task': (
            'Chọn comparable gần nhất về vị trí/tiện ích/hạ tầng/kết nối/view sông hoặc thành phố; '
            'điều chỉnh theo chuyên môn thẩm định giá 20 năm; đề xuất giá bán/m² cho sản phẩm căn hộ bàn giao mới tại tọa độ mục tiêu.'
        ),
        'required_output': [
            'Comparable chính được chọn và lý do',
            'Tình trạng bàn giao của comparable chính và quy tắc VAT áp dụng: đã bàn giao thì không nhân 1.1; chưa bàn giao/chưa VAT thì nhân 1.1',
            'Các điều chỉnh: vị trí, tiện ích, hạ tầng, giao thông, view, chất lượng, thương hiệu, pháp lý/bàn giao, thanh khoản',
            'Khoảng giá thấp - trung bình đề xuất - cao, tất cả đã gồm VAT',
            'Giá bán đề xuất/m² đã gồm VAT và ghi chú độ tin cậy'
        ]
    }), ensure_ascii=False)
    try:
        txt = await ai.chat(system, user, temperature=0.12)
    except Exception as e:
        return f'\n\n## Phân tích bán ra khi bàn giao mới\nChưa tạo được phần phân tích AI do lỗi {type(e).__name__}. Cần kiểm tra thủ công từ mẫu giá đã thu thập.'
    return '\n\n## Phân tích bán ra khi bàn giao mới\n' + txt.strip()


async def ai_investor_summary(ai, criteria: SearchCriteria, projects: ProjectsResult, buckets: dict, sale_text: str) -> dict[str, Any]:
    samples = summarize_price_samples(buckets, limit=18)
    loc = getattr(criteria, 'location_context', {}) or {}
    ranked = rank_comparables_for_valuation(criteria, projects)
    system = (
        'Bạn là chuyên gia thẩm định giá bất động sản 20 năm kinh nghiệm, viết tóm tắt cho chủ đầu tư. '
        'Không nói về bot/scrape/job. Không bịa nguồn. '
        'Phải chọn comparable chính gần nhất/tương đồng nhất với tọa độ theo: vị trí, tiện ích, hạ tầng, kết nối giao thông, view sông/thành phố, chất lượng, thương hiệu, pháp lý/bàn giao, thanh khoản. '
        'Trả JSON hợp lệ gồm: location_bullets, selected_comparable, adjustment_bullets, average_suggested_price, suggested_price, price_rationale, confidence. '
        'location_bullets: 4-6 bullet phân tích vị trí/tiện ích/hạ tầng/giao thông/view. '
        'adjustment_bullets: 3-6 bullet giải thích điều chỉnh tăng/giảm so với comparable chính. '
        'average_suggested_price: một giá trung bình đề xuất duy nhất, đơn vị triệu/m², đã gồm VAT. suggested_price phải dùng đúng giá trung bình này, không đưa thêm số khác làm lệch nhau; có thể ghi kèm biên kiểm chứng trong price_rationale. '
        'Quy tắc VAT/bàn giao bắt buộc: dự án tham chiếu đã bàn giao thì không nhân 1.1; dự án chưa bàn giao hoặc giá chưa VAT thì nhân 1.1 để quy đổi sang giá gồm VAT.'
    )
    user_payload = clean_for_json({
        'location_context': loc,
        'area_description': projects.area_description,
        'ranked_comparables_for_valuation': ranked,
        'market_samples': samples,
        'sale_assessment_text': sale_text,
        'task': 'Tóm tắt thẩm định giá căn hộ cho chủ đầu tư, chọn comparable phù hợp nhất và đề xuất giá bán/m².'
    })
    user = json.dumps(user_payload, ensure_ascii=False)
    try:
        data = await ai.chat_json(system, user, temperature=0.08)
        if not isinstance(data, dict):
            raise ValueError('not dict')
        bullets = data.get('location_bullets') or []
        if isinstance(bullets, str): bullets = [bullets]
        adj = data.get('adjustment_bullets') or []
        if isinstance(adj, str): adj = [adj]
        return {
            'location_bullets': [fix_vn_text(str(x).strip()) for x in bullets if str(x).strip()][:6],
            'selected_comparable': fix_vn_text(str(data.get('selected_comparable') or (ranked[0].get('name') if ranked else '')).strip()),
            'adjustment_bullets': [fix_vn_text(str(x).strip()) for x in adj if str(x).strip()][:6],
            'average_suggested_price': fix_vn_text(str(data.get('average_suggested_price') or data.get('suggested_price') or '').strip()),
            'suggested_price': fix_vn_text(str(data.get('average_suggested_price') or data.get('suggested_price') or '').strip()),
            'price_rationale': fix_vn_text(str(data.get('price_rationale') or '').strip()),
            'confidence': fix_vn_text(str(data.get('confidence') or '').strip()),
            'ranked_comparables': ranked,
        }
    except Exception as e:
        bullets = []
        parts = []
        for k in ['road', 'ward', 'suburb', 'district', 'city']:
            v = loc.get(k)
            if v and v not in parts:
                parts.append(str(v))
        if parts:
            bullets.append('Vị trí ghi nhận: ' + ', '.join(parts))
        pois = [x.get('name') for x in (loc.get('nearest_pois') or []) if isinstance(x, dict) and x.get('name')]
        if pois:
            bullets.append('Tiện ích/điểm nhận diện gần vị trí: ' + ', '.join(pois[:4]))
        chosen = ranked[0] if ranked else {}
        return {
            'location_bullets': [fix_vn_text(x) for x in (bullets or ['Chưa đủ dữ liệu vị trí để phân tích sâu; cần kiểm chứng thêm trên bản đồ và khảo sát thực địa.'])],
            'selected_comparable': fix_vn_text(chosen.get('name') or ''),
            'adjustment_bullets': [fix_vn_text(x) for x in (chosen.get('valuation_reasons') or [])],
            'average_suggested_price': extract_suggested_price_from_text(sale_text) or 'Xem phần phân tích chi tiết bên dưới',
            'suggested_price': extract_suggested_price_from_text(sale_text) or 'Xem phần phân tích chi tiết bên dưới',
            'price_rationale': f'AI summary lỗi {type(e).__name__}; dùng comparable gần nhất và dữ liệu báo cáo chi tiết để kiểm chứng.',
            'confidence': 'Cần kiểm chứng thêm',
            'ranked_comparables': ranked,
        }

def _name_tokens(s: str) -> set[str]:
    import re
    s = fix_vn_text(s or '').lower()
    toks = set(re.findall(r'[a-z0-9à-ỹđ]+', s))
    stop = {'can','ho','du','an','the','toa','block','quan','phuong','tp','hcm','thanh','pho','ho','chi','minh','complex','apartment'}
    return {t for t in toks if len(t) >= 2 and t not in stop}

def median_price_per_m2_for_name(name: str, buckets: dict) -> dict[str, Any]:
    vals = []
    name_l = fix_vn_text(name or '').lower()
    name_tokens = _name_tokens(name_l)
    for bucket_name, listings in (buckets or {}).items():
        bucket_l = fix_vn_text(str(bucket_name or '')).lower()
        bucket_tokens = _name_tokens(bucket_l)
        for l in listings or []:
            title = fix_vn_text(str(getattr(l, 'title', '') or '')).lower()
            ppm = getattr(l, 'price_per_m2', None)
            if not ppm:
                continue
            title_tokens = _name_tokens(title)
            overlap = len(name_tokens & (bucket_tokens | title_tokens))
            matched = (name_l and (name_l in bucket_l or name_l in title)) or (bucket_l and bucket_l in name_l) or overlap >= max(1, min(2, len(name_tokens)))
            if matched:
                try:
                    v = float(ppm)
                    if 5 <= v <= 300:
                        vals.append(v)
                except Exception:
                    pass
    if not vals:
        return {}
    vals.sort()
    n = len(vals)
    med = vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2
    med = round(med, 1)
    return {
        'reference_price': med,
        'reference_price_label': f"{med:g} triệu/m²",
        'ref_avg_price_per_m2': med,
        'ref_price_sample_count': n,
        'ref_price_min': round(min(vals), 1),
        'ref_price_max': round(max(vals), 1),
        'ref_price_label': f"{med:g} triệu/m²",
    }

def attach_ref_average_prices(projects: ProjectsResult, buckets: dict) -> None:
    for p in getattr(projects, 'projects', []) or []:
        got = median_price_per_m2_for_name(p.get('name') or '', buckets)
        if got:
            p.update(got)

def _dist_km(a_lat, a_lng, b_lat, b_lng):
    import math
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp = math.radians(b_lat - a_lat)
    dl = math.radians(b_lng - a_lng)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(x), math.sqrt(1 - x))


async def run_web_valuation(payload: dict[str, Any]) -> dict[str, Any]:
    write_progress('init', 'Đang nhận yêu cầu R&D và khởi tạo BDS_bot stack...')
    ai, ai_fast, ai_bds, ai_report = _make_clients()
    criteria = SearchCriteria(
        lat=float(payload['lat']),
        lng=float(payload.get('lng', payload.get('lon'))),
        property_type=payload.get('property_type') or payload.get('ptype') or 'chungcu',
        mdsdd=payload.get('mdsdd') or None,
        feature=payload.get('feature') or 'skip',
    )
    criteria.transaction = payload.get('transaction') or 'buy'
    criteria.segment = payload.get('segment') or None
    # Preserve explicit user/project keyword (e.g. "Lovera Vista") for comparable search.
    # Without this, coordinate-only reverse geocode can dominate and the AI/fallback
    # returns generic ward/road comparables even when the user typed a project name.
    criteria.human_summary = " | ".join(str(payload.get(k) or '').strip() for k in ('project_name', 'project', 'text', 'address', 'query') if str(payload.get(k) or '').strip())
    if criteria.transaction == 'rent':
        raw_ptype = (criteria.property_type or '').lower()
        # Normalize rental intent from the UI. Some forms send transaction=rent
        # with property_type=chungcu/canho/apartment instead of rent_chungcu.
        # Without this, downstream AI/search prompts may fall back to the generic
        # apartment sale flow and generate "mua/bán chung cư" keywords.
        if raw_ptype in {'rent_chungcu', 'chungcu', 'canho', 'can_ho', 'apartment'}:
            criteria.rent_subtype = 'rent_chungcu'
            criteria.property_type = 'chungcu'
        elif raw_ptype in {'rent_vanphong', 'vanphong', 'van_phong', 'office'}:
            criteria.rent_subtype = 'rent_vanphong'
            criteria.property_type = 'shophouse'
        elif raw_ptype in {'rent_santhuongmai', 'santhuongmai', 'san_thuong_mai', 'retail'}:
            criteria.rent_subtype = 'rent_santhuongmai'
            criteria.property_type = 'shophouse'
        elif raw_ptype in {'rent_nha', 'nha'}:
            criteria.rent_subtype = 'rent_nha'
            criteria.property_type = 'nha'
        else:
            criteria.rent_subtype = raw_ptype or 'rent_generic'
    # Apartments use project/comparable-first flow. Office lease keeps direct
    # street-search for rent prices, but also asks AI for 5 office/project
    # comparables so the report has a proper comparison set.
    rent_subtype = getattr(criteria, 'rent_subtype', None)
    use_comparable_flow = criteria.property_type == 'chungcu'
    needs_ai_comparables = (criteria.transaction == 'rent' and rent_subtype == 'rent_vanphong')
    rd_mode = str(payload.get('mode') or payload.get('rdMode') or 'standard').lower()
    is_fast_mode = rd_mode == 'fast'
    warnings: list[str] = []
    write_progress('resolve_location', 'Đang xác định khu vực/vị trí nghiên cứu...', warnings)
    if isinstance(payload.get('location_context'), dict) and payload.get('location_context'):
        criteria.location_context = payload['location_context']
    else:
        try:
            criteria.location_context = await resolve_location_context(ai_fast, criteria)
        except Exception as e:
            note = await ai_support_agent(ai_report, 'resolve_location', payload, e, 'continue without location_context')
            warnings.append(f'resolve_location_context lỗi: {type(e).__name__}. {note}')
            log_error('resolve_location', payload, e, 'continue without location_context', note)
            criteria.location_context = {}

    if not use_comparable_flow and not needs_ai_comparables:
        write_progress('direct_street_search', 'Sản phẩm direct-search: ưu tiên tìm/search thẳng theo tên đường...', warnings)
        projects = direct_land_projects(criteria)
    else:
        write_progress('find_comparables', 'Đang tìm 5 dự án/khu vực/văn phòng comparable bằng AI...', warnings)
        try:
            projects = await asyncio.wait_for(find_nearby_projects(ai_fast, criteria), timeout=45)
        except Exception as e:
            note = 'Fallback dự án/khu vực vì AI tìm comparable quá chậm/timeout.'
            warnings.append(f"find_nearby_projects lỗi/timeout, dùng fallback: {type(e).__name__}. {note}")
            log_error('find_comparables', payload, e, 'fallback_nearby_projects', note)
            if criteria.transaction == 'rent' and rent_subtype == 'rent_chungcu':
                projects = fallback_rent_apartment_projects(criteria, type(e).__name__)
            else:
                projects = fallback_nearby_projects(criteria, type(e).__name__)

    project_text = "\n".join(_project_line(i, p) for i, p in enumerate(projects.projects[:5])) or "  (AI không trả về dự án nào)"
    if not use_comparable_flow:
        intro = (
            f"Khu vực: {projects.area_description}\n\n"
            + (f"5 dự án/khu vực tham chiếu:\n{project_text}\n\n" if needs_ai_comparables else '')
            + "⏳ Đang tìm mẫu tin trực tiếp theo tên đường/phường/khu vực trên Batdongsan, Guland, Alonhadat…"
        )
    else:
        intro = (
            f"Khu vực: {projects.area_description}\n\n"
            f"5 dự án/khu vực tham chiếu:\n{project_text}\n\n"
            "⏳ Tiếp tục scrape Batdongsan, Guland, Alonhadat…"
        )

    project_names = [p.get('name', '') for p in projects.projects if p.get('name')]
    write_progress('discover_links', 'Đang search evidence Batdongsan/Guland/Alonhadat cho các dự án comparable...', warnings)
    try:
        search_targets = await asyncio.wait_for(build_search_targets(ai_fast, criteria, projects), timeout=(10 if is_fast_mode else 25))
    except Exception as e:
        search_targets = fallback_search_targets(criteria, projects)
        warnings.append(f'build_search_targets lỗi/timeout, dùng keyword fallback: {type(e).__name__}.')

    if use_comparable_flow:
        # Comparable apartment flow still needs evidence URLs. Run a lightweight Batdongsan
        # discovery layer instead of skipping evidence entirely, then merge coordinate fallback.
        try:
            evidence_buckets = await asyncio.wait_for(discover_batdongsan_evidence_links(search_targets, per_target_limit=(1 if is_fast_mode else 2)), timeout=(18 if is_fast_mode else 35))
        except Exception as e:
            warnings.append(f'Batdongsan evidence search lỗi/timeout, dùng fallback links: {type(e).__name__}.')
            log_error('discover_batdongsan_evidence', payload, e, 'fallback_source_links', 'Evidence search failed')
            evidence_buckets = {}
        evidence_buckets = merge_listing_buckets(evidence_buckets, fallback_source_links(project_names, criteria.lat, criteria.lng))
    else:
        try:
            source_hits = await asyncio.wait_for(discover_real_source_links(search_targets, per_source_limit=(2 if is_fast_mode else 4)), timeout=(18 if is_fast_mode else 45))
            evidence_buckets = listings_from_search_hits(source_hits)
        except Exception as e:
            note = 'Tự fallback nguồn search vì search link nguồn thật quá chậm/timeout.'
            warnings.append(f"discover links lỗi/timeout, dùng fallback links: {type(e).__name__}. {note}")
            log_error('discover_links', payload, e, 'fallback_source_links', note)
            evidence_buckets = fallback_source_links(project_names, criteria.lat, criteria.lng)
        if not any(evidence_buckets.values()):
            evidence_buckets = fallback_source_links(project_names, criteria.lat, criteria.lng)

    write_progress('scrape_sources', 'Đang scrape Batdongsan/Guland/Alonhadat...', warnings)
    if use_comparable_flow:
        note = 'Web fast-mode: bỏ qua scrape nguồn nặng cho flow comparable để tránh treo; dùng evidence/fallback + AI estimate có nhãn kiểm chứng.'
        warnings.append(note)
        buckets = {}
    else:
        try:
            buckets = await asyncio.wait_for(scrape_all_sources(ai_bds, criteria, projects, max_concurrent=1), timeout=(20 if is_fast_mode else 90))
        except Exception as e:
            note = 'Bỏ qua scrape nguồn vì quá chậm/timeout; tiếp tục bằng evidence/fallback buckets để web không treo.'
            warnings.append(f"scrape_all_sources lỗi/timeout: {type(e).__name__}. {note}")
            log_error('scrape_sources', payload, e, 'continue with evidence/browser buckets', note)
            buckets = {}
    buckets = merge_listing_buckets(buckets, evidence_buckets)

    has_price = any((getattr(l, 'price_total', None) or getattr(l, 'price_per_m2', None)) for listings in buckets.values() for l in listings)
    if not use_comparable_flow:
        write_progress('browser_street_search', 'Sản phẩm direct-search: Chrome đang search trực tiếp Batdongsan theo tên đường/phường...', warnings)
        if is_fast_mode and getattr(criteria, 'transaction', 'buy') != 'rent':
            warnings.append('Fast-mode: bỏ qua browser_direct_land_buckets nặng; dùng Google snippet/browser_price nhanh để tránh treo Playwright.')
        else:
            try:
                land_true = await asyncio.wait_for(browser_direct_land_buckets(criteria, projects), timeout=(120 if is_fast_mode else 220))
                buckets = merge_listing_buckets(buckets, land_true)
            except Exception as e:
                note = 'R&D cho thuê: Playwright nguồn cho thuê timeout/lỗi; tiếp tục bằng nguồn còn lại.' if (is_fast_mode and getattr(criteria, 'transaction', 'buy') == 'rent') else await ai_support_agent(ai_report, 'browser_direct_land', payload, e, 'try Google snippet browser price search')
                warnings.append(f"browser direct land lỗi/timeout: {type(e).__name__}. {note}")
                log_error('browser_direct_land', payload, e, 'try Google snippet browser price search', note)
        if getattr(criteria, 'transaction', 'buy') == 'rent':
            warnings.append('R&D cho thuê: bỏ qua Google/browser snippet để tránh lẫn mẫu Nhà đất bán; chỉ dùng nguồn/tab cho thuê.')
        else:
            try:
                land_browser = await asyncio.wait_for(browser_price_buckets(criteria, projects, max_projects=(3 if is_fast_mode else 5)), timeout=(35 if is_fast_mode else 120))
                buckets = merge_listing_buckets(buckets, land_browser)
            except Exception as e:
                note = 'Fast-mode bỏ qua AI support phụ sau lỗi browser search.' if is_fast_mode else await ai_support_agent(ai_report, 'browser_land_search', payload, e, 'continue with scraped/direct source buckets only')
                warnings.append(f"browser land search lỗi/timeout: {type(e).__name__}. {note}")
                log_error('browser_land_search', payload, e, 'continue with scraped/direct source buckets only', note)
    else:
        write_progress('browser_buckets', 'Flow comparable: Playwright ?ang search Batdongsan theo t?n d? ?n/khu v?c + qu?n + th?nh ph?...', warnings)
        is_rent_chungcu = (getattr(criteria, 'transaction', 'buy') == 'rent' and getattr(criteria, 'rent_subtype', '') == 'rent_chungcu')
        if is_rent_chungcu and is_fast_mode:
            warnings.append('R&D cho thu? chung c? fast-mode: b? qua Playwright comparable n?ng ?? tr?nh treo; d?ng evidence/fallback + AI estimate ??n v? tri?u/c?n/th?ng.')
        else:
            try:
                apt_browser = await asyncio.wait_for(
                    browser_true_buckets_async(criteria, projects, max_projects=5, per_project_timeout=(55 if is_fast_mode else 70)),
                    timeout=(700 if is_fast_mode else 780),
                )
                sample_count = sum(len(v or []) for v in apt_browser.values())
                if sample_count == 0:
                    loc = getattr(criteria, 'location_context', {}) or {}
                    city = (loc.get('city') or loc.get('province') or 'TP H? Ch? Minh') if isinstance(loc, dict) else 'TP H? Ch? Minh'
                    district = loc.get('district') if isinstance(loc, dict) else ''
                    fallback_browser = {}
                    for pr in (projects.projects or [])[:5]:
                        pname = (pr.get('name') or '').strip()
                        if not pname:
                            continue
                        keyword = (pr.get('search_keyword') or '').strip() or ' '.join(x for x in [pname, district, city] if x)
                        try:
                            rows = await asyncio.wait_for(scrape_batdongsan_playwright(keyword, limit=10, headless=False, mode=getattr(criteria, 'transaction', 'buy') or 'buy'), timeout=75)
                        except Exception:
                            rows = []
                        if rows:
                            fallback_browser.setdefault(f'Batdongsan.com.vn::{pname}', []).extend(rows)
                    if fallback_browser:
                        apt_browser = fallback_browser
                        sample_count = sum(len(v or []) for v in apt_browser.values())
                        warnings.append('Reuse-session Batdongsan tr? 0 m?u; ?? fallback m? search ??c l?p t?ng d? ?n.')
                buckets = merge_listing_buckets(buckets, apt_browser)
                warnings.append(f'Playwright Batdongsan flow comparable: {len(apt_browser)} bucket, {sample_count} m?u gi?.')
                if sample_count:
                    warnings.append('?? l?y m?u gi? Batdongsan b?ng Playwright theo keyword t?n d? ?n + qu?n + th?nh ph?.')
            except Exception as e:
                note = 'Playwright Batdongsan flow comparable timeout/l?i; ti?p t?c b?ng evidence/fallback + AI estimate.'
                warnings.append(f'browser flow comparable l?i/timeout: {type(e).__name__}. {note}')
                log_error('browser_buckets_comparable', payload, e, 'continue with fallback/AI estimate', note)

    has_price = any((getattr(l, 'price_total', None) or getattr(l, 'price_per_m2', None)) for listings in buckets.values() for l in listings)
    if not has_price:
        if not use_comparable_flow:
            warnings.append('Không có mẫu giá real parse được; không dùng AI estimate cho sản phẩm direct-search.')
            write_progress('no_real_street_price', 'Không có mẫu giá thực parse được; trả kết quả không có giá tham chiếu.', warnings)
        else:
            warnings.append('Web nguồn/search bị chặn hoặc không parse được giá; dùng AI estimate có nhãn kiểm chứng.')
            write_progress('ai_support', 'Nguồn thật chưa đủ giá; AI support đang tạo estimate có nhãn cần kiểm chứng...', warnings)
            try:
                ai_est_timeout = 60 if criteria.property_type == 'chungcu' else 60
                est = await asyncio.wait_for(build_ai_estimate_buckets(ai_report, criteria, projects), timeout=ai_est_timeout)
                buckets = merge_listing_buckets(buckets, est)
            except Exception as e:
                note = 'AI estimate timeout; giữ bucket hiện có và trả kết quả có cảnh báo, không gọi AI support phụ.'
                warnings.append(f'AI estimate lỗi: {type(e).__name__}. {note}')
                log_error('ai_support', payload, e, 'continue with available buckets', note)

    # Enforce transaction intent after every source has been merged, before any
    # report text, price summary, or verification link is rendered.
    is_rent = (getattr(criteria, 'transaction', 'buy') or 'buy') == 'rent'
    buckets = _filter_buckets_by_transaction(buckets, is_rent)
    buckets = _filter_buckets_by_rent_subtype(buckets, getattr(criteria, 'rent_subtype', '') if is_rent else '')

    write_progress('build_report', 'Đang tổng hợp báo cáo trực tiếp theo tên đường/khu vực...' if not use_comparable_flow else 'Đang tổng hợp báo cáo theo dự án/khu vực comparable...', warnings)
    try:
        if not use_comparable_flow:
            report = build_direct_land_report(projects, buckets, is_rent=is_rent)
        else:
            report = await asyncio.wait_for(build_project_price_report(ai_report, criteria, projects, buckets), timeout=60)
    except Exception as e:
        note = 'Report AI timeout/lỗi; dùng báo cáo tối thiểu deterministic từ dữ liệu hiện có, không gọi AI support phụ.'
        warnings.append(f'build_project_price_report lỗi: {type(e).__name__}. {note}')
        log_error('build_report', payload, e, 'minimal deterministic report', note)
        lines = ['📍 *Định giá trực tiếp theo tên đường/khu vực*' if not use_comparable_flow else '📍 *Định giá theo dự án/khu vực comparable*', '', 'Báo cáo chi tiết bị lỗi, em trả bản tối thiểu từ dữ liệu đã lấy được:']
        for idx, p in enumerate(projects.projects[:5], 1):
            name = p.get('name') or f'Comparable {idx}'
            listings = buckets.get(name, []) or []
            lines.append(f"\n{idx}. {name}")
            if listings:
                lines.append(f"- Số mẫu/link có được: {len(listings)}")
                first_urls = [getattr(x, 'url', '') for x in listings if getattr(x, 'url', '')][:3]
                if first_urls:
                    lines.append('- Link kiểm chứng:')
                    lines.extend([f"  {i}) {u}" for i, u in enumerate(first_urls, 1)])
            else:
                lines.append('- Chưa lấy được mẫu giá trực tiếp; cần kiểm chứng thêm.')
        report = '\n'.join(lines)

    attach_ref_average_prices(projects, buckets)

    ai_sale_assessment_text = ''
    investor_summary = {}
    if criteria.property_type == 'chungcu':
        # Restore valuation-appraisal section in web fast-mode without adding slow chained AI calls.
        # It is deterministic from real Batdongsan/Playwright samples and appears after the R&D price table.
        try:
            appraisal_text, appraisal_summary = build_appraisal_summary(criteria, projects, buckets)
            if appraisal_text:
                ai_sale_assessment_text = appraisal_text
                investor_summary.update(appraisal_summary or {})
                warnings.append('Đã bổ sung báo cáo thẩm định giá sơ bộ từ mẫu giá thật.')
            else:
                warnings.append('Chưa đủ mẫu giá thật để dựng báo cáo thẩm định giá sơ bộ.')
        except Exception as e:
            warnings.append(f'Báo cáo thẩm định giá sơ bộ lỗi: {type(e).__name__}.')
            log_error('appraisal_summary', payload, e, 'continue without appraisal section')
        report += ai_sale_assessment_text

    write_progress('render_map', 'Đang dựng bản đồ kiểm chứng...', warnings)
    map_b64 = None
    map_caption = None
    map_points = []
    if use_comparable_flow:
        write_progress('render_map', 'Đang geocode 5 dự án/khu vực comparable và dựng bản đồ...', warnings)
        try:
            map_points = await asyncio.wait_for(geocode_projects_google_maps(criteria, projects, timeout_sec=180), timeout=200)
        except Exception as e:
            warnings.append(f'Google Maps geocode lỗi: {type(e).__name__}.')
            log_error('render_map_geocode', payload, e, 'fallback nominatim')
            map_points = []
        try:
            resolved = {getattr(mp, 'name', ''): mp for mp in map_points}
            missing = [(p.get('name') or '').strip() for p in projects.projects[:5]
                       if (p.get('name') or '').strip() and not (resolved.get((p.get('name') or '')[:80]) or resolved.get(p.get('name') or ''))]
            if missing:
                write_progress('render_map', f'Bổ sung tọa độ {len(missing)} dự án qua OpenStreetMap...', warnings)
                extra = await asyncio.wait_for(geocode_names_nominatim(criteria, missing, max_dist_km=8.0), timeout=90)
                have = {(mp.name or '').strip().lower() for mp in map_points}
                for mp in (extra or []):
                    if (mp.name or '').strip().lower() not in have:
                        map_points.append(mp)
        except Exception as e:
            warnings.append(f'Nominatim geocode fallback lỗi: {type(e).__name__}.')
    if use_comparable_flow:
        try:
            map_points = [mp for mp in map_points if _dist_km(criteria.lat, criteria.lng, mp.lat, mp.lng) <= 8.0]
            point_by_name = {getattr(mp, 'name', ''): mp for mp in map_points}
            for p in projects.projects:
                mp = point_by_name.get((p.get('name') or '')[:80]) or point_by_name.get(p.get('name') or '')
                if mp:
                    p['distance_km'] = round(_dist_km(criteria.lat, criteria.lng, mp.lat, mp.lng), 2)
                    p['lat'] = mp.lat
                    p['lng'] = mp.lng
            valuation_points = build_valuation_points(projects, map_points, buckets, getattr(criteria, 'transaction', 'buy'))
            map_png = render_valuation_map_png(criteria.lat, criteria.lng, valuation_points, title='Bản đồ vệ tinh: vị trí nghiên cứu + dự án khảo sát')
            map_caption = '🗺️ Bản đồ so sánh: pin dự án/khu vực + giá/m²'
            if not map_png:
                map_png = build_map_snapshot(criteria.lat, criteria.lng, map_points, title=f"Vị trí so sánh quanh {projects.area_description}")
                map_caption = '🗺️ Map sơ đồ dự phòng: tọa độ cần định giá và các dự án/khu vực so sánh'
            if map_png:
                map_b64 = base64.b64encode(map_png).decode('ascii')
        except Exception as e:
            note = 'Bỏ qua render map vì lỗi/timeout.'
            warnings.append(f'render map lỗi: {type(e).__name__}. {note}')
            log_error('render_map', payload, e, 'continue without map image', note)
            map_caption = None
            map_b64 = None

    direct_struct = direct_market_structured_fields(buckets, is_rent=(getattr(criteria, 'transaction', 'buy') == 'rent')) if not use_comparable_flow else {}
    merged_investor_summary = dict(direct_struct.get('investor_summary') or {})
    merged_investor_summary.update(investor_summary or {})
    if (direct_struct.get('price_sample_count') or 0) > 0 and not use_comparable_flow:
        ref = merged_investor_summary.get('reference_price_label') or merged_investor_summary.get('average_suggested_price') or direct_struct.get('suggested_price_range') or ''
        samples = direct_struct.get('price_samples') or []
        sample_lines = []
        for i, sm in enumerate(samples[:8], 1):
            title = sm.get('title') or sm.get('source') or 'Mẫu thị trường'
            ppm = sm.get('price_per_m2')
            total = sm.get('price_total')
            bits = []
            try:
                if ppm and is_rent:
                    bits.append(f"{_fmt_num(float(ppm)*1000,0)} ngàn/m²/tháng")
                elif ppm:
                    bits.append(f"{_fmt_num(float(ppm),0)} triệu/m²")
            except Exception:
                pass
            try:
                if total and is_rent:
                    bits.append(f"{_fmt_num(float(total)*1000,1)} triệu/tài sản/tháng")
                elif total:
                    bits.append(f"{_fmt_num(float(total),1)} tỷ")
            except Exception:
                pass
            sample_lines.append(f"{i}. {title[:180]}" + (" — " + " / ".join(bits) if bits else ""))
        report = '\n'.join([
            '📍 *Định giá trực tiếp theo mẫu tin thị trường*',
            '',
            f"Giá tham chiếu: {ref}" if ref else 'Giá tham chiếu: cần kiểm chứng thêm',
            f"Số mẫu có giá: {direct_struct.get('price_sample_count') or 0}/{direct_struct.get('sample_count') or 0}",
            '',
            '*Mẫu tin/link kiểm chứng:*',
            *sample_lines,
            '',
            'Lưu ý: giá là median/tổng hợp từ mẫu tin thị trường đã parse được; cần kiểm chứng diện tích, vị trí, pháp lý và trạng thái tin trước khi ra quyết định.'
        ])
    result_comparables = projects.projects[:5] if use_comparable_flow else (direct_struct.get('direct_comparables') or [])
    if needs_ai_comparables:
        seen_names = {str(x.get('name') or '').strip().lower() for x in result_comparables if isinstance(x, dict)}
        for p in (projects.projects or [])[:5]:
            name = str(p.get('name') or '').strip()
            if name and name.lower() not in seen_names:
                result_comparables.append(p)
                seen_names.add(name.lower())
    result = {
        'ok': True,
        'criteria': payload,
        'area': projects.area_description,
        'intro': intro,
        'comparables': result_comparables[:8],
        'location_context': getattr(criteria, 'location_context', {}) or {},
        'ai_sale_assessment': ai_sale_assessment_text,
        'investor_summary': merged_investor_summary,
        'price_samples': direct_struct.get('price_samples') or [],
        'price_sample_count': direct_struct.get('price_sample_count') or 0,
        'sample_count': direct_struct.get('sample_count') or 0,
        'suggested_price_range': direct_struct.get('suggested_price_range') or '',
        'report': report,
        'text': intro + "\n\n" + report,
        'map_png_base64': map_b64,
        'map_caption': map_caption if map_b64 else None,
        'warnings': warnings,
    }
    result['summary_score'] = market_summary_score(result)
    write_progress('done', 'Hoàn tất báo cáo R&D thị trường.', warnings)
    return result


def strip_surrogates(obj):
    if isinstance(obj, str):
        return fix_vn_text(obj)
    if isinstance(obj, list):
        return [strip_surrogates(x) for x in obj]
    if isinstance(obj, dict):
        return {strip_surrogates(k): strip_surrogates(v) for k, v in obj.items()}
    return obj


def main():
    raw = sys.stdin.read()
    payload = json.loads(raw or '{}')
    try:
        out = asyncio.run(run_web_valuation(payload))
    except Exception as e:
        out = {'ok': False, 'error': f'{type(e).__name__}: {e}'}
    out = strip_surrogates(out)
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode('utf-8', 'replace'))
    sys.stdout.buffer.write(b'\n')


if __name__ == '__main__':
    main()
