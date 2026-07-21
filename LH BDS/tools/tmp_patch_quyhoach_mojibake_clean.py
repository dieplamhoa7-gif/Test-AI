from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8')
patch=r'''
<script id="qh-mojibake-clean-final">
(function(){
  const dict={
    'd�n':'dân','D�n':'Dân','T�n':'Tân','B�nh':'Bình','Tr�':'Trị','D�ng':'Đông','ph?n':'phần','m?t':'một','thu?c':'thuộc','T?nh':'Tỉnh','l?':'lộ','Khu d�n cu':'Khu dân cư','Phu?ng':'Phường','Qu?n':'Quận','Th�nh ph?':'Thành phố','H? Ch� Minh':'Hồ Chí Minh','Di?n t�ch':'Diện tích','th?a':'thửa','d?t':'đất','D?t':'Đất','giao th�ng':'giao thông','c�ng tr�nh':'công trình','c�ng c?ng':'công cộng','M?t d?':'Mật độ','T?ng':'Tầng','quy ho?ch':'quy hoạch','x�y d?ng':'xây dựng','d?c':'dọc','ngu?n':'nguồn','d? li?u':'dữ liệu','�?ang':'Đang','�?ã':'Đã','Ch?a':'Chưa','kh�ng':'không','TA3m t��_t':'Tóm tắt','Tr���ng thA�i':'Trạng thái','GiA�':'Giá','mA�':'m²','M�?XD':'MĐXD','HSSD�?':'HSSDĐ','T��ng cao':'Tầng cao','Ch��cc n��ng':'Chức năng','�?��" A�n':'Đồ án','C��ng':'Cổng','quy ho���ch':'quy hoạch','chA-nh':'chính','�?��T r��Tng':'Độ rộng','�`����?ng':'đường','H����>ng':'Hướng','m���t ti��?n':'mặt tiền'};
  function fixText(t){
    if(t==null) return t; let x=String(t);
    for(const [a,b] of Object.entries(dict)) x=x.split(a).join(b);
    x=x.replace(/\uFFFD/g,'')
       .replace(/\?\?/g,'')
       .replace(/\s+/g,' ')
       .replace(/m\s*²/g,'m²')
       .trim();
    return x;
  }
  window.fixMojibake=fixText;
  const oldKv=window.kv;
  if(typeof oldKv==='function') window.kv=function(k,v){ return oldKv(fixText(k),fixText(v)); };
  const oldClean=window.cleanText;
  if(typeof oldClean==='function') window.cleanText=function(v){ return fixText(oldClean(v)); };
  function walk(n){
    if(!n) return;
    if(n.nodeType===3){ const y=fixText(n.nodeValue); if(y!==n.nodeValue) n.nodeValue=y; return; }
    if(n.nodeType!==1 || ['SCRIPT','STYLE','TEXTAREA','INPUT'].includes(n.tagName)) return;
    for(const c of [...n.childNodes]) walk(c);
  }
  function apply(){ walk(document.getElementById('locationBox')); walk(document.getElementById('planningBox')); walk(document.getElementById('indicatorBox')); walk(document.getElementById('sourceBox')); walk(document.getElementById('riskBox')); }
  window.__fixQHMojibake=apply;
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply); else apply();
  setTimeout(apply,500); setTimeout(apply,2000); setInterval(apply,1500);
  try{new MutationObserver(apply).observe(document.body,{childList:true,subtree:true,characterData:true});}catch(e){}
})();
</script>
'''
if 'qh-mojibake-clean-final' not in s:
    s=s.replace('</body></html>', patch+'</body></html>')
p.write_text(s,encoding='utf-8')
print('patched mojibake cleaner')
