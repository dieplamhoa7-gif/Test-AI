import json,re,pathlib
src=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx")
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
texts={p.name:p.read_text(encoding='utf-8',errors='ignore') for p in src.glob('*.md')}

def find_article(file, art_no=None, contains=None):
    text=texts.get(file,'')
    pat = rf'(?m)^\s*(Điều\s+{art_no}[a-zA-Z]?\.\s+[^\n]+)' if art_no else r'(?m)^\s*(Điều\s+\d+[a-zA-Z]?\.\s+[^\n]+)'
    ms=list(re.finditer(pat,text))
    for i,m in enumerate(ms):
        end=ms[i+1].start() if i+1<len(ms) else min(len(text),m.start()+5000)
        block=text[m.start():end]
        if contains and contains.lower() not in block.lower():
            continue
        return {'article':clean(m.group(1)),'source_file':file,'summary':clean(block[len(m.group(1)):])[:650],'quote':clean(block)[:1400]}
    # fallback global contains
    if contains:
        idx=text.lower().find(contains.lower())
        if idx>=0:
            block=text[max(0,idx-250):idx+1200]
            return {'article':contains,'source_file':file,'summary':clean(block)[:650],'quote':clean(block)[:1400]}
    return {'article':f'Chưa tìm thấy điều {art_no or contains}','source_file':file,'summary':'Cần bổ sung/rà lại nguồn luật.', 'quote':''}

