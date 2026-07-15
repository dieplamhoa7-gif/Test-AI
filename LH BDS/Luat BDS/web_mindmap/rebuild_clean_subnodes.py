# -*- coding: utf-8 -*-
import json, copy
from pathlib import Path
base=Path(__file__).resolve().parents[1]
p=base/'web_mindmap/tpre_bds_flow.json'
data=json.loads(p.read_text(encoding='utf-8'))
NOTE='Timeline gồm hai lớp: mốc theo quy định pháp luật/TTHC tính từ hồ sơ hợp lệ và mốc thực tế quản trị dự án phụ thuộc độ sạch hồ sơ, thẩm quyền, phối hợp cơ quan và phản hồi thị trường/dân cư.'

def node(code,title,phase_id,owner,summary,inputs,outputs,deps,risks):
    return {'code':code,'title':title,'phase_id':phase_id,'owner':owner,'summary':summary,'inputs':inputs,'outputs':outputs,'dependencies':deps,'implementation_risks':risks,'statutory_timeline':[],'legal_basis':[],'legal_timeline_note':NOTE}
clean={
'III.1':[
 node('III-I.1','Hồ sơ năng lực NĐT / pháp lý đất đai đầu vào','III.1','Đầu tư pháp lý + Tài chính + GPMB','Node đầu vào để chọn đúng route lựa chọn nhà đầu tư: chấp thuận NĐT, đấu giá QSDĐ, đấu thầu dự án có sử dụng đất, hoặc tự có/thỏa thuận nhận QSDĐ.',['Hồ sơ pháp lý nhà đầu tư, đăng ký doanh nghiệp, ngành nghề, người đại diện.','Báo cáo tài chính, xác nhận vốn chủ sở hữu, phương án huy động vốn/tín dụng.','Hồ sơ khu đất: GCN, bản đồ ranh, hiện trạng, loại đất, nguồn gốc đất, phần đất công/xen kẹt nếu có.','Thông tin quy hoạch, kế hoạch sử dụng đất, chương trình/kế hoạch phát triển nhà ở nếu là dự án nhà ở.','Ma trận lựa chọn route: đấu giá, đấu thầu, CTNĐT, đang có/nhận QSDĐ.'],['Bộ DD pháp lý nhà đầu tư và khu đất.','Kết luận route lựa chọn NĐT/tiếp cận đất.','Danh mục điều kiện phải bổ sung trước khi nộp CTCTĐT/CTNĐT hoặc hồ sơ đấu thầu/đấu giá.'],['Pre-FS/Product brief','Thông tin quy hoạch cấp trên','Kết quả DD đất và tài chính'],['Nhầm điều kiện chấp thuận NĐT với điều kiện giao đất.','Đánh giá thiếu đất công/xen kẹt hoặc nghĩa vụ đấu giá/đấu thầu.']),
 node('III-O.1','CTCTĐT / CTNĐT / công nhận CĐT / ký quỹ','III.1','Đầu tư pháp lý','Mốc pháp lý xác lập chủ trương, nhà đầu tư/chủ đầu tư và nghĩa vụ bảo đảm thực hiện dự án; là nền cho đất, quy hoạch, thiết kế, GPXD và bán hàng.',['Bộ hồ sơ từ III-I.1.','Đề xuất dự án: mục tiêu, địa điểm, quy mô, vốn, tiến độ, nhu cầu sử dụng đất.','Tài liệu chứng minh năng lực tài chính và kinh nghiệm.','Phương án ký quỹ/bảo đảm thực hiện dự án.','Văn bản/quyết định lựa chọn NĐT nếu đi theo đấu giá/đấu thầu.'],['Quyết định CTCTĐT hoặc văn bản chấp thuận NĐT.','Văn bản công nhận/chấp thuận CĐT dự án nhà ở nếu thuộc diện.','Thỏa thuận/chứng từ ký quỹ hoặc bảo đảm thực hiện dự án.','Căn cứ triển khai giao đất/thuê đất/chuyển mục đích và các thủ tục kỹ thuật tiếp theo.'],['Hoàn tất route lựa chọn NĐT','Có cơ sở quy hoạch/đất tối thiểu','Năng lực tài chính đã chứng minh'],['Chỉ tiêu dự án trong CTCTĐT lệch QHCT.','Không tính nghĩa vụ ký quỹ trong dòng tiền.','Thiếu căn cứ công nhận CĐT cho dự án nhà ở.'])],
'V':[node('V-I.1','Bản đồ HTVT, cắm mốc, bàn giao ranh và hồ sơ đất đầu vào','V','GPMB + Pháp lý đất + Kỹ thuật','Node đầu vào cho quyết định giao/thuê đất, chuyển mục đích, định giá đất và cấp GCN dự án; cần khóa ranh, diện tích, hiện trạng và hồ sơ địa chính.',['Bản đồ hiện trạng vị trí, trích đo/trích lục địa chính, ranh mốc ngoài thực địa.','Biên bản cắm mốc, bàn giao ranh, hồ sơ GPMB/bồi thường hoặc thỏa thuận nhận QSDĐ.','QHCT/Tổng mặt bằng được duyệt và chỉ tiêu sử dụng đất.','Quyết định CTCTĐT/CTNĐT/CĐT và hồ sơ dự án.','Danh mục thửa đất, loại đất, nguồn gốc, tình trạng pháp lý, tranh chấp/thế chấp nếu có.'],['Bộ hồ sơ địa chính đủ nộp thủ tục giao/thuê/chuyển mục đích.','Diện tích/ranh pháp lý dùng cho xác định giá đất và nghĩa vụ tài chính.','Danh sách vấn đề cần xử lý: chênh diện tích, đất xen kẹt, đất công, tranh chấp, cập nhật biến động.'],['CTCTĐT/CTNĐT hoặc căn cứ lựa chọn NĐT','QHCT/Tổng mặt bằng','GPMB hoặc hồ sơ nhận QSDĐ'],['Chênh diện tích giữa bản đồ, QHCT và GCN.','Đất công/xen kẹt chưa xử lý.','Chưa hoàn tất GPMB nhưng đã model như đất sạch.'])],
'VIII':[node('VIII-I.1','Mẫu HĐMB, bảo lãnh, nghiệm thu mốc và hồ sơ mở bán','VIII','Kinh doanh + Pháp chế + Tài chính','Node đầu vào để xin/thực hiện thông báo đủ điều kiện bán BĐS hình thành trong tương lai và kiểm soát booking, đặt cọc, HĐMB đúng pháp luật.',['Hồ sơ pháp lý dự án: CTCTĐT/CTNĐT, QHCT, đất/GCN/QĐ đất, GPXD nếu thuộc diện.','Biên bản nghiệm thu phần móng hoặc HTKT theo loại sản phẩm.','Mẫu HĐMB/HĐ thuê mua, chính sách bán hàng, tiến độ thanh toán.','Thông tin công khai dự án/sản phẩm: pháp lý, tiến độ, thế chấp/giải chấp, hạn chế chuyển nhượng nếu có.','Cam kết/chứng thư bảo lãnh ngân hàng cho nhà ở HTTTL nếu thuộc diện.'],['Bộ hồ sơ mở bán đủ điều kiện.','Mẫu hợp đồng và thông tin công khai thống nhất với pháp lý dự án.','Căn cứ nộp/thực hiện thông báo đủ điều kiện bán và triển khai giao dịch.'],['GPXD/thiết kế và nghiệm thu mốc','Đất/GCN/QĐ đất','Bảo lãnh ngân hàng và hợp đồng mẫu'],['Marketing/booking trước điều kiện bán.','HĐMB mẫu mâu thuẫn pháp lý dự án.','Thiếu giải chấp/bảo lãnh khiến không đủ điều kiện giao dịch.'])]
}
for ph in data['phases']:
    ph['legal_timeline_note']=NOTE
    for it in ph.get('items',[]):
        it['legal_timeline_note']=NOTE
    if ph['id'] in clean:
        # inherit phase legal basis/timeline for subnodes to avoid duplicated wrong text
        for n in clean[ph['id']]:
            n['legal_basis']=copy.deepcopy(ph['items'][0].get('legal_basis',[]))
            n['statutory_timeline']=copy.deepcopy(ph.get('statutory_timeline',[]))
        ph['subnodes']=clean[ph['id']]
        ph['items'][0]['subnodes']=copy.deepcopy(clean[ph['id']])

data['table_audit']='deduped_phase_tables_utf8_v3'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for out in [base/'FINAL_BDS_LEGAL_WEB/tpre_bds_flow.json', Path('deploy_bds_legal_process/public/bds-legal-process/tpre_bds_flow.json')]:
    if out.exists(): out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('rebuilt clean subnodes')
