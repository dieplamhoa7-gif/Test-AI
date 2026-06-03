// Telegram MVP bot for B─ÉS planning reports.
// Usage:
//   $env:TELEGRAM_BOT_TOKEN="<token>"; node bds_planning_bot.js
// Optional:
//   $env:BDS_ALLOWED_CHAT_IDS="-5161160484"  # comma-separated allowlist
//
// The bot watches Telegram messages containing coordinates / map links and replies
// with a planning report using bds_planning_checker.js.

const fs = require('fs');
const { parseCoordinateInput, lookupHcmPlanning, lookupGulandPriceStats, summarize, toMarkdown } = require('./bds_planning_checker');
let parseGulandPopupText = () => null;
let formatGulandPopup = () => '';
try { ({ parseGulandPopupText, formatGulandPopup } = require('./guland_popup_parser')); } catch (e) { console.error('[guland_popup_parser] load failed:', e && e.message || e); }
const { parseQhVietPopupText, formatQhVietPopup } = require('./qhviet_popup_parser');
const { searchBatdongsanComparables } = require('./batdongsan_price_search');
const { collectApartmentProjectValuations, formatApartmentProjectValuationReport, projectsToMapPoints } = require('./apartment_project_valuation');
const { repairMojibake } = require('./mojibake_repair');
const { lookupK1LandFee } = require('./k1_land_fee_lookup');
let planningBrowserPopups = null;
try { planningBrowserPopups = require('./planning_browser_popups'); } catch (_) {}
let mapScreenshot = null;
try { mapScreenshot = require('./map_screenshot'); } catch (e) { console.error('[map_screenshot] load failed:', e && e.message || e); }

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ALLOWED_CHAT_IDS = (process.env.BDS_ALLOWED_CHAT_IDS || '')
  .split(',')
  .map(s => s.trim())
  .filter(Boolean);

if (!TOKEN) {
  console.error('Missing TELEGRAM_BOT_TOKEN env var');
  process.exit(2);
}

const API = `https://api.telegram.org/bot${TOKEN}`;
let offset = Number(process.env.BDS_TELEGRAM_OFFSET || 0);
const seen = new Set();
let BOT_USERNAME = null;
const BOT_ALIASES = (process.env.BDS_BOT_ALIASES || 'LHBDS_Bot')
  .split(',')
  .map(s => s.trim().replace(/^@/, '').toLowerCase())
  .filter(Boolean);

function allowed(chatId) {
  return ALLOWED_CHAT_IDS.length === 0 || ALLOWED_CHAT_IDS.includes(String(chatId));
}


function fixKnownBadVietnamese(text) {
  return repairMojibake(String(text ?? ''))
    .replaceAll('GIA BDS', 'GIÁ BĐS')
    .replaceAll('T?a d?', 'Tọa độ')
    .replaceAll('Khu v?c', 'Khu vực')
    .replaceAll('chua ro', 'chưa rõ')
    .replaceAll('Lo?i t�i s?n', 'Loại tài sản')
    .replaceAll('MDSDD', 'MĐSDĐ')
    .replaceAll('V? tr�', 'Vị trí')
    .replaceAll('Ngu?n', 'Nguồn')
    .replaceAll('Gi� tham kh?o', 'Giá tham khảo')
    .replaceAll('Ly do', 'Lý do')
    .replaceAll('S? m?u d�ng d? t�nh', 'Số mẫu dùng để tính')
    .replaceAll('Kho?ng gi�', 'Khoảng giá')
    .replaceAll('Trung b�nh', 'Trung bình')
    .replaceAll('Trung v?', 'Trung vị')
    .replaceAll('B? l?c', 'Bộ lọc')
    .replaceAll('m?u so s�nh uu ti�n c�ng', 'mẫu so sánh ưu tiên cùng')
    .replaceAll('du?ng', 'đường')
    .replaceAll('m?t ti?n', 'mặt tiền')
    .replaceAll('h?m', 'hẻm')
    .replaceAll('c�ch', 'cách')
    .replaceAll('D?t', 'Đất')
    .replaceAll('Nh�', 'Nhà')
    .replaceAll('Chung cu', 'Chung cư')
    .replaceAll('Kho/xu?ng', 'Kho/xưởng')
    .replaceAll('Shophouse/m?t b?ng', 'Shophouse/mặt bằng')
    .replaceAll('Anh ch?n lo?i t�i s?n d? em l?c gi�', 'Anh chọn loại tài sản để em lọc giá')
    .replaceAll('Lo?i t�i s?n', 'Loại tài sản')
    .replaceAll('QH Vi?t', 'QH Việt')
    .replaceAll('uu ti�n', 'ưu tiên')
    .replaceAll('Ch? ti�u � ch?c nang', 'Chỉ tiêu ô chức năng')
    .replaceAll('Chua d?c du?c th�ng tin quy ho?ch chi ti?t', 'Chưa đọc được thông tin quy hoạch chi tiết')
    .replaceAll('D�ng /gi� d? tra gi� ri�ng', 'Dùng /giá để tra giá riêng')
    .replaceAll('Popup t? d?ng', 'Popup tự động');
}

function sanitizeExtra(extra = {}) {
  if (!extra || typeof extra !== 'object') return extra;
  const out = JSON.parse(JSON.stringify(extra));
  const rows = out.reply_markup?.inline_keyboard;
  if (Array.isArray(rows)) {
    for (const row of rows) for (const btn of row) if (btn && typeof btn.text === 'string') btn.text = fixKnownBadVietnamese(btn.text);
  }
  return out;
}

