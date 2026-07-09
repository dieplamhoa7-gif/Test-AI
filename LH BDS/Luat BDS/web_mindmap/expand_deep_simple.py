import json
from pathlib import Path
web=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap')
deploy=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process')
path=web/'bds_process_timeline_lawfaithful.json'
data=json.loads(path.read_text(encoding='utf-8'))
DEEP={
'gate6':{
'deep_summary':'Huy động vốn/mở bán là vùng rủi ro cao nhất về tranh chấp và xử phạt. Cần tách rõ booking, đặt cọc, hợp đồng mua bán, góp vốn/hợp tác để không biến thành huy động trái phép.',
'detail_conditions':['Có QSDĐ/quyết định đất phù hợp với dự án.','Có hồ sơ dự án, QHCT, thiết kế/GPXD theo loại công trình.','Đã nghiệm thu mốc móng/hạ tầng hoặc mốc tương ứng theo loại sản phẩm.','Đã công khai thông tin dự án/BĐS trước khi kinh doanh.','Có bảo lãnh NH cho nhà ở HTTTL nếu thuộc diện.','HĐ mẫu, tiến độ thanh toán, quảng cáo không vượt điều kiện pháp lý.'],
'detail_steps':['Lập checklist pháp lý bán hàng theo từng loại sản phẩm.','Hoàn tất nghiệm thu mốc bắt buộc và hồ sơ xây dựng liên quan.','Làm bảo lãnh NH nếu là nhà ở HTTTL thuộc diện.','Công khai thông tin dự án, sản phẩm, HĐ mẫu, pháp lý đất/quy hoạch/xây dựng.','Gửi thông báo/xin xác nhận đủ điều kiện bán nếu pháp luật hoặc địa phương yêu cầu.','Ký HĐ đúng mẫu, thu tiền đúng tiến độ, lưu hồ sơ khách hàng.'],
'detail_authority':['Sở Xây dựng thường là đầu mối xác nhận/thông báo đủ điều kiện bán nhà ở HTTTL tùy địa phương.','Ngân hàng thương mại phát hành bảo lãnh.','Cơ quan quản lý hệ thống thông tin nhà ở/thị trường BĐS đối với công khai thông tin.'],
'detail_timeline':['Chuẩn bị bộ pháp lý bán hàng: 2–6 tuần nếu nền pháp lý đủ.','Thông báo/xác nhận đủ điều kiện bán: thường khoảng 15 ngày làm việc tùy địa phương và hồ sơ.','Bảo lãnh NH: 2–8 tuần tùy ngân hàng, hạn mức, tài sản bảo đảm và pháp lý dự án.'],
'detail_mistakes':['Thu booking/đặt cọc thực chất như huy động vốn khi chưa đủ điều kiện.','Quảng cáo tiện ích/tiến độ/pháp lý vượt thực tế.','Không có bảo lãnh nhưng vẫn bán nhà ở HTTTL thuộc diện phải bảo lãnh.','HĐ mẫu không khớp luật hoặc không công khai thông tin đầy đủ.']},
'gate2':{
'deep_summary':'Bước này biến cơ hội thành dự án có NĐT hợp lệ. Trọng tâm là đúng thẩm quyền CTCTĐT và đúng route chọn NĐT; sai route có thể phải quay lại từ đầu.',
'detail_conditions':['Xác định được thẩm quyền CTCTĐT hoặc dự án không thuộc diện CTCTĐT.','NĐT có tư cách pháp lý, năng lực tài chính, kinh nghiệm phù hợp.','Đề xuất dự án thống nhất với đất, quy hoạch, tổng vốn, tiến độ, GPMB.','Nếu thuộc diện đấu thầu NĐT thì phải theo mời quan tâm/HSMT/HSDT/kết quả lựa chọn.'],
'detail_steps':['Phân loại dự án theo thẩm quyền CTCTĐT.','Phân loại route chọn NĐT: đấu giá, đấu thầu, chấp thuận NĐT, công nhận chủ đầu tư.','Chuẩn bị hồ sơ đề xuất dự án và năng lực NĐT.','Nộp hồ sơ, theo dõi thẩm định, giải trình đất/quy hoạch/vốn/môi trường.','Nhận CTCTĐT/kết quả chọn NĐT và kiểm điều kiện kèm theo.'],
'detail_authority':['Sở KHĐT thường là đầu mối cấp tỉnh.','UBND tỉnh/Thủ tướng/Quốc hội tùy thẩm quyền.','Bên mời quan tâm/bên mời thầu/cơ quan quyết định tổ chức đấu thầu nếu đấu thầu NĐT.'],
'detail_timeline':['CTCTĐT thực tế thường 45–120+ ngày tùy thẩm quyền/hồ sơ.','Đấu thầu NĐT có thể vài tháng đến hơn 1 năm.','Vòng giải trình có thể kéo dài nếu đất/quy hoạch/tổng vốn chưa nhất quán.'],
'detail_mistakes':['Nộp CTCTĐT khi route đất chưa rõ.','Năng lực tài chính không tương xứng tổng vốn.','Tổng vốn/diện tích/tiến độ không khớp giữa hồ sơ đầu tư và quy hoạch/đất.','Không dự phòng tình huống đấu thầu cạnh tranh.']},
'gate3':{
'deep_summary':'Đất đai là điểm nghẽn lớn nhất của dự án BĐS. Có CTCTĐT hoặc trúng thầu chưa đủ; cần đất sạch, quyết định đất, tiền đất và đăng ký đất phù hợp.',
'detail_conditions':['Có căn cứ giao đất/thuê đất/chuyển mục đích hoặc kết quả đấu giá/đấu thầu/CTCTĐT.','GPMB hoàn thành hoặc có lộ trình bàn giao theo tiến độ.','Có cơ sở xác định tiền SDĐ/tiền thuê đất/giá đất.','Không có tranh chấp, kê biên, hạn chế giao dịch cản trở dự án.'],
'detail_steps':['Hoàn thiện GPMB/bồi thường/tái định cư hoặc nhận bàn giao đất theo tiến độ.','Nộp hồ sơ giao đất/thuê đất/chuyển mục đích.','Xác định giá đất, tiền SDĐ/tiền thuê đất, chi phí bồi thường được xử lý.','Nộp nghĩa vụ tài chính hoặc hoàn tất cơ chế khấu trừ/miễn giảm nếu có.','Đăng ký đất, cấp/chỉnh lý GCN, cập nhật hồ sơ dự án.'],
'detail_authority':['Sở TNMT/Văn phòng đăng ký đất đai.','UBND cấp tỉnh hoặc cơ quan được phân cấp quyết định đất.','Cơ quan thuế/tài chính/hội đồng thẩm định giá đất tùy nội dung tiền đất.'],
'detail_timeline':['GPMB: 6–24+ tháng tùy số hộ và độ phức tạp.','Giao/thuê/chuyển mục đích và tiền đất: thường 1–6+ tháng nếu hồ sơ rõ.','Cấp/chỉnh lý GCN: thường 30–90+ ngày sau khi đủ điều kiện.'],
'detail_mistakes':['Không khóa chi phí GPMB và tiền đất trong mô hình tài chính.','Quyết định đất lệch ranh/diện tích/mục đích so với quy hoạch.','Chưa xong nghĩa vụ tài chính nhưng đã cam kết mở bán/cấp sổ.','Không kiểm đất xen kẹt, đường vào, hạ tầng ngoài ranh.']}
}
for s in data['steps']:
    d=DEEP.get(s['id'])
    if d: s.update(d)
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(deploy/'bds_process_timeline_lawfaithful.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('expanded deep simple')
