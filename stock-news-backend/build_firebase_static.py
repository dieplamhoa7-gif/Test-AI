from pathlib import Path

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
    html = html.replace("__MARKET_API_BASE__", "")
    return html


for out_name, src in files.items():
    text = src.read_text(encoding="utf-8")
    var_name = "DASHBOARD_HTML" if "dashboard" in src.name else ("WARRANTS_HTML" if "warrants" in src.name else "NEWS_HTML")
    html = patch_html(extract_raw_py_string(text, var_name))
    (PUBLIC / out_name).write_text(html, encoding="utf-8")

print(f"Built Firebase static frontend in {PUBLIC}")
for p in sorted(PUBLIC.glob("*.html")):
    print(p.name, round(p.stat().st_size / 1024, 1), "KB")
