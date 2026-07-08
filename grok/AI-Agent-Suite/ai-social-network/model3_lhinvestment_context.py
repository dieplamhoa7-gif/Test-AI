from __future__ import annotations

import email.utils
import json
import os
import re
import importlib.util
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import math

def _detect_workspace() -> Path:
    env = os.environ.get("OPENCLAW_WORKSPACE") or os.environ.get("WORKSPACE")
    if env and Path(env).exists():
        return Path(env)
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "AGENTS.md").exists() or (p / "tmp_lh_push_clean").exists():
            return p
    # ai-social-network is workspace/grok/AI-Agent-Suite/ai-social-network
    if len(here.parents) >= 4:
        return here.parents[3]
    return Path.cwd()


WORKSPACE = _detect_workspace()
LH_ROOTS = [
    # Current clean/live reference must win: Hòa Đại ka wants Model3/Codex to anchor reports
    # to LHINVT_WEB_CLEAN first because it is local, fast, and mirrors lhinvt.web.app data.
    WORKSPACE / "LHINVT_WEB_CLEAN",
    # Main repo is fallback if clean copy misses a file/symbol.
    WORKSPACE / "stock-news-backend",
    WORKSPACE / "tmp_lh_push_clean" / "stock-news-backend",
    WORKSPACE / "CLAUDE_INVESTMENT_MODEL_REVIEW" / "stock-news-backend",
    # Restored backup is last fallback only; never prefer it over LHINVT_WEB_CLEAN/current repo.
    WORKSPACE / "_restore_lhinvestment_from_backup_20260626",
]

LHINVT_LIVE_BASE = os.environ.get("LHINVT_LIVE_BASE", "https://lhinvt.web.app").rstrip("/")

DEFAULT_RSS_URLS = [
    # Override/extend via SUPERLH_MODEL3_RSS_URLS="url1,url2" if CafeF/Vietstock changes feed paths.
    "https://cafef.vn/thi-truong-chung-khoan.rss",
    "https://cafef.vn/doanh-nghiep.rss",
    "https://cafef.vn/tai-chinh-chung-khoan.rss",
    "https://vietstock.vn/830/chung-khoan.rss",
    "https://vietstock.vn/737/doanh-nghiep.rss",
]

NEWS_SEARCH_SITES = [
    "cafef.vn", "vietstock.vn", "fireant.vn", "24hmoney.vn",
    "ssi.com.vn", "iboard.ssi.com.vn", "hsx.vn", "hnx.vn",
]


def extract_symbol(task: str) -> str:
    text = (task or "").upper()
    # Prefer explicit Vietnamese stock tickers: 3-5 uppercase chars/digits, common HOSE/HNX style.
    skip = {"MODEL", "HTML", "FILE", "NEWS", "CODEX", "KIRO", "VN", "USD", "CEO", "CFO"}
    candidates = re.findall(r"\b[A-Z]{2,5}\d?\b", text)
    for c in candidates:
        if c not in skip and not c.startswith("MODEL"):
            return c
    return ""


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _clip(s: str, n: int = 700) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n].rstrip() + "…"


def _find_first_existing(rel: str) -> Path | None:
    rel = rel.replace("\\", os.sep)  # portability: rel viết kiểu Windows vẫn chạy trên POSIX
    for root in LH_ROOTS:
        p = root / rel
        if p.exists():
            return p
    return None


def _manual_price_override(symbol: str) -> dict[str, Any] | None:
    paths = [Path(__file__).resolve().parent / "data" / "manual_price_overrides.json"]
    sym = symbol.upper().strip()
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data.get("items") if isinstance(data, dict) else None
            item = items.get(sym) if isinstance(items, dict) else None
            if isinstance(item, dict) and item.get("close") is not None:
                return item
        except Exception:
            continue
    return None


def _latest_local_clean_snapshot(symbol: str) -> dict[str, Any] | None:
    """Fast local source: LHINVT_WEB_CLEAN mirrors the current lhinvt.web.app data.

    Prefer this over importing stock-news-backend.market_data because it is lighter and
    avoids live library/cache side effects. Values still need freshness checks against
    chart/EOD rows in _indicator_matrix_raw.
    """
    sym = symbol.upper().strip()
    clean = WORKSPACE / "LHINVT_WEB_CLEAN"
    if not clean.exists():
        return None
    rels = [
        r"firebase_public\data\market_data.json",
        r"data\market_data.json",
        r"firebase_public\data\market_watch.json",
        r"data\market_watch.json",
        rf"firebase_public\data\charts\{sym}.json",
        rf"firebase_public\data\charts\{sym}_day.json",
    ]
    candidates: list[tuple[str, Any, float]] = []
    for rel in rels:
        p = clean / rel.replace("\\", os.sep)
        data = _read_json(p) if p.exists() else None
        rec = _find_symbol_record(data, sym) if data is not None else None
        if rec is None and isinstance(data, dict) and ("rows" in data or "data" in data):
            rec = data
        if rec is None:
            continue
        _, ts = _record_date_score(rec)
        candidates.append((str(p), rec, ts))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[2], reverse=True)
    src, rec, _ = candidates[0]
    return {
        "ok": True,
        "source": f"LHINVT_WEB_CLEAN local cache ({src})",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "symbol": rec,
        "macro_index_overview": {},
    }


