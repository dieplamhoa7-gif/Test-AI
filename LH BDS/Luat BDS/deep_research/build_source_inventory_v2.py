import json, pathlib, re
base=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS")
src=base/'_converted_md_from_docx'; deep=base/'deep_research'
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def good_title(lines, stem):
    for l in lines[:120]:
        x=clean(re.sub(r'^#+\s*','',l))
        if not x or x in ('---','--','___'): continue
        if re.search(r'^(LUẬT|NGHỊ ĐỊNH|THÔNG TƯ|NGHỊ QUYẾT|QUYẾT ĐỊNH)\b', x, re.I): return x
        if re.search(r'(Luật|Nghị định|Thông tư|Nghị quyết|Quyết định)\s+số', x, re.I): return x
    for l in lines[:120]:
        x=clean(re.sub(r'^#+\s*','',l))
        if x and x not in ('---','--','___'): return x[:300]
    return stem
items=[]
for p in sorted(src.glob('*.md')):
    text=p.read_text(encoding='utf-8',errors='ignore')
    lines=text.splitlines()
    title=good_title(lines,p.stem)
    head='\n'.join(lines[:220])
    num=''
    m=re.search(r'(Luật|Nghị định|Thông tư|Nghị quyết|Quyết định)\s+số\s*[:：]?\s*([^\n\r]+)', head, re.I)
    if m: num=clean(m.group(0))[:160]
    items.append({'file':p.name,'title':title,'detected_number':num,'size':p.stat().st_size})
(deep/'local_source_inventory_v2.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Local source inventory v2','',f'Tổng file: {len(items)}','']
for it in items:
    md += [f"## {it['file']}", f"- Title: {it['title']}", f"- Number: {it['detected_number'] or 'chưa detect'}", '']
(deep/'LOCAL_SOURCE_INVENTORY_V2.md').write_text('\n'.join(md),encoding='utf-8')
print('wrote',len(items))
