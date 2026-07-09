from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\tpre_flowchart_popup.html')
s=p.read_text(encoding='utf-8')
# add css for expert sections
css='.expertGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;grid-column:1/-1}.expertCard{border:1px solid #e2e8f0;border-radius:16px;background:linear-gradient(180deg,#fff,#fbfdff);padding:14px}.expertCard h4{margin:0 0 8px;text-transform:uppercase;font-size:11px;letter-spacing:.08em;color:#0b3d91}.warn{border-color:#ffe3e3;background:#fff8f8}.warn h4{color:#c92a2a}.pro{border-color:#d3f9d8;background:#fbfffb}.pro h4{color:#2b8a3e}@media(max-width:900px){.expertGrid{grid-template-columns:1fr}}\n'
s=s.replace('@media(max-width:900px){.dossier{grid-template-columns:1fr}.lawPoint{grid-template-columns:1fr;gap:3px}}',css+'@media(max-width:900px){.dossier{grid-template-columns:1fr}.lawPoint{grid-template-columns:1fr;gap:3px}}')
old="""<div class=\"section full\"><h4>Kết quả / output pháp lý</h4>${lines(it.outputs)}</div><div class=\"section full\"><h4>Luật liên quan — tóm tắt trước, nguồn điều/khoản sau</h4><div class=\"lawGrid\">${laws(it.legal_basis)}</div></div>`; modal.classList.add('open')}"""
new="""<div class=\"section full\"><h4>Kết quả / output pháp lý</h4>${lines(it.outputs)}</div><div class=\"expertGrid\"><div class=\"expertCard\"><h4>Khi nào áp dụng</h4>${lines(applyFor(p.id))}</div><div class=\"expertCard\"><h4>Cơ quan / thẩm quyền</h4>${lines(authorityFor(p.id))}</div><div class=\"expertCard\"><h4>Phụ thuộc trước / sau</h4>${lines(dependencyFor(p.id))}</div><div class=\"expertCard warn\"><h4>Rủi ro & lỗi thường gặp</h4>${lines(riskFor(p.id))}</div><div class=\"expertCard pro\"><h4>Checklist CĐT/NĐT</h4>${lines(checklistFor(p.id))}</div><div class=\"expertCard pro\"><h4>Ghi chú chuyên gia</h4>${lines(expertFor(p.id))}</div></div><div class=\"section full\"><h4>Luật liên quan — tóm tắt trước, nguồn điều/khoản sau</h4><div class=\"lawGrid\">${laws(it.legal_basis)}</div></div>`; modal.classList.add('open')}"""
s=s.replace(old,new)
insert=r'''
function applyFor(id){return {
I:['Áp dụng cho mọi dự án trước khi quyết định mua đất, nhận chuyển nhượng dự án, tham gia đấu giá/đấu thầu hoặc nộp CTCTĐT.','Đặc biệt cần khi dự án có đất hỗn hợp, đất công xen kẹt, pháp lý cũ, M&A dự án dở dang hoặc chưa rõ route chọn NĐT.'],
II:['Áp dụng khi dự án phải tạo quỹ đất sạch, có thu hồi đất, bồi thường, hỗ trợ, TĐC, tự thỏa thuận nhận QSDĐ hoặc xử lý M&A/quyền dự án.'],
III:['Áp dụng khi dự án thuộc diện phải chấp thuận chủ trương đầu tư/chấp thuận NĐT hoặc phải xác lập tư cách CĐT trước khi triển khai đất, quy hoạch, xây dựng.'],
IV:['Áp dụng khi dự án cần QHCT 1/500, quy hoạch tổng mặt bằng hoặc điều chỉnh chỉ tiêu quy hoạch làm cơ sở thiết kế, đất, GPXD, bán hàng.'],
V:['Áp dụng khi cần giao đất, thuê đất, chuyển mục đích, xác định giá đất/nghĩa vụ tài chính hoặc cấp GCN QSDĐ dự án.'],
VI:['Áp dụng cho giai đoạn chuẩn bị thi công: thiết kế, thẩm định, PCCC, môi trường, đấu nối, GPXD và thông báo khởi công.'],
VII:['Áp dụng khi dự án đã có điều kiện khởi công và triển khai san nền, HTKT, HTXH, nhà thấp tầng/cao tầng, tiện ích/cảnh quan.'],
VIII:['Áp dụng khi CĐT muốn huy động vốn, mở bán, ký HĐMB, bán/cho thuê mua nhà ở hoặc BĐS hình thành trong tương lai.'],
IX:['Áp dụng khi hoàn thành hạng mục/công trình cần nghiệm thu với nhà thầu, PCCC, môi trường và CQNN để đưa vào sử dụng.'],
X:['Áp dụng khi bàn giao HTKT/HTXH, bàn giao nhà cho khách hàng và làm thủ tục cấp GCN cho người mua.'],
XI:['Áp dụng sau bàn giao: quản lý vận hành, bảo hành, xử lý tồn tại, hậu kiểm và hồ sơ pháp lý sau bán.']}[id]||[]}
function authorityFor(id){return {
I:['Nội bộ CĐT/NĐT chủ trì; phối hợp tư vấn pháp lý, quy hoạch, kỹ thuật, tài chính, kinh doanh.','Có thể cần xác minh thông tin tại Sở TNMT, Sở Xây dựng/Sở QHKT, UBND địa phương, VPĐK đất đai.'],
II:['UBND cấp có thẩm quyền, cơ quan TNMT, tổ chức phát triển quỹ đất, hội đồng bồi thường/GPMB, UBND cấp xã/huyện.'],
III:['UBND cấp tỉnh, Thủ tướng hoặc Quốc hội tùy thẩm quyền; cơ quan đăng ký đầu tư/Sở KHĐT; Sở ngành lấy ý kiến; cơ quan tổ chức đấu giá/đấu thầu nếu có.'],
IV:['Cơ quan quy hoạch kiến trúc/Sở Xây dựng/Sở QHKT, UBND cấp có thẩm quyền, hội đồng thẩm định quy hoạch nếu áp dụng.'],
V:['UBND cấp tỉnh/cấp huyện, Sở TNMT, VPĐK đất đai, cơ quan thuế, Sở Tài chính, hội đồng thẩm định giá đất.'],
VI:['Cơ quan chuyên môn về xây dựng, Sở Xây dựng/Sở quản lý công trình chuyên ngành, Cảnh sát PCCC, cơ quan môi trường, đơn vị quản lý hạ tầng kỹ thuật, cơ quan cấp GPXD.'],
VII:['CĐT, nhà thầu, tư vấn giám sát, tư vấn thiết kế, cơ quan quản lý trật tự xây dựng/chuyên môn xây dựng khi kiểm tra.'],
VIII:['Sở Xây dựng/cơ quan quản lý nhà ở và thị trường BĐS, ngân hàng bảo lãnh, CĐT, sàn/đơn vị kinh doanh nếu có.'],
IX:['CĐT, nhà thầu, tư vấn giám sát, cơ quan chuyên môn về xây dựng, Cảnh sát PCCC, cơ quan môi trường/đơn vị đấu nối.'],
X:['VPĐK đất đai, cơ quan TNMT, UBND có thẩm quyền, cơ quan thuế, ngân hàng giải chấp, ban quản lý/vận hành.'],
XI:['CĐT, đơn vị vận hành, nhà thầu bảo hành, ban quản trị/khách hàng, cơ quan quản lý khi hậu kiểm/khiếu nại.']}[id]||[]}
function dependencyFor(id){return {
I:['Đầu vào cho toàn bộ flow: quyết định có đi tiếp hay không, đi theo route nào, ngân sách và tiến độ nào.','Nếu Pre-FS sai, các bước CTCTĐT, đất, quy hoạch, tài chính và bán hàng sẽ sai theo.'],
II:['Phụ thuộc bản đồ ranh, hiện trạng, pháp lý đất và ngân sách.','Là điều kiện then chốt cho giao đất, thi công, cấp GCN; có thể chạy song song CTCTĐT/QHCT nhưng không được bỏ qua đường găng.'],
III:['Phụ thuộc quy hoạch/kế hoạch nhà ở/kế hoạch sử dụng đất, năng lực NĐT, route đất.','Output là nền cho giao đất, ký quỹ, triển khai thiết kế/quy hoạch và các thủ tục tiếp theo.'],
IV:['Phụ thuộc quy hoạch cấp trên, chỉ tiêu được duyệt, dữ liệu hiện trạng.','Output QHCT là input cho thiết kế, GPXD, đất, nghĩa vụ tài chính, bán hàng, cấp sổ.'],
V:['Phụ thuộc CTCTĐT/QHCT/GPMB/bản đồ/cắm mốc.','Output đất và tài chính là nền cho GCN, điều kiện bán, cấp sổ và bảo đảm pháp lý dự án.'],
VI:['Phụ thuộc QHCT, quyết định đất/ranh, khảo sát và yêu cầu sản phẩm.','Output là điều kiện khởi công, thi công, nghiệm thu, bán hàng và bàn giao.'],
VII:['Phụ thuộc GPXD/TKBVTC/điều kiện khởi công.','Nghiệm thu giai đoạn tạo mốc cho bán HTTTL; hoàn công tạo điều kiện nghiệm thu/cấp sổ.'],
VIII:['Phụ thuộc đất, thiết kế, GPXD, bảo lãnh, nghiệm thu mốc và công khai thông tin.','Output bán hàng tạo nghĩa vụ hợp đồng, bàn giao, bảo lãnh và cấp GCN cho khách hàng.'],
IX:['Phụ thuộc thi công đúng thiết kế, hồ sơ chất lượng, PCCC, môi trường, đấu nối.','Output là điều kiện đưa vào sử dụng, bàn giao, vận hành, cấp sổ.'],
X:['Phụ thuộc nghiệm thu hoàn thành, nghĩa vụ tài chính, hoàn công, giải chấp.','Output kết thúc vòng pháp lý sản phẩm: bàn giao và GCN cho khách hàng.'],
XI:['Phụ thuộc hồ sơ bàn giao, hợp đồng bảo hành, danh mục tài sản.','Ảnh hưởng uy tín, khiếu nại, vận hành và hồ sơ pháp lý hậu dự án.']}[id]||[]}
function riskFor(id){return {
I:['Đánh giá thiếu đất công/xen kẹt, tranh chấp, thế chấp, hạn chế chuyển nhượng.','Nhầm route đấu giá/đấu thầu/chấp thuận NĐT dẫn tới mất thời gian hoặc không thể triển khai.'],
II:['Không kiểm soát khiếu nại, tài sản trên đất, hồ sơ chủ đất, kinh phí GPMB.','GPMB không theo phân kỳ nhưng kế hoạch thi công/bán hàng lại giả định đất sạch.'],
III:['Hồ sơ năng lực tài chính yếu; quy mô/tiến độ/tổng vốn không khớp thực tế.','Thiếu cập nhật kế hoạch nhà ở/kế hoạch sử dụng đất hoặc sai hình thức lựa chọn NĐT.'],
IV:['QHCT đẹp về kinh doanh nhưng không khớp hạ tầng, dân số, PCCC, giao thông.','Điều chỉnh QHCT sau khi đã thiết kế/bán hàng gây cascade điều chỉnh pháp lý.'],
V:['Giá đất tăng/không dự báo được làm vỡ phương án tài chính.','Chưa xong nghĩa vụ tài chính/GCN nhưng đã cam kết bán hàng/cấp sổ.'],
VI:['PCCC/GPMT/đấu nối làm muộn, phải sửa thiết kế.','Thiết kế không khớp QHCT/GPXD hoặc thiếu thẩm tra/thẩm định.'],
VII:['Thi công lệch GPXD/TKBVTC; thiếu hồ sơ nghiệm thu chất lượng.','Không tách mốc nghiệm thu phục vụ điều kiện bán hàng.'],
VIII:['Marketing/booking biến tướng thành huy động vốn trái điều kiện.','Mẫu HĐMB, bảo lãnh, thông tin công khai không khớp pháp lý thực tế.'],
IX:['Thiếu nghiệm thu PCCC/môi trường/đấu nối; hồ sơ hoàn công thiếu hoặc sai.','Tồn tại hiện trường làm chậm văn bản kiểm tra nghiệm thu.'],
X:['Sai diện tích, thiếu bản vẽ, chưa giải chấp, chưa hoàn tất nghĩa vụ tài chính.','Hồ sơ khách hàng không chuẩn làm chậm cấp GCN hàng loạt.'],
XI:['Không có quy trình bảo hành, không phân định lỗi nhà thầu/CĐT/khách hàng.','Thiếu hồ sơ vận hành gây tranh chấp về tài sản chung/riêng, phí, bàn giao.']}[id]||[]}
function checklistFor(id){return {
I:['Có bản đồ ranh và hồ sơ đất?','Có kiểm tra quy hoạch/kế hoạch sử dụng đất/kế hoạch nhà ở?','Có ma trận route pháp lý và risk register?'],
II:['Có danh sách chủ sử dụng đất và tài sản trên đất?','Có phương án vốn GPMB?','Có mốc hoàn tất GPMB theo phân kỳ?'],
III:['Có xác định thẩm quyền CTCTĐT?','Có hồ sơ năng lực tài chính?','Có route lựa chọn NĐT đúng luật?','Có kế hoạch ký quỹ/bảo đảm?'],
IV:['Có chỉ tiêu quy hoạch cấp trên?','Có design brief?','Có bản đồ hiện trạng/cao độ/cắm mốc?','Có kiểm tra PCCC/giao thông sơ bộ?'],
V:['Có QHCT và bản đồ HTVT?','Có hồ sơ giao/thuê đất/chuyển mục đích?','Có phương án giá đất/nghĩa vụ tài chính?','Có kế hoạch cấp GCN dự án?'],
VI:['Có khảo sát địa hình/địa chất?','Có TKCS/TKKT/TKBVTC?','Có PCCC, GPMT/ĐTM, đấu nối?','Có hồ sơ GPXD/thông báo khởi công?'],
VII:['Có GPXD/TKBVTC được duyệt?','Có kế hoạch nghiệm thu giai đoạn?','Có hồ sơ chất lượng/hoàn công cập nhật thường xuyên?'],
VIII:['Có đủ điều kiện bán HTTTL?','Có bảo lãnh?','Có mẫu HĐMB?','Có công khai thông tin dự án?','Có kiểm soát nội dung marketing?'],
IX:['Có hồ sơ hoàn công?','Có nghiệm thu PCCC/GPMT/đấu nối?','Có hồ sơ đề nghị CQNN kiểm tra nghiệm thu?'],
X:['Có bản vẽ sơ đồ nhà đất/phân lô?','Có xác nhận nghĩa vụ tài chính?','Có hồ sơ giải chấp?','Có bộ hồ sơ cấp GCN cho khách hàng?'],
XI:['Có quy trình bảo hành?','Có danh mục tồn tại?','Có hồ sơ vận hành/tài sản?','Có đầu mối xử lý khiếu nại?']}[id]||[]}
function expertFor(id){return {
I:['Đừng để Pre-FS chỉ là phân tích tài chính; pháp lý đất và route đầu tư quyết định dự án có chạy được hay không.'],
II:['GPMB nên quản trị như một dự án riêng với ngân sách, tiến độ, rủi ro và owner rõ.'],
III:['CTCTĐT nên chốt đủ rộng để tránh phải điều chỉnh nhiều lần, nhưng không quá mơ hồ gây khó thẩm định.'],
IV:['QHCT phải được kiểm tra ngược từ sản phẩm bán hàng, PCCC, giao thông, hạ tầng và cấp sổ.'],
V:['Giá đất/nghĩa vụ tài chính là biến số tài chính lớn; cập nhật financial model ngay khi có dữ liệu mới.'],
VI:['PCCC, môi trường, đấu nối nên có checklist riêng từ giai đoạn thiết kế cơ sở.'],
VII:['Hồ sơ hoàn công không thể làm thật tốt nếu đến cuối mới gom; phải quản trị từ đầu.'],
VIII:['Pháp lý bán hàng phải đi cùng sales script; sales nói sai trạng thái pháp lý là rủi ro lớn.'],
IX:['Nghiệm thu là bài kiểm tra tổng hợp của toàn bộ thiết kế/thi công/PCCC/môi trường; không phải chỉ là thủ tục cuối.'],
X:['Cấp sổ nên chuẩn bị trước bàn giao, không đợi khách hàng thúc mới gom hồ sơ.'],
XI:['Hậu bàn giao tốt giúp giảm tranh chấp và bảo vệ thương hiệu dự án sau bán.']}[id]||[]}
'''
marker='function splitPoint(x)'
s=s.replace(marker,insert+'\n'+marker)
p.write_text(s,encoding='utf-8')
print('patched expert sections')
