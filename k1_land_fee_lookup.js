const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const JSON_PATH = path.join(__dirname, 'exports', 'k1_pdf_relevant_extract.json');
const rows = JSON.parse(fs.readFileSync(JSON_PATH, 'utf8'));

function normalize(s) {
  return String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd').replace(/Đ/g, 'D')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function titleCaseVi(s) {
  return String(s || '').replace(/\s+/g, ' ').trim();
}

function parseNumeric(s) {
  if (!s) return null;
  const v = String(s).replace(/\./g, '').replace(',', '.').trim();
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function parseAreaFromText(text) {
  const m = String(text || '').match(/(\d{1,4}(?:[\.,]\d{1,2})?)\s*m2\b/i);
  if (!m) return null;
  return Number(String(m[1]).replace(',', '.'));
}

function compactGeo(loc = {}) {
  return {
    ward: loc.ward || loc.suburb || loc.neighbourhood || '',
    district: loc.district || loc.city || '',
    city: loc.city || loc.state || '',
    road: loc.road || loc.nearest_road?.name || '',
  };
}

function extractStreetEntries(pageText, page) {
  const lines = String(pageText || '').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const line of lines) {
    const tokens = line.match(/\d{1,3}\.\d{3}|\d+,\d+|\d+/g) || [];
    if (tokens.length < 7) continue;
    const m = line.match(/^\s*(\d+)\s+(.+?)\s+(TRỌN ĐƯỜNG|T\.?RỌN ĐƯỜNG|.+?)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)(?:\s+(\d+,\d+))?/i);
    if (!m) continue;
    out.push({
      page,
      stt: Number(m[1]),
      road: titleCaseVi(m[2]),
      segment: titleCaseVi(m[3]),
      priceResidentialThousand: parseNumeric(m[4]),
      priceCommercialThousand: parseNumeric(m[5]),
      priceBusinessThousand: parseNumeric(m[6]),
      kResidential: parseNumeric(m[7]),
      kCommercial: parseNumeric(m[8]),
      kBusiness: parseNumeric(m[9]),
      kAgricultural: parseNumeric(m[10] || m[7]),
      raw: line,
    });
  }
  return out;
}

const allEntries = rows.flatMap(r => extractStreetEntries(r.text, r.page));

function chooseCandidateByRoad(entries, road) {
  const nr = normalize(road);
  const exact = entries.filter(e => normalize(e.road) === nr);
  if (exact.length) return exact;
  const contains = entries.filter(e => normalize(e.road).includes(nr) || nr.includes(normalize(e.road)));
  return contains;
}

