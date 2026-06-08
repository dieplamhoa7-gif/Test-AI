import json
from pathlib import Path
files=[Path('data/news_cache.json'),Path('firebase_public/data/news_cache.json'),Path('data/news_cache_en.json'),Path('firebase_public/data/news_cache_en.json')]
for p in files:
    if not p.exists():
        print('missing',p); continue
    obj=json.loads(p.read_text(encoding='utf-8'))
    arr=obj if isinstance(obj,list) else obj.get('items') if isinstance(obj,dict) else []
    changed=0
    if isinstance(arr,list):
        for x in arr:
            if not isinstance(x,dict): continue
            sn=x.get('snippet') or x.get('description') or x.get('summary') or ''
            if sn and not x.get('summary'):
                x['summary']=sn; changed+=1
            if sn and not x.get('description'):
                x['description']=sn
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    print(p,'items',len(arr) if isinstance(arr,list) else 'na','summary_filled',changed,'type',type(obj).__name__)
