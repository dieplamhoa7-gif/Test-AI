import urllib.request,re,pathlib
base='https://qhviet.com/quy-hoach/thanh-pho-ho-chi-minh-hanh-chinh-2-cap'
out=pathlib.Path(__file__).parent
html=urllib.request.urlopen(base,timeout=30).read().decode('utf-8','replace')
(out/'page.html').write_text(html,encoding='utf-8')
urls=[]
for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)', html):
    u=m.group(1)
    if u.startswith('//'): u='https:'+u
    elif u.startswith('/'): u='https://qhviet.com'+u
    elif not u.startswith('http'): u='https://qhviet.com/'+u
    urls.append(u)
print('scripts',len(urls))
for i,u in enumerate(urls):
    try:
        data=urllib.request.urlopen(u,timeout=60).read()
        name=re.sub(r'[^A-Za-z0-9_.-]+','_',u.split('/')[-1] or f'script{i}.js')
        if not name.endswith('.js'): name += '.js'
        (out/name).write_bytes(data)
        print(i,len(data),u,'->',name)
    except Exception as e: print('ERR',u,e)
