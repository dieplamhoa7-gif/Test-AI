// Prototype: multi-source planning lookup by coordinate/map link.
// Usage:
//   node bds_planning_checker.js 10.845790835609225 106.76200727878299
//   node bds_planning_checker.js "https://www.google.com/maps?q=10.845790835609225,106.76200727878299"
//
// Sources:
// - Official HCMC planning portal: sqhkt-qlqh.tphcm.gov.vn / thongtinquyhoach.hochiminhcity.gov.vn
// - Guland: public coordinate planning page + browser/manual fallback (some content requires VIP/session)
// - QH Viß╗çt: public web app + browser/manual fallback (data is app encoded/tile based)

const OFFICIAL = 'https://sqhkt-qlqh.tphcm.gov.vn';
let browserFallback = null;
try { browserFallback = require('./guland_browser_fallback'); } catch (_) {}

async function postForm(url, data) {
  const body = new URLSearchParams(data);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  const text = await res.text();
  try { return { status: res.status, data: JSON.parse(text), text }; }
  catch { return { status: res.status, data: null, text }; }
}


function overpassEscape(s) {
  return String(s || '').replace(/["\\]/g, ' ');
}

async function lookupNearbyOsmContext(lat, lon, radiusM = 350) {
  const q = `
[out:json][timeout:12];
(
  way(around:${radiusM},${lat},${lon})["highway"]["name"];
  node(around:${radiusM},${lat},${lon})["name"]["place"];
  node(around:${radiusM},${lat},${lon})["name"]["amenity"];
  node(around:${radiusM},${lat},${lon})["name"]["building"];
  node(around:${radiusM},${lat},${lon})["name"]["landuse"];
  way(around:${radiusM},${lat},${lon})["name"]["building"];
  way(around:${radiusM},${lat},${lon})["name"]["landuse"];
  relation(around:${radiusM},${lat},${lon})["name"];
);
out center tags 40;`;
  const res = await fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'User-Agent': 'OpenClaw-BDS-Planning-Prototype/0.1' },
    body: new URLSearchParams({ data: q }),
  });
  if (!res.ok) throw new Error(`Overpass HTTP ${res.status}`);
  const json = await res.json();
  const elements = json.elements || [];
  const dist = (e) => {
    const la = e.lat ?? e.center?.lat;
    const lo = e.lon ?? e.center?.lon;
    return Number.isFinite(la) && Number.isFinite(lo) ? haversineMeters(Number(lat), Number(lon), la, lo) : 999999;
  };
  const named = elements.map(e => ({
    id: e.id,
    type: e.type,
    name: e.tags?.name,
    highway: e.tags?.highway,
    amenity: e.tags?.amenity,
    building: e.tags?.building,
    landuse: e.tags?.landuse,
    place: e.tags?.place,
    distance_m: dist(e),
  })).filter(x => x.name).sort((a,b)=>a.distance_m-b.distance_m);
  const roads = named.filter(x => x.highway);
  const pois = named.filter(x => !x.highway);
  return {
    nearest_road: roads[0] || null,
    nearest_pois: pois.slice(0, 5),
    radius_m: radiusM,
  };
}

