from __future__ import annotations

import re
from typing import Any

BAD_MOJIBAKE_MARKERS = (
    "\ufffd", "Ã", "Ä", "Æ", "Ð", "ð", "áº", "á»", "â€",
    "ThA", "phá»", "Ä‘", "Æ°", "Æ¡",
    # Some upstream caches/providers replace Vietnamese bytes with literal '?'
    # instead of U+FFFD. Count only high-signal Vietnamese finance phrases to
    # avoid treating normal question marks as mojibake.
    "B�o", "c? phi", "c? ph", "d?u t", "T�m t", "d? li", "k? thu", "d�nh gi",
    "h? tr", "kh�ng c", "r?i ro", "tin t?c", "l?i nhu", "khuy?n ngh",
)

UNACCENTED_MARKERS = (
    "Tm tt", "dau tu", "Ngan hang", "Ngn hng", "Viet Nam", "Vit Nam",
    "Thanh Vuong", "Thnh Vng", "co phieu", "c phiu", "phan tich", "phn tch",
    "ky thuat", "k thut", "tin tuc", "tin tc", "loi nhuan", "li nhun",
    "tich cuc", "tch cc", "tieu cuc", "tiu cc", "trung tinh", "trung tnh",
    "danh gia", "nh gi", "tac dong", "tc ng", "ho tro", "h tr", "khang cu", "khng c",
    "thanh khoan", "thanh khon", "rui ro", "ri ro", "du lieu", "d liu",
    "dieu kien", "iu kin", "ket qua", "kt qu", "khuyen nghi", "khuyn ngh",
)

