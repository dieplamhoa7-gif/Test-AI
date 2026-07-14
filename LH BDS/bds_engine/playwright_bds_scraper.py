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
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if Path(p).exists():
            return p
    raise RuntimeError("Chrome not found")


def profile_dir() -> str:
    base = os.environ.get("BDS_CHROME_PROFILE")
    if base:
        Path(base).mkdir(parents=True, exist_ok=True)
        return base
    p = Path(os.environ.get("LOCALAPPDATA", ".")) / "LHBDS_Bot_Playwright_Profile"
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

def _num_vn(s: str) -> float | None:
    try:
        return float(s.strip().replace(".", "").replace(",", "."))
    except Exception:
        return None


def _tokens(s: str) -> list[str]:
    return [t.lower() for t in re.split(r"\W+", s or "") if len(t) >= 4]


def _query_match(query: str, text: str, url: str) -> bool:
    # City/admin words are useful for Batdongsan search/autocomplete, but many
    # listing cards/URLs omit them. Do not reject a valid La Casa / Era Town
    # listing only because "Hồ Chí Minh" is absent from the card text.
    ignored = {
        "shophouse", "mặt", "tiền", "nha", "nhà", "phố", "thuong", "thương", "mai", "mại",
        "hồ", "chi", "chí", "minh", "ho", "thành", "thanh", "phố", "pho", "hcm", "tphcm",
        "quận", "quan", "huyện", "huyen", "phường", "phuong",
    }
    short_stop = {"de", "la", "the", "can", "ho", "du", "an", "khu", "toa", "nha", "ban"}
    qtokens = [t.lower() for t in re.split(r"\W+", query or "") if len(t) >= 2 and t.lower() not in ignored and t.lower() not in short_stop]
    hay = ((text or "") + " " + (url or "")).lower()
    if not qtokens:
        return False
    # Require the leading distinctive project token. Otherwise `RiverGate Residence`
    # can incorrectly match `Đạt Gia Residence`, and `Saigon Royal` can match
    # `Royal Vạn Phúc` only because of a generic second token.
    leading = qtokens[0]
    hay_compact = re.sub(r"\W+", "", hay)
    if leading not in hay and leading not in hay_compact:
        return False
    # For short project names (La Casa, Era Town, Icon 56), the leading token is
    # enough. For longer names, require at least 2 project tokens when available.
    hits = sum(1 for t in qtokens if t in hay or t in hay_compact)
    return hits >= max(1, min(2, len(qtokens)))


