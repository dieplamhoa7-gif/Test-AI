import { lookupK1LandFee } from './k1.js';

function corsHeaders() {
  return {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'access-control-allow-headers': 'content-type, authorization',
    'cache-control': 'no-store',
  };
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders(), 'content-type': 'application/json; charset=utf-8' },
  });
}

function redact(s) {
  return String(s || '').replace(/[A-Za-z0-9_\-]{24,}/g, '[redacted]');
}

function cleanVi(s) { return String(s || '').replace(/Ð/g, 'Đ').replace(/ð/g, 'đ'); }

async function reverseGeocode(lat, lon) {
  const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&accept-language=vi`, {
    headers: { 'user-agent': 'LHRealEstateWorker/1.0 (contact: lhrealestate.web.app)' },
  });
  if (!r.ok) throw new Error('reverse_geocode_failed_' + r.status);
  const data = await r.json();
  const a = data.address || {};
  const road = cleanVi(a.road || data.name || '');
  const ward = cleanVi(a.suburb || a.quarter || a.neighbourhood || a.city_district || '');
  let district = cleanVi(a.district || a.city || a.county || '');
  let city = cleanVi(a.state || a.city || 'Thành phố Hồ Chí Minh');
  const display = cleanVi(data.display_name || [road, ward, district, city].filter(Boolean).join(', '));
  return { road, ward, suburb: ward, district, city, display_name: display, raw: data };
}

function normalizeManualGeo(payload) {
  let ward = cleanVi(String(payload.ward || payload.phuong || '').trim());
  let road = cleanVi(String(payload.road || payload.duong || '').trim());
  let district = cleanVi(String(payload.district || '').trim());
  let city = cleanVi(String(payload.city || 'Thành phố Hồ Chí Minh').trim());
  if (/Hòa Hưng/i.test([ward, road].join(' '))) {
    ward = 'Phường Hòa Hưng';
    city = 'Thành phố Hồ Chí Minh';
    if (/Thủ Đức/i.test(district)) district = '';
  }
  return { ward, suburb: ward, road, district, city, display_name: [road, ward, district, city].filter(Boolean).join(', ') };
}

async function handleK1Search(request) {
  const payload = await request.json().catch(() => ({}));
  const geo = normalizeManualGeo(payload);
  if (!geo.ward || !geo.road) return json({ ok:false, error:'ward_and_road_required' }, 400);
  const k1 = await lookupK1LandFee({ lat:null, lon:null, geoLocation:geo, text:payload.text || '', landUse:payload.landUse || 'ODT', position:payload.position || 'VT1', planningMultiplier:1 });
  if (k1 && k1.error) return json({ ok:false, location:geo, error:k1.error, k1 }, 422);
  return json({ ok:true, location:geo, k1 });
}

async function resolveGeoFromPayload(payload) {
  const lat = Number(payload.lat), lon = Number(payload.lon ?? payload.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new Error('lat/lon required');
  let geo = payload.location_context && typeof payload.location_context === 'object' ? payload.location_context : await reverseGeocode(lat, lon);
  geo = { ...geo, road: cleanVi(geo.road || ''), ward: cleanVi(geo.ward || geo.suburb || ''), suburb: cleanVi(geo.suburb || geo.ward || ''), district: cleanVi(geo.district || ''), city: cleanVi(geo.city || 'Thành phố Hồ Chí Minh'), display_name: cleanVi(geo.display_name || '') };
  return { lat, lon, geo };
}

async function handleK1Lookup(request) {
  const payload = await request.json().catch(() => ({}));
  let got;
  try { got = await resolveGeoFromPayload(payload); } catch (e) { return json({ ok:false, error:e.message }, 400); }
  const { lat, lon, geo } = got;
  const k1 = await lookupK1LandFee({ lat, lon, geoLocation:geo, text:payload.text || '', landUse:payload.landUse || 'ODT', position:payload.position || 'VT1', planningMultiplier:1 });
  if (k1 && k1.error) return json({ ok:false, location:geo, error:k1.error, k1 }, 422);
  return json({ ok:true, location:geo, k1 });
}

async function handlePlanningLookup(request) {
  const payload = await request.json().catch(() => ({}));
  let got;
  try { got = await resolveGeoFromPayload(payload); } catch (e) { return json({ ok:false, error:e.message }, 400); }
  const { lat, lon, geo } = got;
  return json({
    ok: true,
    degraded: true,
    location: geo,
    planning: {
      summary: 'Bản cloud-free đã xác định vị trí bằng geocoding công khai. QH Việt/Guland cần browser nên chưa chạy trên Worker free.',
      location: geo,
      zoning: 'Cần đối chiếu QH Việt/Guland hoặc nguồn quy hoạch chính thức.',
      warnings: ['Worker free không chạy Chrome/Playwright; kết quả này là fallback vị trí, chưa phải kết luận quy hoạch chính thức.']
    },
    raw: { lat, lon, source: 'OpenStreetMap/Nominatim reverse geocoding' },
    qhviet: { ok:false, degraded:true, error:'browser_backend_required' },
    guland: { ok:false, degraded:true, error:'browser_backend_required' }
  });
}

async function handleLegalAsk(request) {
  const payload = await request.json().catch(() => ({}));
  const q = cleanVi(payload.question || payload.query || '');
  return json({
    ok: true,
    degraded: true,
    answer: [
      'Bản cloud-free đã nhận câu hỏi pháp lý nhưng chưa nối được AI 9Router public endpoint.',
      'Checklist kiểm tra tối thiểu: (1) pháp lý quyền sử dụng đất/sổ; (2) quy hoạch và lộ giới; (3) nghĩa vụ tài chính đất; (4) hạn chế giao dịch/thế chấp/tranh chấp; (5) điều kiện đầu tư/xây dựng nếu là dự án.',
      'Không dùng kết quả này thay cho ý kiến luật sư hoặc văn bản cơ quan nhà nước.'
    ].join('\n'),
    citations: [],
    question: q,
    note: 'Cần endpoint public 9Router hoặc migrate legal corpus + model khác để trả lời sâu.'
  });
}

async function handleBdsStart(request) {
  const payload = await request.json().catch(() => ({}));
  const id = 'cf_' + Date.now().toString(36);
  return json({ ok:true, jobId:id, statusUrl:'/bds/valuation/status/' + id, cloudFallback:true, input:payload });
}

async function handleBdsStatus(request, path) {
  const id = path.split('/').pop() || 'cf_job';
  return json({
    ok: true,
    jobId: id,
    status: 'done',
    stage: 'done',
    message: 'Hoàn tất báo cáo R&D fallback trên Worker free.',
    result: {
      ok: true,
      mode: 'cloud-free-fallback',
      confidence: 'Sơ bộ',
      sample_count: 0,
      price_sample_count: 0,
      area: 'Khu vực theo tọa độ đã nhập',
      intro: 'Báo cáo R&D sơ bộ chạy trên Cloudflare Worker free. Chưa scrape Batdongsan/Guland vì cần browser backend.',
      comparables: [],
      investor_summary: { location_bullets:['Đã nhận tọa độ và tạo báo cáo sơ bộ cloud-free.'], confidence:'Sơ bộ', price_rationale:'Chưa có mẫu giá thật vì Worker free không chạy browser scraping.' },
      report: 'R&D cloud-free fallback: cần backend có browser/Playwright hoặc nguồn dữ liệu public API để scrape mẫu giá thật khi máy chủ local tắt.',
      text: 'R&D cloud-free fallback: chưa có mẫu giá thật. Cần migrate scraper sang dịch vụ có browser hoặc dùng nguồn API public.'
    }
  });
}

async function proxyChat(request, env) {
  const base = String(env.NINEROUTER_BASE_URL || '').replace(/\/$/, '');
  const key = env.NINEROUTER_API_KEY;
  const payload = await request.json().catch(() => ({}));
  payload.model = payload.model || env.NINEROUTER_MODEL || 'APIBDS';
  if (!base) {
    const fallbackContent = JSON.stringify({
      ok: false,
      cloudFallback: true,
      warning: 'AI/OCR chưa chạy trên Worker vì chưa có 9Router public base URL. NVTC/K1 vẫn dùng nguồn PDF/K1 cloud-free; nếu có bản vẽ cần đọc diện tích tự động thì cần bật backend local hoặc cấu hình endpoint AI public.',
      items: [],
      duong: '',
      doan: '',
      viTri: 1
    });
    return json({
      id: 'chatcmpl-cloudfallback',
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: payload.model,
      choices: [{ index: 0, message: { role: 'assistant', content: fallbackContent }, finish_reason: 'stop' }],
      usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      cloudFallback: true,
      note: 'NINEROUTER_BASE_URL chưa được cấu hình; trả fallback OpenAI-compatible để frontend không gãy.'
    }, 200);
  }
  if (!key) return json({ ok:false, error:'server_missing_ninerouter_secret' }, 500);
  if (!payload.model || /^claude/i.test(String(payload.model))) payload.model = env.NINEROUTER_MODEL || 'APIBDS';
  try {
    const upstream = await fetch(base + '/chat/completions', {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: 'Bearer ' + key },
      body: JSON.stringify(payload),
    });
    const text = await upstream.text();
    return new Response(text, {
      status: upstream.status,
      headers: { ...corsHeaders(), 'content-type': upstream.headers.get('content-type') || 'application/json; charset=utf-8' },
    });
  } catch (err) {
    return json({ ok:false, error:redact(err && err.message || err) }, 502);
  }
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response('', { status: 204, headers: corsHeaders() });
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, '') || '/';
    if (request.method === 'GET' && path === '/health') {
      return json({ ok:true, runtime:'cloudflare-workers-free', model:env.NINEROUTER_MODEL || 'APIBDS', hasKey:!!env.NINEROUTER_API_KEY, hasPublicBase:!!env.NINEROUTER_BASE_URL, k1:true });
    }
    if (request.method === 'POST' && path === '/nvtc/k1-search') return handleK1Search(request);
    if (request.method === 'POST' && path === '/nvtc/k1-lookup') return handleK1Lookup(request);
    if (request.method === 'POST' && path === '/planning/lookup') return handlePlanningLookup(request);
    if (request.method === 'POST' && path === '/legal/ask') return handleLegalAsk(request);
    if (request.method === 'POST' && path === '/bds/valuation/start') return handleBdsStart(request);
    if (request.method === 'GET' && path.startsWith('/bds/valuation/status/')) return handleBdsStatus(request, path);
    if (request.method === 'POST' && path === '/v1/chat/completions') return proxyChat(request, env);
    return json({ ok:false, error:'endpoint_not_available_on_free_worker_yet', path, note:'Backend free đang online cố định. Endpoint này cần migrate logic khỏi Chrome/Python local hoặc dùng dịch vụ browser/server riêng.' }, 501);
  }
};
