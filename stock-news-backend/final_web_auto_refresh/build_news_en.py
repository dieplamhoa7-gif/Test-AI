"""Build lightweight English news translation cache.

Flow:
1) Read data/news_cache.json created by the normal news/summarizer pipeline.
2) Translate title/snippet/summary to English via Google Translate-compatible endpoint.
3) Write data/news_cache_en.json.

This is an offline/cache build step. The web/Render server must only read output JSON.
No AI/model is loaded on the web render path.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DEFAULT_INPUT = DATA / "news_cache.json"
DEFAULT_OUTPUT = DATA / "news_cache_en.json"
DEFAULT_TM = DATA / "translation_memory_vi_en.json"

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
VI_HINT_RE = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)


def clean_text(value: Any, max_chars: int = 900) -> str:
    text = html.unescape(str(value or ""))
    text = TAG_RE.sub(" ", text)
    text = SPACE_RE.sub(" ", text).strip()
    return text[:max_chars].strip()


def looks_vietnamese(text: str) -> bool:
    if VI_HINT_RE.search(text or ""):
        return True
    lower = f" {text.lower()} "
    hints = [" cổ phiếu ", " chứng khoán ", " doanh nghiệp ", " lợi nhuận ", " tăng ", " giảm ", " thị trường ", " nhà đầu tư "]
    return any(h in lower for h in hints)


def key_for(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def google_translate(text: str, source: str = "vi", target: str = "en", timeout: int = 20) -> str:
    # Unofficial public Google Translate endpoint; used only in offline cache build.
    q = urllib.parse.urlencode({
        "client": "gtx",
        "sl": source,
        "tl": target,
        "dt": "t",
        "q": text,
    })
    url = f"https://translate.googleapis.com/translate_a/single?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(part[0] for part in data[0] if part and part[0]).strip()


def translate_cached(text: str, tm: dict[str, str], sleep: float = 0.15) -> str:
    text = clean_text(text)
    if not text:
        return ""
    if not looks_vietnamese(text):
        return text
    k = key_for(text)
    if k in tm:
        return tm[k]
    try:
        out = google_translate(text)
    except Exception as exc:
        print(f"WARN translate failed: {exc} | {text[:80]}")
        out = text
    tm[k] = out
    if sleep > 0:
        time.sleep(sleep)
    return out


def load_items(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return {"items": raw}, raw
    items = raw.get("items") if isinstance(raw, dict) else []
    return raw if isinstance(raw, dict) else {"items": []}, items if isinstance(items, list) else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--tm", type=Path, default=DEFAULT_TM)
    ap.add_argument("--limit", type=int, default=200, help="Translate newest N items; preserve remaining without EN fields")
    ap.add_argument("--sleep", type=float, default=0.15)
    args = ap.parse_args()

    raw, items = load_items(args.input)
    tm = json.loads(args.tm.read_text(encoding="utf-8")) if args.tm.exists() else {}

    out_items: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        row = dict(item)
        if idx < args.limit:
            title = clean_text(row.get("title"), 500)
            snippet = clean_text(row.get("snippet") or row.get("summary"), 900)
            summary = clean_text(row.get("summary") or row.get("snippet"), 900)
            row["titleEn"] = translate_cached(title, tm, args.sleep)
            row["snippetEn"] = translate_cached(snippet, tm, args.sleep)
            row["summaryEn"] = translate_cached(summary, tm, args.sleep)
        out_items.append(row)
        if (idx + 1) % 25 == 0:
            print(f"translated/preserved {idx+1}/{len(items)}")
            args.tm.write_text(json.dumps(tm, ensure_ascii=False, indent=2), encoding="utf-8")

    out = dict(raw)
    out["items"] = out_items
    out["translation"] = {
        "target": "en",
        "method": "google-translate-offline-cache",
        "translatedLimit": min(args.limit, len(items)),
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    args.tm.write_text(json.dumps(tm, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output} items={len(out_items)} tm={len(tm)}")


if __name__ == "__main__":
    main()
