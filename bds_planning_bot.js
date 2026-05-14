// Telegram MVP bot for B─ÉS planning reports.
// Usage:
//   $env:TELEGRAM_BOT_TOKEN="<token>"; node bds_planning_bot.js
// Optional:
//   $env:BDS_ALLOWED_CHAT_IDS="-5161160484"  # comma-separated allowlist
//
// The bot watches Telegram messages containing coordinates / map links and replies
// with a planning report using bds_planning_checker.js.

const { parseCoordinateInput, lookupHcmPlanning, lookupGulandPriceStats, summarize, toMarkdown } = require('./bds_planning_checker');
const { parseGulandPopupText, formatGulandPopup } = require('./guland_popup_parser');
const { parseQhVietPopupText, formatQhVietPopup } = require('./qhviet_popup_parser');
const { searchBatdongsanComparables } = require('./batdongsan_price_search');
let planningBrowserPopups = null;
try { planningBrowserPopups = require('./planning_browser_popups'); } catch (_) {}

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

function cleanTelegramMarkdown(text) {
  // Keep simple bold markers for important prices; strip only fragile chars.
  return text.replace(/[_`\[]/g, '');
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

function commandKind(text) {
  const s = String(text || '').trim().toLowerCase();
  if (s.startsWith('/gi├í') || s.startsWith('/gia')) return 'price';
  if (s.startsWith('/qh')) return 'planning';
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
  return Number.isFinite(v) ? `${v.toFixed(2)} tß╗╖` : '-';
}

function fmtAreaShort(v) {
  return Number.isFinite(v) ? `${Number(v).toLocaleString('vi-VN', { maximumFractionDigits: 1 })} m2` : '-';
}

function formatBatdongsanReport(result) {
  const rows = result?.comparables || [];
  if (!rows.length) return 'Mß║½u so s├ính tß╗½ nguß╗ôn ngo├ái\n- Ch╞░a t├¼m ─æ╞░ß╗úc mß║½u ph├╣ hß╗úp.';
  return [
    'Mß║½u so s├ính tß╗½ nguß╗ôn ngo├ái',
    ...rows.slice(0, 6).map((r, i) => [
      `${i + 1}. ─É╞░ß╗¥ng: ${r.road_name || '-'}`,
      `   Diß╗çn t├¡ch: ${fmtAreaShort(r.area_m2)} | Tß╗òng tiß╗ün: ${formatMoneyBillion(r.total_billion)} | Gi├í/m2: ${Number.isFinite(r.price_million_m2) ? `*${fmtPrice(r.price_million_m2)}*` : '-'}`,
      `   M─ÉSD─É: ${r.land_use_code || 'ch╞░a r├╡'} | Vß╗ï tr├¡: ${r.position || 'ch╞░a r├╡'} | Loß║íi: ${r.asset_type || '-'}`,
      `   Nguß╗ôn: ${r.source || 'web'}${r.url ? ` - ${r.url}` : ''}`,
    ].filter(Boolean).join('\n')),
    result?.url ? `Nguß╗ôn search: ${result.url}` : null,
  ].filter(Boolean).join('\n');
}

function assetLabel(code) {
  return ({ land: '─Éß║Ñt', house: 'Nh├á', apartment: 'Chung c╞░', factory: 'Kho/x╞░ß╗ƒng', shophouse: 'Shophouse/mß║╖t bß║▒ng' })[code] || code || 'ch╞░a chß╗ìn';
}
function positionLabel(code) {
  return ({ frontage: 'Mß║╖t tiß╗ün', alley: 'Hß║╗m', corner: 'C─ân g├│c/2 mß║╖t tiß╗ün', any: 'Bß╗Å qua' })[code] || code || 'ch╞░a chß╗ìn';
}
function positionTraitsForCode(code) {
  if (code === 'frontage') return ['mß║╖t tiß╗ün/kinh doanh'];
  if (code === 'alley') return ['hß║╗m/ng├╡'];
  if (code === 'corner') return ['c─ân g├│c/2 mß║╖t tiß╗ün'];
  return [];
}


function normalizeViText(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/─æ/g, 'd').replace(/─É/g, 'D').toLowerCase();
}


function formatGeoAddress(loc) {
  if (!loc) return 'ch╞░a x├íc ─æß╗ïnh';
  return [
    loc.road ? `─É╞░ß╗¥ng geocode: ${loc.road}` : null,
    loc.nearest_road?.name ? `─É╞░ß╗¥ng gß║ºn nhß║Ñt: ${loc.nearest_road.name} (~${Math.round(loc.nearest_road.distance_m)}m)` : null,
    loc.nearest_pois?.length ? `POI/dß╗▒ ├ín gß║ºn: ${loc.nearest_pois.slice(0, 3).map(p => `${p.name} ~${Math.round(p.distance_m)}m`).join('; ')}` : null,
    loc.neighbourhood ? `Khu phß╗æ: ${loc.neighbourhood}` : null,
    (loc.ward || loc.suburb) ? `Ph╞░ß╗¥ng/x├ú: ${loc.ward || loc.suburb}` : null,
    loc.district ? `Quß║¡n/huyß╗çn/TP: ${loc.district}` : null,
    (loc.city || loc.state) ? `Tß╗ënh/TP: ${loc.city || loc.state}` : null,
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
  if (c === 'ODT') return ['M─ÉSD─É ─æß║Ñt ß╗ƒ/thß╗ò c╞░'];
  if (c === 'TMD' || c === 'TMDV') return ['M─ÉSD─É TMDV/hß╗ùn hß╗úp'];
  if (c === 'SKC') return ['M─ÉSD─É SKC/sß║ún xuß║Ñt'];
  if (c === 'CLN') return ['M─ÉSD─É CLN/─æß║Ñt v╞░ß╗¥n'];
  if (c === 'NN') return ['M─ÉSD─É n├┤ng nghiß╗çp'];
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
      ...extra,
    });
  }
}

function fmtPrice(v) {
  return Number.isFinite(v) ? `${v.toFixed(2)} tr/m2` : 'ch╞░a c├│';
}

function formatPriceReport(priceStats) {
  if (!priceStats || !priceStats.sample_count) {
    return [
      'Gi├í tham khß║úo Guland',
      '- Ch╞░a lß║Ñy ─æ╞░ß╗úc mß║½u gi├í quanh khu vß╗▒c.',
      priceStats?.error ? `- L├╜ do: ${priceStats.error}` : null,
    ].filter(Boolean).join('\n');
  }
  return [
    'Gi├í tham khß║úo Guland',
    `- Sß╗æ mß║½u d├╣ng ─æß╗â t├¡nh: ${priceStats.sample_count}`,
    `- Khoß║úng gi├í: *${fmtPrice(priceStats.min_million_m2)} - ${fmtPrice(priceStats.max_million_m2)}*`,
    `- Trung b├¼nh: *${fmtPrice(priceStats.avg_million_m2)}*`,
    `- Trung vß╗ï: *${fmtPrice(priceStats.median_million_m2)}*`,
    priceStats.filter_note ? `- Bß╗Ö lß╗ìc: ${priceStats.filter_note}` : null,
    '3 mß║½u so s├ính bß║»t buß╗Öc ╞░u ti├¬n c├╣ng M─ÉSD─É + c├╣ng ─æ╞░ß╗¥ng + c├╣ng mß║╖t tiß╗ün/hß║╗m:',
    ...(priceStats.comparable_positions || []).map((p, idx) => {
      const r = p.representative || {};
      const range = p.sample_count > 1 ? `; khoß║úng ${fmtPrice(p.min_million_m2)}-${fmtPrice(p.max_million_m2)}` : '';
      const road = p.road_name ? `; ─æ╞░ß╗¥ng ${p.road_name}` : '';
      const traits = p.traits?.length ? `; ${p.traits.join(', ')}` : '';
      const src = r.source_url ? `\n   Link: ${r.source_url}` : '';
      return `${idx + 1}. *${fmtPrice(p.price_million_m2)}*; c├ích ~${Math.round(p.distance_m)}m${road}${traits}${range}\n   ${String(r.title || '').slice(0, 120)}${src}`;
    }).filter(Boolean),
  ].filter(x => x !== null).join('\n');
}

function fmtArea(v) {
  return Number.isFinite(Number(v)) ? `${Number(v).toLocaleString('vi-VN', { maximumFractionDigits: 2 })} m2` : '-';
}

function formatParcelHeader(summary, ...parsedSources) {
  const parcel = parsedSources.map(x => x?.parcel).find(p => p && (p.map_sheet || p.parcel_no || p.area_m2 || p.old_area || p.new_area)) || {};
  return [
    'Th├┤ng tin thß╗¡a',
    parcel.map_sheet ? `- Sß╗æ tß╗¥: ${parcel.map_sheet}` : null,
    parcel.parcel_no ? `- Sß╗æ thß╗¡a: ${parcel.parcel_no}` : null,
    parcel.area_m2 ? `- Diß╗çn t├¡ch thß╗¡a: ${fmtArea(parcel.area_m2)}` : null,
    parcel.old_area ? `- Khu vß╗▒c c┼⌐: ${parcel.old_area}` : null,
    parcel.new_area ? `- Khu vß╗▒c mß╗¢i: ${parcel.new_area}` : null,
    !parcel.old_area && !parcel.new_area && summary.location?.display_name ? `- Khu vß╗▒c: ${summary.location.display_name}` : null,
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
    uniqueLandLines.length ? '- M─ÉSD─É/chß╗⌐c n─âng ─æß║Ñt:' : null,
    ...uniqueLandLines,
    official.population || main.danso ? `- D├ón sß╗æ: ${official.population || main.danso}` : null,
    official.floors || main.floors ? `- Tß║ºng cao: ${official.floors || main.floors}` : null,
    official.density || main.building_density ? `- M─ÉXD: ${official.density || main.building_density}` : null,
    official.far || main.far ? `- HSSD─É: ${official.far || main.far}` : null,
    sourceUrl ? `- Nguß╗ôn: ${sourceUrl}` : null,
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
  if (!onlyA.length && !onlyB.length) return 'Kß║┐t luß║¡n: Quy hoß║ích Guland giß╗æng QH Viß╗çt vß╗ü nh├│m chß╗⌐c n─âng ─æß║Ñt ─æß╗ìc ─æ╞░ß╗úc.';
  return 'Kß║┐t luß║¡n: Quy hoß║ích Guland kh├íc QH Viß╗çt hoß║╖c ch╞░a khß╗¢p ho├án to├án vß╗ü chß╗⌐c n─âng ─æß║Ñt; ╞░u ti├¬n kiß╗âm tra lß║íi popup ─æ├║ng ─æiß╗âm v├á nguß╗ôn ch├¡nh thß╗æng.';
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
    `QHHCM ╞░u ti├¬n: ${summary.cross_check_links?.hcm_official?.web_url || `https://thongtinquyhoach.hochiminhcity.gov.vn/#/${summary.input.lat}/${summary.input.lon}/18`}`,
    e.source_url ? `Chß╗ë ti├¬u ├┤ chß╗⌐c n─âng: ${e.source_url}` : null,
    e.mixed_source_url ? `Bß║úng chß╗⌐c n─âng hß╗ùn hß╗úp: ${e.mixed_source_url}` : null,
    `QH Viß╗çt/Guland fallback: ${summary.cross_check_links?.qhviet?.home_url} | ${summary.cross_check_links?.guland?.coordinate_planning_url}`,
  ] : [
    `Guland: ${summary.cross_check_links?.guland?.coordinate_planning_url}`,
    `QH Viß╗çt: ${summary.cross_check_links?.qhviet?.home_url}`,
  ];
  return [
    'B├üO C├üO QUY HOß║áCH',
    `Tß╗ìa ─æß╗Ö: ${summary.input.lat}, ${summary.input.lon}`,
    summary.location?.display_name ? `Vß╗ï tr├¡: ${summary.location.display_name}` : null,
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
    qhviet ? formatSourceBlock('QH Viß╗çt', qhviet, summary.cross_check_links?.qhviet?.home_url, {}) : null,
    sourceConclusion,
    !guland && !qhviet && !officialAsParsed ? 'Ch╞░a ─æß╗ìc ─æ╞░ß╗úc th├┤ng tin quy hoß║ích chi tiß║┐t.' : null,
    '',
    formatPriceReport(priceStats),
    '',
    'Nguß╗ôn',
    sources.filter(Boolean).map(x => `- ${x}`).join('\n'),
  ].filter(Boolean).join('\n');
}

async function answerCallbackQuery(id, text = '') {
  if (!id) return;
  await tg('answerCallbackQuery', { callback_query_id: id, text }).catch(() => null);
}

function buildPlanningReportOnly(summary, gulandText, qhvietText, popupErrors = []) {
  const emptyPrice = { sample_count: 0, error: 'D├╣ng /gi├í ─æß╗â tra gi├í ri├¬ng.' };
  let report = buildFinalReport(summary, gulandText, emptyPrice, qhvietText)
    .replace(/\nGi├í tham khß║úo Guland[\s\S]*?\nNguß╗ôn\n/, '\nNguß╗ôn\n');
  if (popupErrors.length && !gulandText && !qhvietText) report += `\n\nPopup tß╗▒ ─æß╗Öng\n${popupErrors.map(x => `- ${x}`).join('\n')}`;
  return report;
}

async function askPriceStep(req, key) {
  const selected = [
    req.asset ? `Loß║íi t├ái sß║ún: ${assetLabel(req.asset)}` : null,
    req.landUse ? `M─ÉSD─É: ${req.landUse}` : null,
  ].filter(Boolean).join('\n');
  if (!req.asset) {
    await sendMessage(req.chatId, ['Anh chß╗ìn loß║íi t├ái sß║ún ─æß╗â em lß╗ìc gi├í:', selected].filter(Boolean).join('\n'), req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: '─Éß║Ñt', callback_data: `price:asset:land:${key}` },
      { text: 'Nh├á', callback_data: `price:asset:house:${key}` },
      { text: 'Chung c╞░', callback_data: `price:asset:apartment:${key}` },
    ], [
      { text: 'Kho/x╞░ß╗ƒng', callback_data: `price:asset:factory:${key}` },
      { text: 'Shophouse/mß║╖t bß║▒ng', callback_data: `price:asset:shophouse:${key}` },
    ]] } });
    return;
  }
  if (!req.landUse) {
    await sendMessage(req.chatId, ['Anh chß╗ìn M─ÉSD─É:', selected].filter(Boolean).join('\n'), req.replyTo, { reply_markup: { inline_keyboard: [[
      { text: 'ODT', callback_data: `price:land:ODT:${key}` },
      { text: 'TMD', callback_data: `price:land:TMD:${key}` },
      { text: 'SKC', callback_data: `price:land:SKC:${key}` },
      { text: 'CLN', callback_data: `price:land:CLN:${key}` },
      { text: 'NN', callback_data: `price:land:NN:${key}` },
    ]] } });
    return;
  }
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
  console.log(`[price] search location="${bdsLocationText}" lat=${req.lat} lon=${req.lon} asset=${req.asset} land=${req.landUse}`);
  const bds = await searchBatdongsanComparables({
    lat: req.lat,
    lon: req.lon,
    locationText: bdsLocationText,
    target: { code: req.landUse, asset: req.asset },
  }).catch(err => ({ error: err.message || String(err), comparables: [] }));
  console.log(`[price] external comparables=${bds.comparables?.length || 0} error=${bds.error || ''} query=${bds.query || ''}`);
  await sendMessage(req.chatId, [`GI├ü B─ÉS`, `Tß╗ìa ─æß╗Ö: ${req.lat}, ${req.lon}`, `Khu vß╗▒c search: ${bdsLocationText || 'ch╞░a r├╡'}`, `Loß║íi t├ái sß║ún: ${assetLabel(req.asset)}`, `M─ÉSD─É: ${req.landUse}`, '', formatPriceReport(stats), '', formatBatdongsanReport(bds)].join('\n'), req.replyTo);
}

async function handlePriceSelection(query) {
  const data = String(query.data || '');
  if (!data.startsWith('price:')) return false;
  const parts = data.split(':');
  let req;
  if (parts.length === 3) {
    // Backward compatibility with old buttons: price:ODT:key
    const [, code, key] = parts;
    req = pendingPriceRequests.get(key);
    if (!req) { await answerCallbackQuery(query.id, 'Y├¬u cß║ºu gi├í ─æ├ú hß║┐t hß║ín, gß╗¡i lß║íi /gi├í + tß╗ìa ─æß╗Ö gi├║p em.'); return true; }
    req.landUse = code;
  } else {
    const [, step, value, key] = parts;
    req = pendingPriceRequests.get(key);
    if (!req) { await answerCallbackQuery(query.id, 'Y├¬u cß║ºu gi├í ─æ├ú hß║┐t hß║ín, gß╗¡i lß║íi /gi├í + tß╗ìa ─æß╗Ö gi├║p em.'); return true; }
    if (step === 'asset') req.asset = value;
    if (step === 'land') req.landUse = value;
    if (step === 'pos') req.position = value;
  }
  await answerCallbackQuery(query.id, '─É├ú nhß║¡n lß╗▒a chß╗ìn.');
  if (!req.asset || !req.landUse) {
    await askPriceStep(req, parts[parts.length - 1]);
    return true;
  }
  await answerCallbackQuery(query.id, '─Éang tra gi├í...');
  await runPriceLookup(req);
  pendingPriceRequests.delete(parts[parts.length - 1]);
  return true;
}

async function handleMessage(msg) {
  const chatId = msg.chat?.id;
  if (!chatId || !allowed(chatId)) return;

  const rawText = [msg.text, msg.caption].filter(Boolean).join(' ');
  const mentioned = botWasMentioned(rawText, [...(msg.entities || []), ...(msg.caption_entities || [])]);
  const text = stripBotMention(rawText);
  const replyText = msg.reply_to_message ? [msg.reply_to_message.text, msg.reply_to_message.caption].filter(Boolean).join(' ') : '';
  let combinedText = [text, replyText].filter(Boolean).join('\n');
  const kind = commandKind(text) || commandKind(combinedText) || 'planning';
  if (!mentioned && !commandKind(combinedText) && !looksLikePlanningRequest(combinedText)) return;
  combinedText = await resolveShortMapLinks(combinedText);

  const parsed = parseCoordinateInput([combinedText]);
  if (!parsed) {
    await sendMessage(chatId, 'Em thß║Ñy anh gß╗¡i link/nhß║»c quy hoß║ích, nh╞░ng ch╞░a ─æß╗ìc ─æ╞░ß╗úc tß╗ìa ─æß╗Ö lat/lon thß║¡t. Link official dß║íng #/3/1/18 l├á trß║íng th├íi giao diß╗çn, kh├┤ng ─æß╗º ─æß╗â bot gß╗ìi API. Anh gß╗¡i tß╗ìa ─æß╗Ö dß║íng 10.845790835609225,106.76200727878299 hoß║╖c link Google Maps c├│ tß╗ìa ─æß╗Ö nh├⌐.', msg.message_id);
    return;
  }

  const key = `${chatId}:${msg.message_id}`;
  if (seen.has(key)) return;
  seen.add(key);

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

  await sendMessage(chatId, 'Em nhß║¡n tß╗ìa ─æß╗Ö rß╗ôi, ─æang tra quy hoß║ích...', msg.message_id);
  try {
    const raw = await lookupHcmPlanning(parsed.lat, parsed.lon);
    const summary = summarize(raw);
    let gulandText = /Tß╗¥\s+\d+\s+Thß╗¡a\s+\d+|Th├┤ng tin quy hoß║ích x├óy dß╗▒ng|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT)\b\s*[\d.,]+\s*m2/i.test(combinedText) ? combinedText : null;
    let qhvietText = /Th├┤ng tin thß╗¡a\s+Sß╗æ tß╗¥\s+\d+\s+Sß╗æ thß╗¡a\s+\d+|Khu vß╗▒c mß╗¢i|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|SON)\b\s+─Éß║Ñt/i.test(combinedText) ? combinedText : null;
    const popupErrors = [];
    const browserPopupsEnabled = process.env.BDS_DISABLE_BROWSER_POPUPS !== '1';
    if (browserPopupsEnabled && !gulandText && planningBrowserPopups?.readGulandPopupText) {
      const got = await planningBrowserPopups.readGulandPopupText(parsed.lat, parsed.lon).catch(err => { popupErrors.push(`Guland popup: ${err.message || err}`); return null; });
      if (got?.text && !got.degraded) gulandText = got.text;
      else if (got?.degraded) popupErrors.push(`Guland popup: ${got.text.split('\n')[0]}`);
    } else if (!gulandText) {
      popupErrors.push('Guland popup: auto-click ─æang bß╗ï tß║»t bß║▒ng BDS_DISABLE_BROWSER_POPUPS=1.');
    }
    if (browserPopupsEnabled && !qhvietText && planningBrowserPopups?.readQhVietPopupText) {
      const got = await planningBrowserPopups.readQhVietPopupText(parsed.lat, parsed.lon, summary.location || {}).catch(err => { popupErrors.push(`QH Viß╗çt popup: ${err.message || err}`); return null; });
      if (got?.text && !got.degraded) qhvietText = got.text;
      else if (got?.degraded) popupErrors.push(`QH Viß╗çt popup: ${got.text.split('\n')[0]}`);
    } else if (!qhvietText) {
      popupErrors.push('QH Viß╗çt popup: auto-click ─æang bß╗ï tß║»t bß║▒ng BDS_DISABLE_BROWSER_POPUPS=1.');
    }
    const planningTraitsText = [
      summary.exact_indicators?.chuc_nang_dat,
      ...(summary.exact_indicators?.mixed_functions || []).map(x => x.chuc_nang_dat),
      gulandText,
      combinedText,
    ].filter(Boolean).join(' ');
    let report = buildPlanningReportOnly(summary, gulandText, qhvietText, popupErrors);
    await sendMessage(chatId, report, msg.message_id);
  } catch (err) {
    await sendMessage(chatId, `Em tra bß╗ï lß╗ùi: ${err.message || err}. Anh gß╗¡i lß║íi tß╗ìa ─æß╗Ö/link gi├║p em.`, msg.message_id);
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
  console.log('B─ÉS planning bot started');
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
