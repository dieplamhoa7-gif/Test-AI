import re,json,pathlib,collections
src=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx")
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\deep_research")

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
# legal topic model for BDS development process
topics={
 'planning': ['quy hoạch','quy hoạch chi tiết','quy hoạch đô thị','chương trình phát triển nhà ở','kế hoạch phát triển nhà ở','chỉ tiêu quy hoạch'],
 'investment_policy': ['chấp thuận chủ trương đầu tư','quyết định chủ trương đầu tư','chấp thuận nhà đầu tư','dự án đầu tư'],
 'investor_selection': ['lựa chọn nhà đầu tư','đấu thầu lựa chọn nhà đầu tư','đấu giá quyền sử dụng đất','nhà đầu tư quan tâm','mời quan tâm'],
 'land_recovery_compensation': ['thu hồi đất','bồi thường','hỗ trợ tái định cư','giải phóng mặt bằng'],
 'land_allocation_conversion': ['giao đất','cho thuê đất','chuyển mục đích sử dụng đất','đăng ký đất đai'],
 'land_finance': ['tiền sử dụng đất','tiền thuê đất','giá đất','bảng giá đất','nghĩa vụ tài chính'],
 'environment_fire_infra': ['đánh giá tác động môi trường','giấy phép môi trường','phòng cháy chữa cháy','pccc','đấu nối hạ tầng'],
 'construction': ['giấy phép xây dựng','thẩm định thiết kế','thiết kế cơ sở','khởi công','nghiệm thu công trình'],
 'real_estate_business': ['bất động sản hình thành trong tương lai','đủ điều kiện bán','huy động vốn','bảo lãnh ngân hàng','hợp đồng mua bán'],
 'certificate_handover_operation': ['cấp giấy chứng nhận','bàn giao nhà','quản lý vận hành','bảo trì','nhà chung cư']
}
articles=[]
for p in src.glob('*.md'):
    text=p.read_text(encoding='utf-8',errors='ignore')
    ms=list(re.finditer(r'(?m)^\s*(Điều\s+\d+[a-zA-Z]?\.\s+[^\n]+)', text))
    title=next((clean(re.sub(r'^#+\s*','',l)) for l in text.splitlines() if clean(l)), p.stem)
    for i,m in enumerate(ms):
        end=ms[i+1].start() if i+1<len(ms) else min(len(text),m.start()+7000)
        block=text[m.start():end]
        low=block.lower()
        scores={k:sum(1 for kw in kws if kw in low) for k,kws in topics.items()}
        hits=[k for k,v in scores.items() if v]
        if hits:
            articles.append({'file':p.name,'doc_title':title[:220],'article':clean(m.group(1)),'topics':hits,'score':sum(scores.values()),'summary_source':clean(block[len(m.group(1)):])[:900],'quote':clean(block)[:1800]})
# top articles per topic
by=collections.defaultdict(list)
for a in articles:
    for t in a['topics']: by[t].append(a)
report=[]
report.append('# Deep research: Quy trình phát triển dự án BĐS')
report.append('')
report.append(f'- Tổng số điều khoản match chủ đề: {len(articles)}')
report.append('')
for t in topics:
    arr=sorted(by[t], key=lambda x:-x['score'])[:20]
    report.append(f'## {t}')
    for a in arr[:10]:
        report.append(f"- **{a['article']}** — `{a['file']}`")
        report.append(f"  - Tóm tắt nguồn: {a['summary_source'][:350]}")
    report.append('')
(out/'article_topic_index.json').write_text(json.dumps({'topics':topics,'articles':articles},ensure_ascii=False,indent=2),encoding='utf-8')
(out/'DEEP_RESEARCH_INDEX.md').write_text('\n'.join(report),encoding='utf-8')
print('articles',len(articles),'topics', {k:len(v) for k,v in by.items()})
