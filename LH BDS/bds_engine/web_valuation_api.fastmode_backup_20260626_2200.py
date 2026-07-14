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
    try:
        x = x.encode('utf-8', 'replace').decode('utf-8', 'replace')
    except Exception:
        pass
    if _ftfy_fix_text:
        try:
            x = _ftfy_fix_text(x)
        except Exception:
            pass
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
    data = {'ok': True, 'jobId': JOB_ID, 'time': _now(), 'stage': stage, 'message': fix_vn_text(message), 'warnings': [fix_vn_text(w) for w in (warnings or [])]}
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
from ai_search_planner import build_search_targets
from browser_search import discover_real_source_links, listings_from_search_hits, merge_listing_buckets
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


def build_appraisal_summary(criteria: SearchCriteria, projects: ProjectsResult, buckets: dict) -> tuple[str, dict[str, Any]]:
    """Deterministic appraisal section restored for web fast-mode.

    Uses real Batdongsan/browser samples already collected, so it is fast and
    does not add another AI call. This complements the raw R&D price table with
    a valuation-style conclusion like the older report.
    """
    project_rows = []
    all_ppm: list[float] = []
    for p in (projects.projects or [])[:5]:
        name = (p.get('name') or '').strip()
        listings = []
        for key, rows in (buckets or {}).items():
            k = str(key).lower()
            if name and (name.lower() in k or k.endswith('::' + name.lower())):
                listings.extend(rows or [])
        ppms = [float(getattr(x, 'price_per_m2', 0) or 0) for x in listings if getattr(x, 'price_per_m2', None)]
        if ppms:
            med = _median(ppms)
            project_rows.append({'name': name, 'median': med, 'min': min(ppms), 'max': max(ppms), 'n': len(ppms), 'developer': p.get('developer') or '', 'scale': p.get('scale') or ''})
            all_ppm.extend(ppms)
    if not all_ppm:
        return ('', {})
    market_med = _median(all_ppm) or 0
    low = market_med * 0.95
    high = market_med * 1.05
    selected = sorted(project_rows, key=lambda r: (abs((r.get('median') or market_med) - market_med), -r.get('n', 0)))[0] if project_rows else {}
    lines = [
        '',
        '🏦 *Báo cáo thẩm định giá sơ bộ*',
        '',
        f'- Phương pháp: so sánh trực tiếp từ {len(project_rows)} dự án comparable, {len(all_ppm)} mẫu giá rao có nguồn Batdongsan/Playwright.',
        f'- Mặt bằng giá thị trường: khoảng {_fmt_num(min(all_ppm),1)}–{_fmt_num(max(all_ppm),1)} triệu/m²; median {_fmt_num(market_med,1)} triệu/m².',
        f'- Khoảng giá đề xuất thận trọng cho sản phẩm mục tiêu: {_fmt_num(low,1)}–{_fmt_num(high,1)} triệu/m².',
    ]
    if selected:
        lines.append(f'- Comparable neo chính: {selected["name"]} (~{_fmt_num(selected["median"],1)} triệu/m², {selected["n"]} mẫu), sau đó đối chiếu với các dự án còn lại theo vị trí/quy mô/bàn giao.')
    lines.extend(['', '*Bảng comparable dùng cho thẩm định:*'])
    for i, r in enumerate(sorted(project_rows, key=lambda x: x.get('median') or 0, reverse=True), 1):
        lines.append(f'{i}. {r["name"]}: median ~{_fmt_num(r["median"],1)} triệu/m² ({r["n"]} mẫu; biên {_fmt_num(r["min"],1)}–{_fmt_num(r["max"],1)}).')
    lines.extend([
        '',
        '*Kết luận sơ bộ:*',
        f'- Nếu sản phẩm mục tiêu có chất lượng/vị trí tương đương nhóm trung vị, có thể lấy mốc {_fmt_num(market_med,1)} triệu/m² làm giá tham chiếu.',
        '- Nếu tầng/view/pháp lý/nội thất tốt hơn nhóm mẫu, xem xét cộng biên 3–7%; nếu bất lợi hơn, trừ 3–10%.',
        '- Đây là báo cáo sơ bộ từ giá rao thị trường; trước khi chốt giá cần kiểm chứng giao dịch thực tế, pháp lý căn hộ và tình trạng bàn giao.',
    ])
    summary = {
        'selected_comparable': selected.get('name'),
        'reference_price': round(market_med, 1),
        'reference_price_label': f'~{_fmt_num(market_med,1)} triệu/m²',
        'suggested_price_range': f'{_fmt_num(low,1)}–{_fmt_num(high,1)} triệu/m²',
        'sample_count': len(all_ppm),
        'comparable_count': len(project_rows),
    }
    return '\n'.join(lines), summary


