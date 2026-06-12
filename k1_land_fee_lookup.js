const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const JSON_PATH = path.join(__dirname, 'exports', 'k1_pdf_relevant_extract.json');
const rows = JSON.parse(fs.readFileSync(JSON_PATH, 'utf8'));

function normalize(s) {
  return String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[đð]/g, 'd').replace(/[ĐÐ]/g, 'D')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function normalizedIndexToOriginalIndex(original, needleNorm) {
  const src = String(original || '');
  const target = normalize(needleNorm);
  if (!target) return -1;
  let acc = '';
  const map = [];
  for (let i = 0; i < src.length; i++) {
    const n = normalize(src[i]);
    if (!n) continue;
    if (acc && !acc.endsWith(' ')) { acc += ' '; map.push(i); }
    for (const ch of n) { acc += ch; map.push(i); }
  }
  const j = acc.indexOf(target);
  return j >= 0 ? map[j] : -1;
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
    display: loc.display_name || '',
    nearestRoad: loc.nearest_road?.name || '',
    pois: (loc.nearest_pois || []).map(p => p.name).filter(Boolean),
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

const allEntries = rows.flatMap(r => extractStreetEntries(r.text, r.page))
  .filter(e => normalize(e.road).length >= 3 && !/^\d+$/.test(normalize(e.road)) && !/^phu\b|^stt\b/.test(normalize(e.road)));

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

function roadVariants(road) {
  const raw = String(road || '').trim();
  const noHem = raw.replace(/^\s*(hẻm|hem|ngõ|ngo|kiệt|kiet)\s+\d+[a-zA-Z\/\-]*\s+/i, '').trim();
  const noPrefix = noHem.replace(/^\s*(đường|duong|đ\.|d\.)\s+/i, '').trim();
  const noAccentTitle = normalize(noPrefix).split(' ').map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ');
  const variants = [raw, noHem, noPrefix, noAccentTitle];
  // Common aliases in OCR/table text.
  variants.push(noPrefix.replace(/^ba\s+tháng\s+hai$/i, '3 Tháng 2'));
  variants.push(noPrefix.replace(/^3\s+tháng\s+2$/i, '3 Tháng 2'));
  return [...new Set(variants.filter(Boolean))];
}

function contextTextForGeo(geo) {
  return normalize([geo.ward, geo.district, geo.city, geo.road, geo.nearestRoad, geo.display, ...(geo.pois || [])].filter(Boolean).join(' '));
}

function scoreSegmentByContext(segment, geo) {
  const ctx = contextTextForGeo(geo);
  const seg = normalize(segment);
  if (!seg || !ctx) return 0;
  let score = 0;
  const parts = seg.split(' ').filter(x => x.length >= 3);
  for (const p of parts) if (ctx.includes(p)) score += 1;
  // Bonus if full endpoint/POI-ish phrase appears.
  for (const phrase of seg.split(/\s+(?:den|toi|nguyen|tran|le|vo|pham|ton|hai|ba)\s+/).filter(Boolean)) {
    const np = normalize(phrase);
    if (np.length >= 5 && ctx.includes(np)) score += 2;
  }
  return score;
}

function extractRoadDirectCandidatesFromPage(row, road, geo = {}) {
  const nroad = normalize(road);
  if (!nroad) return [];
  const text = String(row.text || '');
  if (!normalize(text).includes(nroad)) return [];
  const header = findWardHeader(text);
  const roadUpper = String(road || '').toUpperCase();
  const indices = [];
  let start = 0;
  const upper = text.toUpperCase();
  while (true) {
    const i = upper.indexOf(roadUpper, start);
    if (i < 0) break;
    indices.push(i);
    start = i + Math.max(1, roadUpper.length);
  }
  const normFallback = [];
  if (!indices.length) {
    const normText = normalize(text);
    const idxNorm = normText.indexOf(nroad);
    if (idxNorm >= 0) normFallback.push(Math.max(0, Math.floor(idxNorm * text.length / Math.max(1, normText.length)) - 50));
  }
  const candidates = [];
  for (const idx of [...indices.slice(0, 12), ...normFallback.slice(0, 4)]) {
    const isNormFallback = normFallback.includes(idx);
    const before = text.slice(Math.max(0, idx - 35), idx).replace(/\s+/g, ' ').trim();
    // Accept only when the road appears as a table road-name row, normally after STT.
    // Normalized fallback is allowed because OCR may use visually different Đ/Ð/no accents.
    if (!isNormFallback && before && !/(^|\s)\d{1,3}\s*$/.test(before)) continue;
    let sliceRaw = text.slice(idx, idx + 900);
    // If fallback started before the road, trim again to the road token so previous row numbers do not leak in.
    const rel = normalizedIndexToOriginalIndex(sliceRaw, road);
    if (rel > 0) sliceRaw = sliceRaw.slice(rel);
    let slice = sliceRaw.replace(/\s+/g, ' ');
    const sliceNorm = normalize(slice);
    if (!roadVariants(road).some(rv => sliceNorm.startsWith(normalize(rv)))) continue;
    const escapedRoad = roadUpper.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const body = slice.replace(new RegExp('^' + escapedRoad + '\\s+', 'i'), '');
    const rowRe = /(.{2,140}?)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d{1,3}(?:\.\d{3})+)\s+(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)(?:\s+(\d+,\d+))?/g;
    let m2, matched = 0;
    while ((m2 = rowRe.exec(body)) && matched < 8) {
      let segment = titleCaseVi(m2[1]).replace(/\s+/g, ' ').trim();
      if (/^\d+,\d+\b/.test(segment)) break;
      if (/^\d+\s+[A-ZÀ-Ỵ]/.test(segment)) break;
      if (/\b\d{1,3}\s+[A-ZÀ-Ỵ].*\bĐIỆN\s+BIÊN\s+PHỦ\b/i.test(segment)) break;
      if (!segment || /^(STT|TÊN ĐƯỜNG|ĐOẠN ĐƯỜNG|Phụ lục|Ban hành)$/i.test(segment)) continue;
      matched++;
      candidates.push({
        page: row.page,
        stt: null,
        road: titleCaseVi(road),
        segment,
        priceResidentialThousand: parseNumeric(m2[2]),
        priceCommercialThousand: parseNumeric(m2[3]),
        priceBusinessThousand: parseNumeric(m2[4]),
        kResidential: parseNumeric(m2[5]),
        kCommercial: parseNumeric(m2[6]),
        kBusiness: parseNumeric(m2[7]),
        kAgricultural: parseNumeric(m2[8] || m2[5]),
        raw: (road + ' ' + m2[0]).slice(0, 650),
        areaHeader: header,
        segmentScore: scoreSegmentByContext(segment, geo),
      });
    }
    if (!matched) {
      const nums = slice.match(/\d{1,3}\.\d{3}|\d+,\d+/g) || [];
      const priceNums = nums.filter(x => /\d{1,3}\.\d{3}/.test(x)).slice(0, 3);
      const kNums = nums.filter(x => /\d+,\d+/.test(x)).slice(0, 4);
      if (priceNums.length < 3 || kNums.length < 3) continue;
      const segMatch = slice.match(new RegExp(escapedRoad + '\\s+(.{0,120}?)\\s+' + priceNums[0].replace('.', '\\.'), 'i'));
      const segment = titleCaseVi(segMatch?.[1] || 'TRỌN ĐƯỜNG/đoạn gần nhất trong phụ lục');
      candidates.push({
        page: row.page,
        stt: null,
        road: titleCaseVi(road),
        segment,
        priceResidentialThousand: parseNumeric(priceNums[0]),
        priceCommercialThousand: parseNumeric(priceNums[1]),
        priceBusinessThousand: parseNumeric(priceNums[2]),
        kResidential: parseNumeric(kNums[0]),
        kCommercial: parseNumeric(kNums[1]),
        kBusiness: parseNumeric(kNums[2]),
        kAgricultural: parseNumeric(kNums[3] || kNums[0]),
        raw: slice.slice(0, 650),
        areaHeader: header,
        segmentScore: scoreSegmentByContext(segment, geo),
      });
    }  }
  return candidates;
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
  const direct = rows.flatMap(row => {
    const hits = roadVariants(geo.road || '').flatMap(rv => extractRoadDirectCandidatesFromPage(row, rv, geo));
    return hits.map(hit => {
      const headerNorm = normalize(hit.areaHeader);
      let score = 10 + (hit.segmentScore || 0);
      if (geoWard && headerNorm && (headerNorm.includes(geoWard) || geoWard.includes(headerNorm))) score += 30;
      else if (geoWard && headerNorm) score -= 20;
      if (normalize(row.text).includes(nroad) || roadVariants(geo.road || '').some(rv => normalize(row.text).includes(normalize(rv)))) score += 2;
      return { ...hit, score };
    });
  }).filter(Boolean).sort((a,b) => b.score - a.score || b.segmentScore - a.segmentScore || a.page - b.page);
  if (direct.length) {
    const best = direct[0];
    const bestHeaderNorm = normalize(best.areaHeader);
    const sameWardDirect = direct.filter(x => {
      const h = normalize(x.areaHeader);
      if (!bestHeaderNorm || !h) return x.page === best.page;
      return h === bestHeaderNorm || h.includes(bestHeaderNorm) || bestHeaderNorm.includes(h);
    });
    best.alternatives = sameWardDirect
      .filter(x => x !== best)
      .slice(0, 8)
      .map(x => ({ road: x.road, segment: x.segment, page: x.page, score: x.score, raw: x.raw, wardHeader: x.areaHeader }));
    best.confidence = sameWardDirect.length === 1 || (best.score - sameWardDirect[1].score >= 3) ? 'high' : 'medium';
    return best;
  }

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

function calcAdjusted(entry, landUse = 'ODT', opts = {}) {
  if (!entry) return null;
  const code = String(landUse || 'ODT').toUpperCase();
  const positionMultiplier = Number(opts.positionMultiplier || 1);
  const planningMultiplier = Number(opts.planningMultiplier || 1);
  let baseThousand, marketK, label;
  if (code === 'TMD' || code === 'TMDV') {
    baseThousand = entry.priceCommercialThousand; marketK = entry.kCommercial; label = 'Đất thương mại dịch vụ';
  } else if (code === 'SKC' || code === 'SXKD') {
    baseThousand = entry.priceBusinessThousand; marketK = entry.kBusiness; label = 'Đất SXKD phi nông nghiệp';
  } else {
    baseThousand = entry.priceResidentialThousand; marketK = entry.kResidential; label = 'Đất ở';
  }
  const totalK = marketK * planningMultiplier * positionMultiplier;
  return { baseThousand, marketK, planningMultiplier, positionMultiplier, totalK, adjustedThousand: baseThousand * totalK, label };
}

function renderEvidencePage(page) {
  return new Promise((resolve, reject) => {
    execFile('python', [path.join(__dirname, 'tools', 'render_pdf_page.py'), String(page)], { cwd: __dirname }, (err, stdout, stderr) => {
      if (err) return reject(new Error(stderr || err.message));
      resolve(String(stdout || '').trim());
    });
  });
}

async function lookupK1LandFee({ lat, lon, geoLocation, text, landUse='ODT', position='VT1', planningMultiplier=1 }) {
  const best = findBestK1ByGeo(geoLocation || {});
  if (!best) return { error: 'Chưa match được đường/phụ lục K1 từ tọa độ này.' };
  const positionMultiplier = String(position || 'VT1').toUpperCase() === 'VT1' ? 1 : 1.35;
  const calc = calcAdjusted(best, landUse, { positionMultiplier, planningMultiplier });
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
      priceResidentialThousand: best.priceResidentialThousand,
      priceCommercialThousand: best.priceCommercialThousand,
      priceBusinessThousand: best.priceBusinessThousand,
      kResidential: best.kResidential,
      kCommercial: best.kCommercial,
      kBusiness: best.kBusiness,
      kAgricultural: best.kAgricultural,
      confidence: best.confidence || 'medium',
      alternatives: best.alternatives || [],
    },
    landUse,
    calc: {
      label: calc.label,
      baseThousandPerM2: calc.baseThousand,
      marketK: calc.marketK,
      planningK: calc.planningMultiplier,
      positionK: calc.positionMultiplier,
      totalK: calc.totalK,
      adjustedThousandPerM2: calc.adjustedThousand,
      adjustedMillionPerM2: calc.adjustedThousand / 1000,
      estimatedTotalVnd: totalVnd,
      estimatedTotalBillion: totalVnd ? totalVnd / 1e9 : null,
    },
    evidencePath,
  };
}

module.exports = { lookupK1LandFee };

