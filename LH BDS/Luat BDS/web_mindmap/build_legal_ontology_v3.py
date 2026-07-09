import json, pathlib, re
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
base=json.loads((out/'legal_knowledge_v2.json').read_text(encoding='utf-8'))
old={n['id']:n for n in base['nodes']}

def lb(ids):
    arr=[]
    for i in ids:
        arr += old.get(i,{}).get('legal_basis',[])
    return arr

def n(id,title,type,summary,parent=None,children=None,checks=None,basis=None):
    return {'id':id,'title':title,'type':type,'summary':summary,'parent':parent,'children':children or [],'checkpoints':checks or [],'legal_basis':basis or []}

nodes=[]
# Level 0
nodes.append(n('root','Bản đồ pháp lý dự án bất động sản','root','Chọn một mảng pháp lý lớn để đi sâu. Cây này tổ chức theo logic triển khai dự án: pháp lý đầu vào, đất đai, đầu tư/lựa chọn nhà đầu tư, xây dựng, kinh doanh và hậu kiểm.',children=['dev_process','land_access','investment_selection','construction_compliance','sales_handover']))
# Level 1 domains
nodes += [
 n('dev_process','Quy trình phát triển dự án nhà ở/khu đô thị','domain','Luồng tổng thể từ rà soát quỹ đất đến cấp sổ. Đây là master process để quản lý timeline dự án.',parent='root',children=['prep_stage','approval_stage','implementation_stage','commercial_stage']),
 n('land_access','Pháp lý đất đai và tiếp cận quỹ đất','domain','Nhóm quy định quyết định dự án đi theo đấu giá, đấu thầu, giao/thuê đất, chuyển mục đích hay thỏa thuận nhận quyền sử dụng đất.',parent='root',children=['land_due_diligence','land_allocation','land_auction','land_tender','land_agreement','land_finance']),
 n('investment_selection','Đầu tư và lựa chọn nhà đầu tư','domain','Nhóm thủ tục xác lập quyền triển khai dự án: chấp thuận chủ trương đầu tư, chấp thuận nhà đầu tư, lựa chọn nhà đầu tư, đấu giá/đấu thầu.',parent='root',children=['investment_policy','investor_approval','investor_selection_routes']),
 n('construction_compliance','Quy hoạch, xây dựng, môi trường, PCCC','domain','Nhóm thủ tục kỹ thuật để dự án đủ điều kiện thiết kế, cấp phép, khởi công, thi công, nghiệm thu.',parent='root',children=['planning_layer','environment_fire','building_permit','construction_acceptance']),
 n('sales_handover','Kinh doanh, bàn giao, cấp sổ và vận hành','domain','Nhóm điều kiện đưa sản phẩm ra thị trường, huy động vốn, bán nhà hình thành trong tương lai, bàn giao, cấp GCN và vận hành.',parent='root',children=['future_property_sale','handover_operation','certificate_issuance'])
]
# Process groups
nodes += [
 n('prep_stage','Giai đoạn chuẩn bị dự án','stage','Mục tiêu là xác định dự án có thể làm được không: quỹ đất, quy hoạch, chỉ tiêu, loại dự án, cơ chế pháp lý dự kiến.',parent='dev_process',children=['land_due_diligence','planning_layer'],checks=['Xác định ranh đất, hiện trạng sử dụng đất, chủ sử dụng đất.','Kiểm tra quy hoạch/kế hoạch sử dụng đất và quy hoạch xây dựng/đô thị.','Dự kiến cơ chế tiếp cận đất và lựa chọn nhà đầu tư.']),
 n('approval_stage','Giai đoạn phê duyệt/chọn nhà đầu tư/đất đai','stage','Giai đoạn quyết định quyền triển khai: chấp thuận chủ trương đầu tư, lựa chọn nhà đầu tư, giao/thuê đất/chuyển mục đích và nghĩa vụ tài chính.',parent='dev_process',children=['investment_policy','investor_selection_routes','land_allocation','land_finance']),
 n('implementation_stage','Giai đoạn thiết kế, cấp phép, thi công','stage','Giai đoạn biến quyền pháp lý thành công trình: môi trường, PCCC, thiết kế, giấy phép xây dựng, khởi công, nghiệm thu.',parent='dev_process',children=['environment_fire','building_permit','construction_acceptance']),
 n('commercial_stage','Giai đoạn kinh doanh và hậu kiểm','stage','Giai đoạn đưa sản phẩm ra thị trường: đủ điều kiện bán/huy động vốn, bàn giao, cấp sổ, vận hành và bảo trì.',parent='dev_process',children=['future_property_sale','handover_operation','certificate_issuance'])
]
# Land access branches
nodes += [
 n('land_due_diligence','Rà soát pháp lý quỹ đất','procedure','Bước nền để tránh sai nhánh: kiểm tra nguồn gốc đất, hiện trạng, quy hoạch, tranh chấp, hạn chế chuyển nhượng/chuyển mục đích và điều kiện đưa vào dự án.',parent='land_access',checks=old['p0']['checkpoints'],basis=lb(['p0','p1'])),
 n('land_allocation','Giao đất, cho thuê đất, chuyển mục đích','procedure','Thủ tục xác lập quyền sử dụng đất chính thức cho dự án sau khi đã xác định cơ chế đầu tư/quỹ đất.',parent='land_access',checks=old['p3']['checkpoints'],basis=lb(['p3'])),
 n('land_auction','Đấu giá quyền sử dụng đất','decision','Nhánh áp dụng khi pháp luật đất đai yêu cầu Nhà nước giao/cho thuê đất thông qua đấu giá QSDĐ và quỹ đất đủ điều kiện tổ chức đấu giá.',parent='land_access',checks=old['p2_daugia']['checkpoints'],basis=lb(['p2_daugia'])),
 n('land_tender','Đấu thầu dự án có sử dụng đất','decision','Nhánh áp dụng khi dự án/quỹ đất thuộc diện lựa chọn nhà đầu tư thông qua đấu thầu dự án có sử dụng đất.',parent='land_access',checks=old['p2_dauthau']['checkpoints'],basis=lb(['p2_dauthau'])),
 n('land_agreement','Thỏa thuận nhận QSDĐ hoặc đang có QSDĐ','decision','Nhánh nhà đầu tư tự thỏa thuận nhận chuyển nhượng/thuê/góp vốn bằng QSDĐ hoặc đang có QSDĐ, rồi xử lý thủ tục đầu tư và đất đai tương ứng.',parent='land_access',checks=old['p2_thoathuan']['checkpoints'],basis=lb(['p2_thoathuan'])),
 n('land_finance','Nghĩa vụ tài chính đất đai','procedure','Xác định giá đất, tiền sử dụng đất, tiền thuê đất, thuế/phí/lệ phí và chứng từ hoàn thành nghĩa vụ tài chính.',parent='land_access',checks=old['p4']['checkpoints'],basis=lb(['p4']))
]
# Investment
nodes += [
 n('investment_policy','Chấp thuận chủ trương đầu tư','procedure','Thủ tục xác nhận sự đồng ý của cơ quan có thẩm quyền về mục tiêu, quy mô, địa điểm, tiến độ, nhu cầu đất và điều kiện triển khai dự án.',parent='investment_selection',checks=old['p2_ctdt']['checkpoints'],basis=lb(['p2_ctdt'])),
 n('investor_approval','Chấp thuận nhà đầu tư','procedure','Xác định/chấp thuận chủ thể được thực hiện dự án trong trường hợp pháp luật đầu tư/đất đai cho phép, có thể gắn với hoặc sau chấp thuận chủ trương đầu tư.',parent='investment_selection',checks=['Có đồng thời chấp thuận chủ trương và nhà đầu tư không?','Nhà đầu tư có quyền sử dụng đất hoặc điều kiện tiếp cận đất hợp lệ không?','Có cần đấu giá/đấu thầu trước khi chấp thuận nhà đầu tư không?'],basis=lb(['p2_ctdt','p2_thoathuan'])),
 n('investor_selection_routes','Các tuyến lựa chọn nhà đầu tư','decision_group','Đây là điểm rẽ nhánh: cùng là lựa chọn nhà đầu tư nhưng có thể đi theo đấu giá QSDĐ, đấu thầu dự án có sử dụng đất, chấp thuận nhà đầu tư hoặc thỏa thuận QSDĐ.',parent='investment_selection',children=['land_auction','land_tender','land_agreement','investor_approval'],checks=['Không nhầm đấu giá QSDĐ với đấu thầu dự án có sử dụng đất.','Kiểm tra danh mục khu đất/dự án và tình trạng GPMB.','Nếu nhà đầu tư đang có đất, kiểm tra điều kiện thỏa thuận/chuyển mục đích.'],basis=lb(['p2_daugia','p2_dauthau','p2_thoathuan']))
]
# Construction
nodes += [
 n('planning_layer','Quy hoạch và chỉ tiêu dự án','procedure','Lớp pháp lý xác định dự án được xây cái gì, mật độ/tầng cao/dân số/hạ tầng ra sao và có phù hợp chương trình/kế hoạch phát triển nhà ở không.',parent='construction_compliance',checks=old['p1']['checkpoints'],basis=lb(['p1'])),
 n('environment_fire','Môi trường, PCCC và đấu nối hạ tầng','procedure','Các điều kiện kỹ thuật song song hoặc tiền đề cho thiết kế/cấp phép: môi trường, PCCC, đấu nối điện nước, thoát nước, giao thông.',parent='construction_compliance',checks=old['p5']['checkpoints'],basis=lb(['p5'])),
 n('building_permit','Thiết kế, thẩm định và giấy phép xây dựng','procedure','Lập và thẩm định thiết kế, xin giấy phép xây dựng nếu thuộc diện, đáp ứng điều kiện khởi công.',parent='construction_compliance',checks=old['p6']['checkpoints'],basis=lb(['p6'])),
 n('construction_acceptance','Thi công, nghiệm thu, hoàn công','procedure','Quản lý thi công theo thiết kế/giấy phép; nghiệm thu giai đoạn, nghiệm thu hoàn thành, hoàn công và nghiệm thu chuyên ngành.',parent='construction_compliance',checks=old['p7']['checkpoints'],basis=lb(['p7']))
]
# Sales
nodes += [
 n('future_property_sale','Bán/huy động vốn BĐS hình thành trong tương lai','procedure','Kiểm tra điều kiện đưa sản phẩm vào kinh doanh: pháp lý đất, hồ sơ dự án, tiến độ xây dựng, bảo lãnh ngân hàng, thông báo đủ điều kiện bán.',parent='sales_handover',checks=old['p8']['checkpoints'],basis=lb(['p8'])),
 n('handover_operation','Bàn giao, quản lý vận hành, bảo trì','procedure','Sau nghiệm thu và đủ điều kiện bàn giao, chủ đầu tư tổ chức bàn giao, vận hành, bảo trì, quản lý chung cư/khu đô thị theo quy định.',parent='sales_handover',checks=old['p9']['checkpoints'],basis=lb(['p9'])),
 n('certificate_issuance','Cấp GCN/sổ cho chủ đầu tư và người mua','procedure','Hoàn thiện hồ sơ cấp giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở/tài sản gắn liền với đất cho chủ đầu tư và người mua.',parent='sales_handover',checks=old['p9']['checkpoints'],basis=lb(['p9']))
]
# ensure children sync
by={x['id']:x for x in nodes}
for x in nodes: x['children']=[] if x.get('children') is None else x['children']
for x in nodes:
    if x.get('parent') and x['id'] not in by[x['parent']]['children']:
        by[x['parent']]['children'].append(x['id'])
flows=[]
for x in nodes:
    for c in x.get('children',[]): flows.append({'from':x['id'],'to':c,'label':'đi sâu'})
data={'title':'Bản đồ pháp lý dự án BĐS','subtitle':'Cây phân cấp tự tổ chức theo logic luật: domain → giai đoạn → quyết định → thủ tục → căn cứ điều luật. Không hard-code theo ví dụ, ví dụ chỉ là một nhánh trong ontology.','version':'v3-ontology-drilldown','nodes':nodes,'flows':flows,'notes':['Cấu trúc này tách bước tổng thể và bước con rõ hơn.', 'Các căn cứ pháp lý kế thừa từ bản trích xuất hiện có; cần tiếp tục bổ sung nguồn luật còn thiếu.']}
(out/'legal_ontology_v3.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('nodes',len(nodes),'flows',len(flows),'laws',sum(len(x.get('legal_basis',[])) for x in nodes))
