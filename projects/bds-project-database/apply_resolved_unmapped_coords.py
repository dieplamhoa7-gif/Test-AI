from pathlib import Path
import json,csv,re,collections
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database');p=B/'project_master_curated_deduped.json'
rows=json.load(open(p,encoding='utf-8'));res=json.load(open(B/'map_link_resolution_all.json',encoding='utf-8'))
by={x.get('url'):(x.get('lat',''),x.get('lng','')) for x in res}
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
# Candidate coords direct from each record's own attached map URLs only.
cands=[]
for r in rows:
 if c(r.get('latitude')) and c(r.get('longitude')):continue
 found=[]
 for u in [x.strip() for x in c(r.get('map_urls')).split(';') if x.strip()]:
  lat,lng=by.get(u,('',''))
  try:
   if 8<=float(lat)<=23.5 and 102<=float(lng)<=109.8:found.append((lat,lng,u))
  except:pass
 uniq=[]
 for x in found:
  if (x[0],x[1]) not in [(a,b) for a,b,_ in uniq]:uniq.append(x)
 if len(uniq)==1:cands.append((r,uniq[0]))
# coordinate reuse validation among proposed values; if >=4 project names use same new point, don't apply.
count=collections.Counter((a,b) for _,(a,b,_) in cands)
changed=[];held=[]
for r,(lat,lng,u) in cands:
 if count[(lat,lng)]>=4:
  held.append({'curated_id':r.get('curated_id'),'project_name':r.get('project_name'),'url':u,'reason':'same_new_coordinate_for_4plus_records'});continue
 r['latitude']=lat;r['longitude']=lng;r['coordinates']=f'{lat}, {lng}';r['coordinate_source']='resolved_direct_teams_map_link';r['coordinate_quality']='resolved_direct_map_link';r['map_link_match_score']='record_own_map_url';changed.append({'curated_id':r.get('curated_id'),'project_name':r.get('project_name'),'latitude':lat,'longitude':lng,'url':u})
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for fn,data,fs in [('resolved_unmapped_coords_apply_log.csv',changed,['curated_id','project_name','latitude','longitude','url']),('resolved_unmapped_coords_held.csv',held,['curated_id','project_name','url','reason'])]:
 with open(B/fn,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(data)
print({'candidates':len(cands),'applied':len(changed),'held_shared':len(held)})
