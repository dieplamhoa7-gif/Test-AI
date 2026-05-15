// Lightweight batdongsan.com.vn comparable search for B─ÉS bot.
// Uses real browser/CDP first because Google and batdongsan block plain Node fetch.

const { spawn } = require('child_process');
const path = require('path');
const { repairMojibake } = require('./mojibake_repair');
const DEFAULT_CDP = process.env.BDS_BROWSER_CDP || 'http://127.0.0.1:18800';
const DEFAULT_CHROME = process.env.BDS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const DEFAULT_PROFILE = process.env.BDS_BROWSER_PROFILE || path.join(__dirname, '.bds-browser-profile');
let chromeStartedByBot = false;

async function cdpJson(path, options = {}) {
  const res = await fetch(`${DEFAULT_CDP}${path}`, options);
  if (!res.ok) throw new Error(`CDP HTTP ${res.status} ${path}`);
  return res.json();
}

async function ensureCdpBrowser() {
  try { await cdpJson('/json/version'); return true; } catch (_) {}
  if (chromeStartedByBot) return false;
  chromeStartedByBot = true;
  try {
    const child = spawn(DEFAULT_CHROME, [
      '--remote-debugging-port=18800',
      `--user-data-dir=${DEFAULT_PROFILE}`,
      '--no-first-run',
      '--disable-popup-blocking',
      'about:blank',
    ], { detached: true, stdio: 'ignore' });
    child.unref();
    await wait(4500);
    await cdpJson('/json/version');
    return true;
  } catch (_) {
    return false;
  }
}

async function openTab(url) {
  await ensureCdpBrowser();
  try { return await cdpJson(`/json/new?${encodeURIComponent(url)}`, { method: 'PUT' }); }
  catch (_) { return await cdpJson(`/json/new?${encodeURIComponent(url)}`); }
}

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

async function withCdp(wsUrl, fn) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = ev => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
      else resolve(msg.result);
    }
  };
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error('CDP websocket error'));
    setTimeout(() => reject(new Error('CDP websocket open timeout')), 5000);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const msgId = ++id;
    const timeoutMs = params.__timeoutMs || 12000;
    delete params.__timeoutMs;
    const timer = setTimeout(() => {
      if (pending.has(msgId)) { pending.delete(msgId); reject(new Error(`CDP command timeout: ${method}`)); }
    }, timeoutMs);
    pending.set(msgId, { resolve: v => { clearTimeout(timer); resolve(v); }, reject: e => { clearTimeout(timer); reject(e); } });
    ws.send(JSON.stringify({ id: msgId, method, params }));
  });
  try { return await fn(send); }
  finally { try { ws.close(); } catch (_) {} }
}

function normalizeText(s) {
  return repairMojibake(String(s || '')).normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
}

function detectAssetType(text) {
  const t = normalizeText(text);
  if (/chung cu|can ho|apartment|condotel/.test(t)) return 'chung c╞░/c─ân hß╗Ö';
  if (/kho|xuong|nha xuong|nha may|san xuat/.test(t)) return 'kho/x╞░ß╗ƒng';
  if (/nha|biet thu|shophouse|nha pho|mat bang|khach san|van phong/.test(t)) return 'nh├á/c├┤ng tr├¼nh';
  if (/dat nen|lo dat|dat tho cu|dat vuon|\bdat\b/.test(t)) return '─æß║Ñt/nß╗ün';
  return 'kh├íc/kh├┤ng r├╡';
}

function detectLandUseCode(text) {
  const t = normalizeText(text);
  if (/\bodt\b|dat o|tho cu|so hong|so do|dat do thi/.test(t)) return 'ODT';
  if (/\bcln\b|cay lau nam|dat vuon|vuon/.test(t)) return 'CLN';
  if (/\bskc\b|kho xuong|nha xuong|san xuat|co so san xuat/.test(t)) return 'SKC';
  if (/\btmd\b|\btmdv\b|thuong mai dich vu|khach san|van phong|mat bang|shophouse/.test(t)) return 'TMD';
  if (/nong nghiep|\bnn\b|\bhnk\b|\blua\b|dat lua/.test(t)) return 'NN';
  return null;
}

function detectPosition(text) {
  const t = normalizeText(text);
  if (/mat tien|\bmt\b|duong lon|kinh doanh/.test(t)) return 'mß║╖t tiß╗ün';
  if (/hem|ngo/.test(t)) return 'hß║╗m';
  return null;
}

function parseAreaM2(text) {
  const s = normalizeText(text).replace(/,/g, '.');
  const labelled = s.match(/(?:dien tich|dt)\s*:?\s*(\d+(?:\.\d+)?)\s*m2/);
  if (labelled) return Number(labelled[1]);

  // Dimensions often appear as "11x22m2", "12m x 22m", "KT: 6.4x8m".
  // Use product only when it looks like the main area and not just secondary KT.
  const dim = s.match(/(?:^|\s)(\d+(?:\.\d+)?)\s*m?\s*[x├ù]\s*(\d+(?:\.\d+)?)\s*m/)
    || s.match(/(?:kt|kich thuoc|ngang)\s*:?\s*(\d+(?:\.\d+)?)\s*m?\s*[x├ù]\s*(\d+(?:\.\d+)?)\s*m/);
  if (dim) {
    const a = Number(dim[1]), b = Number(dim[2]);
    const area = a * b;
    if (Number.isFinite(area) && area >= 15 && area <= 20000) return area;
  }

  const m = s.match(/(\d+(?:\.\d+)?)\s*m2/);
  return m ? Number(m[1]) : null;
}

