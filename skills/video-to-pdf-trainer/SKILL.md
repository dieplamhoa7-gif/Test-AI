---
name: video-to-pdf-trainer
description: >
  Tóm tắt video học thuật (YouTube, MIT OCW, hoặc bất kỳ URL nào) và tạo file
  PDF training chuyên nghiệp 30–50 trang, tiếng Việt đầy đủ dấu, theo format
  đẹp với màu sắc, bảng biểu, công thức, box ứng dụng đầu tư. Kích hoạt khi
  người dùng cung cấp: link video/playlist YouTube hoặc OCW, hoặc paste/upload
  nội dung transcript/notes từ bài giảng và yêu cầu tạo tài liệu học tập, tóm
  tắt bài giảng, hoặc training PDF. Cũng kích hoạt khi người dùng nói "tóm tắt
  video này", "làm PDF từ bài này", "training document", "study guide", "tài
  liệu học tập" kèm link hoặc nội dung bài giảng.
---

# Video → Training PDF Skill

## Tổng quan

Skill này chuyển đổi nội dung video bài giảng thành **PDF training chuyên
nghiệp 30–50 trang**, tiếng Việt, có đầy đủ dấu, bảng biểu, công thức toán,
box ứng dụng thực tế. Format giống hệt tài liệu MIT 18.642 đã tạo trước đó.

---

## Bước 1: Thu thập nội dung

### 1A – Từ URL YouTube / MIT OCW

Với mỗi URL được cung cấp, thực hiện tuần tự:

1. **Fetch trang video** (`mcp__workspace__web_fetch`) để lấy:
   - Tiêu đề video, mô tả, tên giảng viên, khóa học
   - Danh sách video trong playlist (nếu là playlist)

2. **Nếu là MIT OCW**, fetch thêm:
   - Trang course home: `https://ocw.mit.edu/courses/<slug>/`
   - Trang calendar: `<course-url>/pages/calendar/`
   - Trang từng tuần: `<course-url>/pages/week-N/` để lấy video descriptions
   - File transcript PDF nếu có link (ví dụ: `<course-url>/<filename>_transcript.pdf`)

3. **Nếu là YouTube thông thường**, fetch:
   - `https://www.youtube.com/watch?v=<ID>` để lấy description
   - Tìm auto-generated transcript nếu có (thử `youtube.com/api/timedtext?v=<ID>&lang=en`)

4. **Tổng hợp nội dung** từ tất cả các nguồn trên thành một outline có cấu trúc.

### 1B – Từ file / nội dung paste

Nếu người dùng upload file (PDF, TXT, DOCX) hoặc paste text:
- Đọc toàn bộ nội dung
- Extract: các heading, định nghĩa, công thức, ví dụ, câu hỏi thảo luận

### 1C – Thông tin còn thiếu

Nếu sau khi fetch vẫn thiếu nội dung chi tiết cho một số phần:
- Dùng kiến thức có sẵn để bổ sung (với ghi chú "Bổ sung từ kiến thức tổng quát")
- **Không** bịa đặt số liệu, tên người, hay công thức sai

---

## Bước 2: Phân tích và cấu trúc nội dung

Từ nội dung thu thập được, tổ chức thành các modules. Với mỗi video/bài giảng,
xác định:

```
Module N: [Tên topic]
├── Lecture info: số, tiêu đề, giảng viên, tổ chức
├── Động lực (Why does this matter?): liên kết với mục tiêu người học
├── Các khái niệm chính: 3–8 khái niệm, mỗi khái niệm có:
│   ├── Định nghĩa chính xác
│   ├── Công thức (nếu có)
│   └── Ví dụ số cụ thể
├── Bảng tóm tắt so sánh (nếu có nhiều trường hợp/phương pháp)
├── Ứng dụng thực tế cho người học
└── Điểm mấu chốt (Key Takeaways): 3–5 bullet
```

**Quy tắc ưu tiên nội dung:**
- Nội dung xuất hiện trong video description + transcript → ưu tiên cao nhất
- Nội dung từ lecture notes PDF → ưu tiên cao
- Kiến thức bổ sung từ domain → ưu tiên thấp (ghi rõ nguồn)

---

## Bước 3: Sinh file PDF

Chạy script Python đã được cung cấp trong thư mục `scripts/`:

```bash
python scripts/generate_pdf.py \
  --title "Tên khóa học / Video" \
  --output "/path/to/output.pdf" \
  --content_json "/tmp/content.json"
```

Trước khi chạy, tạo file `/tmp/content.json` với cấu trúc:

```json
{
  "course_title": "Tên đầy đủ khóa học",
  "subtitle": "Training Guide – [chuyên đề]",
  "instructors": "Danh sách giảng viên",
  "date": "Năm / Kỳ học",
  "guest_lecturers": "Tổ chức khách mời (nếu có)",
  "modules": [
    {
      "number": "1",
      "title": "TÊN MODULE IN HOA",
      "subtitle": "Lectures N–M  ·  Giảng viên",
      "lectures": [
        {
          "number": "1",
          "title": "Tên lecture",
          "instructor": "Tên – Tổ chức"
        }
      ],
      "sections": [
        {
          "heading": "1.1  Tên mục",
          "type": "section",
          "body": "Đoạn văn giải thích chi tiết...",
          "formulas": [
            {"label": "Tên công thức", "formula": "Y = X*beta + epsilon"}
          ],
          "bullets": ["Bullet point 1", "Bullet point 2"],
          "table": {
            "headers": ["Cột 1", "Cột 2", "Cột 3"],
            "rows": [["A", "B", "C"], ["D", "E", "F"]]
          }
        }
      ],
      "invest_box": "Ứng dụng đầu tư thực tế cho người dùng...",
      "key_takeaways": ["Điểm 1", "Điểm 2", "Điểm 3"]
    }
  ],
  "formula_summary": [
    ["Tên", "Công thức đầy đủ"]
  ],
  "references": [
    {"name": "Tên tài liệu", "url": "https://..."}
  ]
}
```

