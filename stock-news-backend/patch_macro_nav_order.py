from pathlib import Path
PUBLIC=Path('firebase_public')
PAGES=['stocks.html','index.html','cw.html','news-page.html','warrants.html','stock-report.html','account.html']

def active_for(page):
    if page in ('cw.html','warrants.html'): return 'cw'
    if page=='news-page.html': return 'news'
    if page=='stock-report.html': return 'report'
    if page=='account.html': return 'account'
    return 'stocks'

def nav(active):
    def cls(k): return 'chip-btn active' if active==k else 'chip-btn'
    ac = ' aria-current="page"' if active else ''
    return (
        '<nav class="main-tabs">'
        f'<a class="{cls("macro")}" href="/macro?v=20260716-1625"{" aria-current=\"page\"" if active=="macro" else ""}>Vĩ Mô</a>'
        f'<a class="{cls("stocks")}" href="/stocks?v=20260716-1625"{" aria-current=\"page\"" if active=="stocks" else ""}>Chứng Khoán</a>'
        f'<a class="{cls("cw")}" href="/cw?v=20260716-1625"{" aria-current=\"page\"" if active=="cw" else ""}>Chứng Quyền</a>'
        f'<a class="{cls("news")}" href="/news-page?v=20260716-1625"{" aria-current=\"page\"" if active=="news" else ""}>Tin Tức</a>'
        f'<a class="{cls("report")}" href="/stock-report?v=20260716-1625"{" aria-current=\"page\"" if active=="report" else ""}>Báo cáo cổ phiếu</a>'
        f'<a class="{cls("account")}" href="/account?v=20260716-1625"{" aria-current=\"page\"" if active=="account" else ""}>Account</a>'
        '</nav>'
    )

for page in PAGES:
    p=PUBLIC/page
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    i=s.find('<nav class="main-tabs"')
    j=s.find('</nav>',i)
    if i<0 or j<0:
        print(page,'no nav')
        continue
    j+=len('</nav>')
    s=s[:i]+nav(active_for(page))+s[j:]
    if '<!-- LH_MACRO_NAV_CANONICAL_20260716_1625 -->' not in s:
        s=s.replace('</head>','<!-- LH_MACRO_NAV_CANONICAL_20260716_1625 -->\n</head>',1)
    p.write_text(s,encoding='utf-8')
    print(page,'patched')

# macro nav injection if macro standalone already has no main nav: leave its original head/body intact, only ensure canonical marker.
p=PUBLIC/'macro.html'
if p.exists():
    s=p.read_text(encoding='utf-8',errors='ignore')
    if '<!-- LH_MACRO_CANONICAL_ROUTE /macro -->' not in s:
        s=s.replace('<head>','<head>\n<!-- LH_MACRO_CANONICAL_ROUTE /macro -->',1)
    p.write_text(s,encoding='utf-8')
    print('macro marker ok')