def _latest_lhinvt_live_snapshot(symbol: str) -> dict[str, Any] | None:
    """Fallback to the currently deployed LHINVT web JSON if local clean copy misses data."""
    sym = symbol.upper().strip()
    headers = {"User-Agent": "SuperLH-Model3/1.0"}
    endpoints = [
        f"{LHINVT_LIVE_BASE}/data/market_data.json",
        f"{LHINVT_LIVE_BASE}/data/market_watch.json",
        f"{LHINVT_LIVE_BASE}/data/charts/{sym}.json",
        f"{LHINVT_LIVE_BASE}/data/charts/{sym}_day.json",
    ]
    candidates: list[tuple[str, Any, float]] = []
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=10, params={"ts": int(datetime.now(timezone.utc).timestamp())})
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception:
            continue
        rec = _find_symbol_record(data, sym)
        if rec is None and isinstance(data, dict) and ("rows" in data or "data" in data):
            rec = data
        if rec is None:
            continue
        _, ts = _record_date_score(rec)
        candidates.append((url, rec, ts))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[2], reverse=True)
    url, rec, _ = candidates[0]
    return {
        "ok": True,
        "source": f"{LHINVT_LIVE_BASE} live JSON ({url})",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "symbol": rec,
        "macro_index_overview": {},
    }


def _latest_live_market_snapshot(symbol: str) -> dict[str, Any]:
    local = _latest_local_clean_snapshot(symbol)
    if local:
        return local
    live = _latest_lhinvt_live_snapshot(symbol)
    if live:
        return live
    """Force refresh current PTKT/price/index data from stock-news-backend.

    Hòa Đại ka updates prices daily, so Model3 must prefer this live fetch over
    stale JSON caches. If it fails, return an explicit error and let the report
    say data is missing instead of silently trusting old price 80-style caches.
    """
    backend = WORKSPACE / "stock-news-backend"
    if not backend.exists():
        return {"ok": False, "error": f"stock-news-backend not found at {backend}"}
    module_path = backend / "app" / "market_data.py"
    if not module_path.exists():
        return {"ok": False, "error": f"market_data.py not found at {module_path}"}
    try:
        spec = importlib.util.spec_from_file_location("superlh_live_market_data", module_path)
        if spec is None or spec.loader is None:
            return {"ok": False, "error": f"Cannot load spec for {module_path}"}
        mod = importlib.util.module_from_spec(spec)
        sys.modules["superlh_live_market_data"] = mod
        spec.loader.exec_module(mod)
        override = _manual_price_override(symbol)
        if override:
            return {
                "ok": True,
                "source": "manual_price_overrides.json verified override",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "symbol": {
                    "ticker": symbol.upper(),
                    "close": override.get("close"),
                    "price": override.get("close"),
                    "asOfDate": override.get("date"),
                    "source": override.get("source") or "manual verified source",
                    "note": override.get("note") or "Manual override because library/cache source is stale or inconsistent.",
                },
                "macro_index_overview": {},
            }
        eod_close = getattr(mod, "_get_latest_eod_close", lambda _s: None)(symbol.upper())
        if eod_close is not None:
            symbol_data = {
                "ticker": symbol.upper(),
                "close": eod_close,
                "price": eod_close,
                "source": "vnstock.Quote.history EOD",
            }
            try:
                base = mod.get_market_symbol(symbol.upper(), force_refresh=False)
                if isinstance(base, dict):
                    base.update(symbol_data)
                    symbol_data = base
            except Exception:
                pass
            index_data = mod.get_index_overview(force_refresh=False)
            return {
                "ok": True,
                "source": "stock-news-backend.app.market_data vnstock EOD first",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "symbol": symbol_data,
                "macro_index_overview": index_data,
            }
        symbol_data = mod.get_market_symbol(symbol.upper(), force_refresh=False)
        index_data = mod.get_index_overview(force_refresh=False)
        return {
            "ok": True,
            "source": "stock-news-backend.app.market_data cached fallback",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol_data,
            "macro_index_overview": index_data,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "source": "stock-news-backend.app.market_data vnstock EOD first", "error": f"{type(exc).__name__}: {exc}"}
    finally:
        sys.modules.pop("superlh_live_market_data", None)


def _record_date_score(rec: Any) -> tuple[str, float]:
    candidates = []
    for names in (("asOfDate", "date", "tradingDate", "updated_at", "time", "fetched_at", "lastUpdated"),):
        v = _deep_find_key(rec, names)
        if v not in (None, ""):
            candidates.append(str(v))
    raw = candidates[0] if candidates else ""
    try:
        norm = raw.replace("Z", "+00:00")
        ts = datetime.fromisoformat(norm[:10] if re.match(r"^\d{4}-\d{2}-\d{2}$", norm[:10]) else norm).timestamp()
    except Exception:
        ts = 0.0
    return raw, ts



