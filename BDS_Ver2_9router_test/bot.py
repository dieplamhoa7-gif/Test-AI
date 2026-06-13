"""Telegram bot: /gia <lat>,<lng> → menu loại → MĐSDĐ → đặc tính → định giá."""
from __future__ import annotations

import logging
import os
import sys
import time
try:
    import msvcrt  # Windows-only single-instance lock
except ImportError:  # Linux/Render
    msvcrt = None
try:
    import fcntl  # POSIX single-instance lock
except ImportError:
    fcntl = None
import re
import uuid
import asyncio
from io import BytesIO

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from flask import Flask, request, jsonify

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from ai_client import NineRouterClient, make_role_client
from ai_search_planner import build_search_targets
from browser_search import discover_real_source_links, listings_from_search_hits, merge_listing_buckets
from browser_crawler import browser_price_buckets
from playwright_bds_scraper import browser_true_buckets_async
from search_fallback import fallback_source_links
from config import load_settings
from map_snapshot import MapPoint, build_map_snapshot
from valuation_map import ValuationMapPoint, render_valuation_map_png
from google_maps_geocoder import geocode_projects_google_maps
from scraper import (
    fallback_nearby_projects,
    FEATURE_LABELS,
    MDSDD_LABELS,
    PROPERTY_TYPE_LABELS,
    SearchCriteria,
    find_nearby_projects,
    scrape_all_sources,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bds-bot")


_SINGLE_INSTANCE_LOCK = None

def acquire_single_instance_lock() -> bool:
    """Prevent multiple Telegram polling instances for the same bot on Windows."""
    global _SINGLE_INSTANCE_LOCK
    lock_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bds_bot_single_instance.lock")
    f = open(lock_path, "a+")
    try:
        if msvcrt is not None:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        elif fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        logger.warning("Another bot.py instance is already running; exiting this duplicate instance.")
        try:
            f.close()
        except Exception:
            pass
        return False
    # Keep the file handle open to hold the OS lock. Do not write/truncate here;
    # OneDrive/Windows may deny writes on locked files.
    _SINGLE_INSTANCE_LOCK = f
    return True

# === Cấu hình menu ===
PROPERTY_TYPES = [
    ("dat", "Đất"),
    ("nha", "Nhà"),
    ("chungcu", "Chung cư"),
    ("khoxuong", "Kho/xưởng"),
    ("shophouse", "Shophouse/mặt bằng"),
]

TRANSACTION_LABELS = {"buy": "Mua", "rent": "Thuê"}
RENT_TYPES = [
    ("rent_nha", "Thuê nhà"),
    ("rent_vanphong", "Văn phòng"),
    ("rent_santhuongmai", "Sàn thương mại"),
    ("rent_chungcu", "Chung cư"),
]
SEGMENTS = [("A", "Hạng A"), ("B", "Hạng B"), ("C", "Hạng C")]
SEGMENT_LABELS = {k: v for k, v in SEGMENTS}

# Mỗi loại có set MĐSDĐ riêng (giữ đúng ảnh mẫu)
MDSDD_BY_TYPE: dict[str, list[tuple[str, str]]] = {
    "dat":        [("ODT", "ODT"), ("ONT", "ONT"), ("TMD", "TMD"), ("SKC", "SKC"), ("CLN", "CLN"), ("NN", "NN")],
    "nha":        [("ODT", "ODT"), ("ONT", "ONT"), ("TMD", "TMD")],
    "chungcu":    [("ODT", "ODT"), ("TMD", "TMD"), ("SKC", "SKC"), ("CLN", "CLN"), ("NN", "NN")],
    "khoxuong":   [("SKC", "SKC"), ("TMD", "TMD"), ("CLN", "CLN"), ("NN", "NN")],
    "shophouse":  [("ODT", "ODT"), ("TMD", "TMD"), ("SKC", "SKC")],
}

FEATURES = [
    ("mattien", "Mặt tiền"),
    ("cango", "Căn góc/2MT"),
    ("hem", "Hẻm/ngõ"),
    ("skip", "Bỏ qua"),
]

COORD_RE = re.compile(
    r"^\s*([-+]?\d+\.?\d*)\s*[, ]\s*([-+]?\d+\.?\d*)\s*$"
)

# Lưu state tạm theo session_id (sinh từ callback_data) — tránh giới hạn 64-byte của callback_data
SESSIONS: dict[str, dict] = {}


# ---------- helpers ----------
def _new_session(lat: float, lng: float) -> str:
    sid = uuid.uuid4().hex[:10]
    SESSIONS[sid] = {"lat": lat, "lng": lng}
    return sid


def _kb_transaction(sid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Mua", callback_data=f"x|{sid}|buy"),
            InlineKeyboardButton("Thuê", callback_data=f"x|{sid}|rent"),
        ]
    ])


def _kb_property_type(sid: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Đất", callback_data=f"t|{sid}|dat"),
            InlineKeyboardButton("Nhà phố", callback_data=f"t|{sid}|nha"),
            InlineKeyboardButton("Chung cư", callback_data=f"t|{sid}|chungcu"),
        ],
        [
            InlineKeyboardButton("Shophouse", callback_data=f"t|{sid}|shophouse"),
            InlineKeyboardButton("Kho/xưởng", callback_data=f"t|{sid}|khoxuong"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def _kb_rent_type(sid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Thuê nhà", callback_data=f"rt|{sid}|rent_nha"),
            InlineKeyboardButton("Văn phòng", callback_data=f"rt|{sid}|rent_vanphong"),
        ],
        [
            InlineKeyboardButton("Sàn thương mại", callback_data=f"rt|{sid}|rent_santhuongmai"),
            InlineKeyboardButton("Chung cư", callback_data=f"rt|{sid}|rent_chungcu"),
        ],
    ])


