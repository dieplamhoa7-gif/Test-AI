from pathlib import Path
from playwright.sync_api import sync_playwright

html = Path('stock-news-backend/local_internal_redesign_safe/index.html').resolve()
out = Path('stock-news-backend/local_internal_redesign_safe/preview.png')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
    page.goto(html.as_uri(), wait_until='networkidle')
    page.screenshot(path=str(out), full_page=True)
    browser.close()
print(out, out.stat().st_size)
