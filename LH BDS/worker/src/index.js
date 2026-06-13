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

async function proxyChat(request, env) {
  const base = String(env.NINEROUTER_BASE_URL || '').replace(/\/$/, '');
  const key = env.NINEROUTER_API_KEY;
  if (!base) return json({ ok:false, error:'ninerouter_public_base_url_not_configured', note:'9Router hiện đang chạy local trên máy chủ cũ; cần endpoint public để Worker proxy trực tiếp.' }, 501);
  if (!key) return json({ ok:false, error:'server_missing_ninerouter_secret' }, 500);
  const payload = await request.json().catch(() => ({}));
  payload.model = payload.model || env.NINEROUTER_MODEL || 'APIBDS';
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
      return json({ ok:true, runtime:'cloudflare-workers-free', model:env.NINEROUTER_MODEL || 'APIBDS', hasKey:!!env.NINEROUTER_API_KEY, hasPublicBase:!!env.NINEROUTER_BASE_URL });
    }
    if (request.method === 'POST' && path === '/v1/chat/completions') return proxyChat(request, env);
    return json({ ok:false, error:'endpoint_not_available_on_free_worker_yet', path, note:'Backend free đang online cố định. Endpoint này cần migrate logic khỏi Chrome/Python local hoặc dùng dịch vụ browser/server riêng.' }, 501);
  }
};
