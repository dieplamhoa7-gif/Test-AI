"""
Deep scrape TradingEconomics visible/embedded page data without using Download.

- Opens pages like a normal browser with Playwright.
- Extracts visible tables/text.
- Scans inline scripts and page HTML for embedded series/config/value snippets.
- Does not click Download, does not login, does not bypass subscription.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SOURCE_NAME = "TradingEconomics browser deep scrape"
PARSER_VERSION = "te_deep_scrape_v1"
BASE_URL = "https://tradingeconomics.com/vietnam"
PAGES = {
    "interbankRate": "interbank-rate",
    "interestRate": "interest-rate",
    "moneySupplyM0": "money-supply-m0",
    "moneySupplyM1": "money-supply-m1",
    "moneySupplyM2": "money-supply-m2",
    "inflationCpi": "inflation-cpi",
    "inflationRateMom": "inflation-rate-mom",
    "retailSalesYoy": "retail-sales-yoy",
    "foreignDirectInvestment": "foreign-direct-investment",
    "industrialProduction": "industrial-production",
    "balanceOfTrade": "balance-of-trade",
    "manufacturingPmi": "manufacturing-pmi",
    "foreignExchangeReserves": "foreign-exchange-reserves",
}


def _num(v: Any) -> float | None:
    try:
        return float(str(v).replace(',', '').strip())
    except Exception:
        return None


def _parse_tables(tables: list[list[list[str]]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    main: dict[str, Any] = {}
    related: list[dict[str, Any]] = []
    for table in tables:
        if not table:
            continue
        header = table[0]
        if 'Actual' in header and 'Previous' in header and len(table) > 1:
            for k, v in zip(header, table[1]):
                main[k.lower()] = v
            main['actualValue'] = _num(main.get('actual'))
            main['previousValue'] = _num(main.get('previous'))
        if 'Related' in header and 'Last' in header:
            for row in table[1:]:
                if len(row) >= 5:
                    related.append({
                        'indicator': row[0], 'last': _num(row[1]), 'previous': _num(row[2]),
                        'unit': row[3], 'reference': row[4]
                    })
    return main, related


def _extract_embedded_candidates(html: str, scripts_text: str) -> dict[str, Any]:
    text = html + "\n" + scripts_text
    out: dict[str, Any] = {}

    # Look for date/value pairs often embedded in chart configs.
    # Conservative: collect up to 500 pairs if pattern exists.
    pairs = []
    patterns = [
        r'\[\s*Date\.UTC\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]',
        r'\[\s*"(\d{4}-\d{2}-\d{2})"\s*,\s*(-?\d+(?:\.\d+)?)\s*\]',
        r'\{\s*"date"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*(-?\d+(?:\.\d+)?)',
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            if len(m.groups()) == 4:
                y, mo, d, val = m.groups()
                # JS month may be 0-indexed; keep raw too to avoid mislabeling.
                pairs.append({'dateRaw': f'Date.UTC({y},{mo},{d})', 'value': _num(val)})
            elif len(m.groups()) == 2:
                dt, val = m.groups()
                pairs.append({'date': dt, 'value': _num(val)})
            if len(pairs) >= 500:
                break
        if pairs:
            break
    if pairs:
        out['seriesCandidates'] = pairs

    # Extract obvious latest summary sentence, e.g. decreased to X from Y.
    sent = re.search(r'((?:[A-Z][^\.]{20,240}?)(?:decreased|increased|rose|fell|was|stood)[^\.]{20,240}\.)', text, re.I)
    if sent:
        out['summarySentence'] = re.sub(r'\s+', ' ', sent.group(1)).strip()

    # Extract Highcharts/TradingEconomics variable names snippets for debugging.
    snippets = []
    for kw in ['series', 'HistoricalData', 'chart', 'spline', 'data:']:
        idx = text.lower().find(kw.lower())
        if idx >= 0:
            snippets.append(text[max(0, idx-200):idx+500])
    if snippets:
        out['debugSnippets'] = snippets[:5]
    return out


def scrape_one(page, key: str, slug: str) -> dict[str, Any]:
    url = f'{BASE_URL}/{slug}'
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(2500)
    payload = page.evaluate("""() => {
      const tables = [...document.querySelectorAll('table')].map(table =>
        [...table.querySelectorAll('tr')].map(tr =>
          [...tr.querySelectorAll('th,td')].map(td => td.innerText.trim()).filter(Boolean)
        ).filter(r => r.length)
      );
      const scripts = [...document.querySelectorAll('script')].map(s => s.textContent || '').join('\\n');
      const html = document.documentElement.outerHTML;
      return {
        url: location.href,
        title: document.querySelector('h1')?.innerText || document.title,
        summary: document.querySelector('h2')?.innerText || '',
        bodyText: document.body.innerText.slice(0, 5000),
        tables,
        scriptsText: scripts.slice(0, 1000000),
        html: html.slice(0, 1000000)
      };
    }""")
    main, related = _parse_tables(payload.get('tables', []))
    embedded = _extract_embedded_candidates(payload.get('html', ''), payload.get('scriptsText', ''))
    return {
        'key': key,
        'slug': slug,
        'url': payload.get('url'),
        'title': payload.get('title'),
        'summary': payload.get('summary'),
        'actual': main.get('actualValue'),
        'previous': main.get('previousValue'),
        'unit': main.get('unit'),
        'reference': main.get('reference') or main.get('dates'),
        'frequency': main.get('frequency'),
        'stats': main,
        'related': related,
        'embedded': embedded,
    }


def fetch(headless: bool = False, pages: dict[str, str] | None = None) -> dict[str, Any]:
    pages = pages or PAGES
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {'source': SOURCE_NAME, 'status': 'not_installed'}
    data = {}
    errors = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36', viewport={'width': 1366, 'height': 900})
        page = ctx.new_page()
        for key, slug in pages.items():
            try:
                data[key] = scrape_one(page, key, slug)
            except Exception as e:
                errors[key] = str(e)[:300]
        browser.close()
    return {
        'source': SOURCE_NAME,
        'parserVersion': PARSER_VERSION,
        'fetchedAt': datetime.now().isoformat(),
        'status': 'ok' if data else 'error',
        'data': data,
        'errors': errors or None,
        'note': 'Scraped visible page and embedded HTML/script candidates only. No Download/login/subscription bypass.'
    }


def save(result: dict[str, Any], out_path: str | Path | None = None) -> str:
    out = Path(out_path) if out_path else Path(__file__).resolve().parents[2] / 'data' / 'tradingeconomics_deep_scrape_latest.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(out)

if __name__ == '__main__':
    res = fetch(headless=False)
    out = save(res)
    series_counts = {k: len(v.get('embedded', {}).get('seriesCandidates', [])) for k, v in res.get('data', {}).items()}
    print(json.dumps({'status': res.get('status'), 'pages': len(res.get('data', {})), 'seriesCounts': series_counts, 'errors': res.get('errors'), 'out': out}, ensure_ascii=False, indent=2))