async function reverseGeocode(lat, lon) {
  const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&accept-language=vi,en&zoom=18`;
  const res = await fetch(url, { headers: { 'User-Agent': 'OpenClaw-BDS-Planning-Prototype/0.1' } });
  return res.ok ? res.json() : null;
}

function parseCoordinateInput(args) {
  const raw = args.join(' ').trim();
  if (!raw) return null;

  // Official HCMC web links may contain hashes like #/3/1/18 (UI state / map state),
  // which are NOT coordinates. Only accept official-link numbers when they look like
  // real HCMC lat/lon values.
  const isOfficialHcmLink = /thongtinquyhoach\.hochiminhcity\.gov\.vn|sqhkt-qlqh\.tphcm\.gov\.vn/i.test(raw);
  const candidates = [];
  for (const m of raw.matchAll(/!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)/g)) {
    candidates.push({ lat: Number(m[1]), lon: Number(m[2]), raw, source: 'google_place_marker' });
  }
  for (const m of raw.matchAll(/@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)/g)) {
    candidates.push({ lat: Number(m[1]), lon: Number(m[2]), raw, source: 'google_map_view' });
  }
  const nums = raw.match(/-?\d+(?:\.\d+)?/g)?.map(Number) || [];
  for (let i = 0; i < nums.length - 1; i++) {
    const a = nums[i], b = nums[i + 1];
    if (Math.abs(a) <= 90 && Math.abs(b) <= 180) candidates.push({ lat: a, lon: b, raw });
    if (Math.abs(b) <= 90 && Math.abs(a) <= 180) candidates.push({ lat: b, lon: a, raw, swapped: true });
  }

  // Preserve source priority. Google place marker (!3d,!4d) is more precise than
  // viewport center (@lat,lng). Do not prefer an HCM-looking viewport if a marker
  // coordinate points elsewhere.
  const marker = candidates.find(c => c.source === 'google_place_marker' && isLikelyVietnamCoordinate(c.lat, c.lon));
  if (marker) return marker;
  if (isOfficialHcmLink) {
    const hcm = candidates.find(c => isLikelyHcmCoordinate(c.lat, c.lon));
    return hcm || null;
  }

  const vietnam = candidates.find(c => isLikelyVietnamCoordinate(c.lat, c.lon));
  if (vietnam) return vietnam;
  return candidates[0] || null;
}

function isLikelyHcmCoordinate(lat, lon) {
  return lat >= 10.3 && lat <= 11.2 && lon >= 106.2 && lon <= 107.2;
}

function isLikelyVietnamCoordinate(lat, lon) {
  return lat >= 8 && lat <= 24 && lon >= 102 && lon <= 110;
}

function buildGulandCheckPlanUrl(lat, lon, radiusDeg = 0.005) {
  const latN = Number(lat), lonN = Number(lon);
  const qs = new URLSearchParams({
    lat: String(latN),
    lng: String(lonN),
    lat_ne: String(latN + radiusDeg),
    lng_ne: String(lonN + radiusDeg * 2.07),
    lat_sw: String(latN - radiusDeg),
    lng_sw: String(lonN - radiusDeg * 2.07),
    cid: '',
    map: '1',
    price: '',
    type: '',
    is_check_plan: '0',
    district_id: '',
    province_id: '',
    ward_id: '',
    map_attr: 'Price-View-Type=on&type-map-filter[]=land&type-map-filter[]=house&day-min=0&day-max=180&size-min=0&size-max=10001&price-min=0&price-max=30.1',
  });
  return `https://guland.vn/post-save/check-plan?${qs.toString()}`;
}

function parseMillionPerM2(label) {
  const m = String(label || '').match(/[\d.]+/);
  return m ? Number(m[0]) : null;
}

function haversineMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = d => d * Math.PI / 180;
  const dLat = toRad(lat2 - lat1), dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function extractRoadName(text) {
  const raw = normalizeText(text || '');
  const patterns = [
    /(?:duong|mat tien|mt)\s+([a-z0-9\s]+?)(?:\s+-|\s*,|\s+phuong|\s+quan|\s+thu duc|\s+tp|$)/,
    /(?:dang|ban).*?\b([a-z]+\s+van\s+[a-z]+|vo\s+van\s+ngan|duong\s+so\s+\d+|so\s+\d+)\b/,
  ];
  for (const re of patterns) {
    const m = raw.match(re);
    if (m?.[1]) return m[1].replace(/^duong\s+/, '').trim();
  }
  return null;
}

function extractFrontWidth(text) {
  const raw = normalizeText(text || '');
  const m = raw.match(/(?:ngang|mat tien)\s*(?:rong)?\s*[:\-]?\s*(\d+(?:[.,]\d+)?)\s*m/);
  return m ? Number(m[1].replace(',', '.')) : null;
}

function detectLandUseTraits(text) {
  const t = normalizeText(text || '');
  const traits = [];
  if (/giao thong|\bdgt\b|lo gioi|hanh lang|duong quy hoach|mo duong/.test(t)) traits.push('M─ÉSD─É giao th├┤ng');
  if (/cay xanh|cong vien|mat nuoc|cong cong|truong hoc|y te/.test(t)) traits.push('M─ÉSD─É c├┤ng cß╗Öng/c├óy xanh');
  if (/\bodt\b|dat o|tho cu|so hong|so do|cong nhan|dat do thi|nha o/.test(t)) traits.push('M─ÉSD─É ─æß║Ñt ß╗ƒ/thß╗ò c╞░');
  if (/\btmdv?\b|thuong mai|dich vu|kinh doanh|hon hop|phuc hop/.test(t)) traits.push('M─ÉSD─É TMDV/hß╗ùn hß╗úp');
  if (/\bskc\b|san xuat|kho xuong|nha xuong|cong nghiep/.test(t)) traits.push('M─ÉSD─É SKC/sß║ún xuß║Ñt');
  // Do not infer CLN from generic "v╞░ß╗¥n/view v╞░ß╗¥n/s├ón v╞░ß╗¥n" in house ads.
  // Only accept explicit legal/planning wording for land use.
  if (/\bcln\b|cay lau nam|dat (?:vuon|cay lau nam)|vuon cay lau nam/.test(t)) traits.push('M─ÉSD─É CLN/─æß║Ñt v╞░ß╗¥n');
  if (/dat nong nghiep|\bhnk\b|\bluc\b|dat lua/.test(t)) traits.push('M─ÉSD─É n├┤ng nghiß╗çp');
  return [...new Set(traits)];
}

