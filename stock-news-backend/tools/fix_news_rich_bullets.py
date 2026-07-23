from pathlib import Path

files = [Path("firebase_public/index.html"), Path("app/dashboard_template.py")]
old_helpers = """    function stripHtmlTags(value) { return String(value ?? '').replace(/<[^>]*>/g, ' ').replace(/\\*\\*(.*?)\\*\\*/g, '$1').replace(/__(.*?)__/g, '$1').replace(/\\s+/g, ' ').trim(); }
    function highlightNewsNumbers(text='') { return escapeHtml(text).replace(/((?:\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?:[,.]\\d+)?\\s*(?:%|tỷ|triệu|nghìn|đồng|VND|USD|cp|cổ phiếu|lần|x|điểm|ha|MW|kWh|năm|tháng|ngày)?)/gi, '<b class=\"news-number\">$1</b>'); }"""
new_helpers = """    function stripHtmlTags(value) { return String(value ?? '').replace(/<[^>]*>/g, ' ').replace(/\\*\\*(.*?)\\*\\*/g, '$1').replace(/__(.*?)__/g, '$1').replace(/\\s+/g, ' ').trim(); }
    // News may contain only <strong>; sanitize before rendering so the AI format is retained safely.
    function renderNewsRichText(value='') { const token='__LH_STRONG__'; const marked=String(value ?? '').replace(/<strong\\s*>/gi, token+'O').replace(/<\\/strong\\s*>/gi, token+'C'); const escaped=escapeHtml(marked).replace(new RegExp(token+'O','g'), '<strong>').replace(new RegExp(token+'C','g'), '</strong>'); return escaped.replace(/((?:\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?:[,.]\\d+)?\\s*(?:%|tỷ|triệu|nghìn|đồng|VND|USD|cp|cổ phiếu|lần|x|điểm|ha|MW|kWh|năm|tháng|ngày)?)/gi, '<b class=\"news-number\">$1</b>'); }
    function newsBulletLines(item, rawSnippet, title) { const direct=Array.isArray(item.summaryBullets) ? item.summaryBullets : []; const lines=(direct.length ? direct : String(rawSnippet||'').split(/(?<=[.!?])\\s+/)).map(x=>removeDuplicateNewsLead(title, String(x||'').trim())).filter(x=>stripHtmlTags(x).length>12).slice(0,5); return lines.length ? lines : [removeDuplicateNewsLead(title, rawSnippet)]; }
    function highlightNewsNumbers(text='') { return renderNewsRichText(text); }"""
old_render = """const snippet = removeDuplicateNewsLead(title, rawSnippet); return `<article class=\"news-card\"><div class=\"news-meta\"><span class=\"source-tag\">${escapeHtml(item.source || 'unknown')}</span><span>${escapeHtml(formatTime(item.published_at || item.fetched_at))}</span></div><h3 class=\"news-title\">${highlightNewsNumbers(title)}</h3><p class=\"news-snippet\">${highlightNewsNumbers(snippet)}</p><div class=\"news-actions\"><a class=\"open-link\" href=\"${escapeHtml(item.url || '#')}\" target=\"_blank\" rel=\"noreferrer\">${newsText('Đọc bài gốc','Read original')}</a></div></article>`;"""
new_render = """const bullets = newsBulletLines(item, rawSnippet, title); return `<article class=\"news-card\"><div class=\"news-meta\"><span class=\"source-tag\">${escapeHtml(item.source || 'unknown')}</span><span>${escapeHtml(formatTime(item.published_at || item.fetched_at))}</span></div><h3 class=\"news-title\">${highlightNewsNumbers(title)}</h3><ul class=\"news-snippet news-bullet-list\">${bullets.map(line => `<li>${renderNewsRichText(line)}</li>`).join('')}</ul><div class=\"news-actions\"><a class=\"open-link\" href=\"${escapeHtml(item.url || '#')}\" target=\"_blank\" rel=\"noreferrer\">${newsText('Đọc bài gốc','Read original')}</a></div></article>`;"""
css_extra = "\n    .news-bullet-list { padding-left:19px; margin-top:10px; white-space:normal; }\n    .news-bullet-list li { margin:0 0 7px; padding-left:2px; }\n    .news-bullet-list li::marker { color:var(--accent); }\n    .news-bullet-list strong { color:var(--text); font-weight:800; }"
for path in files:
    text = path.read_text(encoding="utf-8")
    for old, new, label in [(old_helpers, new_helpers, "helpers"), (old_render, new_render, "renderer")]:
        if old not in text:
            raise SystemExit(f"{label} anchor absent: {path}")
        text = text.replace(old, new, 1)
    css_pos = text.find(".news-snippet {")
    css_end = text.find("\n", css_pos)
    if css_pos < 0 or css_end < 0:
        raise SystemExit(f"css anchor absent: {path}")
    text = text[:css_end] + css_extra + text[css_end:]
    path.write_text(text, encoding="utf-8")
    print("patched", path)
