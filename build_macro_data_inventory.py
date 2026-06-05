#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "macro_data_inventory"
OUT.mkdir(exist_ok=True)

EXCLUDE_PARTS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "tradingagents_venv",
    "AppData", "site-packages"
}
KEYWORDS = [
    "macro", "vimo", "vi-mo", "vĩ", "vi_mo", "kinh_te", "kinhte", "cycle",
    "pinetree", "sbv", "nhnn", "widata", "wigroup", "wiffeed", "wifeed",
    "tradingeconomics", "dbnomics", "worldbank", "wbgapi", "fred", "yfinance",
    "interbank", "liên nh", "liennh", "lien_ngan_hang", "lãi suất", "lai_suat", "lai-suat",
    "omo", "tin_phieu", "tín phiếu", "bom_hut", "bơm hút", "liquidity",
    "cpi", "inflation", "gdp", "pmi", "credit", "fx", "usd_vnd", "usdvnd", "dxy", "vix", "brent", "gold", "bond", "yield",
    "market_flow", "foreign", "turnover", "breadth"
]
EXTS = {".xlsx", ".xls", ".csv", ".json", ".md", ".py", ".html", ".txt", ".zip"}

SOURCE_HINTS = [
    ("Pinetree", ["pinetree", "morning brief", "ban-tin-sang"]),
    ("SBV/NHNN", ["sbv", "nhnn", "ngân hàng nhà nước", "ngan hang nha nuoc"]),
    ("WiData/WiGroup/WiFeed", ["widata", "wigroup", "wiffeed", "wifeed"]),
    ("TradingEconomics", ["tradingeconomics"]),
    ("yfinance/Yahoo", ["yfinance", "^vix", "^gspc", "^tnx", "bz=f", "gc=f"]),
    ("WorldBank/DBnomics/FRED", ["worldbank", "wbgapi", "dbnomics", "fred", "pandas-datareader"]),
    ("Internal macro score", ["macro_score", "macroscore", "regime", "risk-on", "risk-off", "cuối chu kỳ", "phòng thủ"]),
    ("Market flow/local", ["foreignnetbuy", "foreign net", "turnover", "vnindex", "breadth"]),
]


def skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_PARTS)


def safe_read(path: Path, max_bytes: int = 24000) -> str:
    try:
        with path.open("rb") as f:
            raw = f.read(max_bytes)
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def keyword_score(path: Path, text: str) -> tuple[int, list[str]]:
    hay = (str(path.relative_to(ROOT)).lower() + "\n" + text[:12000].lower())
    hits = []
    for kw in KEYWORDS:
        if kw.lower() in hay:
            hits.append(kw)
    return len(set(hits)), sorted(set(hits))[:25]


def classify(path: Path, text: str, hits: list[str]) -> tuple[str, str, str, str]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    low = (rel + "\n" + text[:12000]).lower()
    source = "unknown/mixed"
    for name, pats in SOURCE_HINTS:
        if any(p in low for p in pats):
            source = name
            break
    if path.suffix.lower() in {".xlsx", ".xls", ".csv", ".json"}:
        role = "data"
    elif path.suffix.lower() in {".py"}:
        role = "code"
    elif path.suffix.lower() in {".md", ".txt"}:
        role = "notes/report/skill"
    elif path.suffix.lower() == ".html":
        role = "preview/html"
    elif path.suffix.lower() == ".zip":
        role = "archive/handoff"
    else:
        role = "other"
    if "claude" in low:
        owner = "Claude/Claude handoff or backup"
    elif "claude_handoff" in rel:
        owner = "OpenClaw handoff for Claude"
    elif "skills/" in rel:
        owner = "OpenClaw skill"
    elif "stock-news-backend" in rel:
        owner = "LH Investment backend/OpenClaw"
    elif "memory/" in rel:
        owner = "OpenClaw memory notes"
    else:
        owner = "workspace"
    desc = ""
    if path.name == "macro_cycle_local.json":
        desc = "Pinetree daily macro snapshot + local macro regime score"
    elif path.name == "macro_overview.json":
        desc = "Older/static macro overview score cache"
    elif path.name == "sbv_probe.json":
        desc = "Probe results for SBV/NHNN URLs; mostly redirects/page shell"
    elif path.name == "macro_cycle.py":
        desc = "Fetcher/parser/scorer for Pinetree Morning Brief macro cycle"
    elif path.name == "build_macro_local_page.py":
        desc = "Builds local macro preview HTML page"
    elif "vn-macro-cycle-research" in rel:
        desc = "Macro skill/source map for regime filter"
    elif "macro" in low or "vĩ" in low:
        desc = "Macro-related file detected by keywords"
    return source, role, owner, desc