function parseTotalBillion(text) {
  const s = normalizeText(text).replace(/,/g, '.');
  const labelledTy = s.match(/(?:gia|gia:)\s*:?\s*(\d+(?:\.\d+)?)\s*(ty|ti)/);
  if (labelledTy) return Number(labelledTy[1]);
  const tyMatches = [...s.matchAll(/(\d+(?:\.\d+)?)\s*(ty|ti)/g)].map(m => Number(m[1])).filter(Number.isFinite);
  if (tyMatches.length) return Math.max(...tyMatches);
  const labelledTr = s.match(/(?:gia|gia:)\s*:?\s*(\d+(?:\.\d+)?)\s*(tr|trieu)(?!\s*\/)/);
  if (labelledTr) return Number(labelledTr[1]) / 1000;
  return null;
}

function parsePriceMillionM2(text) {
  const s = normalizeText(text).replace(/,/g, '.');
  let m = s.match(/(\d+(?:\.\d+)?)\s*(?:tr|trieu)\s*\/\s*m2/);
  if (m) return Number(m[1]);
  const total = parseTotalBillion(text);
  const area = parseAreaM2(text);
  if (Number.isFinite(total) && Number.isFinite(area) && area > 0) return total * 1000 / area;
  return null;
}

function sourceName(url) {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch (_) { return 'web'; }
}

function extractRoadName(text) {
  const raw = normalizeText(text || '');
  const known = [
    'vo van ngan', 'huynh van nghe', 'dang van bi', 'kha van can', 'pham van dong',
    'le van viet', 'do xuan hop', 'song hanh', 'xa lo ha noi', 'quoc lo 13',
    'nguyen xi', 'dien bien phu', 'nguyen duy trinh', 'nguyen thi dinh', 'mai chi tho',
  ];
  for (const k of known) if (raw.includes(k)) return k;
  const m = raw.match(/(?:duong|mat tien|mt|hem|hxh)\s+([a-z0-9\s]+?)(?:\s+-|\s*,|\s+phuong|\s+quan|\s+tp|\s+gia|$)/);
  return m?.[1]?.replace(/^duong\s+/, '').trim() || null;
}

function resultToComparable(item, target = {}) {
  const text = [item.title, item.snippet].filter(Boolean).join(' ');
  const assetType = repairMojibake(detectAssetType(text));
  const landUseCode = detectLandUseCode(text);
  const position = repairMojibake(detectPosition(text));
  const price_million_m2 = parsePriceMillionM2(text);
  const area_m2 = parseAreaM2(text);
  const total_billion = parseTotalBillion(text);
  const roadName = extractRoadName(text);
  const targetCode = String(target.code || '').toUpperCase();
  const sameLandUse = !targetCode || !landUseCode || landUseCode === targetCode;
  const isApartment = assetType === 'chung c╞░/c─ân hß╗Ö';
  const wantsApartment = String(target.asset || '').toLowerCase() === 'apartment';
  const okAsset = wantsApartment ? isApartment : (targetCode === 'SKC' ? assetType === 'kho/x╞░ß╗ƒng' || /SKC/.test(landUseCode || '') : !isApartment);
  const sameRoad = !target.roadName || !roadName || normalizeText(roadName) === normalizeText(target.roadName);
  const checklist = {
    asset_type: okAsset,
    land_use: sameLandUse,
    road: sameRoad,
    position: !!position,
    price: Number.isFinite(price_million_m2),
  };
  return {
    source: sourceName(item.url),
    title: repairMojibake(item.title),
    snippet: repairMojibake(item.snippet),
    url: item.url,
    asset_type: assetType,
    land_use_code: landUseCode,
    position,
    road_name: roadName,
    area_m2,
    total_billion,
    price_million_m2,
    checklist,
    accepted: okAsset && sameLandUse && sameRoad,
    score: (sameLandUse ? 100 : 0) + (sameRoad ? 30 : 0) + (roadName ? 25 : -60) + (position ? 10 : 0) + (Number.isFinite(price_million_m2) ? 20 : 0) - (isApartment && !wantsApartment ? 1000 : 0)
      - (Number.isFinite(price_million_m2) && (price_million_m2 < 1 || price_million_m2 > 1000) ? 500 : 0),
  };
}

