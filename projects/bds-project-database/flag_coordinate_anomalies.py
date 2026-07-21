from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
anoms=list(csv.DictReader(open(base/'coordinate_anomaly_groups.csv',encoding='utf-8-sig',newline='')))
bad_coords=set()
# Only flag clearly suspicious: 6+ records and 5+ different name groups at same exact coord.
for a in anoms:
    try:
        if int(a.get('record_count') or 0)>=6 and int(a.get('name_groups') or 0)>=5:
            bad_coords.add(a['coordinate'])
    except: pass
flagged=0
for r in masters:
    ck=''
    if r.get('latitude') and r.get('longitude'):
        try: ck=f"{round(float(r['latitude']),5)},{round(float(r['longitude']),5)}"
        except: ck=r.get('coordinates','')
    if ck in bad_coords:
        r['coordinate_quality']='suspicious_shared_by_many_projects'
        r['coordinate_anomaly_note']='Same coordinate is shared by many unrelated project names; verify before relying on map marker.'
        flagged+=1
    elif r.get('latitude') and r.get('longitude'):
        r['coordinate_quality']=r.get('coordinate_source') or 'resolved'
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'suspicious_coordinate_groups':len(bad_coords),'flagged_records':flagged})