async def browser_direct_land_buckets(criteria: SearchCriteria, projects: ProjectsResult) -> dict:
    loc = getattr(criteria, 'location_context', {}) or {}
    area = projects.area_description
    road = extract_road(loc)
    ward = loc.get('ward') or loc.get('suburb') or loc.get('phuong') or ''
    district = loc.get('district') or loc.get('city') or ''
    queries = []
    city = loc.get('city') or loc.get('province') or 'Hồ Chí Minh'
    road_scope = ' '.join(x for x in [road, ward, district, city] if x)
    if road:
        queries += [f"bán nhà đất mặt tiền {road_scope}", f"bán đất mặt tiền {road_scope}"]
    if ward:
        queries += [f"bán nhà đất {ward} {district} Hồ Chí Minh", f"bán đất {ward} {district} Hồ Chí Minh"]
    queries.append(f"bán nhà đất {area}")
    buckets = {}
    write_progress('browser_street_queries', 'Chrome search theo tên đường: ' + ' | '.join(queries[:5]))
    for q in queries[:5]:
        try:
            rows = await scrape_batdongsan_playwright(q, limit=8, headless=False, mode='buy')
            if rows:
                buckets.setdefault('Batdongsan.com.vn', []).extend(rows)
        except Exception:
            continue
    return buckets


def build_direct_land_report(projects: ProjectsResult, buckets: dict) -> str:
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
        lines.append(f"- Giá/m² median: ~{_fmt_num(med(ppms),0)} tr/m²")
        lines.append(f"- Biên giá/m²: {_fmt_num(min(ppms),0)}–{_fmt_num(max(ppms),0)} tr/m²")
    elif totals:
        lines.append(f"- Số mẫu có giá tổng: {len(totals)}")
        lines.append(f"- Giá tổng median: ~{_fmt_num(med(totals),1)} tỷ")
    lines.append('')
    lines.append('*Mẫu tin/link kiểm chứng:*')
    for i, x in enumerate(all_items[:12], 1):
        desc = []
        if x.get('ppm'): desc.append(f"~{_fmt_num(x['ppm'],0)} tr/m²")
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


