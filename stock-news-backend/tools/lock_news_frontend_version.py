from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "firebase_public/index.html",
    ROOT / "firebase_public/stocks.html",
    ROOT / "firebase_public/news-page.html",
    ROOT / "app/dashboard_template.py",
]
CSS = """
    /* LH_NEWS_FORMAT_V2_LOCKED */
    .news-bullet-list { padding-left:19px; margin-top:10px; white-space:normal; }
    .news-bullet-list li { margin:0 0 7px; padding-left:2px; }
    .news-bullet-list li::marker { color:var(--accent); }
    .news-bullet-list strong { color:var(--text); font-weight:800; }
"""
HELPERS = """    // LH_NEWS_FORMAT_V2_LOCKED: preserve approved bullets and <strong> keywords safely.
    function renderNewsRichText(value='') { const token='__LH_STRONG__'; const marked=String(value ?? '').replace(/<strong\\s*>/gi, token+'O').replace(/<\\/strong\\s*>/gi, token+'C'); const escaped=escapeHtml(marked).replace(new RegExp(token+'O','g'), '<strong>').replace(new RegExp(token+'C','g'), '</strong>'); return escaped.replace(/((?:\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?:[,.]\\d+)?\\s*(?:%|tỷ|triệu|nghìn|đồng|VND|USD|cp|cổ phiếu|lần|x|điểm|ha|MW|kWh|năm|tháng|ngày)?)/gi, '<b class=\"news-number\">$1</b>'); }
    function newsBulletLines(item, rawSnippet, title) { const direct=Array.isArray(item.summaryBullets) ? item.summaryBullets : []; const lines=(direct.length ? direct : String(rawSnippet||'').split(/(?:\\r?\\n\\s*[-•]\\s*|(?<=[.!?])\\s+)/)).map(x=>removeDuplicateNewsLead(title, String(x||'').replace(/^[-•]\\s*/, '').trim())).filter(x=>stripHtmlTags(x).length>12).slice(0,5); return lines.length ? lines : [removeDuplicateNewsLead(title, rawSnippet)]; }
    function highlightNewsNumbers(text='') { return renderNewsRichText(text); }"""

for path in FILES:
    text = path.read_text(encoding="utf-8", errors="strict")
    # Remove prior lock CSS/helpers, if any.
    text = re.sub(r"\n\s*/\* LH_NEWS_FORMAT_V2_LOCKED \*/[\s\S]*?\.news-bullet-list strong \{[^}]*\}\n", "\n", text, count=1)
    text = re.sub(r"\s*// (?:News may contain only <strong>; sanitize before rendering so the AI format is retained safely\.|LH_NEWS_FORMAT_V2_LOCKED:[^\n]*)\n\s*function renderNewsRichText[\s\S]*?function highlightNewsNumbers\(text=''\) \{[^\n]*\}", lambda _: "\n" + HELPERS, text, count=1)
    if "function renderNewsRichText" not in text:
        anchor = "    function inferCategory(item)"
        pos = text.find(anchor)
        if pos < 0:
            raise SystemExit(f"Cannot insert news helpers: {path}")
        text = text[:pos] + HELPERS + "\n" + text[pos:]
    # Insert locked CSS after the first news-snippet rule.
    m = re.search(r"^[ \t]*\.news-snippet \{[^\n]*\}\s*$", text, flags=re.M)
    if not m:
        raise SystemExit(f"Cannot find news CSS: {path}")
    text = text[:m.end()] + CSS + text[m.end():]
    # Approved rich-summary field order. Never prefer legacy summaryAi.
    text = re.sub(
        r"const rawSnippet = currentLang === 'en' \? .*?; const title = stripHtmlTags\(rawTitle\);",
        "const rawSnippet = currentLang === 'en' ? (item.summaryEn || item.ai_summary_en || item.summary_full_en || item.snippetEn || item.summary || item.ai_summary || item.summary_full || item.snippet || '') : (item.summary || item.ai_summary || item.summary_full || item.summaryBullets?.join(' ') || item.snippet || ''); const title = stripHtmlTags(rawTitle);",
        text,
        count=1,
    )
    # Replace old paragraph renderer or already-bulleted renderer.
    text, n = re.subn(
        r"const (?:snippet|bullets) = .*?; return `<article class=\"news-card\"><div class=\"news-meta\">(.*?)</div><h3 class=\"news-title\">\$\{highlightNewsNumbers\(title\)\}</h3><(?:p class=\"news-snippet\">\$\{highlightNewsNumbers\(snippet\)\}</p>|ul class=\"news-snippet news-bullet-list\">\$\{bullets\.map\(line => `<li>\$\{renderNewsRichText\(line\)\}</li>`\)\.join\(''\)\}</ul>)",
        "const bullets = newsBulletLines(item, rawSnippet, title); return `<article class=\"news-card\"><div class=\"news-meta\">\\1</div><h3 class=\"news-title\">${highlightNewsNumbers(title)}</h3><ul class=\"news-snippet news-bullet-list\">${bullets.map(line => `<li>${renderNewsRichText(line)}</li>`).join('')}</ul>",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"Cannot replace news renderer: {path}")
    path.write_text(text, encoding="utf-8")
    print("locked", path.relative_to(ROOT))
