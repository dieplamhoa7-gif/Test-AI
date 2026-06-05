---
name: vn-equity-research
description: >-
  Bộ khung phân tích & định giá cổ phiếu cho thị trường Việt Nam (và áp dụng được cho cổ phiếu nước ngoài),
  vận hành chủ yếu bằng tiếng Việt, thuật ngữ tài chính giữ nguyên tiếng Anh. Bao gồm: phân tích cơ bản
  (đọc BCTC, chỉ số tài chính, chất lượng lợi nhuận), phân tích kỹ thuật (indicators, mô hình giá, tín hiệu),
  định giá (DCF, SOTP, relative/multiples, cross-check), và xuất báo cáo (Word/PDF/PowerPoint). PHẢI dùng skill
  này bất cứ khi nào người dùng nhắc tới: phân tích cổ phiếu, equity research, định giá doanh nghiệp, đọc/đánh giá
  báo cáo tài chính, P/E - P/B - EV/EBITDA, DCF, SOTP, target price, phân tích kỹ thuật, RSI/MACD, hoặc muốn
  ra một báo cáo phân tích đầu tư — kể cả khi không nói rõ chữ "định giá" hay "phân tích". Không dùng cho việc
  đưa khuyến nghị mua/bán cá nhân hóa (skill này tạo khung phân tích, không phải lời khuyên đầu tư).
---

# VN Equity Research

Skill này giúp dựng phân tích equity research có kỷ luật phương pháp luận, ưu tiên dữ liệu thực tế và kiểm tra chéo, thay vì kết luận cảm tính. Output linh hoạt: phân tích inline trong chat, hoặc xuất file (Word/Excel/PDF/PPT) tùy yêu cầu.

## Nguyên tắc nền (BẮT BUỘC tuân thủ trong mọi phân tích)

1. **Số liệu kỳ đã qua dùng actual, không dùng forecast/plan.** Bất kỳ con số nào phủ một giai đoạn đã kết thúc (doanh thu năm ngoái, LNST quý vừa rồi…) phải dùng số liệu **realized đã công bố**, không dùng kế hoạch hay ước tính cũ. Forecast chỉ cho kỳ tương lai.
2. **Tách các nguồn thu nhập có bản chất khác nhau khi định giá.** Lợi nhuận từ hoạt động cốt lõi và lợi nhuận tài chính (vd: lãi tiền gửi trên lượng tiền mặt lớn) phải định giá tách biệt — core business theo DCF/multiples của ngành, dòng lãi theo perpetuity hoặc giá trị tài sản — không blend chung vào một P/E.
3. **Không double-count giao dịch nội bộ (related-party).** Cổ tức/giao dịch giữa công ty mẹ và công ty con của cùng tập đoàn không được tính trùng vào giá trị.
4. **Mọi giả định định giá phải nêu rõ và biện minh được.** Cost of equity (Rf, β, ERP), growth rate, terminal value, holding discount — ghi rõ nguồn/lý do từng input, không để mặc định ngầm.
5. **Cross-check bằng ≥2 phương pháp độc lập.** Một kết quả định giá đơn lẻ không đủ tin cậy; đối chiếu DCF với relative valuation, và P/E với Gordon Growth/PEG, rồi giải thích chênh lệch.
6. **Phân biệt giá trị nội tại và tác động kế toán.** Các sự kiện như IPO công ty con, thay đổi NCI, pha loãng EPS có thể đổi EPS/cấu trúc sở hữu mà **không** đổi giá trị nội tại — phải tách bạch hai thứ.
7. **Đây là khung phân tích, không phải khuyến nghị đầu tư cá nhân hóa.** Luôn kết thúc phân tích bằng ghi chú rằng đây là tư liệu phân tích, không phải lời khuyên đầu tư, và quyết định cuối cùng cần dữ liệu thị trường cập nhật/ý kiến chuyên gia được cấp phép.

## Quy trình tổng quát

Xác định người dùng đang cần gì rồi vào đúng module (đọc file reference tương ứng — chỉ đọc khi cần để tiết kiệm context):

| Nhu cầu | Đọc file |
|---|---|
| Đọc/đánh giá BCTC, chỉ số tài chính, chất lượng lợi nhuận, "doanh nghiệp này có tốt không" | `references/phan-tich-co-ban.md` |
| Indicators, mô hình giá, hỗ trợ/kháng cự, tín hiệu kỹ thuật, điểm vào/ra theo chart | `references/phan-tich-ky-thuat.md` |
| Target price, DCF, SOTP, relative/multiples, cost of capital, holding discount | `references/dinh-gia.md` |
| Cần ra báo cáo Word/PDF/slide hoặc model Excel | `references/trinh-bay-bao-cao.md` |

Một yêu cầu "phân tích toàn diện cổ phiếu X" thường cần: cơ bản → định giá → (tùy chọn) kỹ thuật cho timing → xuất báo cáo. Làm tuần tự, áp nguyên tắc nền ở mọi bước.

## Thu thập dữ liệu

- Cần số liệu hiện hành (giá, BCTC mới, lãi suất, vĩ mô) → dùng `web_search`/`web_fetch`. Ưu tiên nguồn gốc: công bố thông tin của doanh nghiệp, BCTC kiểm toán, HOSE/HNX, SSC, báo cáo công ty CK uy tín. Tránh diễn đàn/nguồn SEO.
- Nếu người dùng cung cấp file (BCTC PDF, model Excel) → đọc file đó trước, ưu tiên hơn số liệu nhớ.
- Ghi rõ thời điểm và nguồn của mỗi con số quan trọng.

## Khi nào KHÔNG dùng skill này

- Hỏi định nghĩa khái niệm đơn lẻ ("P/E là gì") → trả lời trực tiếp, không cần skill.
- Xin khuyến nghị mua/bán cá nhân hóa ("tôi nên mua X không") → trả về khung phân tích + nhắc đây không phải lời khuyên đầu tư, không phán quyết thay người dùng.
- Tác vụ không liên quan equity research.
