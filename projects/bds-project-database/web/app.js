const projects=(window.PROJECTS||[]).filter(p=>Number.isFinite(+p.lat)&&Number.isFinite(+p.lng));
const qs=s=>document.querySelector(s); const map=L.map('map',{zoomControl:false}).setView([10.82,106.72],10); L.control.zoom({position:'bottomright'}).addTo(map); L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:20,attribution:'&copy; OpenStreetMap'}).addTo(map);
const markers=new Map(); let activeId=null; let sortMode='score'; let allBounds=null; let viewMode='cards';
function esc(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));} function clean(v){return String(v??'').trim();} function short(v,n=90){v=clean(v);return v.length>n?esc(v.slice(0,n-1))+'…':esc(v);} function scoreClass(s){s=+s||0;return s>=70?'score-good':s>=45?'score-mid':'score-low';} function prio(p){p=(p||'medium').toLowerCase();return p.includes('high')?'high':p.includes('low')?'low':'medium';}
function firstVal(p,keys){const r=p.popup||{};for(const k of keys){if(clean(r[k]))return r[k];}return '';} function markerIcon(p){return L.divIcon({className:'',iconSize:[30,30],iconAnchor:[15,30],popupAnchor:[0,-27],html:`<div class="marker-pin priority-${prio(p.priority)}"><span>${Math.round(+p.score||0)}</span></div>`});}
const GROUPS=(window.FIELD_SECTIONS||[]).map(section=>[section.id, section.title, section.fields]);
function chipClass(label,val){const s=(label+' '+val).toLowerCase(); if(/irr|npv|lợi nhuận|doanh thu|hoàn vốn/.test(s)) return 'good'; if(/giá|chi phí|tỷ|tr\/m2|triệu|tmđt|tsdđ|lur/.test(s)) return 'money'; return '';}
function splitValue(label,val){
  const raw=String(val||'').replace(/\r/g,'\n').trim();
  if(!raw) return [];
  let parts=[];
  if(raw.includes('\n')) parts=raw.split(/\n+/);
  else if(raw.includes(';')) parts=raw.split(/;\s*/);
  else if(raw.length>220 && /\s[-+]\s|\s\d+[.)]\s|\s[a-z]\)\s/i.test(raw)) parts=raw.split(/(?=\s[-+]\s|\s\d+[.)]\s|\s[a-z]\)\s)/i);
  else parts=[raw];
  const out=[];
  parts.forEach(p=>{
    p=clean(p).replace(/^[-+•]\s*/,'');
    if(!p) return;
    if(p.length>360 && /[,;]\s+/.test(p)){
      p.split(/;\s*/).forEach(x=>{x=clean(x); if(x) out.push(x);});
    } else out.push(p);
  });
  return [...new Set(out)].slice(0,40);
}
function formatValue(label,val){
  const parts=splitValue(label,val); if(!parts.length) return '';
  if(parts.length===1 && parts[0].length<220) return esc(parts[0]);
  if(parts.length<=10 && parts.every(x=>x.length<120)) return `<div class="value-chips">${parts.map(x=>`<span class="value-chip ${chipClass(label,x)}">${esc(x)}</span>`).join('')}</div>`;
  return `<ul class="value-list">${parts.map(x=>`<li class="${chipClass(label,x)}">${esc(x)}</li>`).join('')}</ul>`;
}
const FIELD_FALLBACKS={land_area_main:['land_area'],land_area_main_raw:['land_area_raw_mentions'],asking_land_price:['asking_price'],selling_price:['price_mentions'],far_clean:['far'],max_floors_clean:['max_floors'],density_clean:['building_density'],population_clean:['population'],total_investment_clean:['total_investment'],revenue_clean:['revenue'],profit_clean:['profit'],irr_clean:['irr'],npv_clean:['npv'],payback_clean:['payback']};
function fieldValue(r,k){if(clean(r[k]))return r[k];for(const alt of FIELD_FALLBACKS[k]||[]){if(clean(r[alt]))return r[alt];}return '';}
function table(fields,r){const body=fields.map(([label,k])=>[label,k,fieldValue(r,k)]).filter(([,,v])=>clean(v)).map(([label,k,v])=>`<tr><th>${esc(label)}</th><td>${formatValue(label,v)}</td></tr>`).join('');return body?`<table class="info-table"><tbody>${body}</tbody></table>`:'';}
function financialEvidencePanel(r){
  let items=[];try{items=JSON.parse(r.financial_line_items||'[]')}catch(e){} if(!Array.isArray(items)||!items.length)return '';
  const rows=items.filter(x=>clean(x&&x.label)&&clean(x&&x.value)).slice(0,80).map(x=>`<tr><th>${esc(x.label)}</th><td>${esc(x.value)}</td></tr>`).join('');
  if(!rows)return '';
  return `<section class="financial-evidence" data-group="financial-evidence"><h4>CHI TIẾT SỐ LIỆU TÀI CHÍNH TỪ BÁO CÁO</h4><p>Mỗi dòng gồm đúng 2 cột: <b>Mục</b> và <b>Giá trị</b>. Không hiển thị số rời không có nhãn.</p><table class="financial-table"><thead><tr><th>Mục</th><th>Giá trị</th></tr></thead><tbody>${rows}</tbody></table></section>`;
}

