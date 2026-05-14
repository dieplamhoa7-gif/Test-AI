from pathlib import Path

API_BASE = "https://lhinvestment.onrender.com"
ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "firebase_public"
PUBLIC.mkdir(exist_ok=True)

files = {
    "index.html": ROOT / "app" / "dashboard_template.py",
    "stocks.html": ROOT / "app" / "dashboard_template.py",
    "warrants.html": ROOT / "app" / "warrants_light_template.py",
    "news-page.html": ROOT / "app" / "news_light_template.py",
}


def extract_raw_py_string(text: str, var_name: str) -> str:
    marker = f"{var_name} = r'''"
    start = text.index(marker) + len(marker)
    end = text.rindex("'''")
    return text[start:end]


def patch_html(html: str) -> str:
    html = html.replace("__MARKET_API_BASE__", API_BASE)
    html = html.replace("const API_BASE = '';", f"const API_BASE = '{API_BASE}';")
    html = html.replace("const API_BASE='';", f"const API_BASE='{API_BASE}';")
    html = html.replace("const MARKET_API_BASE = '';", f"const MARKET_API_BASE = '{API_BASE}';")
    html = html.replace("const MARKET_API_BASE = '__MARKET_API_BASE__';", f"const MARKET_API_BASE = '{API_BASE}';")
    return html

for out_name, src in files.items():
    text = src.read_text(encoding="utf-8")
    var_name = "DASHBOARD_HTML" if "dashboard" in src.name else ("WARRANTS_HTML" if "warrants" in src.name else "NEWS_HTML")
    html = patch_html(extract_raw_py_string(text, var_name))
    (PUBLIC / out_name).write_text(html, encoding="utf-8")

# Pretty URLs for Firebase Hosting rewrites.
for route, target in {"stocks/MWG.html": "stocks.html", "warrants/CMWG2511.html": "warrants.html"}.items():
    # Placeholder examples only are not needed; Firebase rewrites handle these routes.
    pass

print(f"Built Firebase static frontend in {PUBLIC}")
for p in sorted(PUBLIC.glob('*.html')):
    print(p.name, round(p.stat().st_size / 1024, 1), "KB")

