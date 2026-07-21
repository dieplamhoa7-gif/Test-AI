from pathlib import Path
import json,csv,re,collections
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(B/'published_clean_projects.json',encoding='utf-8'))
# Raw chunks allow us to locate a map link even if it was not attached in current master field.
chunks=json.load(open(B/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
urlre=re.compile(r'https?://[^\s<>"\]\)]+',re.I)
mapre=re.compile(r'(?:goo\.gl/maps|maps\.app\.goo\.gl|google\.com/maps|google\.com/maps/d)',re.I)
def tokens(s):return set(re.findall(r'[a-zA-ZÀ-ỹĐđ]{4,}',c(s).lower()))
out=[]
for r in rows:
 if r.get('has_map')=='yes':continue
 name=c(r.get('project_name')); nt=tokens(name)
 urls=[u.rstrip('.,;') for u in urlre.findall(c(r.get('map_urls'))+' '+c(r.get('source_excerpt'))) if mapre.search(u)]
 # look for raw chunks with name token overlap and maps URLs
 raw=[]
 for ch in chunks:
  tx=c(ch.get('text','')); us=[u.rstrip('.,;') for u in urlre.findall(tx) if mapre.search(u)]
  if not us:continue
  overlap=len(nt & tokens(tx))
  if overlap>=2:raw += us
 raw=list(dict.fromkeys(raw))
 allurls=list(dict.fromkeys(urls+raw))
 q=c(r.get('coordinate_quality')); source=c(r.get('coordinate_source'));score=c(r.get('map_link_match_score'))
 if allurls:
  cat='has_unresolved_or_unattached_map_link'
 elif q in ['needs_coordinate_review','suspicious_shared_by_many_projects'] or source:
  cat='coordinate_removed_or_needs_review'
 else:cat='no_map_link_found_in_matched_raw'
 out.append({'curated_id':r.get('curated_id'),'project_name':name,'category':cat,'map_urls_found':'; '.join(allurls),'existing_map_urls':c(r.get('map_urls')),'coordinate_quality':q,'coordinate_source':source,'match_score':score,'source_files':c(r.get('source_files'))})
with open(B/'unmapped_projects_audit.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
counts=collections.Counter(x['category'] for x in out)
md=['# Audit dự án chưa có map','',f'- Tổng dự án chưa map: **{len(out)}**','']+[f'- {k}: **{v}**' for k,v in counts.items()]
(B/'unmapped_projects_audit.md').write_text('\n'.join(md),encoding='utf-8')
print({'unmapped':len(out),'categories':dict(counts)})