function cleanTelegramMarkdown(text) {
  // Keep simple bold markers for important prices; strip only fragile chars.
  return fixKnownBadVietnamese(text).replace(/[_`\[]/g, '');
}

async function resolveShortMapLinks(text) {
  const urls = String(text || '').match(/https?:\/\/(?:maps\.app\.goo\.gl|goo\.gl\/maps)\/\S+/gi) || [];
  let out = text;
  for (const rawUrl of urls) {
    const url = rawUrl.replace(/[)\].,]+$/, '');
    try {
      const res = await fetch(url, { redirect: 'manual', headers: { 'User-Agent': 'Mozilla/5.0' } });
      const loc = res.headers.get('location');
      if (loc) out += `\n${loc}`;
    } catch (_) {}
  }
  return out;
}

const pendingPriceRequests = new Map();
const pendingK1Requests = new Map();

function commandKind(text) {
  const s = String(text || '').trim().toLowerCase();
  const first = s.split(/\s+/)[0].replace(/@\w+$/, '');
  // Accept /gia, /giá, and mojibake/replacement variants like /gi�.
  if (first === '/gi' || first.startsWith('/gia') || first.startsWith('/giá') || first.startsWith('/gi├') || first.startsWith('/gi�')) return 'price';
  if (first === 'tc' || first.startsWith('/tc')) return 'k1';
  if (first.startsWith('/k1') || first.startsWith('/tiendat') || first.startsWith('/tiềnđất') || first.startsWith('/tien')) return 'k1';
  if (first.startsWith('/qh')) return 'planning';
  return null;
}

function mentionNames() {
  return [BOT_USERNAME, ...BOT_ALIASES].filter(Boolean).map(s => String(s).replace(/^@/, '').toLowerCase());
}

function botWasMentioned(text, entities = []) {
  const s = String(text || '');
  const names = mentionNames();
  return names.some(name => new RegExp(`@${name}\\b`, 'i').test(s)) || entities.some(e => {
    if (e.type !== 'mention') return false;
    const mentioned = s.slice(e.offset, e.offset + e.length).replace(/^@/, '').toLowerCase();
    return names.includes(mentioned);
  });
}

function stripBotMention(text) {
  let out = String(text || '');
  for (const name of mentionNames()) out = out.replace(new RegExp(`@${name}\\b`, 'ig'), '');
  return out.trim();
}

function formatMoneyBillion(v) {
  return Number.isFinite(v) ? `${v.toFixed(2)} tỷ` : '-';
}

function fmtAreaShort(v) {
  return Number.isFinite(v) ? `${Number(v).toLocaleString('vi-VN', { maximumFractionDigits: 1 })} m2` : '-';
}

function formatBatdongsanReport(result) {
  const rows = result?.comparables || [];
  if (!rows.length) return 'Mẫu so sánh từ nguồn ngoài\n- Chưa tìm được mẫu phù hợp.';
  return [
    'Mẫu so sánh từ nguồn ngoài',
    ...rows.slice(0, 6).map((r, i) => [
      `${i + 1}. Đường: ${r.road_name || '-'}`,
      `   Diện tích: ${fmtAreaShort(r.area_m2)} | Tổng tiền: ${formatMoneyBillion(r.total_billion)} | Giá/m2: ${Number.isFinite(r.price_million_m2) ? `*${fmtPrice(r.price_million_m2)}*` : '-'}`,
      `   MĐSDĐ: ${r.land_use_code || 'chưa rõ'} | Vị trí: ${r.position || 'chưa rõ'} | Loại: ${r.asset_type || '-'}`,
      `   Nguồn: ${r.source || 'web'}${r.url ? ` - ${r.url}` : ''}`,
    ].filter(Boolean).join('\n')),
    result?.url ? `Nguồn search: ${result.url}` : null,
  ].filter(Boolean).join('\n');
}

function assetLabel(code) {
  return ({ land: 'Đất', house: 'Nhà', apartment: 'Chung cư', factory: 'Kho/xưởng', shophouse: 'Shophouse/mặt bằng' })[code] || code || 'chưa chọn';
}
function positionLabel(code) {
  return ({ frontage: 'Mặt tiền', alley: 'Hẻm', corner: 'Căn góc/2 mặt tiền', any: 'Bỏ qua' })[code] || code || 'chưa chọn';
}
function positionTraitsForCode(code) {
  if (code === 'frontage') return ['mặt tiền/kinh doanh'];
  if (code === 'alley') return ['hẻm/ngõ'];
  if (code === 'corner') return ['căn góc/2 mặt tiền'];
  return [];
}


function normalizeViText(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/─æ/g, 'd').replace(/─É/g, 'D').toLowerCase();
}


function formatGeoAddress(loc) {
  if (!loc) return 'chưa xác định';
  return [
    loc.road ? `Đường geocode: ${loc.road}` : null,
    loc.nearest_road?.name ? `Đường gần nhất: ${loc.nearest_road.name} (~${Math.round(loc.nearest_road.distance_m)}m)` : null,
    loc.nearest_pois?.length ? `POI/dự án gần: ${loc.nearest_pois.slice(0, 3).map(p => `${p.name} ~${Math.round(p.distance_m)}m`).join('; ')}` : null,
    loc.neighbourhood ? `Khu phố: ${loc.neighbourhood}` : null,
    (loc.ward || loc.suburb) ? `Phường/xã: ${loc.ward || loc.suburb}` : null,
    loc.district ? `Quận/huyện/TP: ${loc.district}` : null,
    (loc.city || loc.state) ? `Tỉnh/TP: ${loc.city || loc.state}` : null,
    loc.display_name ? `Full: ${loc.display_name}` : null,
  ].filter(Boolean).join('\n');
}

function extractGeoField(raw, label) {
  const m = String(raw || '').match(new RegExp(label + ':\s*([^\n;]+)', 'i'));
  return m?.[1]?.replace(/~\d+.*$/,'').trim() || '';
}

function compactBdsLocationFromGeo(loc = {}) {
  const city = loc.state || loc.city || '';
  const district = loc.district || loc.city || '';
  const ward = loc.ward || loc.suburb || loc.neighbourhood || '';
  const road = loc.road || loc.nearest_road?.name || '';
  const pois = (loc.nearest_pois || []).map(p => p.name).filter(Boolean);
  const project = [loc.road, ...pois].find(x => /commerce|khu đô thị|khu do thi|residence|apartment|lotus|camellia|palace/i.test(x || '')) || '';
  return [project, road, ward, district, city]
    .filter(Boolean)
    .filter((v, i, a) => a.findIndex(x => normalizeViText(x) === normalizeViText(v)) === i)
    .slice(0, 5)
    .join(' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function enrichLocationForBdsSearch(...texts) {
  const raw = texts.filter(Boolean).join(' ');
  const norm = normalizeViText(raw);
  const roads = [
    ['vo van ngan', 'Võ Văn Ngân'], ['huynh van nghe', 'Huỳnh Văn Nghệ'],
    ['vo nguyen giap', 'Võ Nguyên Giáp'], ['nguyen van thoai', 'Nguyễn Văn Thoại'],
    ['nguyen trung truc', 'Nguyễn Trung Trực'], ['tran phu', 'Trần Phú'],
    ['dang van bi', 'Đặng Văn Bi'], ['kha van can', 'Kha Vạn Cân'],
    ['pham van dong', 'Phạm Văn Đồng'], ['le van viet', 'Lê Văn Việt'],
  ];
  const areas = [
    ['hai phong|le chan|kenh duong|hoang huy commerce', 'Kênh Dương Lê Chân Hải Phòng'],
    ['da nang|ngu hanh son|son tra', 'Đà Nẵng'],
    ['rach gia|kien giang', 'Rạch Giá Kiên Giang'],
    ['binh trung', 'Bình Trưng Thủ Đức TP HCM'], ['binh tho', 'Bình Thọ Thủ Đức TP HCM'],
    ['lai thieu|thuan an|binh hoa', 'Lái Thiêu Thuận An Bình Dương'],
    ['bien hoa|dong nai|tran bien|buu long', 'Biên Hòa Đồng Nai'],
    ['ho chi minh|tp hcm|tphcm', 'TP HCM'],
  ];
  const knownRoad = roads.find(([k]) => norm.includes(k))?.[1] || '';
  const nearestRoadMatch = raw.match(new RegExp('Đường gần nhất:\s*([^~\n;]+)', 'i'));
  const geoRoadMatch = raw.match(new RegExp('Đường geocode:\s*([^\n;]+)', 'i'));
  const road = knownRoad || nearestRoadMatch?.[1]?.trim() || geoRoadMatch?.[1]?.trim() || '';
  const poi = extractGeoField(raw, 'POI/dự án gần').split('~')[0].trim();
  const area = areas.find(([k]) => new RegExp(k).test(norm))?.[1] || '';
  return [poi, road, area].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim() || raw.replace(/\s+/g, ' ').trim();
}

function buildBdsSearchLocation(locationText = '') {
  const raw = String(locationText || '');
  const cleaned = raw
    .replace(/-?\d{1,2}\.\d+\s*,\s*-?\d{2,3}\.\d+/g, ' ')
    .replace(/@LHBDS_Bot/ig, ' ')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  // Prefer specific road/ward/neighbourhood. Do not collapse "B├¼nh Tr╞░ng Thß╗º ─Éß╗⌐c"
  // to only "Thß╗º ─Éß╗⌐c", because that makes evidence too far away.
  const norm = normalizeViText(cleaned);
  const roadMatch = cleaned.match(/(?:─æ╞░ß╗¥ng|duong)?\s*(V├╡ V─ân Ng├ón|Huß╗│nh V─ân Nghß╗ç|─Éß║╖ng V─ân Bi|Kha Vß║ín C├ón|Phß║ím V─ân ─Éß╗ông|L├¬ V─ân Viß╗çt|Nguyß╗àn Duy Trinh|Nguyß╗àn Xiß╗ân|Mai Ch├¡ Thß╗ì)/i);
  const areaPatterns = [
    ['binh trung', 'B├¼nh Tr╞░ng Thß╗º ─Éß╗⌐c TP HCM'],
    ['binh tho', 'B├¼nh Thß╗ì Thß╗º ─Éß╗⌐c TP HCM'],
    ['truong tho', 'Tr╞░ß╗¥ng Thß╗ì Thß╗º ─Éß╗⌐c TP HCM'],
    ['an phu', 'An Ph├║ Thß╗º ─Éß╗⌐c TP HCM'],
    ['thao dien', 'Thß║úo ─Éiß╗ün Thß╗º ─Éß╗⌐c TP HCM'],
    ['linh dong', 'Linh ─É├┤ng Thß╗º ─Éß╗⌐c TP HCM'],
    ['linh chieu', 'Linh Chiß╗âu Thß╗º ─Éß╗⌐c TP HCM'],
    ['lai thieu|thuan an|binh hoa', 'L├íi Thi├¬u Thuß║¡n An TP HCM'],
  ];
  const area = areaPatterns.find(([pat]) => new RegExp(pat).test(norm))?.[1] || '';
  if (roadMatch && area) return `${roadMatch[1]} ${area}`;
  if (area) return area;
  const cityMatch = cleaned.match(/(Thß╗º ─Éß╗⌐c|TP\.??\s*Hß╗ô Ch├¡ Minh|Hß╗ô Ch├¡ Minh|TPHCM|TP HCM|─Éß╗ông Nai|Bi├¬n H├▓a|Trß║Ñn Bi├¬n|Bß╗¡u Long|Kh├ính H├▓a|Nha Trang)/i);
  if (roadMatch && cityMatch) return `${roadMatch[1]} ${cityMatch[1]}`;
  if (roadMatch) return roadMatch[1];
  if (cityMatch) return cityMatch[1];
  return cleaned;
}

function landUseTraitsForCode(code) {
  const c = String(code || '').toUpperCase();
  if (c === 'ODT') return ['MĐSDĐ ─æß║Ñt ß╗ƒ/thß╗ò c╞░'];
  if (c === 'TMD' || c === 'TMDV') return ['MĐSDĐ TMDV/hß╗ùn hß╗úp'];
  if (c === 'SKC') return ['MĐSDĐ SKC/sß║ún xuß║Ñt'];
  if (c === 'CLN') return ['MĐSDĐ CLN/─æß║Ñt v╞░ß╗¥n'];
  if (c === 'NN') return ['MĐSDĐ n├┤ng nghiß╗çp'];
  return [];
}

function looksLikePlanningRequest(text) {
  if (!text) return false;
  const lower = text.toLowerCase();
  if (/google\.com\/maps|maps\.app\.goo\.gl|q=\-?\d|@?\-?\d+\.\d+[,\s]+\d+\.\d+/.test(text)) return true;
  if (/thongtinquyhoach\.hochiminhcity\.gov\.vn|sqhkt-qlqh\.tphcm\.gov\.vn/i.test(text)) return true;
  return /(quy hoß║ích|qh|tß╗ìa ─æß╗Ö|toa do|m─æxd|hssd|tß║ºng cao|d├ón sß╗æ|mß╗Ñc ─æ├¡ch)/i.test(lower) && /\d+\.\d+/.test(text);
}

async function tg(method, payload) {
  const res = await fetch(`${API}/${method}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {}),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok || !data?.ok) throw new Error(`${method} failed: ${res.status} ${JSON.stringify(data)}`);
  return data.result;
}

