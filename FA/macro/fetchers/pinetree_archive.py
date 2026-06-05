"""
Pinetree Morning Brief archive crawler.

Crawls category pages:
https://pinetree.vn/post/category/cap-nhat-thi-truong/ban-tin-sang/

Then fetches every "Bản tin sáng DD/MM/YYYY" post found and parses macro tables
with macro.fetchers.pinetree parser.

Outputs:
- data/pinetree_archive/posts_index.json
- data/pinetree_archive/raw/YYYY-MM-DD.txt
- data/pinetree_archive/parsed/YYYY-MM-DD.json
- data/pinetree_archive/pinetree_macro_timeline.csv
- data/pinetree_archive/pinetree_macro_timeline.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from macro.fetchers import pinetree

SOURCE = "Pinetree Morning Brief Archive"
PARSER_VERSION = "pinetree_archive_v1"
CATEGORY_URL = "https://pinetree.vn/post/category/cap-nhat-thi-truong/ban-tin-sang/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LHInvestment/pinetree-archive"
FA_ROOT = Path(__file__).resolve().parents[2]
OUT = FA_ROOT / "data" / "pinetree_archive"


def _get(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*", "Accept-Language": "vi,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def page_url(page: int) -> str:
    return CATEGORY_URL if page <= 1 else CATEGORY_URL.rstrip("/") + f"/page/{page}/"


def discover_posts(max_pages: int = 130, sleep_s: float = 0.15) -> dict[str, Any]:
    posts: dict[str, dict[str, Any]] = {}
    page_errors: dict[str, str] = {}
    last_nonempty = 0
    for p in range(1, max_pages + 1):
        url = page_url(p)
        try:
            html = _get(url)
        except Exception as e:
            page_errors[str(p)] = str(e)[:180]
            continue
        found = 0
        for m in re.finditer(r'href="(https://pinetree\.vn/post/(\d{8})/ban-tin-sang-(\d{2})-(\d{2})-(\d{4})/)"', html):
            post_url, ymd, dd, mm, yyyy = m.groups()
            d = f"{yyyy}-{mm}-{dd}"
            posts[d] = {"date": d, "ymd": ymd, "url": post_url, "page": p, "title": f"Bản tin sáng {dd}/{mm}/{yyyy}"}
            found += 1
        if found:
            last_nonempty = p
        # stop after several empty pages once beyond discovered pages
        if p > 5 and found == 0 and p - last_nonempty >= 3:
            break
        time.sleep(sleep_s)
    return {"source": SOURCE, "parserVersion": PARSER_VERSION, "fetchedAt": datetime.now().isoformat(), "count": len(posts), "posts": sorted(posts.values(), key=lambda x: x["date"], reverse=True), "pageErrors": page_errors or None}


def fetch_post(post: dict[str, Any]) -> dict[str, Any]:
    html = _get(post["url"])
    text = pinetree._strip_html(html)
    parsed = pinetree.parse(text, post["url"])
    parsed.update({
        "date": post["date"],
        "title": post.get("title"),
        "archiveSource": SOURCE,
        "archiveParserVersion": PARSER_VERSION,
        "rawTextHash": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
    })
    return {"text": text, "parsed": parsed}


def _metric_rows(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key in pinetree.LABEL_MAP.keys():
        val = parsed.get(key)
        if isinstance(val, dict) and val.get("value") is not None:
            rows.append({
                "date": parsed.get("date"),
                "indicator": key,
                "label": pinetree.LABEL_MAP.get(key, key),
                "value": val.get("value"),
                "change1d": val.get("change1d"),
                "ytd": val.get("ytd"),
                "source": "Pinetree Morning Brief",
                "url": parsed.get("url"),
                "rawTextHash": parsed.get("rawTextHash"),
            })
    return rows


def _rebuild_timeline() -> tuple[int, int]:
    rows = []
    for fp in sorted((OUT / "parsed").glob("*.json")):
        try:
            parsed = json.loads(fp.read_text(encoding="utf-8"))
            rows.extend(_metric_rows(parsed))
        except Exception:
            continue
    rows.sort(key=lambda r: (r["date"], r["indicator"]))
    fields = ["date", "indicator", "label", "value", "change1d", "ytd", "source", "url", "rawTextHash"]
    csv_path = OUT / "pinetree_macro_timeline.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    json_path = OUT / "pinetree_macro_timeline.json"
    post_count = len(list((OUT / "parsed").glob("*.json")))
    json_path.write_text(json.dumps({"source": SOURCE, "parserVersion": PARSER_VERSION, "fetchedAt": datetime.now().isoformat(), "postCount": post_count, "rowCount": len(rows), "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    return post_count, len(rows)


def crawl(max_pages: int = 130, max_posts: int | None = None, sleep_s: float = 0.15, incremental: bool = False) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    (OUT / "parsed").mkdir(exist_ok=True)
    idx = discover_posts(max_pages=max_pages, sleep_s=sleep_s)
    posts = idx["posts"][:max_posts] if max_posts else idx["posts"]

    # Merge index with existing if incremental.
    index_path = OUT / "posts_index.json"
    if incremental and index_path.exists():
        try:
            old = json.loads(index_path.read_text(encoding="utf-8"))
            merged = {p["date"]: p for p in old.get("posts", [])}
            for p in idx.get("posts", []):
                merged[p["date"]] = p
            idx["posts"] = sorted(merged.values(), key=lambda x: x["date"], reverse=True)
            idx["count"] = len(idx["posts"])
        except Exception:
            pass
    index_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")

    errors = {}
    ok = 0
    skipped = 0
    for post in posts:
        d = post["date"]
        parsed_path = OUT / "parsed" / f"{d}.json"
        if incremental and parsed_path.exists():
            skipped += 1
            continue
        try:
            res = fetch_post(post)
            (OUT / "raw" / f"{d}.txt").write_text(res["text"], encoding="utf-8")
            parsed_path.write_text(json.dumps(res["parsed"], ensure_ascii=False, indent=2), encoding="utf-8")
            ok += 1
        except Exception as e:
            errors[d] = str(e)[:220]
        time.sleep(sleep_s)

    post_count, row_count = _rebuild_timeline()
    summary = {"source": SOURCE, "postsDiscovered": idx["count"], "postsFetchedThisRun": ok, "postsSkippedExisting": skipped, "totalPostsStored": post_count, "rowCount": row_count, "errors": errors or None, "outDir": str(OUT)}
    (OUT / "crawl_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=130)
    ap.add_argument("--max-posts", type=int, default=0)
    args = ap.parse_args()
    res = crawl(max_pages=args.max_pages, max_posts=args.max_posts or None)
    print(json.dumps(res, ensure_ascii=False, indent=2))
