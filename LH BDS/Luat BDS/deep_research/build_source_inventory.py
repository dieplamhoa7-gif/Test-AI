import re,json,pathlib
src=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx")
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\deep_research")
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def classify(name,text):
    low=(name+' '+text[:5000]).lower()
    groups=[]
    rules={
      'đất đai':['đất đai','giao đất','cho thuê đất','giá đất','tiền sử dụng đất','đăng ký đất đai'],
      'nhà ở':['nhà ở','chung cư','phát triển nhà ở'],
      'kinh doanh bđs':['kinh doanh bất động sản','bất động sản hình thành trong tương lai'],
      'đầu tư':['đầu tư','chủ trương đầu tư','nhà đầu tư'],
      'đấu thầu/đấu giá':['đấu thầu','đấu giá','lựa chọn nhà đầu tư'],
      'xây dựng/quy hoạch':['xây dựng','quy hoạch','giấy phép xây dựng'],
      'môi trường/pccc':['môi trường','pccc','phòng cháy'],
      'tài chính/thuế/phí':['thuế','phí','lệ phí','tiền thuê đất','tiền sử dụng đất','btc'],
      'ngân hàng/bảo lãnh':['ngân hàng','bảo lãnh','nhnn']
    }
    for g,ks in rules.items():
        if any(k in low for k in ks): groups.append(g)
    return groups or ['khác/cần rà']
items=[]
for p in sorted(src.glob('*.md')):
    text=p.read_text(encoding='utf-8',errors='ignore')
    lines=[clean(re.sub(r'^#+\s*','',l)) for l in text.splitlines() if clean(l)]
    title=lines[0] if lines else p.stem
    so=''
    for l in lines[:80]:
        m=re.search(r'(Luật|Nghị định|Thông tư|Nghị quyết|Quyết định)\s+số\s+([^\s,;]+)',l,re.I)
        if m: so=m.group(0); break
    items.append({'file':p.name,'title':title[:300],'detected_number':so,'size':p.stat().st_size,'groups':classify(p.name,text),'first_lines':lines[:8]})
(out/'local_source_inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Local source inventory','',f'Tổng file: {len(items)}','']
for it in items:
    md.append(f"## {it['file']}")
    md.append(f"- Title: {it['title']}")
    md.append(f"- Number: {it['detected_number'] or 'chưa detect'}")
    md.append(f"- Groups: {', '.join(it['groups'])}")
    md.append('')
(out/'LOCAL_SOURCE_INVENTORY.md').write_text('\n'.join(md),encoding='utf-8')
print('local sources',len(items))
