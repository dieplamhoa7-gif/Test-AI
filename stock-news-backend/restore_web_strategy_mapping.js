const fs=require('fs');
for (const file of ['firebase_public/data/strategy_matrix_cache.json','firebase_public/data/strategy_results_cache.json']) {
  const j=JSON.parse(fs.readFileSync(file,'utf8'));
  if (Array.isArray(j.columns)) j.columns=j.columns.filter(c=>c.id!=='lh2_final');
  if (Array.isArray(j.strategies)) j.strategies=j.strategies.filter(s=>s.id!=='lh2_final');
  j.updatedAt=new Date().toISOString();
  j.note=String(j.note||'').replace(/ \| Added LH2 Final.*$/,'') + ' | Restored existing web strategy mapping: no new LH2 column.';
  fs.writeFileSync(file, JSON.stringify(j,null,2),'utf8');
}
console.log('restored');