function simplifyLocationVariants(locationText) {
  const raw = repairMojibake(String(locationText || '')).replace(/^\/gi?á|^\/gia|^\/qh/ig, '').trim();
  const norm = normalizeText(raw);
  const parts = [];
  const roadMap = [
    ['ly thuong kiet', 'Phố Lý Thường Kiệt'],
    ['vo van ngan', 'Võ Văn Ngân'], ['huynh van nghe', 'Huỳnh Văn Nghệ'],
    ['dang van bi', 'Đặng Văn Bi'], ['kha van can', 'Kha Vạn Cân'],
    ['pham van dong', 'Phạm Văn Đồng'], ['nguyen van thoai', 'Nguyễn Văn Thoại'],
    ['vo nguyen giap', 'Võ Nguyên Giáp'], ['nguyen trung truc', 'Nguyễn Trung Trực'],
    ['tran phu', 'Trần Phú'], ['lac hong', 'Lạc Hồng'], ['nguyen trai', 'Nguyễn Trãi'],
  ];
  const areaMap = [
    ['hoan kiem|cua nam', 'Hoàn Kiếm Hà Nội'],
    ['ha noi', 'Hà Nội'],
    ['cau giay|trung hoa', 'Cầu Giấy Hà Nội'],
    ['thanh xuan', 'Thanh Xuân Hà Nội'],
    ['thu duc|binh tho|binh trung', 'Thủ Đức TP HCM'],
    ['bien hoa|dong nai|tran bien|buu long', 'Biên Hòa Đồng Nai'],
    ['da nang|ngu hanh son|son tra', 'Đà Nẵng'],
    ['rach gia|kien giang', 'Rạch Giá Kiên Giang'],
    ['hai phong|le chan|kenh duong', 'Lê Chân Hải Phòng'],
  ];
  const road = roadMap.find(([pat]) => new RegExp(pat).test(norm))?.[1] || '';
  const area = areaMap.find(([pat]) => new RegExp(pat).test(norm))?.[1] || '';
  if (road && area) parts.push(`${road} ${area}`);
  if (road) parts.push(road);
  if (area) parts.push(area);
  if (!parts.length) parts.push(raw.split(/[,;\n]/)[0].split(/\s+/).slice(0, 6).join(' '));
  return [...new Set(parts.filter(Boolean))];
}

function targetAssetKeywords(code, asset, position) {
  const c = String(code || '').toUpperCase();
  const a = String(asset || '').toLowerCase();
  const p = String(position || '').toLowerCase();
  let base;
  if (a === 'apartment') base = ['chung cư', 'căn hộ'];
  else if (a === 'house') base = ['bán nhà'];
  else if (a === 'factory' || c === 'SKC') base = ['kho xưởng', 'nhà xưởng', 'đất sản xuất'];
  else if (a === 'shophouse' || c === 'TMD') base = ['shophouse', 'mặt bằng kinh doanh', 'nhà mặt tiền'];
  else if (c === 'CLN') base = ['đất vườn', 'đất cây lâu năm'];
  else if (c === 'NN') base = ['đất nông nghiệp', 'đất vườn'];
  else base = ['bán đất', 'đất thổ cư', 'nhà đất bán'];
  const pos = p === 'frontage' ? 'mặt tiền' : p === 'alley' ? 'hẻm' : p === 'corner' ? 'căn góc 2 mặt tiền' : '';
  return pos ? base.flatMap(x => [x, `${x} ${pos}`]) : base;
}

function buildQueries(locationText, target = {}) {
  const locs = simplifyLocationVariants(repairMojibake(locationText));
  const code = String(target.code || '').toUpperCase();
  const kinds = targetAssetKeywords(code, target.asset, target.position).map(repairMojibake).slice(0, 2);
  const queries = [];
  for (const loc of locs.slice(0, 3)) {
    for (const kind of kinds) {
      // Keep keywords short: asset + road/area only. Long ward/city strings dilute Google.
      queries.push(repairMojibake(`${kind} ${loc}`));
      queries.push(repairMojibake(`${kind} ${loc} batdongsan`));
      queries.push(repairMojibake(`${kind} ${loc} alonhadat`));
    }
    if (code) queries.push(repairMojibake(`${code} ${loc}`));
  }
  return queries.filter(Boolean);
}

function extractGoogleLinks(html) {
  const urls = new Set();
  for (const m of html.matchAll(/href="\/url\?q=(https?:\/\/[^&"]+)/g)) urls.add(decodeURIComponent(m[1]));
  for (const m of html.matchAll(/href="(https?:\/\/(?:www\.)?(?:batdongsan\.com\.vn|alonhadat\.com\.vn|nhadat\.cafeland\.vn|muaban\.net)\/[^"]+)/g)) urls.add(m[1].replace(/&amp;/g, '&'));
  return [...urls].filter(u => /(?:batdongsan\.com\.vn|alonhadat\.com\.vn|nhadat\.cafeland\.vn|muaban\.net)\//.test(u) && !/wiki\.batdongsan/.test(u));
}


function htmlDecode(s) {
  return String(s || '')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function slugifyVi(s) {
  return normalizeText(s).replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

async function alonhadatSuggest(query) {
  const url = `https://alonhadat.com.vn/handler/Handler.ashx?command=22&query=${encodeURIComponent(query)}`;
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'vi,en;q=0.8' } });
  const json = await res.json().catch(() => null);
  return json?.suggestions || [];
}

