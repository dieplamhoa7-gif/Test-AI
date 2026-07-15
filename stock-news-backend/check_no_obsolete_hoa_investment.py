from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORBIDDEN = [
    "hoa-investment.onrender.com",
    "hoa-investment.web.app",
    "hoa-investment.firebaseapp.com",
]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
EXTS = {".html", ".js", ".json", ".py", ".yaml", ".yml", ".md", ".txt"}

hits: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in EXTS:
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.name == Path(__file__).name:
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for needle in FORBIDDEN:
        if needle.lower() in text.lower():
            rel = path.relative_to(ROOT)
            hits.append(f"{rel}: contains obsolete endpoint {needle}")

if hits:
    print("Forbidden obsolete hoa-investment endpoint references found:")
    print("\n".join(hits))
    raise SystemExit(1)

print("OK: no obsolete hoa-investment endpoint references found.")
