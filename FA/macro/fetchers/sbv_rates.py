"""
Fetcher: SBV/NHNN Interest Rates — Chính thức từ sbv.gov.vn
============================================================
Strategy (theo thứ tự ưu tiên):

  1. SBV weekly PDF press release (CONFIRMED WORKING)
     - Listing: https://www.sbv.gov.vn/vi/web/sbv_portal/thông-tin-về-hoạt-động-ngân-hàng-trong-tuần
     - Scrape HTML → find latest article URL → fetch article → extract PDF URL → download PDF → parse
     - Data: VND/USD interbank rates overnight/1W/2W/1M/3M/6M/9M (weekly frequency)

  2. Pinetree Morning Brief cross-reference (daily, already fetched)
     - overnight rate only, from shared snapshot

  3. Manual override JSON (fallback)
     - FA/data/manual_override.json

Dữ liệu trả về:
  {
    "vnd": {"overnight": 7.26, "1w": 7.41, "1m": 7.30, "3m": 7.66, "6m": 8.12},
    "usd": {"overnight": 3.63, "1w": 3.68, "1m": 3.74, "3m": 3.86},
    "weekRange": "25-29.5.2026",
    "source": "sbv_weekly_pdf",
    "pdfUrl": "...",
  }

Install: pip install pypdf  (hoặc pypdf2 / pdfplumber nếu muốn)
"""
from __future__ import annotations

import io
import json
import re
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any

SOURCE_NAME = "SBV/NHNN Interbank Rates"
PARSER_VERSION = "sbv_v2_pdf"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LHInvestment/macro-sbv"

LISTING_URL = (
    "https://www.sbv.gov.vn/vi/web/sbv_portal/"
    "th%C3%B4ng-tin-v%E1%BB%81-ho%E1%BA%A1t-%C4%91%E1%BB%99ng-ng%C3%A2n-h%C3%A0ng-trong-tu%E1%BA%A7n"
)
SBV_BASE = "https://www.sbv.gov.vn"

MANUAL_OVERRIDE_PATH = Path(__file__).resolve().parents[2] / "data" / "manual_override.json"


