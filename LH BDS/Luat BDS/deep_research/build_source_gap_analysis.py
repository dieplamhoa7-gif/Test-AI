import json, pathlib, re
base=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS")
deep=base/'deep_research'
local=json.loads((deep/'local_source_inventory.json').read_text(encoding='utf-8'))
# target source checklist. If matched in local file/title, mark provided.
targets=[
 {'id':'land_law_2024','name':'Luật Đất đai 2024','patterns':['31_2024_qh15','Luật Đất đai']},
 {'id':'housing_law_2023','name':'Luật Nhà ở 2023','patterns':['27_2023_qh15','Luật Nhà ở']},
 {'id':'reb_law_2023','name':'Luật Kinh doanh bất động sản 2023','patterns':['29_2023_qh15','Kinh doanh bất động sản']},
 {'id':'bidding_law_2023','name':'Luật Đấu thầu 2023/sửa đổi','patterns':['22_2023_qh15','Luật Đấu thầu','đấu thầu']},
 {'id':'investment_law','name':'Luật Đầu tư và văn bản sửa đổi','patterns':['Luật Đầu tư','đầu tư']},
 {'id':'construction_law','name':'Luật Xây dựng và sửa đổi','patterns':['Luật Xây dựng','xây dựng']},
 {'id':'urban_planning_law_2024','name':'Luật Quy hoạch đô thị và nông thôn 2024','patterns':['47_2024_qh15','Quy hoạch đô thị']},
 {'id':'land_decree_102','name':'Nghị định 102/2024/NĐ-CP hướng dẫn Luật Đất đai','patterns':['102_2024_nd-cp','102/2024']},
 {'id':'land_finance_decree_103','name':'Nghị định 103/2024/NĐ-CP tiền sử dụng đất/tiền thuê đất','patterns':['103_2024_nd-cp','103/2024']},
 {'id':'land_price_decree_71','name':'Nghị định 71/2024/NĐ-CP về giá đất','patterns':['71_2024_nd-cp','71/2024','giá đất']},
 {'id':'housing_decree','name':'Nghị định hướng dẫn Luật Nhà ở 2023','patterns':['95_2024','nhà ở','chung cư']},
 {'id':'reb_decree_96','name':'Nghị định 96/2024/NĐ-CP hướng dẫn Luật Kinh doanh BĐS','patterns':['96_2024_nd-cp','96/2024','kinh doanh bất động sản']},
 {'id':'investment_decree','name':'Nghị định hướng dẫn Luật Đầu tư/chấp thuận chủ trương','patterns':['31_2021_nd','96_2026_nd-cp','chấp thuận chủ trương đầu tư']},
 {'id':'bidding_investor_decree_274','name':'Nghị định 274/2026/NĐ-CP lựa chọn nhà đầu tư dự án đầu tư kinh doanh','patterns':['274_2026','274/2026']},
 {'id':'environment_law_decree','name':'Luật/Nghị định môi trường ĐTM/GPMT','patterns':['bảo vệ môi trường','đánh giá tác động môi trường','giấy phép môi trường']},
 {'id':'pccc_law_decree','name':'Luật/Nghị định PCCC thẩm duyệt/nghiệm thu','patterns':['pccc','phòng cháy','chữa cháy']},
 {'id':'construction_decree','name':'Nghị định quản lý dự án đầu tư xây dựng/GPXD/nghiệm thu','patterns':['15_2021','175_2024','giấy phép xây dựng','quản lý dự án đầu tư xây dựng']},
 {'id':'bank_guarantee_circular','name':'Thông tư NHNN bảo lãnh nhà ở hình thành trong tương lai','patterns':['49_2024_tt-nhnn','bảo lãnh','nhnn']},
 {'id':'land_registration_circular','name':'Thông tư BTNMT hồ sơ đất đai/đăng ký đất đai/GCN','patterns':['10_2024_tt-btnmt','08_2024_tt-btnmt','09_2024_tt-btnmt','đăng ký đất đai','giấy chứng nhận']},
 {'id':'finance_circular','name':'Thông tư BTC tài chính đất/thuế/phí/lệ phí','patterns':['tt-btc','tiền sử dụng đất','tiền thuê đất','lệ phí']},
]

def hit(target,item):
    hay=(item['file']+' '+item['title']+' '+item.get('detected_number','')+' '+ ' '.join(item.get('groups',[]))).lower()
    return any(p.lower() in hay for p in target['patterns'])
results=[]
for t in targets:
    matches=[i for i in local if hit(t,i)]
    results.append({**t,'status':'provided' if matches else 'missing_or_uncertain','matches':[{'file':m['file'],'title':m['title'],'groups':m['groups']} for m in matches[:8]]})
(deep/'SOURCE_GAP_ANALYSIS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Source gap analysis — dùng cái anh đã cung cấp, chỉ bổ sung phần thiếu','']
md.append('## Đã có / khả năng đã có trong 61 file local')
for r in results:
    if r['status']=='provided':
        md.append(f"### {r['name']}")
        for m in r['matches'][:5]: md.append(f"- `{m['file']}` — {m['title']}")
        md.append('')
md.append('## Thiếu hoặc chưa chắc, cần research/bổ sung')
for r in results:
    if r['status']!='provided': md.append(f"- **{r['name']}** (`{r['id']}`) — cần tìm/bổ sung")
md.append('')
md.append('## Nguyên tắc tiếp theo')
md.append('- Không research lại văn bản đã có file local, trừ khi cần kiểm tra hiệu lực/sửa đổi.')
md.append('- Chỉ đi tìm văn bản thiếu hoặc chưa chắc.')
md.append('- Sau khi bổ sung nguồn, mới trích điều/khoản/điểm theo từng gate dự án.')
(deep/'SOURCE_GAP_ANALYSIS.md').write_text('\n'.join(md),encoding='utf-8')
print('provided',sum(1 for r in results if r['status']=='provided'),'missing',sum(1 for r in results if r['status']!='provided'))
