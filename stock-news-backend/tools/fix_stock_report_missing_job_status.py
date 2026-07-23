from pathlib import Path
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
if 'id="jobStatus"' not in s:
    s=s.replace('<section class="report-hero">', '<section class="report-hero">\n<span id="jobStatus" class="pill" style="display:none">idle</span>', 1)
p.write_text(s, encoding='utf-8')
