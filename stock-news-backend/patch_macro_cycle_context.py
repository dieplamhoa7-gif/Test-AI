from __future__ import annotations

import json
import re
from pathlib import Path

HTML = Path("firebase_public/macro.html")
text = HTML.read_text(encoding="utf-8")
match = re.search(r"const DATA=(\{.*?\});\n", text, re.S)
if not match:
    raise SystemExit("const DATA not found")

data = json.loads(match.group(1))
phases = data.get("phases") or []
if not phases:
    raise SystemExit("DATA.phases not found")

phase = phases[-1]
if phase.get("s") != "2026-01":
    raise SystemExit(f"Unexpected latest phase: {phase}")

phase["name"] = "Cuối mở rộng / Quá nhiệt — phòng thủ"
phase["desc"] = (
    "Tăng trưởng thực vẫn mạnh (GDP 8,4%; IIP 8,79%) nên chưa phải suy thoái. "
    "Tuy nhiên CPI 5,58% vượt ngưỡng tham chiếu 4,5%, tín dụng 17,96% tăng nhanh hơn M2 6,42% "
    "(khe hở khoảng 11,5 điểm %), USD/VND ở 26.500 và dầu Brent gần 95,63 USD/thùng làm tăng áp lực "
    "lạm phát, tỷ giá và chi phí vốn. NHNN đang bơm ròng OMO khoảng 4.898 tỷ đồng, cho thấy hỗ trợ "
    "thanh khoản ngắn hạn nhưng chưa đủ xác nhận một chu kỳ nới lỏng mới. Kết luận: kinh tế ở cuối pha "
    "mở rộng, có dấu hiệu quá nhiệt và chuyển sang trạng thái phòng thủ; rủi ro điều chỉnh/biến động của "
    "thị trường cao hơn, nhưng chưa có đủ bằng chứng để gọi là suy thoái hay risk-off toàn diện."
)

payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
updated = text[: match.start(1)] + payload + text[match.end(1) :]
HTML.write_text(updated, encoding="utf-8")
print(json.dumps({"status": "ok", "phaseName": phase["name"]}, ensure_ascii=True))
