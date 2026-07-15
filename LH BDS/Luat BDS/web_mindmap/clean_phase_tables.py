# -*- coding: utf-8 -*-
import json, copy, re
from pathlib import Path
base=Path(__file__).resolve().parents[1]
p=base/'web_mindmap/tpre_bds_flow.json'
data=json.loads(p.read_text(encoding='utf-8'))

def detail(objective, scope, dossier, procedure, output, risks):
    return {'objective':objective,'scope':scope,'dossier':dossier,'procedure':procedure,'output':output,'risks':risks}
DETAILS={
'I':detail('Quyết định có nên theo đuổi dự án hay không; nếu theo đuổi thì chọn route pháp lý nào trước khi đặt cọc, M&A hoặc phát sinh chi phí lớn.', ['Legal DD khu đất/chủ đất/chủ dự án','Kiểm tra quy hoạch, kế hoạch sử dụng đất, kế hoạch phát triển nhà ở','Xác định route: đấu giá, đấu thầu, chấp thuận NĐT, đang có/nhận QSDĐ, M&A','Sơ bộ sản phẩm, tiền đất, GPMB, tiến độ pháp lý'], ['GCN/hồ sơ đất, bản đồ ranh, hiện trạng','Thông tin quy hoạch/kế hoạch sử dụng đất/kế hoạch nhà ở','Hồ sơ pháp lý chủ đất/chủ dự án/NĐT','Dữ liệu thị trường, sản phẩm, giá bán'], ['Lập data room','Rà đất/quy hoạch/đầu tư/nhà ở/GPMB','Chọn route pháp lý','Model sơ bộ tiền đất, GPMB, chi phí pháp lý','Kết luận go/no-go và điều kiện tiên quyết'], ['Pre-FS report','Legal DD report','Route matrix','Risk register','Điều kiện tiên quyết trước đặt cọc/M&A'], ['Đặt cọc khi chưa rõ route đất/đầu tư','Không phát hiện đất công/xen kẹt/quy hoạch treo','Model thiếu tiền đất/GPMB/ký quỹ']),
'II':detail('Tạo đất sạch hoặc hồ sơ thu mua/M&A đủ chắc để chuyển sang giao đất, thuê đất, chuyển mục đích, thi công và cấp GCN dự án.', ['Thu hồi đất, kiểm đếm, bồi thường, hỗ trợ, tái định cư','Tự thỏa thuận nhận QSDĐ/thu mua/M&A nếu route cho phép','Xử lý đất công, đất xen kẹt, hạ tầng hiện hữu','Chỉnh lý hồ sơ địa chính'], ['Bản đồ ranh, danh mục thửa/chủ sử dụng','Hồ sơ GCN, hiện trạng tài sản','Phương án bồi thường, hỗ trợ, TĐC','Biên bản kiểm đếm, chi trả, bàn giao'], ['Khóa ranh và danh sách chủ sử dụng','Phân loại đất theo cơ chế xử lý','Lập kế hoạch kiểm đếm/bồi thường/chi trả','Theo dõi khiếu nại, tái định cư','Chốt xác nhận hoàn thành GPMB'], ['Phương án BTHTTĐC được duyệt','Biên bản chi trả/bàn giao mặt bằng','Hồ sơ đất sạch/nhận QSDĐ','Căn cứ nộp hồ sơ đất'], ['GPMB kéo dài do khiếu nại','Thiếu vốn bồi thường/TĐC','Đất công/xen kẹt chưa xử lý','Chênh ranh thực tế và quy hoạch']),
'III':detail('Xác lập đúng tư cách nhà đầu tư/chủ đầu tư và cơ sở pháp lý đầu tư qua route phù hợp: chấp thuận NĐT, đấu giá QSDĐ hoặc đấu thầu dự án có sử dụng đất.', ['CTCTĐT/CTNĐT','Lựa chọn route NĐT','Hồ sơ năng lực và đề xuất dự án','Công nhận/chấp thuận CĐT nếu là dự án nhà ở','Ký quỹ/bảo đảm thực hiện dự án'], ['Đề xuất dự án','Hồ sơ pháp lý và năng lực tài chính NĐT','Tài liệu đất, quy hoạch, kế hoạch nhà ở/kế hoạch sử dụng đất','Hồ sơ đấu giá hoặc đấu thầu theo route','Phương án ký quỹ'], ['Chốt route với cơ quan chuyên môn','Chuẩn bị hồ sơ đầu tư/đấu giá/đấu thầu','Thẩm định năng lực, quy mô, vốn, tiến độ','Nhận quyết định/văn bản chấp thuận hoặc kết quả lựa chọn NĐT','Thực hiện ký quỹ và chuyển sang đất/quy hoạch/thiết kế'], ['Quyết định CTCTĐT/CTNĐT hoặc kết quả lựa chọn NĐT','Văn bản công nhận/chấp thuận CĐT nếu cần','Thỏa thuận/chứng từ ký quỹ','Cơ sở triển khai đất, QHCT, thiết kế, GPXD'], ['Chọn sai route','Năng lực tài chính không đạt','Nội dung CTCTĐT không khớp QHCT/model kinh doanh','Không dự trù ký quỹ']),
'IV':detail('Khóa QHCT/TMB làm xương sống cho thiết kế, đất, nghĩa vụ tài chính, GPXD, bán hàng và cấp GCN.', ['Nhiệm vụ QHCT/TMB','Đồ án QHCT 1/500 hoặc tổng mặt bằng','Quy định quản lý xây dựng','Lấy ý kiến/thẩm định/phê duyệt','Cập nhật chỉ tiêu quy hoạch'], ['Quy hoạch cấp trên','Bản đồ hiện trạng, cao độ, ranh, hạ tầng','Design/product brief','Hồ sơ lấy ý kiến, thẩm định, trình duyệt'], ['Kiểm tra phù hợp quy hoạch cấp trên','Lập nhiệm vụ và thiết kế ý tưởng','Lập đồ án, lấy ý kiến, giải trình','Thẩm định, phê duyệt','Cập nhật chỉ tiêu sang thiết kế, đất, tài chính, bán hàng'], ['Quyết định phê duyệt QHCT/TMB','Quy định quản lý xây dựng','Bản vẽ ranh/chỉ tiêu/cơ cấu đất/hạ tầng'], ['Chỉ tiêu quy hoạch không khớp sản phẩm','Không đủ HTXH/bãi xe/giao thông/PCCC','QHCT lệch ranh đất','Điều chỉnh QHCT sau khi đã tính giá đất']),
'V':detail('Chuyển cơ sở đầu tư/quy hoạch thành quyền sử dụng đất dự án hợp pháp, hoàn tất nghĩa vụ tài chính và cấp GCN QSDĐ dự án.', ['Giao đất, thuê đất, chuyển mục đích','Xác định giá đất, tiền sử dụng đất/tiền thuê đất','Hoàn thành nghĩa vụ tài chính','Đăng ký đất đai/cấp GCN dự án'], ['QHCT/TMB, CTCTĐT/CTNĐT/CĐT','Bản đồ địa chính/HTVT, cắm mốc, bàn giao ranh','Hồ sơ GPMB/đất sạch/nhận QSDĐ','Hồ sơ xác định giá đất','Chứng từ nộp tiền và hồ sơ cấp GCN'], ['Nộp hồ sơ giao/thuê/chuyển mục đích','Thẩm định điều kiện đất, ranh, quy hoạch, GPMB','Ban hành quyết định đất','Xác định giá đất và thông báo nghĩa vụ tài chính','Nộp tiền, đăng ký/cấp GCN'], ['QĐ giao đất/thuê đất/chuyển mục đích','Quyết định/phê duyệt giá đất hoặc thông báo nghĩa vụ tài chính','Xác nhận hoàn thành nghĩa vụ tài chính','GCN QSDĐ dự án'], ['Giá đất kéo dài','Sai diện tích/ranh','Chưa hoàn tất GPMB','Điều chỉnh QHCT làm phát sinh tiền đất bổ sung']),
'VI':detail('Hoàn thành nhóm thủ tục kỹ thuật để đủ điều kiện khởi công, thi công, nghiệm thu, mở bán và đưa công trình vào sử dụng.', ['Khảo sát, TKCS/BCNCKT, TKKT/TKBVTC','ĐTM/GPMT','PCCC','Đấu nối giao thông, điện, nước, thoát nước, XLNT','GPXD và thông báo khởi công'], ['QHCT/TMB, ranh đất, chỉ tiêu quy hoạch','Hồ sơ khảo sát','Bộ thiết kế kiến trúc/kết cấu/MEP/PCCC/môi trường','Hồ sơ thẩm tra/thẩm định','Văn bản đấu nối, PCCC, môi trường, GPXD'], ['Chạy song song thiết kế, PCCC, môi trường, đấu nối','Thẩm định thiết kế','Hoàn thiện ĐTM/GPMT và PCCC','Xin GPXD hoặc xác định miễn GPXD','Thông báo khởi công'], ['Văn bản thẩm định thiết kế','ĐTM/GPMT','Văn bản thẩm duyệt PCCC, thỏa thuận đấu nối','GPXD/thông báo khởi công'], ['PCCC/môi trường làm muộn phải sửa thiết kế','Thiết kế không khớp QHCT/ranh','Đấu nối không đủ công suất','GPXD chậm']),
'VII':detail('Thi công đúng pháp lý, thiết kế, GPXD và tạo đủ hồ sơ chất lượng/nghiệm thu giai đoạn.', ['San nền, HTKT, phần móng, phần thân, hoàn thiện','Quản lý thay đổi thiết kế/GPXD','Hồ sơ chất lượng, nhật ký, thí nghiệm, hoàn công','An toàn lao động, môi trường thi công','Nghiệm thu giai đoạn/mốc bán hàng'], ['GPXD/TKBVTC và điều kiện khởi công','Hợp đồng nhà thầu, tư vấn giám sát','Nhật ký, biên bản nghiệm thu, kết quả thí nghiệm','Bản vẽ hoàn công','Hồ sơ ATLĐ, môi trường, PCCC công trường'], ['Bàn giao mặt bằng, mốc ranh, hồ sơ thiết kế','Thi công theo phân kỳ','Nghiệm thu công việc/giai đoạn','Xác nhận mốc móng/HTKT nếu cần mở bán','Chuẩn bị hồ sơ hoàn công'], ['Hồ sơ nghiệm thu giai đoạn','Biên bản nghiệm thu mốc móng/HTKT','Bản vẽ hoàn công và hồ sơ chất lượng'], ['Thi công sai GPXD/QHCT','Hồ sơ chất lượng thiếu','Tai nạn lao động/sự cố công trình','Thay đổi thiết kế không cập nhật pháp lý']),
'VIII':detail('Mở bán/huy động vốn đúng điều kiện pháp luật, kiểm soát thông tin bán hàng, hợp đồng, bảo lãnh và tiến độ thanh toán.', ['Điều kiện bán BĐS/nhà ở HTTTL','Thông báo đủ điều kiện bán/cho thuê mua','Bảo lãnh ngân hàng','Hợp đồng mẫu, chính sách bán hàng, công khai thông tin','Kiểm soát booking/giữ chỗ/đặt cọc'], ['Pháp lý dự án: đầu tư, quy hoạch, đất, GPXD','Nghiệm thu móng/HTKT','Bảo lãnh/chứng thư bảo lãnh','Mẫu HĐMB/phụ lục/chính sách thanh toán','Thông tin công khai dự án/sản phẩm'], ['Rà điều kiện bán theo loại sản phẩm','Hoàn thiện bảo lãnh, hợp đồng mẫu, công khai thông tin','Nộp/thực hiện thông báo đủ điều kiện bán','Đào tạo sales script','Theo dõi ký HĐMB, thanh toán, bảo lãnh, giải chấp'], ['Văn bản/thông báo đủ điều kiện bán','Bộ pháp lý bán hàng','HĐMB/phụ lục hợp lệ','Bảo lãnh/chứng thư nếu thuộc diện'], ['Booking/đặt cọc thành huy động vốn trái luật','Sales nói quá trạng thái pháp lý','Thiếu bảo lãnh/giải chấp','HĐMB mẫu có điều khoản rủi ro']),
'IX':detail('Xác nhận công trình/hạng mục đủ điều kiện đưa vào sử dụng, làm nền bàn giao, vận hành và cấp GCN cho khách hàng.', ['Nghiệm thu CĐT-nhà thầu-tư vấn','Nghiệm thu PCCC, môi trường, đấu nối','Kiểm tra công tác nghiệm thu của CQNN nếu thuộc diện','Hồ sơ hoàn công, chất lượng','Xử lý tồn tại trước bàn giao'], ['Bản vẽ hoàn công, nhật ký, biên bản nghiệm thu','Kết quả thí nghiệm/kiểm định','Văn bản nghiệm thu PCCC, GPMT/vận hành thử, đấu nối','Báo cáo hoàn thành','Danh mục tồn tại'], ['Tổng rà hồ sơ chất lượng và hoàn công','Nghiệm thu nội bộ','Hoàn tất PCCC, môi trường, đấu nối','Nộp hồ sơ kiểm tra nghiệm thu CQNN nếu thuộc diện','Nhận văn bản chấp thuận nghiệm thu/đủ điều kiện sử dụng'], ['Biên bản nghiệm thu hoàn thành','Văn bản kiểm tra/chấp thuận nghiệm thu nếu có','Hồ sơ hoàn công hoàn chỉnh','Điều kiện bàn giao, vận hành, cấp GCN'], ['Thiếu PCCC/GPMT/đấu nối','Hồ sơ hoàn công không khớp thực tế','Tồn tại hiện trường chưa đóng','Bàn giao khi chưa đủ điều kiện sử dụng']),
'X':detail('Bàn giao sản phẩm/hạ tầng đúng pháp luật và hoàn tất hồ sơ cấp GCN cho khách hàng/người mua.', ['Bàn giao nhà/căn hộ/sản phẩm','Bàn giao HTKT/HTXH nếu có','Hồ sơ cấp GCN người mua','Giải chấp, nghĩa vụ tài chính, hoàn công','Xử lý sai lệch diện tích, phần chung-riêng, bảo hành'], ['HĐMB, phụ lục, chứng từ thanh toán','Biên bản bàn giao, danh mục tồn tại, bảo hành','Bản vẽ sơ đồ nhà đất/phân lô, hoàn công','Xác nhận nghĩa vụ tài chính, giải chấp','Hồ sơ khách hàng'], ['Chuẩn bị checklist bàn giao','Đối chiếu diện tích, hoàn công, pháp lý, thanh toán','Ký biên bản bàn giao','Lập/nộp hồ sơ cấp GCN khách hàng','Theo dõi bổ sung hồ sơ, nhận và bàn giao GCN'], ['Biên bản bàn giao sản phẩm','Hồ sơ cấp GCN hoàn chỉnh','GCN cho khách hàng','Biên bản bàn giao hạ tầng nếu có'], ['Chậm cấp GCN do tài chính/giải chấp','Sai lệch diện tích/hồ sơ hoàn công','Tranh chấp phần chung-riêng','Bàn giao hạ tầng không được tiếp nhận']),
'XI':detail('Quản trị nghĩa vụ sau bàn giao: vận hành, bảo hành, hậu kiểm, xử lý khiếu nại và lưu trữ hồ sơ pháp lý dự án.', ['Bảo hành công trình/sản phẩm','Vận hành BQL, phí dịch vụ, nội quy, tài sản chung','Hậu kiểm pháp lý, thanh tra, kiểm toán nếu có','Bàn giao tài sản/hạ tầng còn lại','Lưu trữ data room pháp lý'], ['Hồ sơ hoàn công/nghiệm thu/cấp GCN','Danh mục tài sản, thiết bị, hồ sơ vận hành','Hợp đồng bảo hành/bảo trì','Sổ bảo hành khách hàng, ticket khiếu nại','Biên bản bàn giao tài sản/hạ tầng/BQL'], ['Thiết lập quy trình tiếp nhận lỗi/bảo hành/khiếu nại','Theo dõi SLA nhà thầu','Bàn giao vận hành cho BQL/đơn vị quản lý/cơ quan','Chuẩn bị hồ sơ hậu kiểm','Đóng data room dự án'], ['Hồ sơ bảo hành/vận hành','Biên bản xử lý tồn tại/khiếu nại','Biên bản bàn giao tài sản/hạ tầng/BQL','Kho hồ sơ pháp lý hoàn chỉnh'], ['Không phân định lỗi bảo hành/vận hành','Thiếu hồ sơ thiết bị/tài sản','Khiếu nại kéo dài','Bàn giao tài sản công/hạ tầng không xong'])
}

