"""Control real Chrome via Chrome DevTools Protocol to search BĐS sites.

This is closer to a human browser than raw HTTP/headless dump. It starts Chrome
with a persistent user-data-dir and remote debugging, then evaluates JS in the
rendered page to extract listing rows/prices/URLs.
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

import requests
import websocket

from scraper import Listing, SearchCriteria


def _chrome_path() -> str | None:
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]:
        if Path(p).exists():
            return p
    return None


def _free_port() -> int:
    s = socket.socket(); s.bind(('127.0.0.1',0)); port=s.getsockname()[1]; s.close(); return port


def _num_vn(s: str) -> float | None:
    try:
        s=s.strip().replace('.', '').replace(',', '.')
        return float(s)
    except Exception:
        return None


def _parse_listing(source: str, row: dict) -> Listing | None:
    title=(row.get('title') or '').strip()
    price=(row.get('price') or '').strip()
    area=(row.get('area') or '').strip()
    url=(row.get('url') or '').strip()
    pt=None; ar=None; ppm=None
    m=re.search(r'(\d{1,3}(?:[\.,]\d+)?)\s*tỷ', price, re.I)
    if m: pt=_num_vn(m.group(1))
    m=re.search(r'(\d{1,4}(?:[\.,]\d+)?)\s*m', area, re.I)
    if m: ar=_num_vn(m.group(1))
    if pt and ar: ppm=pt*1000/ar
    if not pt and not ppm: return None
    return Listing(source=source, title='[browser thật] '+title[:180], price_total=pt, area=ar, price_per_m2=ppm, url=url)


class CDPChrome:
    def __init__(self):
        self.proc=None; self.port=None; self.ws=None; self.msg_id=0; self.user_data=None

    def start(self):
        chrome=_chrome_path()
        if not chrome: raise RuntimeError('Chrome not found')
        self.port=_free_port()
        # Persistent profile keeps Cloudflare/session cookies between runs.
        default_profile = Path(os.environ.get('LOCALAPPDATA', tempfile.gettempdir())) / 'LHBDS_Bot_Chrome_Profile'
        self.user_data = os.environ.get('BDS_CHROME_PROFILE') or str(default_profile)
        Path(self.user_data).mkdir(parents=True, exist_ok=True)
        self.proc=subprocess.Popen([
            chrome,
            f'--remote-debugging-port={self.port}',
            f'--user-data-dir={self.user_data}',
            '--no-first-run','--no-default-browser-check','--disable-popup-blocking',
            '--remote-allow-origins=*',
            '--window-size=1365,1600',
            'about:blank'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline=time.time()+20
        while time.time()<deadline:
            try:
                r=requests.get(f'http://127.0.0.1:{self.port}/json/version',timeout=1)
                if r.ok: break
            except Exception: time.sleep(.2)
        tabs=requests.get(f'http://127.0.0.1:{self.port}/json').json()
        wsurl=tabs[0]['webSocketDebuggerUrl']
        self.ws=websocket.create_connection(wsurl, timeout=10)
        self.call('Page.enable'); self.call('Runtime.enable')

    def close(self):
        try:
            if self.ws: self.ws.close()
        except Exception: pass
        try:
            if self.proc: self.proc.terminate()
        except Exception: pass

    def call(self, method, params=None, timeout=20):
        self.msg_id+=1
        self.ws.send(json.dumps({'id':self.msg_id,'method':method,'params':params or {}}))
        end=time.time()+timeout
        while time.time()<end:
            msg=json.loads(self.ws.recv())
            if msg.get('id')==self.msg_id:
                if 'error' in msg: raise RuntimeError(msg['error'])
                return msg.get('result')
        raise TimeoutError(method)

    def navigate(self,url,wait=5):
        self.call('Page.navigate',{'url':url},timeout=10)
        time.sleep(wait)

    def eval(self, expr, timeout=20):
        res=self.call('Runtime.evaluate',{'expression':expr,'returnByValue':True,'awaitPromise':True},timeout=timeout)
        return res.get('result',{}).get('value')


def scrape_batdongsan_browser(query: str, limit: int = 10) -> list[Listing]:
    c=CDPChrome(); out=[]
    try:
        c.start()
        c.navigate('https://batdongsan.com.vn',wait=7)
        # interact like human: set input and click search
        js = f"""
        (() => {{
          const q={json.dumps(query)};
          const input=[...document.querySelectorAll('input')].find(i=>i.offsetParent!==null && (i.placeholder||i.type==='text'||i.getAttribute('role')==='searchbox'));
          if(input){{input.focus(); input.value=q; input.dispatchEvent(new Event('input',{{bubbles:true}})); input.dispatchEvent(new Event('change',{{bubbles:true}}));}}
          const btn=[...document.querySelectorAll('button,a')].find(el=>/Tìm kiếm/i.test(el.innerText||''));
          if(btn) btn.click();
          return !!input;
        }})()
        """
        c.eval(js); time.sleep(8)
        rows=c.eval(r"""
        (() => {
          const rows=[];
          for (const a of [...document.querySelectorAll('a[href]')]){
            const txt=(a.innerText||a.textContent||'').replace(/\s+/g,' ').trim();
            const href=a.href;
            if(!txt || !href.includes('/ban-')) continue;
            if(!/(tỷ|Giá thỏa thuận|m²|m2)/i.test(txt)) continue;
            const price=(txt.match(/(?:Giá thỏa thuận|\d{1,3}(?:[,.]\d+)?\s*tỷ)/i)||[''])[0];
            const area=(txt.match(/\d{1,4}(?:[,.]\d+)?\s*m²?/i)||[''])[0];
            if(!price || !area) continue;
            rows.push({title:txt, price, area, url:href});
          }
          const seen=new Set();
          return rows.filter(r=>{ if(seen.has(r.url)) return false; seen.add(r.url); return true; }).slice(0,20);
        })()
        """,timeout=20) or []
        for r in rows[:limit]:
            l=_parse_listing('Batdongsan.com.vn',r)
            if l: out.append(l)
        return out
    finally:
        c.close()


def browser_true_buckets(criteria: SearchCriteria, projects) -> dict[str, list[Listing]]:
    buckets={}
    kind={'shophouse':'shophouse','nha':'nhà mặt tiền','dat':'đất','chungcu':'căn hộ','khoxuong':'kho xưởng'}.get(criteria.property_type,criteria.property_type)
    for p in projects.projects[:3]:
        name=p.get('name','').strip()
        if not name: continue
        try:
            listings=scrape_batdongsan_browser(f'{name} {kind}', limit=6)
        except Exception:
            listings=[]
        if listings:
            buckets.setdefault('Batdongsan.com.vn',[]).extend(listings)
    return buckets
