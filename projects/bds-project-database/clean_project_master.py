from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master.json',encoding='utf-8'))
ALIASES={
 'cao tầng với tổng diện tích đất là 5':'Cao tầng 31 Trần Não',
 'Trần Đức 1 (2':'Trần Đức 1 2.8ha Thuận Giao',
 'Diamond Garden ở đường Đào Trí':'Diamond Garden Đào Trí Phú Thuận',
 'Khách sạn 5 sao tại đường 12 Hùng Vương':'Khách sạn 5 sao 12 Hùng Vương Đà Lạt',
 'nhà ở':'Lô đất Phú Thọ Hòa Tân Phú',
 '(nguồn anh Hùng)':'Lô mặt tiền Quốc Lộ 13 Hiệp Bình Phước',
 'có lợi thế vị trí khi cách ga Metro Bình Thái khoảng 700m':'Urban Green / Bình Thái',
 'H2-02':'Cát Lái Sky Habitat H2-02',
 'H2-02 (Sky Habitat) thuộc KDC Cát Lái I':'Cát Lái Sky Habitat H2-02',
 'Bà Kèo':'Bãi Kèo Phú Quốc',
 'Bào Kèo':'Bãi Kèo Phú Quốc',
 '10ha Đường Long Thuận':'Long Thuận Long Phước Quận 9 10ha',
 'đường Ngô Chí Quốc':'Khu đất Ngô Chí Quốc Bình Chiểu Thủ Đức',
}
BAD_PREFIX=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|như sau$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ|mention|một lần|không phải|xác nhận|để hiệu quả)',re.I)

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def norm(s):
 s=clean(s).lower(); s=re.sub(r'^(dự án|da|khu đất|lô đất)\s+','',s); s=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',s); return clean(s)
def infer_from_excerpt(ex):
 pats=[r'dự án\s+([^,.\n:;]{4,90})',r'DA\s+([^,.\n:;]{4,90})',r'khu đất\s+([^,.\n:;]{4,90})',r'lô đất\s+([^,.\n:;]{4,90})',r'khách sạn\s+([^,.\n:;]{4,90})']
 for p in pats:
  m=re.search(p,ex or '',re.I)
  if m:
   c=clean(m.group(1)).strip(' -:;,.')
   if c and len(c)>4 and not BAD_PREFIX.search(c): return c[:120]
 return ''
for r in masters:
 old=clean(r.get('project_name'))
 new=ALIASES.get(old,old)
 if not new or BAD_PREFIX.search(new) or len(new)<5:
  inferred=infer_from_excerpt(r.get('source_excerpt',''))
  if inferred: new=ALIASES.get(inferred,inferred)
 # trim sentence tails
 new=re.sub(r'\s+(như sau|theo phương án.*|với các giả định.*)$','',new,flags=re.I).strip(' -:;,.')
 r['project_name_raw']=old
 r['project_name']=new[:140] if new else old
 r['clean_key']=norm(r['project_name'])
# merge exact clean_key + coordinate again after name cleaning
merged={}
for r in masters:
 coord=''
 if r.get('latitude') and r.get('longitude'):
  try: coord=f"{round(float(r['latitude']),5)},{round(float(r['longitude']),5)}"
  except: coord=f"{r.get('latitude')},{r.get('longitude')}"
 key=(r.get('clean_key',''),coord)
 if key not in merged:
  merged[key]=r
 else:
  a=merged[key]
  a['mention_count']=int(a.get('mention_count') or 0)+int(r.get('mention_count') or 0)
  for f in ['source_files','senders','map_urls','land_area','planning_summary','legal_summary','asking_price','price_mentions','selling_price','land_cost','total_investment','revenue','profit','irr','npv','risks','next_actions','attachments']:
   vals=[]
   for v in [a.get(f,''),r.get(f,'')]:
    for p in re.split(r';\s*',clean(v)):
     if p and p not in vals: vals.append(p)
   a[f]='; '.join(vals)[:1200]
  dates=[d for d in [a.get('first_report_date'),a.get('latest_report_date'),r.get('first_report_date'),r.get('latest_report_date')] if d]
  if dates:
   a['first_report_date']=min(dates); a['latest_report_date']=max(dates)
  if r.get('source_excerpt') and r.get('source_excerpt') not in a.get('source_excerpt',''):
   a['source_excerpt']=(a.get('source_excerpt','')+'\n\n---\n\n'+r.get('source_excerpt',''))[:5000]
out=list(merged.values())
out.sort(key=lambda x:(not bool(x.get('latitude') and x.get('longitude')),-int(x.get('data_completeness_score') or 0),x.get('project_name','')))
for i,r in enumerate(out,1): r['master_id']=f'BDS-MASTER-{i:04d}'
fields=list(out[0].keys()) if out else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(out)
(base/'project_popup_master_clean.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print({'input':len(masters),'clean_master':len(out),'with_coords':sum(1 for r in out if r.get('latitude') and r.get('longitude')),'out':str(base/'project_popup_master_clean.csv')})
