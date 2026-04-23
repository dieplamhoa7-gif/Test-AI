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
        "Phần tóm tắt phải viết thành 5 đến 8 câu, đủ ý, mạch lạc, bao quát đầy đủ nội dung quan trọng nhất của bài. "
        "Không nhắc lại, không chép lại tiêu đề bài. "
        "Ưu tiên số liệu quan trọng, tên công ty, mã cổ phiếu, mốc thời gian, quyết định, nguyên nhân, tác động và sự kiện chính. "
        "Nếu bài có đủ dữ kiện, hãy nêu nhận xét ngắn về tác động tích cực hoặc tiêu cực tới mã cổ phiếu/doanh nghiệp liên quan; nói rõ mã nào hưởng lợi, mã nào chịu ảnh hưởng. "
        "Nếu không đủ dữ kiện để nhận định thì không được bịa thêm. "
        "Văn phong trực diện, rõ ràng, dễ hiểu, không lan man, không thêm suy diễn. "
        "Mỗi câu phải có thông tin, tránh câu rỗng. "
        "Trả đúng định dạng 2 dòng:\n"
        "Category: <1 nhãn>\n"
        "Summary: <đoạn tóm tắt 5-8 câu>"
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
                        "Hãy tóm tắt các tin từ nội dung bài viết, không lặp tiêu đề, không bịa thêm dữ kiện. "
                        "Bài tóm tắt phải gồm 5 đến 8 câu hoàn chỉnh, đủ ý, đầy đủ nội dung cốt lõi, mạch lạc và dễ đọc. "
                        "Ưu tiên giữ số liệu quan trọng, tên công ty, mã cổ phiếu, mốc thời gian, nguyên nhân, diễn biến và tác động chính. "
                        "Nếu dữ liệu đủ rõ, hãy thêm nhận xét ngắn về ảnh hưởng tích cực/tiêu cực tới mã cổ phiếu hoặc doanh nghiệp liên quan, nêu rõ mã nào được lợi hoặc bị ảnh hưởng. "
                        "Nếu không đủ dữ kiện thì không suy diễn. "
                        "Văn phong trực diện, rõ ràng, thực dụng. Không viết gạch đầu dòng, không chia mục, không viết quá ngắn."                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Tóm tắt các tin sau từ nội dung bài viết. "
                        "Viết thành 5 đến 8 câu hoàn chỉnh, đủ ý, đầy đủ nội dung quan trọng. "
                        "Giữ nguyên số liệu, tên công ty, mã cổ phiếu và sự kiện quan trọng. "
                        "Nếu có đủ dữ kiện, thêm nhận xét ngắn về mã nào tích cực, mã nào tiêu cực và vì sao. "
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
