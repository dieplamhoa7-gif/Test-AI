import json,pathlib
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
deep=json.loads((out/'legal_deep_v4.json').read_text(encoding='utf-8'))
by={n['id']:n for n in deep['nodes']}
def pick(id): return by[id]
def laws(*ids, limit=10):
    arr=[]; seen=set()
    for id in ids:
        for l in by.get(id,{}).get('legal_basis',[]):
            key=(l.get('source_file'),l.get('article'))
            if key not in seen:
                seen.add(key); arr.append(l)
            if len(arr)>=limit: return arr
    return arr
nodes=[]
def add(id,title,type,summary,parent=None,children=None,source_ids=(),outputs=None,risks=None,checks=None):
    nodes.append({'id':id,'title':title,'type':type,'summary':summary,'parent':parent,'children':children or [],'outputs':outputs or [],'risks':risks or [],'checkpoints':checks or [],'legal_basis':laws(*source_ids)})
add('root','Flow pháp lý phát triển dự án BĐS nhà ở/khu đô thị','root','Đi theo đúng tính chất dự án: mỗi giai đoạn là một “cửa pháp lý” phải qua. Bấm từng cửa để xem thủ tục con, route rẽ nhánh, output, rủi ro và điều luật trích dẫn.',children=['gate0','gate1','gate2','gate3','gate4','gate5','gate6','gate7'])
add('gate0','Gate 0 — Khảo sát quỹ đất & tiền khả thi','gate','Mục tiêu: biết khu đất có thể phát triển dự án hay không trước khi đi vào chi phí pháp lý lớn.', 'root', ['land_status','planning_fit','route_matrix'], ('land_dd','planning','selection_decision'), outputs=['Báo cáo pháp lý quỹ đất','Ma trận route pháp lý','Danh sách điều kiện/rủi ro cần xử lý'], risks=['Sai nguồn gốc đất hoặc quy hoạch dẫn tới chọn sai toàn bộ quy trình'])
add('gate1','Gate 1 — Quy hoạch & chỉ tiêu phát triển','gate','Mục tiêu: xác định dự án được xây gì, mật độ/tầng cao/dân số/hạ tầng ra sao, có cần lập/điều chỉnh quy hoạch chi tiết hay không.', 'root', ['planning_fit','housing_program','detail_planning'], ('planning',), outputs=['Căn cứ phù hợp quy hoạch','Chỉ tiêu quy hoạch kiến trúc','Nhiệm vụ/quy hoạch chi tiết nếu cần'])
add('gate2','Gate 2 — Chủ trương đầu tư & nhà đầu tư','gate','Mục tiêu: xác lập sự chấp thuận của Nhà nước về dự án và chủ thể thực hiện, đồng thời quyết định cơ chế lựa chọn nhà đầu tư.', 'root', ['investment_policy','investor_route','investor_approval_node'], ('investment_policy','investor_approval','selection_decision'), outputs=['Chấp thuận chủ trương đầu tư','Chấp thuận nhà đầu tư/kết quả lựa chọn NĐT','Điều kiện triển khai dự án'])
add('gate3','Gate 3 — Tiếp cận đất & hoàn tất đất đai','gate','Mục tiêu: biến cơ chế đầu tư thành quyền sử dụng đất hợp pháp cho dự án: thu hồi/GPMB, giao/thuê đất, chuyển mục đích, đăng ký đất.', 'root', ['land_recovery_node','land_allocation_node','land_finance_node'], ('land_recovery','land_allocation','land_finance'), outputs=['Mặt bằng/quyền sử dụng đất','Quyết định giao/thuê/chuyển mục đích','Hoàn thành nghĩa vụ tài chính'])
add('gate4','Gate 4 — Điều kiện kỹ thuật trước xây dựng','gate','Mục tiêu: hoàn thiện môi trường, PCCC, đấu nối hạ tầng, thiết kế/thẩm định/giấy phép để đủ điều kiện khởi công.', 'root', ['environment_node','design_permit_node'], ('environment_fire','design_permit'), outputs=['ĐTM/GPMT/PCCC/đấu nối','Thiết kế được thẩm định','Giấy phép xây dựng/điều kiện khởi công'])
add('gate5','Gate 5 — Thi công, nghiệm thu, hoàn công','gate','Mục tiêu: xây dựng đúng pháp lý và tạo điều kiện bàn giao/kinh doanh/cấp sổ.', 'root', ['construction_node','acceptance_node'], ('construction_acceptance',), outputs=['Biên bản nghiệm thu','Hồ sơ hoàn công','Điều kiện bàn giao'])
add('gate6','Gate 6 — Kinh doanh & huy động vốn','gate','Mục tiêu: xác định khi nào được bán/huy động vốn nhà ở/BĐS hình thành trong tương lai, bảo lãnh, hợp đồng, thông báo đủ điều kiện.', 'root', ['future_sale_node','contract_capital_node'], ('future_sale',), outputs=['Văn bản đủ điều kiện bán','Bảo lãnh ngân hàng','Hợp đồng mua bán/thuê mua hợp lệ'])
add('gate7','Gate 7 — Bàn giao, cấp sổ, vận hành','gate','Mục tiêu: hoàn tất vòng đời dự án sau xây dựng: bàn giao, cấp GCN, vận hành, bảo trì, hậu kiểm.', 'root', ['handover_node','certificate_node','operation_node'], ('handover','certificate','operation'), outputs=['Bàn giao sản phẩm','GCN/sổ cho người mua','Cơ chế vận hành/bảo trì'])
# children details
add('land_status','Rà soát hiện trạng và nguồn gốc đất','procedure','Kiểm tra chủ sử dụng, loại đất, thời hạn, tranh chấp, tài sản trên đất, hạn chế giao dịch, khả năng đưa vào dự án.', 'gate0', source_ids=('land_dd',), outputs=['Legal DD đất'], risks=['Đất không sạch pháp lý hoặc không đủ điều kiện chuyển mục đích'])
add('planning_fit','Phù hợp quy hoạch/kế hoạch sử dụng đất','procedure','Đối chiếu quy hoạch sử dụng đất, quy hoạch đô thị/xây dựng, chỉ tiêu và kế hoạch sử dụng đất hằng năm.', 'gate0', source_ids=('planning',), outputs=['Kết luận phù hợp/không phù hợp quy hoạch'])
add('route_matrix','Ma trận route pháp lý dự án','decision','Kết luận dự án đi theo đấu giá, đấu thầu, chấp thuận nhà đầu tư hay thỏa thuận QSDĐ/đang có QSDĐ.', 'gate0', ['route_auction','route_tender','route_agreement','route_direct_approval'], ('selection_decision','auction_route','tender_route','agreement_route'))
add('housing_program','Chương trình/kế hoạch phát triển nhà ở','procedure','Kiểm tra dự án nhà ở có phù hợp chương trình/kế hoạch phát triển nhà ở và chỉ tiêu địa phương không.', 'gate1', source_ids=('planning',))
add('detail_planning','Quy hoạch chi tiết/chỉ tiêu kiến trúc','procedure','Xác định nhu cầu lập, điều chỉnh, phê duyệt quy hoạch chi tiết hoặc tổng mặt bằng theo loại dự án.', 'gate1', source_ids=('planning',))
add('investment_policy','Chấp thuận chủ trương đầu tư','procedure','Xác định thẩm quyền, hồ sơ, nội dung chấp thuận chủ trương đầu tư và các điều kiện đi kèm.', 'gate2', source_ids=('investment_policy',))
add('investor_route','Chọn tuyến lựa chọn nhà đầu tư','decision','Cửa rẽ nhánh giữa đấu giá QSDĐ, đấu thầu dự án có sử dụng đất, chấp thuận nhà đầu tư, thỏa thuận QSDĐ.', 'gate2', ['route_auction','route_tender','route_agreement','route_direct_approval'], ('selection_decision','auction_route','tender_route','agreement_route'))
add('investor_approval_node','Chấp thuận nhà đầu tư','procedure','Ghi nhận nhà đầu tư khi đáp ứng điều kiện; không dùng để né đấu giá/đấu thầu nếu pháp luật bắt buộc.', 'gate2', source_ids=('investor_approval',))
add('route_auction','Route A — Đấu giá quyền sử dụng đất','route','Áp dụng khi Nhà nước giao/cho thuê đất thông qua đấu giá QSDĐ; cần quỹ đất đủ điều kiện, phương án đấu giá, giá khởi điểm, công nhận kết quả.', 'investor_route', source_ids=('auction_route',), outputs=['Phương án đấu giá','Kết quả trúng đấu giá','Căn cứ giao/thuê đất'], risks=['Quỹ đất chưa đủ điều kiện đấu giá','Sai giá khởi điểm/phương án đấu giá'])
add('route_tender','Route B — Đấu thầu lựa chọn NĐT dự án có sử dụng đất','route','Áp dụng khi dự án/khu đất thuộc diện đấu thầu lựa chọn nhà đầu tư. Cần công bố dự án, mời quan tâm nếu có, HSMT/HSDT, phê duyệt kết quả.', 'investor_route', source_ids=('tender_route',), outputs=['Danh mục/khu đất đấu thầu','HSMT/HSDT','Kết quả lựa chọn NĐT'], risks=['Thiếu NĐ 274/2026 nếu áp dụng','Nhầm với đấu giá QSDĐ'])
add('route_agreement','Route C — Thỏa thuận nhận QSDĐ / đang có QSDĐ','route','Nhà đầu tư tự thỏa thuận nhận chuyển nhượng/thuê/góp vốn bằng QSDĐ hoặc đang có QSDĐ; kiểm tra điều kiện chuyển mục đích và đầu tư.', 'investor_route', source_ids=('agreement_route',), outputs=['Chứng cứ QSDĐ','Hồ sơ chuyển mục đích/đầu tư'], risks=['Không thỏa thuận được 100% diện tích','Đất không đủ điều kiện chuyển mục đích'])
add('route_direct_approval','Route D — Chấp thuận nhà đầu tư/giao đất không đấu giá đấu thầu','route','Áp dụng khi thuộc trường hợp pháp luật cho phép không đấu giá/không đấu thầu; phải có căn cứ loại trừ rõ.', 'investor_route', source_ids=('investor_approval','land_allocation'), outputs=['Căn cứ loại trừ đấu giá/đấu thầu','Văn bản chấp thuận nhà đầu tư/giao đất'], risks=['Áp dụng sai trường hợp loại trừ'])
add('land_recovery_node','Thu hồi đất, bồi thường, GPMB','procedure','Nếu thuộc trường hợp Nhà nước thu hồi đất, phải xử lý thu hồi, bồi thường, hỗ trợ, tái định cư và mặt bằng.', 'gate3', source_ids=('land_recovery',))
add('land_allocation_node','Giao đất, thuê đất, chuyển mục đích','procedure','Thủ tục chính thức để dự án có quyền sử dụng đất hợp pháp theo route đã chọn.', 'gate3', source_ids=('land_allocation',))
add('land_finance_node','Giá đất và nghĩa vụ tài chính','procedure','Xác định giá đất, tiền sử dụng đất/thuê đất, thuế phí và chứng từ hoàn thành nghĩa vụ tài chính.', 'gate3', source_ids=('land_finance',))
add('environment_node','Môi trường, PCCC, hạ tầng đấu nối','procedure','Các thủ tục kỹ thuật song song: môi trường, PCCC, điện nước, thoát nước, giao thông, hạ tầng ngoài hàng rào.', 'gate4', source_ids=('environment_fire',))
add('design_permit_node','Thiết kế, thẩm định, giấy phép xây dựng','procedure','Lập/thẩm định thiết kế, xin giấy phép xây dựng nếu thuộc diện, đáp ứng điều kiện khởi công.', 'gate4', source_ids=('design_permit',))
add('construction_node','Thi công theo thiết kế/giấy phép','procedure','Tổ chức thi công, giám sát, quản lý chất lượng, an toàn và thay đổi thiết kế nếu có.', 'gate5', source_ids=('construction_acceptance',))
add('acceptance_node','Nghiệm thu, hoàn công','procedure','Nghiệm thu giai đoạn/hoàn thành, hoàn công, nghiệm thu PCCC/hạ tầng để đủ điều kiện bàn giao.', 'gate5', source_ids=('construction_acceptance',))
add('future_sale_node','Điều kiện bán BĐS hình thành trong tương lai','procedure','Kiểm tra điều kiện dự án, đất, tiến độ xây dựng, bảo lãnh ngân hàng và thông báo đủ điều kiện bán.', 'gate6', source_ids=('future_sale',))
add('contract_capital_node','Hợp đồng, bảo lãnh, huy động vốn','procedure','Kiểm soát mẫu hợp đồng, bảo lãnh, tiến độ thanh toán, giới hạn huy động vốn và công bố thông tin.', 'gate6', source_ids=('future_sale',))
add('handover_node','Bàn giao nhà/công trình','procedure','Bàn giao khi đủ nghiệm thu và điều kiện pháp lý/kỹ thuật, kèm hồ sơ bàn giao.', 'gate7', source_ids=('handover',))
add('certificate_node','Cấp GCN/sổ','procedure','Cấp giấy chứng nhận cho chủ đầu tư/người mua theo loại sản phẩm và phần diện tích.', 'gate7', source_ids=('certificate',))
add('operation_node','Vận hành, bảo trì, hậu kiểm','procedure','Quản lý vận hành, quỹ bảo trì, ban quản trị, sở hữu chung-riêng và xử lý hậu kiểm sau bàn giao.', 'gate7', source_ids=('operation',))
# sync children reverse
by2={n['id']:n for n in nodes}
for n in nodes:
    if n['parent'] and n['id'] not in by2[n['parent']]['children']:
        by2[n['parent']]['children'].append(n['id'])
flows=[]
for n in nodes:
    for c in n['children']: flows.append({'from':n['id'],'to':c})
result={'title':'Flow pháp lý phát triển dự án BĐS nhà ở/khu đô thị','subtitle':'Bản v5 tổ chức theo tính chất dự án: từng cửa pháp lý, route rẽ nhánh, thủ tục con, output, rủi ro và trích dẫn điều luật.','version':'v5-project-flow','nodes':nodes,'flows':flows,'source':'legal_deep_v4 + manual project-flow curation'}
(out/'legal_project_flow_v5.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('nodes',len(nodes),'flows',len(flows),'laws',sum(len(n['legal_basis']) for n in nodes))
