# -*- coding: utf-8 -*-
import json, copy, re
from pathlib import Path
base = Path(__file__).resolve().parents[1]
p = base / 'web_mindmap' / 'tpre_bds_flow.json'
data = json.loads(p.read_text(encoding='utf-8'))

def law(doc, article, source, applies='', conditions='', dossier='', authority='', output='', notes=''):
    pts=[]
    for label,val in [('Áp dụng trong flow',applies),('Điều kiện/checkpoint',conditions),('Hồ sơ/dữ liệu cần chuẩn bị',dossier),('Cơ quan/thẩm quyền thường gặp',authority),('Output pháp lý',output),('Lưu ý thực hiện',notes)]:
        if val: pts.append(f'{label}: {val}')
    return {'doc':doc,'article':article,'source_file':source,'points':pts}

# canonical extra laws by phase prefix, written in UTF-8 to avoid PowerShell mojibake
EXTRA = {
'I': [
 law('Luật Nhà ở 2023','Điều 31, 32, 33; chương trình/kế hoạch phát triển nhà ở','27_2023_qh15_530121_full.md','Rà tính phù hợp của dự án nhà ở/khu đô thị với chương trình, kế hoạch phát triển nhà ở địa phương ngay từ Pre-FS.','Dự án nhà ở thương mại phải phù hợp quy hoạch, chương trình/kế hoạch phát triển nhà ở và điều kiện về đất ở/đất được phép chuyển mục đích.','Văn bản kế hoạch phát triển nhà ở, chỉ tiêu dân số, cơ cấu sản phẩm, thông tin nhà ở xã hội nếu có.','UBND cấp tỉnh, Sở Xây dựng.','Kết luận dự án có đủ nền pháp lý nhà ở để đưa vào CTCTĐT/QHCT hay cần cập nhật/bổ sung.','Nếu bỏ qua kế hoạch nhà ở, hồ sơ đầu tư/quy hoạch có thể bị trả hoặc phải điều chỉnh.'),
 law('Luật Quy hoạch đô thị và nông thôn 2024','Nhóm quy định hệ thống quy hoạch và quy hoạch chi tiết','47_2024_qh15_583645_full.md','Kiểm tra quy hoạch cấp trên, chỉ tiêu sử dụng đất, chức năng đất, hạ tầng và yêu cầu lập QHCT/TMB.','Ý tưởng dự án phải phù hợp định hướng quy hoạch cấp trên; nếu chưa phù hợp phải tính thủ tục điều chỉnh quy hoạch.','Bản đồ quy hoạch, chỉ tiêu quy hoạch, văn bản cung cấp thông tin quy hoạch, hồ sơ hiện trạng.','Sở Xây dựng/Sở QHKT, UBND có thẩm quyền.','Kết luận quy hoạch đầu vào và điều kiện lập QHCT/TMB.','Quy hoạch là điều kiện nền cho đất, thiết kế, GPXD, bán hàng và cấp sổ.')],
'II': [law('Luật Đất đai 2024','Điều 78-91; bồi thường, hỗ trợ, tái định cư','31_2024_qh15_523642_full.md','Bổ sung căn cứ riêng cho thu hồi đất, kiểm đếm, phương án bồi thường, hỗ trợ, tái định cư.','Có căn cứ thu hồi đất; phương án BTHTTĐC đúng đối tượng, loại đất, tài sản, chính sách tái định cư.','Thông báo thu hồi, hồ sơ kiểm đếm, phương án bồi thường, hồ sơ TĐC, biên bản chi trả/bàn giao.','UBND cấp có thẩm quyền, tổ chức làm nhiệm vụ bồi thường GPMB, cơ quan TNMT.','Phương án BTHTTĐC phê duyệt, biên bản bàn giao mặt bằng, xác nhận hoàn thành GPMB.','GPMB là timeline thực tế khó nhất; pháp luật có mốc thủ tục nhưng thực tế phụ thuộc đồng thuận/khiếu nại.')],
'III': [
 law('Luật Đấu thầu 2023 và NĐ 115/2024/NĐ-CP','Lựa chọn NĐT dự án có sử dụng đất','22_2023_qh15_526686_full.md;115_2024_nd-cp_614098_full.md','Áp dụng khi dự án phải lựa chọn nhà đầu tư thông qua đấu thầu dự án có sử dụng đất.','Dự án thuộc danh mục/đủ điều kiện đấu thầu; có yêu cầu sơ bộ năng lực, kinh nghiệm; hồ sơ mời thầu và tiêu chí đánh giá hợp lệ.','Danh mục dự án, hồ sơ mời quan tâm/mời thầu, yêu cầu năng lực, phương án sơ bộ dự án, đất/quy hoạch.','Bên mời thầu, cơ quan chuyên môn, UBND cấp tỉnh/cơ quan có thẩm quyền.','Quyết định phê duyệt kết quả lựa chọn NĐT, hợp đồng dự án nếu có.','Nếu thuộc diện đấu thầu mà đi thẳng CTNĐT/chấp thuận NĐT sẽ rủi ro tính hợp pháp route.'),
 law('Luật Đấu giá tài sản 2016 sửa đổi 2024','Đấu giá quyền sử dụng đất','01_2016_qh14_12902_full.md;37_2024_qh15_585018_full.md','Áp dụng cho route đấu giá QSDĐ khi Nhà nước giao/cho thuê đất qua đấu giá.','Khu đất đủ điều kiện đấu giá, có quy hoạch, phương án đấu giá, giá khởi điểm, hồ sơ đất sạch theo yêu cầu.','Phương án đấu giá, quyết định đấu giá, thông tin khu đất, hồ sơ tham gia, chứng từ đặt trước.','UBND/cơ quan TNMT, tổ chức đấu giá tài sản, hội đồng đấu giá nếu có.','Biên bản/kết quả trúng đấu giá, quyết định công nhận kết quả.','Timeline đấu giá phụ thuộc chuẩn bị đất sạch và phê duyệt giá khởi điểm.')],
'IV': [law('Luật Kiến trúc 2019','Thi tuyển phương án kiến trúc, quản lý kiến trúc','40_2019_qh14_387023_full.md','Kiểm tra công trình/dự án có thuộc diện thi tuyển phương án kiến trúc hoặc chịu quy chế quản lý kiến trúc không.','Dự án ở khu vực có yêu cầu quản lý kiến trúc, công trình điểm nhấn/cấp đặc biệt/cấp I hoặc trường hợp địa phương yêu cầu.','Quy chế quản lý kiến trúc, nhiệm vụ thiết kế, hồ sơ thi tuyển nếu thuộc diện.','Cơ quan quản lý kiến trúc/quy hoạch, hội đồng thi tuyển, UBND/cơ quan được phân cấp.','Phương án kiến trúc được lựa chọn hoặc xác nhận không thuộc diện thi tuyển.','Cần chốt trước khi khóa concept/QHCT để tránh sửa thiết kế.')],
'V': [
 law('NĐ 71/2024/NĐ-CP về giá đất','Xác định giá đất cụ thể','71_2024_nd-cp_607252_full.md','Bổ sung cơ sở xác định giá đất cụ thể, phương pháp định giá và trình tự thẩm định giá đất.','Có quyết định đất/chuyển mục đích/điều chỉnh quy hoạch làm phát sinh nghĩa vụ tài chính; dữ liệu thị trường và phương pháp định giá phù hợp.','Hồ sơ giá đất, chứng thư tư vấn nếu có, dữ liệu so sánh, phương án tài chính, QHCT, diện tích tính tiền.','Sở TNMT/Sở Tài chính, hội đồng thẩm định giá đất, UBND cấp tỉnh, cơ quan thuế.','Quyết định/phê duyệt giá đất cụ thể, thông báo nghĩa vụ tài chính.','Đây thường là đường găng dòng tiền; cần model sensitivity giá đất.'),
 law('NĐ 101/2024/NĐ-CP','Đăng ký đất đai, cấp GCN dự án','101_2024_nd-cp_613131_full.md','Áp dụng khi đăng ký biến động, cấp GCN QSDĐ dự án sau giao/thuê/chuyển mục đích và hoàn thành nghĩa vụ tài chính.','Hoàn thành nghĩa vụ tài chính, hồ sơ đất/ranh/diện tích thống nhất, không vướng tranh chấp/thế chấp trái điều kiện.','Đơn đăng ký, quyết định đất, chứng từ tài chính, bản đồ, hồ sơ pháp lý dự án.','VPĐK đất đai, Sở TNMT, UBND có thẩm quyền.','GCN QSDĐ dự án hoặc xác nhận biến động.','GCN dự án là căn cứ quan trọng cho thế chấp, bán hàng, cấp sổ khách hàng.')],
'VI': [
 law('Luật Tài nguyên nước 2023','Khai thác, sử dụng nước; xả nước thải; bảo vệ nguồn nước','28_2023_qh15_531341_full.md','Kiểm tra thủ tục liên quan nguồn cấp nước, thoát nước, xả thải, hồ điều hòa, khai thác nước dưới đất/nước mặt nếu có.','Dự án có công trình khai thác nước/xả thải hoặc tác động nguồn nước phải có giấy phép/xác nhận tương ứng.','Hồ sơ đấu nối cấp thoát nước, phương án xả thải, thiết kế XLNT, thông số nguồn tiếp nhận.','Cơ quan tài nguyên nước/môi trường, đơn vị cấp thoát nước địa phương.','Văn bản/giấy phép/thỏa thuận liên quan tài nguyên nước và đấu nối thoát nước.','Thường liên thông với GPMT và nghiệm thu vận hành trạm XLNT.'),
 law('Luật Điện lực và văn bản hướng dẫn','Đấu nối điện, trạm biến áp, cấp điện dự án','28_2004_qh11_15_full.md','Bổ sung cơ sở làm việc với đơn vị điện lực về thỏa thuận đấu nối, công suất, trạm biến áp và nghiệm thu điện.','Nhu cầu phụ tải, vị trí đấu nối, phương án cấp điện và hành lang an toàn điện phải phù hợp.','Hồ sơ nhu cầu công suất, thiết kế cấp điện, thỏa thuận đấu nối, hồ sơ trạm biến áp.','Đơn vị điện lực, cơ quan quản lý năng lượng/xây dựng khi liên quan.','Thỏa thuận đấu nối/cấp điện, nghiệm thu đóng điện.','Chậm điện ảnh hưởng nghiệm thu vận hành, bàn giao và kinh doanh.')],
'VII': [law('Luật An toàn, vệ sinh lao động 2015','An toàn lao động trên công trường','84_2015_qh13_4958_full.md','Quản trị an toàn thi công, thiết bị có yêu cầu nghiêm ngặt, đào tạo và xử lý tai nạn lao động.','Nhà thầu phải có biện pháp ATLĐ, huấn luyện, kiểm định thiết bị, bảo hộ và phương án ứng cứu.','Kế hoạch ATLĐ, hồ sơ huấn luyện, kiểm định thiết bị, nhật ký an toàn, biên bản sự cố nếu có.','Chủ đầu tư, nhà thầu, tư vấn giám sát, cơ quan lao động/thanh tra khi có sự cố.','Hồ sơ an toàn công trường và điều kiện thi công hợp pháp.','Tai nạn nghiêm trọng có thể dừng thi công, ảnh hưởng nghiệm thu và pháp lý dự án.')],
'VIII': [
 law('Luật Nhà ở 2023','Bán/cho thuê mua nhà ở hình thành trong tương lai; bảo lãnh; bàn giao','27_2023_qh15_530121_full.md','Bổ sung căn cứ riêng cho nhà ở bên cạnh Luật KDBĐS: điều kiện giao dịch, bảo lãnh, bàn giao và quyền người mua.','Dự án nhà ở đủ điều kiện pháp lý, nghiệm thu mốc, bảo lãnh, công khai thông tin và hợp đồng đúng mẫu/đúng nội dung bắt buộc.','Hồ sơ nhà ở, nghiệm thu móng/HTKT, bảo lãnh, HĐMB, thông tin công khai.','Sở Xây dựng, ngân hàng bảo lãnh, chủ đầu tư.','Bộ hồ sơ bán nhà ở HTTTL hợp lệ.','Luật KDBĐS xử giao dịch BĐS, Luật Nhà ở xử nghĩa vụ nhà ở/chủ đầu tư/người mua; phải dùng cả hai.'),
 law('Luật Bảo vệ quyền lợi người tiêu dùng 2023','Thông tin, hợp đồng theo mẫu, điều khoản giao dịch chung','19_2023_qh15_526683_full.md','Kiểm soát nội dung bán hàng, quảng cáo, hợp đồng mẫu, điều khoản bất lợi cho khách hàng.','Thông tin cung cấp phải chính xác; điều khoản mẫu không được loại trừ trách nhiệm trái luật hoặc gây bất lợi bất hợp lý.','Brochure, sales kit, booking form, HĐMB, phụ lục, chính sách bán hàng.','Cơ quan quản lý cạnh tranh/bảo vệ người tiêu dùng, Sở Công Thương khi liên quan.','Bộ hợp đồng/thông tin bán hàng giảm rủi ro tranh chấp và xử phạt.','Sales script và tài liệu marketing phải khớp trạng thái pháp lý thật.')],
'X': [law('Bộ luật Dân sự 2015','Hợp đồng, bàn giao tài sản, bảo hành, trách nhiệm dân sự','91_2015_qh13_48695_full.md','Bổ sung nền hợp đồng cho bàn giao nhà, xử lý vi phạm, phạt, bồi thường, bảo hành và tranh chấp khách hàng.','HĐMB/phụ lục/biên bản bàn giao phải rõ đối tượng, diện tích, chất lượng, thời hạn, quyền/nghĩa vụ.','HĐMB, phụ lục, biên bản bàn giao, danh mục tồn tại, bảo hành, chứng từ thanh toán.','Tòa án/trọng tài/cơ quan giải quyết tranh chấp nếu phát sinh; CĐT và khách hàng trong vận hành hợp đồng.','Bộ hồ sơ bàn giao giảm tranh chấp và làm nền cấp GCN.','Pháp lý dự án đúng nhưng hợp đồng/bàn giao sai vẫn có rủi ro tranh chấp lớn.')],
'XI': [law('Luật Quản lý, sử dụng tài sản công 2017','Bàn giao HTKT/HTXH cho Nhà nước nếu hình thành tài sản công','15_2017_qh14_215536_full.md','Áp dụng khi hạ tầng kỹ thuật/xã hội phải bàn giao cho Nhà nước/đơn vị quản lý chuyên ngành.','Tài sản bàn giao phải đủ hồ sơ hoàn công, nghiệm thu, định danh tài sản và điều kiện tiếp nhận của cơ quan quản lý.','Hồ sơ hoàn công, nghiệm thu, quyết định/biên bản bàn giao, danh mục tài sản, giá trị tài sản nếu cần.','UBND/cơ quan chuyên ngành/đơn vị quản lý tài sản công.','Biên bản/quyết định tiếp nhận hạ tầng, giảm nghĩa vụ vận hành của CĐT.','Nếu không xử lý bàn giao hạ tầng, dễ kéo dài vận hành tạm và phát sinh chi phí hậu dự án.')]
}

