from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report

WORKSPACE = Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace")
TEMP_DIR = WORKSPACE / "temp" / "notebooklm-share"
NLM = Path(os.environ.get("NLM_EXE", Path(os.environ.get("LOCALAPPDATA", "")) / r"Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\nlm.exe"))

NOTEBOOKLM_STOCK_PROMPT = """
Bạn là chuyên gia phân tích đầu tư chứng khoán, TradingAgents research coordinator và chuyên gia thiết kế bản trình bày tài chính cho lãnh đạo/quỹ đầu tư.

NHIỆM VỤ: Đọc TOÀN BỘ file báo cáo cổ phiếu đã upload và tạo BẢN TRÌNH BÀY DỌC / PORTRAIT từ nội dung báo cáo.

YÊU CẦU QUAN TRỌNG NHẤT:
1. PHẢI GIỮ NGUYÊN TOÀN BỘ NỘI DUNG QUAN TRỌNG trong file báo cáo.
2. Được phép viết lại câu chữ ngắn gọn hơn, súc tích hơn, nhưng KHÔNG được làm mất ý, mất số liệu, mất nguồn, mất luận điểm, mất cảnh báo hoặc mất điều kiện theo dõi.
3. Không được bỏ qua: tin tức/nguồn, tác động tích cực-tiêu cực-trung tính, sentiment, market snapshot, chiến lược LH, từng chỉ báo RSI/MACD/volume/ROC/Ichimoku/Bollinger/MA/ADX/RS support-resistance, rankScore, entry/stop/takeprofit, fundamental/valuation, bull/bear, catalyst, invalidation, risk score, trade plan, data gaps và disclaimer.

NGUYÊN TẮC EVIDENCE-ONLY:
- Chỉ sử dụng thông tin có trong file báo cáo.
- Không tự lấy thêm dữ liệu ngoài. Không bịa số liệu, không suy diễn ngoài báo cáo.
- Nếu thông tin không có trong báo cáo, ghi: “Không có trong báo cáo”. Nếu dữ liệu cũ/chưa xác nhận, giữ nguyên cảnh báo như “Cache chưa xác nhận”, “Cần cập nhật EOD/volume mới”, “Chưa đủ cơ sở kết luận”.
- Không đưa khuyến nghị đầu tư cá nhân hóa; chỉ trình bày phân tích, kịch bản, điều kiện theo dõi.

YÊU CẦU BỐ CỤC MODEL 3 / NOTEBOOKLM:
- Mục tiêu chính: tạo 2 TRANG DỌC DÀI / two-page long portrait infographic, độ phân giải cao, nhìn như ảnh mẫu dashboard/report dài.
- Không tạo slide deck ngang/thưa. Chia thành đúng 2 trang dọc dense để đủ nội dung hơn.
- Mỗi trang phải là một phần của cùng một báo cáo dài liên tục, không được thành slide thuyết trình rời rạc.
- Trang 1 chứa panel 01–05; Trang 2 chứa panel 06–10. Mỗi trang dense, nhiều bảng/ô nhỏ, ít khoảng trắng, nhiều visual/smartart.

PHONG CÁCH THIẾT KẾ:
- Phong cách theo ảnh mẫu: A4/portrait infographic dashboard siêu dense, nền xanh navy/blue-gradient, header lớn, nhiều panel nhỏ viền sáng, ít khoảng trắng.
- Dark-tech/institutional research dashboard: nền navy/xanh đậm (#071B3A, #0B2A5B, #123B7A), chữ trắng/xanh nhạt, font sans-serif hiện đại.
- Phải có visual hooks thu hút: hero visual/header graphic, icon nhỏ cho từng panel, mini chart/sparkline, gauge/donut, heatmap, arrow flow, faint stock chart watermark hoặc grid/glow decoration nếu có thể.
- Không được bỏ chỉ báo kỹ thuật đã có trong DOCX; nếu nhiều chỉ báo thì đưa vào bảng/matrix nhỏ thay vì cắt bỏ.
- Không được chỉ là bảng chữ đơn điệu; mỗi trang cần 3-5 yếu tố visual ngoài chữ/bảng.
- Ưu tiên bản biểu/card nhỏ gọn thay vì đoạn văn dài: KPI strip nhỏ, bảng chỉ báo, timeline, matrix, badge, gauge, checklist.
- Làm thông tin nhỏ lại: bullet ngắn, câu ngắn, chữ trong từng ô/card nhỏ gọn hơn, nhiều cột/bảng hơn; mỗi trang nên có 8-14 block nhỏ hoặc 3-5 bảng/matrix; nhưng tuyệt đối không mất nội dung quan trọng.
- Accent cyan/vàng/cam/đỏ/xanh lá. Nhãn màu: Tích cực xanh/cyan; Tiêu cực đỏ/cam; Trung tính/chưa rõ xám/vàng; Rủi ro đỏ/cam.

BỐ CỤC BẮT BUỘC — 2 TRANG DỌC DÀI GỒM 10 BẢNG/Ô NHỎ:
TRANG 1: panel 01–05. TRANG 2: panel 06–10. Không bỏ panel nào.
01. HEADER / HERO: mã cổ phiếu, tên doanh nghiệp, ngày dữ liệu, trạng thái dữ liệu, visual stock/market.
02. EXECUTIVE SUMMARY: 3–5 ý chính nhất, verdict, sentiment, điểm cần theo dõi.
03. KPI SNAPSHOT: giá, % thay đổi, volume/thanh khoản, rankScore, risk score, data freshness.
04. NEWS & CATALYST TIMELINE: tin tức, nguồn, tác động tích cực/tiêu cực/trung tính.
05. MARKET / SECTOR CONTEXT: VNIndex/ngành/vĩ mô nếu có trong báo cáo, tác động ngắn gọn.
06. TECHNICAL MATRIX: RSI, MACD, MA, ADX/DI, Bollinger, Ichimoku, ROC/ret5, volume, support/resistance/RS.
07. LH STRATEGY BOX: strategy status, entry, stop, take profit, invalidation, điều kiện kích hoạt.
08. FUNDAMENTAL / VALUATION: KQKD, valuation, driver, target/mean/median nếu có.
09. BULL / BASE / BEAR + RISK: 3 kịch bản, catalyst, risk probability-impact, điểm hủy luận điểm.
10. ACTION CHECKLIST / DISCLAIMER: checklist theo dõi, dữ liệu thiếu, cảnh báo, disclaimer.

MAP NỘI DUNG DOCX → PANEL (bắt buộc lấy đúng nguồn, không bỏ sót):
- Mục 1 + 1B (Quan điểm tổng hợp + Điểm tổng hợp 4 lớp) → panel 02 Executive Summary + 03 KPI Snapshot: giữ nguyên verdict, điểm từng lớp và bằng chứng.
- Mục 2 (bảng tin có nhãn sentiment) → panel 04 News & Catalyst Timeline: giữ nhãn Tích cực/Tiêu cực/Trung tính và số đếm sentiment.
- Mục 4A/4B (vĩ mô, tác động ngành) → panel 05 Market/Sector Context.
- Mục 3 + 3B + 3C (Indicator Matrix, 4 cặp chỉ báo, tín hiệu hệ thống V3: xu hướng hiệu lực, phân kỳ RSI/MACD, Ichimoku, VWAP, Fibonacci, Donchian, Risk/Reward, signal score) → panel 06 Technical Matrix: KHÔNG được bỏ bất kỳ tín hiệu nào của mục 3C.
- Mục 3D (LH Strategy Box: chiến lược, trạng thái, entry/stop/TP) → panel 07 LH Strategy Box.
- Mục 4C (P/E, target CTCK, upside, stop loss CTCK, báo cáo CTCK mới nhất) → panel 08 Fundamental/Valuation.
- Mục 5 + 6 (kịch bản Bull/Base/Bear gắn số liệu, catalyst) + mục 7 (risk score X/5 kèm các yếu tố rủi ro) → panel 09 Bull/Base/Bear + Risk.
- Mục 8 (kế hoạch theo dõi, trigger tích cực/tiêu cực) + disclaimer → panel 10 Action Checklist/Disclaimer.

CÁCH VIẾT:
- Có thể rút gọn câu dài thành bullet ngắn nhưng không được xóa ý.
- Chuyển đoạn văn thành bảng/biểu/matrix/checklist khi có thể.
- Mọi số liệu, nhãn trạng thái, nguồn, cảnh báo phải giữ nguyên.
- Ưu tiên rõ ràng, súc tích, đầy đủ hơn là đẹp nhưng thiếu nội dung.
""".strip()

