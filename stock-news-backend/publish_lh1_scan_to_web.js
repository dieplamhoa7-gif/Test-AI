const fs=require('fs');
const scan=JSON.parse(fs.readFileSync('data/lh1_premium_vn100_today_scan.json','utf8'));
const pub='firebase_public/data';
fs.copyFileSync('data/lh1_premium_vn100_today_scan.json', `${pub}/lh1_current_scan.json`);
function toChip(x, action){
  const close=Number(x.close||0); const support=Number(x.support||0);
  const rs=x.rsSnapshot||{}; const resistance=Number(rs.activeResistanceDay||rs.resistanceDay||0);
  const target = resistance && resistance>close ? resistance : +(close*1.12).toFixed(2);
  const stop = support && support<close ? +(support*0.985).toFixed(2) : +(close*0.95).toFixed(2);
  const miss=(x.premiumMiss||x.missingReasons||[]);
  return {
    symbol:x.symbol, strategy:'LH1 Pullback', strategyId:'b4_trend_pullback', action,
    rankScore:x.score||0, entryPrice:close, lastClose:close, support:support||null,
    takeProfit:+target.toFixed(2), targetPrice:+target.toFixed(2), stopLoss:+stop.toFixed(2),
    targetPct: close? +(((target/close)-1)*100).toFixed(2):null, stopPct: close? +((1-(stop/close))*100).toFixed(2):null,
    distSupportPct:x.distSupportPct, missingReasons:miss,
    missingDetails: miss.map(m=>`${m}: chưa đạt ngưỡng LH1 premium`),
    hoverNote: miss.length ? `LH1 chưa mua: còn thiếu ${miss.join(', ')}` : 'Đạt LH1 Pullback/Premium scan.',
    entryIndicators:x.entryIndicators||{}, asOfDate:x.date, source:'lh1_current_scan.json'
  };
}
const buy=(scan.premiumSignals||[]).filter(x=>x.action==='BUY_CANDIDATE').map(x=>toChip(x,'BUY'));
const watch=[...(scan.premiumSignals||[]).filter(x=>x.action!=='BUY_CANDIDATE').map(x=>toChip(x,'WATCH')),
             ...(scan.nearMisses||[]).slice(0,20).map(x=>toChip(x,'WATCH'))];
const resultsPath=`${pub}/strategy_results_cache.json`;
const results=JSON.parse(fs.readFileSync(resultsPath,'utf8'));
for (const s of results.strategies||[]) {
  if (s.id==='b4_trend_pullback') {
    s.name='LH1 Pullback'; s.buy=buy; s.watchlist=watch; s.source='data/lh1_current_scan.json';
    s.method='Current LH1 Pullback/Premium scan from scan_lh1_premium_vn100_today.py. BUY are full pass; WATCH are near-pass.';
  }
}
results.updatedAt=new Date().toISOString();
fs.writeFileSync(resultsPath, JSON.stringify(results,null,2),'utf8');
console.log(JSON.stringify({buy:buy.map(x=>x.symbol),watch:watch.map(x=>x.symbol),latestDates:scan.latestDates},null,2));
