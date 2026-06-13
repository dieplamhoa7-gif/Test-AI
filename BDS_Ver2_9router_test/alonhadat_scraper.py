from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from scraper import Listing, SearchCriteria

BASE = "https://alonhadat.com.vn"


def _vn_norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower().replace("đ", "d")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _location_terms(criteria: SearchCriteria) -> list[str]:
    loc = getattr(criteria, "location_context", {}) or {}
    terms=[]
    if isinstance(loc, dict):
        for k in ["street", "ward", "district", "city", "province"]:
            v=(loc.get(k) or "").strip()
            if v: terms.append(v)
        hint=(loc.get("search_hint") or "").strip()
        if hint: terms.append(hint)
    return terms


def _property_keywords(criteria: SearchCriteria) -> list[str]:
    pt=(criteria.property_type or "").lower()
    if pt == "dat": return ["đất", "bán đất"]
    if pt == "nha": return ["nhà", "nhà phố", "bán nhà"]
    if pt == "khoxuong": return ["kho", "xưởng", "nhà xưởng", "kho xưởng"]
    if pt == "shophouse": return ["shophouse", "mặt bằng", "nhà mặt tiền"]
    if pt == "chungcu": return ["căn hộ", "chung cư"]
    return [pt]


def _significant_tokens(s: str) -> list[str]:
    stop = {"ban", "mua", "nha", "dat", "can", "ho", "chung", "cu", "tp", "tinh", "thanh", "pho", "quan", "huyen", "phuong", "xa", "duong", "hem", "mat", "tien", "gia", "ty", "trieu"}
    return [t for t in _vn_norm(s).split() if len(t) >= 3 and t not in stop]


