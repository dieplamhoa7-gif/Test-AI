import json, shutil
from pathlib import Path
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS')
json_path=base/'web_mindmap/bds_process_timeline_lawfaithful.json'
data=json.loads(json_path.read_text(encoding='utf-8'))

def lp(doc, article, source, pts):
    return {'doc':doc,'article':article,'source_file':source,'points':pts}

curated={
0:[
 lp('Luật Đất đai 2024','Điều 18, Điều 23, Điều 116, Điều 124, Điều 126, Điều 127','31_2024_qh15_523642_full.md',[
  'Kiểm tra quyền tiếp cận thông tin đất đai, hiện trạng pháp lý thửa đất và căn cứ giao đất/cho thuê đất/chuyển mục đích.',
  'Phân tuyến tiếp cận đất: không đấu giá/không đấu thầu, đấu giá QSDĐ, đấu thầu lựa chọn NĐT, hoặc thỏa thuận nhận QSDĐ/đang có QSDĐ.',
  'Nếu dự án phải chuyển mục đích sử dụng đất hoặc sử dụng đất do Nhà nước quản lý, cần kiểm tra trước điều kiện đưa vào kế hoạch sử dụng đất và cơ chế lựa chọn NĐT.' ]),
 lp('Luật KDBĐS 2023','Điều 6, Điều 40','29_2023_qh15_530116_full.md',[
  'Thông tin dự án BĐS đưa vào kinh doanh phải công khai đầy đủ, trung thực, chính xác trên hệ thống thông tin về nhà ở và thị trường BĐS và website doanh nghiệp.',
  'Điều kiện chuyển nhượng dự án yêu cầu có CTĐT/CTCTĐT/chấp thuận đầu tư, có lựa chọn/công nhận chủ đầu tư nếu thuộc trường hợp phải thực hiện, có quy hoạch chi tiết và điều kiện đất đai liên quan.',
  'Dùng Điều 40 như checklist DD khi mua/chuyển nhượng dự án hoặc nhận góp vốn dự án.' ]),
 lp('NĐ 102/2024/NĐ-CP','Điều 44, Điều 49, Điều 55, Điều 62','102_2024_nd-cp_603982_full.md',[
  'Quy định căn cứ, trình tự, thủ tục giao đất/cho thuê đất/chuyển mục đích đối với các trường hợp không thuộc diện CTCTĐT/CTNĐT.',
  'Có quy định thủ tục giao đất/cho thuê đất không đấu giá, không đấu thầu và trường hợp thông qua đấu thầu lựa chọn NĐT.',
  'Có cơ chế thỏa thuận nhận QSDĐ để thực hiện dự án phát triển kinh tế - xã hội; cần rà điều kiện thửa đất, loại đất, quy hoạch và hạn chế tiếp cận đất đai.' ])],
1:[
 lp('Luật Quy hoạch đô thị và nông thôn 2024','Điều 3 và các nhóm quy định về hệ thống quy hoạch','47_2024_qh15_583645_full.md',[
  'Xác định hệ thống quy hoạch đô thị và nông thôn, làm nền để kiểm tra dự án phải phù hợp quy hoạch chung, phân khu, chi tiết hoặc quy hoạch có liên quan.',
  'QHCT/chỉ tiêu kiến trúc là căn cứ quan trọng cho thiết kế, GPXD, điều kiện kinh doanh và chuyển nhượng dự án.' ]),
 lp('NĐ 115/2024/NĐ-CP','Điều 13, Điều 36','115_2024_nd-cp_606864_full.md',[
  'HSMT lựa chọn NĐT phải căn cứ các quy hoạch, kế hoạch, chương trình có liên quan; nếu quy hoạch thay đổi phải xử lý trước khi phê duyệt HSMT.',
  'Kết quả lựa chọn NĐT và hợp đồng dự án phải được trình, thẩm định, phê duyệt, công khai theo quy định đấu thầu.' ]),
 lp('NQ 254/2025/QH15','Điều 4','254_2025_qh15_684580_full.md',[
  'Điều kiện đấu giá QSDĐ đối với dự án nhà ở có thể căn cứ quy hoạch phân khu/quy hoạch chung nếu không yêu cầu lập quy hoạch phân khu hoặc QHCT theo pháp luật quy hoạch đô thị và nông thôn.',
  'Điều kiện đấu thầu lựa chọn NĐT dự án có sử dụng đất gắn với yêu cầu về quy hoạch theo Luật Đất đai và văn bản hướng dẫn.' ])],
2:[
 lp('Luật Đầu tư 2025','Điều 3, Điều 23, Điều 24, Điều 30','143_2025_qh15_681550_full.md',[
  'CTCTĐT là việc cơ quan có thẩm quyền chấp thuận mục tiêu, địa điểm, quy mô, tiến độ, thời hạn dự án; có thể bao gồm NĐT/hình thức lựa chọn NĐT và cơ chế đặc biệt nếu có.',
  'Lựa chọn NĐT thực hiện dự án đầu tư gồm đấu giá QSDĐ, đấu thầu lựa chọn NĐT, chấp thuận NĐT hoặc hình thức khác theo luật chuyên ngành.',
  'NĐT phải ký quỹ hoặc có bảo lãnh ngân hàng về nghĩa vụ ký quỹ để bảo đảm thực hiện dự án có đề nghị Nhà nước giao đất/cho thuê đất/chuyển mục đích, trừ trường hợp luật loại trừ.' ]),
 lp('NĐ hướng dẫn Luật Đầu tư/CTCTĐT','Điều 27, Điều 32','96_2026_nd-cp_690303_full.md',[
  'Hồ sơ đề nghị CTCTĐT do NĐT đề xuất gồm văn bản đề nghị, tài liệu tư cách pháp lý, tài liệu chứng minh năng lực tài chính và các tài liệu dự án theo quy định.',
  'Bảo đảm thực hiện dự án được lập bằng thỏa thuận giữa cơ quan đăng ký đầu tư và NĐT; thỏa thuận ghi nhận thông tin dự án, biện pháp bảo đảm, số tiền, thời hạn và điều kiện hoàn trả/không hoàn trả.' ]),
 lp('NĐ 115/2024/NĐ-CP','Điều 1, Điều 36, Điều 66','115_2024_nd-cp_606864_full.md',[
  'Quy định chi tiết lựa chọn NĐT thực hiện dự án thuộc trường hợp phải đấu thầu theo pháp luật quản lý ngành, lĩnh vực, trong đó có dự án sử dụng đất.',
  'Cần kiểm tra điều kiện nhà đầu tư: tư cách hợp lệ, năng lực, không bị cấm/tạm ngừng/đình chỉ kinh doanh BĐS, đáp ứng điều kiện giao đất/cho thuê đất.' ])],
3:[
 lp('Luật Đất đai 2024','Điều 79, Điều 116, Điều 124, Điều 126, Điều 127, Điều 153, Điều 158, Điều 160','31_2024_qh15_523642_full.md',[
  'Xác định trường hợp Nhà nước thu hồi đất, giao đất, cho thuê đất, cho phép chuyển mục đích, đấu giá QSDĐ, đấu thầu lựa chọn NĐT hoặc thỏa thuận nhận QSDĐ.',
  'Nghĩa vụ tài chính đất gồm tiền sử dụng đất, tiền thuê đất, giá đất cụ thể/bảng giá đất theo trường hợp; cần khóa thời điểm xác định giá và hồ sơ đầu vào.',
  'Dự án thông qua thỏa thuận nhận QSDĐ/đang có QSDĐ phải đáp ứng điều kiện về loại đất, quy hoạch, năng lực và hạn chế tiếp cận đất đai nếu có.' ]),
 lp('NĐ 102/2024/NĐ-CP','Điều 44, Điều 46, Điều 49, Điều 62','102_2024_nd-cp_603982_full.md',[
  'Quy định trình tự giao đất/cho thuê đất/chuyển mục đích sử dụng đất, bao gồm trường hợp không đấu giá/không đấu thầu và trường hợp qua đấu thầu lựa chọn NĐT.',
  'Có tiêu chí, điều kiện chuyển mục đích đối với đất trồng lúa, đất rừng phòng hộ, đất rừng đặc dụng, đất rừng sản xuất sang mục đích khác.',
  'Có chính sách khuyến khích thỏa thuận nhận QSDĐ để thực hiện dự án phát triển kinh tế - xã hội.' ]),
 lp('NĐ 103/2024/NĐ-CP','Điều 4 và nhóm quy định tiền sử dụng đất/tiền thuê đất','103_2024_nd-cp_550020_full.md',[
  'Diện tích tính tiền sử dụng đất là diện tích đất có thu tiền sử dụng đất ghi trên quyết định giao đất/chuyển mục đích/điều chỉnh quy hoạch chi tiết/chuyển hình thức sử dụng đất.',
  'Giá đất tính tiền sử dụng đất, tiền thuê đất xác định theo trường hợp luật định; trường hợp đấu giá là giá trúng đấu giá.',
  'Cần tách phần nghĩa vụ tài chính đất với chi phí bồi thường, hỗ trợ, tái định cư và chi phí hạ tầng.' ])],
4:[
 lp('Luật BVMT sửa đổi 2025','Điều 1 sửa đổi Luật BVMT','146_2025_qh15_675259_full.md',[
  'Rà soát đối tượng phải/không phải thực hiện đánh giá tác động môi trường; một số dự án đầu tư công khẩn cấp hoặc dự án không thuộc đối tượng theo luật/nghị quyết Quốc hội được loại trừ.',
  'Rà soát đối tượng phải/không phải có giấy phép môi trường; nếu phải có GPMT thì phải thực hiện đúng thời điểm trước vận hành hoặc trước khởi công theo trường hợp.' ]),
 lp('NĐ 131/2025/NĐ-CP','Điều 26','131_2025_nd-cp_660659_full.md',[
  'Chủ tịch UBND cấp tỉnh có thẩm quyền cấp giấy phép môi trường theo khoản 4 Điều 41 Luật BVMT đối với dự án/cơ sở nhóm I, II, III tại các phụ lục tương ứng của NĐ 08/2022/NĐ-CP.',
  'Cần kiểm tra thẩm quyền GPMT theo nhóm dự án, quy mô, yếu tố nhạy cảm môi trường và địa bàn.' ]),
 lp('NĐ 140/2025/NĐ-CP và NĐ 144/2025/NĐ-CP','Quy định phân quyền GPXD, quản lý chất lượng công trình','140_2025_nd-cp_660586_full.md;144_2025_nd-cp_660606_full.md',[
  'Thẩm quyền cấp GPXD theo Luật Xây dựng được phân cấp cho UBND cấp xã trong một số trường hợp theo NĐ 140/2025/NĐ-CP.',
  'Quy định phân quyền, phân cấp kiểm tra công tác nghiệm thu, quản lý chất lượng công trình xây dựng; cần kiểm tra loại/cấp công trình để xác định cơ quan kiểm tra.' ])],
5:[
 lp('NĐ 140/2025/NĐ-CP','Điều 8','140_2025_nd-cp_660586_full.md',[
  'Phân cấp thực hiện kiểm tra công tác nghiệm thu theo NĐ 06/2021/NĐ-CP về quản lý chất lượng, thi công xây dựng và bảo trì công trình.',
  'Cần xác định cấp công trình, loại công trình và cơ quan chuyên môn về xây dựng để biết nghĩa vụ kiểm tra nghiệm thu.' ]),
 lp('NĐ 144/2025/NĐ-CP','Điều 13 và nhóm quy định thẩm quyền quản lý chất lượng công trình','144_2025_nd-cp_660606_full.md',[
  'Quy định nhiệm vụ, thẩm quyền kiểm tra công tác nghiệm thu đối với công trình cấp đặc biệt và công trình thuộc lĩnh vực chuyên ngành trên địa bàn tỉnh.',
  'Dùng làm căn cứ phân luồng hồ sơ nghiệm thu, hoàn công, cập nhật tài sản gắn liền với đất.' ]),
 lp('Luật KDBĐS 2023','Điều 6','29_2023_qh15_530116_full.md',[
  'Trước khi đưa dự án/BĐS vào kinh doanh, doanh nghiệp phải công khai thông tin dự án, quyết định CTCTĐT/CTĐT, quyết định giao đất/cho thuê đất/chuyển mục đích, quy hoạch chi tiết, GPXD và thông tin nghiệm thu nếu có.',
  'Thi công/nghiệm thu không chỉ là bước xây dựng mà còn là điều kiện đầu vào cho kinh doanh, huy động vốn và bàn giao.' ])],
6:[
 lp('Luật KDBĐS 2023','Điều 6 và nhóm điều về kinh doanh BĐS hình thành trong tương lai','29_2023_qh15_530116_full.md',[
  'Trước khi kinh doanh, chủ đầu tư phải công khai đầy đủ thông tin dự án/BĐS; thông tin bao gồm pháp lý đầu tư, đất đai, quy hoạch, GPXD, nghiệm thu và hạn chế quyền nếu có.',
  'Điều kiện bán/cho thuê mua BĐS hình thành trong tương lai cần kiểm tra hồ sơ pháp lý dự án, giấy tờ đất, thiết kế/GPXD, nghiệm thu phần móng hoặc hạ tầng theo loại sản phẩm.',
  'Hợp đồng kinh doanh BĐS phải đúng mẫu/nội dung bắt buộc; không gom tiền/huy động vốn trái tuyến trước khi đủ điều kiện.' ]),
 lp('NĐ 96/2024/NĐ-CP','Chương về kinh doanh BĐS có sẵn và BĐS hình thành trong tương lai','96_2024_nd-cp_600395_full.md',[
  'Quy định chi tiết đối tượng, loại công trình/phần diện tích sàn được đưa vào kinh doanh; hướng dẫn hồ sơ, trình tự liên quan đến kinh doanh BĐS.',
  'Dùng để kiểm tra loại sản phẩm được phép bán/cho thuê mua/chuyển nhượng và hồ sơ công khai trước giao dịch.' ]),
 lp('Thông tư NHNN về bảo lãnh nhà ở hình thành trong tương lai','Quy định/cam kết bảo lãnh','49_2024_tt-nhnn_629634_full.md',[
  'Giao dịch nhà ở hình thành trong tương lai cần rà nghĩa vụ bảo lãnh của ngân hàng thương mại theo pháp luật kinh doanh BĐS và ngân hàng.',
  'Cần tách cam kết bảo lãnh/chứng thư bảo lãnh với thỏa thuận cấp bảo lãnh giữa ngân hàng và chủ đầu tư; kiểm tra phạm vi, thời hạn, nghĩa vụ hoàn tiền.' ])],
7:[
 lp('Luật Đất đai 2024','Nhóm quy định đăng ký đất đai, cấp GCN, quyền của người sử dụng đất','31_2024_qh15_523642_full.md',[
  'Sau bàn giao, chủ đầu tư phải hoàn tất hồ sơ đất đai/tài sản gắn liền với đất để người mua được đăng ký, cấp GCN theo quy định.',
  'Cần kiểm tra việc hoàn thành nghĩa vụ tài chính, nghiệm thu, hoàn công, bản vẽ hoàn công và tình trạng thế chấp/giải chấp trước khi làm sổ cho khách hàng.' ]),
 lp('NĐ 101/2024/NĐ-CP','Nhóm quy định đăng ký đất đai, tài sản gắn liền với đất, cấp GCN','101_2024_nd-cp_613131_full.md',[
  'Quy định nơi nộp hồ sơ, trả kết quả và thời gian giải quyết thủ tục đăng ký đất đai/cấp GCN; thời gian không tính phần xác định và thực hiện nghĩa vụ tài chính, xử lý vi phạm, trưng cầu giám định, niêm yết/công khai nếu có.',
  'Là căn cứ thực hiện thủ tục cấp GCN lần đầu/cấp cho người mua, đăng ký biến động và cập nhật tài sản gắn liền với đất.' ]),
 lp('NĐ 357/2025/NĐ-CP','Điều 15, Điều 25','357_2025_nd-cp_600394_full.md',[
  'Cơ sở dữ liệu nhà ở và thị trường BĐS có thông tin dự án, chủ đầu tư, mã số dự án/công trình, sản phẩm BĐS và thông tin quản lý vận hành nhà chung cư.',
  'Giai đoạn vận hành cần cập nhật/chia sẻ dữ liệu dự án, đơn vị quản lý vận hành và thông tin liên quan theo quy định.' ])]
}

