from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("body:JSON.stringify({...c,includeGuland:true,includeQhViet:true})", "body:JSON.stringify({...c,includeGuland:false,includeQhViet:true})", 1)
needle="sourceBox.innerHTML=[block('1. Cổng quy hoạch TP.HCM - nguồn chính'"
idx=s.find(needle)
if idx<0: raise SystemExit('needle sourceBox not found')
end=s.find(";const warnings=[]", idx)
if end<0: raise SystemExit('end warnings not found')
insert_pos=end+1
async_code="""
try{setTimeout(async()=>{try{const rg=await fetch(API_BASE+'/planning/lookup',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({...c,includeGuland:true,includeQhViet:false})});const jg=await rg.json();if(!rg.ok||!jg.ok||!jg.guland)return;const gv2=jg.guland?.parsed||null;const heads=[...document.querySelectorAll('.source-result h3')];const h=heads.find(x=>String(x.textContent||'').includes('Guland'));const card=h?h.closest('.source-result'):null;if(card){card.innerHTML=`<h3>3. Guland - tách chỉ tiêu từ popup/map</h3>${[kv('Trạng thái',jg.guland?.ok?'Đã đọc được':'Chưa đọc được: '+(jg.guland?.error||'không có dữ liệu')),kv('Tóm tắt',jg.guland?.summary),kv('Tờ/thửa',gv2?.parcel?.map_sheet?`${gv2.parcel.map_sheet}/${gv2.parcel.parcel_no}`:''),kv('Diện tích thửa',gv2?.parcel?.area_m2?`${Number(gv2.parcel.area_m2).toLocaleString('vi-VN')} m²`:''),kv('Hiện trạng thửa',gv2?.parcel?.land_code?`${gv2.parcel.land_code} - ${cleanText(gv2.parcel.land_use||'')}`:cleanText(gv2?.parcel?.land_use||'')),kv('Các ô/chức năng đọc được',areaRows(gv2)),kv('Quy hoạch xây dựng',(gv2?.planning||[]).filter(x=>x.kind==='construction_planning'||x.land_use).map(x=>`${x.area_m2?Number(x.area_m2).toLocaleString('vi-VN')+' m² ':''}${x.code?x.code+' - ':''}${cleanText(x.land_use||'')}`).join('<br>')),kv('Giá/tin Guland đọc được',gulandDeals(jg.guland?.text||gv2?.raw_text||'')),kv('Tầng cao',gv2?.height||(gv2?.planning||[]).find(x=>x.height)?.height),kv('MĐXD',firstDensity(gv2)!=null?`${firstDensity(gv2)}%`:''),kv('HSSDĐ',firstFar(gv2)),kv('Raw popup',jg.guland?.text?cleanText(String(jg.guland.text).slice(0,700)):'')].join('')}<p><a href="${gulandUrl}" target="_blank" rel="noopener">Mở nguồn kiểm chứng</a></p>`;if(window.__forcePlanningNavy)window.__forcePlanningNavy();}}catch(e){}},80)}catch(e){}
"""
s=s[:insert_pos]+async_code+s[insert_pos:]
p.write_text(s,encoding='utf-8')
print('patched async guland')