// Send a PNG buffer as Telegram photo via multipart/form-data.
async function sendPhoto(chatId, pngBuffer, caption, replyTo) {
  const fd = new FormData();
  fd.append('chat_id', String(chatId));
  if (caption) fd.append('caption', String(caption).slice(0, 1000));
  if (replyTo) fd.append('reply_parameters', JSON.stringify({ message_id: replyTo }));
  fd.append('photo', new Blob([pngBuffer], { type: 'image/png' }), 'map.png');
  const res = await fetch(`${API}/sendPhoto`, { method: 'POST', body: fd });
  const data = await res.json().catch(() => null);
  if (!res.ok || !data?.ok) throw new Error(`sendPhoto failed: ${res.status} ${JSON.stringify(data)}`);
  return data.result;
}

// Fire-and-forget multi-pin map screenshot.
//   - 1st arg can be (chatId, lat, lon, replyTo, label) for single-pin back-compat
//     OR (chatId, points, replyTo, label) where points = [{lat,lon,label?}, ...]
//   - Multi-pin: fitBounds với padding 15% mỗi cạnh → bounding box 5 pins chiếm ~70% ảnh.
//   - Single-pin: zoom 18 mặc định.
// Never throws — only logs on failure so it never blocks the text reply.
// Skip entirely if BDS_DISABLE_MAP_SCREENSHOT=1.
async function trySendMapScreenshot(chatId, a, b, c, d) {
  if (process.env.BDS_DISABLE_MAP_SCREENSHOT === '1') return;
  if (!mapScreenshot) { console.error('[map] module not loaded'); return; }
  // Normalize arguments: detect whether 2nd arg is points array or numeric lat
  let points, replyTo, label;
  if (Array.isArray(a)) {
    points = a; replyTo = b; label = c;
  } else {
    points = [{ lat: Number(a), lon: Number(b), label: '📍' }];
    replyTo = c; label = d;
  }
  if (!points.length) return;
  try {
    console.log(`[map] capture ${points.length} pin(s): ${points.map(p => p.lat+','+p.lon).join(' | ')}`);
    const t0 = Date.now();
    const png = await mapScreenshot.captureMultiPinMapAt(points, { width: 1920, height: 1080, zoom: 18, paddingPct: 0.15, mode: 'satellite' });
    console.log(`[map] captured ${png.length} bytes in ${Date.now() - t0}ms`);
    const captionLines = [
      label || '📍 Bản đồ vị trí',
      points.length === 1
        ? `Tọa độ: ${points[0].lat}, ${points[0].lon}`
        : `${points.length} điểm — bounding box ~70% ảnh, padding 15%`,
      points.length > 1 ? points.slice(0, 8).map((p, i) => `${i+1}. ${p.label || '(không tên)'} — ${p.lat}, ${p.lon}`).join('\n') : null,
    ].filter(Boolean);
    await sendPhoto(chatId, png, captionLines.join('\n'), replyTo);
    console.log('[map] photo sent OK');
  } catch (err) {
    console.error('[map] capture/send failed:', err && err.message || err);
  }
}