function detectListingTraits(item) {
  const original = [item.title, item.content].filter(Boolean).join(' ');
  const text = normalizeText(original);
  const traits = [];
  const evidence = [];
  const add = (trait, re) => {
    const m = text.match(re);
    if (m) { traits.push(trait); evidence.push({ trait, match: m[0] }); }
  };
  add('mß║╖t tiß╗ün/kinh doanh', /mat tien|\bmt\b|duong lon|kinh doanh/);
  add('c─ân g├│c/2 mß║╖t tiß╗ün', /can goc|goc 2 mat|2 mat tien|hai mat tien/);
  add('hß║╗m/ng├╡', /hem|ngo/);
  add('─æß║Ñt', /\bdat\b|dat nen|lo dat/);
  add('nh├á/c├┤ng tr├¼nh', /nha|toa nha|biet thu|shophouse/);
  const road_name = extractRoadName(original);
  const frontage_m = extractFrontWidth(original);
  const land_use_traits = detectLandUseTraits(original);
  for (const t of land_use_traits) traits.push(t);
  if (road_name) evidence.push({ trait: 't├¬n ─æ╞░ß╗¥ng', match: road_name });
  if (frontage_m) evidence.push({ trait: 'bß╗ü ngang', match: `${frontage_m}m` });
  return { traits: [...new Set(traits)], evidence, road_name, frontage_m, land_use_traits };
}

function classifyPlanningTraits(text) {
  return detectLandUseTraits(text || '');
}

function traitScore(itemTraits, targetTraits) {
  if (!targetTraits?.length) return 0;
  const set = new Set(itemTraits || []);
  return targetTraits.reduce((s, t) => s + (set.has(t) ? 1 : 0), 0);
}

function comparableScore(row, target) {
  const landUseScore = traitScore(row.land_use_traits, target.landUseTraits);
  const sameRoad = target.roadName && row.road_name && normalizeText(row.road_name) === normalizeText(target.roadName) ? 1 : 0;
  const positionScore = traitScore(row.traits, target.positionTraits);
  const frontageDiff = Number.isFinite(row.frontage_m) && Number.isFinite(target.frontageM) ? Math.abs(row.frontage_m - target.frontageM) : null;
  const frontageScore = frontageDiff === null ? 0 : Math.max(0, 1 - frontageDiff / Math.max(target.frontageM, 1));
  const distanceScore = Math.max(0, 1 - row.distance_m / 1000);
  const excludedLandUse = row.land_use_traits?.some(t => /giao th├┤ng|c├┤ng cß╗Öng|c├óy xanh/i.test(t)) && !target.landUseTraits?.some(t => /giao th├┤ng|c├┤ng cß╗Öng|c├óy xanh/i.test(t));
  return {
    // Priority: land use -> road -> balanced(distance, position traits) -> frontage.
    total: (excludedLandUse ? -100000 : 0) + landUseScore * 10000 + sameRoad * 5000 + distanceScore * 1000 + positionScore * 1000 + frontageScore * 200,
    landUseScore,
    sameRoad,
    distanceScore,
    positionScore,
    frontageScore,
    frontageDiff,
    excludedLandUse,
  };
}

function summarizeRows(rows) {
  const values = rows.map(x => x.price_million_m2).filter(Number.isFinite).sort((a, b) => a - b);
  if (!values.length) return { sample_count: 0, min_million_m2: null, max_million_m2: null, avg_million_m2: null, median_million_m2: null };
  const avg = values.reduce((s, v) => s + v, 0) / values.length;
  const median = values.length % 2 ? values[(values.length - 1) / 2] : (values[values.length / 2 - 1] + values[values.length / 2]) / 2;
  return { sample_count: values.length, min_million_m2: values[0], max_million_m2: values.at(-1), avg_million_m2: avg, median_million_m2: median };
}

async function fetchGulandCheckPlanJson(lat, lon, url, allowBrowserFallback = true) {
  const preferBrowser = process.env.GULAND_FETCH_MODE !== 'node_first';
  if (preferBrowser && allowBrowserFallback && browserFallback?.fetchGulandCheckPlanViaBrowser) {
    try {
      const json = await browserFallback.fetchGulandCheckPlanViaBrowser(lat, lon, url);
      json.__fetch_source = 'browser_session';
      return json;
    } catch (browserErr) {
      if (process.env.GULAND_FETCH_MODE === 'browser_only') throw new Error(`Browser Guland failed: ${browserErr.message || browserErr}`);
      // Fall through to Node as a backup when browser is unavailable.
    }
  }

  const headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
    'Referer': `https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lon}`,
    'X-Requested-With': 'XMLHttpRequest',
  };
  if (process.env.GULAND_COOKIE) headers.Cookie = process.env.GULAND_COOKIE;
  const res = await fetch(url, { headers });
  if (res.ok) return res.json();
  const nodeError = `Guland price API HTTP ${res.status}`;
  if (!preferBrowser && allowBrowserFallback && browserFallback?.fetchGulandCheckPlanViaBrowser && [401, 403, 419, 429].includes(res.status)) {
    try {
      const json = await browserFallback.fetchGulandCheckPlanViaBrowser(lat, lon, url);
      json.__fetch_source = 'browser_fallback_after_node_' + res.status;
      return json;
    } catch (err) {
      throw new Error(`${nodeError}; browser fallback failed: ${err.message || err}`);
    }
  }
  throw new Error(nodeError);
}