LBDS='29_2023_qh15_530116_full.md' # Kinh doanh BDS likely
LDD='31_2024_qh15_523642_full.md'
LDauTu='61_2024_tt-nhnn_639420_full.md'
# use known files from previous extraction
nodes=[
{'id':'root','title':'Tổng hợp pháp lý dự án BĐS','type':'root','summary':'Trang tri thức pháp lý theo cấu trúc tổng thể → quy trình → nhánh thủ tục → điều luật. Mục tiêu là giúp đội dự án hiểu phải làm gì, căn cứ nào, output nào và rủi ro nào trước khi triển khai.'},
{'id':'housing','parent':'root','title':'Quy trình phát triển dự án BĐS nhà ở','type':'process','summary':'Luồng chuẩn cho dự án nhà ở/khu đô thị: kiểm tra quy hoạch, chủ trương đầu tư, lựa chọn nhà đầu tư, đất đai, tài chính, thiết kế, xây dựng, bán hàng và cấp sổ.'},
{'id':'p0','parent':'housing','title':'P0. Rà soát quỹ đất và quy hoạch','type':'phase','summary':'Xác định hiện trạng đất, chủ sử dụng, quy hoạch, kế hoạch sử dụng đất, chỉ tiêu kiến trúc, khả năng chuyển mục đích và phương án tiếp cận đất.'},
{'id':'p1','parent':'housing','title':'P1. Quy hoạch, chương trình phát triển nhà ở','type':'phase','summary':'Đối chiếu quy hoạch đô thị/nông thôn, quy hoạch xây dựng, chương trình/kế hoạch phát triển nhà ở và chỉ tiêu dự án trước khi xin thủ tục đầu tư.'},
{'id':'p2','parent':'housing','title':'P2. Chấp thuận chủ trương đầu tư và lựa chọn NĐT','type':'phase','summary':'Nút rẽ quan trọng: dự án có phải chấp thuận chủ trương không, cơ chế chọn nhà đầu tư là giao trực tiếp, đấu giá đất, đấu thầu dự án có sử dụng đất hay thỏa thuận nhận quyền sử dụng đất.'},
{'id':'p2_ctdt','parent':'p2','title':'Chấp thuận chủ trương đầu tư','type':'branch','summary':'Xác lập sự đồng ý của cơ quan nhà nước về mục tiêu, quy mô, địa điểm, tiến độ, nhu cầu đất và điều kiện triển khai dự án trước khi đi vào lựa chọn/ghi nhận nhà đầu tư.'},
{'id':'p2_lcnt','parent':'p2','title':'Lựa chọn nhà đầu tư','type':'branch','summary':'Sau khi xác định dự án và quỹ đất, cần xác định cơ chế lựa chọn NĐT: đấu giá quyền sử dụng đất, đấu thầu lựa chọn NĐT, chấp thuận NĐT hoặc nhận chuyển nhượng/thỏa thuận quyền sử dụng đất.'},
{'id':'p2_daugia','parent':'p2_lcnt','title':'Đấu giá quyền sử dụng đất','type':'deep','summary':'Áp dụng khi Nhà nước giao đất/cho thuê đất thông qua đấu giá đối với quỹ đất đủ điều kiện đấu giá. Cần kiểm tra đất đã giải phóng mặt bằng, quy hoạch, giá khởi điểm, phương án đấu giá và điều kiện tham gia.'},
{'id':'p2_dauthau','parent':'p2_lcnt','title':'Đấu thầu lựa chọn NĐT dự án có sử dụng đất','type':'deep','summary':'Áp dụng với dự án đầu tư có sử dụng đất thuộc danh mục/khu đất phải đấu thầu. Cần đi theo logic công bố dự án, mời quan tâm nếu có, sơ tuyển/đấu thầu, phê duyệt kết quả và ký kết hợp đồng.'},
{'id':'p2_thoathuan','parent':'p2_lcnt','title':'Thỏa thuận nhận quyền sử dụng đất / đang có quyền sử dụng đất','type':'deep','summary':'Nhà đầu tư tự thỏa thuận nhận chuyển nhượng, thuê, góp vốn bằng quyền sử dụng đất hoặc đang có quyền sử dụng đất, sau đó thực hiện thủ tục đầu tư, đất đai, chuyển mục đích nếu đủ điều kiện.'},
{'id':'p3','parent':'housing','title':'P3. Giao đất, thuê đất, chuyển mục đích, GPMB','type':'phase','summary':'Hoàn tất quyền sử dụng đất cho dự án: thu hồi đất nếu thuộc trường hợp Nhà nước thu hồi, bồi thường/tái định cư, giao đất/thuê đất/chuyển mục đích và đăng ký đất đai.'},
{'id':'p4','parent':'housing','title':'P4. Nghĩa vụ tài chính đất đai','type':'phase','summary':'Xác định giá đất, tiền sử dụng đất, tiền thuê đất, các khoản thuế/phí/lệ phí và chứng từ hoàn thành nghĩa vụ tài chính trước các mốc bán hàng/cấp sổ.'},
{'id':'p5','parent':'housing','title':'P5. Môi trường, PCCC, hạ tầng đấu nối','type':'phase','summary':'Bảo đảm phê duyệt/xác nhận môi trường, thẩm duyệt PCCC, thỏa thuận đấu nối điện nước thoát nước giao thông và các điều kiện kỹ thuật liên quan.'},
{'id':'p6','parent':'housing','title':'P6. Thiết kế, thẩm định, giấy phép xây dựng','type':'phase','summary':'Lập thiết kế, thẩm định thiết kế, xin giấy phép xây dựng nếu thuộc diện cấp phép, đủ điều kiện khởi công và quản lý chất lượng công trình.'},
{'id':'p7','parent':'housing','title':'P7. Thi công, nghiệm thu, hoàn công','type':'phase','summary':'Tổ chức thi công theo giấy phép/thiết kế, nghiệm thu từng phần và hoàn thành công trình, hoàn công, nghiệm thu PCCC/hạ tầng trước bàn giao.'},
{'id':'p8','parent':'housing','title':'P8. Huy động vốn, bán nhà ở hình thành trong tương lai','type':'phase','summary':'Kiểm tra điều kiện đưa BĐS hình thành trong tương lai vào kinh doanh, bảo lãnh ngân hàng, thông báo đủ điều kiện bán, hợp đồng mẫu và giới hạn huy động vốn.'},
{'id':'p9','parent':'housing','title':'P9. Cấp sổ, bàn giao, vận hành, hậu kiểm','type':'phase','summary':'Bàn giao nhà/công trình, cấp GCN cho người mua, vận hành chung cư/khu đô thị, bảo trì, ban quản trị và xử lý hậu kiểm pháp lý.'},
]
# attach curated legal bases
basis={
'p2_ctdt':[find_article('96_2026_nd-cp_690303_full.md',30,'Chấp thuận chủ trương đầu tư'), find_article('31_2024_qh15_523642_full.md',116,'Căn cứ giao đất')],
'p2_daugia':[find_article(LDD,125,'đấu giá quyền sử dụng đất'), find_article('102_2024_nd-cp_603982_full.md',55,'đấu giá quyền sử dụng đất'), find_article('102_2024_nd-cp_603982_full.md',49,'giao đất')],
'p2_dauthau':[find_article(LDD,126,'đấu thầu lựa chọn nhà đầu tư'), find_article('102_2024_nd-cp_603982_full.md',57,'đấu thầu lựa chọn nhà đầu tư'), find_article('102_2024_nd-cp_603982_full.md',49,'đấu thầu lựa chọn nhà đầu tư')],
'p2_thoathuan':[find_article(LDD,127,'thỏa thuận'), find_article(LDD,122,'chuyển mục đích'), find_article('102_2024_nd-cp_603982_full.md',44,'chuyển mục đích')],
'p3':[find_article(LDD,79,'thu hồi đất'), find_article(LDD,228,'Trình tự, thủ tục giao đất'), find_article('102_2024_nd-cp_603982_full.md',49,'giao đất')],
'p4':[find_article('103_2024_nd-cp_550020_full.md',3,'tiền sử dụng đất'), find_article('103_2024_nd-cp_550020_full.md',4,'tiền thuê đất'), find_article(LDD,159,'bảng giá đất')],
'p1':[find_article('47_2024_qh15_583645_full.md',15,'Căn cứ lập quy hoạch'), find_article('47_2024_qh15_583645_full.md',16,'Trình tự lập'), find_article('27_2025_tt-bnv_687549_full.md',None,'chương trình phát triển nhà ở')],
'p8':[find_article('29_2023_qh15_530116_full.md',24,'bất động sản hình thành trong tương lai'), find_article('96_2024_nd-cp_600395_full.md',None,'bất động sản hình thành trong tương lai'), find_article('49_2024_tt-nhnn_629634_full.md',None,'bảo lãnh')],
'p9':[find_article(LDD,143,'Cấp Giấy chứng nhận'), find_article('101_2024_nd-cp_613131_full.md',None,'quản lý vận hành nhà chung cư'), find_article('05_2024_tt-bxd_619409_full.md' if False else '04_2024_tt-bxd_619409_full.md',None,'quản lý vận hành')]
}
for n in nodes:
    n['legal_basis']=basis.get(n['id'],[])
    n['children']=[x['id'] for x in nodes if x.get('parent')==n['id']]
    n['checkpoints']=['Xác định loại dự án và nguồn gốc đất trước khi áp quy trình.', 'Đối chiếu luật gốc, nghị định hướng dẫn và văn bản địa phương tại thời điểm thực hiện.']
    if n['id']=='p2_daugia': n['checkpoints']=['Đất có thuộc trường hợp phải đấu giá không?', 'Quỹ đất đã đủ điều kiện tổ chức đấu giá chưa?', 'Giá khởi điểm/phương án đấu giá đã được phê duyệt chưa?']
    if n['id']=='p2_dauthau': n['checkpoints']=['Dự án có thuộc danh mục/khu đất đấu thầu lựa chọn NĐT không?', 'Có phải mời quan tâm trước không?', 'Dự án thuộc quy trình 1 giai đoạn hay 2 giai đoạn?']
    if n['id']=='p2_ctdt': n['checkpoints']=['Dự án có thuộc diện chấp thuận chủ trương đầu tư không?', 'Cơ quan chấp thuận là Quốc hội, Thủ tướng hay UBND cấp tỉnh?', 'Nội dung chấp thuận có đồng thời chấp thuận nhà đầu tư không?']