async function sendPhotoFile(chatId, filePath, caption, replyTo) {
  const fd = new FormData();
  fd.append('chat_id', String(chatId));
  if (caption) fd.append('caption', String(caption).slice(0, 1000));
  if (replyTo) fd.append('reply_parameters', JSON.stringify({ message_id: replyTo }));
  const buf = fs.readFileSync(filePath);
  fd.append('photo', new Blob([buf], { type: 'image/png' }), 'k1_evidence.png');
  const res = await fetch(`${API}/sendPhoto`, { method: 'POST', body: fd });
  const data = await res.json().catch(() => null);
  if (!res.ok || !data?.ok) throw new Error(`sendPhotoFile failed: ${res.status} ${JSON.stringify(data)}`);
  return data.result;
}

async function sendMessage(chatId, text, replyTo, extra = {}) {
  const chunks = [];
  while (text.length > 3900) {
    chunks.push(text.slice(0, 3900));
    text = text.slice(3900);
  }
  chunks.push(text);
  for (const chunk of chunks) {
    await tg('sendMessage', {
      chat_id: chatId,
      text: cleanTelegramMarkdown(chunk),
      parse_mode: 'Markdown',
      reply_parameters: replyTo ? { message_id: replyTo } : undefined,
      disable_web_page_preview: true,
      ...sanitizeExtra(extra),
    });
  }
}

function fmtPrice(v) {
  return Number.isFinite(v) ? `${v.toFixed(2)} tr/m2` : 'chưa có';
}

function formatPriceReport(priceStats) {
  if (!priceStats || !priceStats.sample_count) {
    return [
      'Giá tham khảo Guland',
      '- Chưa lấy được mẫu giá quanh khu vực.',
      priceStats?.error ? `- Lý do: ${priceStats.error}` : null,
    ].filter(Boolean).join('\n');
  }
  return [
    'Giá tham khảo Guland',
    `- Số mẫu dùng để tính: ${priceStats.sample_count}`,
    `- Khoảng giá: *${fmtPrice(priceStats.min_million_m2)} - ${fmtPrice(priceStats.max_million_m2)}*`,
    `- Trung bình: *${fmtPrice(priceStats.avg_million_m2)}*`,
    `- Trung vị: *${fmtPrice(priceStats.median_million_m2)}*`,
    priceStats.filter_note ? `- Bộ lọc: ${priceStats.filter_note}` : null,
    '3 mẫu so sánh ưu tiên cùng MĐSDĐ + cùng đường + cùng mặt tiền/hẻm:',
    ...(priceStats.comparable_positions || []).map((p, idx) => {
      const r = p.representative || {};
      const range = p.sample_count > 1 ? `; khoảng ${fmtPrice(p.min_million_m2)}-${fmtPrice(p.max_million_m2)}` : '';
      const road = p.road_name ? `; đường ${p.road_name}` : '';
      const traits = p.traits?.length ? `; ${p.traits.join(', ')}` : '';
      const src = r.source_url ? `\n   Link: ${r.source_url}` : '';
      return `${idx + 1}. *${fmtPrice(p.price_million_m2)}*; cách ~${Math.round(p.distance_m)}m${road}${traits}${range}\n   ${String(r.title || '').slice(0, 120)}${src}`;
    }).filter(Boolean),
  ].filter(x => x !== null).join('\n');
}

function fmtArea(v) {
  return Number.isFinite(Number(v)) ? `${Number(v).toLocaleString('vi-VN', { maximumFractionDigits: 2 })} m2` : '-';
}

function formatParcelHeader(summary, ...parsedSources) {
  const parcel = parsedSources.map(x => x?.parcel).find(p => p && (p.map_sheet || p.parcel_no || p.area_m2 || p.old_area || p.new_area)) || {};
  return [
    'Thông tin thửa',
    parcel.map_sheet ? `- Số tờ: ${parcel.map_sheet}` : null,
    parcel.parcel_no ? `- Số thửa: ${parcel.parcel_no}` : null,
    parcel.area_m2 ? `- Diện tích thửa: ${fmtArea(parcel.area_m2)}` : null,
    parcel.old_area ? `- Khu vực cũ: ${parcel.old_area}` : null,
    parcel.new_area ? `- Khu vực mới: ${parcel.new_area}` : null,
    !parcel.old_area && !parcel.new_area && summary.location?.display_name ? `- Khu vực: ${summary.location.display_name}` : null,
  ].filter(Boolean).join('\n');
}

function getLandRows(parsed) {
  const landRows = parsed?.land_rows || parsed?.parcel?.land_rows || [];
  const planRows = parsed?.planning || [];
  const seenRows = new Set();
  const rows = [];
  for (const r of [...landRows, ...planRows]) {
    const key = [
      String(r.code || '').toUpperCase().trim(),
      String(r.land_use || '').toLowerCase().trim(),
      Number.isFinite(Number(r.area_m2)) ? Number(r.area_m2).toFixed(2) : '',
      String(r.floors || r.building_density || r.far || '').toLowerCase().trim(),
    ].join('|');
    if (seenRows.has(key)) continue;
    seenRows.add(key);
    rows.push(r);
  }
  return rows;
}

