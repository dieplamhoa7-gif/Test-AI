import json, re
from pathlib import Path
web=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap')
deploy=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process')
js=web/'bds_process_timeline_lawfaithful.json'
data=json.loads(js.read_text(encoding='utf-8'))

def clean_point(p):
    p=re.sub(r'\s+',' ',p or '').strip(' ;,.•-–—')
    p=re.sub(r'^[A-Za-zÀ-ỹ]\)\s*$', '', p)  # lone y), a)
    p=re.sub(r'^\.\s*','',p)                 # .1 / .abc
    p=re.sub(r'^[A-Za-zÀ-ỹ]\s+(?=\d+[\).]|[a-zđ]\))','',p)
    return p.strip()
for s in data.get('steps',[]):
    for key in ['legal_points']:
        for b in s.get(key,[]):
            b['points']=[x for x in (clean_point(p) for p in b.get('points',[])) if x and not re.fullmatch(r'[A-Za-zÀ-ỹ]\)?|\.?\d+',x)]
    for proc in s.get('procedures',[]):
        for b in proc.get('legal_points',[]):
            b['points']=[x for x in (clean_point(p) for p in b.get('points',[])) if x and not re.fullmatch(r'[A-Za-zÀ-ỹ]\)?|\.?\d+',x)]
DETAIL={
'gate0':('Điều kiện: có hồ sơ QSDĐ/rường ranh, hiện trạng, quy hoạch sơ bộ; xác định được route đất.','Bước làm: thu hồ sơ đất → kiểm quy hoạch/kế hoạch SDĐ → kiểm GPMB/tranh chấp → lập ma trận route.','Thời gian: rà nhanh 3–15 ngày; xin thông tin quy hoạch/địa chính thường 2–6 tuần.','Hồ sơ: GCN/QĐ đất, bản đồ ranh, thông tin quy hoạch, hiện trạng GPMB, hồ sơ chủ đất.'),
'gate1':('Điều kiện: quy hoạch cấp trên cho phép hoặc có cơ sở điều chỉnh; chỉ tiêu đủ hiệu quả tài chính.','Bước làm: lấy thông tin quy hoạch → lập chỉ tiêu/sản phẩm → kiểm hạ tầng/dân số/bãi xe → lập/điều chỉnh QHCT nếu cần.','Thời gian: thông tin quy hoạch thường 10–20 ngày làm việc; QHCT/điều chỉnh có thể 3–12+ tháng.','Hồ sơ: bản đồ quy hoạch, nhiệm vụ quy hoạch, tổng mặt bằng sơ bộ, thuyết minh chỉ tiêu.'),
'gate2':('Điều kiện: xác định thẩm quyền CTCTĐT/route chọn NĐT; NĐT có pháp lý, tài chính, kinh nghiệm.','Bước làm: phân loại thẩm quyền → lập hồ sơ đề xuất → nộp/tham gia mời quan tâm/đấu thầu → giải trình → nhận quyết định/kết quả.','Thời gian: CTCTĐT thực tế 45–120+ ngày; đấu thầu NĐT vài tháng đến hơn 1 năm tùy dự án.','Hồ sơ: đề nghị dự án, pháp lý NĐT, BCTC/cam kết tài chính, đề xuất dự án, tài liệu đất/quy hoạch.'),
'gate3':('Điều kiện: có căn cứ giao/thuê/chuyển mục đích hoặc kết quả đấu giá/đấu thầu/CTCTĐT; GPMB đủ tiến độ.','Bước làm: GPMB → nộp hồ sơ đất → xác định giá đất/tiền đất → nộp nghĩa vụ tài chính → đăng ký đất/GCN.','Thời gian: thủ tục đất và tiền đất thường 1–6+ tháng; GPMB có thể 6–24+ tháng.','Hồ sơ: CTCTĐT/kết quả chọn NĐT, hồ sơ GPMB, hồ sơ giao/thuê/chuyển mục đích, tờ khai tài chính, hồ sơ GCN.'),
'gate4':('Điều kiện: đất/quy hoạch/chủ trương đủ để thiết kế; xác định nghĩa vụ GPXD, ĐTM/GPMT, PCCC, đấu nối.','Bước làm: lập-thẩm định thiết kế → xin GPXD/miễn GPXD → làm ĐTM/GPMT → thẩm duyệt PCCC → thỏa thuận đấu nối.','Thời gian: GPXD thường 20–30 ngày làm việc nếu đủ hồ sơ; ĐTM/GPMT/PCCC thường 30–90+ ngày.','Hồ sơ: thiết kế, hồ sơ GPXD, ĐTM/GPMT, PCCC, văn bản đấu nối hạ tầng.'),
'gate5':('Điều kiện: đủ điều kiện khởi công; nhà thầu/tư vấn đủ năng lực; hồ sơ thiết kế/GPXD/PCCC/môi trường theo giai đoạn.','Bước làm: khởi công → thi công/quản lý chất lượng → nghiệm thu móng/hạ tầng/giai đoạn → hoàn công/nghiệm thu hoàn thành.','Thời gian: theo tiến độ dự án; nhà cao tầng thường 18–36+ tháng thi công.','Hồ sơ: thông báo khởi công, nhật ký/hồ sơ chất lượng, biên bản nghiệm thu, hoàn công, chứng nhận chuyên ngành.'),
'gate6':('Điều kiện huy động vốn/mở bán: có QSDĐ; hồ sơ dự án; thiết kế/GPXD; nghiệm thu mốc móng/hạ tầng theo loại SP; công khai thông tin; bảo lãnh NH cho nhà ở HTTTL nếu thuộc diện.','Bước làm: rà bộ pháp lý bán hàng → nghiệm thu mốc bắt buộc → làm bảo lãnh NH → công khai thông tin/HĐ mẫu → thông báo/xác nhận đủ điều kiện nếu cần → ký HĐ và thu tiền đúng tiến độ.','Thời gian: chuẩn bị hồ sơ bán hàng 2–6 tuần nếu nền pháp lý đủ; thông báo/xác nhận thường khoảng 15 ngày làm việc tùy địa phương; bảo lãnh NH 2–8 tuần.','Hồ sơ: QSDĐ, CTCTĐT, QHCT, thiết kế/GPXD, nghiệm thu móng/hạ tầng, bảo lãnh NH, thông tin công khai, HĐ mẫu.'),
'gate7':('Điều kiện: công trình nghiệm thu đưa vào sử dụng; PCCC/môi trường/hạ tầng hoàn tất; nghĩa vụ tài chính và hồ sơ đất không cản trở cấp GCN.','Bước làm: nghiệm thu hoàn thành → bàn giao SP/hạ tầng → lập hồ sơ cấp GCN → vận hành/quỹ bảo trì/ban quản trị nếu có.','Thời gian: bàn giao theo HĐ sau nghiệm thu; cấp GCN thực tế 30–90+ ngày nếu hồ sơ đủ, lâu hơn nếu vướng tiền đất/hoàn công.','Hồ sơ: nghiệm thu hoàn thành, hoàn công, PCCC/môi trường, HĐ mua bán-bàn giao, hồ sơ cấp GCN, hồ sơ vận hành.')
}
for s in data.get('steps',[]):
    d=DETAIL.get(s.get('id'))
    if d:
        s['detail_conditions']=[d[0]]; s['detail_steps']=[d[1]]; s['detail_timeline']=[d[2]]; s['detail_dossier']=[d[3]]
js.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(deploy/'bds_process_timeline_lawfaithful.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('patched direct detail')