def _location_match(criteria: SearchCriteria, text: str) -> bool:
    tn=_vn_norm(text)
    loc = getattr(criteria, "location_context", {}) or {}
    if not isinstance(loc, dict):
        return True
    # district/province-city is mandatory when available; street/ward gives extra precision but not mandatory.
    district=_vn_norm(loc.get("district") or "")
    city=_vn_norm(loc.get("city") or loc.get("province") or "")
    street=_vn_norm(loc.get("street") or "")
    ward=_vn_norm(loc.get("ward") or "")
    if district and district not in tn:
        # accept Q4/Q7 style
        m=re.search(r"quan\s+(\d+)", district)
        if not (m and f"q{m.group(1)}" in tn):
            return False
    if city:
        city_ok = city in tn or "hcm" in tn or "tphcm" in tn or "ho chi minh" in tn or "sai gon" in tn
        # only force common HCM aliases for HCM; other provinces need token match if present in text.
        if "ho chi minh" in city and not city_ok:
            return False
    # If street is supplied and text mentions some address-like road, require street token hit.
    if street:
        stoks=[t for t in street.split() if len(t)>=4]
        if stoks and any(x in tn for x in ["duong", "mat tien", "mt ", "hem"]):
            if sum(1 for t in stoks if t in tn) < max(1, len(stoks)//2):
                return False
    return True


def _query_match(query: str, criteria: SearchCriteria, text: str) -> bool:
    if not _location_match(criteria, text):
        return False
    toks=_significant_tokens(query)
    if not toks:
        return True
    tn=_vn_norm(text)
    hits=sum(1 for t in toks if t in tn)
    return hits >= max(1, min(len(toks), int(len(toks)*0.55+0.5)))


def _num_vn(x: str) -> float | None:
    try:
        return float((x or "").replace(".", "").replace(",", "."))
    except Exception:
        return None


def _parse_listing_text(text: str, url: str, mode: str = "buy") -> Listing | None:
    text = re.sub(r"\s+", " ", text or "").strip()
    low = text.lower()
    if not text or any(x in low for x in ["cần mua", "can mua", "tuyển", "ký gửi"]):
        return None
    if mode == "buy" and ("/tháng" in low or "/thang" in low or "/năm" in low or "/nam" in low):
        return None
    price_total = None
    m = re.search(r"(\d{1,4}(?:[\.,]\d+)?)\s*tỷ", text, flags=re.I)
    if m:
        price_total = _num_vn(m.group(1))
    else:
        m = re.search(r"(\d{2,5}(?:[\.,]\d+)?)\s*triệu", text, flags=re.I)
        if m:
            v = _num_vn(m.group(1)); price_total = v/1000.0 if v else None
    area = None
    for pat in [r"(?:Diện tích|Dien tich|DT)\s*:?\s*(\d{2,6}(?:[\.,]\d+)?)\s*m", r"(\d{2,6}(?:[\.,]\d+)?)\s*m2", r"(\d{2,6}(?:[\.,]\d+)?)\s*m²"]:
        mm = re.search(pat, text, flags=re.I)
        if mm:
            area = _num_vn(mm.group(1)); break
    if not price_total or not area or area <= 0:
        return None
    ppm = price_total * 1000.0 / area
    if ppm <= 1 or ppm > 1500:
        return None
    return Listing("Alonhadat", title=text[:240], price_total=price_total, area=area, price_per_m2=ppm, url=url)


def _candidate_queries(criteria: SearchCriteria, project_name: str | None = None) -> list[str]:
    loc = getattr(criteria, "location_context", {}) or {}
    district = loc.get("district") if isinstance(loc, dict) else None
    city = loc.get("city") if isinstance(loc, dict) else None
    street = loc.get("street") if isinstance(loc, dict) else None
    kws = _property_keywords(criteria)
    bases=[]
    if project_name:
        bases.append(project_name)
    for kw in kws[:3]:
        parts=[kw, street, district, city]
        bases.append(" ".join(x for x in parts if x))
        parts2=[kw, district, city]
        bases.append(" ".join(x for x in parts2 if x))
    # de-dupe
    out=[]; seen=set()
    for q in bases:
        q=re.sub(r"\s+"," ",q or "").strip()
        if q and q.lower() not in seen:
            seen.add(q.lower()); out.append(q)
    return out


def scrape_alonhadat_query(query: str, criteria: SearchCriteria, limit: int = 10) -> list[Listing]:
    url = f"{BASE}/can-ban-nha-dat?kw={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"}
    out=[]; seen=set()
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=25) as c:
            r=c.get(url)
            if r.status_code>=400: return []
            soup=BeautifulSoup(r.text,"html.parser")
    except Exception:
        return []
    for a in soup.select('a[href$=".html"]'):
        href=a.get('href') or ''
        full=urljoin(BASE,href)
        if full in seen or any(x in href for x in ['dang-nhap','dang-tin','kinh-nghiem','mau-nha']): continue
        seen.add(full)
        node=a; texts=[a.get_text(' ',strip=True)]
        for _ in range(7):
            node=node.parent
            if not node: break
            t=node.get_text(' ',strip=True)
            if t and len(t)>len(max(texts,key=len)):
                texts.append(t)
            if t and ('Giá:' in t or 'Diện tích:' in t) and len(t)>80:
                break
        text=max(texts,key=len)
        if not ('Giá:' in text or re.search(r'\d+[\.,]?\d*\s*tỷ',text,re.I)): continue
        if not ('Diện tích' in text or re.search(r'\d+\s*m',text,re.I)): continue
        if not _query_match(query, criteria, text): continue
        l=_parse_listing_text(text, full, mode=getattr(criteria,'transaction','buy'))
        if l: out.append(l)
        if len(out)>=limit: break
    return out


def alonhadat_location_buckets(criteria: SearchCriteria, limit: int = 10) -> dict[str, list[Listing]]:
    rows=[]
    for q in _candidate_queries(criteria):
        for l in scrape_alonhadat_query(q, criteria, limit=limit):
            if all(l.url != x.url for x in rows): rows.append(l)
        if len(rows)>=limit: break
    return {"Alonhadat::location": rows[:limit]} if rows else {}


def alonhadat_buckets(criteria: SearchCriteria, projects, limit_per_project: int = 10) -> dict[str, list[Listing]]:
    buckets={}
    # For đất/nhà/kho xưởng, location-based matching is safer than project-name matching.
    if (criteria.property_type or '').lower() in {'dat','nha','khoxuong','shophouse'}:
        buckets.update(alonhadat_location_buckets(criteria, limit=limit_per_project))
    # Project mode remains conservative; only keep if location filter passes.
    for pr in getattr(projects,'projects',[])[:5]:
        name=(pr.get('name') or '').strip()
        if not name: continue
        rows=[]
        for q in _candidate_queries(criteria, name):
            for l in scrape_alonhadat_query(q, criteria, limit=limit_per_project):
                if all(l.url != x.url for x in rows): rows.append(l)
            if len(rows)>=limit_per_project: break
        if rows: buckets[f"Alonhadat::{name}"]=rows[:limit_per_project]
    return buckets