function formatSourceBlock(name, parsed, sourceUrl, official = {}) {
  const planRows = parsed?.planning || [];
  const main = planRows.find(p => p.floors || p.building_density || p.far) || planRows[0] || {};
  const rows = getLandRows(parsed);
  const landLines = rows.map(r => `- ${r.code || '-'}: ${fmtArea(r.area_m2)} - ${r.land_use || '-'}`);
  const seenLines = new Set();
  const uniqueLandLines = landLines.filter(line => {
    const key = line.toLowerCase().replace(/\s+/g, ' ').trim();
    if (seenLines.has(key)) return false;
    seenLines.add(key);
    return true;
  });
  return [
    `Theo ${name}`,
    uniqueLandLines.length ? '- MĐSDĐ/chức năng đất:' : null,
    ...uniqueLandLines,
    official.population || main.danso ? `- Dân số: ${official.population || main.danso}` : null,
    official.floors || main.floors ? `- Tầng cao: ${official.floors || main.floors}` : null,
    official.density || main.building_density ? `- MĐXD: ${official.density || main.building_density}` : null,
    official.far || main.far ? `- HSSDĐ: ${official.far || main.far}` : null,
    sourceUrl ? `- Nguồn: ${sourceUrl}` : null,
  ].filter(Boolean).join('\n');
}

function comparePlanningSources(guland, qhviet) {
  if (!guland || !qhviet) return null;
  const norm = rows => new Set(getLandRows(rows).map(r => `${String(r.code || '').toUpperCase()}|${String(r.land_use || '').toLowerCase()}`));
  const a = norm(guland);
  const b = norm(qhviet);
  if (!a.size || !b.size) return null;
  const onlyA = [...a].filter(x => !b.has(x));
  const onlyB = [...b].filter(x => !a.has(x));
  if (!onlyA.length && !onlyB.length) return 'Kết luận: Quy hoạch Guland giống QH Việt về nhóm chức năng đất đọc được.';
  return 'Kết luận: Quy hoạch Guland khác QH Việt hoặc chưa khớp hoàn toàn về chức năng đất; ưu tiên kiểm tra lại popup đồng điểm và nguồn chính thống.';
}

function buildFinalReport(summary, gulandText, priceStats, qhvietText = null) {
  const p = summary.planning_project;
  const e = summary.exact_indicators;
  const guland = gulandText ? parseGulandPopupText(gulandText) : null;
  const qhviet = qhvietText ? parseQhVietPopupText(qhvietText) : null;
  const officialAsParsed = e.chuc_nang_dat ? { parcel: {}, land_rows: [{ code: e.ma_o_pho || '-', area_m2: e.dien_tich, land_use: e.chuc_nang_dat }] } : null;
  const sourceConclusion = comparePlanningSources(guland, qhviet);
  const inHcm = summary.official_functional_lots?.skipped !== 'outside_hcm';
  const sources = inHcm ? [
    `QHHCM ưu tiên: ${summary.cross_check_links?.hcm_official?.web_url || `https://thongtinquyhoach.hochiminhcity.gov.vn/#/${summary.input.lat}/${summary.input.lon}/18`}`,
    e.source_url ? `Chỉ tiêu ô chức năng: ${e.source_url}` : null,
    e.mixed_source_url ? `Bảng chức năng hỗn hợp: ${e.mixed_source_url}` : null,
    `QH Việt/Guland fallback: ${summary.cross_check_links?.qhviet?.home_url} | ${summary.cross_check_links?.guland?.coordinate_planning_url}`,
  ] : [
    `Guland: ${summary.cross_check_links?.guland?.coordinate_planning_url}`,
    `QH Việt: ${summary.cross_check_links?.qhviet?.home_url}`,
  ];
  return [
    'BÁO CÁO QUY HOẠCH',
    `Tọa độ: ${summary.input.lat}, ${summary.input.lon}`,
    summary.location?.display_name ? `Vị trí: ${summary.location.display_name}` : null,
    '',
    formatParcelHeader(summary, qhviet, guland, officialAsParsed),
    '',
    inHcm && officialAsParsed ? formatSourceBlock('QHHCM', officialAsParsed, e.source_url || summary.cross_check_links?.hcm_official?.web_url, {
      dien_tich: e.dien_tich,
      population: e.dan_so_lo_o_pho || p?.DanSoQH,
      floors: e.tang_cao,
      density: e.mat_do_xay_dung ? `${e.mat_do_xay_dung}%` : null,
      far: e.he_so_su_dung_dat,
      location: summary.location?.display_name,
    }) : null,
    guland ? formatSourceBlock('Guland', guland, summary.cross_check_links?.guland?.coordinate_planning_url, {}) : null,
    qhviet ? formatSourceBlock('QH Việt', qhviet, summary.cross_check_links?.qhviet?.home_url, {}) : null,
    sourceConclusion,
    !guland && !qhviet && !officialAsParsed ? 'Chưa đọc được thông tin quy hoạch chi tiết.' : null,
    '',
    formatPriceReport(priceStats),
    '',
    'Nguồn',
    sources.filter(Boolean).map(x => `- ${x}`).join('\n'),
  ].filter(Boolean).join('\n');
}

async function answerCallbackQuery(id, text = '') {
  if (!id) return;
  await tg('answerCallbackQuery', { callback_query_id: id, text: fixKnownBadVietnamese(text) }).catch(() => null);
}

function buildPlanningReportOnly(summary, gulandText, qhvietText, popupErrors = []) {
  const emptyPrice = { sample_count: 0, error: 'Dùng /giá để tra giá riêng.' };
  let report = buildFinalReport(summary, gulandText, emptyPrice, qhvietText)
    .replace(/\nGiá tham khảo Guland[\s\S]*?\nNguồn\n/, '\nNguồn\n');
  if (!gulandText && !qhvietText) {
    report += '\n\nĐối chiếu popup/browser\n';
    if (popupErrors.length) report += popupErrors.map(x => `- ${x}`).join('\n');
    else report += '- Chưa đọc được popup Guland/QH Việt; báo cáo hiện dùng dữ liệu quy hoạch chính + link đối chiếu.';
  }
  return report;
}

async function askPriceStep(req, key) {
  const selected = [
    req.asset ? `Loại tài sản: ${assetLabel(req.asset)}` : null,
    req.landUse ? `MĐSDĐ: ${req.landUse}` : null,
  ].filter(Boolean).join('\n');
  if (!req.asset) {
    await sendMessage(req.chatId, ['Anh chọn loại tài sản để em lọc giá:', selected].filter(Boolean).join('\n'), req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: 'Đất', callback_data: `price:asset:land:${key}` },
      { text: 'Nhà', callback_data: `price:asset:house:${key}` },
      { text: 'Chung cư', callback_data: `price:asset:apartment:${key}` },
    ], [
      { text: 'Kho/xưởng', callback_data: `price:asset:factory:${key}` },
      { text: 'Shophouse/mặt bằng', callback_data: `price:asset:shophouse:${key}` },
    ]] } });
    return;
  }
  if (!req.landUse) {
    await sendMessage(req.chatId, ['Anh chọn MĐSDĐ:', selected].filter(Boolean).join('\n'), req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: 'ODT', callback_data: `price:land:ODT:${key}` },
      { text: 'TMD', callback_data: `price:land:TMD:${key}` },
      { text: 'SKC', callback_data: `price:land:SKC:${key}` },
      { text: 'CLN', callback_data: `price:land:CLN:${key}` },
      { text: 'NN', callback_data: `price:land:NN:${key}` },
    ]] } });
    return;
  }
}

