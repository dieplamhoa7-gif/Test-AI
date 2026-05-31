import sys, json, requests
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
url='https://cafef.vn/du-lieu/Ajax/PageNew/FileBCTC.ashx?Symbol=mwg&Type=1&Year=0'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=30)
print('status',r.status_code,'len',len(r.text))
obj=r.json()
print('success',obj.get('Success'),'items',len(obj.get('Data') or []))
open('tmp_mwg_bctc_list.json','w',encoding='utf-8').write(json.dumps(obj,ensure_ascii=False,indent=2))
for x in (obj.get('Data') or [])[:30]:
    print(x.get('Year'), x.get('Time'), x.get('Name'), x.get('Link'))
