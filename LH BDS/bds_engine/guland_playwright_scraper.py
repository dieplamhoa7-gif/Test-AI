from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote_plus

from scraper import Listing, SearchCriteria
from playwright_bds_scraper import chrome_path


def _num_vn(s: str) -> float | None:
    try: return float((s or '').replace('.', '').replace(',', '.'))
    except Exception: return None


def _parse_text(text: str, url: str, mode: str='buy') -> Listing | None:
    text=re.sub(r'\s+',' ',text or '').strip()
    low=text.lower()
    if not text or 'just a moment' in low: return None
    if mode=='buy' and ('/tháng' in low or '/thang' in low): return None
    price=None
    m=re.search(r'(\d{1,4}(?:[\.,]\d+)?)\s*tỷ',text,re.I)
    if m: price=_num_vn(m.group(1))
    else:
        m=re.search(r'(\d{2,5}(?:[\.,]\d+)?)\s*triệu',text,re.I)
        if m:
            v=_num_vn(m.group(1)); price=v/1000 if v else None
    area=None
    for pat in [r'(\d{2,6}(?:[\.,]\d+)?)\s*m2', r'(\d{2,6}(?:[\.,]\d+)?)\s*m²']:
        mm=re.search(pat,text,re.I)
        if mm: area=_num_vn(mm.group(1)); break
    if not price or not area: return None
    ppm=price*1000/area
    if ppm<=1 or ppm>1500: return None
    return Listing('Guland', title=text[:240], price_total=price, area=area, price_per_m2=ppm, url=url)


def _queries(criteria: SearchCriteria):
    loc=getattr(criteria,'location_context',{}) or {}
    street=loc.get('street') if isinstance(loc,dict) else None
    district=loc.get('district') if isinstance(loc,dict) else None
    city=loc.get('city') if isinstance(loc,dict) else None
    pt=(criteria.property_type or '').lower()
    kw={'dat':'đất','nha':'nhà phố','khoxuong':'kho xưởng','shophouse':'shophouse','chungcu':'căn hộ'}.get(pt,pt)
    return [' '.join(x for x in [kw, street, district, city] if x), ' '.join(x for x in [kw, district, city] if x)]


async def guland_buckets_async(criteria: SearchCriteria, limit: int=10) -> dict[str, list[Listing]]:
    from playwright.async_api import async_playwright
    mode=getattr(criteria,'transaction','buy') or 'buy'
    out=[]
    async with async_playwright() as p:
        ctx=await p.chromium.launch_persistent_context(
            user_data_dir=str(Path.home()/ 'AppData'/'Local'/'LHBDS_Guland_Profile'),
            executable_path=chrome_path(), headless=False, viewport={'width':1365,'height':1200},
            args=['--disable-blink-features=AutomationControlled','--no-first-run','--no-default-browser-check'],
        )
        page=ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            for q in _queries(criteria):
                if not q: continue
                # Try generic search URLs; Guland may change routing, browser profile handles CF cookies.
                for url in [f'https://guland.vn/search?keyword={quote_plus(q)}', f'https://guland.vn/mua-ban-bat-dong-san?keyword={quote_plus(q)}']:
                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                        await page.wait_for_timeout(9000)
                        body=(await page.locator('body').inner_text(timeout=10000))
                        if 'Enable JavaScript and cookies' in body or 'Just a moment' in body:
                            await page.wait_for_timeout(20000)
                            body=(await page.locator('body').inner_text(timeout=10000))
                        links=await page.locator('a[href]').evaluate_all("""
                            els => els.slice(0,120).map(a=>({text:a.innerText||'', href:a.href||''}))
                        """)
                        for it in links:
                            href=it.get('href') or ''
                            txt=it.get('text') or ''
                            if not href.startswith('http') or len(txt)<40: continue
                            if not any(x in href for x in ['/mua-ban', '/ban-', '/nha-dat', '/bat-dong-san']): continue
                            l=_parse_text(txt,href,mode=mode)
                            if l and all(l.url!=x.url for x in out): out.append(l)
                            if len(out)>=limit: break
                    except Exception:
                        continue
                    if len(out)>=limit: break
                if len(out)>=limit: break
        finally:
            await ctx.close()
    return {'Guland::location': out[:limit]} if out else {}