def prefix(ph): return ph['id'].split('.')[0]
def has_bad(txt): return any(x in txt for x in ['??','Lu?t ','N? ','?i?u','Quy?t','M?c ti'])
def law_id(l):
    doc=l.get('doc','').lower()
    art=l.get('article','').lower()
    if 'đấu thầu' in doc or '115/2024' in doc: return 'tender'
    if 'đấu giá' in doc: return 'auction'
    if '102/2024' in doc: return 'nd102'
    if '103/2024' in doc: return 'nd103'
    if 'đất đai' in doc: return 'land'
    if 'đầu tư' in doc: return 'investment'
    return doc+'|'+art
for ph in data['phases']:
    pref=prefix(ph)
    det=copy.deepcopy(DETAILS[pref])
    ph['phase_detail']=det
    for it in ph.get('items',[]):
        it['phase_detail']=copy.deepcopy(det)
        it['implementation_scope']=det['scope']
        it['procedure_steps']=det['procedure']
        it['risk_register']=det['risks']
        new=[]; seen=set()
        for l in it.get('legal_basis',[]):
            txt=json.dumps(l,ensure_ascii=False)
            if has_bad(txt): continue
            lid=law_id(l)
            # put route-specific laws in correct table
            if ph['id']=='III.2' and lid=='tender': continue
            if ph['id']=='III.3' and lid=='auction': continue
            if ph['id']=='III.1' and lid in {'auction','tender'}: continue
            if lid in seen: continue
            new.append(l); seen.add(lid)
        it['legal_basis']=new
    for n in ph.get('subnodes',[]):
        n['parent_phase_detail']=copy.deepcopy(det)
        if n.get('phase_id','').split('.')[0] != pref:
            n['phase_id']=pref

data['table_audit']='deduped_phase_tables_utf8_v1'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for out in [base/'FINAL_BDS_LEGAL_WEB/tpre_bds_flow.json', Path('deploy_bds_legal_process/public/bds-legal-process/tpre_bds_flow.json')]:
    if out.exists(): out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('cleaned phase tables')