def key(l): return (l.get('source_file',''), l.get('doc','').lower())

def clean_laws(existing, pref):
    cleaned=[]
    for l in existing:
        txt=json.dumps(l,ensure_ascii=False)
        # drop mojibake copies added by prior PowerShell run; keep original good Vietnamese laws
        if '??' in txt or 'Lu?t ' in txt or 'N? ' in txt or '?i?u' in txt:
            continue
        cleaned.append(l)
    keys={key(l) for l in cleaned}
    for l in EXTRA.get(pref,[]):
        if key(l) not in keys:
            cleaned.append(copy.deepcopy(l)); keys.add(key(l))
    return cleaned

for ph in data['phases']:
    pref=ph['id'].split('.')[0]
    for it in ph.get('items',[]): it['legal_basis']=clean_laws(it.get('legal_basis',[]), pref)
    for n in ph.get('subnodes',[]): n['legal_basis']=clean_laws(n.get('legal_basis',[]), pref)

data['encoding_audit']='fixed_utf8_phase_laws_v1'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2), encoding='utf-8')
for out in [base/'FINAL_BDS_LEGAL_WEB/tpre_bds_flow.json', Path('deploy_bds_legal_process/public/bds-legal-process/tpre_bds_flow.json')]:
    if out.exists(): out.write_text(json.dumps(data,ensure_ascii=False,indent=2), encoding='utf-8')
print('fixed utf8 legal basis')
