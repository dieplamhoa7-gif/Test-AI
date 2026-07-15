# -*- coding: utf-8 -*-
import json
from pathlib import Path
base=Path(__file__).resolve().parents[1]
p=base/'web_mindmap/tpre_bds_flow.json'
data=json.loads(p.read_text(encoding='utf-8'))
TIMELINES={
'I':['Theo quy định: chưa phải thủ tục hành chính độc lập; dùng để chuẩn bị trước khi nộp CTCTĐT/CTNĐT/QHCT/đất.','Thực tế: 2–6 tuần cho dự án đơn giản; 1–3 tháng nếu phải rà M&A, đất công/xen kẹt, điều chỉnh quy hoạch hoặc kế hoạch nhà ở.'],
'II':['Theo Luật Đất đai 2024: thực hiện theo trình tự thông báo thu hồi, điều tra/kiểm đếm, lập-phê duyệt phương án BTHTTĐC, chi trả và bàn giao mặt bằng.','Thực tế: 3–12 tháng nếu ít hộ và đồng thuận; 12–36 tháng+ nếu nhiều hộ, khiếu nại, tái định cư, đất công/xen kẹt hoặc vốn GPMB chậm.'],
'III':['Theo quy định đầu tư/đấu thầu/đấu giá: thời hạn xử lý phụ thuộc thẩm quyền và route; hồ sơ CTCTĐT/CTNĐT thường tính bằng chục ngày làm việc sau khi hồ sơ hợp lệ, đấu thầu/đấu giá dài hơn do công bố, mời quan tâm/mời thầu/đấu giá.','Thực tế: CTCTĐT/CTNĐT 2–6 tháng; đấu giá/đấu thầu NĐT 4–12 tháng+; route có điều chỉnh quy hoạch/kế hoạch nhà ở/đất sạch sẽ kéo dài thêm.'],
'IV':['Theo quy định quy hoạch: lập nhiệm vụ, lấy ý kiến, thẩm định, phê duyệt QHCT/TMB theo TTHC địa phương và thẩm quyền phê duyệt.','Thực tế: 2–6 tháng nếu quy hoạch cấp trên rõ; 6–12 tháng+ nếu phải điều chỉnh chỉ tiêu, đấu nối giao thông, dân số, HTXH hoặc lấy ý kiến nhiều vòng.'],
'V':['Theo Luật Đất đai 2024 và nghị định hướng dẫn: giao/thuê/chuyển mục đích, xác định giá đất, thông báo nghĩa vụ tài chính, cấp GCN là các thủ tục nối tiếp; thời hạn cụ thể theo TTHC và tính từ hồ sơ hợp lệ.','Thực tế: quyết định đất 1–3 tháng sau khi đủ hồ sơ; giá đất/nghĩa vụ tài chính 3–12 tháng+; cấp GCN dự án 1–3 tháng sau khi hoàn tất tài chính và hồ sơ địa chính sạch.'],
'VI':['Theo quy định xây dựng/môi trường/PCCC: thẩm định thiết kế, ĐTM/GPMT, PCCC, đấu nối và GPXD có thời hạn riêng theo từng TTHC sau khi hồ sơ hợp lệ.','Thực tế: 3–9 tháng nếu chạy song song; 9–18 tháng+ nếu PCCC/môi trường/đấu nối làm muộn hoặc phải sửa thiết kế.'],
'VII':['Theo quy định: thời gian thi công theo tiến độ dự án, GPXD, thiết kế và hợp đồng; nghiệm thu giai đoạn thực hiện theo quy định quản lý chất lượng.','Thực tế: HTKT/khu thấp tầng 6–18 tháng; cao tầng 18–36 tháng+; phụ thuộc vốn, nhà thầu, thời tiết, thay đổi thiết kế và điều kiện nghiệm thu mốc bán hàng.'],
'VIII':['Theo Luật KDBĐS/Luật Nhà ở: chỉ được bán/cho thuê mua BĐS HTTTL khi đủ điều kiện pháp lý, nghiệm thu mốc, bảo lãnh/công khai thông tin; thủ tục thông báo/kiểm tra theo TTHC địa phương.','Thực tế: chuẩn bị bộ mở bán 2–6 tuần nếu pháp lý sạch; 1–3 tháng+ nếu thiếu bảo lãnh, nghiệm thu mốc, giải chấp hoặc mẫu hợp đồng phải sửa.'],
'IX':['Theo quy định quản lý chất lượng/PCCC/môi trường: nghiệm thu CĐT-nhà thầu, nghiệm thu PCCC/môi trường/đấu nối, kiểm tra công tác nghiệm thu của CQNN nếu thuộc diện.','Thực tế: 1–3 tháng nếu hồ sơ hoàn công sạch; 3–9 tháng+ nếu thiếu PCCC, GPMT/vận hành thử, đấu nối hoặc tồn tại hiện trường.'],
'X':['Theo NĐ 101/2024 và pháp luật nhà ở/đất đai: cấp GCN cho người mua sau khi đủ điều kiện chuyển quyền, hoàn thành nghĩa vụ tài chính, nghiệm thu/hoàn công và hồ sơ người mua.','Thực tế: bàn giao 1–2 tháng theo từng block/phân kỳ; cấp GCN khách hàng 3–12 tháng+ tùy nghĩa vụ tài chính, giải chấp, hoàn công, sai khác diện tích và hồ sơ khách hàng.'],
'XI':['Theo hợp đồng, pháp luật xây dựng/nhà ở/dân sự: bảo hành, vận hành, xử lý tồn tại và bàn giao hạ tầng/tài sản theo thời hạn cam kết/quy định chuyên ngành.','Thực tế: bảo hành 12–60 tháng tùy hạng mục/loại công trình; hậu kiểm và bàn giao hạ tầng có thể kéo dài 6–24 tháng nếu hồ sơ tài sản, hoàn công, tiếp nhận chưa sạch.']
}
# Only keep generic III subnodes on III.1; route phases III.2/III.3 should not repeat the same subnodes.
for ph in data['phases']:
    pref=ph['id'].split('.')[0]
    tl=TIMELINES[pref]
    ph['statutory_timeline']=tl
    for it in ph.get('items',[]):
        it['statutory_timeline']=tl
        if ph['id'] in ('III.2','III.3'):
            it.pop('subnodes',None)
    if ph['id'] in ('III.2','III.3'):
        ph.pop('subnodes',None)
    for n in ph.get('subnodes',[]):
        n['phase_id']=ph['id']
        n['statutory_timeline']=tl
        # remove old mojibake inherited details; display uses parent phase detail from phase/item
        n.pop('parent_phase_detail',None)

data['table_audit']='deduped_phase_tables_utf8_v2'
data['table_audit_note']='Removed duplicated III subnodes from III.2/III.3 and rewrote statutory timelines in UTF-8.'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for out in [base/'FINAL_BDS_LEGAL_WEB/tpre_bds_flow.json', Path('deploy_bds_legal_process/public/bds-legal-process/tpre_bds_flow.json')]:
    if out.exists(): out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('fixed remaining table issues')