def _google_news_rss_urls(symbol: str) -> list[str]:
    year = datetime.now().year
    sym = symbol.upper()
    queries = [
        f'{sym} cổ phiếu doanh nghiệp {year}',
        f'{sym} kết quả kinh doanh cổ tức phát hành M&A pháp lý {year}',
        f'{sym} site:cafef.vn OR site:vietstock.vn OR site:fireant.vn {year}',
    ]
    import urllib.parse
    return [
        'https://news.google.com/rss/search?q=' + urllib.parse.quote_plus(q) + '&hl=vi&gl=VN&ceid=VN:vi'
        for q in queries
    ]

def _rss_urls() -> list[str]:
    raw = os.environ.get("SUPERLH_MODEL3_RSS_URLS", "").strip()
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return DEFAULT_RSS_URLS


def _parse_rss_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        dt = email.utils.parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return value


def fetch_rss_news(symbol: str, limit: int = 10) -> list[dict[str, str]]:
    sym = symbol.upper()
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    headers = {"User-Agent": "Mozilla/5.0 SuperLHBot/1.0"}
    for url in [*_rss_urls(), *_google_news_rss_urls(symbol)]:
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
        except Exception:
            continue
        source = "cafef" if "cafef" in url.lower() else ("vietstock" if "vietstock" in url.lower() else "rss")
        for item in root.findall(".//item"):
            title = "".join(item.findtext("title") or "").strip()
            link = "".join(item.findtext("link") or "").strip()
            desc = "".join(item.findtext("description") or "").strip()
            pub = _parse_rss_date(item.findtext("pubDate") or item.findtext("published") or "")
            hay = f" {title} {desc} ".upper()
            if not (re.search(rf"(?<![A-Z0-9]){re.escape(sym)}(?![A-Z0-9])", hay) or sym in title.upper()):
                continue
            key = link or title
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append({
                "source": source + "-rss",
                "title": title,
                "url": link,
                "published_at": pub,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "snippet": _clip(re.sub(r"<[^>]+>", " ", desc), 500),
            })
    rows.sort(key=lambda x: x.get("published_at") or x.get("fetched_at") or "", reverse=True)
    return rows[:limit]


def load_cache_news(symbol: str, limit: int = 10) -> list[dict[str, str]]:
    p = _find_first_existing(r"data\news_cache.json") or _find_first_existing(r"firebase_public\data\news_cache.json")
    data = _read_json(p) if p else []
    if not isinstance(data, list):
        return []
    sym = symbol.upper()
    rows: list[dict[str, str]] = []
    for item in data:
        title = str(item.get("title") or "")
        body = " ".join(str(item.get(k) or "") for k in ("snippet", "fullText", "summary"))
        hay = f" {title} {body} ".upper()
        if re.search(rf"(?<![A-Z0-9]){re.escape(sym)}(?![A-Z0-9])", hay) or sym in title.upper():
            rows.append({
                "source": str(item.get("source") or ""),
                "title": title,
                "url": str(item.get("url") or ""),
                "published_at": str(item.get("published_at") or ""),
                "fetched_at": str(item.get("fetched_at") or ""),
                "snippet": _clip(item.get("snippet") or item.get("fullText") or "", 500),
            })
    return rows[:limit]


def load_archive_news(symbol: str, limit: int = 30) -> list[dict[str, str]]:
    """Search LHInvestment monthly archives + 24hmoney reports for symbol-related news."""
    sym = symbol.upper()
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    rels = [
        r"data\news_archive_202606.json",
        r"firebase_public\data\news_archive_202606.json",
        r"data\24hmoney_reports.json",
        r"firebase_public\data\24hmoney_reports.json",
    ]
    for rel in rels:
        p = _find_first_existing(rel)
        data = _read_json(p) if p else None
        stack0 = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
        stack = []
        for x in stack0:
            if isinstance(x, list):
                stack.extend(x)
            else:
                stack.append(x)
        for item in stack:
            if isinstance(item, dict):
                title = str(item.get("title") or item.get("headline") or item.get("name") or "")
                body = " ".join(str(item.get(k) or "") for k in ("snippet", "summary", "content", "fullText", "text", "body"))
                url = str(item.get("url") or item.get("link") or "")
                source = str(item.get("source") or item.get("site") or rel)
                date = str(item.get("published_at") or item.get("date") or item.get("created_at") or item.get("fetched_at") or "")
            else:
                title = str(item); body = ""; url = ""; source = rel; date = ""
            hay = f" {title} {body} ".upper()
            if not (re.search(rf"(?<![A-Z0-9]){re.escape(sym)}(?![A-Z0-9])", hay) or sym in title.upper()):
                continue
            key = url or title
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append({"source": source, "title": title, "url": url, "published_at": date, "fetched_at": "", "snippet": _clip(body, 700)})
    return rows[:limit]


def fetch_yahoo_fundamental(symbol: str) -> dict[str, Any]:
    """Best-effort Yahoo Finance quoteSummary for .VN/.HM. Does not fail workflow."""
    candidates = [f"{symbol}.VN", f"{symbol}.HM", symbol]
    modules = "price,summaryDetail,defaultKeyStatistics,financialData,assetProfile,earnings"
    headers = {"User-Agent": "Mozilla/5.0 SuperLHBot/1.0"}
    for ticker in candidates:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules={modules}"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            result = (((data or {}).get("quoteSummary") or {}).get("result") or [None])[0]
            if result:
                return {"ticker": ticker, "source": url, "data": result}
        except Exception:
            continue
    return {}


