from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

SOURCE_NAME = "SBV liquidity: OMO + tín phiếu + liên ngân hàng"
PARSER_VERSION = "sbv_liquidity_v1"
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "sbv_liquidity"

OMO_URL = "https://www.sbv.gov.vn/vi/web/sbv_portal/nghi%E1%BB%87p-v%E1%BB%A5-th%E1%BB%8B-tr%C6%B0%E1%BB%9Dng-m%E1%BB%9F"
TBILL_URL = "https://www.sbv.gov.vn/vi/web/sbv_portal/thong-tin-chao-ban-tin-phieu-nhnn"
SBV_HOME = "https://www.sbv.gov.vn/"


def _num(v: Any) -> float | None:
    if v is None:
        return None
    s = str(v).strip()
    if not s or s in {"-", "--"}:
        return None
    s = re.sub(r"[^0-9,\.\-]", "", s)
    if not s:
        return None
    try:
        # Vietnamese format: 1.000,00
        if "," in s and "." in s:
            return float(s.replace(".", "").replace(",", "."))
        if "," in s:
            return float(s.replace(",", "."))
        return float(s)
    except Exception:
        return None


def _iso_date_from_vi(text: str) -> str | None:
    m = re.search(r"Ng[àa]y\s+(\d{1,2})\s+th[áa]ng\s+(\d{1,2})\s+n[ăa]m\s+(\d{4})", text, re.I)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})", text)
    if m:
        y = int(m.group(3)); y = 2000 + y if y < 100 else y
        return f"{y:04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return None


def _scrape_pages_with_playwright(headless: bool = False, timeout_ms: int = 45000) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    pages = {"omo": OMO_URL, "tbill": TBILL_URL, "home": SBV_HOME}
    out: dict[str, Any] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=headless)
        page = browser.new_page(locale="vi-VN")
        for key, url in pages.items():
            item: dict[str, Any] = {"url": url}
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(2500)
                item["title"] = page.title()
                item["text"] = page.locator("body").inner_text(timeout=10000)
                item["tables"] = page.evaluate("""
() => Array.from(document.querySelectorAll('table')).map((t) =>
  Array.from(t.querySelectorAll('tr')).map((tr) =>
    Array.from(tr.querySelectorAll('th,td')).map((td) => (td.innerText || '').trim())
  )
)
""")
                item["status"] = "ok"
            except Exception as e:
                item["status"] = "error"
                item["error"] = str(e)[:300]
            out[key] = item
        browser.close()
    return out


def _parse_omo(page: dict[str, Any]) -> dict[str, Any]:
    text = page.get("text") or ""
    result = {"status": page.get("status"), "url": page.get("url"), "date": _iso_date_from_vi(text), "transactions": []}
    total = 0.0
    for table in page.get("tables") or []:
        current_type = None
        for row in table:
            cells = [c.strip() for c in row if str(c).strip()]
            joined = " | ".join(cells)
            if re.search(r"Mua\s+k[ỳy]\s+h[ạa]n", joined, re.I):
                current_type = "reverse_repo_issue"
            elif re.search(r"B[áa]n\s+k[ỳy]\s+h[ạa]n", joined, re.I):
                current_type = "repo_drain"
            m = re.search(r"K[ỳy]\s+h[ạa]n\s+(\d+)\s+ng[àa]y", joined, re.I)
            if m:
                nums = [_num(x) for x in cells]
                nums = [x for x in nums if x is not None]
                volume = nums[-2] if len(nums) >= 2 else (nums[0] if nums else None)
                rate = nums[-1] if nums else None
                members = next((c for c in cells if re.match(r"\d+/\d+", c)), None)
                if volume is not None:
                    tx = {"type": current_type or "reverse_repo_issue", "tenorDays": int(m.group(1)), "volumeBn": volume, "rate": rate, "members": members}
                    result["transactions"].append(tx)
                    total += volume if tx["type"] == "reverse_repo_issue" else -volume
    result["reverseRepoIssueBn"] = round(sum(t["volumeBn"] for t in result["transactions"] if t["type"] == "reverse_repo_issue"), 2) if result["transactions"] else None
    result["reverseRepoDrainBn"] = round(sum(t["volumeBn"] for t in result["transactions"] if t["type"] != "reverse_repo_issue"), 2) if result["transactions"] else None
    result["reverseRepoNetBn"] = round(total, 2) if result["transactions"] else None
    rates = [t.get("rate") for t in result["transactions"] if t.get("rate") is not None]
    result["omoRate"] = rates[0] if rates else None
    result["status"] = "ok" if result["transactions"] else "no_omo_transactions_parsed"
    return result