function buildAlonhadatUrls(locationText = '', target = {}) {
  const norm = normalizeText(locationText);
  const urls = [];
  const asset = String(target.asset || '').toLowerCase();
  const code = String(target.code || '').toUpperCase();
  let prop = 'nha-dat';
  if (asset === 'apartment') prop = 'can-ho-chung-cu';
  else if (asset === 'house') prop = 'nha';
  else if (asset === 'factory' || code === 'SKC') prop = 'kho-xuong';
  else if (asset === 'shophouse' || code === 'TMD') prop = 'nha-mat-tien';
  else if (code === 'CLN' || code === 'NN') prop = 'dat-nong-lam-nghiep';
  else prop = 'dat-tho-cu-dat-o';
  if ((asset === 'apartment' || prop === 'can-ho-chung-cu') && /binh trung/.test(norm)) urls.push('https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/binh-trung-thanh-pho-thu-duc-px776.html');
  else if ((asset === 'apartment' || prop === 'can-ho-chung-cu') && /thu duc|ho chi minh|tp hcm|tphcm/.test(norm)) urls.push('https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/ho-chi-minh/150/thanh-pho-thu-duc.html');
  if ((asset === 'apartment' || prop === 'can-ho-chung-cu') && /lai thieu|thuan an|binh hoa/.test(norm)) urls.push('https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/binh-duong/592/thanh-pho-thuan-an.html');
  if (/vo van ngan/.test(norm) && /thu duc|ho chi minh|tp hcm|tphcm/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-vo-van-ngan-thanh-pho-thu-duc-dp2496.html`);
  if (/huynh van nghe/.test(norm) && /dong nai|bien hoa|tran bien|buu long/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-huynh-van-nghe-thanh-pho-bien-hoa-dp245.html`);
  if (/lai thieu|thuan an|binh hoa/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/lai-thieu-thanh-pho-thuan-an-px2270.html`);
  if (/da nang/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/3/da-nang.html`);
  if (/ngu hanh son/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/da-nang/587/quan-ngu-hanh-son.html`);
  if (/son tra/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/da-nang/586/quan-son-tra.html`);
  if (/nguyen van thoai/.test(norm)) {
    urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-nguyen-van-thoai-quan-son-tra-dp2818.html`);
    urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-nguyen-van-thoai-quan-ngu-hanh-son-dp2920.html`);
  }
  if (/vo nguyen giap/.test(norm)) {
    urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-vo-nguyen-giap-quan-son-tra-dp10472.html`);
    urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-vo-nguyen-giap-quan-ngu-hanh-son-dp10957.html`);
  }
  if (/rach gia|kien giang/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/kien-giang/661/thanh-pho-rach-gia.html`);
  if (/nguyen trung truc/.test(norm)) { urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-nguyen-trung-truc-thanh-pho-rach-gia-dp6250.html`); urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/kien-giang/661/thanh-pho-rach-gia.html`); }
  if (/tran phu/.test(norm)) { urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-tran-phu-thanh-pho-rach-gia-dp6272.html`); urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/kien-giang/661/thanh-pho-rach-gia.html`); }
  if (/lac hong/.test(norm)) { urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-lac-hong-thanh-pho-rach-gia-dp10517.html`); urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/kien-giang/661/thanh-pho-rach-gia.html`); }
  if (/hai phong|le chan|kenh duong|hoang huy commerce/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/hai-phong/442/quan-le-chan.html`);
  if (/vo nguyen giap/.test(norm) && /hai phong|le chan|kenh duong|hoang huy/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-dai-lo-vo-nguyen-giap-quan-le-chan-dp19865.html`);
  if (/kenh duong/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/kenh-duong-quan-le-chan-px1176.html`);
  if (/ha noi/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/1/ha-noi.html`);
  if (/hoan kiem|cua nam|ly thuong kiet/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/ha-noi/412/quan-hoan-kiem.html`);
  if (/cua nam/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/cua-nam-quan-hoan-kiem-px85.html`);
  if (/ly thuong kiet/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/pho-ly-thuong-kiet-quan-hoan-kiem-dp486.html`);
  if (/cau giay|trung hoa|yen hoa|nghia do/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/ha-noi/408/quan-cau-giay.html`);
  if (/trung hoa/.test(norm)) { urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/trung-hoa-quan-cau-giay-px22.html`); urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-trung-hoa-quan-cau-giay-dp141.html`); }
  if (/tay mo|smart city|vinhomes/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/tay-mo-quan-nam-tu-liem-px399.html`);
  if (/nguyen trai|thanh xuan/.test(norm)) urls.push(`https://alonhadat.com.vn/nha-dat/can-ban/${prop}/duong-nguyen-trai-quan-thanh-xuan-dp737.html`);
  return urls;
}

