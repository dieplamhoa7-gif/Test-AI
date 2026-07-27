import json,re,unicodedata
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parent
MAN=BASE/'manual_10parts'; WEB=BASE/'web'
RAW_CHUNKS=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
def chunk_texts(ids):
    out=[]
    for c in ids or []:
        try: i=int(c)-1
        except Exception: continue
        if 0 <= i < len(RAW_CHUNKS):
            txt=(RAW_CHUNKS[i].get('text') or '').strip()
            if txt and txt not in out: out.append(txt)
    return '\n\n--- chunk ---\n\n'.join(out)

def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    s=re.sub(r'\b(du an|khu|kdc|kdt|khu do thi|khu dan cu|chung cu|cum|cong nghiep|ccn|kcn|resort|khach san|toa nha|quy dat|lo|dat|cap nhat|bao cao|phuong an|project)\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s).strip()
    return ' '.join(w for w in s.split() if len(w)>1)

def canon(name):
    n=norm(name)
    rules=[
      ('long thuan long phuoc quan', '10ha Đường Long Thuận, Long Phước, Quận 9'),
      ('vinh phu gan phu quang', '12ha KDC Vĩnh Phú gần Phú Quang'),
      ('vo thi sau bien hoa', '2,1ha Võ Thị Sáu, Biên Hòa'),
      ('ba keo phu quoc', 'Dự án Bà Kèo, Phú Quốc'),
      ('cat lai sky habitat', 'Cát Lái - Sky Habitat / H2-02'),
      ('hoi an riverside', 'Hội An Riverside Resort & Spa'),
      ('phu quang', 'Dự án Phú Quang'),
      ('phuong hoang', 'Dự án Phượng Hoàng'),
      ('353 no trang long', '353 Nơ Trang Long, Bình Thạnh'),
      ('48 nguyen thien thuat', '48 Nguyễn Thiện Thuật, Nha Trang'),
      ('50ha vinh tuong yen lac', '50ha Vĩnh Tường - Yên Lạc, Vĩnh Phúc'),
      ('2769m2 hoang sa', '2.769m2 Hoàng Sa, Đà Nẵng'),
      ('769m2 hoang sa', '2.769m2 Hoàng Sa, Đà Nẵng'),
      ('an phu pg', 'KĐT An Phú - PG'),
      ('an ton', 'KDC An Tôn'),
      ('asia phu my binh chanh', 'Asia Phú Mỹ - Bình Chánh'),
      ('tay thanh tan phu', 'Khu đất Tây Thạnh, Tân Phú'),
      ('1691 3n quoc lo 1a', '1691/3N Quốc lộ 1A, An Phú Đông, Q12'),
      ('kien giang ckg', 'Khu đất 35ha/38,8ha Kiên Giang - CKG'),
      ('phu tho hoa quan tan phu', 'Khu đất Phú Thọ Hòa, Tân Phú'),
      ('102ha phuoc an nhon trach', 'Đấu giá 102ha Phước An, Nhơn Trạch'),
      ('can ho dich vu quan', 'Căn hộ dịch vụ Quận 2 khoảng 1,1ha'),
      ('386ha nhon trach', 'Cụm dự án đấu thầu 386ha Nhơn Trạch'),
      ('pk kq 46ha bien hoa', 'Khu gia đình quân nhân PK-KQ 8,46ha Biên Hòa'),
      ('vo van kiet', 'Dự án Võ Văn Kiệt'),
      ('green hill quy nhon', 'Green Hill, Quy Nhơn'),
      ('greenhill village quy nhon', 'Green Hill, Quy Nhơn'),
      ('hoa vien vinh thanh', 'Hoa viên Vĩnh Thanh'),
      ('holiday beach', 'Holiday Beach Đà Nẵng'),
      ('thai hoa lien son lien hoa vinh phuc', 'KCN Thái Hòa - Liễn Sơn - Liên Hòa, Vĩnh Phúc'),
      ('dong a premier', 'Khách sạn Đông Á Premier, Nha Trang'),
      ('tan mai danh sach dau gia dong nai', 'Khu nhà ở Tân Mai - đấu giá Đồng Nai'),
      ('richland quan', 'Richland Quận 9'),
      ('serene da nang', 'Serene Đà Nẵng'),
      ('hau nghia duc hoa', 'KĐT mới Hậu Nghĩa - Đức Hòa'),
      ('truong thinh tran nao', 'Chung cư Trường Thịnh, Trần Não'),
      ('xuan cau lach huyen', 'KCN/Khu phi thuế quan Xuân Cầu - Lạch Huyện'),
      ('van phong an phu', 'Văn phòng / Chung cư An Phú'),
      ('197 le van sy', '197 Lê Văn Sỹ, Quận 3'),
      ('viet an thuan giao', 'Cao tầng Việt An, Thuận Giao'),
      ('nguyen huu tho nha be', 'Nguyễn Hữu Thọ, Nhà Bè'),
      ('giao yen giao thuy nam', 'CCN Giao Yến, Giao Thủy, Nam Định'),
      ('dong trung', 'Dự án Đông Trung, Bình Dương'),
      ('felicia da nang', 'Felicia Đà Nẵng'),
      ('fenica', 'Dự án Fenica'),
      ('phu gia khiem', 'Phú Gia Khiêm / PGK'),
      ('120 dang van bi thu duc', 'Khu đất 4.600 m2 tại 120 Đặng Văn Bi, Thủ Đức'),
      ('dang van bi thu duc', 'Khu đất 4.600 m2 tại 120 Đặng Văn Bi, Thủ Đức'),
      ('ngo chi quoc binh chieu', 'Ngô Chí Quốc, Bình Chiểu, Thủ Đức'),
      ('the bale', 'The Bale, Mũi Né/Phan Thiết'),
      ('bai truong phu quoc', None),
    ]
    # High-confidence duplicate aliases found by possible_duplicate_groups_audit.py
    if 'ang van bi' in n and 'thu uc' in n:
        return 'Khu đất 4.600 m2 tại 120 Đặng Văn Bi, Thủ Đức'
    if '769m2' in n and 'hoang sa' in n and 'nang' in n:
        return '2.769m2 Hoàng Sa, Đà Nẵng'
    if 'hoa xuan' in n or 'oa xuan' in n:
        return 'Chung cư Hòa Xuân A2-3 & A2-4'
    if '72 74' in n and 'vo thi sau' in n:
        return 'Khu đất/văn phòng 72-74 Võ Thị Sáu, Tân Định, Quận 1'
    if '1ha' in n and 'son tra' in n and 'nang' in n:
        return 'Dự án 1ha Sơn Trà, Đà Nẵng'
    if 'giao yen' in n and 'giao thuy' in n and 'nam' in n:
        return 'CCN Giao Yến, Giao Thủy, Nam Định'
    if 'ong trung' in n and ('thuan an' in n or 'binh duong' in n or n.strip() == 'ong trung'):
        return 'Dự án Đông Trung, Thuận An/Bình Dương'
    if 'felicia' in n and 'nhom' not in n and 'b11' not in n and 'serence' not in n and 'phu hai' not in n:
        return 'Felicia Đà Nẵng - tổ hợp khách sạn và condotel'
    for needle,label in rules:
        if needle in n and label: return label
    return name.strip()

def date_key(r): return r.get('report_date') or '9999-99-99'


def generic_financial_lines(text, chunk='', existing=None):
    txt=text or ''
    existing_blob=' '.join((x.get('label','')+' '+x.get('value','')) for x in (existing or [])).lower()
    keys=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất)',re.I)
    bad=re.compile(r'^(by |message by|translate|edited|image by|image$)',re.I)
    out=[]
    candidates=[re.sub(r'\s+',' ',x).strip(' -•\t') for x in txt.splitlines()]
    # Some Teams exports collapse report bullets into long paragraphs. Split those into compact evidence sentences too.
    blob=re.sub(r'\s+',' ',txt)
    candidates += [x.strip(' -•\t') for x in re.split(r'(?<=[.;:])\s+(?=[A-ZÀ-Ỵ0-9+\-])|\s+(?=\d+[/.]\s)|\s+(?=[IVX]+/)', blob)]
    seen=set()
    for line in candidates:
        if line in seen: continue
        seen.add(line)
        if len(line)<18 or bad.search(line): continue
        if len(line)>360: line=line[:357].rstrip()+ '…'
        if not keys.search(line): continue
        low=line.lower()
        if low in existing_blob: continue
        # keep dense numeric/financial evidence, skip generic narrative unless it has a number
        if not re.search(r'\d', line): continue
        label='Dòng số liệu từ nguồn'
        if re.search(r'IRR|NPV|LNTT|LNST|hiệu quả|khả thi', line, re.I): label='Hiệu quả / FS từ nguồn'
        elif re.search(r'giá bán|giá chào|giá đất|giá đấu|tr/m2|triệu/m2', line, re.I): label='Giá / đơn giá từ nguồn'
        elif re.search(r'chi phí|vốn|lãi vay|tổng mức đầu tư|tiền sử dụng đất|TMĐT|TMDT', line, re.I): label='Chi phí / vốn từ nguồn'
        item={'label':label,'value':line,'source_chunk':str(chunk)}
        if item['value'].lower() not in [x.get('value','').lower() for x in out]: out.append(item)
        if len(out)>=12: break
    return out

