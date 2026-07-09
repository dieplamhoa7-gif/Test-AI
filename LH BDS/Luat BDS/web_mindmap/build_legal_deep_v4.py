import json,pathlib,re
base=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS")
out=base/'web_mindmap'; deep=base/'deep_research'
idx=json.loads((deep/'article_topic_index.json').read_text(encoding='utf-8'))
arts=idx['articles']
def top(topic,n=6,prefer=()):
    arr=[a for a in arts if topic in a['topics']]
    bad=('điều khoản thi hành','trách nhiệm thi hành','quy định chuyển tiếp','sửa đổi, bổ sung','bãi bỏ','mẫu số','phụ lục')
    def score(a):
        title=(a['article']+' '+a['summary_source'][:300]).lower()
        if any(b in title for b in bad):
            base=-50
        else:
            base=a['score']
        base += sum(20 for p in prefer if p.lower() in title or p in a['file'])
        # prefer substantive articles with topic terms in title
        return base
    arr=sorted(arr,key=score,reverse=True)
    seen=set(); res=[]
    for a in arr:
        if score(a) < 0: continue
        key=(a['file'],a['article'])
        if key in seen: continue
        seen.add(key); res.append({'article':a['article'],'source_file':a['file'],'document':a['doc_title'],'summary':a['summary_source'],'quote':a['quote']})
        if len(res)>=n: break
    return res

def node(id,title,type,summary,parent=None,children=None,topic=None,outputs=None,risks=None,checks=None,prefer=()):
    return {'id':id,'title':title,'type':type,'summary':summary,'parent':parent,'children':children or [],'topic':topic,'outputs':outputs or [],'risks':risks or [],'checkpoints':checks or [],'legal_basis':top(topic,7,prefer) if topic else []}
nodes=[]
nodes.append(node('root','Bản đồ pháp lý phát triển dự án BĐS','root','Cây tri thức đi từ tổng thể đến chi tiết: mỗi domain mở ra giai đoạn, quyết định rẽ nhánh, thủ tục con, output, rủi ro và căn cứ điều luật.'))
# domains
nodes += [
 node('master_process','Master timeline phát triển dự án','domain','Luồng tổng thể quản lý dự án từ khảo sát quỹ đất đến bàn giao/cấp sổ.', 'root', ['stage_0','stage_1','stage_2','stage_3','stage_4']),
 node('land_domain','Đất đai và quỹ đất','domain','Xác định dự án lấy đất bằng cách nào, đất có được chuyển mục đích/giao/thuê/đấu giá/đấu thầu không.', 'root', ['land_dd','land_recovery','land_allocation','auction_route','tender_route','agreement_route','land_finance'], 'land_allocation_conversion'),
 node('investment_domain','Đầu tư và lựa chọn nhà đầu tư','domain','Xác định chủ trương đầu tư, nhà đầu tư, cơ chế lựa chọn và điều kiện triển khai.', 'root', ['investment_policy','investor_approval','selection_decision','auction_route','tender_route','agreement_route'], 'investment_policy'),
 node('planning_build_domain','Quy hoạch, xây dựng, môi trường, PCCC','domain','Nhóm pháp lý kỹ thuật: quy hoạch/chỉ tiêu, môi trường, PCCC, thiết kế, giấy phép, thi công, nghiệm thu.', 'root', ['planning','environment_fire','design_permit','construction_acceptance'], 'planning'),
 node('business_domain','Kinh doanh, bàn giao, cấp sổ, vận hành','domain','Nhóm pháp lý thương mại và hậu kiểm: bán BĐS hình thành trong tương lai, huy động vốn, bàn giao, cấp GCN, vận hành.', 'root', ['future_sale','handover','certificate','operation'], 'real_estate_business')]
