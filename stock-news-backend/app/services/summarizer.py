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


def _clip_text(text: str, limit: int = 6000) -> str:
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
        "Phân loại tin vào 1 nhóm: Tổng hợp, Chứng khoán, Ngân hàng, Bất động sản, Pháp luật, Chính trị, Khác. "
        "Tóm tắt 5-8 câu bằng tiếng Việt, đủ ý, không lặp tiêu đề, không bịa. "
        "Ưu tiên số liệu, công ty, mã cổ phiếu, thời gian, nguyên nhân, diễn biến, tác động. "
        "Nếu đủ dữ kiện, nêu ngắn mã/doanh nghiệp nào tích cực hoặc tiêu cực. "
        "Trả đúng 2 dòng:\nCategory: <nhãn>\nSummary: <tóm tắt>"
    )

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            max_tokens=420,
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
            max_tokens=520,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tóm tắt tin tài chính bằng tiếng Việt. "
                        "Viết 5-8 câu, đủ ý, không lặp tiêu đề, không bịa. "
                        "Giữ số liệu, công ty, mã cổ phiếu, thời gian, nguyên nhân, diễn biến, tác động. "
                        "Nếu đủ dữ kiện, nêu ngắn mã nào tích cực/tiêu cực. "
                        "Không gạch đầu dòng, không chia mục."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Tóm tắt dữ liệu sau thành 5-8 câu, đủ ý. "
                        "Giữ số liệu, công ty, mã cổ phiếu, sự kiện chính. "
                        "Nếu đủ dữ kiện, thêm nhận xét ngắn mã nào tích cực/tiêu cực. "
                        "Không lặp tiêu đề.\n\n"
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
