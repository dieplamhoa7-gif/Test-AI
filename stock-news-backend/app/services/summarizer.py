import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "APIFREE")
DEFAULT_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:20128/v1")
SUMMARY_MAX_WORDS = int(os.getenv("SUMMARY_MAX_WORDS", "50"))
ALLOWED_STRONG_TAGS = (("<strong>", "</strong>"),)


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

    cleaned = [p.strip() for p in parts if len(p.split()) >= 8]
    selected = cleaned[:max_sentences]

    if len(selected) < min_sentences:
        words = raw.split()
        chunk_size = max(22, min(36, max(1, len(words) // 5)))
        generated = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]).strip(" ,;:-")
            if chunk:
                if chunk[-1] not in ".!?":
                    chunk += "."
                generated.append(chunk)
            if len(generated) >= max_sentences:
                break
        selected = generated[:max_sentences]

    final_sentences = selected[:max_sentences]
    if len(final_sentences) > 5:
        final_sentences = final_sentences[:5]
    return " ".join(final_sentences)


def _fallback_snippet(item: Dict) -> str:
    full_text = (item.get("fullText") or "").strip()
    if full_text:
        return _fallback_sentences(full_text)
    return ""


def classify_and_summarize_item(item: Dict) -> Dict[str, str]:
    full_text = _clip_text(item.get("fullText") or "")
    if not full_text:
        return {"category": "Kinh Tế", "summary": ""}

    client = _client()
    if client is None:
        return {"category": "Kinh Tế", "summary": _fallback_snippet(item)}

    prompt = (
        "Bạn là giám đốc đầu tư chứng khoán. "
        "Hãy đọc kỹ tin và phân loại đúng 1 nhãn: Chứng khoán, Ngân hàng, Bất động sản, Doanh nghiệp, Vĩ mô, Quốc tế, Pháp luật, Khác. "
        "Tóm tắt đúng 5 câu: đủ ý, bôi đậm sự kiện chính và số liệu quan trọng (% giá trị, chỉ số), thời gian bằng thẻ <strong>...</strong>. "
        "Phong cách thực dụng, đi thẳng vào vấn đề, không lan man, không lặp tiêu đề, không bịa; có thể viết tắt. "
        "Nêu nhận định ảnh hưởng tích cực/tiêu cực đến các cổ phiếu có trong bài nếu đủ dữ kiện. "
        "Không dùng Markdown **, không dùng HTML khác ngoài <strong>. "
        "Trả đúng 2 dòng: Category: <nhãn> và Summary: <đúng 5 câu>."
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
        category = "Kinh Tế"
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
        return {"category": "Kinh Tế", "summary": _fallback_snippet(item)}


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
