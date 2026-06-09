// Local-only 9Router proxy for NVTC Dao Tri web app.
// Keeps the BDS 9Router key out of browser HTML/localStorage.
// Usage: node nvtc_9router_proxy.js
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.NVTC_PROXY_PORT || 8787);
const LOCAL_9ROUTER_BASE = process.env.NINEROUTER_BASE_URL || 'http://localhost:20128/v1';
const FALLBACK_MODEL = process.env.NINEROUTER_BDS_MODEL || process.env.NINEROUTER_MODEL || 'APIBDS';
const PRIVATE_KEY_FILE = path.join(__dirname, '9router_private_keys', '9router_split_keys_private.txt');

function readBdsKey() {
  const envKey = process.env.BDS_9ROUTER_API_KEY || process.env.NINEROUTER_API_KEY || process.env.OPENAI_API_KEY;
  if (envKey) return envKey.trim();
  try {
    const txt = fs.readFileSync(PRIVATE_KEY_FILE, 'utf8');
    const m = txt.match(/^\s*BDS_9ROUTER_API_KEY\s*=\s*(.+?)\s*$/m) || txt.match(/^\s*NINEROUTER_API_KEY\s*=\s*(.+?)\s*$/m);
    return m ? m[1].trim().replace(/^['"]|['"]$/g, '') : '';
  } catch { return ''; }
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS, GET');
  res.setHeader('Access-Control-Allow-Headers', 'content-type, authorization');
}

const server = http.createServer(async (req, res) => {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, {'content-type':'application/json'});
    return res.end(JSON.stringify({ok:true, base:LOCAL_9ROUTER_BASE, model:FALLBACK_MODEL, hasKey:!!readBdsKey()}));
  }
  if (req.method !== 'POST' || req.url !== '/v1/chat/completions') {
    res.writeHead(404, {'content-type':'application/json'});
    return res.end(JSON.stringify({error:'not_found'}));
  }
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const payload = JSON.parse(body || '{}');
      payload.model = payload.model || FALLBACK_MODEL;
      if (!payload.model || /^claude/i.test(payload.model)) payload.model = FALLBACK_MODEL;
      const key = readBdsKey();
      const headers = {'content-type':'application/json'};
      if (key) headers.authorization = 'Bearer ' + key;
      const upstream = await fetch(LOCAL_9ROUTER_BASE.replace(/\/$/, '') + '/chat/completions', {
        method: 'POST', headers, body: JSON.stringify(payload)
      });
      const text = await upstream.text();
      res.writeHead(upstream.status, {'content-type': upstream.headers.get('content-type') || 'application/json'});
      res.end(text);
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'});
      res.end(JSON.stringify({error: String(e && e.message || e)}));
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`NVTC 9Router proxy listening on http://0.0.0.0:${PORT}`);
  console.log(`Forwarding to ${LOCAL_9ROUTER_BASE} with model ${FALLBACK_MODEL}`);
});