# stages
nodes += [
 node('stage_0','GĐ0. Tiền khả thi pháp lý','stage','Rà soát khả năng làm dự án trước khi bỏ chi phí lớn: đất, quy hoạch, loại dự án, cơ chế tiếp cận đất, rủi ro pháp lý.', 'master_process',['land_dd','planning','selection_decision'], outputs=['Legal DD report','Ma trận rủi ro','Đề xuất route pháp lý']),
 node('stage_1','GĐ1. Phê duyệt đầu tư và lựa chọn nhà đầu tư','stage','Chốt dự án có cần chủ trương đầu tư không, nhà đầu tư được chọn bằng cơ chế nào, điều kiện triển khai là gì.', 'master_process',['investment_policy','selection_decision','investor_approval'], 'investment_policy'),
 node('stage_2','GĐ2. Đất đai và tài chính đất','stage','Hoàn thiện quyền sử dụng đất cho dự án và nghĩa vụ tài chính đất đai.', 'master_process',['land_recovery','land_allocation','land_finance'], 'land_allocation_conversion'),
 node('stage_3','GĐ3. Thiết kế, cấp phép, thi công','stage','Hoàn thiện điều kiện kỹ thuật và xây dựng: môi trường/PCCC/đấu nối, thiết kế, giấy phép, thi công, nghiệm thu.', 'master_process',['environment_fire','design_permit','construction_acceptance'], 'construction'),
 node('stage_4','GĐ4. Kinh doanh và hậu kiểm','stage','Đưa sản phẩm ra thị trường, bàn giao, cấp sổ và vận hành sau bán hàng.', 'master_process',['future_sale','handover','certificate','operation'], 'real_estate_business')]
