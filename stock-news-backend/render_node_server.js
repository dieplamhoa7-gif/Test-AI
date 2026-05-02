const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 10000;
const ROOT = __dirname;
const DATA = path.join(ROOT, 'data');
const HTML_PATH = path.join(DATA, 'dashboard_static.html');

function send(res, status, body, type = 'application/json; charset=utf-8') {
  res.writeHead(status, {
    'Content-Type': type,
    'Cache-Control': type.startsWith('text/html') ? 'no-store, max-age=0' : 'public, max-age=60, stale-while-revalidate=300',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
  });
  res.end(body);
}

function readJsonFile(name) {
  return fs.readFileSync(path.join(DATA, name), 'utf8');
}

function notFound(res) {
  send(res, 404, JSON.stringify({ detail: 'Not Found' }));
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;
  try {
    if (pathname === '/health') {
      return send(res, 200, JSON.stringify({ ok: true, service: 'web', runtime: 'node-cache-server' }));
    }
    if (pathname === '/' || pathname === '/stocks' || pathname === '/warrants' || pathname === '/news-page' || pathname.startsWith('/stocks/') || pathname.startsWith('/warrants/')) {
      const html = fs.readFileSync(HTML_PATH, 'utf8');
      return send(res, 200, html, 'text/html; charset=utf-8');
    }
    if (pathname === '/strategy-results-cache') {
      return send(res, 200, readJsonFile('strategy_results_cache.json'));
    }
    if (pathname === '/strategy-matrix-cache') {
      return send(res, 200, readJsonFile('strategy_matrix_cache.json'));
    }
    if (pathname === '/rs-levels-cache') {
      const file = fs.existsSync(path.join(DATA, 'rs_levels_hsx_all_cache.json')) ? 'rs_levels_hsx_all_cache.json' : 'rs_levels_only_cache.json';
      return send(res, 200, readJsonFile(file));
    }
    if (pathname === '/market-overview') {
      return send(res, 200, JSON.stringify({ items: [], status: 'cache-only-node-fallback' }));
    }
    if (pathname === '/market-data' || pathname.startsWith('/market-data/')) {
      return send(res, 200, JSON.stringify({ items: [], status: 'cache-only-node-fallback' }));
    }
    if (pathname === '/warrants-data') {
      return send(res, 200, JSON.stringify({ items: [], status: 'cache-only-node-fallback' }));
    }
    if (pathname === '/news') {
      return send(res, 200, JSON.stringify({ items: [], status: 'cache-only-node-fallback' }));
    }
    return notFound(res);
  } catch (err) {
    return send(res, 500, JSON.stringify({ detail: 'Server Error', error: String(err && err.message || err) }));
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Hoa investment cache server listening on ${PORT}`);
});