def _parse_tbill(page: dict[str, Any]) -> dict[str, Any]:
    text = page.get("text") or ""
    result = {"status": page.get("status"), "url": page.get("url"), "date": _iso_date_from_vi(text), "offers": []}
    total_issue = 0.0
    for table in page.get("tables") or []:
        for row in table:
            cells = [c.strip() for c in row if str(c).strip()]
            joined = " | ".join(cells)
            if not re.search(r"t[íi]n\s*phi[ếe]u|k[ỳy]\s*h[ạa]n|kh[ốo]i\s*l[ưư]ợng|l[ãa]i\s*su[ấa]t", joined, re.I):
                continue
            tenor = None
            m = re.search(r"K[ỳy]\s*h[ạa]n(?:\s*T[íi]n\s*phi[ếe]u\s*NHNN)?\s*:?\s*(\d+)\s+Ng[àa]y", joined, re.I)
            if m:
                tenor = int(m.group(1))
            # Only parse volume from rows explicitly labelled khối lượng. Do NOT parse dates as amounts.
            is_volume_row = bool(re.search(r"kh[ốo]i\s*l[ưư]ợng", joined, re.I))
            volume = None
            if is_volume_row and len(cells) >= 2:
                volume = _num(cells[-1])
                # SBV labels this field as VNĐ; normalize to tỷ đồng if a raw VND amount is supplied.
                if volume and volume > 1_000_000:
                    volume = volume / 1_000_000_000
            rate = None
            is_rate_row = bool(re.search(r"l[ãa]i\s*su[ấa]t", joined, re.I))
            if is_rate_row and len(cells) >= 2:
                rate = _num(cells[-1])
            if tenor or volume is not None or rate is not None:
                result["offers"].append({"type": "tbill_offer", "tenorDays": tenor, "volumeBn": volume, "rate": rate, "raw": joined[:300]})
                if volume is not None:
                    total_issue += volume
    result["tbillIssueBn"] = round(total_issue, 2) if total_issue else None
    # Maturity/outstanding generally requires rolling history unless the page exposes explicit fields.
    result["tbillMaturityBn"] = None
    result["tbillOutstandingBn"] = None
    out_m = re.search(r"(?:l[ưưu]+\s*h[àa]nh|d[ưưu]+\s*n[ợo])[^\d]{0,30}([\d\.\,]+)\s*t[ỷy]", text, re.I)
    if out_m:
        result["tbillOutstandingBn"] = _num(out_m.group(1))
    result["tbillNetBn"] = -(result["tbillIssueBn"] or 0) + (result["tbillMaturityBn"] or 0) if result.get("tbillIssueBn") is not None else None
    result["note"] = "SBV page currently exposes tender offer fields; issued volume may be blank. Actual issued/maturity/outstanding requires result page or rolling history/backfill."
    result["status"] = "ok" if result["offers"] or result.get("tbillOutstandingBn") is not None else "no_tbill_rows_parsed"
    return result


def _parse_policy_rates_from_home(page: dict[str, Any]) -> dict[str, Any]:
    text = page.get("text") or ""
    result: dict[str, Any] = {"status": page.get("status"), "url": page.get("url")}
    # SBV homepage has a "LÃI SUẤT" box, sometimes not expanded in body text. Keep placeholders if not visible.
    patterns = {
        "discountRate": r"t[áa]i\s+chi[ếe]t\s+kh[ấa]u[^\d]{0,30}(\d+[\.,]\d+|\d+)",
        "refinancingRate": r"t[áa]i\s+c[ấa]p\s+v[ốo]n[^\d]{0,30}(\d+[\.,]\d+|\d+)",
    }
    for k, pat in patterns.items():
        m = re.search(pat, text, re.I)
        result[k] = _num(m.group(1)) if m else None
    result["status"] = "ok" if any(result.get(k) is not None for k in patterns) else "not_visible_on_home"
    return result


