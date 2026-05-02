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

function readJson(name) {
  return JSON.parse(readJsonFile(name));
}

function rsCacheFile() {
  return fs.existsSync(path.join(DATA, 'rs_levels_hsx_all_cache.json')) ? 'rs_levels_hsx_all_cache.json' : 'rs_levels_only_cache.json';
}

function itemFromRs(row) {
  const symbol = String(row.symbol || '').toUpperCase();
  return {
    ticker: symbol,
    symbol,
    price: row.price || 0,
    changePct: row.changePct || 0,
    volume: row.volume || 0,
    sector: 'Khác',
    technical: {
      trend: row.marketStructureDay || 'Trung tính',
      supportDay: row.supportDay,
      resistanceDay: row.resistanceDay,
      supportDay2: row.supportDay2,
      resistanceDay2: row.resistanceDay2,
      activeSupportDay: row.activeSupportDay,
      activeResistanceDay: row.activeResistanceDay,
      supportLevelsDay: row.supportLevelsDay || [],
      resistanceLevelsDay: row.resistanceLevelsDay || [],
      supportWeek: row.supportWeek,
      resistanceWeek: row.resistanceWeek,
      activeSupportWeek: row.activeSupportWeek,
      activeResistanceWeek: row.activeResistanceWeek,
      supportMonth: row.supportMonth,
      resistanceMonth: row.resistanceMonth,
      activeSupportMonth: row.activeSupportMonth,
      activeResistanceMonth: row.activeResistanceMonth,
      pivotDay: row.pivotDay,
      pivotWeek: row.pivotWeek,
      pivotMonth: row.pivotMonth,
      srStatusDay: row.srStatusDay,
      srStatusWeek: row.srStatusWeek,
      srStatusMonth: row.srStatusMonth,
      atr: row.atr,
      vwapDay: row.vwapDay,
      donchianHighDay: row.donchianHighDay,
      donchianLowDay: row.donchianLowDay,
      donchianMidDay: row.donchianMidDay,
      marketStructureDay: row.marketStructureDay,
      ma20: row.ma20Anchor,
      ma50: row.ma50Anchor,
      ma200: row.ma200Anchor,
      recommendation: row.srStatusDay || 'Theo dõi vùng hỗ trợ/kháng cự từ cache R/S.'
    },
    financial: {}
  };
}

function marketDataFromRs() {
  const cache = readJson(rsCacheFile());
  const rows = Array.isArray(cache.items) ? cache.items : [];
  const preferred = ['MWG','FPT','HPG','SSI'];
  const chosen = preferred.map(s => rows.find(x => String(x.symbol).toUpperCase() === s)).filter(Boolean);
  const items = (chosen.length ? chosen : rows.slice(0, 30)).map(itemFromRs);
  return { items, updatedAt: cache.createdAt, status: 'rs-cache-node-fallback' };
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
      return send(res, 200, readJsonFile(rsCacheFile()));
    }
    if (pathname === '/market-overview') {
      return send(res, 200, JSON.stringify({ items: [], status: 'cache-only-node-fallback' }));
    }
    if (pathname === '/market-data') {
      return send(res, 200, JSON.stringify(marketDataFromRs()));
    }
    if (pathname.startsWith('/market-data/')) {
      const symbol = decodeURIComponent(pathname.split('/').pop() || '').toUpperCase();
      const cache = readJson(rsCacheFile());
      const row = (cache.items || []).find(x => String(x.symbol || '').toUpperCase() === symbol);
      if (!row) return notFound(res);
      return send(res, 200, JSON.stringify(itemFromRs(row)));
    }
    if (pathname === '/market-symbols') {
      const q = String(url.searchParams.get('query') || '').toUpperCase();
      const limit = Math.max(1, Math.min(50, Number(url.searchParams.get('limit') || 20)));
      const cache = readJson(rsCacheFile());
      const items = (cache.items || []).filter(x => !q || String(x.symbol || '').toUpperCase().includes(q)).slice(0, limit).map(x => ({ symbol: String(x.symbol || '').toUpperCase(), name: '' }));
      return send(res, 200, JSON.stringify(items));
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
