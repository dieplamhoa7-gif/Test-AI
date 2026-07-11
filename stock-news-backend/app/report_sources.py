from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any
import hashlib
import json
import re

import httpx

REPORTS_URL = "https://24hmoney.vn/bao-cao-phan-tich"
CACHE_TTL_SECONDS = 6 * 60 * 60
_http_cache: tuple[float, list[dict[str, Any]]] | None = None


def _decode_js_string(value: str) -> str:
    return value.replace("\\/", "/").replace("\\n", "\n").replace("\\t", "\t")


def _extract_list_data(html_text: str) -> list[dict[str, Any]]:
    start = html_text.find("listData:[")
    if start < 0:
        return []
    arr_start = html_text.find("[", start)
    depth = 0
    in_str = False
    esc = False
    arr_end = None
    for idx, ch in enumerate(html_text[arr_start:], arr_start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    arr_end = idx + 1
                    break
    if not arr_end:
        return []
    raw = html_text[arr_start:arr_end]
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r"\{id:(.*?)(?=\},\{id:|\}\])", raw, re.S):
        chunk = "{id:" + match.group(1) + "}"

        def str_val(key: str) -> str:
            m = re.search(key + r':"((?:\\.|[^"\\])*)"', chunk)
            return _decode_js_string(m.group(1)).strip() if m else ""

        id_match = re.search(r"id:(\d+)", chunk)
        symbols = [s.strip().upper() for s in re.split(r"[,;\s]+", str_val("symbols")) if s.strip()]
        title = str_val("title")
        url_file = str_val("url_file")
        if not title or not url_file:
            continue
        stable_key = url_file.lower() or title.lower()
        rows.append({
            "id": int(id_match.group(1)) if id_match else None,
            "symbol": symbols[0] if symbols else "",
            "symbols": symbols,
            "title": title,
            "source": str_val("source") or "24HMoney",
            "url": url_file,
            "url_file": url_file,
            "thumbnail": str_val("thumbnail"),
            "summary": str_val("summary"),
            "report_date": datetime.now(timezone.utc).date().isoformat(),
            "provider": "24HMoney",
            "dedupe_key": hashlib.sha1(stable_key.encode("utf-8")).hexdigest(),
        })
    return rows


def collect_24hmoney_reports(limit: int = 50, force: bool = False) -> list[dict[str, Any]]:
    global _http_cache
    now = monotonic()
    if _http_cache and not force and (now - _http_cache[0]) < CACHE_TTL_SECONDS:
        return _http_cache[1][:limit]
    resp = httpx.get(REPORTS_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    rows = _extract_list_data(resp.text)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for row in rows:
        key = str(row.get("dedupe_key") or row.get("url") or row.get("title")).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    _http_cache = (now, unique)
    return unique[:limit]


def cache_24hmoney_reports(path: Path, limit: int = 80, force: bool = False) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = collect_24hmoney_reports(limit=limit, force=force)
    payload = {"source": REPORTS_URL, "updatedAt": datetime.now(timezone.utc).isoformat(), "items": rows, "count": len(rows)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_cached_24hmoney_reports(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items", data if isinstance(data, list) else [])
        return items if isinstance(items, list) else []
    except Exception:
        return []
