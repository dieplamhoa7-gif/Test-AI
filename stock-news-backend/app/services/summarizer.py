import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "APIFREE")
DEFAULT_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:20128/v1")
SUMMARY_MAX_WORDS = int(os.getenv("SUMMARY_MAX_WORDS", "50"))


def _client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=DEFAULT_BASE_URL)


def _clip_text(text: str, limit: int = 4000) -> str:
    return (text or "").strip()[:limit]


def _fallback_snippet(item: Dict) -> str:
    full_text = (item.get("fullText") or "").strip()
    if full_text:
        words = full_text.split()
        return " ".join(words[:SUMMARY_MAX_WORDS])
    return ""


def classify_and_summarize_item(item: Dict) -> Dict[str, str]:
    full_text = _clip_text(item.get("fullText") or "")
    if not full_text:
        return {"category": "Khác", "summary": ""}

    client = _client()
    if client is None:
        return {"category": "Khác", "summary": _fallback_snippet(item)}

    prompt = (
        "Bạn là trợ lý phân loại và tóm tắt tin tài chính/chứng khoán bằng tiếng Việt. "
        "Phân loại bài vào đúng 1 nhóm trong danh sách: Tổng hợp, Chứng khoán, Ngân hàng, Bất động sản, Pháp luật, Chính trị, Khác. "
        f"Tóm tắt tối đa {SUMMARY_MAX_WORDS} chữ. "
        "Không nhắc lại, không chép lại tiêu đề bài. "
        "Ưu tiên số liệu quan trọng, tên công ty, mã cổ phiếu, sự kiện quan trọng. "
        "Văn phong trực diện, ngắn gọn, thực dụng. Không thêm suy diễn. "
        "Trả đúng định dạng 2 dòng:\n"
        "Category: <1 nhãn>\n"
        "Summary: <tóm tắt>"
    )

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            max_tokens=220,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": full_text},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        category = "Khác"
        summary = ""
        for line in content.splitlines():
            line = line.strip()
            lower = line.lower()
            if lower.startswith("category:"):
                category = line.split(":", 1)[1].strip() or "Khác"
            elif lower.startswith("summary:"):
                summary = line.split(":", 1)[1].strip()
        if not summary:
            summary = content.strip()
        return {"category": category, "summary": summary or _fallback_snippet(item)}
    except Exception:
        return {"category": "Khác", "summary": _fallback_snippet(item)}


def summarize_news(items: List[Dict], max_chars: int = 1200) -> str:
    if not items:
        return "Không có dữ liệu tin tức để tóm tắt."

    client = _client()
    blocks = []
    for idx, it in enumerate(items, 1):
        full_text = _clip_text(it.get("fullText") or it.get("snippet") or "", limit=max_chars)
        if not full_text:
            continue
        blocks.append(f"{idx}. Nguồn: {it.get('source', 'unknown')}\nNội dung: {full_text}")

    if not blocks:
        return "Không có đủ nội dung bài để tóm tắt."

    if client is None:
        texts = []
        for it in items[:4]:
            text = _fallback_snippet(it)
            if text:
                texts.append(f"- {text}")
        return "\n".join(texts) if texts else "Không có đủ nội dung bài để tóm tắt."

    content = "\n\n".join(blocks)[:max_chars * 2]

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            max_tokens=220,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý tài chính tiếng Việt. "
                        "Phân loại và tóm tắt tin từ nội dung bài viết, không lặp tiêu đề, không bịa thêm dữ kiện. "
                        "Ưu tiên số liệu quan trọng, tên công ty, mã cổ phiếu, sự kiện chính. "
                        "Văn phong trực diện, ngắn gọn, thực dụng. "
                        "Chỉ xuất đúng 3 phần:\n"
                        "1. Toàn cảnh: 1-2 câu\n"
                        "2. Điểm chính: tối đa 4 gạch đầu dòng\n"
                        "3. Nhóm tin/Mã/Doanh nghiệp: liệt kê ngắn"                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Tóm tắt các tin sau từ nội dung bài viết. "
                        "Giữ nguyên số liệu, tên công ty, sự kiện quan trọng. "
                        "Không lặp lại tiêu đề bài.\n\n"
                        f"DỮ LIỆU:\n{content}"
                    ),
                },
            ],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        texts = []
        for it in items[:4]:
            text = _fallback_snippet(it)
            if text:
                texts.append(f"- {text}")
        return "\n".join(texts) if texts else "Không có đủ nội dung bài để tóm tắt."


def enrich_news_with_ai(items: List[Dict]) -> List[Dict]:
    enriched = []
    for item in items:
        current = dict(item)
        result = classify_and_summarize_item(current)
        current["category"] = result.get("category") or "Khác"
        if result.get("summary"):
            current["snippet"] = result["summary"]
        elif current.get("fullText"):
            current["snippet"] = _fallback_snippet(current)
        else:
            current["snippet"] = ""
        enriched.append(current)
    return enriched
