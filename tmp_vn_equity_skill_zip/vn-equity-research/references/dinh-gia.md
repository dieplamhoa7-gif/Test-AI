# Định giá (Valuation)

Mục tiêu: ra giá trị nội tại / target price có cơ sở, dùng ≥2 phương pháp độc lập và kiểm tra chéo. Áp toàn bộ nguyên tắc nền trong SKILL.md, đặc biệt: actual cho kỳ đã qua, tách nguồn thu nhập khác bản chất, biện minh mọi giả định, không double-count related-party.

## Khung lựa chọn phương pháp

| Tình huống | Phương pháp chính |
|---|---|
| Dòng tiền dự báo được, doanh nghiệp ổn định | DCF (FCFF/FCFE) |
| Tập đoàn nhiều mảng bản chất khác nhau, hoặc có dòng thu tài chính lớn | **SOTP** (Sum-of-the-parts) |
| Có nhóm so sánh (peers) rõ ràng | Relative / multiples |
| Cổ phiếu trả cổ tức ổn định | Dividend Discount Model (Gordon Growth) |

Thực hành tốt: chạy ≥2 phương pháp rồi đối chiếu, giải thích chênh lệch (nguyên tắc nền #5).

## 1. Cost of capital (nêu rõ từng input — nguyên tắc nền #4)

**Cost of equity (CAPM):** Re = Rf + β × ERP
- **Rf:** lợi suất trái phiếu chính phủ kỳ hạn dài (vd 10 năm) của thị trường tương ứng — ghi rõ thời điểm.
- **β:** beta của cổ phiếu/ngành; nêu nguồn và cách ước lượng (regression hay bottom-up; có unlever/relever theo cấu trúc vốn không).
- **ERP:** equity risk premium thị trường — ghi rõ nguồn/giá trị giả định.

**WACC** = E/V × Re + D/V × Rd × (1−t), với Rd = chi phí nợ, t = thuế suất hiệu dụng. Dùng WACC chiết khấu FCFF; dùng Re chiết khấu FCFE/cổ tức.

## 2. DCF

1. **Dự báo dòng tiền** 5 năm (explicit): doanh thu → biên → EBIT → NOPAT → +D&A −CapEx −ΔNWC = FCFF (hoặc FCFE). Kỳ đã qua dùng actual; chỉ dự báo kỳ tương lai.
2. **Terminal value:** Gordon Growth TV = FCF₍ₙ₊₁₎ / (WACC − g); g (long-run growth) phải hợp lý (≤ tăng trưởng danh nghĩa dài hạn của nền kinh tế). Hoặc dùng exit multiple. Kiểm tra tỷ trọng TV trong tổng giá trị — TV quá lớn (>70–75%) là rủi ro mô hình.
3. **Chiết khấu** về hiện tại theo WACC/Re → enterprise value → trừ net debt (+ tài sản ngoài hoạt động) → equity value → chia số cổ phần → giá trị/cổ phiếu.
4. **Phân tích độ nhạy** (sensitivity) theo WACC và g (ma trận 2 chiều) — bắt buộc.

## 3. SOTP (cho tập đoàn đa mảng / có dòng tài chính lớn)

Định giá từng cấu phần theo phương pháp phù hợp rồi cộng lại:
- **Mảng cốt lõi:** DCF hoặc multiple của ngành tương ứng.
- **Dòng lãi tài chính** (lãi tiền gửi trên tiền mặt ròng lớn): định giá riêng như **perpetuity** (lãi ròng / suất chiết khấu phù hợp) hoặc tính theo giá trị khối tài sản tiền mặt — KHÔNG blend vào P/E cốt lõi (nguyên tắc nền #2).
- **Công ty con / khoản đầu tư:** theo giá trị thị trường hoặc định giá riêng; loại trừ giao dịch nội bộ để tránh tính trùng (nguyên tắc nền #3).
- **Holding discount:** trừ chiết khấu công ty mẹ; nên **phân rã định lượng** thay vì áp một con số chung — ví dụ: chi phí thanh khoản + chi phí bộ máy mẹ (parent overhead) + ma sát thuế cổ tức. Ghi rõ cấu phần.
- **Trừ nợ ròng và các nghĩa vụ cấp tập đoàn** để ra equity value.

## 4. Relative / multiples

- Chọn peers cùng ngành, quy mô, mô hình tương đồng; nêu lý do chọn.
- Multiples: P/E, P/B, EV/EBITDA, EV/Sales, PEG. Điều chỉnh cho khác biệt tăng trưởng/biên/rủi ro.
- Dùng forward multiples khi có dự báo đáng tin; cẩn trọng khi earnings có yếu tố one-off (chuẩn hóa trước).

## 5. Cross-check (bắt buộc)

- Đối chiếu **DCF ↔ relative**: chênh lệch lớn → rà giả định.
- Kiểm tra **P/E ngụ ý** từ DCF so với **Gordon Growth** và **PEG**: P/E hợp lý ≈ payout × (1+g)/(Re−g); PEG ≈ P/E / tăng trưởng EPS.
- Nếu xây model Excel: thiết kế các nhóm cross-check để kiểm tra hội tụ (convergence) giữa các phương pháp.

## 6. Tác động kế toán vs giá trị nội tại

Sự kiện như IPO công ty con, tăng tỷ lệ NCI, pha loãng EPS làm thay đổi EPS của cổ đông mẹ và cơ cấu sở hữu **mà không** đổi giá trị nội tại của cả tập đoàn. Trình bày tách bạch: (a) giá trị nội tại trước/sau, (b) tác động EPS/NCI thuần túy kế toán. Tránh kết luận "rẻ/đắt đi" chỉ vì EPS thay đổi do pha loãng.

## 7. Kịch bản

Dựng tối thiểu 3 kịch bản (thận trọng/cơ sở/lạc quan) với giả định khác nhau về tăng trưởng, biên, định giá đầu ra; nêu xác suất định tính và dải giá trị. Kết thúc bằng ghi chú "tư liệu phân tích, không phải lời khuyên đầu tư".