def _news_rank_score(n: dict[str, str], symbol: str) -> int:
    title = (n.get("title") or "").upper()
    body = (n.get("snippet") or "").upper()
    hay = title + " " + body
    score = 0
    aliases = {symbol.upper()}
    if symbol.upper() == "VPB":
        aliases.update({"VPBANK", "VIỆT NAM THỊNH VƯỢNG", "VIETNAM THINH VUONG"})
    if any(a in hay for a in aliases):
        score += 50
    if symbol.upper() in title or any(a in title for a in aliases if a != symbol.upper()):
        score += 30
    if re.search(r"KHUYẾN NGHỊ|GIÁ MỤC TIÊU|MUA|LỢI NHUẬN|KQKD|TRÁI PHIẾU|CỔ TỨC|PHÁT HÀNH|TĂNG TRƯỞNG|DOANH THU|LNTT|NIM|NỢ XẤU|TÍN DỤNG|CASA|LDR|SMBC", hay):
        score += 20
    if re.search(r"CHỨNG QUYỀN|CVPB|HOSE:\s*CVPB|CW\.|COVERED WARRANT", hay):
        score -= 80
    if re.search(r"NHỊP ĐẬP|VN-INDEX|THỊ TRƯỜNG|SẮC ĐỎ|RUNG LẮC", title):
        score -= 30
    return score


def curate_news(symbol: str, rows: list[dict[str, str]], limit: int = 12) -> list[dict[str, str]]:
    scored = []
    seen = set()
    for n in rows:
        key = n.get("url") or n.get("title")
        if not key or key in seen:
            continue
        seen.add(key)
        s = _news_rank_score(n, symbol)
        if s >= 30:
            nn = dict(n)
            nn["rank_score"] = str(s)
            scored.append(nn)
    scored.sort(key=lambda x: (int(x.get("rank_score") or 0), x.get("published_at") or x.get("fetched_at") or ""), reverse=True)
    return scored[:limit]


def load_news(symbol: str, limit: int = 10) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rss = fetch_rss_news(symbol, max(limit, 50))
    cache = load_cache_news(symbol, max(limit, 50))
    archive = load_archive_news(symbol, max(limit, 50))
    seen = set()
    merged_cache = []
    for n in [*cache, *archive]:
        key = n.get("url") or n.get("title")
        if key and key not in seen:
            seen.add(key); merged_cache.append(n)
    return rss[:limit], merged_cache[:max(limit, 50)]


def _find_symbol_record(obj: Any, symbol: str) -> Any:
    sym = symbol.upper()
    if isinstance(obj, dict):
        if sym in obj:
            return obj[sym]
        for key in ("symbol", "ticker", "code"):
            if str(obj.get(key, "")).upper() == sym:
                return obj
        for v in obj.values():
            found = _find_symbol_record(v, sym)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_symbol_record(v, sym)
            if found is not None:
                return found
    return None


def load_json_record(symbol: str, rels: list[str]) -> tuple[str, Any]:
    best_rel = ""
    best_rec = None
    best_ts = -1.0
    for rel in rels:
        p = _find_first_existing(rel)
        data = _read_json(p) if p else None
        rec = _find_symbol_record(data, symbol) if data is not None else None
        if rec is None:
            continue
        _, ts = _record_date_score(rec)
        # Prefer the freshest dated record. If no dates exist, keep the first hit by LH_ROOTS/rels priority.
        if best_rec is None or ts > best_ts:
            best_rel, best_rec, best_ts = rel, rec, ts
    return best_rel, best_rec


def _strategy_cache_candidates(symbol: str) -> list[Path]:
    """Current cache first; then any backup/trash cache that actually contains the symbol."""
    candidates: list[Path] = []
    for rel in (r"data\strategy_results_cache.json", r"firebase_public\data\strategy_results_cache.json"):
        p = _find_first_existing(rel)
        if p and p not in candidates:
            candidates.append(p)
    if candidates:
        # Perf: có cache chính thì dùng ngay, không quét toàn workspace (rglob cực chậm với node_modules/backup).
        return candidates
    sym = symbol.upper()
    shallow_dirs = [WORKSPACE, WORKSPACE / "data", WORKSPACE / "firebase_public" / "data", WORKSPACE / "backups"]
    for root in LH_ROOTS:
        shallow_dirs.extend([root, root / "data", root / "firebase_public" / "data"])
    seen: set[Path] = set()
    for d in shallow_dirs:
        p = d / "strategy_results_cache.json"
        if p in seen or p in candidates:
            continue
        seen.add(p)
        try:
            if p.exists() and sym in p.read_text(encoding="utf-8", errors="ignore").upper():
                candidates.append(p)
        except Exception:
            continue
    return candidates