def _parse_row(source: str, row: dict, mode: str = "buy") -> Listing | None:
    title = (row.get("title") or "").strip()
    price = (row.get("price") or "").strip()
    area = (row.get("area") or "").strip()
    # For sale mode, drop rental/income snippets; for rent mode, keep them.
    if mode == "buy" and ("/năm" in title.lower() or "/tháng" in title.lower() or "/nam" in title.lower()):
        return None
    url = (row.get("url") or "").strip()
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

            # Pick first concrete project/area autocomplete suggestion after choosing sale/rent tab.
            # Do not choose generic city suggestions like "Mua bán BĐS tại Hồ Chí Minh".
            picked = await page.evaluate(r"""([q, mode]) => {
              const qlow = (q||'').toLowerCase();
              const stop = new Set(['hồ','ho','chí','chi','minh','thành','thanh','phố','pho','tp','hcm','tphcm','hà','ha','nội','noi','de','la','the','can','căn','ho','hộ','du','an','dự','án','khu','toa','tòa','nha','nhà','ban','bán']);
              const qparts = qlow.split(/\s+/).map(x=>x.trim()).filter(x=>x.length>=2 && !stop.has(x));
              const modeOk = txt => mode === 'rent' ? /thuê/i.test(txt) : /mua bán/i.test(txt);
              const isGeneric = txt => /^(mua bán|thuê)$|bđs tại hồ chí minh$|bđs tại hà nội$|tại hồ chí minh$|tại hà nội$/i.test(txt.trim());
              const matchProject = txt => {
                const t = txt.toLowerCase(); const compact = t.replace(/\W+/g, '');
                let hits = 0;
                for (const part of qparts) if(t.includes(part) || compact.includes(part)) hits++;
                return hits >= 1;
              };
              const els=[...document.querySelectorAll('a,li,div,span')]
                .filter(el=>el.offsetParent!==null)
                .map(el=>({el, txt:(el.innerText||el.textContent||'').replace(/\s+/g,' ').trim()}))
                .filter(x=>x.txt && x.txt.length<220 && /Mua bán|Thuê|chung cư|căn hộ|BĐS|City|Khu đô thị|Residence|Riverside|Town|Casa|Park|View|Gate|Royal|Icon/i.test(x.txt));
              for (const x of els) {
                if(isGeneric(x.txt)) continue;
                if(!modeOk(x.txt)) continue;
                if(!matchProject(x.txt)) continue;
                x.el.click(); return x.txt;
              }
              for (const x of els) {
                if(isGeneric(x.txt)) continue;
                if(matchProject(x.txt)) { x.el.click(); return x.txt; }
              }
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
                if not _query_match(query, r.get("title", ""), r.get("url", "")):
                    continue
                l=_parse_row("Batdongsan.com.vn", r, mode=mode)
                if l: out.append(l)
                if len(out) >= limit:
                    break
            return out
        finally:
            await ctx.close()


async def browser_true_buckets_async(criteria: SearchCriteria, projects, max_projects: int = 5) -> dict[str, list[Listing]]:
    city = "Hồ Chí Minh"
    if "hà nội" in (criteria.human_summary or "").lower():
        city = "Hà Nội"
    elif "đà nẵng" in (criteria.human_summary or "").lower() or "da nang" in (criteria.human_summary or "").lower():
        city = "Đà Nẵng"
    buckets: dict[str, list[Listing]] = {}
    is_apartment = (getattr(criteria, "property_type", "") or "").lower() in {"chungcu", "canho", "apartment"}
    for p in projects.projects[:max_projects]:
        name=(p.get("name") or "").strip()
        if not name:
            continue
        try:
            # User rule: keyword = project/area name + city. Avoid adding asset type here
            # because it can make Batdongsan autocomplete choose the wrong category.
            mode = getattr(criteria, "transaction", "buy") or "buy"
            rows = await scrape_batdongsan_playwright(f"{name} {city}", limit=10, headless=False, mode=mode)
            # For landed/street searches Batdongsan often needs district/city context.
            # For apartments, fallback street/district queries make fast-mode exceed timeout
            # and often broaden away from the project, so keep the exact project+city query.
            if not is_apartment:
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

    picked = await page.evaluate(r"""([q, mode]) => {
      const qlow = (q||'').toLowerCase();
      const stop = new Set(['hồ','ho','chí','chi','minh','thành','thanh','phố','pho','tp','hcm','tphcm','hà','ha','nội','noi','de','la','the','can','căn','ho','hộ','du','an','dự','án','khu','toa','tòa','nha','nhà','ban','bán']);
      const qparts = qlow.split(/\s+/).map(x=>x.trim()).filter(x=>x.length>=2 && !stop.has(x));
      const modeOk = txt => mode === 'rent' ? /thuê/i.test(txt) : /mua bán/i.test(txt);
      const isGeneric = txt => /^(mua bán|thuê)$|bđs tại hồ chí minh$|bđs tại hà nội$|tại hồ chí minh$|tại hà nội$/i.test(txt.trim());
      const matchProject = txt => {
        const t = txt.toLowerCase();
        const compact = t.replace(/\W+/g, '');
        let hits = 0;
        for (const part of qparts) if(t.includes(part) || compact.includes(part)) hits++;
        return hits >= 1;
      };
      const els=[...document.querySelectorAll('a,li,div,span')]
        .filter(el=>el.offsetParent!==null)
        .map(el=>({el, txt:(el.innerText||el.textContent||'').replace(/\s+/g,' ').trim()}))
        .filter(x=>x.txt && x.txt.length<220 && /Mua bán|Thuê|chung cư|căn hộ|BĐS|City|Khu đô thị|Residence|Riverside|Town|Casa|Park|View|Gate|Royal|Icon/i.test(x.txt));
      // Batdongsan usually ranks the closest suggestion first. Keep that order,
      // only skip generic city/category suggestions and wrong transaction type.
      for (const x of els) {
        if(isGeneric(x.txt)) continue;
        if(!modeOk(x.txt)) continue;
        if(!matchProject(x.txt)) continue;
        x.el.click();
        return x.txt;
      }
      // Fallback: first project-like suggestion even if it misses explicit mode text.
      for (const x of els) {
        if(isGeneric(x.txt)) continue;
        if(matchProject(x.txt)) { x.el.click(); return x.txt; }
      }
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
        if not _query_match(query, r.get("title", ""), r.get("url", "")):
            continue
        l=_parse_row("Batdongsan.com.vn", r, mode=mode)
        if l: out.append(l)
        if len(out) >= limit: break
    return out


async def browser_true_buckets_async_reuse(criteria: SearchCriteria, projects, max_projects: int = 5, per_project_timeout: int = 35) -> dict[str, list[Listing]]:
    """Open Batdongsan once, choose sale/rent tab once, then search projects sequentially.

    This follows the manual flow Hòa Đại ka prefers: open Batdongsan a single
    time, click Nhà đất bán/cho thuê once, then reuse the same page for project
    1 -> project 5. Each project has its own timeout so one slow autocomplete or
    result page does not hang the whole R&D job.
    """
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
            user_data_dir=profile_dir(), executable_path=chrome_path(), headless=False,
            viewport={"width":1365,"height":1600},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        async def goto_batdongsan_with_retry(attempts: int = 3):
            last_err = None
            for i in range(attempts):
                try:
                    if page.is_closed():
                        raise RuntimeError("page closed before goto")
                    await page.goto("https://batdongsan.com.vn", wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(4000)
                    return
                except Exception as exc:
                    last_err = exc
                    logger.warning("Batdongsan initial goto failed attempt %s/%s: %s", i + 1, attempts, exc)
                    try:
                        await page.wait_for_timeout(1500 + i * 1000)
                        await page.goto("about:blank", wait_until="domcontentloaded", timeout=10000)
                    except Exception:
                        pass
            raise last_err or RuntimeError("Batdongsan initial goto failed")
        try:
            await goto_batdongsan_with_retry()
            tab_text = "Nhà đất cho thuê" if mode == "rent" else "Nhà đất bán"
            async def ensure_mode_tab():
                try:
                    await page.get_by_text(tab_text, exact=False).first.click(timeout=8000)
                    await page.wait_for_timeout(1200)
                except Exception:
                    pass
            await ensure_mode_tab()
            is_apartment = (getattr(criteria, "property_type", "") or "").lower() in {"chungcu", "canho", "apartment"}
            for pr in projects.projects[:max_projects]:
                name=(pr.get("name") or "").strip()
                if not name: continue
                search_name = _clean_project_search_name(name)
                try:
                    # Primary rule: clean project name + city only. Reuse the same
                    # browser/page; do not close and reopen Batdongsan per project.
                    rows = await asyncio.wait_for(
                        _search_on_existing_page(page, f"{search_name} {city}", mode=mode, limit=10),
                        timeout=per_project_timeout,
                    )
                    if not is_apartment:
                        district = loc.get("district") if isinstance(loc, dict) else None
                        street = loc.get("street") if isinstance(loc, dict) else None
                        # Fallbacks only if no rows: add real district/street from reverse context, never hardcode.
                        if not rows and district and district.lower() not in search_name.lower():
                            rows = await asyncio.wait_for(
                                _search_on_existing_page(page, f"{search_name} {district} {city}", mode=mode, limit=10),
                                timeout=per_project_timeout,
                            )
                        if not rows and street and street.lower() not in search_name.lower():
                            rows = await asyncio.wait_for(
                                _search_on_existing_page(page, f"{search_name} {street} {district or ''} {city}", mode=mode, limit=10),
                                timeout=per_project_timeout,
                            )
                except Exception:
                    rows = []
                    # Recover the same browser tab for the next project if a search timed out.
                    try:
                        await page.goto("https://batdongsan.com.vn", wait_until="domcontentloaded", timeout=30000)
                        await page.wait_for_timeout(1500)
                        await ensure_mode_tab()
                    except Exception:
                        pass
                if rows:
                    buckets.setdefault(f"Batdongsan.com.vn::{name}", []).extend(rows)
            return buckets
        finally:
            await ctx.close()

# Preferred optimized implementation
browser_true_buckets_async = browser_true_buckets_async_reuse
