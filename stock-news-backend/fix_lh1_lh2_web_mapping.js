const fs=require('fs');
const matrixPath='firebase_public/data/strategy_matrix_cache.json';
const resultsPath='firebase_public/data/strategy_results_cache.json';
const matrix=JSON.parse(fs.readFileSync(matrixPath,'utf8'));
for (const c of matrix.columns||[]) {
  if (c.id==='b4_trend_pullback') {
    c.name='LH1 Pullback'; c.shortName='LH1'; c.priority=1; c.style='primary';
    c.summary='LH1 Pullback / B4 precision: mua cổ phiếu trong xu hướng tăng, chờ nhịp điều chỉnh về gần hỗ trợ rồi vào khi lực hồi phục xuất hiện. Đây là LH1 lịch sử trên web, không phải chiến lược mới.';
    c.indicators='RSI, khoảng cách tới hỗ trợ, volumeRatio, ROC20, Bollinger position, core positive/negative score, R/S support/resistance, MA/Ichimoku/MACD tham chiếu';
    c.tooltipMetrics={winRate:'74.19%', averageReturn:'+2.90%/lệnh', totalReturn:'+90.0%'};
    c.validation={status:'LH1 lịch sử / Pullback chính', all:'Audit 2025-2026: 31 lệnh · WR 74.19% · avg +2.90% · tổng +90.0%', oos2026:'OOS 2026: 6 lệnh · WR 50% · avg 0.0%', source:'data/lh1_lh2_walkforward_audit.json'};
  }
  if (c.id==='shakeout_breakdown_rebound') {
    c.name='LH2 Shakeout Rebound'; c.shortName='LH2'; c.priority=2; c.style='danger';
    c.summary='LH2 Shakeout Rebound / false-break: bắt nhịp hồi sau pha rũ hàng, giá thủng hỗ trợ ngắn hạn 2-4% để loại lực yếu rồi kéo ngược lại. Đây là LH2 lịch sử trên web, không phải breakout v6.';
    c.indicators='False-break support 2-4%, core positive/negative score, ROC, market breadth, trend score, R/S support/resistance, volume, RSI/MACD/Bollinger tham chiếu';
    c.tooltipMetrics={winRate:'86.36%', averageReturn:'+4.67%/lệnh', totalReturn:'+102.66%'};
    c.validation={status:'LH2 lịch sử / Shakeout false-break', all:'Audit 2025-2026: 22 lệnh · WR 86.36% · avg +4.67% · tổng +102.66%', oos2026:'OOS 2026: 4 lệnh · WR 75% · avg +3.38%', source:'data/lh1_lh2_walkforward_audit.json'};
  }
  if (c.id==='clean_split_a_bottom') { c.priority=3; }
}
matrix.columns=(matrix.columns||[]).filter(c=>c.id!=='lh2_final').sort((a,b)=>(a.priority||99)-(b.priority||99));
matrix.updatedAt=new Date().toISOString();
matrix.note='Web strategy mapping restored: LH1 = b4_trend_pullback / Pullback; LH2 = shakeout_breakdown_rebound / Shakeout Rebound. No new LH2 breakout strategy column.';
fs.writeFileSync(matrixPath, JSON.stringify(matrix,null,2),'utf8');
const results=JSON.parse(fs.readFileSync(resultsPath,'utf8'));
results.strategies=(results.strategies||[]).filter(s=>s.id!=='lh2_final');
for (const s of results.strategies) {
  if (s.id==='b4_trend_pullback') s.name='LH1 Pullback';
  if (s.id==='shakeout_breakdown_rebound') s.name='LH2 Shakeout Rebound';
}
results.updatedAt=new Date().toISOString();
results.note='Web strategy results restored: LH1 uses b4_trend_pullback; LH2 uses shakeout_breakdown_rebound.';
fs.writeFileSync(resultsPath, JSON.stringify(results,null,2),'utf8');
console.log(JSON.stringify({cols:matrix.columns.map(c=>({id:c.id,name:c.name,shortName:c.shortName})),strategies:results.strategies.map(s=>({id:s.id,name:s.name}))},null,2));