def load_strategy_records(symbol: str, limit: int = 12) -> list[dict[str, Any]]:
    sym = symbol.upper()
    out: list[dict[str, Any]] = []
    for p in _strategy_cache_candidates(symbol):
        data = _read_json(p) if p else None
        if not isinstance(data, dict):
            continue
        source_path = str(p)
        for strategy in data.get("strategies") or []:
            if not isinstance(strategy, dict):
                continue
            sid = strategy.get("id")
            sname = strategy.get("name")
            for bucket in ("buy", "watchlist", "avoid", "sell", "hold"):
                rows = strategy.get(bucket) or []
                if not isinstance(rows, list):
                    continue
                for row in rows:
                    if isinstance(row, dict) and str(row.get("symbol") or "").upper() == sym:
                        item = dict(row)
                        item["bucket"] = bucket
                        item["strategyGroupId"] = sid
                        item["strategyGroupName"] = sname
                        item["strategySourcePath"] = source_path
                        out.append(item)
    # Rank BUY/WATCH first, then higher score.
    order = {"buy": 0, "watchlist": 1, "hold": 2, "avoid": 3, "sell": 4}
    out.sort(key=lambda x: (order.get(str(x.get("bucket")), 9), -float(x.get("rankScore") or x.get("score") or 0)))
    return out[:limit]


def compact_record(rec: Any, max_chars: int = 2500) -> str:
    if rec is None:
        return ""
    try:
        text = json.dumps(rec, ensure_ascii=False, indent=2)
    except Exception:
        text = str(rec)
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "…"


def _deep_find_key(obj: Any, names: tuple[str, ...]) -> Any:
    wanted = {n.lower() for n in names}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in wanted and v not in (None, ""):
                return v
        for v in obj.values():
            found = _deep_find_key(v, names)
            if found not in (None, ""):
                return found
    elif isinstance(obj, list):
        for v in obj[:20]:
            found = _deep_find_key(v, names)
            if found not in (None, ""):
                return found
    return None



def _sma(vals: list[float], n: int) -> float | None:
    return round(sum(vals[-n:]) / n, 4) if len(vals) >= n else None