def summarize_json(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    if isinstance(data, dict):
        keys = list(data.keys())[:20]
        s = "keys=" + ",".join(keys)
        if "createdAt" in data: s += f"; createdAt={data.get('createdAt')}"
        if "date" in data: s += f"; date={data.get('date')}"
        if "macroScore" in data: s += f"; macroScore={data.get('macroScore')}"
        if "phase" in data: s += f"; phase={data.get('phase')}"
        if "rows" in data and isinstance(data["rows"], list): s += f"; rows={len(data['rows'])}"
        if "data" in data and isinstance(data["data"], dict): s += "; dataFields=" + ",".join(list(data["data"].keys())[:16])
        return s
    if isinstance(data, list):
        return f"listRows={len(data)}"
    return type(data).__name__


def main() -> None:
    rows: list[dict[str, Any]] = []
    scan_roots = [
        ROOT / "stock-news-backend",
        ROOT / "skills",
        ROOT / "memory",
        ROOT / "claude_handoff",
        ROOT / "reports",
        ROOT,
    ]
    seen: set[Path] = set()
    for base in scan_roots:
        if not base.exists():
            continue
        iterator = base.rglob("*") if base != ROOT else base.glob("*")
        for path in iterator:
            if not path.is_file() or skip(path):
                continue
            path = path.resolve()
            if path in seen:
                continue
            seen.add(path)
            if path.suffix.lower() not in EXTS:
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            # Search path first, then content for smaller text-ish files.
            text = ""
            if path.suffix.lower() not in {".xlsx", ".xls", ".zip"} and path.stat().st_size <= 3_000_000:
                text = safe_read(path)
            score, hits = keyword_score(path, text)
            if score == 0:
                continue
            source, role, owner, desc = classify(path, text, hits)
            json_summary = summarize_json(path) if path.suffix.lower() == ".json" and path.stat().st_size <= 5_000_000 else ""
            rows.append({
                "path": rel,
                "name": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "role": role,
                "source_hint": source,
                "owner_hint": owner,
                "keyword_hits": "; ".join(hits),
                "description": desc,
                "json_summary": json_summary,
            })
    rows.sort(key=lambda r: (r["role"], r["source_hint"], r["path"]))
    csv_path = OUT / "macro_data_inventory.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["path"])
        w.writeheader(); w.writerows(rows)
    json_path = OUT / "macro_data_inventory.json"
    json_path.write_text(json.dumps({"createdAt": datetime.now(timezone.utc).isoformat(), "count": len(rows), "items": rows}, ensure_ascii=False, indent=2), encoding="utf-8")

    by_role: dict[str,int] = {}
    by_source: dict[str,int] = {}
    for r in rows:
        by_role[r["role"]] = by_role.get(r["role"],0)+1
        by_source[r["source_hint"]] = by_source.get(r["source_hint"],0)+1
    md = []
    md.append("# Macro Data Inventory - LH Investment Workspace\n")
    md.append(f"Created: {datetime.now().isoformat(timespec='seconds')}\n")
    md.append(f"Total macro-related files detected: **{len(rows)}**\n")
    md.append("## Counts by role\n")
    for k,v in sorted(by_role.items()): md.append(f"- {k}: {v}")
    md.append("\n## Counts by source hint\n")
    for k,v in sorted(by_source.items()): md.append(f"- {k}: {v}")
    md.append("\n## High-priority usable macro data/code\n")
    priority = [r for r in rows if r["path"] in {
        "stock-news-backend/data/macro_cycle_local.json",
        "stock-news-backend/data/macro_overview.json",
        "stock-news-backend/data/macro_probe_local/sbv_probe.json",
        "stock-news-backend/app/macro_cycle.py",
        "stock-news-backend/build_macro_local_page.py",
        "skills/vn-macro-cycle-research/SKILL.md",
        "skills/vn-macro-cycle-research/references/macro-source-map.md",
        "claude_handoff/vn_macro_research_pack_2026-06-05.zip",
    }]
    for r in priority:
        md.append(f"- `{r['path']}` — {r['role']} — {r['source_hint']} — {r['description']} {r['json_summary']}")
    md.append("\n## Full inventory\n")
    for r in rows:
        md.append(f"### `{r['path']}`")
        md.append(f"- role: {r['role']}")
        md.append(f"- source_hint: {r['source_hint']}")
        md.append(f"- owner_hint: {r['owner_hint']}")
        md.append(f"- size: {r['size_bytes']} bytes; modified: {r['modified']}")
        if r['description']: md.append(f"- description: {r['description']}")
        if r['json_summary']: md.append(f"- json_summary: {r['json_summary']}")
        md.append(f"- keyword_hits: {r['keyword_hits']}\n")
    md_path = OUT / "macro_data_inventory.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"count": len(rows), "csv": str(csv_path), "json": str(json_path), "md": str(md_path)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