async function lookupGulandPriceStats(lat, lon, options = {}) {
  const url = buildGulandCheckPlanUrl(lat, lon, options.radiusDeg || 0.005);
  const json = await fetchGulandCheckPlanJson(lat, lon, url, options.browserFallback !== false);
  const rows = (json.data || []).map(item => {
    const price_million_m2 = parseMillionPerM2(item.label);
    return {
      id: item.id,
      lat: Number(item.lat),
      lng: Number(item.lng),
      title: item.title || '',
      label: item.label,
      label_ngang: item.label_ngang,
      size: item.size,
      price: item.price,
      price_million_m2,
      distance_m: haversineMeters(Number(lat), Number(lon), Number(item.lat), Number(item.lng)),
      source_url: `https://guland.vn/soi-quy-hoach?lat=${item.lat}&lng=${item.lng}`,
      detail_url: item.slug_title ? `https://guland.vn/${item.slug_title}` : null,
      ...detectListingTraits(item),
    };
  }).filter(x => Number.isFinite(x.price_million_m2));
  const detectedPositionTraits = detectListingTraits({ title: options.contextText || options.planningText || '', content: '' }).traits
    .filter(t => /mß║╖t tiß╗ün|hß║╗m|ng├╡/i.test(t));
  const explicitLandUse = (options.landUseTraits || []).filter(Boolean);
  const target = {
    // User-selected M─ÉSD─É is authoritative for valuation. Do not override it by
    // loose listing/context words such as "v╞░ß╗¥n" in nearby house ads.
    landUseTraits: explicitLandUse.length ? [...new Set(explicitLandUse)] : [...new Set(classifyPlanningTraits(options.planningText || ''))],
    roadName: options.roadName || extractRoadName(options.contextText || options.planningText || ''),
    positionTraits: [...new Set([...(options.positionTraits || []), ...detectedPositionTraits])],
    frontageM: Number(options.frontageM || extractFrontWidth(options.contextText || '') || NaN),
  };
  for (const r of rows) r.comparable = comparableScore(r, target);
  const strictComparableRows = rows.filter(r =>
    !r.comparable.excludedLandUse &&
    (target.landUseTraits.length === 0 || r.comparable.landUseScore > 0) &&
    (!target.roadName || r.comparable.sameRoad) &&
    (target.positionTraits.length === 0 || r.comparable.positionScore > 0) &&
    (!Number.isFinite(target.frontageM) || Number.isFinite(r.frontage_m))
  );
  const filteredRows = strictComparableRows;
  const hasExplicitLandUseFilter = (options.landUseTraits || []).length > 0;
  const minFilteredSamples = options.minFilteredSamples || 3;
  // Prefer strict comparable rows, but never return an empty price report when Guland has
  // nearby price markers. If strict M─ÉSD─É/road/position filtering is too narrow, fall
  // back to all nearby rows and clearly mark the result as a loose reference.
  const rowsForMainPrice = filteredRows.length >= minFilteredSamples ? filteredRows : rows;
  const usedLooseFallback = rowsForMainPrice === rows && filteredRows.length < minFilteredSamples;
  const priceSummary = summarizeRows(rowsForMainPrice);
  const allSummary = summarizeRows(rows);
  const positionMap = new Map();
  for (const r of rowsForMainPrice.sort((a, b) => b.comparable.total - a.comparable.total || a.distance_m - b.distance_m)) {
    // Group very-near duplicate posts into one surveyed position.
    const key = `${r.lat.toFixed(5)},${r.lng.toFixed(5)}`;
    if (!positionMap.has(key)) positionMap.set(key, []);
    positionMap.get(key).push(r);
  }
  let comparable_positions = [...positionMap.entries()].map(([key, group]) => {
    const prices = group.map(x => x.price_million_m2).sort((a, b) => a - b);
    const medianPrice = prices.length % 2 ? prices[(prices.length - 1) / 2] : (prices[prices.length / 2 - 1] + prices[prices.length / 2]) / 2;
    const nearestItem = group.sort((a, b) => a.distance_m - b.distance_m)[0];
    return {
      key,
      lat: nearestItem.lat,
      lng: nearestItem.lng,
      distance_m: nearestItem.distance_m,
      sample_count: group.length,
      price_million_m2: medianPrice,
      min_million_m2: prices[0],
      max_million_m2: prices.at(-1),
      representative: nearestItem,
      traits: [...new Set(group.flatMap(x => x.traits || []))],
      comparable: nearestItem.comparable,
      road_name: nearestItem.road_name,
      frontage_m: nearestItem.frontage_m,
      land_use_traits: [...new Set(group.flatMap(x => x.land_use_traits || []))],
    };
  }).sort((a, b) => b.comparable.total - a.comparable.total || a.distance_m - b.distance_m);
  const strictPositions = comparable_positions.filter(p =>
    (target.landUseTraits.length === 0 || p.comparable.landUseScore > 0) &&
    (!target.roadName || p.comparable.sameRoad) &&
    (target.positionTraits.length === 0 || p.comparable.positionScore > 0)
  );
  comparable_positions = (strictPositions.length >= minFilteredSamples ? strictPositions : comparable_positions).slice(0, 3);

  return {
    source: json.__fetch_source ? `Guland /post-save/check-plan (${json.__fetch_source})` : 'Guland /post-save/check-plan',
    url,
    target,
    filter_applied: rowsForMainPrice === filteredRows && filteredRows.length > 0,
    filter_note: usedLooseFallback ? `Mß║½u lß╗ìc chß║╖t theo M─ÉSD─É/─æ╞░ß╗¥ng/vß╗ï tr├¡ chß╗ë c├│ ${filteredRows.length}/${minFilteredSamples}; ─æang fallback sang to├án bß╗Ö mß║½u gß║ºn ─æiß╗âm ─æß╗â anh vß║½n c├│ gi├í tham khß║úo.` : '─Éang d├╣ng mß║½u ─æ├ú lß╗ìc chß║╖t theo M─ÉSD─É/─æ╞░ß╗¥ng/vß╗ï tr├¡.',
    all_area_stats: allSummary,
    sample_count: priceSummary.sample_count,
    min_million_m2: priceSummary.min_million_m2,
    max_million_m2: priceSummary.max_million_m2,
    avg_million_m2: priceSummary.avg_million_m2,
    median_million_m2: priceSummary.median_million_m2,
    comparable_positions,
  };
}