function detectLandUseCode(text) {
  const s = String(text || '').toUpperCase();
  if (/\bTMD\b|TMDV|THƯƠNG MẠI DỊCH VỤ|THUONG MAI DICH VU/.test(s)) return 'TMD';
  if (/\bSKC\b|SXKD|SẢN XUẤT KINH DOANH|SAN XUAT KINH DOANH/.test(s)) return 'SKC';
  return 'ODT';
}

function detectLandUseCodeFromPlanning(summary, fallbackText = '') {
  const parts = [
    fallbackText,
    summary?.exact_indicators?.chuc_nang_dat,
    ...(summary?.exact_indicators?.mixed_functions || []).map(x => x.chuc_nang_dat),
    ...(summary?.official_functional_lots?.lots || []).map(x => [x.chuc_nang_dat, x.MaChucNang, x.KyHieu].filter(Boolean).join(' ')),
  ].filter(Boolean).join(' ');
  return detectLandUseCode(parts);
}

function formatVnd(v) {
  if (!Number.isFinite(v)) return 'chưa rõ';
  return `${Math.round(v).toLocaleString('vi-VN')} đ`;
}

function formatK1Report(k1) {
  if (!k1 || k1.error) return `K1/tiền đất\n- ${k1?.error || 'Chưa tra được.'}`;
  const c = k1.calc || {};
  const m = k1.match || {};
  return [
    'K1 / TIỀN SỬ DỤNG ĐẤT SƠ BỘ',
    `Tọa độ: ${k1.lat}, ${k1.lon}`,
    `Loại đất tính: ${c.label || k1.landUse}`,
    `Match phụ lục: ${m.wardHeader || 'chưa rõ'} | ${m.road || '-'}`,
    `Thuộc đoạn đường: ${m.segment || '-'}`,
    `Độ tin cậy match đoạn: ${m.confidence || 'medium'}`,
    `Trang dẫn chứng: ${m.page || '-'}`,
    `Đơn giá bảng: ${Number.isFinite(c.baseThousandPerM2) ? c.baseThousandPerM2.toLocaleString('vi-VN') + ' ngàn đ/m2' : '-'}`,
    `Hệ số điều chỉnh mức biến động thị trường: ${Number.isFinite(c.marketK) ? String(c.marketK).replace('.', ',') : '-'}`,
    `Hệ số điều chỉnh quy hoạch: ${Number.isFinite(c.planningK) ? String(c.planningK).replace('.', ',') : '1'} (tạm tính; cần phụ lục/quy hoạch chi tiết nếu áp dụng)`,
    `Hệ số điều chỉnh theo vị trí: ${Number.isFinite(c.positionK) ? String(c.positionK).replace('.', ',') : '1'} (${c.positionK === 1.35 ? 'vị trí 2/3/4' : 'vị trí 1/tạm tính'})`,
    `Tổng hệ số đang dùng: ${Number.isFinite(c.totalK) ? c.totalK.toLocaleString('vi-VN', { maximumFractionDigits: 4 }) : '-'}`,
    `Đơn giá điều chỉnh: ${Number.isFinite(c.adjustedThousandPerM2) ? c.adjustedThousandPerM2.toLocaleString('vi-VN', { maximumFractionDigits: 3 }) + ' ngàn đ/m2' : '-'}`,
    `Tương đương: ${Number.isFinite(c.adjustedMillionPerM2) ? c.adjustedMillionPerM2.toLocaleString('vi-VN', { maximumFractionDigits: 3 }) + ' triệu đ/m2' : '-'}`,
    k1.areaM2 ? `Diện tích nhận từ tin nhắn: ${k1.areaM2} m2` : 'Chưa thấy diện tích m2 trong tin nhắn; bot mới trả đơn giá/m2.',
    Number.isFinite(c.estimatedTotalVnd) ? `Chi phí đất sơ bộ: ${formatVnd(c.estimatedTotalVnd)} (~${c.estimatedTotalBillion.toLocaleString('vi-VN', { maximumFractionDigits: 3 })} tỷ)` : null,
    '',
    'Dẫn chứng dòng phụ lục:',
    `${m.raw || '-'}`,
    m.alternatives?.length ? '' : null,
    m.alternatives?.length ? 'Các đoạn ứng viên khác gần nhất:' : null,
    ...(m.alternatives || []).slice(0, 3).map((a, i) => `${i + 1}. ${a.road} | ${a.segment} | trang ${a.page} | score ${a.score}`),
    '',
    'Lưu ý: đây là ước tính sơ bộ theo bảng giá đất × hệ số K đọc từ phụ lục gần nhất theo tọa độ. Nếu cùng một tên đường có nhiều đoạn, bot đang chọn đoạn có score cao nhất theo geocode/đường gần nhất/POI lân cận; cần đối chiếu hồ sơ vị trí để chốt chính xác.',
  ].filter(Boolean).join('\n');
}

async function runPriceLookup(req) {
  const positionTraits = [];
  const stats = await lookupGulandPriceStats(req.lat, req.lon, {
    landUseTraits: landUseTraitsForCode(req.landUse),
    positionTraits,
    contextText: req.text,
    planningText: [req.landUse, assetLabel(req.asset)].join(' '),
  }).catch(err => ({ error: err.message || String(err), sample_count: 0 }));
  const bdsLocationText = buildBdsSearchLocation(enrichLocationForBdsSearch(formatGeoAddress(req.geoLocation), req.locationText, req.text));

  // Apartment branch: identify ~5 nearby projects + their prices, send report + multi-pin map.
  if (req.asset === 'apartment') {
    console.log(`[price-apartment] lat=${req.lat} lon=${req.lon} geo="${bdsLocationText}"`);
    const projectResult = await collectApartmentProjectValuations({ lat: req.lat, lon: req.lon, geoText: bdsLocationText, limitProjects: 5 })
      .catch(err => ({ error: err.message || String(err), projects: [] }));
    try {
      const summary = (projectResult.projects || []).map(p => `${(p.name || '?').slice(0, 20)}[coords=${p.lat ? 'Y' : 'N'},stat=${p.stats ? p.stats.sample_count : 0}]`).join(' | ');
      console.log(`[price-apartment-result] subject="${projectResult.subject?.area || 'none'}" projects=${(projectResult.projects || []).length} | ${summary}`);
    } catch (_) {}
    await sendMessage(req.chatId, [`GIÁ CHUNG CƯ — ${(projectResult.projects || []).length} DỰ ÁN`, `Tọa độ: ${req.lat}, ${req.lon}`, `Khu vực: ${bdsLocationText || 'chưa rõ'}`, '', formatApartmentProjectValuationReport(projectResult)].join('\n'), req.replyTo);
    // Multi-pin map: tất cả 5 dự án có lat/lon + tọa độ gốc của anh.
    const mapPoints = projectsToMapPoints(projectResult);
    if (mapPoints.length) {
      mapPoints.unshift({ lat: req.lat, lon: req.lon, label: '🎯 Vị trí anh hỏi' });
      trySendMapScreenshot(req.chatId, mapPoints, req.replyTo, `🗺️ ${mapPoints.length - 1} dự án + vị trí anh hỏi`);
    } else {
      trySendMapScreenshot(req.chatId, req.lat, req.lon, req.replyTo, `📍 ${bdsLocationText || 'Vị trí'}`);
    }
    return;
  }

  console.log(`[price] search location="${bdsLocationText}" lat=${req.lat} lon=${req.lon} asset=${req.asset} land=${req.landUse}`);
  const bds = await searchBatdongsanComparables({
    lat: req.lat,
    lon: req.lon,
    locationText: bdsLocationText,
    target: { code: req.landUse, asset: req.asset },
  }).catch(err => ({ error: err.message || String(err), comparables: [] }));
  console.log(`[price] external comparables=${bds.comparables?.length || 0} error=${bds.error || ''} query=${bds.query || ''}`);
  await sendMessage(req.chatId, [`GIÁ BĐS`, `Tọa độ: ${req.lat}, ${req.lon}`, `Khu vực search: ${bdsLocationText || 'chưa rõ'}`, `Loại tài sản: ${assetLabel(req.asset)}`, `MĐSDĐ: ${req.landUse}`, '', formatPriceReport(stats), '', formatBatdongsanReport(bds)].join('\n'), req.replyTo);
  trySendMapScreenshot(req.chatId, req.lat, req.lon, req.replyTo, `📍 ${assetLabel(req.asset)} - ${bdsLocationText || 'Vị trí'}`);
}

