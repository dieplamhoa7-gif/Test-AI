const DB = window.MANUAL_RECORDS_FRONTEND_DB || {records:[],review:[],summary:[],totals:{}};
const $ = s => document.querySelector(s);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const clean = v => String(v ?? '').trim();
let mode = 'records';
let activeId = '';

function yes(v){ return clean(v) ? esc(v) : '<span class="empty-value">Chưa thấy trong chunk</span>'; }
function blob(r){ return JSON.stringify(r).toLowerCase(); }
function chunks(r){ return (r.source_chunks || []).join(', '); }

function init(){
  const t = DB.totals || {};
  $('#kpis').innerHTML = [
    ['Dự án', t.records || 0],
    ['Có tài chính', t.financial_records || 0],
    ['Chỉ tiêu TC', t.financial_items || 0],
    ['Review/Skip', t.review || 0]
  ].map(([k,v]) => `<div class="kpi"><b>${esc(v)}</b><span>${esc(k)}</span></div>`).join('');
  (DB.summary||[]).forEach(s => $('#partFilter').innerHTML += `<option value="${s.part}">Part ${s.part} · ${s.records} records</option>`);
  [...new Set((DB.records||[]).map(r => r.decision).filter(Boolean))].sort().forEach(d => $('#decisionFilter').innerHTML += `<option value="${esc(d)}">${esc(d)}</option>`);
  ['#search','#partFilter','#decisionFilter','#financialOnly'].forEach(sel => $(sel).addEventListener(sel==='#financialOnly'?'change':'input', render));
  $('#partFilter').addEventListener('change', render);
  $('#decisionFilter').addEventListener('change', render);
  document.querySelectorAll('.mode-tabs button').forEach(btn => btn.addEventListener('click', () => { mode = btn.dataset.mode; document.querySelectorAll('.mode-tabs button').forEach(b => b.classList.toggle('active', b===btn)); render(); }));
  $('#resetBtn').addEventListener('click', () => { $('#search').value=''; $('#partFilter').value=''; $('#decisionFilter').value=''; $('#financialOnly').checked=false; render(); });
  render();
}

function filteredRecords(){
  let rows = [...(DB.records || [])];
  const q = $('#search').value.toLowerCase().trim();
  const part = $('#partFilter').value;
  const decision = $('#decisionFilter').value;
  if(part) rows = rows.filter(r => String(r.part) === part);
  if(decision) rows = rows.filter(r => r.decision === decision);
  if($('#financialOnly').checked || mode === 'financial') rows = rows.filter(r => (r.financial_items || []).length);
  if(q) rows = rows.filter(r => blob(r).includes(q));
  rows.sort((a,b) => String(b.report_date||'').localeCompare(String(a.report_date||'')) || String(a.project_name||'').localeCompare(String(b.project_name||''),'vi'));
  return rows;
}
function filteredReview(){
  let rows = [...(DB.review || [])];
  const q = $('#search').value.toLowerCase().trim();
  const part = $('#partFilter').value;
  if(part) rows = rows.filter(r => String(r.part) === part);
  if(q) rows = rows.filter(r => blob(r).includes(q));
  return rows;
}

function render(){
  const rows = mode === 'review' ? filteredReview() : filteredRecords();
  $('#countLabel').textContent = `${rows.length} kết quả`;
  $('#decisionFilter').disabled = mode === 'review';
  $('#financialOnly').disabled = mode === 'review' || mode === 'financial';
  $('#list').innerHTML = rows.map(r => mode === 'review' ? reviewItem(r) : recordItem(r)).join('') || '<div class="review-card"><b>Không có kết quả.</b></div>';
  $('#list').querySelectorAll('.item').forEach((btn, i) => btn.addEventListener('click', () => mode === 'review' ? showReview(rows[i]) : showRecord(rows[i])));
}

