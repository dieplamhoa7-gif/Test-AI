from pathlib import Path
import json,csv
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=base/'project_master_curated_deduped.json'; rows=json.loads(p.read_text(encoding='utf-8'))
r=next(x for x in rows if x.get('project_name')=='Đông Trung')
# Curated from four Teams reports; preserve raw excerpt but prevent mixed scenarios from appearing as one current fact.
r.update({
 'land_area_main':'Phương án pháp lý điều chỉnh: 4,6 ha',
 'land_area_main_raw':'Tổng quy mô ban đầu: 12 ha; quy mô điều chỉnh: 4,6 ha',
 'other_area_mentions':'PA NOTM: 4,8 ha; đất công/NƠ cán bộ: 8.000 m²; đất công phát hiện: 5,4 ha',
 'project_type':'Đất ở hỗn hợp: chung cư cao tầng + nhà phố thấp tầng',
 'product_structure':'PA 4,6 ha: 111 nhà phố liền kề + 5 tháp chung cư trung cấp (1.622 căn); PA tách: 2 khu chung cư 40 tầng (1.886 căn) + 2 khu thấp tầng (116 nền) + 2 block NƠ cán bộ 18 tầng (~359 căn)',
 'planning_doc_status':'Đã có QH 1/500 cho quy mô 12 ha; đã trình điều chỉnh QH 1/500 theo quy mô 4,6 ha',
 'planning_summary':'Quy hoạch cũ: 12 ha, nhà phố thấp tầng, dân số 2.970. Sau rà soát 5,4 ha có nguồn gốc đất công, trình QH 1/500 điều chỉnh còn 4,6 ha gồm đất ở thấp tầng và đất ở hỗn hợp cao tầng. PA tách sau đó: 4,8 ha NOTM + 8.000 m² đất công/NƠ cán bộ.',
 'max_floors_clean':'PA tách: chung cư 40 tầng; NƠ cán bộ 18 tầng',
 'far_clean':'HSSDĐ toàn khu: 3,8 lần',
 'population_clean':'QH cũ: 2.970 người; PA hiệu quả NOTM xem xét 3.950 hoặc 3.021 dân; PA tách: 3.950 dân cho 4,8 ha NOTM + ~550 dân NƠ cán bộ',
 'legal_summary':'Đất: 4,6 ha đã đền bù cho dân. Đầu tư: đã có chủ trương đầu tư nhà phố thấp tầng cho 12 ha; UBND đã chấp thuận chủ trương điều chỉnh sang đất ở cao tầng và nhà phố thấp tầng, giảm quy mô còn 4,6 ha. Xây dựng: chưa có.',
 'legal_status':'4,6 ha đã đền bù cho dân; chưa có pháp lý xây dựng',
 'gpm_status':'Giá trị bồi thường dự kiến được khấu trừ khi đấu thầu: ~468 tỷ (ước ~5 tr/m²)',
 'lur_status':'TSDĐ tạm tính: 32,6 tr/m²; tổng ~1.250 tỷ. Sau khấu trừ bồi thường GPMB, TSDĐ dự kiến ~780 tỷ.',
 'approval_status':'Đã có chủ trương đầu tư 12 ha; UBND chấp thuận điều chỉnh chủ trương giảm về 4,6 ha',
 'asking_land_price':'Chưa có giá chào/mua đất dự án được xác nhận',
 'selling_price':'PA nhà phố: 65 tr/m² đất (giả định cuối 2025). PA căn hộ NOTM: 40,6–45 tr/m² tim tường, chưa VAT.',
 'land_cost':'TSDĐ: đơn giá tạm tính 32,6 tr/m²; tổng ~1.250 tỷ; sau khấu trừ GPMB ~780 tỷ.',
 'total_investment_clean':'Suất đầu tư XD-TB all-in: 13,9 tr/m² (giá 2028); quy đổi hiện tại ~12,6 tr/m²',
 'revenue_clean':'DTKD căn hộ theo PA đầu: 88.422 m² sàn; giá bán bình quân tham chiếu 36,5 tr/m²',
 'profit_clean':'Chưa trích được lợi nhuận chuẩn chung vì các tin là nhiều phương án khác nhau',
 'irr_clean':'IRR chủ đầu tư: 25% (cần xác nhận tương ứng phương án nào)',
 'financial_raw_mentions':'Giữ tại source excerpt; không dùng làm số liệu chuẩn do gồm giá tham chiếu các dự án khác và nhiều phương án.',
 'risks':'5,4 ha có nguồn gốc đất công; chưa có pháp lý xây dựng; hiệu quả phụ thuộc xin chỉ tiêu dân số. PA 3.950 dân hiệu quả hơn PA 3.021 dân.',
 'next_actions':'Xác nhận phương án được chọn (4,6 ha hay PA tách 4,8 ha + 0,8 ha); xác minh chỉ tiêu dân số; rà soát QH 1/500 điều chỉnh, đất công, TSDĐ và pháp lý xây dựng.',
 # The Teams map link matched with score 20 but falls outside Bình Dương; remove it pending verified source.
 'latitude':'','longitude':'','coordinates':'','map_urls':'','coordinate_source':'','coordinate_quality':'needs_coordinate_review','coordinate_anomaly_note':'Tọa độ cũ 20.185875,106.3661313 không phù hợp địa bàn Bình Dương; match Teams map score 20 nên đã gỡ chờ xác minh.',
 'map_link_attached_from_chunk':'','map_link_match_score':''
})
# Ensure new field is present in every record for stable CSV.
for x in rows:x.setdefault('product_structure','')
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='ignore');w.writeheader();w.writerows(rows)
print('Patched Đông Trung',r['curated_id'])
