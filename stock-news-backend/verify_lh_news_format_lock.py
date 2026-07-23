from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FILES = [
    ROOT / "firebase_public/index.html",
    ROOT / "firebase_public/stocks.html",
    ROOT / "firebase_public/news-page.html",
    ROOT / "app/dashboard_template.py",
]
REQUIRED = [
    "LH_NEWS_FORMAT_V2_LOCKED",
    "function renderNewsRichText",
    "function newsBulletLines",
    "news-bullet-list",
    "item.summary || item.ai_summary || item.summary_full",
    "<ul class=\"news-snippet news-bullet-list\">",
]
FORBIDDEN = [
    "<p class=\"news-snippet\">${highlightNewsNumbers(snippet)}</p>",
    "item.summaryAi || item.summary || item.snippet",
]
errors = []
for path in FILES:
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in REQUIRED:
        if token not in text:
            errors.append(f"{path.relative_to(ROOT)} missing required format marker: {token}")
    for token in FORBIDDEN:
        if token in text:
            errors.append(f"{path.relative_to(ROOT)} contains legacy renderer marker: {token}")
if errors:
    print("NEWS FORMAT LOCK FAILED:", *errors, sep="\n", file=sys.stderr)
    raise SystemExit(1)
print("LH news format lock OK (all frontend entry points use rich bullet renderer)")
