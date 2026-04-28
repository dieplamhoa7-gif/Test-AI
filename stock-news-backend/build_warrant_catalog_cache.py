from pathlib import Path
import json
from datetime import datetime
from vnstock import Listing

series = Listing().all_covered_warrant()
items = []
for sym in [str(x).upper().strip() for x in series.tolist() if str(x).strip()]:
    underlying = sym[1:4] if sym.startswith('C') and len(sym) >= 4 else ''
    items.append({'code': sym, 'underlying': underlying, 'source': 'vnstock-catalog-cache'})
out = Path('app/warrants/warrant_catalog.json')
out.write_text(json.dumps({'updatedAt': datetime.now().isoformat(), 'items': items}, ensure_ascii=False, indent=2), encoding='utf-8')
print(out, len(items), round(out.stat().st_size/1024, 1), 'KB')
