from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.market_calendar import vn_market_workdays_left

PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("firebase_public/data/warrants_data.json")
MAX_AGE_HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 18.0

payload = json.loads(PATH.read_text(encoding="utf-8"))
items = payload.get("items") or []
source = payload.get("source")
updated_at_raw = payload.get("updatedAt")
errors: list[str] = []

if source != "vps-realtime-scheduled-refresh":
    errors.append(f"bad source: {source!r}")
if len(items) < 200:
    errors.append(f"too few warrants: {len(items)}")
if not updated_at_raw:
    errors.append("missing updatedAt")
else:
    try:
        updated_at = datetime.fromisoformat(str(updated_at_raw).replace("Z", "+00:00"))
        age = datetime.now(updated_at.tzinfo) - updated_at if updated_at.tzinfo else datetime.now() - updated_at
        if age > timedelta(hours=MAX_AGE_HOURS):
            errors.append(f"stale updatedAt: {updated_at_raw} age={age}")
    except Exception as exc:
        errors.append(f"invalid updatedAt: {updated_at_raw!r} ({exc})")

mismatches = []
for item in items:
    end = item.get("lastTradingDate") or item.get("maturityDate")
    if not end:
        continue
    try:
        end_day = datetime.fromisoformat(str(end)[:10]).date()
    except Exception:
        continue
    expected = vn_market_workdays_left(end_day)
    got = item.get("daysLeft")
    if got != expected:
        mismatches.append((item.get("code"), end, got, expected))
if mismatches:
    errors.append(f"daysLeft mismatches: {mismatches[:10]} total={len(mismatches)}")

if errors:
    print("WARRANT FRESHNESS FAIL")
    for err in errors:
        print("-", err)
    raise SystemExit(1)

print(f"WARRANT FRESHNESS OK: {len(items)} items, source={source}, updatedAt={updated_at_raw}")
