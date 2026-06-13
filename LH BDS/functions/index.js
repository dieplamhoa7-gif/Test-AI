const { onRequest } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const logger = require('firebase-functions/logger');

const NINEROUTER_API_KEY = defineSecret('NINEROUTER_API_KEY');
const NINEROUTER_BASE_URL = process.env.NINEROUTER_BASE_URL || 'https://api.9router.com/v1';
const NINEROUTER_MODEL = process.env.NINEROUTER_MODEL || 'APIBDS';

function setCors(res) {
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.set('Access-Control-Allow-Headers', 'content-type, authorization');
  res.set('Cache-Control', 'no-store');
}

function safeError(err) {
  const msg = String((err && err.message) || err || 'unknown_error');
  // Never echo env/secret-like values.
  return msg.replace(/[A-Za-z0-9_\-]{24,}/g, '[redacted]');
}

exports.api = onRequest({
  region: 'asia-southeast1',
  cors: false,
  secrets: [NINEROUTER_API_KEY],
  timeoutSeconds: 300,
  memory: '1GiB',
}, async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(204).send('');

  const path = (req.path || req.url || '/').split('?')[0];

  if (req.method === 'GET' && path === '/health') {
    return res.json({ ok: true, runtime: 'firebase-functions', model: NINEROUTER_MODEL, hasKey: !!NINEROUTER_API_KEY.value() });
  }

  if (req.method === 'POST' && path === '/v1/chat/completions') {
    try {
      const key = NINEROUTER_API_KEY.value();
      if (!key) return res.status(500).json({ error: 'server_missing_9router_secret' });
      const payload = typeof req.body === 'object' && req.body ? { ...req.body } : {};
      payload.model = payload.model || NINEROUTER_MODEL;
      if (!payload.model || /^claude/i.test(String(payload.model))) payload.model = NINEROUTER_MODEL;
      const upstream = await fetch(NINEROUTER_BASE_URL.replace(/\/$/, '') + '/chat/completions', {
        method: 'POST',
        headers: { 'content-type': 'application/json', authorization: 'Bearer ' + key },
        body: JSON.stringify(payload),
      });
      const text = await upstream.text();
      res.status(upstream.status);
      res.set('content-type', upstream.headers.get('content-type') || 'application/json');
      return res.send(text);
    } catch (err) {
      logger.error('chat proxy failed', { error: safeError(err) });
      return res.status(500).json({ error: safeError(err) });
    }
  }

  return res.status(501).json({
    ok: false,
    error: 'endpoint_not_migrated_to_cloud_yet',
    path,
    note: 'This stable cloud API is active, but this endpoint still needs migration from the local Chrome/Python backend.'
  });
});
