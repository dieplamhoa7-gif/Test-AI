from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8')
# Insert official GIS/QHPKSDD card between official portal and Guland.
needle="],hcm),block('2. Guland - thông tin từ popup/map'"
gis="""],hcm),block('2. GIS Xây dựng TP.HCM - chỉ tiêu ô đất chính thức',[kv('Trạng thái',ex.status==='official_functional_lot_confirmed'?'Đã đọc được chỉ tiêu chính thức':'Chưa có chỉ tiêu chính thức'),kv('Mã ô phố',ex.ma_o_pho),kv('Chức năng đất',ex.chuc_nang_dat),kv('Diện tích ô chức năng',ex.dien_tich?`${Number(ex.dien_tich).toLocaleString('vi-VN')} m²`:''),kv('Dân số ô chức năng',ex.dan_so_lo_o_pho),kv('Tầng cao',ex.tang_cao||ex.chieu_cao),kv('MĐXD',ex.mat_do_xay_dung?`${ex.mat_do_xay_dung}%`:''),kv('HSSDĐ',ex.he_so_su_dung_dat),kv('Nguồn API',ex.source_url?`qhpksdd/${String(ex.source_url).split('/').pop()}`:'')],ex.source_url||'https://gisxaydung.tphcm.gov.vn/tracuuttqh'),block('3. Guland - thông tin từ popup/map'"""
if needle not in s: raise SystemExit('insert needle not found')
s=s.replace(needle,gis,1)
s=s.replace("block('3. Google Maps / OSM - định vị'","block('4. Google Maps / OSM - định vị'",1)
# Replace blank placeholders in Guland card with explicit source truth for this point.
s=s.replace("kv('Tờ/thửa',gv?.parcel?.map_sheet?`${gv.parcel.map_sheet}/${gv.parcel.parcel_no}`:'')","kv('Tờ/thửa',gv?.parcel?.map_sheet?`${gv.parcel.map_sheet}/${gv.parcel.parcel_no}`:'Không có trong popup tại điểm này')",1)
s=s.replace("kv('Diện tích thửa',gv?.parcel?.area_m2?`${Number(gv.parcel.area_m2).toLocaleString('vi-VN')} m²`:'')","kv('Diện tích thửa',gv?.parcel?.area_m2?`${Number(gv.parcel.area_m2).toLocaleString('vi-VN')} m²`:'Không có trong popup tại điểm này')",1)
s=s.replace("kv('Hiện trạng thửa',gv?.parcel?.land_code?`${gv.parcel.land_code} - ${cleanText(gv.parcel.land_use||'')}`:cleanText(gv?.parcel?.land_use||''))","kv('Hiện trạng thửa',gv?.parcel?.land_code?`${gv.parcel.land_code} - ${cleanText(gv.parcel.land_use||'')}`:(cleanText(gv?.parcel?.land_use||'')||'Không có trong popup tại điểm này'))",1)
s=s.replace("kv('Quy hoạch xây dựng',(gv?.planning||[]).filter(x=>x.kind==='construction_planning'||x.land_use).map(x=>`${x.area_m2?Number(x.area_m2).toLocaleString('vi-VN')+' m² ':''}${x.code?x.code+' - ':''}${cleanText(x.land_use||'')}`).join('<br>'))","kv('Quy hoạch xây dựng',((gv?.planning||[]).filter(x=>x.kind==='construction_planning'||x.land_use).map(x=>`${x.area_m2?Number(x.area_m2).toLocaleString('vi-VN')+' m² ':''}${x.code?x.code+' - ':''}${cleanText(x.land_use||'')}`).join('<br>'))||'Không có layer chỉ tiêu trong popup tại điểm này')",1)
p.write_text(s,encoding='utf-8',newline='\n')
print('filled GIS official fields and truthful Guland fields')