def _ema_series(vals: list[float], n: int) -> list[float]:
    if not vals:
        return []
    k = 2 / (n + 1)
    out = [vals[0]]
    for v in vals[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out

def _rsi(vals: list[float], n: int = 14) -> float | None:
    if len(vals) <= n:
        return None
    gains=[]; losses=[]
    for a,b in zip(vals[-n-1:-1], vals[-n:]):
        d=b-a; gains.append(max(d,0)); losses.append(max(-d,0))
    avg_gain=sum(gains)/n; avg_loss=sum(losses)/n
    if avg_loss == 0:
        return 100.0
    return round(100 - 100/(1 + avg_gain/avg_loss), 2)

def _adx_di(highs: list[float], lows: list[float], closes: list[float], n: int = 14) -> tuple[float | None, float | None, float | None]:
    """Wilder ADX14, +DI14, -DI14 từ OHLC. Trả (None, None, None) nếu thiếu dữ liệu."""
    if len(closes) < 2 * n + 1:
        return (None, None, None)
    trs: list[float] = []
    plus_dm: list[float] = []
    minus_dm: list[float] = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm.append(up if (up > down and up > 0) else 0.0)
        minus_dm.append(down if (down > up and down > 0) else 0.0)
    # Wilder smoothing
    atr = sum(trs[:n])
    p_dm = sum(plus_dm[:n])
    m_dm = sum(minus_dm[:n])
    dxs: list[float] = []
    p_di = m_di = 0.0
    for i in range(n, len(trs)):
        atr = atr - atr / n + trs[i]
        p_dm = p_dm - p_dm / n + plus_dm[i]
        m_dm = m_dm - m_dm / n + minus_dm[i]
        if atr <= 0:
            continue
        p_di = 100 * p_dm / atr
        m_di = 100 * m_dm / atr
        denom = p_di + m_di
        if denom > 0:
            dxs.append(100 * abs(p_di - m_di) / denom)
    if len(dxs) < n:
        return (None, None, None)
    adx = sum(dxs[:n]) / n
    for x in dxs[n:]:
        adx = (adx * (n - 1) + x) / n
    return (round(adx, 2), round(p_di, 2), round(m_di, 2))

def _derived_indicators_from_history(symbol: str) -> dict[str, Any] | None:
    rel, rec = load_json_record(symbol, [r"data\vn100_history_from_2023.json"])
    if not isinstance(rec, dict):
        return None
    rows = rec.get("rows") if isinstance(rec.get("rows"), list) else None
    if not rows:
        return None
    rows = [r for r in rows if isinstance(r, dict) and r.get("close") not in (None, "")]
    if len(rows) < 30:
        return None
    closes=[float(r["close"]) for r in rows]
    highs=[float(r.get("high") or r["close"]) for r in rows]
    lows=[float(r.get("low") or r["close"]) for r in rows]
    vols=[float(r.get("volume") or 0) for r in rows]
    ema12=_ema_series(closes,12); ema26=_ema_series(closes,26)
    macd=[a-b for a,b in zip(ema12[-len(ema26):], ema26)] if ema26 else []
    sig=_ema_series(macd,9) if macd else []
    ma20=_sma(closes,20); std20=None
    if len(closes)>=20:
        m=sum(closes[-20:])/20; std20=(sum((x-m)**2 for x in closes[-20:])/20)**0.5
    adx14, plus_di14, minus_di14 = _adx_di(highs, lows, closes, 14)
    out={
        "source": rel + " (derived by Model3 from OHLCV, not guessed)",
        "asOfDate": rows[-1].get("time"), "close": closes[-1],
        "changePct": round((closes[-1]/closes[-2]-1)*100,2) if len(closes)>1 and closes[-2] else None,
        "volume": vols[-1], "avgVol20": _sma(vols,20),
        "volumeRatio": round(vols[-1]/_sma(vols,20),2) if _sma(vols,20) else None,
        "MA10": _sma(closes,10), "MA20": ma20, "MA50": _sma(closes,50), "MA100": _sma(closes,100), "MA200": _sma(closes,200),
        "RSI14": _rsi(closes,14),
        "MACD": round(macd[-1],4) if macd else None, "MACD_signal": round(sig[-1],4) if sig else None,
        "MACD_hist": round(macd[-1]-sig[-1],4) if macd and sig else None,
        "BB_upper": round(ma20+2*std20,4) if ma20 is not None and std20 is not None else None,
        "BB_mid": ma20, "BB_lower": round(ma20-2*std20,4) if ma20 is not None and std20 is not None else None,
        "bbPercent": round((closes[-1]-(ma20-2*std20))/(4*std20),4) if ma20 is not None and std20 not in (None,0) else None,
        "ADX14": adx14, "plusDI": plus_di14, "minusDI": minus_di14,
        "ROC20": round((closes[-1]/closes[-21]-1)*100,2) if len(closes)>20 and closes[-21] else None,
        "ret5": round((closes[-1]/closes[-6]-1)*100,2) if len(closes)>5 and closes[-6] else None,
        "support": round(min(lows[-20:]),4), "resistance": round(max(highs[-20:]),4),
    }
    return {k:v for k,v in out.items() if v is not None}

def _record_asof_date(rec: Any) -> str:
    if not isinstance(rec, dict):
        return ""
    for key in ("asOfDate", "date", "tradingDate", "updated_at", "time"):
        val = rec.get(key)
        if val:
            m = re.search(r"\d{4}-\d{2}-\d{2}", str(val))
            return m.group(0) if m else str(val)[:10]
    tech = rec.get("technical") if isinstance(rec.get("technical"), dict) else None
    return _record_asof_date(tech) if tech else ""


def _live_snapshot_asof(live_snapshot: dict[str, Any] | None) -> str:
    if isinstance(live_snapshot, dict) and isinstance(live_snapshot.get("symbol"), dict):
        return _record_asof_date(live_snapshot["symbol"])
    return ""


def _is_stale_cache_record(rec: Any, live_asof: str) -> bool:
    asof = _record_asof_date(rec)
    return bool(live_asof and asof and asof < live_asof)


def _indicator_matrix_raw(symbol: str, live_snapshot: dict[str, Any] | None = None) -> str:
    """Collect key LHInvestment indicators into a visible matrix for Model 3 agents."""
    records: list[tuple[str, Any]] = []
    stale_notes: list[str] = []
    live_asof = _live_snapshot_asof(live_snapshot)
    if isinstance(live_snapshot, dict) and live_snapshot.get("ok") and isinstance(live_snapshot.get("symbol"), dict):
        records.append(("LIVE_MARKET_FORCE_REFRESH", live_snapshot["symbol"]))
    for label, rels in {
        "EOD": [r"data\v3_full_indicator_cache_v2.json", r"data\eod_all_stocks_hose_hnx.json", r"firebase_public\data\eod_all_stocks_hose_hnx.json", r"data\market_data.json", r"firebase_public\data\market_data.json"],
        "RS_LEVELS": [r"data\rs_levels_vn100_cache.json", r"data\rs_levels_hsx_all_cache.json", r"firebase_public\data\rs_levels_hsx_all_cache.json", r"data\rs_levels_only_cache.json"],
        "INDICATORS": [r"data\v3_full_indicator_cache_v2.json", r"data\lh_canonical_indicators_daily.json", r"data\weekly_indicators_vn100_cache.json", r"data\trading_agents_lite.json"],
        "TRADING_AGENTS_LITE": [r"data\trading_agents_lite.json"],
    }.items():
        rel, rec = load_json_record(symbol, rels)
        if rec is not None:
            if _is_stale_cache_record(rec, live_asof):
                stale_notes.append(f"Bỏ qua {label}:{rel} vì ngày {_record_asof_date(rec)} cũ hơn dữ liệu mới {live_asof}; không dùng làm giá/current indicator.")
                continue
            records.append((label, rec))
    keys = [
        ("asOfDate", ("asOfDate", "date", "tradingDate", "updated_at")),
        ("price/close", ("close", "price", "last", "lastPrice")),
        ("changePct", ("changePct", "pctChange", "percentChange", "change_percent")),
        ("volume", ("volume", "vol")),
        ("avgVol20", ("avgVol20", "avg_volume_20", "avgVolume20")),
        ("volumeRatio", ("volumeRatio", "volRatio")),
        ("MA10", ("MA10", "ma10")), ("MA20", ("MA20", "ma20")), ("MA50", ("MA50", "ma50")), ("MA100", ("MA100", "ma100")), ("MA200", ("MA200", "ma200")),
        ("RSI14", ("RSI14", "rsi14", "RSI", "rsi")),
        ("MACD", ("MACD", "macd")), ("MACD_signal", ("MACD_signal", "macdSignal", "signal")), ("MACD_hist", ("MACD_hist", "macdHist", "histogram")),
        ("ADX", ("ADX", "adx")), ("+DI", ("plusDI", "+DI", "diPlus", "pdi")), ("-DI", ("minusDI", "-DI", "diMinus", "mdi")),
        ("BB_upper", ("bbUpper", "bollingerUpper", "upper")), ("BB_mid", ("bbMiddle", "bbMid", "bollingerMid", "middle")), ("BB_lower", ("bbLower", "bollingerLower", "lower")), ("bbPercent", ("bbPercent", "bbPct", "percentB")),
        ("Ichimoku", ("ichimoku", "tenkan", "kijun", "cloud")),
        ("ROC20", ("ROC20", "roc20")), ("ret5", ("ret5", "return5")),
        ("support", ("support", "supports", "supportLevels")), ("resistance", ("resistance", "resistances", "resistanceLevels")), ("RS", ("rs", "rsLevel", "rs_levels")),
        ("rankScore", ("rankScore", "score")), ("buyScore", ("buyScore",)), ("riskScore", ("riskScore",)), ("action", ("action", "decision", "status")),
    ]
    lines = ["LHINVESTMENT INDICATOR MATRIX RAW (bắt buộc đưa vào báo cáo/NotebookLM; ưu tiên LIVE_MARKET_FORCE_REFRESH; nếu ô trống thì ghi Không có trong LHInvestment context):"]
    derived = _derived_indicators_from_history(symbol)
    if derived:
        if _is_stale_cache_record(derived, live_asof):
            stale_notes.append(f"Bỏ qua DERIVED_OHLCV vì ngày {_record_asof_date(derived)} cũ hơn dữ liệu mới {live_asof}; không dùng làm current indicator.")
        else:
            records.append(("DERIVED_OHLCV", derived))
            lines.append(f"Nguồn bổ sung DERIVED_OHLCV: {derived.get('source')} — tính lại từ lịch sử giá/volume local để tránh thiếu chỉ báo kỹ thuật.")
    if stale_notes:
        lines.append("STALE_CACHE_GUARD: " + " | ".join(stale_notes[:8]))
    for name, aliases in keys:
        vals = []
        for label, rec in records:
            val = _deep_find_key(rec, aliases)
            if val not in (None, ""):
                vals.append(f"{label}={val}")
        lines.append(f"- {name}: " + (" | ".join(vals[:5]) if vals else "Không có trong LHInvestment context"))
    return "\n".join(lines)


def build_lhinvestment_context(task: str) -> str:
    symbol = extract_symbol(task)
    if not symbol:
        return "LHINVESTMENT_CONTEXT: Không xác định được mã cổ phiếu từ yêu cầu. Hãy yêu cầu người dùng ghi rõ ticker."

    live_snapshot = _latest_live_market_snapshot(symbol)
    parts = [
        f"LHINVESTMENT_CONTEXT cho mã {symbol}",
        "NGUYÊN TẮC DỮ LIỆU: giá/current indicator luôn phải là dữ liệu mới nhất. Ưu tiên LHINVT_WEB_CLEAN local cache vì nhanh/nhẹ và đang mirror lhinvt.web.app; nếu thiếu thì fallback live lhinvt.web.app; sau cùng mới dùng stock-news-backend/vnstock/cache. Nếu cache cũ hơn ngày dữ liệu mới thì KHÔNG được dùng làm giá/current indicator; phải ghi rõ stale cache guard.",
        f"Nguồn ưu tiên: {WORKSPACE} / LHINVT_WEB_CLEAN -> {LHINVT_LIVE_BASE} -> stock-news-backend fallback.",
    ]
    if live_snapshot.get("ok"):
        parts.append("\nLIVE_MARKET_FORCE_REFRESH — dữ liệu giá/PTKT/vĩ mô mới nhất theo thứ tự LHINVT_WEB_CLEAN -> lhinvt.web.app -> stock-news-backend fallback:\n" + compact_record(live_snapshot, 4200))
    else:
        parts.append("\nLIVE_MARKET_FORCE_REFRESH: Không lấy được dữ liệu mới. Lỗi: " + str(live_snapshot.get("error") or "unknown") + ". Báo cáo phải cảnh báo thiếu dữ liệu mới, không dùng cache cũ làm giá hiện tại.")

    rss_news, cache_news = load_news(symbol, 50)
    curated_news = curate_news(symbol, [*rss_news, *cache_news], 12)
    parts.append("\nRSS/WEB NEWS MODEL 3 đang tự tra: CafeF/Vietstock RSS + Google News RSS query theo mã/năm hiện tại; có thể override RSS bằng SUPERLH_MODEL3_RSS_URLS.")
    for u in [*_rss_urls(), *_google_news_rss_urls(symbol)]:
        parts.append(f"- {u}")
    if curated_news:
        parts.append("\nMODEL3 CURATED NEWS CANDIDATES — đã lọc/rank sẵn, Kiro BẮT BUỘC chọn ít nhất 5 tin nếu danh sách này có >=5; loại chứng quyền/CVPB và tin thị trường chung yếu:")
        for i, n in enumerate(curated_news, 1):
            date = n.get("published_at") or n.get("fetched_at") or ""
            parts.append(f"{i}. rank={n.get('rank_score')} [{date}] {n.get('title')} — {n.get('source')}\n   URL: {n.get('url')}\n   Tóm tắt: {n.get('snippet')}")
    else:
        parts.append("\nMODEL3 CURATED NEWS CANDIDATES: Không đủ ứng viên news sau lọc/rank.")

    if rss_news:
        parts.append("\nTIN TỨC LIVE TỪ RSS CafeF/Vietstock/Google News (raw, để kiểm chứng):")
        for i, n in enumerate(rss_news, 1):
            date = n.get("published_at") or n.get("fetched_at") or ""
            parts.append(f"{i}. [{date}] {n.get('title')} — {n.get('source')}\n   URL: {n.get('url')}\n   Tóm tắt: {n.get('snippet')}")
    else:
        parts.append("\nTIN TỨC LIVE RSS: Không tìm thấy tin khớp mã trong RSS CafeF/Vietstock hoặc RSS tạm lỗi; dùng cache LHInvestment bên dưới, không được bịa tin cũ/không nguồn.")
    if cache_news:
        parts.append("\nTIN TỨC CACHE/ARCHIVE LHInvestment + 24HMONEY (fallback sau RSS, dùng để đủ tối thiểu 5 tin tác động):")
        for i, n in enumerate(cache_news, 1):
            date = n.get("published_at") or n.get("fetched_at") or ""
            parts.append(f"{i}. [{date}] {n.get('title')} — {n.get('source')}\n   URL: {n.get('url')}\n   Tóm tắt: {n.get('snippet')}")
    else:
        parts.append("\nTIN TỨC CACHE: Không tìm thấy tin khớp mã trong news_cache local.")

    parts.append("\n" + _indicator_matrix_raw(symbol, live_snapshot))

    strategies = load_strategy_records(symbol, 12)
    if strategies:
        parts.append("\nCHIẾN LƯỢC LH / STRATEGY_RESULTS_CACHE (bắt buộc Codex đánh giá từng chỉ báo trong các record này):")
        for i, st in enumerate(strategies, 1):
            parts.append(f"{i}. {st.get('strategyGroupName') or st.get('strategyGroupId')} | bucket={st.get('bucket')} | action={st.get('action')} | rankScore={st.get('rankScore')} | asOf={st.get('asOfDate')}\n{compact_record(st, 2200)}")
    else:
        parts.append("\nCHIẾN LƯỢC LH: Không tìm thấy tín hiệu strategy_results_cache cho mã này; thử gọi API live hoặc báo thiếu dữ liệu.")

    data_sets = {
        "EOD/giá/volume": [r"data\eod_all_stocks_hose_hnx.json", r"firebase_public\data\eod_all_stocks_hose_hnx.json", r"data\market_data.json", r"firebase_public\data\market_data.json"],
        "RS levels/hỗ trợ kháng cự": [r"data\rs_levels_hsx_all_cache.json", r"firebase_public\data\rs_levels_hsx_all_cache.json", r"data\rs_levels_vn100_cache.json", r"data\rs_levels_only_cache.json"],
        "Indicator daily LH canonical": [r"data\lh_canonical_indicators_daily.json", r"data\v3_full_indicator_cache_v2.json", r"data\trading_agents_lite.json"],
        "Fundamental signals": [r"data\fundamental_signals.json", r"firebase_public\data\fundamental_signals.json"],
        "Fundamental top upside/valuation": [r"data\fundamental_top_upside.json", r"firebase_public\data\fundamental_top_upside.json", r"data\fa_market_valuation_breadth_summary.json", r"firebase_public\data\fa_market_valuation_breadth_summary.json"],
        "Market overview": [r"data\market_overview.json", r"firebase_public\data\market_overview.json"],
        "TradingAgents lite": [r"data\trading_agents_lite.json"],
    }
    for label, rels in data_sets.items():
        rel, rec = load_json_record(symbol, rels)
        if rec is not None:
            parts.append(f"\n{label} ({rel}):\n{compact_record(rec, 2200)}")
        else:
            parts.append(f"\n{label}: Không tìm thấy record cho {symbol} trong cache local.")

    yahoo = fetch_yahoo_fundamental(symbol)
    if yahoo:
        parts.append("\nYahoo Finance fundamental/profile best-effort:\n" + compact_record(yahoo, 2600))
    else:
        parts.append("\nYahoo Finance fundamental/profile: Không lấy được dữ liệu Yahoo Finance cho mã này (.VN/.HM).")

    formula = _find_first_existing("TECHNICAL_FORMULA.md")
    if formula:
        try:
            parts.append("\nTECHNICAL_FORMULA.md (trích):\n" + formula.read_text(encoding="utf-8")[:2500])
        except Exception:
            pass
    return "\n".join(parts)