async function askK1Step(req, key) {
  if (!req.landUse) {
    await sendMessage(req.chatId, ['Chọn MĐSDĐ để tính tiền đất:', req.locationText ? `Khu vực: ${req.locationText}` : null, req.suggestedLandUse ? `Gợi ý theo quy hoạch đọc được: ${req.suggestedLandUse}` : null].filter(Boolean).join('\n'), req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: 'ODT / Đất ở', callback_data: `k1:land:ODT:${key}` },
      { text: 'TMD / TMDV', callback_data: `k1:land:TMD:${key}` },
      { text: 'SKC / SXKD', callback_data: `k1:land:SKC:${key}` },
    ]] } });
    return;
  }
  if (!req.position) {
    await sendMessage(req.chatId, 'Chọn vị trí tính hệ số:', req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: 'VT1', callback_data: `k1:pos:VT1:${key}` },
      { text: 'VT2/3/4', callback_data: `k1:pos:VT234:${key}` },
    ]] } });
    return;
  }
}

async function runK1Lookup(req) {
  const raw = await lookupHcmPlanning(req.lat, req.lon);
  const summary = summarize(raw);
  req.geoLocation = summary.location || req.geoLocation || null;
  req.locationText = compactBdsLocationFromGeo(summary.location || {});
  const k1 = await lookupK1LandFee({ lat: req.lat, lon: req.lon, geoLocation: summary.location || {}, text: req.text, landUse: req.landUse, position: req.position === 'VT234' ? 'VT234' : 'VT1', planningMultiplier: 1 });
  await sendMessage(req.chatId, formatK1Report(k1), req.replyTo);
  if (k1?.evidencePath) {
    await sendPhotoFile(req.chatId, k1.evidencePath, `Ảnh dẫn chứng phụ lục K1 - trang ${k1.match?.page || ''}`.trim(), req.replyTo).catch(() => null);
  }
}

async function handlePriceSelection(query) {
  const data = String(query.data || '');
  if (data.startsWith('k1:')) {
    const [, step, value, key] = data.split(':');
    const req = pendingK1Requests.get(key);
    if (!req) { await answerCallbackQuery(query.id, 'Yêu cầu K1 đã hết hạn, gửi lại tọa độ giúp em.'); return true; }
    if (step === 'land') req.landUse = value;
    if (step === 'pos') req.position = value;
    await answerCallbackQuery(query.id, 'Đã nhận lựa chọn.');
    if (!req.landUse || !req.position) {
      await askK1Step(req, key);
      return true;
    }
    await answerCallbackQuery(query.id, 'Đang tính tiền đất...');
    await runK1Lookup(req).catch(async err => { await sendMessage(req.chatId, `Em tra K1/tiền đất bị lỗi: ${err.message || err}`, req.replyTo).catch(() => null); });
    pendingK1Requests.delete(key);
    return true;
  }
  if (!data.startsWith('price:')) return false;
  const parts = data.split(':');
  let req;
  if (parts.length === 3) {
    // Backward compatibility with old buttons: price:ODT:key
    const [, code, key] = parts;
    req = pendingPriceRequests.get(key);
    if (!req) { await answerCallbackQuery(query.id, 'Yêu cầu giá đã hết hạn, gửi lại /giá + tọa độ giúp em.'); return true; }
    req.landUse = code;
  } else {
    const [, step, value, key] = parts;
    req = pendingPriceRequests.get(key);
    if (!req) { await answerCallbackQuery(query.id, 'Yêu cầu giá đã hết hạn, gửi lại /giá + tọa độ giúp em.'); return true; }
    if (step === 'asset') req.asset = value;
    if (step === 'land') req.landUse = value;
    if (step === 'pos') req.position = value;
  }
  await answerCallbackQuery(query.id, 'Đã nhận lựa chọn.');
  if (!req.asset || !req.landUse) {
    await askPriceStep(req, parts[parts.length - 1]);
    return true;
  }
  await answerCallbackQuery(query.id, 'Đang tra giá...');
  await runPriceLookup(req);
  pendingPriceRequests.delete(parts[parts.length - 1]);
  return true;
}