def scenario_items(text, chunk=''):
    txt=text or ''
    out=[]
    m=re.search(r'3\.\s*Hiệu quả(.*?)(?:\n\s*4\.\s*Đề xuất|$)', txt, flags=re.S|re.I)
    if not m: return out
    block=m.group(1)
    lot=''; debt=''
    sale=''
    for raw in block.splitlines():
        line=raw.strip()
        if not line: continue
        lm=re.match(r'[ab]\)\s*(Lô\s*A\d+)', line, flags=re.I)
        if lm: lot=lm.group(1); continue
        if line.lower().startswith('trường hợp'):
            debt=line; continue
        sm=re.search(r'Giả định giá bán căn hộ:\s*([^:]+):?', line, flags=re.I)
        if sm: sale=sm.group(1).strip(); continue
        if 'Giá đấu giá max' in line and 'LNTT' in line:
            irr=re.search(r'IRR\s*([\d,.]+)%', line, flags=re.I)
            price=re.search(r'Giá đấu giá max:\s*([^\(,]+)', line, flags=re.I)
            land=re.search(r'tổng giá trị đất:\s*([^\)]+)', line, flags=re.I)
            margin=re.search(r'LNTT/TMĐT:\s*([\d,.]+%)', line, flags=re.I)
            label=' · '.join(x for x in [lot, debt, ('giá bán '+sale if sale else '')] if x)
            val='; '.join(x for x in [
                ('IRR mục tiêu '+irr.group(1)+'%' if irr else ''),
                ('giá đấu max '+price.group(1).strip() if price else ''),
                ('tổng đất '+land.group(1).strip() if land else ''),
                ('LNTT/TMĐT '+margin.group(1) if margin else '')
            ] if x)
            if label and val: out.append({'label':'Kịch bản hiệu quả - '+label,'value':val,'source_chunk':str(chunk)})
    return out