def _kb_segment(sid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(label, callback_data=f"s|{sid}|{code}") for code, label in SEGMENTS
    ]])


def _kb_mdsdd(sid: str, ptype: str) -> InlineKeyboardMarkup:
    opts = MDSDD_BY_TYPE.get(ptype, [])
    buttons = [
        InlineKeyboardButton(label, callback_data=f"m|{sid}|{code}")
        for code, label in opts
    ]
    # 5 nút mỗi hàng
    rows = [buttons[i : i + 5] for i in range(0, len(buttons), 5)]
    return InlineKeyboardMarkup(rows)


def _kb_feature(sid: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Mặt tiền", callback_data=f"f|{sid}|mattien"),
            InlineKeyboardButton("Căn góc/2MT", callback_data=f"f|{sid}|cango"),
        ],
        [
            InlineKeyboardButton("Hẻm/ngõ", callback_data=f"f|{sid}|hem"),
            InlineKeyboardButton("Bỏ qua", callback_data=f"f|{sid}|skip"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


# ---------- handlers ----------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Xin chào! Em là bot định giá BĐS theo toạ độ.\n\n"
        "Cách dùng:\n"
        "  /gia 10.74321023020177, 106.70092644994568\n\n"
        "Anh gửi toạ độ kèm lệnh, em sẽ hiện menu chọn loại tài sản → MĐSDĐ → đặc tính, "
        "rồi tổng hợp giá từ 3 nguồn Batdongsan, Guland, Alonhadat."
    )


async def cmd_gia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args_text = " ".join(context.args) if context.args else ""
    m = COORD_RE.match(args_text)
    if not m:
        await update.message.reply_text(
            "C? ph?p ch?a ??ng. Vd:\n"
            "  /gia 10.74321023020177, 106.70092644994568"
        )
        return

    lat, lng = float(m.group(1)), float(m.group(2))
    sid = _new_session(lat, lng)

    await update.message.reply_text(
        f"/gia {lat}, {lng}\n\nAnh mu?n *Mua* hay *Thu?*?",
        reply_markup=_kb_transaction(sid),
        parse_mode=ParseMode.MARKDOWN,
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    parts = data.split("|", 2)
    if len(parts) != 3:
        return
    step, sid, value = parts
    session = SESSIONS.get(sid)
    if not session:
        await query.edit_message_text("Phiên đã hết hạn. Anh gửi lại /gia <lat>, <lng> nhé.")
        return

    lat, lng = session["lat"], session["lng"]
    ptype = session.get("ptype")
    transaction = session.get("transaction")

    if step == "x":  # mua/thuê
        session["transaction"] = value
        if value == "buy":
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Mua\nAnh chọn loại tài sản:",
                reply_markup=_kb_property_type(sid),
            )
        else:
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Thuê\nAnh chọn loại thuê:",
                reply_markup=_kb_rent_type(sid),
            )
        return

    if step == "rt":  # loại thuê
        session["ptype"] = value
        rent_label = dict(RENT_TYPES).get(value, value)
        # Thuê nhà -> vị trí; Văn phòng/Sàn TM/Chung cư -> phân khúc rồi vị trí
        if value == "rent_nha":
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Thuê | Loại: {rent_label}\nAnh chọn vị trí:",
                reply_markup=_kb_feature(sid),
            )
        else:
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Thuê | Loại: {rent_label}\nAnh chọn phân khúc:",
                reply_markup=_kb_segment(sid),
            )
        return

    if step == "s":  # phân khúc
        session["segment"] = value
        label = SEGMENT_LABELS.get(value, value)
        await query.edit_message_text(
            f"/gia {lat}, {lng}\n\nPhân khúc: {label}\nAnh chọn vị trí:",
            reply_markup=_kb_feature(sid),
        )
        return

    if step == "t":  # chọn loại tài sản mua
        session["ptype"] = value
        ptype_label = PROPERTY_TYPE_LABELS.get(value, value)
        if value == "chungcu":
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Mua | Loại tài sản: {ptype_label}\nAnh chọn phân khúc:",
                reply_markup=_kb_segment(sid),
            )
        elif value == "shophouse":
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Mua | Loại tài sản: {ptype_label}\nAnh chọn vị trí:",
                reply_markup=_kb_feature(sid),
            )
        else:
            await query.edit_message_text(
                f"/gia {lat}, {lng}\n\nGiao dịch: Mua | Loại tài sản: {ptype_label}\nAnh chọn MĐSDĐ:",
                reply_markup=_kb_mdsdd(sid, value),
            )
        return

    if step == "m":  # chọn MĐSDĐ
        if not ptype:
            await query.edit_message_text("Phiên thiếu thông tin. Anh gửi lại /gia.")
            return
        session["mdsdd"] = value
        ptype_label = PROPERTY_TYPE_LABELS.get(ptype, ptype)
        await query.edit_message_text(
            f"/gia {lat}, {lng}\n\nAnh chọn đặc tính/vị trí tài sản:\n"
            f"Loại tài sản: {ptype_label}\nMĐSDĐ: {value}",
            reply_markup=_kb_feature(sid),
        )
        return

    if step == "f":  # chọn đặc tính → chạy định giá
        if not ptype:
            await query.edit_message_text("Phiên thiếu thông tin. Anh gửi lại /gia.")
            return
        session["feature"] = value
        mdsdd = session.get("mdsdd")
        ptype_label = PROPERTY_TYPE_LABELS.get(ptype, dict(RENT_TYPES).get(ptype, ptype))
        feature_label = FEATURE_LABELS.get(value, value)
        trans_label = TRANSACTION_LABELS.get(session.get("transaction"), session.get("transaction", ""))
        segment_label = SEGMENT_LABELS.get(session.get("segment"), session.get("segment", ""))
        parts_txt = [f"Giao dịch: {trans_label}", f"Loại: {ptype_label}"]
        if mdsdd:
            parts_txt.append(f"MĐSDĐ: {mdsdd}")
        if segment_label:
            parts_txt.append(f"Phân khúc: {segment_label}")
        parts_txt.append(f"Vị trí: {feature_label}")
        await query.edit_message_text(
            f"/gia {lat}, {lng}\n\n" + " | ".join(parts_txt) + "\n\n"
            f"⏳ Đang gọi AI tìm 5 dự án liên quan và scrape 3 nguồn… "
            f"có thể mất 30–90 giây."
        )

        try:
            await run_valuation(context, query, session)
        except Exception as e:
            logger.exception("Lỗi định giá: %s", e)
            await query.message.reply_text(
                f"❌ Có lỗi khi định giá: {type(e).__name__}: {e}"
            )
        finally:
            SESSIONS.pop(sid, None)