function buildThirdPartyLinks(lat, lon, locationHint) {
  const q = `${lat},${lon}`;
  const suburb = locationHint?.suburb || '';
  const city = locationHint?.city || 'TP. Hß╗ô Ch├¡ Minh';
  const inHcm = isLikelyHcmCoordinate(Number(lat), Number(lon));
  return {
    priority_note: inHcm
      ? 'Trong TP.HCM: ╞░u ti├¬n cß╗òng Th├┤ng tin quy hoß║ích TP.HCM; nß║┐u kh├┤ng c├│/locked th├¼ ─æß╗æi chiß║┐u QH Viß╗çt + Guland.'
      : 'Ngo├ái TP.HCM: d├╣ng Guland + QH Viß╗çt; kh├┤ng gß╗ìi nguß╗ôn QHHCM.',
    hcm_official: inHcm ? {
      web_url: `https://thongtinquyhoach.hochiminhcity.gov.vn/#/${lat}/${lon}/18`,
      status: 'primary_inside_hcm',
    } : null,
    guland: {
      coordinate_planning_url: `https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lon}`,
      hcm_planning_url: 'https://guland.vn/soi-quy-hoach/tp-ho-chi-minh',
      location_info_hint: suburb ? `https://guland.vn/check-quy-hoach/thong-tin-quy-hoach-ke-hoach-su-dung-dat-${slugify(suburb)}-${slugify(city)}` : null,
      status: inHcm ? 'fallback_or_cross_check_inside_hcm' : 'primary_outside_hcm',
      note: inHcm ? 'D├╣ng khi cß╗òng TP.HCM kh├┤ng trß║ú dß╗» liß╗çu/─æß╗â ─æß╗æi chiß║┐u.' : 'Nguß╗ôn ch├¡nh ngo├ái TP.HCM, cß║ºn ─æß╗æi chiß║┐u QH Viß╗çt khi c├│ thß╗â.',
    },
    qhviet: {
      home_url: 'https://qhviet.com/',
      google_maps_url: `https://google.com/maps?q=${q}`,
      status: inHcm ? 'fallback_or_cross_check_inside_hcm' : 'primary_cross_check_outside_hcm',
      note: inHcm ? 'D├╣ng fallback/cross-check khi QHHCM thiß║┐u dß╗» liß╗çu.' : 'D├╣ng c├╣ng Guland cho khu vß╗▒c ngo├ái TP.HCM.'
    },
  };
}

