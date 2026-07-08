from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "20260621-lh-final-chartfix-1936",
    "wyckoffDetailPane",
    "loadWyckoffMethod",
    "loadAutoChart",
    "stockVolBox",
    "Ichimoku",
]
FILES = [
    ROOT / "firebase_public" / "stocks.html",
    ROOT / "firebase_public" / "index.html",
]

missing = []
for path in FILES:
    text = path.read_text(encoding="utf-8", errors="replace")
    for marker in REQUIRED:
        if marker not in text:
            missing.append(f"{path.relative_to(ROOT)} missing {marker}")

if missing:
    raise SystemExit("LH final frontend marker check FAILED:\n" + "\n".join(missing))

print("LH final frontend marker check OK")
