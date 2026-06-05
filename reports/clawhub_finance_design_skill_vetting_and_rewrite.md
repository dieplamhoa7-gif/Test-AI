# ClawHub Finance/Design Skill Vetting & Clean Rewrite

## Yêu cầu của Hòa Đại ka

Đọc các skill ClawHub đã chọn, tránh dính mã độc, và viết lại thành skill nội bộ sạch.

## Kết quả truy cập

ClawHub search trả về danh sách skill hữu ích theo nhóm:

- `@hypier / Tradingview Quantitative`
- `@veeramanikandanr48 / Technical Analyst`
- `@qiujiahong / Finance Report Analyzer`
- `@ivangdavila / Pdf Generator`
- `@smseow001 / MiniMax PDF`
- `@antonia-sz / Frontend Design Pro`

Tuy nhiên, một số trang detail mở trực tiếp trả `We couldn't find that page` hoặc không render nội dung code/skill đầy đủ. Vì vậy Tiểu đệ **không cài và không copy code** từ các skill đó.

## Quyết định an toàn

Thay vì import code ngoài, Tiểu đệ viết lại một skill nội bộ sạch:

- `skills/safe-finance-investing-skill-pack/SKILL.md`
- `skills/safe-finance-investing-skill-pack/metadata.json`

Skill này chỉ lấy ý tưởng workflow/chức năng từ các nhóm skill:

1. Quantitative / technical analysis.
2. Chart image analyst.
3. Fundamental / financial report analyzer.
4. Professional PDF/report generator.
5. Frontend/UI polish for finance dashboards.

## Red flags tránh được

- Không chạy script lạ.
- Không tải package lạ.
- Không gửi API key/token ra ngoài.
- Không dùng endpoint không rõ.
- Không copy prompt có thể chứa prompt injection.
- Không thay đổi production Firebase/web.

## Nội dung rewrite

Skill nội bộ có các module:

- Module A — Quantitative / Technical Stock Analysis
- Module B — Chart Image Analyst
- Module C — Fundamental / Financial Report Analyzer
- Module D — Professional PDF / Report Generator
- Module E — Frontend / UI Polish for Finance Dashboards
- Module F — Selection Recommendations from ClawHub Search

## Cách dùng

Khi Hòa Đại ka yêu cầu phân tích cổ phiếu, chart image, báo cáo tài chính, tạo PDF, hoặc polish UI, Tiểu đệ sẽ dùng skill nội bộ này trước, kết hợp các skill hiện có trong workspace.