records=[]; reviews=[]
for fp in sorted(MAN.glob('part_*_manual_records.json')):
    d=json.loads(fp.read_text(encoding='utf-8')); part=d.get('part')
    for r in d.get('records',[]):
        rr=dict(r); rr['part']=part; rr['canonical_project_name']=canon(rr.get('project_name',''))
        records.append(rr)
    reviews += [{**x,'part':part} for x in d.get('review_or_skip',[])]

groups={}
for r in records:
    groups.setdefault(r['canonical_project_name'],[]).append(r)

merged=[]
for i,(name,rs) in enumerate(sorted(groups.items(), key=lambda kv: norm(kv[0])),1):
    rs=sorted(rs, key=lambda r:(date_key(r), r.get('part',0), r.get('id','')))
    financial=[]; chunks=[]; decisions=set(); locations=[]; maps=[]
    reports=[]
    for idx,r in enumerate(rs,1):
        fin=list(r.get('financial_items') or [])
        rawtxt=chunk_texts(r.get('source_chunks',[]))
        fin += scenario_items(rawtxt, (r.get('source_chunks') or [''])[0])
        fin += generic_financial_lines(rawtxt, (r.get('source_chunks') or [''])[0], fin)
        financial += [{**x,'record_id':r.get('id'),'report_no':idx,'project_name':r.get('project_name'),'part':r.get('part')} for x in fin]
        chunks += [str(c) for c in r.get('source_chunks',[])]
        decisions.add(r.get('decision',''))
        if r.get('location'): locations.append(r['location'])
        if r.get('map_url'): maps.append(r['map_url'])
        reports.append({
            'report_no': idx, 'record_id': r.get('id'), 'part': r.get('part'), 'project_name_original': r.get('project_name',''),
            'decision': r.get('decision',''), 'report_date': r.get('report_date',''), 'source_chunks': r.get('source_chunks',[]),
            'source_file': r.get('source_file',''), 'sender': r.get('sender',''), 'location': r.get('location',''), 'map_url': r.get('map_url',''),
            'scale': r.get('scale',''), 'legal_planning': r.get('legal_planning',''), 'business_notes': r.get('business_notes',''),
            'financial_items': fin, 'excerpt': r.get('excerpt',''), 'full_excerpt': chunk_texts(r.get('source_chunks',[]))
        })
    merged.append({
        'master_id': f'G{i:04d}', 'project_name': name, 'report_count': len(rs), 'parts': sorted(set(r.get('part') for r in rs)),
        'first_date': reports[0].get('report_date',''), 'latest_date': reports[-1].get('report_date',''),
        'source_chunks': sorted(set(chunks), key=lambda x:int(x) if x.isdigit() else 99999),
        'location': locations[-1] if locations else '', 'map_url': maps[-1] if maps else '',
        'decisions': sorted(x for x in decisions if x), 'financial_items': financial, 'reports': reports
    })

final={'generated_at':datetime.now().isoformat(timespec='seconds'),'groups':merged,'review':reviews,'totals':{'groups':len(merged),'raw_records':len(records),'multi_report_groups':sum(1 for g in merged if g['report_count']>1),'financial_groups':sum(1 for g in merged if g['financial_items']),'financial_items':sum(len(g['financial_items']) for g in merged),'review':len(reviews)}}
(MAN/'manual_records_merged_reports.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
(WEB/'manual_records_merged_reports.js').write_text('window.MANUAL_MERGED_REPORTS_DB = '+json.dumps(final,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print(json.dumps(final['totals'],ensure_ascii=False))
