import sys, requests, pandas as pd
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
url='https://cafef.vn/du-lieu/hose/mwg-bao-cao-tai-chinh.chn'
html=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=30).text
open('tmp_mwg_cafef_financials.html','w',encoding='utf-8').write(html)
print('saved html', len(html))
try:
    dfs=pd.read_html(html)
    print('tables', len(dfs))
    for i,df in enumerate(dfs[:20]):
        print('\n=== TABLE', i, '===')
        print(df.head(8).to_string())
except Exception as e:
    print('ERR', e)
