const fs = require('fs');
const path = require('path');
function readJson(p){ return JSON.parse(fs.readFileSync(p,'utf8')); }
function writeJson(p,o){ fs.writeFileSync(p, JSON.stringify(o,null,2), 'utf8'); }
const pub = path.join(__dirname,'firebase_public','data');
fs.copyFileSync(path.join(__dirname,'lh2_v6_balanced_backtest.json'), path.join(pub,'lh2_final_backtest.json'));
fs.copyFileSync(path.join(__dirname,'lh2_v6_balanced_today_scan.json'), path.join(pub,'lh2_final_today_scan.json'));
fs.copyFileSync(path.join(__dirname,'lh2_v6_high_freq_backtest.json'), path.join(pub,'lh2_v6_high_freq_backtest.json'));
fs.copyFileSync(path.join(__dirname,'lh2_v6_high_freq_today_scan.json'), path.join(pub,'lh2_v6_high_freq_today_scan.json'));

const matrixPath = path.join(pub,'strategy_matrix_cache.json');
const matrix = readJson(matrixPath);
matrix.updatedAt = new Date().toISOString();
matrix.note = (matrix.note || '') + ' | Added LH2 Final (v6 BALANCED) on 2026-06-06.';
matrix.columns = (matrix.columns || []).filter(c => c.id !== 'lh2_final');
matrix.columns.push({
  id: 'lh2_final',
  name: 'LH2 Final',
  shortName: 'LH2 Final',
  priority: 4,
  style: 'success',
  summary: 'Leader Momentum Breakout v6 BALANCED: breakout qua high20/high50 kết hợp RS-rank, volume/OBV/VWAP, ADX, breadth và vị trí gần đỉnh 52 tuần. Dùng làm tín hiệu breakout bổ sung/confirmation, không thay LH1 sniper.',
  indicators: 'Breakout high20/high50, RS-rank percentile, VolumeRatio, OBV slope, VWAP slope, ADX14, RSI14, RangePos60, nearHigh252, market breadth, MA20/MA50, ATR, Bollinger width, MACD histogram',
  tooltipMetrics: { winRate: '58.33%', averageReturn: '+4.02%/lệnh', totalReturn: '+96.38%' },
  validation: {
    status: 'LH2 final / research breakout confirmation',
    full: 'FULL 2023-nay: 24 lệnh · WR 58.33% · avg +4.02% · tổng +96.38%',
    oos: 'OOS 2025-2026: 13 lệnh · WR 53.85% · avg +3.85% · tổng +50.02%',
    yearly: '2025: 10 lệnh · WR 50% · avg +3.55%; 2026 YTD: 3 lệnh · WR 66.67% · avg +4.83%',
    source: 'data/lh2_final_backtest.json; data/lh2_final_today_scan.json'
  },
  matrix: {
    buy: 'Hiện mã đạt tín hiệu LH2 Final breakout theo scan mới nhất.',
    watch: 'Theo dõi mã tiệm cận điều kiện breakout/leader momentum.',
    avoid: 'Không đạt điều kiện LH2 Final hoặc thị trường/breadth chưa thuận.'
  }
});
matrix.columns.sort((a,b)=>(a.priority||99)-(b.priority||99));
writeJson(matrixPath, matrix);

const resultsPath = path.join(pub,'strategy_results_cache.json');
const results = readJson(resultsPath);
results.updatedAt = new Date().toISOString();
results.strategies = (results.strategies || []).filter(s => s.id !== 'lh2_final');
const scan = readJson(path.join(pub,'lh2_final_today_scan.json'));
const signals = (scan.signals || []).map(x => ({
  symbol: x.symbol,
  strategy: 'LH2 Final',
  strategyId: 'lh2_final',
  action: 'BUY',
  rankScore: 90,
  entryPrice: x.close || x.entry || null,
  lastClose: x.close || null,
  missingReasons: [],
  asOfDate: x.date || null,
  source: 'lh2_final_today_scan.json',
  entryIndicators: x.scores || {}
}));
results.strategies.push({
  id: 'lh2_final',
  name: 'LH2 Final',
  buy: signals,
  watchlist: [],
  rejectTop: [],
  rejectCount: 0,
  source: 'data/lh2_final_today_scan.json',
  canonical: true,
  method: 'LH2 v6 BALANCED final breakout signal. Today scan may be empty when no VN100 symbol passes.'
});
writeJson(resultsPath, results);

console.log(JSON.stringify({ok:true, matrixColumns: matrix.columns.map(c=>c.id), lh2TodayCount: signals.length}, null, 2));