# ── HTTP ─────────────────────────────────────────────────────────────────
def _get(url: str, timeout: int = 15, binary: bool = False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/pdf,text/html,*/*",
        "Accept-Language": "vi,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read() if binary else r.read().decode("utf-8", errors="ignore")


def _num(s: Any) -> float | None:
    if s is None or str(s).strip() in ("-", ""):
        return None
    try:
        return float(str(s).replace(",", ".").strip())
    except Exception:
        return None


# ── Source 1a: Scrape listing → get latest article URL ───────────────────
def _find_latest_article_url(html: str) -> str | None:
    """
    Tìm href bài viết mới nhất trên trang listing.
    Pattern: /vi/web/sbv_portal/w/diễn-biến-thị-trường-...liên-ngân-hàng...
    """
    # Primary pattern: href inside anchor with keyword
    patterns = [
        r'href="(https://www\.sbv\.gov\.vn(?:/vi)?/(?:web/sbv_portal/)?w/di%E1%BB%85n-bi%E1%BA%BFn[^"]+li%C3%AAn-ng%C3%A2n-h%C3%A0ng[^"]*)"',
        r'href="(/(?:vi/)?web/sbv_portal/w/di%E1%BB%85n-bi%E1%BA%BFn[^"]+li%C3%AAn-ng%C3%A2n-h%C3%A0ng[^"]*)"',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            url = m.group(1)
            if not url.startswith("http"):
                url = SBV_BASE + url
            # Remove redirect param
            url = url.split("?")[0]
            return url
    return None


# ── Source 1b: From article page → extract PDF URL ───────────────────────
def _find_pdf_url(html: str) -> str | None:
    """
    Extract PDF download URL from the article page.
    Pattern: /documents/20117/... .pdf/uuid
    """
    patterns = [
        r'href="(https://www\.sbv\.gov\.vn/documents/[^"]+\.pdf[^"]*)"',
        r'href="(/documents/[^"]+\.pdf[^"]*)"',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            url = m.group(1)
            if not url.startswith("http"):
                url = SBV_BASE + url
            return url
    return None


# ── Source 1c: Parse PDF bytes → extract rates ───────────────────────────
def _parse_pdf_bytes(pdf_bytes: bytes) -> dict[str, Any]:
    """
    Parse PDF binary. Uses pypdf (pip install pypdf) or falls back to text heuristics.
    PDF text layout (confirmed from sbv.gov.vn PDF):

        Qua đêm 1 tuần 2 tuần 1 tháng 3 tháng 6 tháng 9 tháng
        VND  7,26  7,41  7,40  7,30  7,66  8,12  8,50
        USD  3,63  3,68  3,74  3,74  3,86  4,16  -
    """
    text = ""

    # Try pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    except ImportError:
        pass
    except Exception:
        pass

    # Try pdfplumber
    if not text.strip():
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
        except ImportError:
            pass
        except Exception:
            pass

    # Fallback: try to decode PDF as utf-8 text (works on some simple PDFs)
    if not text.strip():
        try:
            text = pdf_bytes.decode("utf-8", errors="ignore")
        except Exception:
            pass

    if not text.strip():
        return {"status": "pdf_parse_failed", "note": "install pypdf: pip install pypdf"}

    return _extract_rates_from_text(text)


def _extract_rates_from_text(text: str) -> dict[str, Any]:
    """
    Parse rate table from PDF text content.
    Handles both column-header-then-row and embedded sentence formats.
    """
    result: dict[str, Any] = {"rawText": text[:500]}

    # Extract week range
    week_m = re.search(r"[Tt]uần\s+(?:từ\s+)?(\d{1,2}[-–]\d{1,2}[.\s/]\d{1,2}[.\s/]\d{4})", text)
    if week_m:
        result["weekRange"] = week_m.group(1).strip()

    # ── Method 1: Table row parsing ──
    # Look for table header: "Qua đêm" or "qua đêm"
    # then rows: "VND 7,26 7,41 ..." and "USD 3,63 ..."
    TENORS = ["overnight", "1w", "2w", "1m", "3m", "6m", "9m"]

    def _parse_row(row_text: str) -> list[float | None]:
        nums = re.findall(r"(\d+[,\.]\d+|-)", row_text)
        return [_num(n) for n in nums]

    # Find VND row
    vnd_m = re.search(r"\bVND\b(.{10,80})", text, re.I)
    usd_m = re.search(r"\bUSD\b(.{10,80})", text, re.I)

    if vnd_m:
        vnd_vals = _parse_row(vnd_m.group(1))
        vnd_dict = {}
        for i, tenor in enumerate(TENORS):
            if i < len(vnd_vals):
                vnd_dict[tenor] = vnd_vals[i]
        if vnd_dict:
            result["vnd"] = vnd_dict

    if usd_m:
        usd_vals = _parse_row(usd_m.group(1))
        usd_dict = {}
        for i, tenor in enumerate(TENORS):
            if i < len(usd_vals):
                usd_dict[tenor] = usd_vals[i]
        if usd_dict:
            result["usd"] = usd_dict

    # ── Method 2: Sentence extraction as fallback ──
    # e.g. "lãi suất bình quân kỳ hạn qua đêm ... lên các mức 7,26%/năm, 7,41%/năm và 7,30%/năm"
    if "vnd" not in result:
        sent_m = re.search(
            r"qua\s*đêm.*?(\d+[,\.]\d+)\s*%.*?01\s*tuần.*?(\d+[,\.]\d+)\s*%.*?01\s*tháng.*?(\d+[,\.]\d+)\s*%",
            text, re.I | re.S
        )
        if sent_m:
            result["vnd"] = {
                "overnight": _num(sent_m.group(1)),
                "1w":        _num(sent_m.group(2)),
                "1m":        _num(sent_m.group(3)),
            }

    # FX: extract end-of-week USD/VND rate
    fx_m = re.search(r"(\d{2,3}[.\s]?\d{3})\s*/\s*(\d{2,3}[.\s]?\d{3})\s*VND/USD", text)
    if fx_m:
        buy_str  = fx_m.group(1).replace(" ", "").replace(".", "")
        sell_str = fx_m.group(2).replace(" ", "").replace(".", "")
        result["usdVnd"] = {
            "buy":  _num(buy_str),
            "sell": _num(sell_str),
        }

    result["status"] = "ok" if ("vnd" in result or "usd" in result) else "parse_empty"
    return result


# ── Full SBV weekly PDF pipeline ─────────────────────────────────────────
def _fetch_sbv_weekly_pdf() -> dict[str, Any]:
    """
    Pipeline:
      listing page → latest article URL → article page → PDF URL → PDF bytes → parse
    """
    try:
        # Step 1: listing
        listing_html = _get(LISTING_URL, timeout=15)
        article_url = _find_latest_article_url(listing_html)
        if not article_url:
            return {"status": "no_article_url", "source": "sbv_listing"}

        # Step 2: article page
        article_html = _get(article_url, timeout=12)
        pdf_url = _find_pdf_url(article_html)
        if not pdf_url:
            return {"status": "no_pdf_url", "articleUrl": article_url, "source": "sbv_article"}

        # Step 3: download PDF
        pdf_bytes = _get(pdf_url, timeout=20, binary=True)
        if not pdf_bytes:
            return {"status": "empty_pdf", "pdfUrl": pdf_url}

        # Step 4: parse
        parsed = _parse_pdf_bytes(pdf_bytes)
        parsed["source"] = "sbv_weekly_pdf"
        parsed["pdfUrl"] = pdf_url
        parsed["articleUrl"] = article_url
        parsed["fetchedAt"] = datetime.now().isoformat()
        return parsed

    except Exception as e:
        return {"status": "error", "source": "sbv_weekly_pdf", "error": str(e)[:150]}


# ── Source 2: Pinetree snapshot cross-reference ───────────────────────────
def _get_from_pinetree_snapshot() -> dict[str, Any]:
    try:
        hist_dir = Path(__file__).resolve().parents[2] / "data" / "history"
        if not hist_dir.exists():
            return {"status": "no_history"}
        # History snapshots are saved as ISO dates: YYYY-MM-DD.json.
        # Older code used a dotted glob (????.??.??.json), which never matched
        # current files and caused the Pinetree fallback to fail even when the
        # daily macro database already had an interbank overnight value.
        files = sorted(hist_dir.glob("????-??-??.json"), reverse=True)
        if not files:
            return {"status": "no_history"}
        snap = json.loads(files[0].read_text(encoding="utf-8"))
        # Check merged or pinetree
        for key in ("mergedPinetree", "pinetree"):
            pt = snap.get(key, {})
            ib = pt.get("interbankOvernight", {})
            val = ib.get("value") if isinstance(ib, dict) else None
            if val is not None:
                return {
                    "status": "ok",
                    "source": f"pinetree_snapshot:{files[0].stem}",
                    "vnd": {
                        "overnight": val,
                        "overnight_1d_bps": ib.get("change1d"),
                        "overnight_ytd_bps": ib.get("ytd"),
                    }
                }
        return {"status": "no_interbank_value"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}


# ── Source 3: Manual override ─────────────────────────────────────────────
def _read_manual_override() -> dict[str, Any]:
    if not MANUAL_OVERRIDE_PATH.exists():
        return {"status": "no_file"}
    try:
        data = json.loads(MANUAL_OVERRIDE_PATH.read_text(encoding="utf-8"))
        sbv = data.get("sbvRates", {})
        if sbv and any(v is not None for v in sbv.values()):
            return {"status": "ok", "source": "manual_override",
                    "date": data.get("date", ""),
                    "vnd": {"overnight": sbv.get("overnight")},
                    **{k: v for k, v in sbv.items() if k != "overnight"}}
        return {"status": "empty"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:80]}