function slugify(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/─æ/g, 'd').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function lookupOfficialFunctionalLots(lat, lon) {
  const identify = await postForm(`${OFFICIAL}/computing/930/api/v3.1/a-z/all`, { Lat: lat, Lon: lon });
  const raw = identify.data || identify.text;
  const qhpk = raw?.QHPK ? safeJsonParse(raw.QHPK) : null;
  const lots = Array.isArray(qhpk) ? qhpk.map(f => ({
    gid: f.properties?.gid,
    maopho: f.properties?.maopho,
    chucnang: f.properties?.chucnang,
    dientich: f.properties?.dientich,
    rgbcolor: f.properties?.rgbcolor,
  })).filter(x => x.gid) : [];

  const details = [];
  for (const lot of lots.slice(0, 8)) {
    const detailUrl = `${OFFICIAL}/api/qhpksdd/${lot.gid}`;
    const detailRes = await fetch(detailUrl).then(async r => ({ status: r.status, text: await r.text() })).catch(e => ({ error: String(e) }));
    let detail = safeJsonParse(detailRes.text) || null;
    if (detail && typeof detail === 'object') {
      detail = lowercaseKeys(detail);
      let mixed = null;
      if (String(detail.linktable) === '1') {
        const hhUrl = `${OFFICIAL}/api/qhpksdd/hh/${lot.gid}`;
        const hhRes = await fetch(hhUrl).then(async r => ({ status: r.status, text: await r.text() })).catch(e => ({ error: String(e) }));
        mixed = safeJsonParse(hhRes.text);
      }
      details.push({ ...lot, source_url: detailUrl, detail, mixed_source_url: mixed ? `${OFFICIAL}/api/qhpksdd/hh/${lot.gid}` : null, mixed });
    } else {
      details.push({ ...lot, source_url: detailUrl, error: detailRes.error || detailRes.text });
    }
  }
  return { identify_raw: raw, lots, details };
}

function safeJsonParse(s) {
  if (typeof s !== 'string') return s || null;
  try { return JSON.parse(s); } catch { return null; }
}

function lowercaseKeys(obj) {
  const out = {};
  for (const [k, v] of Object.entries(obj || {})) out[k.toLowerCase()] = v;
  return out;
}

function normalizeText(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/─æ/g, 'd').replace(/─É/g, 'D').toLowerCase();
}

function lotPriority(row) {
  const text = normalizeText([row.maopho, row.chucnang, row.detail?.chucnangsdd].filter(Boolean).join(' '));
  if (/dat\s+o|\bo\b|odt|ont|dan cu|nha o|hon hop.*o|phuc hop.*o/.test(text)) return 100;
  if (/thuong mai|dich vu|tmdv|tm\s*-?\s*dv|phuc hop|hon hop/.test(text)) return 90;
  if (/\bskc\b|san xuat|cong nghiep|kho bai|co so san xuat/.test(text)) return 80;
  if (/dat giao thong|\bdgt\b|\bgt\b/.test(text)) return 5;
  if (/cong vien|cay xanh|mat nuoc/.test(text)) return 10;
  return 50;
}

function mixedPriority(row) {
  const text = normalizeText([row.chucnangsdd, row.chucnang, row.maopho].filter(Boolean).join(' '));
  if (/dat\s+o|\bo\b|odt|ont|dan cu|nha o/.test(text)) return 100;
  if (/thuong mai|dich vu|tmdv|tm\s*-?\s*dv/.test(text)) return 90;
  if (/\bskc\b|san xuat|cong nghiep|kho bai|co so san xuat/.test(text)) return 80;
  if (/phuc hop|hon hop/.test(text)) return 75;
  return 50;
}

function normalizeMixedRows(mixed) {
  const rows = Array.isArray(mixed) ? mixed : (Array.isArray(mixed?.data) ? mixed.data : []);
  return rows.map(r => lowercaseKeys(r)).sort((a, b) => mixedPriority(b) - mixedPriority(a));
}

function pickOfficialDetail(details) {
  const eligible = (details || []).filter(d => d.detail && (d.detail.chucnangsdd || d.detail.tangcao || d.detail.matdo || d.detail.hesosdd || d.detail.danso));
  eligible.sort((a, b) => lotPriority(b) - lotPriority(a));
  return eligible[0] || null;
}

