const projects = (window.PROJECTS || []).filter(p => Number.isFinite(+p.lat) && Number.isFinite(+p.lng));
const qs = s => document.querySelector(s);
const map = L.map('map', { zoomControl: false }).setView([10.82, 106.72], 10);
L.control.zoom({ position: 'bottomright' }).addTo(map);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 20, attribution: '&copy; OpenStreetMap' }).addTo(map);

const markers = new Map();
let activeId = null;

function esc(v){ return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function money(v){ return esc(v || '—'); }
function fmtArea(v){ return esc(v || '—'); }
function priorityClass(p){ p=(p||'medium').toLowerCase(); return p.includes('high')?'high':p.includes('low')?'low':'medium'; }
function markerIcon(p){
  const cls = `priority-${priorityClass(p.priority)}`;
  return L.divIcon({ className:'', iconSize:[28,28], iconAnchor:[14,28], popupAnchor:[0,-25], html:`<div class="marker-pin ${cls}"><span></span></div>` });
}
function popupHtml(p){
  return `<div class="popup">
    <h3>${esc(p.name)}</h3>
    <div class="mini">${esc(p.id)} · ${esc(p.date || 'chưa rõ ngày')} · ${esc(p.status || 'review')}</div>
    <dl>
      <dt>Diện tích</dt><dd>${fmtArea(p.area)}</dd>
      <dt>Giá/Cost</dt><dd>${money(p.price)}</dd>
      <dt>Giá bán</dt><dd>${money(p.sell_price)}</dd>
      <dt>FAR</dt><dd>${esc(p.far || '—')}</dd>
      <dt>Dân số</dt><dd>${esc(p.population || '—')}</dd>
      <dt>IRR</dt><dd>${esc(p.irr || '—')}</dd>
    </dl>
    ${p.map_url ? `<a href="${esc(p.map_url)}" target="_blank" rel="noreferrer">Mở Google Maps</a>` : ''}
  </div>`;
}
function detailHtml(p){
  return `<h3>${esc(p.name)}</h3>
    <div class="detail-grid">
      <b>ID</b><span>${esc(p.id)}</span>
      <b>Ngày báo cáo</b><span>${esc(p.date || '—')}</span>
      <b>Trạng thái</b><span>${esc(p.status || 'review')}</span>
      <b>Loại</b><span>${esc(p.type || '—')}</span>
      <b>Vị trí</b><span>${esc([p.address,p.district,p.province].filter(Boolean).join(', ') || '—')}</span>
      <b>Tọa độ</b><span>${(+p.lat).toFixed(6)}, ${(+p.lng).toFixed(6)}</span>
      <b>Diện tích</b><span>${fmtArea(p.area)}</span>
      <b>Giá/Cost</b><span>${money(p.price)}</span>
      <b>Giá bán SP</b><span>${money(p.sell_price)}</span>
      <b>FAR/Dân số</b><span>${esc([p.far,p.population].filter(Boolean).join(' / ') || '—')}</span>
      <b>IRR</b><span>${esc(p.irr || '—')}</span>
    </div>
    <p>${esc(p.excerpt || '')}</p>
    ${p.map_url ? `<p><a href="${esc(p.map_url)}" target="_blank" rel="noreferrer">Mở Google Maps gốc</a></p>` : ''}`;
}
function setActive(id, zoom=true){
  activeId = id;
  const p = projects.find(x => x.id === id);
  if(!p) return;
  document.querySelectorAll('.project-card').forEach(el => el.classList.toggle('active', el.dataset.id === id));
  const m = markers.get(id);
  if(m){ if(zoom) map.flyTo([p.lat,p.lng], Math.max(map.getZoom(), 15), { duration:.75 }); m.openPopup(); }
  const drawer = qs('#detailDrawer'); drawer.hidden = false; drawer.innerHTML = detailHtml(p);
}
function filtered(){
  const q = qs('#search').value.trim().toLowerCase();
  const st = qs('#statusFilter').value; const ty = qs('#typeFilter').value;
  return projects.filter(p => {
    const blob = [p.name,p.id,p.address,p.province,p.district,p.excerpt,p.price,p.area].join(' ').toLowerCase();
    return (!q || blob.includes(q)) && (!st || (p.status||'')===st) && (!ty || (p.type||'')===ty);
  });
}
function renderList(){
  const rows = filtered();
  qs('#countLabel').textContent = `${rows.length}/${projects.length}`;
  const list = qs('#projectList');
  list.innerHTML = rows.length ? rows.map(p => `<button class="project-card ${p.id===activeId?'active':''}" data-id="${esc(p.id)}" role="listitem">
    <div class="project-title"><strong>${esc(p.name)}</strong><span class="pill">${esc(p.date || 'review')}</span></div>
    <div class="meta"><span>${esc(p.status || 'review')}</span><span>·</span><span>${esc(p.type || '—')}</span><span>·</span><span>${fmtArea(p.area)}</span></div>
    <p class="excerpt">${esc(p.excerpt || '')}</p>
  </button>`).join('') : '<div class="empty">Không có dự án phù hợp bộ lọc.</div>';
  list.querySelectorAll('.project-card').forEach(btn => btn.addEventListener('click', () => setActive(btn.dataset.id)));
  const ids = new Set(rows.map(x=>x.id));
  markers.forEach((m,id)=> ids.has(id) ? m.addTo(map) : map.removeLayer(m));
}
function initFilters(){
  for(const [id,key] of [['#statusFilter','status'],['#typeFilter','type']]){
    const sel=qs(id); [...new Set(projects.map(p=>p[key]).filter(Boolean))].sort().forEach(v=>{ const o=document.createElement('option'); o.value=v; o.textContent=v; sel.appendChild(o); });
    sel.addEventListener('change', renderList);
  }
  qs('#search').addEventListener('input', renderList);
}
function initMetrics(){
  const cities = new Set(projects.map(p=>p.province).filter(Boolean)).size;
  const high = projects.filter(p=>priorityClass(p.priority)==='high').length;
  qs('#metrics').innerHTML = `<div class="metric"><b>${projects.length}</b><span>Dự án có tọa độ</span></div><div class="metric"><b>${cities || '—'}</b><span>Tỉnh/TP</span></div><div class="metric"><b>${high}</b><span>Ưu tiên cao</span></div>`;
}
function initMap(){
  const group = [];
  projects.forEach(p=>{
    const m=L.marker([+p.lat,+p.lng], { icon: markerIcon(p), title:p.name }).bindPopup(popupHtml(p));
    m.on('click',()=>setActive(p.id,false)); markers.set(p.id,m); group.push(m); m.addTo(map);
  });
  if(group.length) map.fitBounds(L.featureGroup(group).getBounds().pad(.16));
}
initMetrics(); initFilters(); initMap(); renderList();
if(projects[0]) setActive(projects[0].id,false);