function parseAlonhadatListHtml(html, listUrl) {
  const items = [...String(html || '').matchAll(/<article class='property-item'[\s\S]*?<\/article>/g)].map(m => m[0]);
  return items.map(it => {
    const href = it.match(/<a class='link[^']*'[^>]+href='([^']+)'/i)?.[1] || '';
    const title = htmlDecode(it.match(/<h3[^>]*>([\s\S]*?)<\/h3>/i)?.[1] || '');
    const text = htmlDecode(stripHtml(it));
    return { url: href ? new URL(href, listUrl).href : listUrl, title, snippet: text };
  });
}

async function fetchAlonhadatComparables(locationText, target = {}, limit = 8) {
  const urls = new Set(buildAlonhadatUrls(locationText, target));
  const roadMatch = String(locationText || '').match(/(?:─æ╞░ß╗¥ng|duong)?\s*([A-Z├Ç-ß╗╕][\w├Ç-ß╗╣]+\s+V─ân\s+[A-Z├Ç-ß╗╕][\w├Ç-ß╗╣]+)/i)
    || String(locationText || '').match(/(Huß╗│nh V─ân Nghß╗ç|─Éß║╖ng V─ân Bi|V├╡ V─ân Ng├ón)/i);
  if (roadMatch) {
    for (const sug of await alonhadatSuggest(roadMatch[1]).catch(() => [])) {
      const data = String(sug.data || '').split(';');
      const streetPart = data[3] || '';
      const streetId = streetPart.split(':')[0];
      const streetSlug = streetPart.split(':')[1];
      const districtSlug = /Th├ánh phß╗æ Thß╗º ─Éß╗⌐c/i.test(sug.value) ? 'thanh-pho-thu-duc' : /Bi├¬n H├▓a/i.test(sug.value) ? 'thanh-pho-bien-hoa' : /Thuß║¡n An/i.test(sug.value) ? 'thanh-pho-thuan-an' : slugifyVi(String(sug.value).split(',')[1] || '');
      if (streetId && streetSlug && districtSlug) urls.add(`https://alonhadat.com.vn/nha-dat/can-ban/dat-tho-cu-dat-o/${streetSlug}-${districtSlug}-dp${streetId}.html`);
    }
  }
  const out = [];
  for (const url of urls) {
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'vi,en;q=0.8' } }).catch(() => null);
    if (!res?.ok) continue;
    const html = await res.text();
    out.push(...parseAlonhadatListHtml(html, url));
    if (out.length >= limit) break;
  }
  return out.slice(0, limit);
}

async function fetchListing(url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'vi,en;q=0.8' } });
  const html = await res.text();
  const title = stripHtml(html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1]
    || html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]
    || '');
  const desc = stripHtml(html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)/i)?.[1]
    || html.match(/<div[^>]+class=["'][^"']*(?:description|content|pr-description)[^"']*["'][^>]*>([\s\S]{0,3000}?)<\/div>/i)?.[1]
    || '');
  const bodyText = stripHtml(html).slice(0, 5000);
  return { url, title, snippet: desc || bodyText };
}

