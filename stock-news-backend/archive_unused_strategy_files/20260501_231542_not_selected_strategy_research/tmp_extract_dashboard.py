from app.dashboard_template import DASHBOARD_HTML
from pathlib import Path
Path('tmp_dashboard.html').write_text(DASHBOARD_HTML, encoding='utf-8')
start = DASHBOARD_HTML.find('<script>')
end = DASHBOARD_HTML.rfind('</script>')
Path('tmp_dashboard.js').write_text(DASHBOARD_HTML[start+8:end], encoding='utf-8')
print(len(DASHBOARD_HTML), start, end)
