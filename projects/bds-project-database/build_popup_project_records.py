from pathlib import Path
import csv,json,re,hashlib
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
web=base/'web'; web.mkdir(exist_ok=True)

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def first(pattern,text,flags=re.I):
    m=re.search(pattern,text or '',flags)
    return clean(m.group(1) if m and m.groups() else (m.group(0) if m else ''))
def all_unique(pattern,text,flags=re.I,limit=18):
    vals=[]
    for m in re.finditer(pattern,text or '',flags):
        v=clean(m.group(1) if m.groups() else m.group(0))
        if v and v not in vals: vals.append(v)
    return '; '.join(vals[:limit])
def score_fields(r):
    keys=['project_name','report_date','map_urls','coordinates','location','land_area','project_type','planning_summary','legal_summary','asking_price','selling_price','total_investment','revenue','profit','irr','npv','risks']
    filled=sum(1 for k in keys if clean(r.get(k,'')))
    return round(filled/len(keys)*100)

def infer_name(text,hint=''):
    hint=clean(hint)
    bad=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|cao tầng$|nhà ở$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ)',re.I)
    aliases={'Trần Đức 1 (2':'Trần Đức 1 2.8ha Thuận Giao','(nguồn anh Hùng)':'Lô mặt tiền Quốc Lộ 13 Hiệp Bình Phước','nhà ở':'Lô đất Phú Thọ Hòa Tân Phú','Diamond Garden ở đường Đào Trí':'Diamond Garden Đào Trí Phú Thuận','Khách sạn 5 sao tại đường 12 Hùng Vương':'Khách sạn 5 sao 12 Hùng Vương Đà Lạt'}
    if hint in aliases: return aliases[hint]
    if hint and not bad.search(hint): return hint[:120]
    pats=[r'dự án\s+([^,.\n:;]{4,110})',r'DA\s+([^,.\n:;]{4,110})',r'khu đất\s+([^,.\n:;]{4,110})',r'lô đất\s+([^,.\n:;]{4,110})',r'khách sạn\s+([^,.\n:;]{4,110})']
    for p in pats:
        m=re.search(p,text or '',re.I)
        if m:
            cand=clean(m.group(1)).strip(' -:;,.')
            if cand and not bad.search(cand): return aliases.get(cand,cand)[:120]
    return hint[:120] or 'Chưa đặt tên'