async function lookupHcmPlanning(lat, lon) {
  const inHcm = isLikelyHcmCoordinate(Number(lat), Number(lon));
  const districtPlanning = inHcm ? await postForm(`${OFFICIAL}/api/doan/ranhqhpk`, { Lat: lat, Lon: lon }) : { data: null, skipped: 'outside_hcm' };
  const officialLots = inHcm ? await lookupOfficialFunctionalLots(lat, lon).catch(e => ({ error: String(e) })) : { skipped: 'outside_hcm' };
  const osm = await reverseGeocode(lat, lon).catch(() => null);
  const nearbyOsm = await lookupNearbyOsmContext(lat, lon).catch(() => null);
  const locationHint = osm ? {
    display_name: osm.display_name,
    road: osm.address?.road || osm.address?.pedestrian || osm.address?.footway || osm.address?.path || osm.address?.residential,
    neighbourhood: osm.address?.neighbourhood || osm.address?.quarter,
    suburb: osm.address?.suburb,
    ward: osm.address?.city_district || osm.address?.borough || osm.address?.suburb,
    district: osm.address?.county || osm.address?.city_district || osm.address?.town,
    city: osm.address?.city || osm.address?.town || osm.address?.municipality,
    state: osm.address?.state,
    postcode: osm.address?.postcode,
    nearest_road: nearbyOsm?.nearest_road || null,
    nearest_pois: nearbyOsm?.nearest_pois || [],
    nearby_radius_m: nearbyOsm?.radius_m || null,
  } : null;

  return {
    input: { lat: Number(lat), lon: Number(lon) },
    location_hint: locationHint,
    official_sources: {
      district_planning_endpoint: `${OFFICIAL}/api/doan/ranhqhpk`,
      parcel_endpoint: `${OFFICIAL}/computing/930/api/v3.1/a-z/all`,
      official_web: 'https://thongtinquyhoach.hochiminhcity.gov.vn/',
      status: inHcm ? 'enabled_for_hcm' : 'skipped_outside_hcm',
    },
    third_party_sources: buildThirdPartyLinks(lat, lon, locationHint),
    district_planning: districtPlanning.data,
    official_lots: officialLots,
    notes: [
      'district_planning gives approved planning boundary/project info and population at project level.',
      'official_lots reads QHPK functional lots from the official identify endpoint, then calls /api/qhpksdd/{gid} and /api/qhpksdd/hh/{gid} for population/storeys/density/FAR when available.',
      'Source priority: inside TP.HCM use official Th├┤ng tin quy hoß║ích TP.HCM first; if missing/locked, fallback/cross-check with QH Viß╗çt + Guland.',
      'Source priority: outside TP.HCM use Guland + QH Viß╗çt and skip HCMC official endpoints.',
    ],
  };
}

function summarize(report) {
  const qh = Array.isArray(report.district_planning) ? report.district_planning[0] : null;
  const officialDetail = pickOfficialDetail(report.official_lots?.details);
  const mixedRows = normalizeMixedRows(officialDetail?.mixed);
  const mixedFirst = mixedRows?.[0] || null;
  const detail = officialDetail?.detail || null;
  return {
    input: report.input,
    location: report.location_hint,
    planning_project: qh ? {
      TenDoAn: qh.TenDoAn,
      TenQH: qh.TenQH,
      DienTich_ha: qh.DienTich,
      DanSoQH: qh.DanSoQH,
      DanSoHH: qh.DanSoHH,
      CoQuanPD: qh.CoQuanPD,
      SoQD: qh.SoQD,
      NgayDuyet: qh.NgayDuyet,
      TrangThai: qh.TrangThai,
      MaQHPKRanh: qh.MaQHPKRanh,
      DCCB: qh.DCCB?.map(d => ({ TenDoAn: d.TenDoAn, SoQD: d.SoQD, NgayDuyet: d.NgayDuyet, MaDCCBRanh: d.MaDCCBRanh })) || [],
    } : null,
    official_functional_lots: report.official_lots,
    exact_indicators: {
      ma_o_pho: detail?.maopho || officialDetail?.maopho || null,
      chuc_nang_dat: mixedFirst?.chucnangsdd || detail?.chucnangsdd || officialDetail?.chucnang || null,
      dien_tich: mixedFirst?.dientich || detail?.dientich || officialDetail?.dientich || null,
      dan_so_lo_o_pho: mixedFirst?.danso || detail?.danso || null,
      mat_do_xay_dung: mixedFirst?.matdo || detail?.matdo || null,
      tang_cao: mixedFirst?.tangcao || detail?.tangcao || null,
      chieu_cao: detail?.chieucao || null,
      he_so_su_dung_dat: mixedFirst?.hesosdd || detail?.hesosdd || null,
      mixed_functions: mixedRows.map(r => ({
        chuc_nang_dat: r.chucnangsdd || r.chucnang || null,
        dien_tich: r.dientich || null,
        dan_so: r.danso || null,
        tang_cao: r.tangcao || null,
        mat_do_xay_dung: r.matdo || null,
        he_so_su_dung_dat: r.hesosdd || null,
      })),
      selection_rule: '╞»u ti├¬n ├┤/chß╗⌐c n─âng ─æß║Ñt ß╗ƒ, th╞░╞íng mß║íi dß╗ïch vß╗Ñ, SKC; nß║┐u ─æß║Ñt phß╗⌐c hß╗úp/hß╗ùn hß╗úp th├¼ giß╗» ─æß║ºy ─æß╗º c├íc cß║Ñu phß║ºn trong mixed_functions.',
      source_url: officialDetail?.source_url || null,
      mixed_source_url: officialDetail?.mixed_source_url || null,
      status: officialDetail ? 'official_functional_lot_confirmed' : 'not_confirmed_yet',
      reason: officialDetail ? 'official qhpksdd detail endpoint returned functional-lot indicators' : (typeof report.official_lots?.identify_raw === 'string' ? report.official_lots.identify_raw.slice(0, 200) : 'official functional-lot identify did not return a detail row'),
    },
    cross_check_links: report.third_party_sources,
    confidence: {
      location: report.location_hint ? 'medium_high' : 'medium',
      district_planning: qh ? 'high_official_endpoint' : 'low',
      exact_indicators: officialDetail ? 'high_official_qhpksdd_endpoint' : 'low_until_vector_identify_succeeds',
    },
  };
}