# ── Public interface ──────────────────────────────────────────────────────
def fetch(prefer_source: str = "auto") -> dict[str, Any]:
    """
    Fetch SBV interbank rates via best available source.

    Returns:
    {
      "source": "sbv_weekly_pdf",
      "weekRange": "25-29.5.2026",
      "pdfUrl": "...",
      "vnd": {
        "overnight": 7.26,
        "1w": 7.41, "2w": 7.40, "1m": 7.30, "3m": 7.66, "6m": 8.12, "9m": 8.50
      },
      "usd": {
        "overnight": 3.63, "1w": 3.68, "2w": 3.74, "1m": 3.74, "3m": 3.86, "6m": 4.16
      },
      "usdVnd": {"buy": 26115, "sell": 26395},
      "status": "ok"
    }
    """
    sources = [
        ("sbv_pdf",   _fetch_sbv_weekly_pdf),
        ("pinetree",  _get_from_pinetree_snapshot),
        ("manual",    _read_manual_override),
    ]

    last_error = None
    for name, fn in sources:
        if prefer_source != "auto" and name != prefer_source:
            continue
        result = fn()
        if result.get("status") == "ok" and ("vnd" in result or "usd" in result):
            return {
                "parserVersion": PARSER_VERSION,
                "fetchedAt": datetime.now().isoformat(),
                **result,
            }
        last_error = result.get("error") or result.get("status")

    return {
        "source": SOURCE_NAME,
        "parserVersion": PARSER_VERSION,
        "status": "all_failed",
        "lastError": str(last_error)[:200],
        "note": (
            "Nếu sbv_weekly_pdf fail: cài 'pip install pypdf'. "
            "Hoặc điền tay vào data/manual_override.json."
        ),
    }


# ── CLI test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    prefer = sys.argv[1] if len(sys.argv) > 1 else "auto"
    result = fetch(prefer_source=prefer)
    # Print clean summary
    print(f"\n=== SBV Interbank Rates ===")
    print(f"Source  : {result.get('source', '?')}")
    print(f"Status  : {result.get('status', '?')}")
    print(f"Week    : {result.get('weekRange', 'N/A')}")
    vnd = result.get("vnd", {})
    usd = result.get("usd", {})
    if vnd:
        print(f"\nVND rates (%/year):")
        for k, v in vnd.items():
            if v is not None:
                print(f"  {k:<12}: {v}")
    if usd:
        print(f"\nUSD rates (%/year):")
        for k, v in usd.items():
            if v is not None:
                print(f"  {k:<12}: {v}")
    if result.get("usdVnd"):
        fx = result["usdVnd"]
        print(f"\nUSD/VND  : {fx.get('buy')} / {fx.get('sell')}")
    if result.get("pdfUrl"):
        print(f"\nPDF     : {result['pdfUrl']}")
    if result.get("note"):
        print(f"\nNote    : {result['note']}")
    print()