async def resolve_location_context(ai: NineRouterClient, criteria: SearchCriteria) -> dict:
    """AI reverse-geocode lightweight context: street/ward/city near coordinates."""
    system = (
        "Bạn là trợ lý GIS/BĐS Việt Nam. Từ tọa độ GPS, hãy suy ra tên đường/trục đường gần nhất, "
        "phường/quận/thành phố và mô tả ngắn để dùng search dự án BĐS. Chỉ trả JSON."
    )
    user = f"""Tọa độ: {criteria.lat}, {criteria.lng}

Trả JSON schema:
{{
  "street": "tên đường/trục đường gần nhất nếu biết",
  "ward": "phường/xã",
  "district": "quận/huyện/TP trực thuộc",
  "city": "thành phố/tỉnh",
  "search_hint": "cụm ngắn, ví dụ: gần đường ... phường ... TP ..."
}}

Nếu không chắc, ghi 'đang kiểm chứng' nhưng vẫn cố đưa thành phố/tỉnh hợp lý.
"""
    try:
        data = await ai.chat_json(system, user, temperature=0.1)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("resolve_location_context lỗi: %s", e)
        return {}


async def run_valuation(
    context: ContextTypes.DEFAULT_TYPE,
    query,
    session: dict,
) -> None:
    settings = context.application.bot_data["settings"]
    ai: NineRouterClient = context.application.bot_data["ai"]
    ai_fast: NineRouterClient = context.application.bot_data.get("ai_fast", ai)
    ai_bds: NineRouterClient = context.application.bot_data.get("ai_bds", ai)
    ai_report: NineRouterClient = context.application.bot_data.get("ai_report", ai)

    criteria = SearchCriteria(
        lat=session["lat"],
        lng=session["lng"],
        property_type=session["ptype"],
        mdsdd=session.get("mdsdd"),
        feature=session.get("feature"),
    )
    # Runtime extras for the BĐS bot flow.
    criteria.transaction = session.get("transaction", "buy")
    criteria.segment = session.get("segment")
    criteria.location_context = await resolve_location_context(ai_fast, criteria)

    # 1) Tìm 5 dự án; nếu AI timeout thì dùng fallback để không dừng bot
    try:
        projects = await find_nearby_projects(ai_fast, criteria)
    except Exception as e:
        logger.warning("find_nearby_projects timeout/lỗi, dùng fallback: %s", e)
        projects = fallback_nearby_projects(criteria, type(e).__name__)
        await query.message.reply_text(
            "⚠️ AI xác định dự án bị chậm/timeout, em dùng bộ comparable fallback để tiếp tục định giá."
        )
    def _short_project_line(i: int, p: dict) -> str:
        name = p.get('name') or '?'
        developer = p.get('developer') or p.get('investor') or p.get('chu_dau_tu') or 'CĐT đang kiểm chứng'
        scale = p.get('scale') or p.get('quy_mo') or p.get('size') or 'quy mô đang kiểm chứng'
        year = p.get('operation_year') or p.get('handover_year') or p.get('year') or p.get('nam_van_hanh') or 'năm vận hành đang kiểm chứng'
        delivered = p.get('delivered') or p.get('handover_status') or p.get('ban_giao') or 'tình trạng bàn giao đang kiểm chứng'
        return f"  {i + 1}. {name} - {developer} - {scale} - {year} - {delivered}"

    proj_text = "\n".join(
        _short_project_line(i, p)
        for i, p in enumerate(projects.projects[:5])
    ) or "  (AI không trả về dự án nào)"

    await query.message.reply_text(
        f"📍 *Khu vực:* {projects.area_description}\n\n"
        f"*5 dự án/khu vực tham chiếu:*\n{proj_text}\n\n"
        f"⏳ Tiếp tục scrape Batdongsan, Guland, Alonhadat…",
        parse_mode=ParseMode.MARKDOWN,
    )

    # 2) AI lập kế hoạch search + lấy link nguồn thật qua search engine
    project_names = [p.get("name", "") for p in projects.projects if p.get("name")]
    try:
        search_targets = await build_search_targets(ai_fast, criteria, projects)
        source_hits = await discover_real_source_links(search_targets, per_source_limit=6)
        evidence_buckets = listings_from_search_hits(source_hits)
    except Exception as e:
        logger.warning("AI/search link nguồn lỗi, dùng fallback source links: %s", e)
        evidence_buckets = fallback_source_links(project_names, criteria.lat, criteria.lng)
    if not any(evidence_buckets.values()):
        logger.warning("Search engine không trả link, dùng fallback source links")
        evidence_buckets = fallback_source_links(project_names, criteria.lat, criteria.lng)

    # 3) Scrape/ước lượng giá từ 3 nguồn, rồi merge thêm URL thật tìm được
    try:
        import asyncio
        buckets = await asyncio.wait_for(
            scrape_all_sources(ai_bds, criteria, projects, max_concurrent=1),
            timeout=180,
        )
    except Exception as e:
        logger.warning("scrape_all_sources lỗi/timeout, chỉ dùng link evidence: %s", e)
        buckets = {}
    buckets = merge_listing_buckets(buckets, evidence_buckets)

    # 3b) Browser thật: LUÔN chạy để lấy link nguồn thật dự án-scoped.
    try:
        import asyncio
        browser_buckets = await asyncio.wait_for(
            browser_true_buckets_async(criteria, projects),
            timeout=180,
        )
        buckets = merge_listing_buckets(buckets, browser_buckets)
    except Exception as e:
        logger.warning("browser_true_buckets lỗi/timeout: %s", e)
    if not any((getattr(l, "price_total", None) or getattr(l, "price_per_m2", None)) for listings in buckets.values() for l in listings):
        try:
            import asyncio
            browser_buckets = await asyncio.wait_for(browser_price_buckets(criteria, projects), timeout=180)
            buckets = merge_listing_buckets(buckets, browser_buckets)
        except Exception as e:
            logger.warning("browser_price_buckets lỗi/timeout: %s", e)

    has_price = any(
        (getattr(l, "price_total", None) or getattr(l, "price_per_m2", None))
        for listings in buckets.values() for l in listings
    )
    if not has_price:
        await query.message.reply_text("⚠️ Web nguồn/search bị chặn hoặc không parse được giá. Em dùng AI ước lượng và sẽ ghi nhãn rõ để anh kiểm chứng.")
        estimate_buckets = await build_ai_estimate_buckets(ai_report, criteria, projects)
        buckets = merge_listing_buckets(buckets, estimate_buckets)

    # 4) Báo cáo theo dự án/khu vực, không thống kê theo web
    project_report = await build_project_price_report(ai_report, criteria, projects, buckets)
    await query.message.reply_text(project_report, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    # 5) Tạo và gửi valuation map: nền bản đồ thật + pin dự án + nhãn giá/m²
    try:
        # Ưu tiên Google Maps search tên dự án + quận/thành phố; không dùng AI ước lượng tọa độ.
        map_points = await geocode_projects_google_maps(criteria, projects, timeout_sec=75)
    except Exception as e:
        logger.warning("Google Maps geocode lỗi, bỏ map points: %s", e)
        map_points = []
    # Map: pin đỏ là tọa độ nghiên cứu tuyệt đối. Chỉ ghim dự án nếu tọa độ geocode
    # nằm trong bán kính hợp lý quanh điểm nghiên cứu; tránh vẽ sai lên vệ tinh.
    def _dist_km(a_lat, a_lng, b_lat, b_lng):
        import math
        r=6371.0
        p1,p2=math.radians(a_lat),math.radians(b_lat)
        dp=math.radians(b_lat-a_lat); dl=math.radians(b_lng-a_lng)
        x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*r*math.atan2(math.sqrt(x), math.sqrt(1-x))
    map_points = [mp for mp in map_points if _dist_km(criteria.lat, criteria.lng, mp.lat, mp.lng) <= 8.0]
    valuation_points = build_valuation_points(projects, map_points, buckets, getattr(criteria, "transaction", "buy"))
    map_png = render_valuation_map_png(
        criteria.lat,
        criteria.lng,
        valuation_points,
        title=f"Bản đồ vệ tinh: vị trí nghiên cứu + dự án khảo sát",
    )
    caption = "🗺️ Bản đồ so sánh: pin dự án/khu vực + giá/m²"
    if not map_png:
        map_png = build_map_snapshot(
            criteria.lat,
            criteria.lng,
            map_points,
            title=f"Vị trí so sánh quanh {projects.area_description}",
        )
        caption = "🗺️ Map sơ đồ dự phòng: tọa độ cần định giá và các dự án/khu vực so sánh"
    if map_png:
        await query.message.reply_photo(
            photo=BytesIO(map_png),
            caption=caption,
        )

    # 6) Link nguồn đã nằm ngay dưới từng dự án trong report.
    # Không gửi thêm danh sách global để tránh lẫn nguồn giữa các dự án.


def _vn_norm(s: str) -> str:
    import unicodedata, re
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _listing_project_match(project_name: str, title: str) -> bool:
    """Strict project/source matching.

    Do NOT assign a source link to a project just because it shares a generic
    area token. For verification links, false positives are worse than missing
    links. Require exact phrase or most/all significant tokens.
    """
    pn = _vn_norm(project_name)
    tt = _vn_norm(title)
    if not pn or not tt:
        return False
    if pn in tt:
        return True
    stop = {"khu", "du", "an", "duong", "pho", "phuong", "quan", "thanh", "pho", "tp", "ho", "chi", "minh", "thu", "duc"}
    tokens = [t for t in pn.split() if len(t) >= 3 and t not in stop]
    if not tokens:
        return False
    hit = sum(1 for t in tokens if t in tt.split() or t in tt)
    # 1-3 significant tokens: require all. Longer names: require >=75%.
    if len(tokens) <= 3:
        return hit == len(tokens)
    return hit / len(tokens) >= 0.75


def _fmt_price_range(values: list[float], unit: str) -> str:
    if not values:
        return "chưa rõ"
    if len(values) == 1:
        return f"~{values[0]:.1f} {unit}"
    return f"{min(values):.1f}–{max(values):.1f} {unit}"


def build_valuation_points(projects, map_points: list[MapPoint], buckets: dict, transaction: str = "buy") -> list[ValuationMapPoint]:
    """Gắn dữ liệu giá trung bình vào tọa độ dự án để vẽ map.

    Buy: hiển thị giá bán TB theo tr/m².
    Rent: hiển thị giá thuê TB; ưu tiên triệu/tháng nếu có tổng giá thuê, kèm triệu/m²/tháng nếu có.
    """
    all_rows = []
    for source, listings in buckets.items():
        for l in listings:
            all_rows.append((source, l))

    out: list[ValuationMapPoint] = []
    is_rent = (transaction == "rent")
    for mp in map_points:
        # Quan trọng: ưu tiên bucket sinh ra từ chính search của dự án đó
        # (Batdongsan.com.vn::<project name>). Không match lại theo title trước,
        # vì title tin đăng nhiều khi không chứa đủ tên dự án làm giá lệch web.
        scoped = [
            (src, l) for src, l in all_rows
            if "::" in src and src.split("::", 1)[1].strip().lower() == mp.name.strip().lower()
        ]
        matched = scoped or [(src, l) for src, l in all_rows if _listing_project_match(mp.name, l.title)]
        # Chỉ lấy mẫu có URL thật, bỏ AI estimate/no-url khỏi giá trên map.
        matched = [(src, l) for src, l in matched if getattr(l, "url", "") and src != "AI estimate"]
        prices = [l.price_total for _, l in matched if l.price_total]
        ppms = [l.price_per_m2 for _, l in matched if l.price_per_m2]
        sources = sorted({src.split("::",1)[0] for src, _ in matched})
        avg_ppm = (sum(ppms) / len(ppms)) if ppms else None
        avg_price = (sum(prices) / len(prices)) if prices else None
        if is_rent:
            # In rent mode scraper stores price_total as billion-equivalent: 0.015 = 15 triệu/tháng.
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

def build_source_links_text(buckets: dict, max_links: int = 12) -> str:
    """Tạo danh sách link nguồn kiểm chứng, ưu tiên URL thật từ listings."""
    rows = []
    seen = set()
    for source, listings in buckets.items():
        for l in listings:
            url = (l.url or "").strip()
            if not url or not (url.startswith("http://") or url.startswith("https://")):
                continue
            if url in seen:
                continue
            seen.add(url)
            title = (l.title or "Tin tham khảo").strip()[:80]
            price = f" — {l.price_per_m2:.0f} tr/m²" if l.price_per_m2 else ""
            rows.append(f"{len(rows)+1}. {source}: {title}{price}\n{url}")
            if len(rows) >= max_links:
                break
        if len(rows) >= max_links:
            break
    if not rows:
        return "🔗 Link nguồn kiểm chứng: hiện bot chưa lấy được URL thật từ nguồn, chỉ có dữ liệu/ước lượng. Em sẽ cần nâng scraper để bắt link thật ổn định hơn."
    return "🔗 Link nguồn kiểm chứng:\n" + "\n\n".join(rows)



def _robust_ppm(values: list[float]) -> tuple[float | None, list[float]]:
    vals = sorted(float(v) for v in values if v and 5 <= float(v) <= 2000)
    if not vals:
        return None, []
    if len(vals) >= 4:
        q1 = vals[len(vals)//4]
        q3 = vals[(len(vals)*3)//4]
        iqr = max(q3 - q1, 1)
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        vals = [v for v in vals if lo <= v <= hi]
    # median is safer than mean for listing data
    n = len(vals)
    if n == 0:
        return None, []
    med = vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2
    return med, vals


def _deterministic_project_report(criteria: SearchCriteria, projects, buckets: dict) -> str:
    all_rows = []
    for source, listings in buckets.items():
        for l in listings:
            # Report should show verifiable sources. Ignore AI estimates/no-url rows
            # when building per-project source links and prices.
            if source == "AI estimate" or (not getattr(l, "url", "") and "::" not in source):
                continue
            all_rows.append((source, l))
    lines = ["📍 *Định giá theo dự án/khu vực comparable*", ""]
    for i, prj in enumerate(projects.projects[:5], 1):
        name = prj.get("name", f"Khu vực {i}")
        # Prefer project-scoped buckets produced directly by Playwright search:
        # source format = "Batdongsan.com.vn::<project name>". Those links are
        # exactly from the search done for this project, so no cross-project match.
        scoped = [(src, l) for src, l in all_rows if "::" in src and src.split("::", 1)[1].strip().lower() == name.lower()]
        matched = scoped or [(src, l) for src, l in all_rows if _listing_project_match(name, l.title) or _listing_project_match(name, l.url or "")]
        if not matched:
            lines.append(f"*{i}. {name}*")
            lines.append("- Chưa lấy được mẫu giá trực tiếp từ web cho dự án/khu vực này.")
            lines.append("")
            continue
        prices = [l.price_total for _, l in matched if l.price_total]
        ppms_raw = [l.price_per_m2 for _, l in matched if l.price_per_m2]
        ppm_med, ppms = _robust_ppm(ppms_raw)
        sources = sorted({src.split("::",1)[0] for src, _ in matched})
        urls = []
        seen = set()
        for _, l in matched:
            if l.url and l.url not in seen:
                seen.add(l.url); urls.append(l.url)
            if len(urls) >= 2:
                break
        lines.append(f"*{i}. {name}*")
        lines.append(f"- Số mẫu khớp: {len(matched)}; sau lọc outlier giá/m²: {len(ppms)}")
        if prices:
            lines.append(f"- Giá tổng: {min(prices):.1f}–{max(prices):.1f} tỷ" if len(prices)>1 else f"- Giá tổng: ~{prices[0]:.1f} tỷ")
        else:
            lines.append("- Giá tổng: chưa rõ")
        if ppms:
            avg = sum(ppms)/len(ppms)
            lines.append(f"- Giá/m²: median ~{ppm_med:.0f} tr/m²; TB sau lọc ~{avg:.0f} tr/m²; biên {min(ppms):.0f}–{max(ppms):.0f} tr/m²")
        else:
            lines.append("- Giá/m²: chưa đủ dữ liệu tin cậy")
        lines.append(f"- Nguồn: {', '.join(sources) if sources else 'chưa rõ'}")
        if urls:
            lines.append("- Link kiểm chứng:")
            for j, u in enumerate(urls, 1):
                lines.append(f"  {j}) {u}")
        lines.append("")
    lines.append("_Lưu ý: giá/m² dùng median/TB sau lọc outlier từ tin rao khớp tên dự án/khu vực; cần kiểm chứng pháp lý, diện tích đất/sàn và trạng thái bàn giao từng tin._")
    return "\n".join(lines)[:3900]

async def build_ai_estimate_buckets(ai: NineRouterClient, criteria: SearchCriteria, projects) -> dict:
    """Fallback cuối: AI ước lượng mặt bằng giá, luôn ghi nhãn [ước lượng]."""
    project_names = [p.get("name", "") for p in projects.projects if p.get("name")]
    system = (
        "Bạn là chuyên viên định giá BĐS Việt Nam. Khi không crawl được web do Cloudflare/captcha, "
        "hãy ước lượng thận trọng mặt bằng giá theo khu vực/dự án, và luôn ghi rõ đây là [ước lượng - cần kiểm chứng]. "
        "Không bịa URL cụ thể."
    )
    user = f"""Tiêu chí: {criteria.human_summary}
Khu vực: {projects.area_description}
Dự án/khu vực quanh tọa độ: {project_names}

Hãy ước lượng giá cho từng dự án/khu vực phù hợp nhất.
Trả JSON đúng schema:
{{
  "listings": [
    {{
      "project": "tên dự án/khu vực",
      "price_total_billion_vnd": 12.5,
      "area_m2": 80,
      "price_per_m2_million_vnd": 156.0,
      "note": "[ước lượng - cần kiểm chứng] lý do ngắn"
    }}
  ]
}}

Quy tắc:
- Ưu tiên loại tài sản/đặc tính người dùng chọn.
- Nếu không đủ cơ sở cho giá tổng, vẫn trả price_per_m2_million_vnd.
- Không ghi URL giả.
"""
    try:
        data = await ai.chat_json(system, user, temperature=0.2)
    except Exception as e:
        logger.warning("AI estimate fallback lỗi: %s", e)
        return {}
    from scraper import Listing
    rows = []
    for item in data.get("listings", []) or []:
        try:
            pt = item.get("price_total_billion_vnd")
            area = item.get("area_m2")
            ppm = item.get("price_per_m2_million_vnd")
            pt = float(pt) if pt else None
            area = float(area) if area else None
            ppm = float(ppm) if ppm else None
            if ppm is None and pt and area:
                ppm = pt * 1000 / area
            if pt is None and ppm and area:
                pt = ppm * area / 1000
            if pt is None and ppm is None:
                continue
            rows.append(Listing(
                source="AI estimate",
                title=f"[ước lượng - cần kiểm chứng] {item.get('project','Comparable')} - {item.get('note','')}",
                price_total=pt,
                area=area,
                price_per_m2=ppm,
                url="",
            ))
        except Exception:
            continue
    return {"AI estimate": rows} if rows else {}


async def geocode_project_points(
    ai: NineRouterClient,
    criteria: SearchCriteria,
    projects,
) -> list[MapPoint]:
    """Lấy tọa độ dự án để ghim map. Chỉ nhận điểm có độ tin cậy đủ cao, không dùng ước lượng mơ hồ."""
    project_names = [p.get("name", "") for p in projects.projects[:5] if p.get("name")]
    if not project_names:
        return []
    loc = getattr(criteria, "location_context", {}) or {}
    district = loc.get("district") if isinstance(loc, dict) else None
    city = loc.get("city") if isinstance(loc, dict) else "TP Hồ Chí Minh"
    system = (
        "Bạn là chuyên gia GIS/BĐS Việt Nam. Nhiệm vụ là geocode CHÍNH XÁC các dự án BĐS đã biết. "
        "Không được lấy tọa độ gốc khảo sát làm tọa độ dự án. Không được bịa nếu không chắc. "
        "Nếu không biết tọa độ dự án, bỏ qua dự án đó. Chỉ trả JSON hợp lệ."
    )
    user = f"""Tọa độ gốc khảo sát: {criteria.lat}, {criteria.lng}
Khu vực bắt buộc: {district or ''}, {city or ''}
Danh sách dự án cần geocode chính xác: {project_names}

Trả JSON schema:
{{
  "points": [
    {{"name": "đúng tên dự án", "lat": 10.0, "lng": 106.0, "confidence": 0.0, "note": "địa chỉ/căn cứ"}}
  ]
}}

Yêu cầu nghiêm ngặt:
- Chỉ trả dự án đúng tên trong danh sách.
- Tọa độ là trung tâm dự án/toà nhà, không phải tọa độ khảo sát.
- confidence >= 0.75 nếu biết rõ địa chỉ/tọa độ.
- Nếu chỉ là ước lượng theo khu vực/phường/quận thì KHÔNG trả điểm đó.
- Tọa độ phải nằm gần khu vực {district or projects.area_description}, {city or ''}.
"""
    try:
        data = await ai.chat_json(system, user, temperature=0.0)
    except Exception as e:
        logger.warning("Geocode project points lỗi: %s", e)
        return []

    def _dist_km(a_lat, a_lng, b_lat, b_lng):
        import math
        r=6371.0; p1=math.radians(a_lat); p2=math.radians(b_lat)
        dp=math.radians(b_lat-a_lat); dl=math.radians(b_lng-a_lng)
        x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*r*math.atan2(math.sqrt(x), math.sqrt(1-x))

    out: list[MapPoint] = []
    allowed = {n.strip().lower(): n for n in project_names}
    for item in data.get("points", []) or []:
        try:
            raw_name = str(item.get("name", "")).strip()
            lat = float(item.get("lat")); lng = float(item.get("lng"))
            conf = float(item.get("confidence", 0) or 0)
            note = str(item.get("note", ""))[:160]
            if not (8 <= lat <= 24 and 102 <= lng <= 110):
                continue
            # Không nhận điểm quá thiếu tin cậy/ước lượng mơ hồ.
            if conf < 0.75 or "ước lượng" in note.lower() or "uoc luong" in note.lower():
                continue
            # Không nhận điểm trùng/sát bất thường với tọa độ khảo sát, trừ khi note nêu đúng địa chỉ dự án rất rõ.
            if _dist_km(criteria.lat, criteria.lng, lat, lng) < 0.05 and raw_name.lower() not in (projects.area_description or '').lower():
                continue
            # Match tên trả về với danh sách gốc.
            canon = None
            for low, orig in allowed.items():
                if low in raw_name.lower() or raw_name.lower() in low:
                    canon = orig; break
            if not canon:
                continue
            out.append(MapPoint(name=canon[:80], lat=lat, lng=lng, note=f"conf={conf:.2f}; {note}"))
        except Exception:
            continue
    return out[:5]


async def build_project_price_report(
    ai: NineRouterClient,
    criteria: SearchCriteria,
    projects,
    buckets: dict,
) -> str:
    """Deterministic report: avoid AI math mistakes/mixing unrelated listings."""
    return _deterministic_project_report(criteria, projects, buckets)


async def build_project_price_report_ai_unused(
    ai: NineRouterClient,
    criteria: SearchCriteria,
    projects,
    buckets: dict,
) -> str:
    """Legacy AI report kept unused as backup."""
    flat = []
    for source, listings in buckets.items():
        for l in listings:
            flat.append({
                "source": source,
                "title": l.title,
                "price_total_billion_vnd": l.price_total,
                "area_m2": l.area,
                "price_per_m2_million_vnd": l.price_per_m2,
                "url": l.url,
            })

    project_names = [p.get("name", "") for p in projects.projects if p.get("name")]
    system = (
        "Bạn là chuyên viên định giá BĐS. Nhiệm vụ của bạn là gom dữ liệu tin rao "
        "theo dự án/khu vực comparable, rồi liệt kê từng dự án/khu vực có giá bao nhiêu. "
        "Không báo cáo theo website/nguồn. Chỉ dùng nguồn web như bằng chứng tham khảo."
    )
    user = f"""Tiêu chí: {criteria.human_summary}
Khu vực: {projects.area_description}
5 dự án/khu vực AI đã chọn: {project_names}

Dữ liệu tin rao thu thập được từ nhiều nguồn:
{flat}

Hãy trả lời bằng tiếng Việt, format Telegram Markdown, ngắn gọn nhưng đủ ý.

Yêu cầu output BẮT BUỘC:
1. Tiêu đề: 📍 Định giá theo dự án/khu vực comparable.
2. PHẢI liệt kê đủ 5 dự án/khu vực AI đã chọn, theo đúng thứ tự trong {project_names}.
3. Với từng dự án/khu vực:
   - Nếu có mẫu giá khớp tên/khu vực: ghi số mẫu, giá thấp-cao, trung bình/trung vị, giá/m² trung bình, link kiểm chứng.
   - Nếu chưa có mẫu giá khớp: ghi rõ "Chưa lấy được mẫu giá trực tiếp từ web cho dự án này"; không được thay bằng giá của dự án khác.
4. Không được dùng dữ liệu Vạn Phúc để lấp cho Him Lam, Phạm Văn Đồng, Linh Đông... nếu title/url không khớp.
5. Không thống kê kiểu 'Batdongsan trung bình bao nhiêu, Guland trung bình bao nhiêu'.
6. Nếu dữ liệu là ước lượng, ghi rõ '[ước lượng]'.
7. Kết thúc bằng 2-3 dòng nhận xét: dự án nào gần nhất/hợp lý nhất, biên giá tham khảo, lưu ý pháp lý/quy hoạch.
"""
    try:
        text = await ai.chat(system, user, temperature=0.2)
    except Exception as e:
        logger.warning("AI project report lỗi: %s", e)
        return _fallback_project_report(criteria, projects, buckets)

    if len(text) > 3900:
        text = text[:3850] + "\n…"
    return text


def _fallback_project_report(criteria: SearchCriteria, projects, buckets: dict) -> str:
    """Fallback đơn giản nếu AI report lỗi."""
    all_rows = []
    for source, listings in buckets.items():
        for l in listings:
            all_rows.append(l)
    lines = ["📍 *Định giá theo dự án/khu vực comparable*", ""]
    if not all_rows:
        lines.append("Chưa có mẫu giá đủ tin cậy từ các nguồn.")
    else:
        for i, p in enumerate(projects.projects[:5], 1):
            name = p.get("name", f"Khu vực {i}")
            matched = [l for l in all_rows if name.lower() in (l.title or "").lower()]
            sample = matched or all_rows[max(0, i-1):i]
            prices = [l.price_total for l in sample if l.price_total]
            ppm = [l.price_per_m2 for l in sample if l.price_per_m2]
            sources = sorted({l.source for l in sample})
            if prices:
                price_txt = f"{min(prices):.1f}–{max(prices):.1f} tỷ" if len(prices) > 1 else f"~{prices[0]:.1f} tỷ"
            else:
                price_txt = "chưa rõ"
            ppm_txt = f"~{sum(ppm)/len(ppm):.0f} tr/m²" if ppm else "chưa rõ"
            lines.append(f"*{i}. {name}*")
            lines.append(f"- Số mẫu: {len(sample)}")
            lines.append(f"- Giá tham khảo: {price_txt}")
            lines.append(f"- Giá/m² TB: {ppm_txt}")
            lines.append(f"- Nguồn: {', '.join(sources) if sources else 'chưa rõ'}")
            lines.append("")
    lines.append("_Lưu ý: kết quả chỉ là tham khảo, cần kiểm chứng từng tin và pháp lý/quy hoạch._")
    return "\n".join(lines)[:3900]


# ---------- main ----------
def build_application() -> Application:
    settings = load_settings()
    ai = NineRouterClient(
        api_key=settings.nineouter_api_key,
        base_url=settings.nineouter_base_url,
        model=settings.nineouter_model,
        timeout=settings.ai_timeout,
    )

    app = Application.builder().token(settings.telegram_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["ai"] = ai
    app.bot_data["ai_fast"] = make_role_client(ai, settings.fast_api_key, settings.fast_base_url, settings.fast_model, settings.ai_fast_timeout)
    app.bot_data["ai_bds"] = make_role_client(ai, settings.bds_api_key, settings.bds_base_url, settings.bds_model, settings.ai_timeout)
    app.bot_data["ai_report"] = make_role_client(ai, settings.report_api_key, settings.report_base_url, settings.report_model, settings.ai_timeout)

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("gia", cmd_gia))
    app.add_handler(CallbackQueryHandler(on_callback))
    return app


def main() -> None:
    if not acquire_single_instance_lock():
        return
    app = build_application()
    logger.info("Bot started, polling…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main_webhook(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run local webhook receiver. Requires Telegram setWebhook to public HTTPS URL."""
    if not acquire_single_instance_lock():
        return
    tg_app = build_application()
    web = Flask(__name__)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(tg_app.initialize())
    loop.run_until_complete(tg_app.start())

    @web.get("/health")
    def health():
        return {"ok": True, "mode": "webhook"}

    @web.post("/telegram/webhook")
    def telegram_webhook():
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        loop.run_until_complete(tg_app.process_update(update))
        return jsonify(ok=True)

    logger.info("Bot webhook receiver started on http://%s:%s/telegram/webhook", host, port)
    web.run(host=host, port=port, threaded=False)


if __name__ == "__main__":
    if os.getenv("BDS_BOT_MODE", "polling").lower() == "webhook":
        main_webhook(host=os.getenv("BDS_WEBHOOK_HOST", "127.0.0.1"), port=int(os.getenv("BDS_WEBHOOK_PORT", "8765")))
    else:
        main()
