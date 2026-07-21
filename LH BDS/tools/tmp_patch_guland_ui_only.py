from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8')
# Safety: never enable QHViet in frontend.
s=s.replace('includeGuland:true,includeQhViet:true','includeGuland:true,includeQhViet:false')
s=s.replace('j.gisxaydung||j.qhviet||{}','j.gisxaydung||{}')
s=s.replace('j.gisxaydung||j.qhviet','j.gisxaydung')
# Add a UI-only post processor: remove old GIS/QHViet source card and renumber Guland/Google.
patch=r'''
<script id="guland-ui-only-final">
(function(){
  function norm(t){return String(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}
  function polishGulandUI(){
    const box=document.getElementById('sourceBox'); if(!box) return;
    const cards=[...box.querySelectorAll('.source-result')];
    for(const card of cards){
      const h=card.querySelector('h3'); const txt=norm(h&&h.textContent);
      if(txt.includes('qh viet') || txt.includes('gis xay dung')) card.style.display='none';
      if(txt.includes('guland')) h.textContent='2. Guland - thông tin từ popup/map';
      if(txt.includes('google maps') || txt.includes('osm')) h.textContent='3. Google Maps / OSM - định vị';
    }
    const guland=[...box.querySelectorAll('.source-result')].find(c=>norm(c.textContent).includes('guland'));
    if(guland && !norm(guland.textContent).includes('gia/tin guland')){
      const rows=[...guland.querySelectorAll('.kv')];
      const hasPrice=rows.some(r=>norm(r.textContent).includes('gia/tin guland'));
      if(!hasPrice){
        const div=document.createElement('div'); div.className='kv';
        div.innerHTML='<b>Giá/tin Guland đọc được</b><span>Đang tải Guland...</span>';
        const link=guland.querySelector('p'); guland.insertBefore(div,link||null);
      }
    }
    try{ if(window.__forcePlanningNavy) window.__forcePlanningNavy(); }catch(e){}
  }
  window.__polishGulandUI=polishGulandUI;
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',polishGulandUI); else polishGulandUI();
  setInterval(polishGulandUI,1200);
  try{new MutationObserver(polishGulandUI).observe(document.body,{childList:true,subtree:true});}catch(e){}
})();
</script>
'''
if 'guland-ui-only-final' not in s:
    s=s.replace('</body></html>', patch+'</body></html>')
p.write_text(s,encoding='utf-8')
print('patched guland UI only; qhviet true?', 'includeQhViet:true' in s, 'qhviet' in s)
