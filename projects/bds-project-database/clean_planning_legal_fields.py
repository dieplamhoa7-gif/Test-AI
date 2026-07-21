from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def uniq(vals,limit=10):
    out=[]
    for v in vals:
        for p in re.split(r';\s*',clean(v)):
            p=p.strip(' -;,.')
            if p and p not in out: out.append(p)
    return '; '.join(out[:limit])
def all_match(pat,text,limit=8):
    vals=[]
    for m in re.finditer(pat,text or '',re.I):
        v=clean(m.group(0))
        if v and v not in vals: vals.append(v)
        if len(vals)>=limit: break
    return '; '.join(vals)
for r in masters:
    text=' '.join(clean(r.get(k,'')) for k in ['planning_summary','legal_summary','legal_status','source_excerpt'])
    r['far_clean']=uniq([r.get('far',''), all_match(r'(?:HSSDĐ|HS SDĐ|hệ số(?: sử dụng đất)?)[^\n.;]{0,45}?\d+[\.,]?\d*',text,8)])
    r['max_floors_clean']=uniq([r.get('max_floors',''), all_match(r'(?:cao|tầng cao|quy mô|xây dựng)[^\n.;]{0,45}?\d+\s*tầng',text,8)])
    r['population_clean']=uniq([r.get('population',''), all_match(r'(?:dân số|dân)[^\n.;]{0,60}?\d+[\.,]?\d*',text,8)])
    r['density_clean']=uniq([r.get('building_density',''), all_match(r'(?:mật độ|MĐXD)[^\n.;]{0,45}?\d+[\.,]?\d*%?',text,8)])
    r['planning_doc_status']=uniq([all_match(r'(?:1/500|1/2000|quy hoạch phân khu|QHCT|phê duyệt quy hoạch|điều chỉnh quy hoạch)[^\n.;]{0,160}',text,10)])
    r['gpm_status']=uniq([all_match(r'(?:GPMB|giải phóng mặt bằng|bồi thường)[^\n.;]{0,160}',text,8)])
    r['lur_status']=uniq([all_match(r'(?:LUR|tiền sử dụng đất|TSDĐ|nghĩa vụ tài chính|tiền sd đất)[^\n.;]{0,180}',text,10)])
    r['approval_status']=uniq([all_match(r'(?:chủ trương đầu tư|giao đất|thuê đất|giấy chứng nhận|GCN|đấu giá|quyết định|phê duyệt)[^\n.;]{0,180}',text,12)])
    # overwrite compatibility fields with clean values where present
    if r['far_clean']: r['far']=r['far_clean']
    if r['max_floors_clean']: r['max_floors']=r['max_floors_clean']
    if r['population_clean']: r['population']=r['population_clean']
    if r['density_clean']: r['building_density']=r['density_clean']
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'rows':len(masters),'far':sum(1 for r in masters if r.get('far_clean')),'floors':sum(1 for r in masters if r.get('max_floors_clean')),'legal_doc':sum(1 for r in masters if r.get('approval_status') or r.get('lur_status'))})
