"""Playwright browser scraper for BĐS listing prices.

Uses installed Chrome with a persistent profile so Cloudflare/session cookies can
be kept across runs. If a site shows a manual challenge, run this once with
headless=False and solve it; later bot runs can reuse the profile.
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

from scraper import Listing, SearchCriteria


def chrome_path() -> str:
    env = os.environ.get("BDS_CHROME_PATH") or os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if env and Path(env).exists():
        return env
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]:
        if Path(p).exists():
            return p
    raise RuntimeError("Chrome not found")


def profile_dir() -> str:
    base = os.environ.get("BDS_CHROME_PROFILE") or os.environ.get("BDS_BROWSER_PROFILE")
    if base:
        Path(base).mkdir(parents=True, exist_ok=True)
        return base
    p = (Path(os.environ.get("LOCALAPPDATA")) if os.environ.get("LOCALAPPDATA") else Path("/tmp")) / "LHBDS_Bot_Playwright_Profile"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)



def _clean_project_search_name(name: str) -> str:
    """Strip AI descriptive words so Batdongsan search uses project name only."""
    n = (name or "").strip()
    # Remove common AI prefixes
    n = re.sub(r"^(dự\s*án|du\s*an|khu\s+vực|khu\s+vuc)\s+", "", n, flags=re.I).strip()
    # Cut descriptive suffixes often added by AI: hạng..., gần..., tại..., Quận...
    cut_patterns = [
        r"\s+hạng\s+.*$", r"\s+hang\s+.*$", r"\s+gần\s+.*$", r"\s+gan\s+.*$",
        r"\s+tại\s+.*$", r"\s+tai\s+.*$", r"\s+ở\s+.*$", r"\s+o\s+.*$",
        r"\s+Quận\s+\d+.*$", r"\s+Quan\s+\d+.*$", r"\s+TP\.?\s*Hồ\s+Chí\s+Minh.*$",
    ]
    for pat in cut_patterns:
        n2 = re.sub(pat, "", n, flags=re.I).strip(" -–,;")
        if n2 and len(n2) >= 3:
            n = n2
    # For area strings separated by dashes, keep as area keywords but remove verbose prefix only.
    return n.strip()

def clean_bds_text(s: str) -> str:
    """Clean mojibake from Batdongsan/browser text before matching/reporting."""
    if not isinstance(s, str):
        return s
    pairs = {
        'CÃ¡ch': 'Cách', 'Máº¡ng': 'Mạng', 'ThÃ¡ng': 'Tháng', 'TÃ¡m': 'Tám',
        'PhÆ°á»\uFFFDng': 'Phường', 'phÆ°á»\uFFFDng': 'phường', 'HÃ²a': 'Hòa', 'HÆ°ng': 'Hưng',
        'ThÃ nh': 'Thành', 'phá»‘': 'phố', 'Thá»§': 'Thủ', 'Ä\uFFFDá»©c': 'Đức',
        'Ä\uFFFDức': 'Đức', 'Ä‘ức': 'đức', 'Ä‘': 'đ', 'Ä\uFFFD': 'Đ', 'Æ°': 'ư', 'Æ¡': 'ơ',
        'Ã¡': 'á', 'Ã ': 'à', 'Ã²': 'ò', 'Ã³': 'ó', 'Ã´': 'ô', 'Ãµ': 'õ',
        'áº¡': 'ạ', 'á»§': 'ủ', 'á»©': 'ứ', 'á»±': 'ự', 'á»™': 'ộ', 'á»‘': 'ố',
        'á»“': 'ồ', 'á»•': 'ổ', 'á»—': 'ỗ', 'á»‹': 'ị', 'á»‰': 'ỉ', 'á»‡': 'ệ',
        'á»ƒ': 'ể', 'áº¿': 'ế', 'á»\uFFFD': 'ờ', 'á»›': 'ớ', 'á»Ÿ': 'ở', 'á»£': 'ợ',
        'áº£': 'ả', 'áº¥': 'ấ', 'áº§': 'ầ', 'áº©': 'ẩ', 'áº«': 'ẫ', 'áº­': 'ậ',
        'áº¯': 'ắ', 'áº±': 'ằ', 'áº³': 'ẳ', 'áºµ': 'ẵ', 'áº·': 'ặ',
    }
    out = s
    for a, b in pairs.items():
        out = out.replace(a, b)
    out = out.replace('ĐứcTám', 'Đức Tám')
    out = out.replace('ThÃ¡ng á»§ Ä\uFFFDá»©cTÃ¡m', 'Tháng Tám')
    out = out.replace('Tháng ủ ĐứcTám', 'Tháng Tám').replace('Tháng ủ Đức Tám', 'Tháng Tám')
    out = out.replace('Tháng Thủ ĐứcTám', 'Tháng Tám').replace('Tháng Thủ Đức Tám', 'Tháng Tám')
    out = out.replace('Phường Hòa Hưng Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Tháng ĐứcTám', 'Tháng Tám').replace('Tháng Đức Tám', 'Tháng Tám')
    out = out.replace('Tháng ủ ĐứcTám', 'Tháng Tám').replace('Tháng ủ Đức Tám', 'Tháng Tám')
    out = out.replace('Tháng Thủ ĐứcTám', 'Tháng Tám').replace('Tháng Thủ Đức Tám', 'Tháng Tám')
    out = out.replace('Phường Hòa Hưng, Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Hòa Hưng Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Hòa Hưng, Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Phường Hòa Hưng Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Phường Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Thành phố Hồ Chí Minh')
    out = out.replace('Thành phố Hồ Chí Minh, Thành phố Thủ Đức', 'Thành phố Hồ Chí Minh')
    out = out.replace('Phường Hòa Hưng, Thành phố Hồ Chí Minh, Phường Hòa Hưng, Thành phố Hồ Chí Minh', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    out = out.replace('\uFFFDức', 'Đức').replace('\uFFFDỨc', 'Đức').replace('\uFFFD đức', ' Đức')
    out = out.replace('Tháng \uFFFDứcTám', 'Tháng Tám').replace('Tháng \uFFFDức Tám', 'Tháng Tám')
    out = out.replace('Tháng ĐứcTám', 'Tháng Tám').replace('Tháng Đức Tám', 'Tháng Tám')
    out = out.replace('Thà nh', 'Thành').replace('thà nh', 'thành')
    return out


def _num_vn(s: str) -> float | None:
    try:
        return float(s.strip().replace(".", "").replace(",", "."))
    except Exception:
        return None


def _tokens(s: str) -> list[str]:
    return [t.lower() for t in re.split(r"\W+", s or "") if len(t) >= 4]


def _query_match(query: str, text: str, url: str) -> bool:
    qtokens = [t for t in _tokens(query) if t not in {"shophouse", "mặt", "tiền", "nha", "nhà", "phố", "thuong", "thương", "mai", "mại"}]
    hay = ((text or "") + " " + (url or "")).lower()
    if not qtokens:
        return True
    return sum(1 for t in qtokens if t in hay) >= max(1, min(2, len(qtokens)))


def _parse_row(source: str, row: dict, mode: str = "buy") -> Listing | None:
    title = clean_bds_text((row.get("title") or "").strip())
    price = clean_bds_text((row.get("price") or "").strip())
    area = clean_bds_text((row.get("area") or "").strip())
    # For sale mode, drop rental/income snippets; for rent mode, keep them.
    if mode == "buy" and ("/năm" in title.lower() or "/tháng" in title.lower() or "/nam" in title.lower()):
        return None
    url = clean_bds_text((row.get("url") or "").strip())
    pt = area_m2 = ppm = None
    if mode == "rent":
        # Rent pattern: "15 triệu/tháng · 80 m²" or "250 nghìn/m²/tháng".
        mppm = re.search(r"(\d{1,4}(?:[\.,]\d+)?)\s*(?:nghìn|ngan)\s*/\s*m", title, re.I)
        if mppm:
            ppm = (_num_vn(mppm.group(1)) or 0) / 1000.0  # million VND/m2/month
        compact_r = re.search(r"(\d{1,4}(?:[\.,]\d+)?)\s*triệu\s*/?\s*tháng\s*·\s*(\d{2,5}(?:[\.,]\d+)?)\s*m", title, re.I)
        if compact_r:
            pt = _num_vn(compact_r.group(1)) / 1000.0  # keep price_total as billion-equivalent? report labels still generic; ppm is key
            area_m2 = _num_vn(compact_r.group(2))
            if area_m2 and not ppm:
                ppm = (_num_vn(compact_r.group(1)) or 0) / area_m2  # million/m2/month
        if not area_m2:
            am = re.findall(r"(?:[· ])(\d{2,5}(?:[\.,]\d+)?)\s*m", area or title, re.I)
            if am: area_m2 = _num_vn(am[0])
    else:
        # Pattern: "39,9 tỷ ·140 m²" or "39,9 tỷ · 140 m²"
        compact = re.search(r"(\d{1,3}(?:[\.,]\d+)?)\s*tỷ\s*·\s*(\d{2,4}(?:[\.,]\d+)?)\s*m", title, re.I)
        if compact:
            pt = _num_vn(compact.group(1))
            area_m2 = _num_vn(compact.group(2))
        else:
            price_src = price if price else title
            pm = re.findall(r"(\d{1,3}(?:[\.,]\d+)?)\s*tỷ", price_src, re.I)
            if pm:
                pt = _num_vn(pm[-1])
            area_src = area if area else title
            am = re.findall(r"(?:[· ])(\d{2,4}(?:[\.,]\d+)?)\s*m", area_src, re.I)
            if am:
                area_m2 = _num_vn(am[0])
        if pt and area_m2:
            ppm = pt * 1000 / area_m2
    if not pt and not ppm:
        return None
    return Listing(source=source, title="[browser thật] " + title[:180], price_total=pt, area=area_m2, price_per_m2=ppm, url=url)


async def scrape_batdongsan_playwright(query: str, limit: int = 10, headless: bool = False, mode: str = "buy") -> list[Listing]:
    query = clean_bds_text(query or '')
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir(),
            executable_path=chrome_path(),
            headless=headless,
            viewport={"width": 1365, "height": 1600},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.goto("https://batdongsan.com.vn", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)
            text0 = (await page.locator("body").inner_text(timeout=10000))[:1000]
            if "Just a moment" in text0 or "Checking your browser" in text0:
                await page.wait_for_timeout(15000)

            # Click sale/rent tab
            tab_text = "Nhà đất cho thuê" if mode == "rent" else "Nhà đất bán"
            try:
                tab = page.get_by_text(tab_text, exact=False).first
                await tab.click(timeout=8000)
                await page.wait_for_timeout(1500)
            except Exception:
                pass

            # Fill the main search input: pick largest visible text input.
            inputs = page.locator("input")
            n_inputs = await inputs.count()
            candidates = []
            for i in range(n_inputs):
                try:
                    el = inputs.nth(i)
                    if await el.is_visible(timeout=500):
                        box = await el.bounding_box()
                        area_px = (box or {}).get("width", 0) * (box or {}).get("height", 0)
                        if area_px > 5000:
                            candidates.append((area_px, i))
                except Exception:
                    pass
            if not candidates:
                raise RuntimeError("Cannot find BDS search input")
            _, idx = max(candidates)
            el = inputs.nth(idx)
            await el.click()
            await el.fill("")
            await page.keyboard.type(query, delay=30)
            await page.wait_for_timeout(2500)

            # Pick best autocomplete suggestion (prefer Mua bán / Khu đô thị / City).
            picked = await page.evaluate("""([q, mode]) => {
              const qlow = (q||'').toLowerCase();
              const score = txt => {
                const t = txt.toLowerCase(); let s = 0;
                for (const part of qlow.split(/\\s+/).filter(x=>x.length>=4)) if(t.includes(part)) s+=5;
                if(/khu đô thị|city/i.test(txt)) s+=10;
                if(mode === "rent") { if(/thuê/i.test(txt)) s+=8; if(/mua bán/i.test(txt)) s-=8; } else { if(/mua bán/i.test(txt)) s+=5; if(/thuê/i.test(txt)) s-=10; }
                if(/không có gợi ý/i.test(txt)) s-=5;
                return s;
              };
              const els=[...document.querySelectorAll('a,li,div,span')]
                .filter(el=>el.offsetParent!==null)
                .map(el=>({el, txt:(el.innerText||el.textContent||'').replace(/\\s+/g,' ').trim()}))
                .filter(x=>x.txt && x.txt.length<220 && /Mua bán|shophouse|City|Khu đô thị|không có gợi ý/i.test(x.txt));
              els.sort((a,b)=>score(b.txt)-score(a.txt));
              if(els[0] && score(els[0].txt)>0){els[0].el.click(); return els[0].txt;}
              return null;
            }""", [query, mode])
            if not picked:
                try:
                    btn = page.get_by_role("button", name="Tìm kiếm", exact=False).first
                    if await btn.is_visible(timeout=3000):
                        await btn.click()
                    else:
                        await page.keyboard.press("Enter")
                except Exception:
                    await page.keyboard.press("Enter")

            await page.wait_for_timeout(9000)
            rows = await page.evaluate(r"""
            (mode) => {
              const rows=[];
              for (const a of [...document.querySelectorAll('a[href]')]){
                const txt=(a.innerText||a.textContent||'').replace(/\s+/g,' ').trim();
                const href=a.href;
                if(!txt || !(mode === 'rent' ? href.includes('/cho-thue-') : href.includes('/ban-'))) continue;
                if(mode === 'rent') { if(!/(triệu|nghìn|m²|m2|tháng)/i.test(txt)) continue; } else { if(!/(tỷ|Giá thỏa thuận|m²|m2)/i.test(txt)) continue; }
                if(mode !== 'rent' && /\/năm|\/tháng|\/nam/i.test(txt)) continue;
                const price=(txt.match(/(?:Giá thỏa thuận|\d{1,3}(?:[,.]\d+)?\s*tỷ)/i)||[''])[0];
                const area=(txt.match(/\d{1,4}(?:[,.]\d+)?\s*m²?/i)||[''])[0];
                if(!price || !area) continue;
                rows.push({title:txt, price, area, url:href});
              }
              const seen=new Set();
              return rows.filter(r=>{ if(seen.has(r.url)) return false; seen.add(r.url); return true; }).slice(0,30);
            }
            """, mode)
            out=[]
            for r in rows:
                r = {k: clean_bds_text(v) if isinstance(v, str) else v for k, v in (r or {}).items()}
                if not _query_match(query, r.get("title", ""), r.get("url", "")):
                    continue
                l=_parse_row("Batdongsan.com.vn", r, mode=mode)
                if l: out.append(l)
                if len(out) >= limit:
                    break
            return out
        finally:
            await ctx.close()


async def browser_true_buckets_async(criteria: SearchCriteria, projects) -> dict[str, list[Listing]]:
    city = "Hồ Chí Minh"
    if "hà nội" in (criteria.human_summary or "").lower():
        city = "Hà Nội"
    elif "đà nẵng" in (criteria.human_summary or "").lower() or "da nang" in (criteria.human_summary or "").lower():
        city = "Đà Nẵng"
    buckets: dict[str, list[Listing]] = {}
    for p in projects.projects[:5]:
        name=(p.get("name") or "").strip()
        if not name:
            continue
        try:
            # User rule: keyword = project/area name + city. Avoid adding asset type here
            # because it can make Batdongsan autocomplete choose the wrong category.
            mode = getattr(criteria, "transaction", "buy") or "buy"
            rows = await scrape_batdongsan_playwright(f"{name} {city}", limit=10, headless=False, mode=mode)
            # For streets/areas, Batdongsan often needs district/city context.
            loc = getattr(criteria, "location_context", {}) or {}
            district = loc.get("district") if isinstance(loc, dict) else None
            street = loc.get("street") if isinstance(loc, dict) else None
            if not rows and district and district.lower() not in name.lower():
                rows = await scrape_batdongsan_playwright(f"{name} {district} {city}", limit=10, headless=False, mode=mode)
            if not rows and street and street.lower() not in name.lower():
                rows = await scrape_batdongsan_playwright(f"{name} {street} {district or ''} {city}", limit=10, headless=False, mode=mode)
        except Exception:
            rows = []
        if rows:
            # Keep project-scoped source bucket so the report can use the exact
            # links returned by the search for this project, without cross-match.
            buckets.setdefault(f"Batdongsan.com.vn::{name}", []).extend(rows)
    return buckets


def browser_true_buckets_playwright(criteria: SearchCriteria, projects) -> dict[str, list[Listing]]:
    return asyncio.run(browser_true_buckets_async_reuse(criteria, projects))


if __name__ == "__main__":
    async def _t():
        rows = await scrape_batdongsan_playwright("Vạn Phúc City shophouse", limit=8, headless=False)
        print("count", len(rows))
        for r in rows:
            print(r)
    asyncio.run(_t())


async def _search_on_existing_page(page, query: str, mode: str = "buy", limit: int = 5) -> list[Listing]:
    """Search project on an already-open Batdongsan page/tab."""
    query = clean_bds_text(query or '')
    # Fill the main search input: pick largest visible text input.
    inputs = page.locator("input")
    n_inputs = await inputs.count()
    candidates = []
    for i in range(n_inputs):
        try:
            el = inputs.nth(i)
            if await el.is_visible(timeout=500):
                box = await el.bounding_box()
                area_px = (box or {}).get("width", 0) * (box or {}).get("height", 0)
                if area_px > 5000:
                    candidates.append((area_px, i))
        except Exception:
            pass
    if not candidates:
        raise RuntimeError("Cannot find BDS search input")
    _, idx = max(candidates)
    el = inputs.nth(idx)
    await el.click()
    try:
        await el.fill("")
    except Exception:
        await page.keyboard.press("Control+A")
    await page.keyboard.type(query, delay=25)
    await page.wait_for_timeout(2200)

    picked = await page.evaluate("""([q, mode]) => {
      const qlow = (q||'').toLowerCase();
      const score = txt => {
        const t = txt.toLowerCase(); let s = 0;
        for (const part of qlow.split(/\s+/).filter(x=>x.length>=4)) if(t.includes(part)) s+=5;
        if(/khu đô thị|city/i.test(txt)) s+=10;
        if(mode === "rent") { if(/thuê/i.test(txt)) s+=8; if(/mua bán/i.test(txt)) s-=8; }
        else { if(/mua bán/i.test(txt)) s+=5; if(/thuê/i.test(txt)) s-=10; }
        if(/không có gợi ý/i.test(txt)) s-=5;
        return s;
      };
      const els=[...document.querySelectorAll('a,li,div,span')]
        .filter(el=>el.offsetParent!==null)
        .map(el=>({el, txt:(el.innerText||el.textContent||'').replace(/\s+/g,' ').trim()}))
        .filter(x=>x.txt && x.txt.length<220 && /Mua bán|Thuê|shophouse|City|Khu đô thị|không có gợi ý/i.test(x.txt));
      els.sort((a,b)=>score(b.txt)-score(a.txt));
      if(els[0] && score(els[0].txt)>0){els[0].el.click(); return els[0].txt;}
      return null;
    }""", [query, mode])
    if not picked:
        try:
            btn = page.get_by_role("button", name="Tìm kiếm", exact=False).first
            if await btn.is_visible(timeout=2500): await btn.click()
            else: await page.keyboard.press("Enter")
        except Exception:
            await page.keyboard.press("Enter")
    await page.wait_for_timeout(6500)

    rows = await page.evaluate(r"""
    (mode) => {
      const rows=[];
      for (const a of [...document.querySelectorAll('a[href]')]){
        const txt=(a.innerText||a.textContent||'').replace(/\s+/g,' ').trim();
        const href=a.href;
        if(!txt || !(mode === 'rent' ? href.includes('/cho-thue-') : href.includes('/ban-'))) continue;
        if(mode === 'rent') { if(!/(triệu|nghìn|m²|m2|tháng)/i.test(txt)) continue; }
        else { if(!/(tỷ|Giá thỏa thuận|m²|m2)/i.test(txt)) continue; }
        if(mode !== 'rent' && /\/năm|\/tháng|\/nam/i.test(txt)) continue;
        const price=(txt.match(/(?:Giá thỏa thuận|\d{1,4}(?:[,.]\d+)?\s*(?:tỷ|triệu|nghìn))/i)||[''])[0];
        const area=(txt.match(/\d{1,5}(?:[,.]\d+)?\s*m²?/i)||[''])[0];
        if(!price || !area) continue;
        rows.push({title:txt, price, area, url:href});
      }
      const seen=new Set();
      return rows.filter(r=>{ if(seen.has(r.url)) return false; seen.add(r.url); return true; }).slice(0,30);
    }
    """, mode)
    out=[]
    for r in rows:
        r = {k: clean_bds_text(v) if isinstance(v, str) else v for k, v in (r or {}).items()}
        if not _query_match(query, r.get("title", ""), r.get("url", "")):
            continue
        l=_parse_row("Batdongsan.com.vn", r, mode=mode)
        if l: out.append(l)
        if len(out) >= limit: break
    return out


async def browser_true_buckets_async_reuse(criteria: SearchCriteria, projects) -> dict[str, list[Listing]]:
    """Open Batdongsan once, choose sale/rent tab once, then search projects sequentially."""
    from playwright.async_api import async_playwright
    city = "Hồ Chí Minh"
    loc = getattr(criteria, "location_context", {}) or {}
    if isinstance(loc, dict) and loc.get("city"):
        city = loc.get("city")
    elif "hà nội" in (criteria.human_summary or "").lower():
        city = "Hà Nội"
    elif "đà nẵng" in (criteria.human_summary or "").lower() or "da nang" in (criteria.human_summary or "").lower():
        city = "Đà Nẵng"
    mode = getattr(criteria, "transaction", "buy") or "buy"
    buckets: dict[str, list[Listing]] = {}
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir(), executable_path=chrome_path(), headless=(os.environ.get("BDS_HEADLESS", "1") != "0"),
            viewport={"width":1365,"height":1600},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check", "--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.goto("https://batdongsan.com.vn", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)
            tab_text = "Nhà đất cho thuê" if mode == "rent" else "Nhà đất bán"
            try:
                await page.get_by_text(tab_text, exact=False).first.click(timeout=8000)
                await page.wait_for_timeout(1500)
            except Exception:
                pass
            for pr in projects.projects[:5]:
                name=(pr.get("name") or "").strip()
                if not name: continue
                search_name = _clean_project_search_name(name)
                try:
                    # Primary rule: clean project name + city only.
                    rows = await _search_on_existing_page(page, f"{search_name} {city}", mode=mode, limit=10)
                    district = loc.get("district") if isinstance(loc, dict) else None
                    street = loc.get("street") if isinstance(loc, dict) else None
                    # Fallbacks only if no rows: add real district/street from reverse context, never hardcode.
                    if not rows and district and district.lower() not in search_name.lower():
                        rows = await _search_on_existing_page(page, f"{search_name} {district} {city}", mode=mode, limit=10)
                    if not rows and street and street.lower() not in search_name.lower():
                        rows = await _search_on_existing_page(page, f"{search_name} {street} {district or ''} {city}", mode=mode, limit=10)
                except Exception:
                    rows = []
                if rows:
                    buckets.setdefault(f"Batdongsan.com.vn::{name}", []).extend(rows)
            return buckets
        finally:
            await ctx.close()

async def scrape_batdongsan_queries_reuse(queries: list[str], mode: str = "buy", limit_per_query: int = 8) -> dict[str, list[Listing]]:
    """Open Batdongsan once, then run many queries on the same page/tab."""
    from playwright.async_api import async_playwright
    buckets: dict[str, list[Listing]] = {}
    queries = [clean_bds_text(q or '').strip() for q in (queries or []) if (q or '').strip()]
    if not queries:
        return buckets
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir(), executable_path=chrome_path(), headless=(os.environ.get("BDS_HEADLESS", "1") != "0"),
            viewport={"width":1365,"height":1600},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check", "--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.goto("https://batdongsan.com.vn", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)
            tab_text = "Nhà đất cho thuê" if mode == "rent" else "Nhà đất bán"
            try:
                await page.get_by_text(tab_text, exact=False).first.click(timeout=8000)
                await page.wait_for_timeout(1500)
            except Exception:
                pass
            for q in queries:
                try:
                    rows = await _search_on_existing_page(page, q, mode=mode, limit=limit_per_query)
                except Exception as e:
                    rows = []
                    buckets.setdefault(f'Batdongsan.com.vn::query::{q}::error::{type(e).__name__}', [])
                if rows:
                    buckets.setdefault(f'Batdongsan.com.vn::query::{q}', []).extend(rows)
                else:
                    buckets.setdefault(f'Batdongsan.com.vn::query::{q}', [])
            return buckets
        finally:
            await ctx.close()

# Preferred optimized implementation
browser_true_buckets_async = browser_true_buckets_async_reuse
