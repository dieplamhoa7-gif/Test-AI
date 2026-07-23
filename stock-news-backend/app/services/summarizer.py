import os
import re
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


def _clean_news_text(text: str) -> str:
    raw = re.sub(r"<[^>]+>", " ", text or "")
    raw = re.sub(r"\s+", " ", raw).strip()
    boiler = [
        "Theo đó", "Cụ thể", "Mới đây", "Được biết", "Trong khi đó",
        "CafeF", "Vietstock", "Ảnh minh họa", "Nguồn:", "Xem thêm",
    ]
    for b in boiler:
        raw = raw.replace(b + ":", b)
    return raw


def _split_sentences_vi(text: str) -> list[str]:
    raw = _clean_news_text(text)
    if not raw:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\s+[•]\s+", raw)
    out: list[str] = []
    for part in parts:
        t = part.strip(" \t\r\n-•;:")
        if len(t) < 35 or len(t.split()) < 7:
            continue
        if not re.search(r"[A-Za-zÀ-ỹ0-9]", t):
            continue
        if t[-1] not in ".!?":
            t += "."
        out.append(t)
    return out


def _score_sentence(sentence: str, title: str = "") -> float:
    s = sentence.lower()
    score = 0.0
    keywords = {
        "giá": 2, "cổ phiếu": 3, "vn-index": 3, "lợi nhuận": 3, "doanh thu": 3,
        "tăng": 2, "giảm": 2, "kịch trần": 4, "sàn": 3, "thanh khoản": 3,
        "khối ngoại": 3, "tự doanh": 3, "cổ tức": 3, "mua": 2, "bán": 2,
        "kế hoạch": 2, "kqkd": 3, "rủi ro": 3, "lãi suất": 3, "tỷ giá": 3,
        "ngân hàng": 2, "bất động sản": 2, "trái phiếu": 3, "nợ": 2,
        "ftse": 3, "nâng hạng": 3, "phát hành": 3, "chào bán": 3,
    }
    for k, w in keywords.items():
        if k in s:
            score += w
    if re.search(r"\b[A-Z]{2,5}\b", sentence):
        score += 3
    if re.search(r"\d+[,.]?\d*\s*(%|tỷ|triệu|nghìn|đồng|cp|cổ phiếu|điểm|ngày|tháng|năm)", s):
        score += 4
    title_words = {w for w in re.findall(r"[A-Za-zÀ-ỹ0-9]{4,}", title.lower())}
    sent_words = set(re.findall(r"[A-Za-zÀ-ỹ0-9]{4,}", s))
    score += min(4, len(title_words & sent_words) * 0.8)
    if len(sentence) > 280:
        score -= 2
    return score


def _fallback_sentences(text: str, title: str = "", min_sentences: int = 4, max_sentences: int = 5) -> str:
    sentences = _split_sentences_vi(text)
    if not sentences:
        raw = _clean_news_text(text)
        return raw[:520].rsplit(" ", 1)[0].strip() + ("." if raw else "")

    # Keep intro context, then choose high-information sentences without duplicating the same idea.
    ranked = sorted(enumerate(sentences), key=lambda x: _score_sentence(x[1], title), reverse=True)
    chosen_idx: list[int] = []
    if sentences:
        chosen_idx.append(0)
    seen_roots: set[str] = set()
    for idx, sent in ranked:
        root = " ".join(re.findall(r"[A-Za-zÀ-ỹ0-9]{4,}", sent.lower())[:8])
        if idx in chosen_idx or root in seen_roots:
            continue
        seen_roots.add(root)
        chosen_idx.append(idx)
        if len(chosen_idx) >= max_sentences:
            break
    chosen = [sentences[i] for i in sorted(chosen_idx)][:max_sentences]

    # Add practical impact line if article lacks one.
    joined_lower = " ".join(chosen).lower()
    if len(chosen) < max_sentences and not any(k in joined_lower for k in ("tác động", "rủi ro", "theo dõi", "nhà đầu tư")):
        if any(k in joined_lower for k in ("lợi nhuận", "doanh thu", "cổ tức", "kqkd")):
            chosen.append("Tác động chính nằm ở kỳ vọng lợi nhuận, dòng tiền và định giá của doanh nghiệp liên quan; cần đối chiếu thêm diễn biến giá và thanh khoản.")
        elif any(k in joined_lower for k in ("vn-index", "lãi suất", "tỷ giá", "ftse", "khối ngoại")):
            chosen.append("Tác động thị trường cần theo dõi qua thanh khoản, phản ứng nhóm ngành liên quan và dòng tiền khối ngoại.")
    return " ".join(chosen[:max_sentences])


def _to_bullets(summary: str) -> list[str]:
    return [x.strip() for x in _split_sentences_vi(summary)[:5]]

def _fallback_snippet(item: Dict) -> str:
    full_text = (item.get("fullText") or "").strip()
    if full_text:
        return _fallback_sentences(full_text, item.get("title") or "")
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
        "Tóm tắt đúng 5 câu, khoảng 100-140 từ: đủ bối cảnh, sự kiện chính, hệ quả đầu tư và rủi ro nếu có. "
        "Bắt buộc bôi đậm bằng thẻ <strong>...</strong> các số liệu, thời gian, mã cổ phiếu, tên riêng quan trọng, sự kiện then chốt (% giá trị, chỉ số, tiền, khối lượng, ngày chốt quyền, KQKD). "
        "Phong cách thực dụng, đi thẳng vào vấn đề, không lan man, không lặp tiêu đề, không bịa; ưu tiên thông tin có thể tác động đến giá/nhóm ngành. "
        "Nêu nhận định ảnh hưởng tích cực/tiêu cực/trung tính đến các cổ phiếu có trong bài nếu đủ dữ kiện. "
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
            current["summaryAi"] = result["summary"]
            current["summaryBullets"] = _to_bullets(result["summary"])
        elif current.get("fullText"):
            current["snippet"] = _fallback_snippet(current)
            current["summaryAi"] = current["snippet"]
            current["summaryBullets"] = _to_bullets(current["snippet"])
        else:
            current["snippet"] = ""
        enriched.append(current)
    return enriched