function recordItem(r){
  const fin = (r.financial_items||[]).length;
  const dup = /duplicate/i.test(r.decision||'');
  return `<button class="item ${activeId===r.id?'active':''}" data-id="${esc(r.id)}"><div class="item-top"><b>${esc(r.project_name)}</b><span class="tag ${fin?'fin':''}">${fin} TC</span></div><div class="meta"><span>Part ${r.part}</span><span>·</span><span>${esc(r.report_date||'chưa ngày')}</span><span>·</span><span>${esc(chunks(r))}</span></div><div class="meta"><span class="tag ${dup?'dup':''}">${esc(r.decision||'record')}</span></div></button>`;
}
function reviewItem(r){
  return `<button class="item" data-id="review-${esc(r.chunk_id)}"><div class="item-top"><b>Chunk ${esc(r.chunk_id)}</b><span class="tag">Part ${r.part}</span></div><div class="meta"><span>${esc(r.reason||'review')}</span></div></button>`;
}

function financialTable(items){
  if(!items || !items.length) return '<div class="source-box"><span class="empty-value">Không có chỉ tiêu tài chính được đề cập.</span></div>';
  return `<table class="financial-table"><thead><tr><th>Mục</th><th>Giá trị</th><th>Chunk nguồn</th></tr></thead><tbody>${items.map(x => `<tr><th>${esc(x.label)}</th><td>${esc(x.value)}</td><td>${esc(x.source_chunk || x.chunk_id || '')}</td></tr>`).join('')}</tbody></table>`;
}
function showRecord(r){
  activeId = r.id;
  document.querySelectorAll('.item').forEach(x => x.classList.toggle('active', x.dataset.id === r.id));
  const p = r.planning || {}, l = r.legal || {};
  $('#detail').innerHTML = `<section class="hero"><p class="eyebrow">${esc(r.decision||'project record')}</p><h2>${esc(r.project_name)}</h2><div class="hero-actions"><span class="pill">${esc(r.id)}</span><span class="pill">Part ${r.part}</span><span class="pill">Chunk ${esc(chunks(r))}</span><span class="pill">${esc(r.report_date||'chưa ngày')}</span>${r.map_url?`<a class="pill gold" href="${esc(r.map_url)}" target="_blank" rel="noreferrer">Google Maps ↗</a>`:''}</div></section><div class="section-grid"><section class="section"><h3>Tổng quan</h3><table class="kv"><tbody><tr><th>Vị trí</th><td>${yes(r.location)}</td></tr><tr><th>Nguồn</th><td>${yes(r.source_file)}</td></tr><tr><th>Người gửi</th><td>${yes(r.sender)}</td></tr><tr><th>Ghi chú kinh doanh</th><td>${yes(r.business_notes)}</td></tr></tbody></table></section><section class="section"><h3>Quy hoạch</h3><div class="planning-cards"><div class="plan-card"><span>Tầng cao</span><b>${yes(p.floors)}</b></div><div class="plan-card"><span>MĐXD</span><b>${yes(p.density)}</b></div><div class="plan-card"><span>HS SDĐ</span><b>${yes(p.far)}</b></div><div class="plan-card"><span>Dân số</span><b>${yes(p.population)}</b></div></div><table class="kv"><tbody><tr><th>Diện tích/Quy mô</th><td>${yes((p.area_mentions||[]).join('; '))}</td></tr><tr><th>Diễn giải quy hoạch</th><td>${yes(p.raw)}</td></tr></tbody></table></section><section class="section"><h3>Pháp lý đất</h3><div class="source-box">${yes(l.land)}</div></section><section class="section"><h3>Pháp lý dự án</h3><div class="source-box">${yes(l.project)}</div></section><section class="section wide"><h3>Các chỉ tiêu tài chính được đề cập</h3>${financialTable(r.financial_items)}</section><section class="section wide"><h3>Pháp lý / quy hoạch gốc từ record</h3><div class="source-box small">${yes(l.raw)}</div></section><section class="section wide"><h3>Excerpt nguồn</h3><div class="source-box small">${yes(r.excerpt)}</div></section></div>`;
}
function showReview(r){
  activeId = `review-${r.chunk_id}`;
  $('#detail').innerHTML = `<section class="hero"><p class="eyebrow">Review / Skip</p><h2>Chunk ${esc(r.chunk_id)}</h2><div class="hero-actions"><span class="pill">Part ${r.part}</span></div></section><section class="section"><h3>Lý do không nhập record</h3><div class="source-box">${yes(r.reason)}</div></section>`;
}

init();
