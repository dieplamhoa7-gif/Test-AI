# -*- coding: utf-8 -*-
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'firebase_public'
FILES=[PUBLIC/n for n in ['index.html','stocks.html','news-page.html','cw.html','warrants.html']]
MARK='lh-cw-live-refresh-20260705'
SCRIPT=r'''
<script id="lh-cw-live-refresh-20260705">
(function(){
  if(!(location.pathname.startsWith('/cw')||location.pathname.startsWith('/warrants'))) return;
  let items=[];
  const norm=x=>String(x||'').toUpperCase().replace(/[^A-Z0-9]/g,'');
  const fmt=n=>{const v=Number(n);return Number.isFinite(v)?v.toLocaleString('vi-VN'):'-';};
  const pct=n=>{const v=Number(n);return Number.isFinite(v)?v.toFixed(2)+'%':'-';};
  const getWatch=()=>{try{return JSON.parse(localStorage.getItem('lh.warrant.watchlist')||'[]').map(norm).filter(Boolean)}catch(e){return[]}};
  function card(x){return `<div class="warrant-card" data-warrant="${x.code}"><strong>${x.code}<span>${x.underlying||''}</span></strong><div class="warrant-row"><span>Giá / Bid-Ask</span><b>${fmt(x.marketPrice||x.lastPrice||x.fairValue)} / ${fmt(x.bid)}-${fmt(x.ask)}</b></div><div class="warrant-row"><span>Cơ sở / Hòa vốn</span><b>${fmt(x.underlyingPrice)} / ${fmt(x.breakeven)}</b></div><div class="warrant-row"><span>Đòn bẩy / Spread</span><b>${fmt(x.leverage)}x / ${pct(x.spreadPct)}</b></div><div class="warrant-row"><span>Nội tại / Time value</span><b>${fmt(x.intrinsicValue)} / ${fmt(x.timeValue)}</b></div><div class="warrant-row"><span>Còn lại / Tín hiệu</span><b>${fmt(x.daysLeft)} ngày / ${x.advancedSignal||'-'}</b></div></div>`}
  async function load(){try{const r=await fetch('/data/warrants_data.json?ts='+Date.now(),{cache:'no-store'});const p=await r.json();items=(Array.isArray(p.items)?p.items:p).map(x=>({...x,code:norm(x.code)})).filter(x=>x.code);const st=document.getElementById('warrantStatus');if(st)st.textContent=`Đã cập nhật ${items.length} chứng quyền lúc ${new Date(p.updatedAt||Date.now()).toLocaleTimeString('vi-VN')}`;window.__lhLatestWarrantItems=items;return p}catch(e){return null}}
  function renderBase(){const grid=document.getElementById('warrantGrid');if(!grid||!items.length)return;const watch=getWatch();const list=watch.length?watch.map(c=>items.find(x=>x.code===c)).filter(Boolean):items.slice(0,80);grid.innerHTML=list.map(card).join('')||'<div class="empty">Không có dữ liệu chứng quyền.</div>';}
  function bindSearch(){const input=document.getElementById('warrantSearchInput'), box=document.getElementById('warrantSuggest'); if(!input||!box||input.dataset.liveRefreshSearch==='1')return; input.dataset.liveRefreshSearch='1'; const run=()=>{const q=norm(input.value); if(!q){renderBase();box.classList.remove('open');box.innerHTML='';return;} const found=items.filter(x=>x.code.includes(q)||norm(x.underlying).includes(q)).slice(0,50); const grid=document.getElementById('warrantGrid'); if(grid)grid.innerHTML=found.map(card).join('')||'<div class="empty">Không tìm thấy mã chứng quyền phù hợp.</div>'; box.innerHTML=found.map(x=>`<div class="search-option" data-warrant="${x.code}"><strong>${x.code}<em>${fmt(x.marketPrice||x.lastPrice||x.fairValue)}</em></strong><span>${x.underlying||''} • Hòa vốn ${fmt(x.breakeven)} • ${fmt(x.daysLeft)} ngày</span></div>`).join(''); box.classList.toggle('open',found.length>0); box.querySelectorAll('[data-warrant]').forEach(el=>el.onclick=()=>{input.value=el.dataset.warrant;box.classList.remove('open');run();});}; ['input','keyup','change'].forEach(ev=>input.addEventListener(ev,run));};
  async function refresh(){await load();renderBase();bindSearch();}
  setTimeout(refresh,700); setInterval(refresh,60000);
})();
</script>'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if MARK not in s:
        s=s.replace('</body>',SCRIPT+'\n</body>')
        p.write_text(s,encoding='utf-8',newline='')
        print('patched',p.name)
    else: print('skip',p.name)
