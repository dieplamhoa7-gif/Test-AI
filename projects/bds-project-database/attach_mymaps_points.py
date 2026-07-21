from pathlib import Path
import json,csv,re,unicodedata
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
km=json.load(open(base/'mymaps_kml_points.json',encoding='utf-8'))
by_mid={x['mid']:x.get('points',[]) for x in km}

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def norm(s):
 s=unicodedata.normalize('NFD',s or ''); s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn'); s=re.sub(r'[^a-z0-9]+',' ',s.lower()); return clean(s)
def score(name,ptname,excerpt):
 q=[t for t in norm(name).split() if len(t)>=3]
 p=norm(ptname); e=norm(excerpt[:1200])
 sc=0
 if norm(name) and norm(name) in p: sc+=80
 for t in q:
  if t in p: sc+=14
  elif t in e and t in p: sc+=5
 return sc
attached=0; review=[]
for r in masters:
 if r.get('latitude') and r.get('longitude'): continue
 mids=re.findall(r'mid=([A-Za-z0-9_-]+)',r.get('map_urls','') or '')
 if not mids: continue
 best=None; bestscore=0
 for mid in mids:
  for pt in by_mid.get(mid,[]):
   sc=score(r.get('project_name',''),pt.get('name',''),r.get('source_excerpt',''))
   if sc>bestscore:
    bestscore=sc; best={**pt,'mid':mid}
 if best and (bestscore>=25 or len(by_mid.get(best['mid'],[]))==1):
  r['latitude']=best['lat']; r['longitude']=best['lng']; r['coordinates']=f"{best['lat']}, {best['lng']}"; r['coordinate_source']='google_mymaps_kml'; r['mymaps_point_name']=best.get('name',''); r['mymaps_match_score']=bestscore; attached+=1
 else:
  review.append({'master_id':r.get('master_id'),'project_name':r.get('project_name'),'mids':'; '.join(mids),'best_point':best.get('name','') if best else '','best_score':bestscore,'points_available':sum(len(by_mid.get(m,[])) for m in mids)})
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
with open(base/'mymaps_match_review.csv','w',encoding='utf-8-sig',newline='') as fp:
 fs=list(review[0].keys()) if review else ['master_id']; w=csv.DictWriter(fp,fieldnames=fs,extrasaction='ignore'); w.writeheader(); w.writerows(review)
print({'attached_mymaps_coords':attached,'review':len(review)})
