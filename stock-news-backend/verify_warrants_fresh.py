import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(__file__).resolve().parent / "firebase_public" / "data" / "warrants_data.json"
data = json.loads(path.read_text(encoding="utf-8"))
items = data.get("items") or []
updated = data.get("updatedAt")
source = data.get("source")
errors = []
if source != "vps-realtime-scheduled-refresh":
    errors.append(f"unexpected source: {source!r}")
if len(items) < 200:
    errors.append(f"too few CW items: {len(items)}")
try:
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(str(updated).replace("Z", "+00:00"))).total_seconds()
    if age > 20 * 60:
        errors.append(f"CW cache stale: {age / 60:.1f} minutes")
except Exception as exc:
    errors.append(f"invalid updatedAt {updated!r}: {exc}")
if errors:
    print("CW freshness guard FAILED: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print(f"CW freshness guard OK: {len(items)} items, source={source}, updatedAt={updated}")
