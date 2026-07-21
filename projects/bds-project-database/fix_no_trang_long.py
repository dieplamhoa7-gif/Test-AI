from pathlib import Path
import json,csv
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database');p=B/'project_master_curated_deduped.json';rows=json.load(open(p,encoding='utf-8'))
# Merge update record into the named address project; create structured scenarios from explicit report text.
parent=next(r for r in rows if r.get('curated_id')=='BDS-CURATED-0022'); child=next(r for r in rows if r.get('curated_id')=='BDS-CURATED-0059')
parent['project_name']='Dự án 353 Nơ Trang Long, Bình Thạnh';parent['project_name_raw']='tại 353 Nơ Trang Long';parent['mention_count']=int(parent.get('mention_count') or 0)+int(child.get('mention_count') or 0)
for f in ['source_files','senders','map_urls','source_excerpt','financial_raw_mentions','attachments','merged_from_ids']:
 vals=[]
 for v in [parent.get(f,''),child.get(f,''), 'BDS-CURATED-0059' if f=='merged_from_ids' else '']:
  for x in str(v or '').split(';'):
   if x.strip() and x.strip() not in vals:vals.append(x.strip())
 parent[f]='; '.join(vals)
parent.update({'land_area_main':'3.399 m²; phù hợp QH sau lộ giới: 3.195 m²','planning_doc_status':'QH 1/2000 – QĐ 5674/QĐ-UBND (2017)','planning_summary':'Chỉ tiêu 1/2000: HSSDĐ 6 lần, dân số 606, tầng cao 18, MĐXD 70%. Có 3 phương án FS; xem tab phương án.','financial_raw_mentions':'Đã bóc tách vào từng tab phương án; không hiển thị danh sách số raw không nhãn.'})
parent['scenario_data']=json.dumps([
 {'id':'pa1','title':'PA1 · Đúng QH 1/2000','status':'Cao tầng – phù hợp chỉ tiêu hiện hữu','area':'Sàn XD 25.289 m²; sàn KD 13.694 m² (căn hộ 12.151,3 m²; shop 1.543 m²)','planning':'18 tầng, 1 hầm, HSSDĐ 6 lần, dân số 465','products':'Căn hộ + shophouse khối đế 1 trệt 1 lầu','revenue':'Doanh thu chưa VAT: 984 tỷ','selling_price':'Căn hộ ~68 tr/m²; ShopTM 1T1L ~102 tr/m² (~1,5 lần căn hộ)','investment':'TMĐT chưa VAT, gồm lãi vay: 851 tỷ; all-in 18 tr/m²; mua đất 220 tỷ; TSDĐ thêm 3,2 tỷ','cost':'Chi phí hoạt động: 147,5 tỷ (15% doanh thu)','profit':'LNTT: 132 tỷ; LNTT/TMĐT: 19,6%'},
 {'id':'pa2','title':'PA2 · Xin thêm dân / HSSDĐ','status':'Cao tầng – vượt chỉ tiêu 1/2000, tham chiếu Ascent Plaza','planning':'24 tầng, 2 hầm, HSSDĐ 9 lần; xin điều chỉnh dân số','products':'Căn hộ + shophouse khối đế 1 trệt 1 lầu','revenue':'Doanh thu chưa VAT: 1.460 tỷ','selling_price':'Căn hộ ~68 tr/m²; ShopTM 1T1L ~102 tr/m²','investment':'TMĐT chưa VAT, gồm lãi vay: 1.254 tỷ; all-in 18,4 tr/m²; TSDĐ đóng thêm 96 tỷ','cost':'Chi phí hoạt động: 219 tỷ (15% doanh thu)','profit':'LNTT: 206 tỷ; LNTT/TMĐT: 20,9%'},
 {'id':'pa3','title':'PA3 · Shophouse thấp tầng','status':'Phương án thấp tầng','planning':'26 căn shophouse, 5 tầng','products':'26 shophouse thấp tầng','revenue':'Tổng doanh thu chưa VAT: 423 tỷ','selling_price':'1 căn góc: 30 tỷ (~201 tr/m² đất); 1 căn giữa: 28 tỷ (~195 tr/m²); 24 căn hẻm: ~15,2 tỷ/căn (~154 tr/m²)','investment':'TMĐT chưa VAT, gồm lãi vay: 350 tỷ; all-in xây dựng 11,7 tr/m²; mua đất 220 tỷ; tạm tính không đóng thêm TSDĐ','cost':'Chi phí hoạt động: 31 tỷ (8% doanh thu)','profit':'LNTT: 72 tỷ; LNTT/TMĐT: 22%'}
 ],ensure_ascii=False)
parent['product_structure']='Xem 3 tab phương án: PA1 đúng QH 1/2000; PA2 xin thêm dân/HSSDĐ; PA3 shophouse thấp tầng.'
rows=[r for r in rows if r.get('curated_id')!='BDS-CURATED-0059'];p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print({'merged':'BDS-CURATED-0059 -> BDS-CURATED-0022','remaining':len(rows)})
