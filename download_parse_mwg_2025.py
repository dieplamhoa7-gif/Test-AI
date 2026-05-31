import sys, json, requests, re
from pathlib import Path
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
obj=json.load(open('tmp_mwg_bctc_list.json',encoding='utf-8'))
items=obj['Data']
annual=[x for x in items if x.get('Year')==2025 and 'hợp nhất năm 2025' in x.get('Name','').lower() and 'kiểm toán' in x.get('Name','').lower()]
print('annual', annual)
url=annual[0]['Link']
p=Path('MWG_BCTC_Hop_Nhat_2025_Kiem_Toan.pdf')
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=60)
p.write_bytes(r.content)
print('downloaded', p, len(r.content))
reader=PdfReader(str(p))
print('pages', len(reader.pages))
text=[]
for i,page in enumerate(reader.pages[:20]):
    try:
        t=page.extract_text() or ''
    except Exception as e:
        t=''
    text.append('\n---PAGE %d---\n'% (i+1)+t)
alltxt='\n'.join(text)
Path('MWG_BCTC_2025_text_sample.txt').write_text(alltxt,encoding='utf-8')
for kw in ['Doanh thu bán hàng', 'Lợi nhuận sau thuế', 'Tổng cộng tài sản', 'Nợ phải trả', 'Vốn chủ sở hữu', 'BÁO CÁO KẾT QUẢ']:
    print('KW',kw, alltxt.lower().find(kw.lower()))
# print snippets around keywords
for kw in ['Doanh thu bán hàng', 'Lợi nhuận sau thuế', 'Tổng cộng tài sản', 'BÁO CÁO KẾT QUẢ']:
    idx=alltxt.lower().find(kw.lower())
    if idx>=0:
        print('\n---',kw,'---')
        print(alltxt[idx:idx+1200])
