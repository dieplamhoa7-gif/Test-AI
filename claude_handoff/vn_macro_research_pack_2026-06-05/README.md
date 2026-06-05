# VN Macro Research Pack - handoff for Claude

Gói này tổng hợp phần vĩ mô đã thu thập/xây dựng cho LH Investment, để gửi Claude đọc tiếp hoặc cải thiện.

## Nội dung

```text
vn_macro_research_pack_2026-06-05/
├─ README.md
├─ MACRO_SUMMARY_VI.md
├─ code/
│  ├─ macro_cycle.py
│  ├─ build_macro_local_page.py
│  └─ tmp_probe_widata.py            # nếu tồn tại trong repo gốc
├─ data/
│  ├─ macro_cycle_local.json         # snapshot Pinetree + macro score local-test
│  ├─ macro_overview.json            # macro score static cache cũ
│  └─ sbv_probe.json                 # kết quả probe NHNN/SBV
├─ reports/
│  └─ source_memory_2026-05-04.md    # raw memory/source notes
└─ skills/
   └─ vn-macro-cycle-research/
      ├─ SKILL.md
      └─ references/
         └─ macro-source-map.md
```

## Cách chạy nhanh

Từ folder code trong repo gốc hoặc copy về đúng cấu trúc `stock-news-backend`:

```bash
py -3 code/macro_cycle.py --date 2026-05-04
```

Trong repo gốc, file `stock-news-backend/build_macro_local_page.py` tạo preview local `stock-news-backend/local_preview/macro.html`.

## Cảnh báo chất lượng dữ liệu

- Đây là local/test pack, không phải dữ liệu production.
- Pinetree Morning Brief là nguồn snapshot ngày, không phải database lịch sử 1 năm hoàn chỉnh.
- SBV/NHNN probe trả HTTP 200 nhưng redirect về trang chủ; chưa lấy được bảng OMO/liên ngân hàng có cấu trúc.
- OMO + interbank 1-year hoàn chỉnh khả năng cần WiData/WiGroup/WiFeed hoặc TradingEconomics paid API.
- Không dùng dữ liệu này làm khuyến nghị đầu tư cá nhân hóa.