function toMarkdown(summary) {
  const p = summary.planning_project;
  const e = summary.exact_indicators;
  return [
    `Tß╗ìa ─æß╗Ö: ${summary.input.lat}, ${summary.input.lon}`,
    `Vß╗ï tr├¡: ${summary.location?.display_name || 'ch╞░a x├íc ─æß╗ïnh'}`,
    '',
    'Nguß╗ôn ch├¡nh thß╗æng TP.HCM:',
    p ? `- ─Éß╗ô ├ín: ${p.TenDoAn}\n- Diß╗çn t├¡ch: ${p.DienTich_ha} ha\n- D├ón sß╗æ QH: ${p.DanSoQH}\n- Q─É: ${p.SoQD} ng├áy ${p.NgayDuyet}\n- Trß║íng th├íi: ${p.TrangThai}` : '- Ch╞░a c├│ dß╗» liß╗çu',
    '',
    'Chß╗ë ti├¬u ├┤ phß╗æ/l├┤:',
    `- ├ö chß╗⌐c n─âng: ${e.ma_o_pho || 'ch╞░a chß╗æt'}`,
    `- Chß╗⌐c n─âng ─æß║Ñt: ${e.chuc_nang_dat || 'ch╞░a chß╗æt'}`,
    `- Diß╗çn t├¡ch: ${e.dien_tich || 'ch╞░a chß╗æt'}`,
    `- D├ón sß╗æ: ${e.dan_so_lo_o_pho || 'ch╞░a chß╗æt'}`,
    `- M─ÉXD: ${e.mat_do_xay_dung || 'ch╞░a chß╗æt'}`,
    `- Tß║ºng cao: ${e.tang_cao || 'ch╞░a chß╗æt'}`,
    `- Chiß╗üu cao: ${e.chieu_cao || 'ch╞░a chß╗æt'}`,
    `- HSSD─É: ${e.he_so_su_dung_dat || 'ch╞░a chß╗æt'}`,
    `- Nguß╗ôn ├┤ chß╗⌐c n─âng: ${e.source_url || 'ch╞░a c├│'}`,
    e.mixed_functions?.length ? 'C├íc cß║Ñu phß║ºn ─æß║Ñt phß╗⌐c hß╗úp/hß╗ùn hß╗úp ╞░u ti├¬n:' : null,
    ...(e.mixed_functions || []).map((r, idx) => `  ${idx + 1}. ${r.chuc_nang_dat || 'Kh├┤ng r├╡'} | DT: ${r.dien_tich || '-'} | D├ón sß╗æ: ${r.dan_so || '-'} | Tß║ºng: ${r.tang_cao || '-'} | M─ÉXD: ${r.mat_do_xay_dung || '-'} | HSSD─É: ${r.he_so_su_dung_dat || '-'}`),
    e.mixed_source_url ? `- Nguß╗ôn bß║úng hß╗ùn hß╗úp: ${e.mixed_source_url}` : null,
    `- Rule chß╗ìn: ${e.selection_rule || 'ch╞░a c├│'}`,
    `- Ghi ch├║: ${e.reason}`,
    '',
    'Link ─æß╗æi chiß║┐u:',
    `- Guland: ${summary.cross_check_links.guland.coordinate_planning_url}`,
    `- QH Viß╗çt: ${summary.cross_check_links.qhviet.home_url}`,
  ].filter(x => x !== null).join('\n');
}

if (require.main === module) {
  const parsed = parseCoordinateInput(process.argv.slice(2));
  if (!parsed) {
    console.error('Usage: node bds_planning_checker.js <lat> <lon|map link>');
    process.exit(2);
  }
  lookupHcmPlanning(parsed.lat, parsed.lon)
    .then(r => {
      const s = summarize(r);
      console.log(JSON.stringify(s, null, 2));
      console.log('\n--- MARKDOWN ---\n' + toMarkdown(s));
    })
    .catch(e => { console.error(e); process.exit(1); });
}

module.exports = { parseCoordinateInput, lookupHcmPlanning, lookupOfficialFunctionalLots, lookupGulandPriceStats, summarize, toMarkdown, buildGulandCheckPlanUrl, fetchGulandCheckPlanJson };