FOCUS_PROMPT = (
    "BẮT BUỘC KHÓA LAYOUT: chỉ tạo TRANG DỌC / PORTRAIT / LONG PORTRAIT. CẤM landscape/trang ngang, cấm 16:9 ngang, cấm slide deck ngang. Nếu công cụ định tạo landscape thì phải chuyển sang A4 portrait hoặc long portrait trước khi xuất. "
    "MODEL 3 OUTPUT CHO NOTEBOOKLM: tạo 2 TRANG DỌC DÀI / TWO-PAGE LONG PORTRAIT INFOGRAPHIC độ phân giải cao theo đúng ảnh mẫu, KHÔNG làm slide thuyết trình thưa. "
    "Nếu công cụ xuất slide/PDF, hãy coi toàn bộ output là một báo cáo dọc dài liên tục gồm đúng 2 trang: Trang 1 panel 01-05, Trang 2 panel 06-10. "
    "Mỗi trang phải có nhiều bảng/ô nhỏ rõ ràng, xếp dạng lưới compact, đầy đủ nội dung, ít chữ, nhiều hình ảnh/visual/smartart. "
    "Phong cách ảnh mẫu: A4/portrait hoặc long portrait infographic/dashboard cao cấp, nền xanh navy/blue-gradient, "
    "nhiều panel nhỏ viền sáng, header lớn ở trên, bảng nhỏ xếp dạng lưới, font nhỏ nhưng rõ, one-page fact sheet/report chứ KHÔNG phải slide thuyết trình thưa. "
    "Toàn trang phải giống institutional equity research infographic: nhiều thông tin, nhiều bảng, nhiều badge/status, ít khoảng trắng, có hình ảnh/visual hooks thu hút người đọc. "
    "BẮT BUỘC giữ đủ nội dung quan trọng, số liệu, nguồn, cảnh báo; đặc biệt không được bỏ các chỉ báo kỹ thuật có trong DOCX: giá/EOD, volume, MA, RSI, MACD, ADX/DI, Bollinger, Ichimoku, ROC/ret5, hỗ trợ/kháng cự/RS, target/mean/median nếu có. Không bịa và không lấy dữ liệu ngoài. "
    "\n\nYÊU CẦU VISUAL GIỐNG ẢNH MẪU: "
    "dùng hero visual ở header (biểu tượng cổ phiếu/doanh nghiệp/market, đường line chart phát sáng, candlestick/arrow/magnifier icon), "
    "dùng icon nhỏ cho từng panel (news, macro, technical, valuation, risk, checklist), dùng mini chart/sparkline/gauge/donut/heatmap khi có thể, "
    "dùng background decorations tinh tế như glow, grid lines, wave/curve, faint stock chart watermark. "
    "Không được chỉ là bảng chữ đơn điệu. Mỗi trang cần ít nhất 3-5 yếu tố visual: icon, mini chart, gauge, heatmap, arrow flow, badge, hoặc watermark. "
    "\n\nBỐ CỤC BẮT BUỘC: top title bar + subtitle/data freshness; dưới là KPI strip nhỏ; thân trang chia 2-3 cột; đúng tinh thần 10 mini panels/cards. "
    "10 ô gồm: 01 Header/Hero, 02 Executive Summary, 03 KPI Snapshot, 04 News/Catalyst Timeline, 05 Market/Sector Context, 06 Technical Matrix, 07 LH Strategy Box, 08 Fundamental/Valuation, 09 Bull/Base/Bear + Risk, 10 Action Checklist/Disclaimer. "
    "Mỗi panel có title bar nhỏ, icon/badge màu, bullet ngắn hoặc bảng 2-4 cột. "
    "Giảm kích thước chữ và ô/card: KHÔNG dùng KPI card quá bự, KHÔNG để khoảng trắng lớn, KHÔNG dùng 1-2 card chiếm nửa trang. "
    "Toàn output phải có mật độ thông tin cao: tối thiểu 10 khối thông tin nhỏ, nhiều bảng/matrix; dùng compact grid 2 cột/3 cột, mini table, mini badge, mini sparkline/gauge nếu có. Không được tạo trang chỉ có tiêu đề + vài bullet. "
    "Ưu tiên BẢNG/BIỂU/CARD nhỏ gọn thay vì đoạn văn dài: KPI strip nhỏ, timeline tin tức, news-impact table, technical indicator matrix, valuation table, "
    "peer comparison nếu có, valuation scorecard, bull/base/bear scenario matrix, risk probability-impact matrix, catalyst checklist, trade plan checklist, data-quality box. "
    "Viết bullet cực ngắn nhưng không mất ý; mỗi ô/card chứa nhiều dòng ngắn. Nếu không đủ chỗ thì tăng số trang, không được làm mất nội dung. "
    "\n\nSTYLE MÀU: nền navy/blue-gradient giống infographic mẫu (#071B3A, #0B2A5B, #123B7A), panel xanh đậm, viền cyan/blue, chữ trắng/xanh nhạt, "
    "accent cyan/vàng/cam/đỏ/xanh lá; dùng glow/neon nhẹ, icon line-art, nhãn màu tích cực/tiêu cực/trung tính/rủi ro. "
    "Kết quả mong muốn: 2 trang dọc dài độ phân giải cao, nhìn như infographic/report/dashboard phân tích cổ phiếu giàu dữ liệu, có hình ảnh thu hút như ảnh mẫu, không phải slide marketing và không phải bảng chữ xấu/sơ sài. "
    "Không phải khuyến nghị đầu tư cá nhân hóa."
)


