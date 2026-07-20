from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Canonical frontend baseline: final_backup_17.7.2026 around 16:00,
# plus later targeted fixes (CW/news) may exist on their own pages. Do NOT use
# the old visible 20260621 badge as a required marker: it was intentionally
# removed before the 17/07 final backup.
STOCK_REQUIRED = [
    "loadAutoChart",
    "stockVolBox",
    "MACD",
    "RSI",
    "Ichimoku",
]
STOCK_FORBIDDEN = [
    "20260621-lh-final-chartfix-1936",
    "LH4 - Quality Shortlist",
]
FILES = [
    ROOT / "firebase_public" / "stocks.html",
    ROOT / "firebase_public" / "index.html",
]

missing = []
for path in FILES:
    text = path.read_text(encoding="utf-8", errors="replace")
    for marker in STOCK_REQUIRED:
        if marker not in text:
            missing.append(f"{path.relative_to(ROOT)} missing {marker}")
    for marker in STOCK_FORBIDDEN:
        if marker in text:
            missing.append(f"{path.relative_to(ROOT)} contains forbidden old marker {marker}")

if missing:
    raise SystemExit("LH 17/07 final frontend marker check FAILED:\n" + "\n".join(missing))

print("LH 17/07 final frontend marker check OK")
