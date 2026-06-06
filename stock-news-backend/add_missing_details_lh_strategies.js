const fs=require('fs');
const p='firebase_public/data/strategy_results_cache.json';
const r=JSON.parse(fs.readFileSync(p,'utf8'));
function fmt(v){ return (v===null||v===undefined||Number.isNaN(Number(v)))?'-':Number(v).toFixed(2); }
function enrichLH2(x){
  const miss=x.missingReasons||[]; const ai=x.entryIndicators||{}; const details=[];
  for (const m of miss) {
    const s=String(m).toLowerCase();
    if (s.includes('thủng')||s.includes('support')||s.includes('hỗ trợ')) details.push(`False-break hỗ trợ: hiện distSupportPct ${fmt(x.distSupportPct)}% / cần thủng hỗ trợ 2-4% rồi hồi`);
    else if (s.includes('volume')) details.push(`Volume: hiện volumeRatio ${fmt(ai.volumeRatio)} / cần dòng tiền xác nhận đủ mạnh`);
    else if (s.includes('rsi')) details.push(`RSI: hiện ${fmt(ai.rsi)} / cần vùng hồi phục phù hợp`);
    else if (s.includes('macd')) details.push(`MACD: hist hiện ${fmt(ai.macdHist)} / cần MACD hồi phục/xác nhận`);
    else if (s.includes('roc')) details.push(`ROC/Momentum: hiện ROC20 ${fmt(ai.roc20)} / cần momentum trong vùng LH2`);
    else details.push(`${m}: chưa đạt điều kiện LH2 Shakeout`);
  }
  if (!details.length && x.action==='BUY') details.push('Đạt điều kiện LH2 Shakeout Rebound theo scan hiện tại.');
  x.missingDetails=details;
  x.hoverNote=details.length && x.action!=='BUY' ? `LH2 chưa mua: ${details.join('; ')}` : 'Đạt LH2 Shakeout Rebound theo scan hiện tại.';
  return x;
}
function enrichLH1(x){
  if (!Array.isArray(x.missingDetails)) x.missingDetails=(x.missingReasons||[]).map(m=>`${m}: chưa đạt LH1 Final`);
  if (!x.hoverNote) x.hoverNote=x.missingDetails.length?`LH1 Final chưa mua: ${x.missingDetails.join('; ')}`:'Đạt LH1 Final.';
  return x;
}
for (const s of r.strategies||[]) {
  if (s.id==='b4_trend_pullback') { s.buy=(s.buy||[]).map(enrichLH1); s.watchlist=(s.watchlist||[]).map(enrichLH1); }
  if (s.id==='shakeout_breakdown_rebound') { s.buy=(s.buy||[]).map(enrichLH2); s.watchlist=(s.watchlist||[]).map(enrichLH2); }
}
r.updatedAt=new Date().toISOString();
fs.writeFileSync(p,JSON.stringify(r,null,2),'utf8');
const out={}; for(const s of r.strategies||[]) if(['b4_trend_pullback','shakeout_breakdown_rebound'].includes(s.id)) out[s.id]={buy:(s.buy||[]).length,watch:(s.watchlist||[]).length,first:(s.watchlist||s.buy||[])[0]?.missingDetails}; console.log(JSON.stringify(out,null,2));
