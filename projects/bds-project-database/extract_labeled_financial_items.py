from pathlib import Path
import json,csv,re
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database');p=B/'project_master_curated_deduped.json';rows=json.load(open(p,encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
# Ordered from specific to broad. Keep the whole source clause so every number retains meaning.
labels=[
 ('Giá chào / chuyển nhượng',r'giá\s+(?:chào|nhận chuyển nhượng|chuyển nhượng|mua đất|gom đất)'),
 ('Giá bán căn hộ',r'giá bán\s+(?:căn hộ|chung cư)'),('Giá bán shophouse/TM',r'giá bán\s+(?:shop|shophouse|sàn thương mại|tm)'),
 ('Giá bán nhà phố/biệt thự/đất',r'giá bán\s+(?:nhà phố|biệt thự|đất|nền)'),
 ('Tiền sử dụng đất',r'tiền sử dụng đất|\btsdđ\b'),('Chi phí mua đất',r'chi phí mua đất|giá vốn đất'),
 ('Chi phí xây dựng / suất đầu tư',r'chi phí xây dựng|suất (?:đầu tư|xây dựng)|đơn giá all.?in|all.?in'),
 ('Chi phí bán hàng',r'chi phí bán hàng'),('Chi phí hoạt động',r'chi phí hoạt động'),('Chi phí tài chính / lãi vay',r'chi phí tài chính|lãi vay|lãi suất'),
 ('Tổng mức đầu tư',r'tổng mức đầu tư|\btmđt\b'),('Doanh thu',r'tổng doanh thu|doanh thu'),
 ('Lợi nhuận trước thuế',r'lợi nhuận trước thuế|\blntt\b'),('Lợi nhuận sau thuế',r'lợi nhuận sau thuế|\blnst\b'),
 ('IRR',r'\birr\b'),('NPV',r'\bnpv\b'),('Thời gian hoàn vốn',r'hoàn vốn|payback'),
 ('Giá trị bồi thường / GPMB',r'bồi thường|\bgpmb\b'),('Giá trị tài sản / định giá',r'định giá|giá trị tài sản')]
num_re=re.compile(r'(?<!\w)\d[\d.,]*\s*(?:tỷ|triệu|tr(?:iệu)?(?:đ|d)?(?:ồng)?|tr/m2|tr\.m2|triệu/m2|%|usd|\$)(?!\w)',re.I)
def extract(text):
 # normalize separators into clauses while retaining report labels
 text=str(text or '').replace('\r','\n'); clauses=[]
 for line in re.split(r'\n+|;\s*',text):
  line=c(line).lstrip('-+• ')
  if line and num_re.search(line):clauses.append(line)
 out=[];unknown=[];seen=set()
 for line in clauses:
  lab=None
  for label,pat in labels:
   if re.search(pat,line,re.I):lab=label;break
  # Limit very long source clauses, but keep enough context around the first number.
  if len(line)>420:
   m=num_re.search(line);a=max(0,m.start()-170);line=line[a:a+420]
  key=(lab or '',line.lower())
  if key in seen:continue
  seen.add(key)
  item={'label':lab or 'Chưa phân loại','value':line}
  (out if lab else unknown).append(item)
 return out,unknown
changed=0;stats=[]
for r in rows:
 source='\n'.join([str(r.get('source_excerpt','')),str(r.get('financial_raw_mentions',''))])
 items,unknown=extract(source)
 r['financial_line_items']=json.dumps(items,ensure_ascii=False) if items else ''
 r['financial_unclassified_items']=json.dumps(unknown[:30],ensure_ascii=False) if unknown else ''
 if items:changed+=1
 stats.append({'curated_id':r.get('curated_id'),'project_name':r.get('project_name'),'labeled_items':len(items),'unclassified_items':len(unknown)})
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(B/'financial_label_extraction_audit.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(stats[0]));w.writeheader();w.writerows(stats)
print({'records':len(rows),'with_labeled_financial_items':changed,'total_labeled':sum(x['labeled_items'] for x in stats),'total_unclassified':sum(x['unclassified_items'] for x in stats)})