async function handleMessage(msg) {
  const chatId = msg.chat?.id;
  if (!chatId || !allowed(chatId)) return;

  const rawText = [msg.text, msg.caption].filter(Boolean).join(' ');
  console.log(`[inbound] chat=${chatId} msg=${msg.message_id} from=${msg.from?.username || msg.from?.id || '-'} text=${JSON.stringify(rawText).slice(0, 500)}`);
  const mentioned = botWasMentioned(rawText, [...(msg.entities || []), ...(msg.caption_entities || [])]);
  const text = stripBotMention(rawText);
  const replyText = msg.reply_to_message ? [msg.reply_to_message.text, msg.reply_to_message.caption].filter(Boolean).join(' ') : '';
  let combinedText = [text, replyText].filter(Boolean).join('\n');
  const lowCombined = normalizeViText(combinedText);
  const kind = commandKind(text) || commandKind(combinedText) || (/\bk1\b|tien su dung dat|tien dat|nghia vu tai chinh|he so dieu chinh/.test(lowCombined) ? 'k1' : 'planning');
  if (!mentioned && !commandKind(combinedText) && !looksLikePlanningRequest(combinedText)) return;
  combinedText = await resolveShortMapLinks(combinedText);

  const parsed = parseCoordinateInput([combinedText]);
  if (!parsed) {
    await sendMessage(chatId, 'Em thấy anh gửi link/nhắc quy hoạch, nhưng chưa đọc được tọa độ lat/lon thật. Link official dạng #/3/1/18 là trạng thái giao diện, không đủ để bot gọi API. Anh gửi tọa độ dạng 10.845790835609225,106.76200727878299 hoặc link Google Maps có tọa độ nhé.', msg.message_id);
    return;
  }

  const key = `${chatId}:${msg.message_id}`;
  if (seen.has(key)) return;
  seen.add(key);

  if (kind === 'k1') {
    await sendMessage(chatId, 'Em nhận tọa độ rồi, đang xác định vị trí để tra K1...', msg.message_id);
    try {
      const raw = await lookupHcmPlanning(parsed.lat, parsed.lon);
      const summary = summarize(raw);
      const reqKey = `${chatId}_${msg.message_id}_k1`;
      const req = { chatId, replyTo: msg.message_id, lat: parsed.lat, lon: parsed.lon, text: combinedText, createdAt: Date.now(), geoLocation: summary.location || null, locationText: compactBdsLocationFromGeo(summary.location || {}) };
      pendingK1Requests.set(reqKey, req);
      await askK1Step(req, reqKey);
      return;
    } catch (err) {
      await sendMessage(chatId, `Em tra K1/tiền đất bị lỗi: ${err.message || err}`, msg.message_id);
      return;
    }
  }

  if (kind === 'price') {
    const reqKey = `${chatId}_${msg.message_id}`;
    const req = { chatId, replyTo: msg.message_id, lat: parsed.lat, lon: parsed.lon, text: combinedText, createdAt: Date.now() };
    try {
      const raw = await lookupHcmPlanning(parsed.lat, parsed.lon);
      const sum = summarize(raw);
      req.geoLocation = sum.location || null;
      req.locationText = compactBdsLocationFromGeo(sum.location || {});
    } catch (_) {}
    pendingPriceRequests.set(reqKey, req);
    await askPriceStep(req, reqKey);
    return;
  }

  await sendMessage(chatId, 'Em nhận tọa độ rồi, đang tra quy hoạch...', msg.message_id);
  try {
    const raw = await lookupHcmPlanning(parsed.lat, parsed.lon);
    const summary = summarize(raw);
    let gulandText = /Tß╗¥\s+\d+\s+Thß╗¡a\s+\d+|Th├┤ng tin quy hoß║ích x├óy dß╗▒ng|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT)\b\s*[\d.,]+\s*m2/i.test(combinedText) ? combinedText : null;
    let qhvietText = /Th├┤ng tin thß╗¡a\s+Sß╗æ tß╗¥\s+\d+\s+Sß╗æ thß╗¡a\s+\d+|Khu vß╗▒c mß╗¢i|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|SON)\b\s+Đất/i.test(combinedText) ? combinedText : null;
    const popupErrors = [];
    const browserPopupsEnabled = process.env.BDS_DISABLE_BROWSER_POPUPS !== '1';
    if (browserPopupsEnabled && !gulandText && planningBrowserPopups?.readGulandPopupText) {
      const got = await planningBrowserPopups.readGulandPopupText(parsed.lat, parsed.lon).catch(err => { popupErrors.push(`Guland popup: ${err.message || err}`); return null; });
      if (got?.text && !got.degraded) gulandText = got.text;
      else if (got?.degraded) popupErrors.push(`Guland popup: ${got.text.split('\n')[0]}`);
    } else if (!gulandText) {
      popupErrors.push('Guland popup: chưa có module reader/parser, đang dùng báo cáo quy hoạch chính + link đối chiếu.');
    }
    if (browserPopupsEnabled && !qhvietText && planningBrowserPopups?.readQhVietPopupText) {
      const got = await planningBrowserPopups.readQhVietPopupText(parsed.lat, parsed.lon, summary.location || {}).catch(err => { popupErrors.push(`QH Việt popup: ${err.message || err}`); return null; });
      if (got?.text && !got.degraded) qhvietText = got.text;
      else if (got?.degraded) popupErrors.push(`QH Việt popup: ${got.text.split('\n')[0]}`);
    } else if (!qhvietText) {
      popupErrors.push('QH Việt popup: chưa có module reader, đang dùng báo cáo quy hoạch chính + link đối chiếu.');
    }
    const planningTraitsText = [
      summary.exact_indicators?.chuc_nang_dat,
      ...(summary.exact_indicators?.mixed_functions || []).map(x => x.chuc_nang_dat),
      gulandText,
      qhvietText,
      combinedText,
    ].filter(Boolean).join(' ');
    let report = buildPlanningReportOnly(summary, gulandText, qhvietText, popupErrors);
    await sendMessage(chatId, report, msg.message_id);

    // Full investor workflow: reuse planning/geocode result, then ask investor to choose MĐSDĐ/position.
    try {
      const reqKey = `${chatId}_${msg.message_id}_k1`;
      const req = { chatId, replyTo: msg.message_id, lat: parsed.lat, lon: parsed.lon, text: combinedText, createdAt: Date.now(), geoLocation: summary.location || null, locationText: compactBdsLocationFromGeo(summary.location || {}) };
      const suggested = detectLandUseCodeFromPlanning(summary, planningTraitsText);
      if (suggested) req.suggestedLandUse = suggested;
      pendingK1Requests.set(reqKey, req);
      await askK1Step(req, reqKey);
    } catch (k1Err) {
      await sendMessage(chatId, `K1/tiền đất: chưa chuẩn bị được bước chọn MĐSDĐ (${k1Err.message || k1Err}).`, msg.message_id).catch(() => null);
    }

    trySendMapScreenshot(chatId, parsed.lat, parsed.lon, msg.message_id, `📍 Quy hoạch tại ${parsed.lat}, ${parsed.lon}`);
  } catch (err) {
    await sendMessage(chatId, `Em tra bị lỗi: ${err.message || err}. Anh gửi lại tọa độ/link giúp em.`, msg.message_id);
  }
}

async function initBotIdentity() {
  try {
    const me = await tg('getMe', {});
    BOT_USERNAME = me?.username || null;
    console.log(`BDS bot identity: @${BOT_USERNAME || 'unknown'}; aliases: ${mentionNames().map(x => '@' + x).join(', ')}`);
  } catch (err) {
    console.error('Could not read bot identity:', err.message || err);
  }
}

async function pollLoop() {
  await initBotIdentity();
  console.log('BĐS planning bot started');
  while (true) {
    try {
      const updates = await tg('getUpdates', { offset, timeout: 35, allowed_updates: ['message', 'callback_query'] });
      for (const update of updates) {
        offset = update.update_id + 1;
        if (update.callback_query) {
          const handled = await handlePriceSelection(update.callback_query);
          if (handled) continue;
        }
        if (update.message) await handleMessage(update.message);
      }
    } catch (err) {
      console.error(new Date().toISOString(), err.message || err);
      await new Promise(r => setTimeout(r, 5000));
    }
  }
}

pollLoop();