VI_PHRASE_FIXES: list[tuple[str, str]] = [
    # Literal-question-mark mojibake seen in generated DOCX files.
    ("BAO CAO PHAN TICH C? PHI?U", "BÁO CÁO PHÂN TÍCH CỔ PHIẾU"),
    ("B�o c�o", "Báo cáo"), ("b�o c�o", "báo cáo"),
    ("c? phi?u", "cổ phiếu"), ("C? phi?u", "Cổ phiếu"),
    ("nh� d?u tu", "nhà đầu tư"), ("d?u tu", "đầu tư"),
    ("T?ng h?p", "Tổng hợp"), ("t?ng h?p", "tổng hợp"),
    ("tin t?c", "tin tức"), ("Tin t?c", "Tin tức"),
    ("k? thu?t", "kỹ thuật"), ("K? thu?t", "Kỹ thuật"),
    ("d?nh gi�", "đánh giá"), ("D?nh gi�", "Đánh giá"),
    ("r?i ro", "rủi ro"), ("R?i ro", "Rủi ro"),
    ("d? li?u", "dữ liệu"), ("D? li?u", "Dữ liệu"),
    ("h? tr?", "hỗ trợ"), ("H? tr?", "Hỗ trợ"),
    ("kh�ng c?", "kháng cự"), ("Kh�ng c?", "Kháng cự"),
    ("l?i nhu?n", "lợi nhuận"), ("L?i nhu?n", "Lợi nhuận"),
    ("khuy?n ngh?", "khuyến nghị"), ("Khuy?n ngh?", "Khuyến nghị"),
    ("di?u ki?n", "điều kiện"), ("Di?u ki?n", "Điều kiện"),
    ("h�nh d?ng", "hành động"), ("H�nh d?ng", "Hành động"),
    ("theo doi", "theo dõi"), ("Theo doi", "Theo dõi"),
    ("v�ng gi�", "vùng giá"), ("V�ng gi�", "Vùng giá"),
    ("thanh kho?n", "thanh khoản"), ("Thanh kho?n", "Thanh khoản"),
    ("c?n", "cần"), ("C?n", "Cần"),
    ("chua", "chưa"), ("Chua", "Chưa"),
    ("Tm tt", "Tóm tắt"), ("tom tat", "tóm tắt"),
    ("dau tu", "đầu tư"),
    ("Ngan hang", "Ngân hàng"), ("Ngn hng", "Ngân hàng"),
    ("Viet Nam", "Việt Nam"), ("Vit Nam", "Việt Nam"),
    ("Thanh Vuong", "Thịnh Vượng"), ("Thnh Vng", "Thịnh Vượng"),
    ("Kch bn", "Kịch bản"), ("kich ban", "kịch bản"),
    ("Trigger / kch hot", "Trigger / kích hoạt"), ("kch hot", "kích hoạt"),
    ("iu kin k thut", "Điều kiện kỹ thuật"), ("dieu kien ky thuat", "điều kiện kỹ thuật"),
    ("iu kin tin tc / c bn", "Điều kiện tin tức / cơ bản"), ("dieu kien tin tuc / co ban", "điều kiện tin tức / cơ bản"),
    ("Vng gi theo di", "Vùng giá theo dõi"), ("vung gia theo doi", "vùng giá theo dõi"),
    ("Xc sut / tin cy nh tnh", "Xác suất / tin cậy định tính"), ("xac suat / tin cay dinh tinh", "xác suất / tin cậy định tính"),
    ("Hnh ng ph hp", "Hành động phù hợp"), ("hanh dong phu hop", "hành động phù hợp"),
    ("Tin tc", "Tin tức"), ("tin tuc", "tin tức"),
    ("c bn", "cơ bản"), ("co ban", "cơ bản"),
    ("k thut", "kỹ thuật"), ("ky thuat", "kỹ thuật"),
    ("phn tch", "phân tích"), ("phan tich", "phân tích"),
    ("c phiu", "cổ phiếu"), ("co phieu", "cổ phiếu"),
    ("nh gi", "đánh giá"), ("danh gia", "đánh giá"),
    ("tc ng", "tác động"), ("tac dong", "tác động"),
    ("tch cc", "tích cực"), ("tich cuc", "tích cực"),
    ("tiu cc", "tiêu cực"), ("tieu cuc", "tiêu cực"),
    ("trung tnh", "trung tính"), ("trung tinh", "trung tính"),
    ("r ri", "rủi ro"), ("ri ro", "rủi ro"), ("rui ro", "rủi ro"),
    ("h tr", "hỗ trợ"), ("ho tro", "hỗ trợ"),
    ("khng c", "kháng cự"), ("khang cu", "kháng cự"),
    ("thanh khon", "thanh khoản"), ("thanh khoan", "thanh khoản"),
    ("li nhun", "lợi nhuận"), ("loi nhuan", "lợi nhuận"),
    ("doanh nghip", "doanh nghiệp"), ("doanh nghiep", "doanh nghiệp"),
    ("d liu", "dữ liệu"), ("du lieu", "dữ liệu"),
    ("kt qu", "kết quả"), ("ket qua", "kết quả"),
    ("khuyn ngh", "khuyến nghị"), ("khuyen nghi", "khuyến nghị"),
    ("duy tr  tng trng", "duy trì tăng trưởng"), ("duy tr tng trng", "duy trì tăng trưởng"),
    ("d bo tng", "dự báo tăng"), ("Da trn tiu /snippet", "Dựa trên tiêu đề/snippet"),
    ("Da trn", "Dựa trên"), ("tiu /snippet", "tiêu đề/snippet"),
    ("i hi c ng", "Đại hội cổ đông"), ("Thng qua tng vn", "Thông qua tăng vốn"),
    ("t mc tiu tng trng", "đặt mục tiêu tăng trưởng"), ("Bo Chnh ph", "Báo Chính phủ"),
    ("K hoch tng vn", "Kế hoạch tăng vốn"), ("mc tiu", "mục tiêu"),
    ("tn hiu", "tín hiệu"), ("nng lc", "năng lực"), ("cho vay", "cho vay"),
    ("cu chuyn", "câu chuyện"), ("m rng", "mở rộng"), ("pha long", "pha loãng"),
    ("pht hnh", "phát hành"), ("thm", "thêm"), ("Mc tiu", "Mục tiêu"),
    ("tng vn ln", "tăng vốn lên"), ("t ng", "tỷ đồng"),
    ("Tóm tắt T VPB", "Tóm tắt VPB"), ("Sn:", "Sàn:"), ("Kt lun", "Kết luận"),
    ("Gc kỹ thuật", "Góc kỹ thuật"), ("Gc cơ bản", "Góc cơ bản"),
    ("ang  trng thi", "đang ở trạng thái"), ("ang trng thi", "đang trạng thái"),
    ("theo di", "theo dõi"), ("cha c", "chưa có"), ("xc nhn", "xác nhận"),
    ("bt ph", "bứt phá"), ("r nhng", "rõ nhưng"), ("cng cha", "cũng chưa"),
    ("ri vo", "rơi vào"), ("trng thi", "trạng thái"), ("suy yu", "suy yếu"),
    ("mnh", "mạnh"), ("Gi hin", "Giá hiện"), ("di MA200", "dưới MA200"),
    ("ngn hn", "ngắn hạn"), ("dữ liệu fundamental nh lng", "dữ liệu fundamental định lượng"),
    ("thiu ng k", "thiếu đáng kể"), ("cc tn hiu nh tnh", "các tín hiệu định tính"),
    ("nghing v hng", "nghiêng về hướng"), ("cng c vn", "củng cố vốn"),
    ("ti u cu trc", "tối ưu cấu trúc"), ("ngun vn", "nguồn vốn"),
    ("Stance hin ti", "Stance hiện tại"), ("trung tính nghing tích cực c iu kin", "trung tính nghiêng tích cực có điều kiện"),
    ("Ph hp vi", "Phù hợp với"), ("chin lc", "chiến lược"), ("vt kháng cự", "vượt kháng cự"),
    ("mua ui", "mua đuổi"), ("gia vng", "giữa vùng"), ("lng l", "lưỡng lự"),
    ("u tin dng", "Ưu tiên dùng"), ("mi hn", "mới hơn"), ("khi c;", "khi có;"),
    ("Nu thiu", "Nếu thiếu"), ("tht s", "thật sự"), ("ghi r", "ghi rõ"),
    ("Ch bo", "Chỉ báo"), ("Gi tr tht t LHInvestment", "Giá trị thật từ LHInvestment"),
    ("Gi tr tht", "Giá trị thật"), ("Nhn", "Nhãn"),
    ("ngha đầu tư", "Ý nghĩa đầu tư"), ("vng theo dõi", "vùng theo dõi"),
]