function findWardHeader(pageText) {
  const m = String(pageText || '').match(/PHƯỜNG\s+([A-ZÀ-Ỵ0-9\s\.]+?)\s*\(/i) || String(pageText || '').match(/XÃ\s+([A-ZÀ-Ỵ0-9\s\.]+?)\s*\(/i);
  return m ? titleCaseVi(m[1]) : '';
}

function extractRoadDirectFromPage(row, road) {
  const nroad = normalize(road);
  if (!nroad) return null;
  const text = String(row.text || '');
  const normText = normalize(text);
  const idxNorm = normText.indexOf(nroad);
  if (idxNorm < 0) return null;
  // Work on original text roughly around road occurrence. Since normalized index is not exact,
  // search common uppercase form too; fallback to a broad slice.
  const roadUpper = String(road || '').toUpperCase();
  let idx = text.toUpperCase().indexOf(roadUpper);
  if (idx < 0) idx = Math.max(0, Math.floor(idxNorm * text.length / Math.max(1, normText.length)) - 50);
  const slice = text.slice(idx, idx + 900).replace(/\s+/g, ' ');
  const nums = slice.match(/\d{1,3}\.\d{3}|\d+,\d+/g) || [];
  const priceNums = nums.filter(x => /\d{1,3}\.\d{3}/.test(x)).slice(0, 3);
  const kNums = nums.filter(x => /\d+,\d+/.test(x)).slice(0, 4);
  if (priceNums.length < 3 || kNums.length < 3) return null;
  const header = findWardHeader(text);
  const segMatch = slice.match(new RegExp(roadUpper.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s+(.{0,80}?)\\s+' + priceNums[0].replace('.', '\\.'), 'i'));
  return {
    page: row.page,
    stt: null,
    road: titleCaseVi(road),
    segment: titleCaseVi(segMatch?.[1] || 'TRỌN ĐƯỜNG/đoạn gần nhất trong phụ lục'),
    priceResidentialThousand: parseNumeric(priceNums[0]),
    priceCommercialThousand: parseNumeric(priceNums[1]),
    priceBusinessThousand: parseNumeric(priceNums[2]),
    kResidential: parseNumeric(kNums[0]),
    kCommercial: parseNumeric(kNums[1]),
    kBusiness: parseNumeric(kNums[2]),
    kAgricultural: parseNumeric(kNums[3] || kNums[0]),
    raw: slice.slice(0, 650),
    areaHeader: header,
    score: 1,
  };
}

function findBestK1ByGeo(location = {}) {
  const geo = compactGeo(location);
  const geoWard = normalize(geo.ward);
  const nroad = normalize(geo.road || '');
  const direct = rows.map(row => {
    const hit = extractRoadDirectFromPage(row, geo.road || '');
    if (!hit) return null;
    const headerNorm = normalize(hit.areaHeader);
    let score = 10;
    if (geoWard && headerNorm && (headerNorm.includes(geoWard) || geoWard.includes(headerNorm))) score += 8;
    if (normalize(row.text).includes(nroad)) score += 2;
    return { ...hit, score };
  }).filter(Boolean).sort((a,b) => b.score - a.score || a.page - b.page);
  if (direct.length) return direct[0];

  const roadCandidates = chooseCandidateByRoad(allEntries, geo.road || '');
  let enriched = roadCandidates.map(e => {
    const row = rows.find(r => r.page === e.page);
    const header = findWardHeader(row?.text || '');
    const headerNorm = normalize(header);
    let score = 0;
    if (normalize(e.road) === normalize(geo.road)) score += 10;
    else if (normalize(e.road).includes(nroad) || nroad.includes(normalize(e.road))) score += 6;
    if (geoWard && headerNorm && (headerNorm.includes(geoWard) || geoWard.includes(headerNorm))) score += 5;
    return { ...e, areaHeader: header, score };
  }).sort((a,b) => b.score - a.score || a.page - b.page || a.stt - b.stt);
  return enriched[0] || null;
}

function calcAdjusted(entry, landUse = 'ODT') {
  if (!entry) return null;
  const code = String(landUse || 'ODT').toUpperCase();
  if (code === 'ODT') {
    return { baseThousand: entry.priceResidentialThousand, k: entry.kResidential, adjustedThousand: entry.priceResidentialThousand * entry.kResidential, label: 'Đất ở' };
  }
  if (code === 'TMD') {
    return { baseThousand: entry.priceCommercialThousand, k: entry.kCommercial, adjustedThousand: entry.priceCommercialThousand * entry.kCommercial, label: 'Đất thương mại dịch vụ' };
  }
  if (code === 'SKC') {
    return { baseThousand: entry.priceBusinessThousand, k: entry.kBusiness, adjustedThousand: entry.priceBusinessThousand * entry.kBusiness, label: 'Đất SXKD phi nông nghiệp' };
  }
  return { baseThousand: entry.priceResidentialThousand, k: entry.kResidential, adjustedThousand: entry.priceResidentialThousand * entry.kResidential, label: 'Đất ở' };
}

function renderEvidencePage(page) {
  return new Promise((resolve, reject) => {
    execFile('python', [path.join(__dirname, 'tools', 'render_pdf_page.py'), String(page)], { cwd: __dirname }, (err, stdout, stderr) => {
      if (err) return reject(new Error(stderr || err.message));
      resolve(String(stdout || '').trim());
    });
  });
}

async function lookupK1LandFee({ lat, lon, geoLocation, text, landUse='ODT' }) {
  const best = findBestK1ByGeo(geoLocation || {});
  if (!best) return { error: 'Chưa match được đường/phụ lục K1 từ tọa độ này.' };
  const calc = calcAdjusted(best, landUse);
  const area = parseAreaFromText(text);
  const totalVnd = area && calc ? area * calc.adjustedThousand * 1000 : null;
  const evidencePath = await renderEvidencePage(best.page).catch(() => null);
  return {
    lat, lon,
    areaM2: area,
    match: {
      wardHeader: best.areaHeader,
      road: best.road,
      segment: best.segment,
      page: best.page,
      stt: best.stt,
      raw: best.raw,
    },
    landUse,
    calc: {
      label: calc.label,
      baseThousandPerM2: calc.baseThousand,
      k: calc.k,
      adjustedThousandPerM2: calc.adjustedThousand,
      adjustedMillionPerM2: calc.adjustedThousand / 1000,
      estimatedTotalVnd: totalVnd,
      estimatedTotalBillion: totalVnd ? totalVnd / 1e9 : null,
    },
    evidencePath,
  };
}

module.exports = { lookupK1LandFee };