# detailed nodes
nodes += [
 node('land_dd','Rà soát pháp lý quỹ đất','procedure','Kiểm tra nguồn gốc, hiện trạng, chủ sử dụng, quy hoạch, tranh chấp, hạn chế giao dịch/chuyển mục đích, khả năng đưa đất vào dự án.', 'land_domain', topic='planning', outputs=['Báo cáo pháp lý quỹ đất','Danh mục tài liệu thiếu','Route tiếp cận đất sơ bộ'], risks=['Sai nguồn gốc đất dẫn tới chọn sai thủ tục','Quy hoạch/kế hoạch sử dụng đất không phù hợp']),
 node('planning','Quy hoạch và chỉ tiêu dự án','procedure','Xác định dự án có phù hợp quy hoạch, chỉ tiêu, chương trình/kế hoạch phát triển nhà ở, quy hoạch chi tiết hay không.', 'planning_build_domain', topic='planning', outputs=['Xác nhận/chứng cứ phù hợp quy hoạch','Chỉ tiêu quy hoạch kiến trúc','Nhu cầu lập/điều chỉnh quy hoạch chi tiết'], risks=['Không phù hợp quy hoạch hoặc thiếu quy hoạch chi tiết','Chỉ tiêu dân số/hạ tầng không đáp ứng']),
 node('investment_policy','Chấp thuận chủ trương đầu tư','procedure','Thủ tục chấp thuận mục tiêu, quy mô, địa điểm, tiến độ, nhu cầu đất, ưu đãi/điều kiện và cơ chế triển khai dự án.', 'investment_domain', topic='investment_policy', outputs=['Quyết định/chấp thuận chủ trương đầu tư','Điều kiện triển khai dự án'], risks=['Xác định sai thẩm quyền chấp thuận','Nội dung CTĐT chưa đủ để làm bước đất đai/lựa chọn NĐT']),
 node('investor_approval','Chấp thuận nhà đầu tư','procedure','Ghi nhận nhà đầu tư thực hiện dự án khi đáp ứng điều kiện theo pháp luật đầu tư/đất đai/đấu thầu.', 'investment_domain', topic='investment_policy', outputs=['Văn bản chấp thuận nhà đầu tư','Cập nhật nhà đầu tư trong hồ sơ dự án'], risks=['Chấp thuận nhà đầu tư khi lẽ ra phải đấu giá/đấu thầu','Năng lực/điều kiện nhà đầu tư chưa đủ']),
 node('selection_decision','Quyết định route lựa chọn nhà đầu tư','decision_group','Điểm rẽ nhánh: đấu giá QSDĐ, đấu thầu dự án có sử dụng đất, chấp thuận nhà đầu tư, hoặc thỏa thuận/đang có QSDĐ.', 'investment_domain',['auction_route','tender_route','agreement_route','investor_approval'], 'investor_selection', outputs=['Ma trận route lựa chọn NĐT','Căn cứ loại trừ/áp dụng từng route'], risks=['Nhầm đấu giá QSDĐ với đấu thầu dự án','Không kiểm tra danh mục khu đất/dự án phải đấu thầu']),
 node('auction_route','Đấu giá quyền sử dụng đất','route','Áp dụng khi Nhà nước giao đất/cho thuê đất thông qua đấu giá QSDĐ; cần quỹ đất đủ điều kiện, phương án đấu giá, giá khởi điểm và kết quả trúng đấu giá.', 'land_domain', topic='investor_selection', outputs=['Phương án đấu giá','Quyết định công nhận kết quả trúng đấu giá','Căn cứ giao/thuê đất sau đấu giá'], risks=['Quỹ đất chưa đủ điều kiện đấu giá','Giá khởi điểm/phương án đấu giá sai hoặc bị khiếu kiện'], prefer=('đấu giá quyền sử dụng đất','Điều 125','Điều 55','102_2024','31_2024')),
 node('tender_route','Đấu thầu lựa chọn NĐT dự án có sử dụng đất','route','Áp dụng khi dự án/khu đất thuộc diện đấu thầu lựa chọn nhà đầu tư. Cần công bố dự án, mời quan tâm nếu thuộc trường hợp, HSMT/HSDT, đánh giá và phê duyệt kết quả.', 'land_domain', topic='investor_selection', outputs=['Danh mục/khu đất đấu thầu','HSMT/HSDT','Kết quả lựa chọn nhà đầu tư','Hợp đồng dự án nếu có'], risks=['Thiếu NĐ 274/2026 hoặc văn bản đấu thầu cập nhật','Sai bước mời quan tâm/sơ tuyển'], prefer=('đấu thầu lựa chọn nhà đầu tư','Điều 126','Điều 57','102_2024','31_2024')),
 node('agreement_route','Thỏa thuận nhận QSDĐ / đang có QSDĐ','route','Nhà đầu tư tự nhận chuyển nhượng/thuê/góp vốn bằng QSDĐ hoặc đang có QSDĐ; phải kiểm tra điều kiện loại đất, quy hoạch, chuyển mục đích và chấp thuận đầu tư.', 'land_domain', topic='land_allocation_conversion', outputs=['Hợp đồng/chứng cứ quyền sử dụng đất','Điều kiện chuyển mục đích','Hồ sơ đầu tư/đất đai tương ứng'], risks=['Không đủ điều kiện nhận chuyển nhượng/chuyển mục đích','Đất hỗn hợp hoặc còn hộ dân không thỏa thuận được'], prefer=('thỏa thuận','nhận quyền sử dụng đất','Điều 127','31_2024')),
 node('land_recovery','Thu hồi đất, bồi thường, hỗ trợ, tái định cư','procedure','Khi thuộc trường hợp Nhà nước thu hồi đất, cần phương án bồi thường/hỗ trợ/tái định cư và tổ chức GPMB.', 'land_domain', topic='land_recovery_compensation', outputs=['Quyết định thu hồi đất','Phương án bồi thường/hỗ trợ/tái định cư','Mặt bằng sạch'], risks=['Kéo dài GPMB','Khiếu nại bồi thường/tái định cư']),
 node('land_allocation','Giao đất, cho thuê đất, chuyển mục đích','procedure','Thủ tục Nhà nước giao/cho thuê đất/cho phép chuyển mục đích để dự án có quyền sử dụng đất hợp pháp.', 'land_domain', topic='land_allocation_conversion', outputs=['Quyết định giao/thuê đất/chuyển mục đích','Hợp đồng thuê đất nếu có','Cập nhật đăng ký đất đai'], risks=['Thiếu căn cứ giao đất/cho thuê đất','Không phù hợp kế hoạch sử dụng đất hằng năm']),
 node('land_finance','Giá đất và nghĩa vụ tài chính đất đai','procedure','Xác định giá đất, tiền sử dụng đất, tiền thuê đất, miễn/giảm/khấu trừ nếu có, thuế/phí/lệ phí.', 'land_domain', topic='land_finance', outputs=['Thông báo nghĩa vụ tài chính','Chứng từ nộp tiền','Căn cứ tính giá đất'], risks=['Chậm xác định giá đất cụ thể','Chi phí đất thay đổi làm vỡ phương án tài chính']),
 node('environment_fire','Môi trường, PCCC, đấu nối hạ tầng','procedure','Các điều kiện kỹ thuật và pháp lý song song: ĐTM/GPMT, thẩm duyệt/nghiệm thu PCCC, đấu nối hạ tầng kỹ thuật.', 'planning_build_domain', topic='environment_fire_infra', outputs=['ĐTM/GPMT','Văn bản PCCC','Thỏa thuận đấu nối'], risks=['Thiếu PCCC/môi trường làm kẹt giấy phép/nghiệm thu','Hạ tầng ngoài hàng rào chưa đồng bộ']),
 node('design_permit','Thiết kế, thẩm định, giấy phép xây dựng','procedure','Lập thiết kế, thẩm định thiết kế, xin GPXD nếu thuộc diện và đủ điều kiện khởi công.', 'planning_build_domain', topic='construction', outputs=['Hồ sơ thiết kế được thẩm định','Giấy phép xây dựng','Thông báo khởi công'], risks=['Thiết kế không khớp quy hoạch/chỉ tiêu','Thiếu điều kiện khởi công']),
 node('construction_acceptance','Thi công, nghiệm thu, hoàn công','procedure','Quản lý thi công, nghiệm thu giai đoạn/hoàn thành, hoàn công và nghiệm thu chuyên ngành trước bàn giao.', 'planning_build_domain', topic='construction', outputs=['Biên bản nghiệm thu','Hồ sơ hoàn công','Điều kiện bàn giao'], risks=['Thi công sai phép/sai thiết kế','Không nghiệm thu được PCCC/hạ tầng']),
 node('future_sale','Bán/huy động vốn BĐS hình thành trong tương lai','procedure','Kiểm tra điều kiện đưa nhà ở/BĐS hình thành trong tương lai vào kinh doanh: đất, hồ sơ dự án, tiến độ xây dựng, bảo lãnh, thông báo đủ điều kiện bán.', 'business_domain', topic='real_estate_business', outputs=['Văn bản đủ điều kiện bán','Bảo lãnh ngân hàng','Hợp đồng mua bán/thuê mua'], risks=['Bán/huy động vốn trước khi đủ điều kiện','Hợp đồng/bảo lãnh không đúng quy định']),
 node('handover','Bàn giao nhà/công trình','procedure','Bàn giao sau nghiệm thu và đủ điều kiện, kèm hồ sơ pháp lý/kỹ thuật, bảo hành/bảo trì theo loại sản phẩm.', 'business_domain', topic='certificate_handover_operation', outputs=['Biên bản bàn giao','Hồ sơ bàn giao','Kích hoạt vận hành/bảo hành'], risks=['Bàn giao khi chưa đủ nghiệm thu','Tranh chấp diện tích/chất lượng/hồ sơ']),
 node('certificate','Cấp GCN/sổ','procedure','Cấp giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở/tài sản gắn liền với đất cho chủ đầu tư/người mua theo từng loại sản phẩm.', 'business_domain', topic='certificate_handover_operation', outputs=['GCN cho chủ đầu tư/người mua','Hồ sơ đăng ký biến động'], risks=['Chưa hoàn thành nghĩa vụ tài chính','Sai phân định diện tích chung/riêng, đất ở/đất thương mại dịch vụ']),
 node('operation','Quản lý vận hành, bảo trì, hậu kiểm','procedure','Tổ chức vận hành chung cư/khu đô thị, quỹ bảo trì, ban quản trị, quản lý phần sở hữu chung-riêng và hậu kiểm sau bàn giao.', 'business_domain', topic='certificate_handover_operation', outputs=['Quy chế vận hành','Quỹ bảo trì/bàn giao hồ sơ','Ban quản trị nếu có'], risks=['Tranh chấp quỹ bảo trì/sở hữu chung riêng','Không bàn giao hồ sơ vận hành đầy đủ'])]
# sync children
by={x['id']:x for x in nodes}
for x in nodes:
    if x.get('parent') and x['id'] not in by[x['parent']]['children']:
        by[x['parent']]['children'].append(x['id'])
flows=[]
for x in nodes:
    for c in x.get('children',[]): flows.append({'from':x['id'],'to':c})
data={'title':'Deep Legal Flow BĐS','subtitle':'Knowledge base pháp lý nhiều tầng cho dự án BĐS: master timeline, domain luật, decision route, thủ tục, output, rủi ro và căn cứ điều luật trích từ 1.717 điều khoản liên quan.','version':'v4-deep-research','nodes':nodes,'flows':flows,'source_stats':{'matched_articles':len(arts),'topics':{t:sum(1 for a in arts if t in a['topics']) for t in set(sum([a['topics'] for a in arts],[]))}}}
(out/'legal_deep_v4.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('nodes',len(nodes),'flows',len(flows),'laws',sum(len(n['legal_basis']) for n in nodes))