def _marker_count(text: str, markers: tuple[str, ...]) -> int:
    # Mojibake markers must be counted case-sensitively. If we lowercase them,
    # marker "Ã" becomes "ã" and clean Vietnamese words like "Nhãn" become false positives.
    if markers is BAD_MOJIBAKE_MARKERS:
        return sum(text.count(m) for m in markers)
    lower = text.lower()
    return sum(lower.count(m.lower()) for m in markers)


def repair_vietnamese_text(text: Any) -> str:
    s = str(text)
    if not s:
        return s
    try:
        from ftfy import fix_text  # type: ignore
        s2 = fix_text(s)
        if _marker_count(s2, BAD_MOJIBAKE_MARKERS) <= _marker_count(s, BAD_MOJIBAKE_MARKERS):
            s = s2
    except Exception:
        pass
    if _marker_count(s, BAD_MOJIBAKE_MARKERS):
        for enc in ("latin1", "cp1252"):
            try:
                fixed = s.encode(enc, "ignore").decode("utf-8", "ignore")
                if fixed and _marker_count(fixed, BAD_MOJIBAKE_MARKERS) < _marker_count(s, BAD_MOJIBAKE_MARKERS):
                    s = fixed
                    break
            except Exception:
                pass
    for src, dst in VI_PHRASE_FIXES:
        s = re.sub(re.escape(src), dst, s, flags=re.I)
    # Collapse accidental repeated Vietnamese syllables caused by earlier cleaners/providers.
    repeat_fixes = {
        "Đáđánh giá": "Đánh giá",
        "địđánh giá": "đánh giá",
        "điều chỉđánh giá": "điều chỉnh",
        "điều chỉ đánh giá": "điều chỉnh",
        "Target/địđánh giá": "Target/định giá",
        "target/địđánh giá": "target/định giá",
        "Tóm tắtỷ đồngắn gọn": "Tóm tắt ngắn gọn",
        "tóm tắtỷ đồngắn gọn": "tóm tắt ngắn gọn",
        "Kỹ thuậtỷ đồngắn hạn": "Kỹ thuật ngắn hạn",
        "kỹ thuậtỷ đồngắn hạn": "kỹ thuật ngắn hạn",
        "đáđáđáđánh giáááá": "đánh giá",
        "đáđáđánh giááá": "đánh giá",
        "đáđánh giáá": "đánh giá",
        "đánh giáá": "đánh giá",
        "đáđánh giá": "đánh giá",
        "Kỹ thuậtỷ đồngắn": "Kỹ thuật ngắn hạn",
        "kỹ thuậtỷ đồngắn": "kỹ thuật ngắn hạn",
        "Tóm tắtỷ đồngắn": "Tóm tắt ngắn gọn",
        "tóm tắtỷ đồngắn": "tóm tắt ngắn gọn",
        "Fundamentalvà": "Fundamental và",
        "đầutư": "đầu tư",
        "Kếthoạch": "Kế hoạch",
        "chínhỗ trợong": "chính trong",
        "ỗ trợong": "trong",
        "ỗ trợong context": "trong context",
    }
    for src, dst in repeat_fixes.items():
        s = s.replace(src, dst)
    # Regex fallback for visually similar composed Vietnamese glitches.
    s = re.sub(r"(?i)target/đ.đánh giá", "Target/định giá", s)
    s = re.sub(r"(?i)đ.đánh giá", "đánh giá", s)
    s = re.sub(r"(?i)điều chỉ\s*đánh giá", "điều chỉnh", s)
    s = re.sub(r"(?i)Đ.đánh giá", "Đánh giá", s)
    # Collapse accidental repeated Vietnamese vowels after providers/cleaners, e.g. rõõõõõ -> rõ.
    s = re.sub(r"([àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ])\1{1,}", r"\1", s, flags=re.I)
    s = s.replace("Ð", "Đ").replace("ð", "đ")
    return s


def clean_vietnamese_object(obj: Any) -> Any:
    if isinstance(obj, str):
        return repair_vietnamese_text(obj)
    if isinstance(obj, list):
        return [clean_vietnamese_object(x) for x in obj]
    if isinstance(obj, dict):
        return {repair_vietnamese_text(k) if isinstance(k, str) else k: clean_vietnamese_object(v) for k, v in obj.items()}
    return obj


def vietnamese_quality_report(text: str) -> dict[str, int | bool]:
    s = str(text or "")
    mojibake = _marker_count(s, BAD_MOJIBAKE_MARKERS)
    unaccented = _marker_count(s, UNACCENTED_MARKERS)
    replacement = s.count("\ufffd")
    return {
        "mojibake_markers": mojibake,
        "unaccented_markers": unaccented,
        "replacement_chars": replacement,
        "needs_repair": bool(mojibake or unaccented >= 3 or replacement),
    }


def has_vietnamese_quality_issue(text: str) -> bool:
    return bool(vietnamese_quality_report(text)["needs_repair"])