def _load_sbv_rates_browser(headless: bool = False) -> dict[str, Any]:
    """Browser fallback for SBV weekly interbank PDF; urllib often times out on SBV."""
    try:
        import sys
        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from macro.fetchers import sbv_rates
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=headless)
            page = browser.new_page(locale="vi-VN")
            page.goto(SBV_HOME, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2500)
            article = page.evaluate("""
() => {
  const links = Array.from(document.querySelectorAll('a')).map(a => ({text: (a.innerText||'').trim(), href: a.href}));
  const hit = links.find(x => /Diễn biến thị trường ngoại tệ và thị trường liên ngân hàng/i.test(x.text));
  return hit || null;
}
""")
            if not article or not article.get("href"):
                browser.close()
                return {"status": "no_weekly_article_link", "source": "sbv_home_browser"}
            page.goto(article["href"], wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2500)
            pdf = page.evaluate("""
() => {
  const links = Array.from(document.querySelectorAll('a')).map(a => ({text: (a.innerText||'').trim(), href: a.href}));
  const hit = links.find(x => /\.pdf/i.test(x.href) || /Diễn biến thị trường ngoại tệ và thị trường liên ngân hàng/i.test(x.text));
  return hit || null;
}
""")
            if not pdf or not pdf.get("href"):
                browser.close()
                return {"status": "no_pdf_link", "articleUrl": article.get("href"), "source": "sbv_article_browser"}
            resp = page.context.request.get(pdf["href"], timeout=45000)
            content = resp.body()
            browser.close()
        parsed = sbv_rates._parse_pdf_bytes(content)
        parsed["source"] = "sbv_weekly_pdf_browser"
        parsed["articleUrl"] = article.get("href")
        parsed["pdfUrl"] = pdf.get("href")
        return parsed
    except Exception as e:
        return {"status": "browser_pdf_failed", "error": str(e)[:250]}


def _load_sbv_rates() -> dict[str, Any]:
    try:
        import sys
        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from macro.fetchers import sbv_rates
        r = sbv_rates.fetch()
    except Exception as e:
        r = {"status": "error", "error": str(e)[:200]}
    if not isinstance(r, dict) or r.get("status") not in {"ok", "partial"}:
        br = _load_sbv_rates_browser(headless=False)
        if br.get("status") == "ok":
            return br
        r = {**(r if isinstance(r, dict) else {}), "browserFallback": br}
    return r


def fetch(headless: bool = False) -> dict[str, Any]:
    pages = _scrape_pages_with_playwright(headless=headless)
    omo = _parse_omo(pages.get("omo", {}))
    tbill = _parse_tbill(pages.get("tbill", {}))
    policy = _parse_policy_rates_from_home(pages.get("home", {}))
    rates = _load_sbv_rates()

    total_net = (omo.get("reverseRepoNetBn") or 0) + (tbill.get("tbillNetBn") or 0)
    result = {
        "source": SOURCE_NAME,
        "parserVersion": PARSER_VERSION,
        "fetchedAt": datetime.now().isoformat(),
        "status": "ok",
        "omo": omo,
        "tbill": tbill,
        "policyRates": policy,
        "interbankRates": rates,
        "summary": {
            "date": omo.get("date") or tbill.get("date"),
            "reverseRepoIssueBn": omo.get("reverseRepoIssueBn"),
            "reverseRepoMaturityBn": None,
            "reverseRepoOutstandingBn": None,
            "reverseRepoNetBn": omo.get("reverseRepoNetBn"),
            "tbillIssueBn": tbill.get("tbillIssueBn"),
            "tbillMaturityBn": tbill.get("tbillMaturityBn"),
            "tbillOutstandingBn": tbill.get("tbillOutstandingBn"),
            "tbillNetBn": tbill.get("tbillNetBn"),
            "totalLiquidityNetBn": round(total_net, 2),
            "omoRate": omo.get("omoRate"),
            "discountRate": policy.get("discountRate"),
            "refinancingRate": policy.get("refinancingRate"),
        },
        "sourcePages": {k: {"url": v.get("url"), "status": v.get("status"), "title": v.get("title")} for k, v in pages.items()},
    }
    # Flatten interbank if available
    vnd = rates.get("vnd") if isinstance(rates, dict) else None
    if isinstance(vnd, dict):
        result["summary"].update({
            "interbankON": vnd.get("overnight"),
            "interbank1W": vnd.get("1w"),
            "interbank2W": vnd.get("2w"),
            "interbank1M": vnd.get("1m"),
            "interbank3M": vnd.get("3m"),
            "interbank6M": vnd.get("6m"),
            "interbank9M": vnd.get("9m"),
        })
    return result


def save(result: dict[str, Any]) -> dict[str, str]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    date_s = result.get("summary", {}).get("date") or datetime.now().strftime("%Y-%m-%d")
    raw_path = DATA_DIR / f"{date_s}.json"
    raw_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"raw": str(raw_path), "latest": str(latest_path)}


if __name__ == "__main__":
    r = fetch(headless=False)
    paths = save(r)
    print(json.dumps({"summary": r.get("summary"), "paths": paths, "sourcePages": r.get("sourcePages")}, ensure_ascii=False, indent=2))
