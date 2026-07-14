import json
from pathlib import Path
d=json.loads(Path('firebase_public/data/charts/MWG_auto_chart_day.json').read_text(encoding='utf-8'))
for p in d.get('patterns',[]):
    if any(x in p.get('type','') for x in ['double','triple','head-shoulders']):
        pts=[]
        for l in p.get('lines') or []:
            if l.get('type')=='point' or len(l.get('points') or [])==1:
                pts.append((l.get('name'), l.get('points')))
        print(p.get('type'), len(pts), pts[:4])