def cleanup_temp(max_age_days: int = 3) -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - max_age_days * 86400
    for p in TEMP_DIR.glob("*"):
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
        except Exception:
            pass


def _run_once(args: list[str], timeout: int = 900) -> tuple[int, str]:
    if not NLM.exists():
        raise FileNotFoundError(f"nlm.exe not found: {NLM}")
    proc = subprocess.run([str(NLM), *args], text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout)
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out


def _is_stale_auth_output(out: str) -> bool:
    low = (out or "").lower()
    return "authentication expired" in low or ("auth" in low and ("expired" in low or "stale" in low))


def notebooklm_auth_check(auto_login: bool = True, timeout: int = 360) -> dict[str, Any]:
    """Validate NotebookLM CLI auth and re-login with the saved browser session if needed.

    This is intentionally safe for dashboard/export use: it first performs a cheap
    `notebook list --json`, then `auth refresh`, then `login` only when the CLI says
    auth is expired/stale. On Hòa Đại ka's machine Chrome already has the account, so
    login normally completes without asking for the password again.
    """
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "list", "message": "NotebookLM auth OK"}
    last = out[-2000:]
    if not _is_stale_auth_output(out):
        return {"ok": False, "stage": "list", "error": last}

    _run_once(["auth", "refresh"], timeout=120)
    time.sleep(2)
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "refresh", "message": "NotebookLM auth refreshed"}
    last = out[-2000:]
    if not auto_login:
        return {"ok": False, "stage": "refresh", "error": last}

    code, out = _run_once(["login"], timeout=timeout)
    if code != 0:
        return {"ok": False, "stage": "login", "error": out[-2000:]}
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "login", "message": "NotebookLM re-login OK"}
    return {"ok": False, "stage": "verify_after_login", "error": out[-2000:]}


