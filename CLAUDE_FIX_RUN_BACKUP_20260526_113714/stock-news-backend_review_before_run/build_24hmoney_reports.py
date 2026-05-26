from pathlib import Path

from app.report_sources import cache_24hmoney_reports

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    out = root / "data" / "24hmoney_reports.json"
    payload = cache_24hmoney_reports(out, limit=80, force=True)
    print(f"Saved {payload['count']} reports to {out}")
