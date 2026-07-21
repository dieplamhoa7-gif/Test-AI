from pathlib import Path
import json,csv,re,unicodedata,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def norm(s):
 s=unicodedata.normalize('NFD',s or ''); s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn'); s=re.sub(r'[^a-z0-9]+',' ',s.lower())
 for w in ['du an','khu dat','lo dat','cao tang','chung cu','khach san','noxh','kdc']:
  s=re.sub(r'\b'+w+r'\b',' ',s)
 return clean(s)
def name_group_key(name):
 n=norm(name)
 # known aliases/shorts
 aliases={'felecia':'felicia da nang','felicia':'felicia da nang','bai keo':'bai keo phu quoc','bao keo':'bai keo phu quoc','h2 02':'cat lai sky habitat h2 02','hai nhan 4':'hai nhan','hai nhan':'hai nhan','hoi an riverside resort spa':'hoi an riverside resort spa'}
 return aliases.get(n,n[:70])
def coord_key(r):
 if not(r.get('latitude') and r.get('longitude')): return ''
 try: return f"{round(float(r['latitude']),5)},{round(float(r['longitude']),5)}"
 except: return clean(r.get('coordinates'))
# coordinate anomaly: same coordinate has many unrelated names
coord_groups=collections.defaultdict(list)
for r in masters:
 ck=coord_key(r)
 if ck: coord_groups[ck].append(r)
coord_anoms=[]
for ck,items in coord_groups.items():
 keys=collections.Counter(name_group_key(r.get('project_name','')) for r in items)
 if len(keys)>=4 or len(items)>=6:
  coord_anoms.append({'coordinate':ck,'record_count':len(items),'name_groups':len(keys),'names':' | '.join(sorted(set(r.get('project_name','') for r in items))[:30]),'ids':'; '.join(r.get('master_id','') for r in items)})
coord_anoms.sort(key=lambda x:(-x['record_count'],-x['name_groups']))
with open(base/'coordinate_anomaly_groups.csv','w',encoding='utf-8-sig',newline='') as fp:
 fs=list(coord_anoms[0].keys()) if coord_anoms else ['coordinate']; w=csv.DictWriter(fp,fieldnames=fs); w.writeheader(); w.writerows(coord_anoms)
# conservative duplicate groups: same normalized/alias name, regardless coord; or same map link with similar names
name_groups=collections.defaultdict(list)
for r in masters:
 key=name_group_key(r.get('project_name',''))
 if key and len(key)>=4: name_groups[key].append(r)
dup_groups=[]
for key,items in name_groups.items():
 if len(items)>=2:
  dup_groups.append({'group_key':key,'count':len(items),'ids':'; '.join(r.get('master_id','') for r in items),'names':' | '.join(sorted(set(r.get('project_name','') for r in items))),'coords':' | '.join(sorted(set(coord_key(r) for r in items if coord_key(r)))),'dates':' | '.join(sorted(set((r.get('latest_report_date') or r.get('first_report_date') or '') for r in items if (r.get('latest_report_date') or r.get('first_report_date')))))})
dup_groups.sort(key=lambda x:-x['count'])
with open(base/'duplicate_project_groups_conservative.csv','w',encoding='utf-8-sig',newline='') as fp:
 fs=list(dup_groups[0].keys()) if dup_groups else ['group_key']; w=csv.DictWriter(fp,fieldnames=fs); w.writeheader(); w.writerows(dup_groups)
md=['# Duplicate & Coordinate Anomaly Analysis\n',f'- Conservative duplicate groups: {len(dup_groups)}',f'- Coordinate anomaly groups: {len(coord_anoms)}','\n## Top coordinate anomalies\n']
for a in coord_anoms[:30]: md.append(f"### {a['coordinate']} — {a['record_count']} records / {a['name_groups']} name groups\n{a['names']}\n")
md.append('\n## Top duplicate groups\n')
for g in dup_groups[:80]: md.append(f"### {g['group_key']} — {g['count']} records\n- IDs: {g['ids']}\n- Names: {g['names']}\n- Coords: {g['coords']}\n- Dates: {g['dates']}\n")
(base/'duplicate_and_coordinate_anomaly_report.md').write_text('\n'.join(md),encoding='utf-8')
print({'duplicate_groups':len(dup_groups),'coordinate_anomaly_groups':len(coord_anoms),'out_duplicates':str(base/'duplicate_project_groups_conservative.csv'),'out_coord_anomalies':str(base/'coordinate_anomaly_groups.csv')})