def summarize_price_samples(buckets: dict, limit: int = 20) -> list[dict[str, Any]]:
    out = []
    seen = set()
    for bucket_name, listings in (buckets or {}).items():
        for l in listings or []:
            url = getattr(l, 'url', '') or ''
            title = getattr(l, 'title', '') or ''
            key = url or title
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'bucket': bucket_name,
                'title': title[:220],
                'source': getattr(l, 'source', '') or '',
                'price_total': getattr(l, 'price_total', None),
                'area_m2': getattr(l, 'area_m2', None),
                'price_per_m2': getattr(l, 'price_per_m2', None),
                'url': url,
            })
            if len(out) >= limit:
                return out
    return out



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

    if criteria.property_type != 'chungcu':
        write_progress('direct_street_search', 'Sản phẩm không phải chung cư: ưu tiên tìm/search theo tên đường...', warnings)
        projects = direct_land_projects(criteria)
    else:
        write_progress('find_comparables', 'Chung cư: đang tìm 5 dự án/khu vực comparable giống BDS_bot...', warnings)
        try:
            projects = await asyncio.wait_for(find_nearby_projects(ai_fast, criteria), timeout=45)
        except Exception as e:
            note = 'Fallback dự án/khu vực vì AI tìm comparable quá chậm/timeout.'
            warnings.append(f"find_nearby_projects lỗi/timeout, dùng fallback: {type(e).__name__}. {note}")
            log_error('find_comparables', payload, e, 'fallback_nearby_projects', note)
            projects = fallback_nearby_projects(criteria, type(e).__name__)

    project_text = "\n".join(_project_line(i, p) for i, p in enumerate(projects.projects[:5])) or "  (AI không trả về dự án nào)"
    if criteria.property_type != 'chungcu':
        intro = (
            f"Khu vực: {projects.area_description}\n\n"
            "⏳ Đang tìm mẫu tin trực tiếp theo tên đường/phường/khu vực trên Batdongsan, Guland, Alonhadat…"
        )
    else:
        intro = (
            f"Khu vực: {projects.area_description}\n\n"
            f"5 dự án/khu vực tham chiếu:\n{project_text}\n\n"
            "⏳ Tiếp tục scrape Batdongsan, Guland, Alonhadat…"
        )

    project_names = [p.get('name', '') for p in projects.projects if p.get('name')]
    if criteria.property_type == 'chungcu':
        write_progress('discover_links', 'Web fast-mode: bỏ qua search link nguồn thật chậm cho chung cư; dùng fallback links + AI estimate...', warnings)
        warnings.append('Web fast-mode: bỏ qua discover_real_source_links cho chung cư vì bước này thường timeout 45-75s trên web; dùng fallback links + AI chính.')
        evidence_buckets = fallback_source_links(project_names, criteria.lat, criteria.lng)
    else:
        write_progress('discover_links', 'Đang search link nguồn thật Batdongsan/Guland/Alonhadat...', warnings)
        try:
            search_targets = await asyncio.wait_for(build_search_targets(ai_fast, criteria, projects), timeout=(12 if is_fast_mode else 30))
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
    if criteria.property_type == 'chungcu':
        note = 'Web fast-mode: bỏ qua scrape nguồn nặng cho chung cư để tránh treo; dùng evidence/fallback + AI estimate có nhãn kiểm chứng.'
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
    if criteria.property_type != 'chungcu':
        write_progress('browser_street_search', 'Sản phẩm không phải chung cư: Chrome đang search trực tiếp Batdongsan theo tên đường/phường...', warnings)
        if is_fast_mode:
            warnings.append('Fast-mode: bỏ qua browser_direct_land_buckets nặng; dùng Google snippet/browser_price nhanh để tránh treo Playwright.')
        else:
            try:
                land_true = await asyncio.wait_for(browser_direct_land_buckets(criteria, projects), timeout=220)
                buckets = merge_listing_buckets(buckets, land_true)
            except Exception as e:
                note = await ai_support_agent(ai_report, 'browser_direct_land', payload, e, 'try Google snippet browser price search')
                warnings.append(f"browser direct land lỗi/timeout: {type(e).__name__}. {note}")
                log_error('browser_direct_land', payload, e, 'try Google snippet browser price search', note)
        try:
            land_browser = await asyncio.wait_for(browser_price_buckets(criteria, projects, max_projects=(3 if is_fast_mode else 5)), timeout=(35 if is_fast_mode else 120))
            buckets = merge_listing_buckets(buckets, land_browser)
        except Exception as e:
            note = 'Fast-mode bỏ qua AI support phụ sau lỗi browser search.' if is_fast_mode else await ai_support_agent(ai_report, 'browser_land_search', payload, e, 'continue with scraped/direct source buckets only')
            warnings.append(f"browser land search lỗi/timeout: {type(e).__name__}. {note}")
            log_error('browser_land_search', payload, e, 'continue with scraped/direct source buckets only', note)
    else:
        write_progress('browser_buckets', 'Chung cư: Playwright đang search Batdongsan theo tên dự án + thành phố...', warnings)
        try:
            apt_browser = await asyncio.wait_for(
                browser_true_buckets_async(criteria, projects, max_projects=5, per_project_timeout=(55 if is_fast_mode else 70)),
                timeout=(320 if is_fast_mode else 420),
            )
            buckets = merge_listing_buckets(buckets, apt_browser)
            sample_count = sum(len(v or []) for v in apt_browser.values())
            warnings.append(f'Playwright Batdongsan chung cư: {len(apt_browser)} bucket, {sample_count} mẫu giá.')
            if sample_count:
                warnings.append('Đã lấy mẫu giá Batdongsan bằng Playwright theo keyword tên dự án + thành phố.')
        except Exception as e:
            note = 'Playwright Batdongsan chung cư timeout/lỗi; tiếp tục bằng evidence/fallback + AI estimate.'
            warnings.append(f'browser chung cư lỗi/timeout: {type(e).__name__}. {note}')
            log_error('browser_buckets_chungcu', payload, e, 'continue with fallback/AI estimate', note)

    has_price = any((getattr(l, 'price_total', None) or getattr(l, 'price_per_m2', None)) for listings in buckets.values() for l in listings)
    if not has_price:
        if criteria.property_type != 'chungcu':
            warnings.append('Không có mẫu giá real parse được; không dùng AI estimate cho sản phẩm không phải chung cư.')
            write_progress('no_real_street_price', 'Không có mẫu giá real parse được; trả kết quả không có số ước lượng.', warnings)
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

    write_progress('build_report', 'Đang tổng hợp báo cáo trực tiếp theo tên đường/khu vực...' if criteria.property_type != 'chungcu' else 'Đang tổng hợp báo cáo theo dự án/khu vực comparable...', warnings)
    try:
        if criteria.property_type != 'chungcu':
            report = build_direct_land_report(projects, buckets)
        else:
            report = await asyncio.wait_for(build_project_price_report(ai_report, criteria, projects, buckets), timeout=60)
    except Exception as e:
        note = 'Report AI timeout/lỗi; dùng báo cáo tối thiểu deterministic từ dữ liệu hiện có, không gọi AI support phụ.'
        warnings.append(f'build_project_price_report lỗi: {type(e).__name__}. {note}')
        log_error('build_report', payload, e, 'minimal deterministic report', note)
        lines = ['📍 *Định giá trực tiếp theo tên đường/khu vực*' if criteria.property_type != 'chungcu' else '📍 *Định giá theo dự án/khu vực comparable*', '', 'Báo cáo chi tiết bị lỗi, em trả bản tối thiểu từ dữ liệu đã lấy được:']
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
    if criteria.property_type == 'chungcu':
        write_progress('render_map', 'Đang geocode 5 dự án và dựng bản đồ...', warnings)
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

    write_progress('done', 'Hoàn tất báo cáo R&D thị trường.', warnings)
    return {
        'ok': True,
        'criteria': payload,
        'area': projects.area_description,
        'intro': intro,
        'comparables': projects.projects[:5],
        'location_context': getattr(criteria, 'location_context', {}) or {},
        'ai_sale_assessment': ai_sale_assessment_text,
        'investor_summary': investor_summary,
        'report': report,
        'text': intro + "\n\n" + report,
        'map_png_base64': map_b64,
        'map_caption': map_caption if map_b64 else None,
        'warnings': warnings,
    }


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