def _run(args: list[str], timeout: int = 900) -> str:
    code, out = _run_once(args, timeout=timeout)
    if code == 0:
        return out.strip()
    stale = _is_stale_auth_output(out)
    if stale:
        auth = notebooklm_auth_check(auto_login=True)
        if auth.get("ok"):
            code2, out2 = _run_once(args, timeout=timeout)
            if code2 == 0:
                return out2.strip()
            out = out2
            code = code2
        else:
            out = f"{out}\n\nAUTO_AUTH_FAILED: {auth}"
    raise RuntimeError(f"nlm {' '.join(args)} failed ({code}): {out[-2000:]}")


def _extract_id(text: str) -> str:
    try:
        d = json.loads(text)
        if isinstance(d, dict):
            for key in ("id", "notebook_id", "uuid", "notebookId"):
                if d.get(key):
                    return str(d[key])
            if isinstance(d.get("notebook"), dict):
                for key in ("id", "uuid"):
                    if d["notebook"].get(key):
                        return str(d["notebook"][key])
    except Exception:
        pass
    m = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text)
    if m:
        return m.group(0)
    raise ValueError(f"Cannot extract NotebookLM id from: {text[:1000]}")


def _pdf_quality_score(pdf_path: Path) -> dict[str, Any]:
    """Best-effort density check. NotebookLM controls visuals, but reject obviously sparse decks."""
    info: dict[str, Any] = {"checked": False, "pages": 0, "text_chars": 0, "ok": True, "reason": ""}
    try:
        from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(pdf_path))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                pass
        info["checked"] = True
        info["pages"] = len(reader.pages)
        info["text_chars"] = sum(len(t.strip()) for t in texts)
        # Model 3 target: one-page/long-infographic style, dense enough to preserve content.
        # NotebookLM may still export 1-2 PDF pages; accept if text density is high.
        pages = int(info["pages"] or 0)
        chars = int(info["text_chars"] or 0)
        portrait_ok = True
        dims = []
        try:
            for page in reader.pages:
                box = page.mediabox
                w = float(box.width); h = float(box.height)
                dims.append([round(w, 1), round(h, 1)])
                if w > h:
                    portrait_ok = False
        except Exception:
            pass
        full_text = "\n".join(texts)
        utf8_report = vietnamese_quality_report(full_text)
        info["page_dims"] = dims
        info["portrait_ok"] = portrait_ok
        info["utf8_report"] = utf8_report
        info["ok"] = bool(1 <= pages <= 2 and chars >= 1800 and portrait_ok and not utf8_report.get("mojibake_markers") and not utf8_report.get("replacement_chars"))
        if not info["ok"]:
            info["reason"] = f"not dense 2-page portrait/utf8 clean enough: pages={pages}, text_chars={chars}, portrait_ok={portrait_ok}, dims={dims}, utf8={utf8_report}"
    except Exception as exc:
        try:
            import fitz  # type: ignore
            doc = fitz.open(str(pdf_path))
            dims=[]; portrait_ok=True
            for page in doc:
                w=float(page.rect.width); h=float(page.rect.height)
                dims.append([round(w,1), round(h,1)])
                if w > h:
                    portrait_ok=False
            info["checked"] = True
            info["pages"] = len(doc)
            info["text_chars"] = sum(len((page.get_text() or "").strip()) for page in doc)
            full_text = "\n".join((page.get_text() or "") for page in doc)
            utf8_report = vietnamese_quality_report(full_text)
            info["page_dims"] = dims
            info["portrait_ok"] = portrait_ok
            info["utf8_report"] = utf8_report
            pages=int(info["pages"] or 0); chars=int(info["text_chars"] or 0)
            info["ok"] = bool(1 <= pages <= 2 and chars >= 1800 and portrait_ok and not utf8_report.get("mojibake_markers") and not utf8_report.get("replacement_chars"))
            if not info["ok"]:
                info["reason"] = f"not dense 2-page portrait/utf8 clean enough: pages={pages}, text_chars={chars}, portrait_ok={portrait_ok}, dims={dims}, utf8={utf8_report}"
        except Exception as exc2:
            info["ok"] = False
            info["reason"] = f"quality check failed: {type(exc).__name__}: {exc}; fallback {type(exc2).__name__}: {exc2}"
    return info