flows=[
{'from':'root','to':'housing','label':'chọn loại dự án'}, {'from':'housing','to':'p0','label':'bắt đầu'}, {'from':'p0','to':'p1','label':'phù hợp quy hoạch'}, {'from':'p1','to':'p2','label':'xác lập cơ chế đầu tư'}, {'from':'p2','to':'p2_ctdt','label':'có/không CTĐT'}, {'from':'p2','to':'p2_lcnt','label':'chọn NĐT'}, {'from':'p2_lcnt','to':'p2_daugia','label':'đấu giá đất'}, {'from':'p2_lcnt','to':'p2_dauthau','label':'đấu thầu dự án'}, {'from':'p2_lcnt','to':'p2_thoathuan','label':'thỏa thuận QSDĐ'}, {'from':'p2','to':'p3','label':'sau cơ chế đầu tư'}, {'from':'p3','to':'p4','label':'tính tiền đất'}, {'from':'p4','to':'p5','label':'song song kỹ thuật'}, {'from':'p5','to':'p6','label':'thiết kế/cấp phép'}, {'from':'p6','to':'p7','label':'thi công'}, {'from':'p7','to':'p8','label':'đủ điều kiện kinh doanh'}, {'from':'p8','to':'p9','label':'bàn giao/cấp sổ'}]
data={'title':'Web luật dự án BĐS','subtitle':'Tổng hợp, tóm tắt và drill-down quy trình pháp lý dự án BĐS nhà ở, có flowchart và trích dẫn điều luật rõ ràng.','version':'v2-curated-preview','nodes':nodes,'flows':flows,'notes':['Bản v2 ưu tiên cấu trúc đúng và trích dẫn rõ hơn cho các nhánh trọng yếu.', 'Cần tiếp tục bổ sung luật quan trọng nếu thiếu, đặc biệt Nghị định 274/2026/NĐ-CP nếu anh muốn giống link tham khảo về lựa chọn nhà đầu tư.']}
(out/'legal_knowledge_v2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('nodes',len(nodes),'flows',len(flows),'with_basis',sum(bool(n['legal_basis']) for n in nodes))
