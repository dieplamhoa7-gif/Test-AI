import json, pathlib
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
d=json.loads((out/'legal_knowledge_v2.json').read_text(encoding='utf-8'))
# Create briefing structure in the style of the reference page
nodes={n['id']:n for n in d['nodes']}
legal_rows=[
 {'doc':'Luật Đất đai 2024','articles':'Điều 79, 116, 124, 125, 126, 127, 143, 228','scope':'Thu hồi đất; giao đất/cho thuê đất; đấu giá QSDĐ; đấu thầu dự án có sử dụng đất; thỏa thuận nhận QSDĐ; cấp GCN.','note':'VĂN BẢN NỀN'},
 {'doc':'Nghị định 102/2024/NĐ-CP','articles':'Điều 44, 49, 55, 57','scope':'Trình tự thủ tục giao đất, cho thuê đất, chuyển mục đích; công bố khu đất đấu thầu; thủ tục đấu giá/đấu thầu liên quan đất.','note':'HƯỚNG DẪN ĐẤT ĐAI'},
 {'doc':'Nghị định 103/2024/NĐ-CP','articles':'Điều 3, 4 và các điều liên quan','scope':'Tiền sử dụng đất, tiền thuê đất, căn cứ tính và nghĩa vụ tài chính đất đai.','note':'TÀI CHÍNH ĐẤT'},
 {'doc':'Luật Quy hoạch đô thị và nông thôn 2024','articles':'Điều 15, 16 và nhóm điều lập/thẩm định/phê duyệt quy hoạch','scope':'Căn cứ lập quy hoạch, trình tự lập nhiệm vụ quy hoạch và quy hoạch.','note':'QUY HOẠCH'},
 {'doc':'Luật Kinh doanh BĐS và nghị định hướng dẫn','articles':'Điều kiện BĐS hình thành trong tương lai, bảo lãnh, hợp đồng','scope':'Điều kiện huy động vốn, bán/cho thuê mua nhà ở hình thành trong tương lai.','note':'KINH DOANH BĐS'},
 {'doc':'Nghị định 274/2026/NĐ-CP','articles':'Điều 4, 9, 10-43, Phụ lục I-II','scope':'Quy trình lựa chọn nhà đầu tư dự án đầu tư kinh doanh theo link mẫu.','note':'CẦN BỔ SUNG NGUỒN NẾU CHƯA CÓ'},
]
branch_questions=[
 {'title':'Rẽ nhánh 1 — Cơ chế đầu tư','body':'Dự án có thuộc diện chấp thuận chủ trương đầu tư không? Nếu có, xác định cơ quan chấp thuận, nội dung chấp thuận và khả năng đồng thời chấp thuận nhà đầu tư.'},
 {'title':'Rẽ nhánh 2 — Cơ chế tiếp cận đất','body':'Quỹ đất đi theo đấu giá QSDĐ, đấu thầu lựa chọn NĐT dự án có sử dụng đất, giao/thuê đất không đấu giá đấu thầu, hay nhà đầu tư thỏa thuận nhận QSDĐ/đang có QSDĐ?'},
 {'title':'Rẽ nhánh 3 — Điều kiện đưa vào kinh doanh','body':'Sau đất đai, tài chính, thiết kế, xây dựng: dự án đã đủ điều kiện huy động vốn/bán BĐS hình thành trong tương lai chưa, có bảo lãnh và thông báo đủ điều kiện chưa?'},
]
process_groups=[
 ['1','Nhà ở thương mại/khu đô thị thông thường','P0 → P9','Quy hoạch → CTĐT/lựa chọn NĐT → đất đai → tài chính → xây dựng → bán hàng → cấp sổ','Luồng chính'],
 ['2','Quỹ đất phải đấu giá QSDĐ','Nhánh P2.2.1','Kiểm tra trường hợp đấu giá, điều kiện quỹ đất, phương án đấu giá, giá khởi điểm, kết quả trúng đấu giá','Nhánh đất đai'],
 ['3','Dự án phải đấu thầu lựa chọn NĐT','Nhánh P2.2.2','Danh mục khu đất/dự án, công bố dự án, mời quan tâm nếu có, HSMT/HSDT, kết quả lựa chọn NĐT','Cần NĐ 274 nếu áp dụng'],
 ['4','Nhà đầu tư thỏa thuận/đang có QSDĐ','Nhánh P2.2.3','Kiểm tra điều kiện nhận chuyển nhượng/thuê/góp vốn QSDĐ, chuyển mục đích, phù hợp quy hoạch và thủ tục đầu tư','Nhánh private land'],
]
steps=['p0','p1','p2','p2_ctdt','p2_lcnt','p2_daugia','p2_dauthau','p2_thoathuan','p3','p4','p5','p6','p7','p8','p9']
brief={'title':'Quy trình pháp lý phát triển dự án BĐS nhà ở','subtitle':'Bản trình bày theo format legal briefing: căn cứ pháp lý → logic rẽ nhánh → nhóm quy trình → từng bước chi tiết → trích dẫn điều luật.', 'legal_rows':legal_rows,'branch_questions':branch_questions,'process_groups':process_groups,'steps':[nodes[s] for s in steps if s in nodes]}
(out/'legal_briefing_format.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding='utf-8')
print('brief steps',len(brief['steps']))
