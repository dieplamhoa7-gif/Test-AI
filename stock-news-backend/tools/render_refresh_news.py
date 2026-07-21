from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    url = os.getenv("NEWS_REFRESH_URL", "https://hoa-investment.onrender.com/news?refresh=true&limit=1000")
    timeout = int(os.getenv("NEWS_REFRESH_TIMEOUT", "240"))
    print(f"[{datetime.now(timezone.utc).isoformat()}] refresh {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Render-Cron-HoaInvestment-News/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(2000).decode("utf-8", errors="replace")
        print(f"status={resp.status} body={body[:1000]}", flush=True)
        if not (200 <= resp.status < 300):
            return 1
        try:
            data = json.loads(body)
            first_title = (data.get("items") or [{}])[0].get("title")
            print(f"total_items={data.get('total_items')} first_title={first_title}", flush=True)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