# map coords
res=json.load(open(base/'map_link_resolution_all.json',encoding='utf-8')) if (base/'map_link_resolution_all.json').exists() else []
coord={x['url']:(x.get('lat'),x.get('lng')) for x in res if x.get('lat') and x.get('lng')}
mentions=list(csv.DictReader(open(base/'project_mentions_from_teams_full.csv',encoding='utf-8-sig',newline='')))
records=[]
for i,m in enumerate(mentions,1):
    text=m.get('excerpt') or ''
    maps=[u.strip() for u in re.split(r';\s*',m.get('map_urls','') or '') if u.strip()]
    lat=lng=''
    for u in maps:
        if u in coord: lat,lng=coord[u]; break
    name=infer_name(text,m.get('project_name_hint',''))
    # keep all project-like records, with or without coords; popup can be used in table too
    rec={
        'record_id':m.get('mention_id') or f'TEAMS-POPUP-{i:04d}',
        'project_name':name,
        'source_chat':m.get('source_chat','Bee || Phân Tích Đầu Tư'),
        'source_file':m.get('source_file',''),
        'chunk_id':m.get('chunk_id',''),
        'report_date':m.get('report_date',''),
        'report_datetime_raw':m.get('report_datetime_raw',''),
        'sender':m.get('sender',''),
        'map_urls':m.get('map_urls',''),
        'latitude':lat,
        'longitude':lng,
        'coordinates':f'{lat}, {lng}' if lat and lng else '',
        'location': first(r'(?:Vị trí|vị trí|Địa chỉ|địa chỉ)[:：]?\s*([^\n]{8,220})',text),
        'province_city': first(r'\b(TP\.?HCM|TP Hồ Chí Minh|Hồ Chí Minh|Đà Nẵng|Đồng Nai|Bình Dương|Bà Rịa[^,.;\n]*|Vĩnh Phúc|Đà Lạt|Phú Quốc|Quảng Nam|Long An)\b',text),
        'district_area': first(r'\b(Quận\s*\d+|Q\.\s*\d+|TP\.\s*Thủ Đức|Thủ Đức|Nhơn Trạch|Long Thành|Biên Hòa|Thuận Giao|Tân Phú|Ngũ Hành Sơn|Hội An|Đà Lạt|Phú Quốc)[^,.;\n]{0,80}',text),
        'land_area': m.get('land_area_mentions','') or all_unique(r'\b\d+[\.,]?\d*\s*(?:ha|m2|m²)\b',text),
        'project_type': first(r'\b(căn hộ|chung cư|cao tầng|thấp tầng|resort|khách sạn|condotel|khu công nghiệp|KCN|văn phòng|nhà phố|biệt thự|đất nền|TMDV|TMĐT)\b',text),
        'land_type': first(r'(?:loại đất|MĐSDĐ|mục đích)[^\n:：]{0,35}[:：]?\s*([^\n]{5,160})',text),
        'planning_summary': all_unique(r'(?:quy hoạch|QH|1/500|1/2000|tầng cao|HSSDĐ|HS SDĐ|hệ số|mật độ|dân số)[^\n]{0,180}',text,limit=12),
        'max_floors': all_unique(r'(?:cao|tầng cao|quy mô)[^\n]{0,30}?\d+\s*tầng',text,limit=6),
        'far': m.get('far_mentions','') or all_unique(r'(?:HSSDĐ|HS SDĐ|hệ số(?: sử dụng đất)?)[^\n,.]{0,50}?\d+[\.,]?\d*',text),
        'building_density': all_unique(r'(?:mật độ|MĐXD)[^\n,.]{0,40}?\d+[\.,]?\d*%?',text),
        'population': m.get('population_mentions','') or all_unique(r'(?:dân số|dân)[^\n,.]{0,50}?\d+[\.,]?\d*',text),
        'legal_summary': all_unique(r'(?:pháp lý|GPMB|chủ trương|1/500|quyết định|giấy chứng nhận|GCN|LUR|tiền sử dụng đất|đấu giá|giao đất|thuê đất)[^\n]{0,220}',text,limit=14),
        'legal_status': first(r'(?:pháp lý[^\n]{0,80}|GPMB[^\n]{0,80}|đã được[^\n]{0,120}|chưa[^\n]{0,120})',text),
        'asking_price': all_unique(r'(?:giá chào|giá mua|giá vốn|giá bán dự án|M&A|chào bán)[^\n]{0,120}?\d+[\.,]?\d*\s*(?:tỷ|tr/m2|triệu/m2|tr\/m2)?',text,limit=10),
        'price_mentions': m.get('price_mentions',''),
        'selling_price': all_unique(r'(?:giá bán|đơn giá bán|giá căn hộ|giá phòng|giá kinh doanh)[^\n]{0,140}?\d+[\.,]?\d*\s*(?:tr/m2|triệu/m2|tỷ|USD|triệu)',text,limit=10),
        'land_cost': all_unique(r'(?:tiền đất|chi phí đất|giá vốn đất|TSDĐ|tiền sử dụng đất|LUR)[^\n]{0,140}?\d+[\.,]?\d*\s*tỷ?',text,limit=10),
        'total_investment': all_unique(r'(?:tổng mức đầu tư|TMĐT|tổng chi phí|chi phí đầu tư)[^\n]{0,140}?\d+[\.,]?\d*\s*tỷ?',text,limit=10),
        'revenue': all_unique(r'(?:doanh thu|DT)[^\n]{0,140}?\d+[\.,]?\d*\s*tỷ?',text,limit=10),
        'profit': all_unique(r'(?:LNTT|LNST|lợi nhuận|gross profit|PBT)[^\n]{0,120}?-?\s*\d+[\.,]?\d*\s*tỷ?',text,limit=10),
        'irr': m.get('irr_mentions','') or all_unique(r'IRR[^\n,.]{0,45}?\d+[\.,]?\d*%?',text),
        'npv': m.get('npv_mentions','') or all_unique(r'NPV[^\n,.]{0,60}?-?\s*\d+[\.,]?\d*\s*tỷ?',text),
        'payback': all_unique(r'(?:hoàn vốn|payback)[^\n]{0,80}?\d+[\.,]?\d*\s*(?:năm|tháng)?',text),
        'risks': all_unique(r'(?:rủi ro|lưu ý|không đạt|chậm|vướng|chưa|cần làm rõ|đề xuất)[^\n]{0,220}',text,limit=14),
        'next_actions': all_unique(r'(?:đề xuất|kiến nghị|cần|tiếp tục|next)[^\n]{0,180}',text,limit=8),
        'attachments': all_unique(r'[^\n]{2,160}\.(?:pdf|xlsx|xls|docx|pptx|png|jpg|jpeg)',text,re.I,limit=12),
        'source_excerpt': text,
    }
    rec['data_completeness_score']=score_fields(rec)
    records.append(rec)
# output
fields=list(records[0].keys()) if records else []
with open(base/'project_popup_records_full.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields); w.writeheader(); w.writerows(records)
(base/'project_popup_records_full.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(web/'popup_records_data.js').write_text('window.POPUP_RECORDS = '+json.dumps(records,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'popup_records':len(records),'fields':len(fields),'with_coords':sum(1 for r in records if r['latitude'] and r['longitude']),'out':str(base/'project_popup_records_full.csv')})