**Nếu script không chạy được** (thiếu thư viện, lỗi path), dùng phương pháp
fallback: viết inline Python trong bash với nội dung đã hardcode từ content.json.
Xem phần **Fallback** cuối file này.

---

## Bước 4: Lưu và trả file

1. Lưu PDF vào workspace folder của người dùng
2. Gọi `mcp__cowork__present_files` để hiển thị file
3. Tóm tắt ngắn: số trang, số modules, các topic chính

---

## Quy tắc nội dung

### Ngôn ngữ
- Tiếng Việt là chính, giữ thuật ngữ kỹ thuật bằng tiếng Anh
- Đầy đủ dấu: đầu tư, chứng khoán, xác suất, phân phối, phương trình...
- Giọng văn chuyên nghiệp, súc tích – không hoa mỹ, không lặp

### Công thức toán
- Tất cả ký tự `<` `>` `&` trong công thức PHẢI escape: `&lt;` `&gt;` `&amp;`
- Hoặc script Python dùng `html.escape(formula)` trước khi truyền vào Paragraph
- Dùng ký hiệu ASCII thuần: `*` thay `×`, `^` thay mũ, `_` thay chỉ số dưới

### Ứng dụng thực tế
- Mỗi module PHẢI có ít nhất 1 ứng dụng cụ thể cho thị trường Việt Nam
  (VN-Index, HOSE, HNX, VCB, HPG, FPT, VHM…) hoặc kinh tế Việt Nam
- Nếu topic không liên quan tài chính, dùng ví dụ từ lĩnh vực của người học

### Độ dài
- Mục tiêu: 30–50 trang PDF
- Nếu video ngắn (< 30 phút): có thể 15–25 trang, không cần kéo dài gượng ép
- Nếu playlist dài: chọn lọc 10–15 video/lectures quan trọng nhất

---

## Cấu trúc PDF chuẩn

```
Trang 1:      BÌA (nền navy, tiêu đề trắng, thông tin khóa học vàng)
Trang 2:      MỤC LỤC (danh sách modules + sections)
Trang 3+:     NỘI DUNG (mỗi module mở đầu bằng chapter banner navy)
Trang áp chót: BẢNG CÔNG THỨC (nếu có toán học)
Trang cuối:   LỊCH HỌC + TÀI LIỆU THAM KHẢO
```

Thiết kế màu sắc:
- Navy `#1B2B4B`: header, chapter banner, table header
- MIT Red `#A31F34`: accent line top of page
- Blue `#2E5FA3`: lecture banner, section headings, formula labels
- Gold `#C49A1B`: module label, key takeaways border, references
- Green `#1B5E20`: investment application boxes
- Light gray `#F4F6FA`: formula background, alternating table rows

---

## Fallback: Inline Python

Nếu không thể chạy `scripts/generate_pdf.py`, dùng template này trực tiếp:

```python
# -*- coding: utf-8 -*-
import html as _html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV",   FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FONT_DIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI",FONT_DIR + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-M", FONT_DIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B",
                               italic="DV-I", boldItalic="DV-BI")

NAVY=colors.HexColor("#1B2B4B"); BLUE=colors.HexColor("#2E5FA3")
RED=colors.HexColor("#A31F34");   GOLD=colors.HexColor("#C49A1B")
GREEN=colors.HexColor("#1B5E20"); LGRN=colors.HexColor("#F0FFF4")
LGRAY=colors.HexColor("#F4F6FA"); GRAY=colors.HexColor("#8A8B8C")
LGOLD=colors.HexColor("#FFFDE7"); WHITE=colors.white

def mk(nm,fn="DV",fs=10,ld=None,tc=colors.black,al=TA_JUSTIFY,
       sb=0,sa=4,li=0,ri=0,bg=None):
    kw=dict(fontName=fn,fontSize=fs,leading=ld or fs*1.5,
            textColor=tc,alignment=al,spaceBefore=sb,spaceAfter=sa,
            leftIndent=li,rightIndent=ri)
    if bg: kw["backColor"]=bg
    return ParagraphStyle(nm,**kw)

# Thêm nội dung và build tương tự generate_mit_v3.py
# [AI điền nội dung cụ thể vào đây dựa trên video đầu vào]
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `paraparser: syntax error` | `<` `>` chưa escape trong formula | Dùng `_html.escape(formula)` |
| Font rendering lỗi (ký tự ■) | Dùng Helvetica thay vì DejaVu | Đổi tất cả fontName thành "DV" |
| `Table too wide` | Tổng colWidths vượt page width | Page width = 21cm - 3.6cm margins = ~17.4cm |
| `style already registered` | Tạo ParagraphStyle trùng tên trong loop | Thêm uid vào tên style |
| Video transcript không accessible | YouTube block fetch | Dùng description + domain knowledge |

---

## Ví dụ câu gọi skill thành công

- "Tóm tắt video này cho tui: https://www.youtube.com/watch?v=abc123"
- "Làm PDF training từ playlist này: https://youtube.com/playlist?list=..."
- "Tôi có transcript bài giảng về Machine Learning, làm file PDF đẹp giống MIT cho tôi"
- "Fetch hết các video OCW này rồi tạo training guide: [URL]"
- "Em làm PDF tóm tắt nội dung file này thành study guide cho anh"
