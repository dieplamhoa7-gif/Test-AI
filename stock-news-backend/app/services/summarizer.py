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


def _fallback_sentences(text: str, min_sentences: int = 5, max_sentences: int = 5) -> str:
    raw = " ".join((text or "").split())
    if not raw:
        return ""

    parts = []
    current = ""
    for ch in raw:
        current += ch
        if ch in ".!?;\n":
            sentence = current.strip()
            if sentence:
                parts.append(sentence)
            current = ""
    if current.strip():
        parts.append(current.strip())

    cleaned = [p for p in parts if len(p.split()) >= 6]
    selected = cleaned[:max_sentences]
    if len(selected) < min_sentences:
        words = raw.split()
        chunk_size = max(18, min(32, len(words) // max(min_sentences, 1) or 18))
        generated = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]).strip()
            if chunk:
                if chunk[-1] not in ".!?":
                    chunk += "."
                generated.append(chunk)
            if len(generated) >= max_sentences:
                break
        selected = generated[:max_sentences]

    return " ".join(selected[:max_sentences])


def _fallback_snippet(item: Dict) -> str:
    full_text = (item.get("fullText") or "").strip()
    if full_text:
        return _fallback_sentences(full_text)
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
        "Tóm tắt đúng 5 câu bằng tiếng Việt, ngắn gọn nhưng đủ ý, không lặp tiêu đề, không bịa. "
        "Có thể dùng viết tắt. Bỏ chi tiết/câu chữ không quan trọng. "
        "Ưu tiên số liệu, công ty, mã cổ phiếu, thời gian, nguyên nhân, diễn biến, tác động chính. "
        "Nếu đủ dữ kiện, nêu rất ngắn mã/doanh nghiệp nào tích cực hoặc tiêu cực. "
        "Trả đúng 2 dòng:\nCategory: <nhãn>\nSummary: <đúng 5 câu>"
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
        merged_text = " ".join(
            (it.get("fullText") or it.get("snippet") or "").strip()
            for it in items[:4]
            if (it.get("fullText") or it.get("snippet") or "").strip()
        )
        return _fallback_sentences(merged_text) or "Không có đủ nội dung bài để tóm tắt."

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
                        "Viết đúng 5 câu, ngắn gọn nhưng đủ ý, không lặp tiêu đề, không bịa. "
                        "Có thể dùng viết tắt; bỏ chi tiết không quan trọng. "
                        "Giữ số liệu, công ty, mã cổ phiếu, thời gian, nguyên nhân, diễn biến, tác động chính. "
                        "Nếu đủ dữ kiện, nêu rất ngắn mã nào tích cực/tiêu cực. Không gạch đầu dòng."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Tóm tắt dữ liệu sau thành đúng 5 câu, ngắn gọn nhưng đủ ý. "
                        "Giữ số liệu, công ty, mã cổ phiếu, sự kiện chính. "
                        "Có thể dùng viết tắt, bỏ ý phụ không quan trọng. "
                        "Nếu đủ dữ kiện, thêm nhận xét rất ngắn mã nào tích cực/tiêu cực. "
                        "Không lặp tiêu đề.\n\n"
                        f"DỮ LIỆU:\n{content}"
                    ),
                },
            ],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        merged_text = " ".join(
            (it.get("fullText") or it.get("snippet") or "").strip()
            for it in items[:4]
            if (it.get("fullText") or it.get("snippet") or "").strip()
        )
        return _fallback_sentences(merged_text) or "Không có đủ nội dung bài để tóm tắt."


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