function scenarioPanel(r){
  if(!clean(r.scenario_data))return '';
  let scenarios=[];try{scenarios=JSON.parse(r.scenario_data)}catch(e){return '';} if(!Array.isArray(scenarios)||!scenarios.length)return '';
  const body=scenarios.map((s,i)=>`<section class="scenario-pane ${i?'hidden':''}" data-scenario="${esc(s.id)}"><div class="scenario-status">${esc(s.status||'Phương án')}</div><div class="scenario-grid">${Object.entries(s).filter(([k])=>!['id','title','status'].includes(k)).map(([k,v])=>`<div><span>${esc(({area:'Quy mô',planning:'Quy hoạch',products:'Sản phẩm',population:'Dân số',legal:'Pháp lý',financial:'Tài chính',revenue:'Doanh thu',selling_price:'Giá bán',investment:'Tổng mức đầu tư',cost:'Chi phí hoạt động',profit:'Lợi nhuận'})[k]||k)}</span><b>${esc(v)}</b></div>`).join('')}</div></section>`).join('');
  return `<section class="scenario-panel" data-group="scenarios"><h4>PHƯƠNG ÁN ĐẦU TƯ (${scenarios.length})</h4><div class="scenario-tabs">${scenarios.map((s,i)=>`<button class="${i?'':'active'}" data-scenario-target="${esc(s.id)}">${esc(s.title)}</button>`).join('')}</div>${body}</section>`;
}
function detailGroups(p){const r=p.popup||{};return scenarioPanel(r)+GROUPS.map(([id,title,fields])=>{const t=table(fields,r);const evidence=id==='financial'?financialEvidencePanel(r):'';return (t||evidence)?`<section class="info-group" data-group="${id}"><h4>${esc(title)}</h4>${t||''}${evidence}</section>`:''}).join('')+`<section class="excerpt-box"><b>Excerpt tin nhắn gốc</b><p>${esc(r.source_excerpt||p.excerpt||'')}</p>${p.map_url?`<a class="map-link" href="${esc(p.map_url)}" target="_blank" rel="noreferrer">Mở Google Maps gốc</a>`:''}</section>`;}
function productSummary(p){
  const r=p.popup||{};
  const src=[r.selling_price,r.project_type,r.planning_summary,r.source_excerpt].filter(Boolean).join('\n');
  const catalog=[['Căn hộ',/căn hộ/i],['Chung cư',/chung cư/i],['Shophouse',/shophouse|shop\s*tm/i],['Nhà phố',/nhà phố/i],['Biệt thự',/biệt thự/i],['Officetel',/officetel/i],['Trung tâm thương mại',/tttm|trung tâm thương mại/i],['Nhà trẻ',/nhà trẻ/i]];
  const prices=String(r.selling_price||'').split(/\n|;/).map(clean).filter(x=>/giá bán|cho thuê/i.test(x)&&catalog.some(([,re])=>re.test(x))).slice(0,5);
  if(prices.length)return prices.map(x=>x.replace(/^[-+•]\s*/,''));
  const out=[];for(const [label,re] of catalog){if(re.test(src))out.push(label);}return out.slice(0,6);
}
function popupRow(label,value,cls=''){return value?`<tr class="${cls}"><th>${esc(label)}</th><td>${value}</td></tr>`:'';}
function popupHtml(p){
  const products=productSummary(p);
  const productHtml=products.length?`<ul class="popup-products">${products.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:'—';
  const finance=[firstVal(p,['irr_clean','irr']),firstVal(p,['npv_clean','npv']),firstVal(p,['profit_clean'])].filter(Boolean).join(' · ');
  return `<div class="popup popup-table-card"><div class="popup-head"><div><small>PROJECT SNAPSHOT</small><h3>${esc(p.name)}</h3></div><span class="score-badge ${scoreClass(p.score)}">${Math.round(+p.score||0)}</span></div><div class="popup-meta">${esc(p.date||p.datetime_raw||'Chưa rõ ngày')} · ${esc(p.type||'raw')}</div><table class="popup-summary">${popupRow('Diện tích',short(firstVal(p,['land_area_main','land_area','area']),100)||'—')}${popupRow('Sản phẩm',productHtml,'product-row')}${popupRow('Giá chào',short(firstVal(p,['asking_land_price','asking_price']),100)||'—')}${popupRow('Giá bán',short(firstVal(p,['selling_price']),140)||'—')}${popupRow('Hiệu quả',short(finance,120)||'—','finance-row')}${popupRow('Quy hoạch',short([firstVal(p,['far_clean']),firstVal(p,['max_floors_clean']),firstVal(p,['population_clean'])].filter(Boolean).join(' · '),130)||'—')}${popupRow('Pháp lý',short(firstVal(p,['legal_status','approval_status','legal_summary']),120)||'—')}</table><div class="popup-actions"><a class="map-link" href="#" onclick="window.__openDetail('${esc(p.id)}');return false;">Mở hồ sơ đầy đủ</a>${p.map_url?`<a href="${esc(p.map_url)}" target="_blank" rel="noreferrer">Google Maps ↗</a>`:''}</div></div>`;
}
function renderDetail(p){qs('#detailPanel').innerHTML=`<div class="detail-hero"><div class="detail-hero-head"><div><p class="eyebrow">Investment record</p><h2>${esc(p.name)}</h2><div class="hero-meta"><span>${esc(p.id)}</span><span>·</span><span>${esc(p.date||p.datetime_raw||'chưa rõ ngày')}</span><span>·</span><span>${esc(p.sender||'')}</span></div></div><span class="score-badge big ${scoreClass(p.score)}">${Math.round(+p.score||0)}</span></div><button class="expand-detail-btn" id="expandDetailBtn" type="button">Mở rộng / thu gọn chi tiết</button></div><nav class="tab-nav">${GROUPS.map(([id,title])=>`<button data-target="${id}">${esc(title)}</button>`).join('')}</nav>${detailGroups(p)}`; qs('#expandDetailBtn')?.addEventListener('click',()=>qs('#detailPanel').classList.toggle('expanded')); qs('#detailPanel').querySelectorAll('.scenario-tabs button').forEach(btn=>btn.addEventListener('click',()=>{const host=btn.closest('.scenario-panel');host.querySelectorAll('.scenario-tabs button').forEach(x=>x.classList.toggle('active',x===btn));host.querySelectorAll('.scenario-pane').forEach(x=>x.classList.toggle('hidden',x.dataset.scenario!==btn.dataset.scenarioTarget));})); qs('#detailPanel').querySelectorAll('.tab-nav button').forEach(btn=>btn.addEventListener('click',()=>{const el=qs(`#detailPanel [data-group="${btn.dataset.target}"]`); if(el) el.scrollIntoView({behavior:'smooth',block:'start'}); qs('#detailPanel').querySelectorAll('.tab-nav button').forEach(b=>b.classList.toggle('active',b===btn));}));}
function setActive(id,zoom=true){activeId=id;const p=projects.find(x=>x.id===id);if(!p)return;document.querySelectorAll('.project-card,#masterTable tbody tr').forEach(el=>el.classList.toggle('active',el.dataset.id===id));const m=markers.get(id);if(m){if(zoom)map.flyTo([p.lat,p.lng],Math.max(map.getZoom(),15),{duration:.75});m.openPopup();}renderDetail(p);} window.__selectProject=setActive;
window.__openDetail=id=>{setActive(id,false);qs('#detailPanel').classList.add('expanded');};
function filtered(){const q=qs('#search').value.trim().toLowerCase(),st=qs('#statusFilter').value,ty=qs('#typeFilter').value,min=+qs('#minScore').value;let arr=projects.filter(p=>{const r=p.popup||{};const blob=Object.values(r).join(' ').toLowerCase();return(+p.score||0)>=min&&(!q||blob.includes(q))&&(!st||(p.status||'')===st)&&(!ty||(p.type||'')===ty);});arr.sort((a,b)=>{if(q){const rank=p=>{const n=(p.name||'').toLowerCase();return n===q?0:n.startsWith(q)?1:n.includes(q)?2:3;};const d=rank(a)-rank(b);if(d)return d;}return sortMode==='name'?a.name.localeCompare(b.name,'vi'):sortMode==='date'?String(b.date||'').localeCompare(String(a.date||'')):(+b.score||0)-(+a.score||0);});return arr;}
function renderCards(rows){const list=qs('#projectList');list.innerHTML=rows.length?rows.map(p=>`<button class="project-card ${p.id===activeId?'active':''}" data-id="${esc(p.id)}" role="listitem"><div class="project-top"><strong>${esc(p.name)}</strong><span class="score-badge ${scoreClass(p.score)}">${Math.round(+p.score||0)}</span></div><div class="meta"><span>${esc(p.date||'chưa ngày')}</span><span>·</span><span>${esc(p.type||'raw')}</span></div><div class="mini-facts"><div class="mini-fact"><span>Diện tích đất</span><b>${short(firstVal(p,['land_area_main','land_area','area']),34)||'—'}</b></div><div class="mini-fact"><span>IRR/NPV</span><b>${short([firstVal(p,['irr_clean','irr']),firstVal(p,['npv_clean','npv'])].filter(Boolean).join(' / '),34)||'—'}</b></div></div><p class="excerpt">${esc(p.excerpt||'')}</p></button>`).join(''):'<div class="empty">Không có dự án phù hợp bộ lọc.</div>';list.querySelectorAll('.project-card').forEach(btn=>btn.addEventListener('click',()=>setActive(btn.dataset.id)));}
function renderTable(rows){const tb=qs('#masterTable tbody');tb.innerHTML=rows.map(p=>`<tr class="${p.id===activeId?'active':''}" data-id="${esc(p.id)}"><td>${esc(p.name)}<div class="table-muted">${esc(p.id)}</div></td><td><span class="score-badge ${scoreClass(p.score)}">${Math.round(+p.score||0)}</span></td><td>${esc(p.date||'—')}</td><td>${short(firstVal(p,['land_area_main','land_area','area']),80)||'—'}</td><td>${short(firstVal(p,['asking_land_price','asking_price','price_mentions']),90)||'—'}</td><td>${short([firstVal(p,['irr_clean','irr']),firstVal(p,['npv_clean','npv'])].filter(Boolean).join(' / '),80)||'—'}</td></tr>`).join('');tb.querySelectorAll('tr').forEach(tr=>tr.addEventListener('click',()=>setActive(tr.dataset.id)));}
function renderList(){const rows=filtered();qs('#countLabel').textContent=`${rows.length}/${projects.length}`;qs('#projectList').hidden=viewMode!=='cards';qs('#masterTableWrap').hidden=viewMode!=='table';renderCards(rows);renderTable(rows);const ids=new Set(rows.map(x=>x.id));markers.forEach((m,id)=>ids.has(id)?m.addTo(map):map.removeLayer(m));}
function csvCell(v){return '"'+String(v??'').replace(/"/g,'""')+'"';} function exportFilteredCsv(){const rows=filtered();const fields=['id','name','score','date','type','lat','lng','area','price','far','population','irr','npv','map_url','source_file'];const csv=[fields.join(',')].concat(rows.map(p=>fields.map(f=>csvCell(p[f])).join(','))).join('\n');const blob=new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='bds_dashboard_filtered.csv';a.click();URL.revokeObjectURL(a.href);}
function setViewMode(mode){viewMode=mode;qs('#cardViewBtn').classList.toggle('active',mode==='cards');qs('#tableViewBtn').classList.toggle('active',mode==='table');renderList();}
function initFilters(){for(const [id,key]of[['#statusFilter','status'],['#typeFilter','type']]){const sel=qs(id);[...new Set(projects.map(p=>p[key]).filter(Boolean))].sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});sel.addEventListener('change',renderList);}qs('#search').addEventListener('input',renderList);qs('#sortMode').addEventListener('change',e=>{sortMode=e.target.value;renderList();});qs('#minScore').addEventListener('input',e=>{qs('#minScoreLabel').textContent=e.target.value;renderList();});qs('#resetFilters').addEventListener('click',()=>{qs('#search').value='';qs('#statusFilter').value='';qs('#typeFilter').value='';qs('#minScore').value=0;qs('#minScoreLabel').textContent='0';renderList();});qs('#fitMapBtn').addEventListener('click',()=>{if(allBounds)map.fitBounds(allBounds.pad(.15));});qs('#exportCsvBtn').addEventListener('click',exportFilteredCsv);qs('#cardViewBtn').addEventListener('click',()=>setViewMode('cards'));qs('#tableViewBtn').addEventListener('click',()=>setViewMode('table'));}
function initMetrics(){const full=(window.FULL_PROJECTS||[]).length, mapped=projects.length,unmapped=Math.max(0,full-mapped);qs('#metrics').innerHTML=`<div class="metric"><b>${full}</b><span>Tổng dự án</span></div><div class="metric"><b>${mapped}</b><span>Có map</span></div><div class="metric"><b>${unmapped}</b><span>Chưa map</span></div>`;}
function initMap(){const group=[];projects.forEach(p=>{const m=L.marker([+p.lat,+p.lng],{icon:markerIcon(p),title:p.name}).bindPopup(popupHtml(p),{maxWidth:380});m.on('click',()=>setActive(p.id,false));markers.set(p.id,m);group.push(m);m.addTo(map);});if(group.length){allBounds=L.featureGroup(group).getBounds();map.fitBounds(allBounds.pad(.15));}}


function fullRowToProject(r){
  return {
    id:r.record_id||r.curated_id||r.master_id, name:r.project_name, lat:Number(r.latitude)||0, lng:Number(r.longitude)||0,
    date:r.report_date, datetime_raw:'', sender:r.senders, type:r.project_type||'full master', status:'full-database',
    priority:Number(r.data_completeness_score)>=70?'high':Number(r.data_completeness_score)>=45?'medium':'low',
    score:Number(r.data_completeness_score)||0, popup:r, area:r.land_area_main, price:r.asking_land_price||r.financial_raw_mentions,
    far:r.far_clean, population:r.population_clean, irr:r.irr_clean, npv:r.npv_clean, excerpt:r.source_excerpt,
    map_url:(r.map_urls||'').split(';')[0]?.trim()||'', source_file:r.source_files, source_chat:'Bee || Phân Tích Đầu Tư'
  };
}
function openFullProjectDetail(masterId){
  const r=(window.FULL_PROJECTS||[]).find(x=>(x.record_id||x.curated_id||x.master_id)===masterId); if(!r)return;
  const mapped=projects.find(p=>p.id===masterId);
  if(mapped){ setActive(masterId, true); qs('#allProjectsOverlay').hidden=true; return; }
  const p=fullRowToProject(r);
  activeId=masterId; renderDetail(p); qs('#allProjectsOverlay').hidden=true;
}

function renderFullTable(){
  const q=(qs('#fullTableSearch')?.value||'').toLowerCase();
  const filt=qs('#fullCompletenessFilter')?.value||'';
  const rows=(window.FULL_PROJECTS||[]).filter(r=>{
    if(q && !Object.values(r).join(' ').toLowerCase().includes(q)) return false;
    if(filt==='missing_coordinates' && r.has_coordinates==='yes') return false;
    if(filt==='missing_area' && r.has_area==='yes') return false;
    if(filt==='missing_planning' && r.has_planning==='yes') return false;
    if(filt==='missing_legal' && r.has_legal==='yes') return false;
    if(filt==='missing_financial' && r.has_financial==='yes') return false;
    return true;
  });
  const tb=qs('#fullProjectTable tbody'); if(!tb)return;
  tb.innerHTML=rows.map(r=>`<tr data-id="${esc(r.record_id||r.curated_id||r.master_id)}"><td>${esc(r.project_name||'')}<div class="table-muted">${esc(r.record_id||r.curated_id||r.master_id||'')} · ${esc(r.province_city||'')}</div></td><td>${esc(r.report_date||'—')}</td><td><span class="flag ${r.has_coordinates==='yes'?'yes':'no'}">${r.has_coordinates}</span></td><td><span class="flag ${r.has_area==='yes'?'yes':'no'}">${r.has_area}</span><div class="table-muted">${short(r.land_area_main,70)||''}</div></td><td><span class="flag ${r.has_planning==='yes'?'yes':'no'}">${r.has_planning}</span></td><td><span class="flag ${r.has_legal==='yes'?'yes':'no'}">${r.has_legal}</span></td><td><span class="flag ${r.has_financial==='yes'?'yes':'no'}">${r.has_financial}</span></td><td><span class="score-badge ${scoreClass(r.score_total||r.data_completeness_score)}">${esc(r.score_total||r.data_completeness_score||0)}</span><div class="table-muted">${esc(r.score_grade||'')}</div></td></tr>`).join('');
  tb.querySelectorAll('tr').forEach(tr=>tr.addEventListener('click',()=>openFullProjectDetail(tr.dataset.id)));
}
function exportFullCsv(){
  const rows=window.FULL_PROJECTS||[]; if(!rows.length)return;
  const fields=Object.keys(rows[0]);
  const csv=[fields.join(',')].concat(rows.map(r=>fields.map(f=>csvCell(r[f])).join(','))).join('\n');
  const blob=new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='bds_full_project_database.csv'; a.click(); URL.revokeObjectURL(a.href);
}
function initFullProjects(){
  qs('#allProjectsBtn')?.addEventListener('click',()=>{qs('#allProjectsOverlay').hidden=false;renderFullTable();});
  qs('#closeAllProjects')?.addEventListener('click',()=>qs('#allProjectsOverlay').hidden=true);
  qs('#fullTableSearch')?.addEventListener('input',renderFullTable);
  qs('#fullCompletenessFilter')?.addEventListener('change',renderFullTable);
  qs('#exportFullCsvBtn')?.addEventListener('click',exportFullCsv);
}

initMetrics();initFilters();initFullProjects();initMap();renderList();if(projects[0])setActive(projects[0].id,false);