def create_presentation_from_docx(docx_path: str, title: str = "LHInvestment Model 3 Report") -> dict[str, Any]:
    cleanup_temp(3)
    docx = Path(docx_path)
    if not docx.exists():
        raise FileNotFoundError(docx)

    nb_out = _run(["notebook", "create", title, "--json"], timeout=120)
    notebook_id = _extract_id(nb_out)

    _run(["source", "add", notebook_id, "--file", str(docx), "--wait", "--wait-timeout", "600"], timeout=900)

    # Nhập prompt trực tiếp vào bước tạo trang trình bày (--focus), không thêm prompt như một source
    # để tránh NotebookLM đưa nội dung chỉ dẫn vào slide như dữ liệu báo cáo.
    base_prompt = repair_vietnamese_text(f"{FOCUS_PROMPT}\n\n{NOTEBOOKLM_STOCK_PROMPT}")
    retry_prompt = base_prompt + (
        "\n\nKIỂM TRA CHẤT LƯỢNG BẮT BUỘC CHO MODEL 3: nếu bản trước ra nhiều slide/trang thưa, bảng/card quá bự, chữ quá bự, ít nội dung hoặc lỗi mojibake/Unicode, "
        "hãy tạo lại thành đúng 2 trang dọc dài dense hơn: Trang 1 panel 01-05, Trang 2 panel 06-10, nhiều visual/smartart/icon/mini chart hơn, giảm khoảng trắng, giữ đủ nội dung quan trọng. "
        "Không bung thành deck ngang hoặc hơn 2 trang nếu không bắt buộc. BẮT BUỘC tiếng Việt Unicode sạch, không mojibake."
    )

    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", title)[:60].strip("-") or "notebooklm-slide-deck"
    last_err = ""
    last_quality: dict[str, Any] = {}
    for attempt, prompt in enumerate((base_prompt, retry_prompt), 1):
        # Model 3: yêu cầu dense one-page infographic; dùng detailed_deck nhưng focus ép 1 trang dài/10 card.
        _run(["slides", "create", notebook_id, "--format", "detailed_deck", "--length", "short", "--language", "vi", "--focus", prompt, "--confirm"], timeout=900)
        out_pdf = TEMP_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{safe}-attempt{attempt}.pdf"
        for _ in range(30):
            try:
                _run(["download", "slide-deck", notebook_id, "--output", str(out_pdf), "--format", "pdf", "--no-progress"], timeout=300)
                if out_pdf.exists() and out_pdf.stat().st_size > 0:
                    # Tự động xóa watermark "NotebookLM + icon" góc phải dưới mỗi trang.
                    try:
                        from pdf_watermark_cleaner import strip_notebooklm_watermark
                        strip_notebooklm_watermark(out_pdf)
                    except Exception:
                        pass  # thiếu PyMuPDF/Pillow thì giữ nguyên PDF, không chặn pipeline
                    last_quality = _pdf_quality_score(out_pdf)
                    if last_quality.get("ok", True) or attempt == 2:
                        return {"ok": bool(last_quality.get("ok", True)), "notebook_id": notebook_id, "slide_pdf": str(out_pdf), "quality": last_quality, "attempt": attempt}
                    last_err = str(last_quality.get("reason") or "deck quality too sparse")
                    break
            except Exception as exc:
                last_err = str(exc)
            time.sleep(20)
    return {"ok": False, "notebook_id": notebook_id, "error": last_err, "quality": last_quality}
