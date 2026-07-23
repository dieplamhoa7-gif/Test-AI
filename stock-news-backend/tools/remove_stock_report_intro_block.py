from pathlib import Path
import re
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Remove the first hero-head block entirely: icon/title/workflow/status pill.
s=re.sub(r'\s*<div class="hero-head">.*?</div>\s*(?=<div class="tickerbar">)', '\n', s, count=1, flags=re.S)
# Keep report card but remove top gap after deleted intro.
s=s.replace('.tickerbar{margin-top:0}', '.tickerbar{margin-top:0}')
p.write_text(s,encoding='utf-8')
