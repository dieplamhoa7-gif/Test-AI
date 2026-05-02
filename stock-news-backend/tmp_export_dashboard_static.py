from pathlib import Path
from app.dashboard_template import DASHBOARD_HTML
out=Path('data/dashboard_static.html')
out.write_text(DASHBOARD_HTML.replace('__MARKET_API_BASE__',''),encoding='utf-8')
print(out, out.stat().st_size)
