# -*- coding: utf-8 -*-
from pathlib import Path
from ftfy import fix_text
from vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report, has_vietnamese_quality_issue

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / 'hybrid_agent_framework.py',
    ROOT / 'model3_docx_formatter.py',
    ROOT / 'app' / 'pipeline_api.py',
    ROOT / 'app' / 'web_app.py',
]

def fix_file(p: Path) -> None:
    if not p.exists():
        return
    raw = p.read_text(encoding='utf-8', errors='replace')
    fixed = fix_text(raw)
    fixed = repair_vietnamese_text(fixed)
    # Hard fixes for common progress mojibake that ftfy cannot infer perfectly.
    pairs = {
        '?? ': '🔎 ', '? ': '✅ ',
        'ph�t': 'phút', 'l?i': 'lỗi', 'L?i': 'Lỗi', 'da ': 'đã ', 'Da ': 'Đã ',
        'dang ': 'đang ', 'Dang ': 'Đang ', 'ch?y': 'chạy', 'd? li?u': 'dữ liệu',
        'ti?ng Vi?t': 'tiếng Việt', 'c� d?u': 'có dấu', 'kh�ng': 'không',
        'b�o c�o': 'báo cáo', 'ph�n t�ch': 'phân tích', 'c? phi?u': 'cổ phiếu',
        'm?t d?u': 'mất dấu', 'd?y d?': 'đầy đủ', 'tr? l?i': 'trả lời',
        'T?o m?t': 'Tạo một', 'ho�n ch?nh': 'hoàn chỉnh', 'to�n b?': 'toàn bộ',
        'B?n l�': 'Bạn là', 'Nhi?m v?': 'Nhiệm vụ', 'c?a b?n': 'của bạn',
        'chu?n UTF-8': 'chuẩn UTF-8', 'S?a to�n b?': 'Sửa toàn bộ',
        'Ki?m HTML': 'Kiểm HTML', 'h?p l?': 'hợp lệ', 'K?t qu?': 'Kết quả',
        'M?c ti�u': 'Mục tiêu', 'B?t bu?c': 'Bắt buộc', 'Vai tr�': 'Vai trò',
        'Ch? tr?': 'Chỉ trả', 'ch�nh t?': 'chính tả', 'van b?n': 'văn bản',
        'Ph?c h?i': 'Phục hồi', 'chuy�n nghi?p': 'chuyên nghiệp',
    }
    for a,b in pairs.items():
        fixed = fixed.replace(a,b)
    if fixed != raw:
        p.write_text(fixed, encoding='utf-8', newline='\n')
        print('fixed', p.relative_to(ROOT), vietnamese_quality_report(fixed))
    else:
        print('unchanged', p.relative_to(ROOT), vietnamese_quality_report(raw))

for t in TARGETS:
    fix_file(t)

# Install a hard quality gate helper used by Model3 output writers.
guard = ROOT / 'model3_utf8_gate.py'
guard.write_text('''# -*- coding: utf-8 -*-\nfrom __future__ import annotations\nfrom pathlib import Path\nfrom typing import Any\nfrom vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report, has_vietnamese_quality_issue\n\n\ndef clean_model3_text(text: Any) -> str:\n    return repair_vietnamese_text(str(text or ""))\n\n\ndef assert_model3_utf8_quality(text: Any, label: str = "model3") -> str:\n    fixed = clean_model3_text(text)\n    q = vietnamese_quality_report(fixed)\n    # Hard fail on actual mojibake/replacement chars; tolerate a few unaccented acronyms/English words.\n    if int(q.get("mojibake_markers", 0)) > 0 or int(q.get("replacement_chars", 0)) > 0:\n        raise ValueError(f"{label} UTF-8 quality gate failed: {q}")\n    return fixed\n\n\ndef write_model3_text(path: str | Path, text: Any, label: str = "model3") -> None:\n    p = Path(path)\n    p.parent.mkdir(parents=True, exist_ok=True)\n    p.write_text(assert_model3_utf8_quality(text, label), encoding="utf-8", newline="\\n")\n''', encoding='utf-8', newline='\n')
print('wrote model3_utf8_gate.py')