function normalizeGoogleResultUrl(href) {
  try {
    const u = new URL(href, 'https://www.google.com');
    const q = u.searchParams.get('q') || u.searchParams.get('url');
    if (q && /(?:batdongsan\.com\.vn|alonhadat\.com\.vn|nhadat\.cafeland\.vn|muaban\.net)\//i.test(q)) return decodeURIComponent(q);
    if (/(?:batdongsan\.com\.vn|alonhadat\.com\.vn|nhadat\.cafeland\.vn|muaban\.net)\//i.test(u.href)) return u.href;
  } catch (_) {}
  return null;
}

async function searchGoogleLinksViaBrowser(query, limit = 8) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  const tab = await openTab(url);
  if (!tab.webSocketDebuggerUrl) throw new Error('Kh├┤ng c├│ browser websocket');
  try {
    return await withCdp(tab.webSocketDebuggerUrl, async send => {
      await send('Runtime.enable');
      await send('Page.enable');
      await send('Page.navigate', { url });
      await wait(6500);
      const res = await send('Runtime.evaluate', { expression: `(() => {
        function norm(href) {
          try {
            const u = new URL(href, location.href);
            const q = u.searchParams.get('q') || u.searchParams.get('url');
            if (q && /(?:batdongsan\\.com\\.vn|alonhadat\\.com\\.vn|nhadat\\.cafeland\\.vn|muaban\\.net)/i.test(q)) return decodeURIComponent(q);
            if (/(?:batdongsan\\.com\\.vn|alonhadat\\.com\\.vn|nhadat\\.cafeland\\.vn|muaban\\.net)/i.test(u.href)) return u.href;
          } catch (_) {}
          return null;
        }
        const urls = [];
        for (const a of document.querySelectorAll('a')) {
          const hrefs = [a.href, a.getAttribute('href'), a.dataset?.href, a.getAttribute('data-url')].filter(Boolean);
          for (const h of hrefs) {
            const n = norm(h);
            if (n && !/wiki\\.batdongsan/i.test(n)) urls.push(n.split('#')[0]);
          }
        }
        const textUrls = ((document.body?.innerText || '').match(/https?:\/\/(?:batdongsan\.com\.vn|alonhadat\.com\.vn|nhadat\.cafeland\.vn|muaban\.net)\/[^\s)]+/g) || []);
        urls.push(...textUrls);
        return [...new Set(urls)].slice(0, ${limit});
      })()`, returnByValue: true, __timeoutMs: 10000 });
      return [...new Set(res.result?.value || [])];
    });
  } finally { if (tab.id) await fetch(`${DEFAULT_CDP}/json/close/${tab.id}`).catch(() => null); }
}

async function fetchListingViaBrowser(url) {
  const tab = await openTab(url);
  if (!tab.webSocketDebuggerUrl) throw new Error('Kh├┤ng c├│ browser websocket');
  try {
    return await withCdp(tab.webSocketDebuggerUrl, async send => {
      await send('Runtime.enable');
      await send('Page.enable');
      await send('Page.navigate', { url });
      await wait(5500);
      const res = await send('Runtime.evaluate', { expression: `(() => {
        const text = (document.body?.innerText || '').replace(/\\s+/g,' ').trim();
        const title = document.querySelector('h1')?.innerText || document.title || '';
        const meta = document.querySelector('meta[name="description"]')?.content || '';
        return { url: location.href, title, snippet: (meta + ' ' + text).slice(0, 6000), blocked: /Just a moment|Cloudflare|Attention Required/i.test(text + ' ' + document.title) };
      })()`, returnByValue: true, __timeoutMs: 10000 });
      return res.result?.value || { url, title: '', snippet: '' };
    });
  } finally { if (tab.id) await fetch(`${DEFAULT_CDP}/json/close/${tab.id}`).catch(() => null); }
}

async function fetchListItemsViaBrowser(url, limit = 8) {
  const tab = await openTab(url);
  if (!tab.webSocketDebuggerUrl) throw new Error('Kh├┤ng c├│ browser websocket');
  try {
    return await withCdp(tab.webSocketDebuggerUrl, async send => {
      await send('Runtime.enable');
      await send('Page.enable');
      await send('Page.navigate', { url });
      await wait(7000);
      const res = await send('Runtime.evaluate', { expression: `(() => { const out=[]; const priceRe=/(tỷ|triệu|m²|m2|tr\\/m)/i; for (const a of document.querySelectorAll('a[href]')) { const href=new URL(a.getAttribute('href'),location.origin).href; if(!/batdongsan\\.com\\.vn\\//i.test(href) || /wiki\\.batdongsan|javascript:/i.test(href)) continue; let box=a; for(let i=0;i<8&&box.parentElement;i++){ const t=(box.innerText||box.textContent||'').replace(/\\s+/g,' ').trim(); if(priceRe.test(t)&&t.length>80) break; box=box.parentElement;} const text=(box.innerText||a.innerText||'').replace(/\\s+/g,' ').trim(); if(!priceRe.test(text) || text.length<80) continue; const title=(a.querySelector('h3')?.innerText||box.querySelector('h3')?.innerText||a.innerText||'').replace(/\\s+/g,' ').trim(); if(!title || /Bán căn hộ chung cư|Bán nhà riêng|Bán đất|Nhà đất bán/i.test(title)) continue; out.push({url:href.split('#')[0],title,snippet:text.slice(0,2500)});} const seen=new Set(); return out.filter(x=>!seen.has(x.url)&&(seen.add(x.url),true)).slice(0,${limit}); })()`, returnByValue: true, __timeoutMs: 12000 });
      return res.result?.value || [];
    });
  } finally { if (tab.id) await fetch(`${DEFAULT_CDP}/json/close/${tab.id}`).catch(() => null); }
}

function directCategoryUrls(locationText, target = {}) {
  const raw = String(locationText || '');
  const norm = normalizeText(raw);
  const urls = [];
  const code = String(target.code || '').toUpperCase();
  const asset = String(target.asset || '').toLowerCase();

  // Direct category fallback is allowed only when the same road/province is explicit
  // in the current request. Never reuse a road category for coordinate-only input.
  const hasHvn = /huynh van nghe/.test(norm);
  const hasDongNai = /dong nai|bien hoa|tran bien|buu long/.test(norm);
  const hasThuDucHcm = /thu duc|ho chi minh|tp hcm|tphcm/.test(norm);
  const hasVoVanNgan = /vo van ngan/.test(norm);

  if (hasHvn && hasDongNai) {
    if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-duong-huynh-van-nghe-245');
    if (asset === 'shophouse' || code === 'TMD') urls.push('https://batdongsan.com.vn/ban-nha-mat-pho-duong-huynh-van-nghe-245');
    urls.push('https://batdongsan.com.vn/ban-dat-duong-huynh-van-nghe-245');
    urls.push('https://batdongsan.com.vn/nha-dat-ban-duong-huynh-van-nghe-245');
  }
  if (hasVoVanNgan && hasThuDucHcm) {
    if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-duong-vo-van-ngan-phuong-binh-tho');
    if (asset === 'shophouse' || code === 'TMD') urls.push('https://batdongsan.com.vn/ban-nha-mat-pho-duong-vo-van-ngan-phuong-binh-tho');
    urls.push('https://batdongsan.com.vn/ban-dat-duong-vo-van-ngan-phuong-binh-tho');
  }
  const hasHaNoi = /ha noi|hoan kiem|cua nam|ly thuong kiet|cau giay|trung hoa|tay mo|smart city|vinhomes|nguyen trai|thanh xuan/.test(norm);
  const hasHaiPhong = /hai phong|le chan|kenh duong|hoang huy commerce/.test(norm);
  const hasDaNang = !hasHaiPhong && !hasHaNoi && /da nang|ngu hanh son|son tra|nguyen van thoai|vo nguyen giap/.test(norm);
  const hasNguHanhSon = /ngu hanh son/.test(norm);
  const hasSonTra = /son tra/.test(norm);
  const hasNguyenVanThoai = /nguyen van thoai/.test(norm);
  const hasVoNguyenGiap = /vo nguyen giap/.test(norm);
  const hasRachGia = /rach gia|kien giang|nguyen trung truc|tran phu|lac hong/.test(norm);
  if (!hasHvn && hasDongNai) {
    if (asset === 'factory' || code === 'SKC') urls.push('https://batdongsan.com.vn/ban-kho-nha-xuong-dong-nai');
    urls.push('https://batdongsan.com.vn/ban-dat-dong-nai');
  }
  if (hasDaNang) {
    if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-da-nang');
    else urls.push('https://batdongsan.com.vn/ban-dat-da-nang');
    if (hasNguHanhSon) urls.push('https://batdongsan.com.vn/ban-dat-quan-ngu-hanh-son-ddn');
    if (hasSonTra) urls.push('https://batdongsan.com.vn/ban-dat-quan-son-tra-ddn');
    if (hasNguyenVanThoai) urls.push('https://batdongsan.com.vn/ban-dat-duong-nguyen-van-thoai-son-tra-ddn');
    if (hasVoNguyenGiap) urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-duong-vo-nguyen-giap-son-tra-ddn');
  }
  if (hasRachGia) {
    if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-tp-rach-gia-kg');
    else if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-rach-gia-kg');
    else urls.push('https://batdongsan.com.vn/ban-dat-tp-rach-gia-kg');
  }
  if (hasHaiPhong) {
    if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-quan-le-chan-hp');
    else if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-quan-le-chan-hp');
    else urls.push('https://batdongsan.com.vn/ban-dat-quan-le-chan-hp');
    if (hasVoNguyenGiap) urls.push('https://batdongsan.com.vn/nha-dat-ban-duong-vo-nguyen-giap-le-chan-hp');
  }
  if (hasHaNoi) {
    if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi');
    else if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-ha-noi');
    else urls.push('https://batdongsan.com.vn/ban-dat-ha-noi');
    if (/hoan kiem|cua nam|ly thuong kiet/.test(norm)) {
      if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-quan-hoan-kiem');
      else if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-quan-hoan-kiem');
      else urls.push('https://batdongsan.com.vn/ban-dat-quan-hoan-kiem');
      if (/ly thuong kiet/.test(norm)) {
        if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-pho-ly-thuong-kiet-hoan-kiem');
        if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-pho-ly-thuong-kiet-hoan-kiem');
        urls.push('https://batdongsan.com.vn/nha-dat-ban-pho-ly-thuong-kiet-hoan-kiem');
        urls.push('https://batdongsan.com.vn/nha-dat-ban-pho-ly-thuong-kiet-quan-hoan-kiem');
      }
      if (/cua nam/.test(norm)) {
        urls.push('https://batdongsan.com.vn/nha-dat-ban-phuong-cua-nam');
        if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-phuong-cua-nam');
        if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-phuong-cua-nam');
      }
    }
    if (/cau giay|trung hoa|yen hoa|nghia do/.test(norm)) {
      if (asset === 'apartment') urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-quan-cau-giay');
      else if (asset === 'house') urls.push('https://batdongsan.com.vn/ban-nha-rieng-quan-cau-giay');
      else urls.push('https://batdongsan.com.vn/ban-dat-quan-cau-giay');
    }
    if (/tay mo|smart city|vinhomes/.test(norm)) urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-vinhomes-smart-city');
    if (/nguyen trai|thanh xuan/.test(norm)) urls.push('https://batdongsan.com.vn/ban-can-ho-chung-cu-duong-nguyen-trai-thanh-xuan');
  }
  return [...new Set(urls)];
}

async function searchBatdongsanComparables({ lat, lon, locationText = '', target = {}, limit = 8 } = {}) {
  const queries = buildQueries(locationText || `${lat}, ${lon}`, target);
  const googleUrls = [];
  let source = 'Google/browser search + multi-source BDS parse';
  for (const q of queries.slice(0, 6)) {
    try { googleUrls.push(...await searchGoogleLinksViaBrowser(q, limit * 2)); } catch (_) {}
    if (googleUrls.length >= limit * 2) break;
  }
  // Fallback to old fetch parser if browser Google produced nothing.
  if (!googleUrls.length) {
    source += ' (fetch fallback empty/blocked)';
    for (const q of queries.slice(0, 4)) {
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(q)}`;
      const res = await fetch(searchUrl, { headers: { 'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'vi,en;q=0.8' } });
      const html = await res.text();
      googleUrls.push(...extractGoogleLinks(html));
      if (googleUrls.length >= limit * 2) break;
    }
  }
  // Put direct category URLs first; Google often returns broad/search links before the exact category.
  const uniqueUrls = [...new Set([...directCategoryUrls(locationText, target), ...googleUrls])].slice(0, limit * 3);
  const listings = [];
  try { listings.push(...await fetchAlonhadatComparables(locationText, target, limit)); } catch (_) {}
  for (const u of uniqueUrls.slice(0, 10)) {
    try {
      if (!/pr\d+/i.test(u)) {
        listings.push(...await fetchListItemsViaBrowser(u, limit));
      } else {
        const item = await fetchListingViaBrowser(u);
        if (!item.blocked) listings.push(item);
      }
    } catch (_) {
      try { listings.push(await fetchListing(u)); } catch (_) {}
    }
  }
  const locNorm = normalizeText(locationText || '');
  const wantsHvn = /huynh van nghe/.test(locNorm);
  const wantsVoVanNgan = /vo van ngan/.test(locNorm);
  const locNormForFilter = normalizeText(locationText || '');
  const strictRoadTerms = ['vo van ngan', 'huynh van nghe', 'nguyen van thoai', 'vo nguyen giap', 'pham van dong', 'nguyen duy trinh', 'mai chi tho', 'nguyen trung truc', 'tran phu', 'lac hong', 'ly thuong kiet']
    .filter(term => locNormForFilter.includes(term));
  const cityTerms = ['ha noi', 'hai phong', 'da nang', 'kien giang', 'ho chi minh', 'dong nai', 'binh duong']
    .filter(term => locNormForFilter.includes(term));
  const strongAreaTerms = ['binh trung', 'lai thieu', 'binh hoa', 'binh tho', 'truong tho', 'an phu', 'thao dien', 'linh dong', 'linh chieu', 'ngu hanh son', 'son tra', 'rach gia', 'kien giang', 'hai phong', 'le chan', 'kenh duong', 'hoang huy commerce', 'ha noi', 'hoan kiem', 'cua nam', 'ly thuong kiet', 'cau giay', 'trung hoa', 'tay mo', 'smart city', 'vinhomes', 'nguyen trai', 'thanh xuan']
    .filter(term => locNormForFilter.includes(term));
  const wantsApartment = String(target.asset || '').toLowerCase() === 'apartment';
  const seenUrls = new Set();
  const mappedAll = listings.filter(x => !x.blocked && !/Just a moment|Enable JavaScript and cookies|Cloudflare|Attention Required/i.test(`${x.title || ''} ${x.snippet || ''}`)).map(x => resultToComparable(x, target));
  const buildComparableList = (strict = true) => mappedAll
    .filter(x => {
      const u = new URL(x.url || 'https://x.invalid', 'https://x.invalid');
      const path = u.pathname.replace(/\/$/, '');
      if (/^\/$|^\/nguoi-ban|^\/nha-dat-ban(?:-[a-z0-9-]+)?$|^\/ban-nha-rieng(?:-[a-z0-9-]+)?$|^\/ban-dat(?:-[a-z0-9-]+)?$|^\/ban-can-ho-chung-cu(?:-[a-z0-9-]+)?$/i.test(path)) return false;
      return !/\/nha-dat-ban(?:-|$)|\/ban-nha-rieng(?:-|$)|\/ban-dat(?:-|$)|\/ban-can-ho-chung-cu(?:-|$)/i.test(path) || /pr\d+/i.test(x.url || '');
    })
    .filter(x => !seenUrls.has(x.url) && (seenUrls.add(x.url), true))
    .filter(x => !wantsApartment || x.asset_type === 'chung cư/căn hộ')
    .filter(x => !Number.isFinite(x.price_million_m2) || (x.price_million_m2 >= 1 && x.price_million_m2 <= 1000))
    .filter(x => Number.isFinite(x.price_million_m2) || Number.isFinite(x.total_billion))
    .filter(x => {
      const hay = normalizeText(`${x.url} ${x.title} ${x.snippet} ${x.road_name || ''}`);
      if (cityTerms.length && !cityTerms.some(term => hay.includes(term))) return false;
      if (strictRoadTerms.length) return strictRoadTerms.some(term => hay.includes(term));
      if (!strongAreaTerms.length) return true;
      return strongAreaTerms.some(term => hay.includes(term));
    })
    .map(x => {
      const hay = normalizeText(`${x.url} ${x.title} ${x.snippet}`);
      const roadBoost = (wantsHvn && /huynh-van-nghe|huynh van nghe/.test(hay)) || (wantsVoVanNgan && /vo-van-ngan|vo van ngan/.test(hay)) ? 500 : 0;
      return { ...x, score: x.score + roadBoost };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
  let comparables = buildComparableList(true);
  // Do not fall back to far/irrelevant Google results. Returning no sample is better
  // than returning another district/city and misleading price guidance.
  return { source, query: repairMojibake(queries.join(' | ')), url: `https://www.google.com/search?q=${encodeURIComponent(repairMojibake(queries[0] || ''))}`, comparables };
}

function stripHtml(s) {
  return String(s || '').replace(/<script[\s\S]*?<\/script>/g, ' ')
    .replace(/<style[\s\S]*?<\/style>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

module.exports = { searchBatdongsanComparables, detectAssetType, detectLandUseCode, parsePriceMillionM2, parseAreaM2, parseTotalBillion };