# Update step and all procedure legal_points using step-specific curated + optional procedure title marker
for i,s in enumerate(data['steps']):
    s['legal_points']=curated.get(i,s.get('legal_points',[]))
    for p in s.get('procedures',[]):
        p['legal_points']=curated.get(i,p.get('legal_points',[]))
        p['legal_basis_note']='Căn cứ đang được map theo gate pháp lý; cần đối chiếu thêm hồ sơ cụ thể của dự án để chốt điều/khoản áp dụng.'

# Also add metadata for UI disclosure
data['legal_basis_status']='curated_from_local_md_v2'
data['legal_basis_note']='Căn cứ pháp lý đã được rà lại từ corpus MD nội bộ; loại bỏ các điều bị lệch topic/chuyển tiếp/hiệu lực. Đây là checklist căn cứ chính, không thay thế việc đối chiếu hồ sơ dự án cụ thể.'
backup=json_path.with_suffix('.pre_curated_backup.json')
shutil.copy2(json_path, backup)
json_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# sync deploy/final json
deploy=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process')
final=base/'FINAL_BDS_LEGAL_WEB'
for out in [deploy/'bds_process_timeline_lawfaithful.json', final/'bds_process_timeline_lawfaithful.json']:
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('patched curated legal basis', json_path, 'backup', backup)
