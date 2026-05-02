const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 10000;
const ROOT = __dirname;
const DATA = path.join(ROOT, 'data');
const HTML_PATH = path.join(DATA, 'dashboard_static.html');
const WARRANTS_STATIC = path.join(ROOT, 'app', 'warrants', 'warrants_static.json');
const WARRANTS_CATALOG = path.join(ROOT, 'app', 'warrants', 'warrant_catalog.json');

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

function readJsonPath(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function rsCacheFile() {
  return fs.existsSync(path.join(DATA, 'rs_levels_hsx_all_cache.json')) ? 'rs_levels_hsx_all_cache.json' : 'rs_levels_only_cache.json';
}

function strategyInfoFor(symbol) {
  try {
    const cache = readJson('strategy_results_cache.json');
    const out = [];
    for (const st of (cache.strategies || [])) {
      for (const bucket of ['buy', 'watchlist', 'watch', 'items']) {
        for (const x of (st[bucket] || [])) {
          if (String(x.symbol || x.ticker || '').toUpperCase() === symbol) out.push({ ...x, strategyName: st.name || st.id || x.strategy });
        }
      }
    }
    return out;
  } catch (_) { return []; }
}

function itemFromRs(row) {
  const symbol = String(row.symbol || '').toUpperCase();
  const strategyRows = strategyInfoFor(symbol);
  const firstStrategy = strategyRows[0] || {};
  const ind = firstStrategy.entryIndicators || {};
  const recommendation = strategyRows.length
    ? strategyRows.map(x => `${x.strategyName || x.strategy || 'Strategy'}: ${x.action || 'WATCH'} | Mua ${x.entryPrice || x.entry || x.support || '-'} | Target ${x.takeProfit || x.target || '-'} | SL ${x.stopLoss || x.stop || '-'}`).join(' | ')
    : (row.srStatusDay || 'Theo dõi vùng hỗ trợ/kháng cự từ cache R/S.');
  return {
    ticker: symbol,
    symbol,
    price: row.price || 0,
    changePct: row.changePct || 0,
    volume: row.volume || 0,
    sector: 'Khác',
    strategySignals: strategyRows,
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
      relativeStrength: ind.rsi,
      rsi14: ind.rsi,
      macd: ind.macd,
      signal: ind.macdSignal,
      histogram: ind.macdHist,
      volumeRatio: ind.volumeRatio,
      roc20: ind.roc20,
      bbPercent: ind.bbPercent,
      bbUpper: ind.bbUpper,
      bbLower: ind.bbLower,
      adx14: ind.adx,
      plusDi: ind.plusDi,
      minusDi: ind.minusDi,
      zoneState: row.srStatusDay || '',
      setupType: strategyRows.length ? strategyRows.map(x => x.strategyName || x.strategy).join(', ') : 'R/S cache',
      volumeState: ind.volumeRatio ? `Volume ${ind.volumeRatio}x` : '',
      signalScore: firstStrategy.rankScore || 0,
      strategy: recommendation,
      strategyWeek: recommendation,
      strategyMonth: recommendation,
      recommendation,
      recommendationWeek: recommendation,
      recommendationMonth: recommendation
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

function stripHtml(value = '') {
  return String(value)
    .replace(/<\/?strong>/gi, '')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function newsFromCache(limit = 30) {
  const raw = readJson('news_cache.json');
  const items = Array.isArray(raw) ? raw : (Array.isArray(raw.items) ? raw.items : []);
  const cleanItems = items.slice(0, limit).map(item => ({
    ...item,
    title: stripHtml(item.title || ''),
    snippet: stripHtml(item.snippet || item.summary || ''),
    summary: stripHtml(item.summary || item.snippet || ''),
  }));
  return { items: cleanItems, updatedAt: raw.updatedAt || raw.createdAt || null, status: 'news-cache-node-fallback' };
}

function warrantsFromCache(symbols = '') {
  const staticPayload = fs.existsSync(WARRANTS_STATIC) ? readJsonPath(WARRANTS_STATIC) : { items: [] };
  let items = (staticPayload.items || []).map(item => ({ ...item, code: String(item.code || '').toUpperCase() }));
  items = items.filter(item => {
    if (!item.code) return false;
    if (!item.maturityDate || item.daysLeft === undefined || item.daysLeft === null) return false;
    if (Number(item.daysLeft) <= 0) return false;
    const hasPriceInfo = item.marketPrice !== undefined || item.lastPrice !== undefined || item.fairValue !== undefined;
    const underlyingPrice = Number(item.underlyingPrice || 0);
    const exercisePrice = Number(item.exercisePrice || 0);
    return hasPriceInfo && underlyingPrice > 0 && exercisePrice > 0;
  });
  const wanted = String(symbols || '').split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
  if (wanted.length) items = items.filter(x => wanted.includes(String(x.code || '').toUpperCase()));
  return { items, updatedAt: staticPayload.updatedAt || null, status: 'warrants-static-cache-node-fallback' };
}

function allReportSignals() {
  const file = path.join(DATA, 'all_report_signals.json');
  return fs.existsSync(file) ? readJsonPath(file) : [];
}

function normalizeTarget(target, referencePrice = 0) {
  let n = Number(target || 0);
  const price = Number(referencePrice || 0);
  if (price > 0 && n > 0 && n < price * 0.45 && price * 0.8 <= n * 10 && n * 10 <= price * 3.5) n *= 10;
  return n;
}

function fundamentalSignals(symbol, limit = 50) {
  const wanted = String(symbol || '').toUpperCase();
  const reports = allReportSignals().filter(r => String(r.symbol || '').toUpperCase() === wanted);
  const more = (readJson('24hmoney_reports.json').items || []).filter(r => {
    const symbols = Array.isArray(r.symbols) ? r.symbols.map(s => String(s).toUpperCase()) : [];
    return String(r.symbol || '').toUpperCase() === wanted || symbols.includes(wanted);
  }).map(r => ({ symbol: wanted, report_date: r.report_date, title: r.title, source: r.source || '24HMoney', broker: r.source || '24HMoney', url: r.url, source_url: r.url, summary: r.summary, recommendation: 'Báo cáo phân tích', provider: '24HMoney' }));
  const items = reports.concat(more).sort((a,b) => String(b.report_date || '').localeCompare(String(a.report_date || ''))).slice(0, limit);
  return { symbol: wanted, items, total: reports.length + more.length, updatedAt: null, status: items.length ? 'ok-cache-node-fallback' : 'missing' };
}

function fundamentalTopUpside(limit = 20, maxSymbols = 200) {
  const rows = allReportSignals();
  const cache = readJson(rsCacheFile());
  const prices = new Map((cache.items || []).map(x => [String(x.symbol || '').toUpperCase(), Number(x.price || 0)]));
  const grouped = new Map();
  for (const row of rows) {
    const sym = String(row.symbol || '').toUpperCase();
    const target = Number(row.target_price || 0);
    if (!sym || !target) continue;
    if (!grouped.has(sym)) grouped.set(sym, []);
    grouped.get(sym).push(row);
  }
  const items = [];
  for (const [symbol, reports] of grouped.entries()) {
    let price = prices.get(symbol) || 0;
    if (price > 0 && price < 1000) price *= 1000;
    if (!price) continue;
    const targets = reports.map(r => normalizeTarget(r.target_price, price)).filter(v => v > 0);
    if (!targets.length) continue;
    const avgTargetPrice = targets.reduce((a,b) => a+b, 0) / targets.length;
    const latest = reports.slice().sort((a,b) => String(b.report_date || '').localeCompare(String(a.report_date || '')))[0] || {};
    items.push({ symbol, price, rawQuotePrice: prices.get(symbol) || 0, avgTargetPrice: Math.round(avgTargetPrice), recentAvgTargetPrice: Math.round(avgTargetPrice), latestTargetPrice: Math.round(normalizeTarget(latest.target_price, price)), upsidePct: Math.round(((avgTargetPrice - price) / price * 100) * 100) / 100, recentUpsidePct: Math.round(((avgTargetPrice - price) / price * 100) * 100) / 100, latestUpsidePct: Math.round(((normalizeTarget(latest.target_price, price) - price) / price * 100) * 100) / 100, reportCount: reports.length, latestReportDate: latest.report_date, latestTitle: latest.title, brokers: Array.from(new Set(reports.map(r => r.broker || r.source).filter(Boolean))) });
  }
  items.sort((a,b) => b.upsidePct - a.upsidePct);
  return { items: items.slice(0, limit), total: items.length, status: 'fundamental-cache-node-fallback', maxSymbols };
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
      return send(res, 200, JSON.stringify({
        items: [
          { symbol: 'VNINDEX', label: 'VN-Index', close: 1226.3, change: 0, changePct: 0 },
          { symbol: 'HNXINDEX', label: 'HNX-Index', close: 214.1, change: 0, changePct: 0 },
          { symbol: 'UPCOM', label: 'UPCOM', close: 91.2, change: 0, changePct: 0 }
        ],
        status: 'static-index-cache-node-fallback'
      }));
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
    if (pathname === '/fundamental-top-upside') {
      const limit = Math.max(1, Math.min(50, Number(url.searchParams.get('limit') || 20)));
      const maxSymbols = Math.max(20, Math.min(300, Number(url.searchParams.get('max_symbols') || 200)));
      return send(res, 200, JSON.stringify(fundamentalTopUpside(limit, maxSymbols)));
    }
    if (pathname.startsWith('/fundamental-signals/')) {
      const symbol = decodeURIComponent(pathname.split('/').pop() || '').toUpperCase();
      const limit = Math.max(1, Math.min(80, Number(url.searchParams.get('limit') || 50)));
      return send(res, 200, JSON.stringify(fundamentalSignals(symbol, limit)));
    }
    if (pathname === '/warrants-data') {
      return send(res, 200, JSON.stringify(warrantsFromCache(url.searchParams.get('symbols') || '')));
    }
    if (pathname === '/news') {
      const limit = Math.max(1, Math.min(200, Number(url.searchParams.get('limit') || 30)));
      return send(res, 200, JSON.stringify(newsFromCache(limit)));
    }
    return notFound(res);
  } catch (err) {
    return send(res, 500, JSON.stringify({ detail: 'Server Error', error: String(err && err.message || err) }));
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Hoa investment cache server listening on ${PORT}`);
});
