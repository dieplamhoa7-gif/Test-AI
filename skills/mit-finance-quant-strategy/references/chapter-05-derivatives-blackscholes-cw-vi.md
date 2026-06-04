# Chương 5 — Derivatives, Black-Scholes và Chứng quyền/CW

Nguồn video:

- Lecture 7 — Linear Rates, Products, and Models
- Lecture 20 — Event Exchange
- Lecture 21 — Black-Scholes Formula, Risk Neutral Valuation

---

## 1. Vì sao chương này quan trọng với anh?

Anh có quan tâm chứng quyền/CW. CW không thể phân tích như cổ phiếu thường. Cùng một cổ phiếu cơ sở tăng 5%, CW có thể:

- tăng mạnh,
- tăng ít,
- không tăng,
- thậm chí giảm,

nếu time decay, spread, implied volatility hoặc thanh khoản bất lợi.

Black-Scholes không phải để thần thánh hóa công thức, mà để hiểu các thành phần định giá option-like product.

---

## 2. Derivative là gì?

Derivative là sản phẩm có giá trị phụ thuộc tài sản cơ sở.

Ví dụ:

- option,
- futures,
- swaps,
- warrants,
- chứng quyền có bảo đảm.

CW phụ thuộc vào:

- giá cổ phiếu cơ sở,
- giá thực hiện,
- thời gian còn lại,
- volatility,
- lãi suất,
- cổ tức nếu có,
- thanh khoản/spread.

---

## 3. Black-Scholes — hiểu trực giác

Black-Scholes định giá option dựa trên ý tưởng no-arbitrage và risk-neutral valuation.

Các biến chính:

```text
S = giá tài sản cơ sở
K = strike/giá thực hiện
T = thời gian còn lại
r = lãi suất phi rủi ro
σ = volatility
```

Với call option/CW mua:

- S tăng → giá option tăng.
- K càng thấp so với S → option càng in-the-money.
- T càng dài → option thường có giá trị thời gian cao hơn.
- σ càng cao → option thường đắt hơn.
- Gần đáo hạn → time decay mạnh.

---

## 4. Risk-neutral valuation

Risk-neutral không có nghĩa thị trường không rủi ro. Nó là kỹ thuật định giá: chiết khấu kỳ vọng payoff dưới xác suất risk-neutral.

Bài học thực tế: giá phái sinh không chỉ là kỳ vọng hướng đi, mà còn là giá của volatility và thời gian.

---

## 5. Áp dụng cho CW Việt Nam

### 5.1. Không xếp hạng CW chỉ bằng upside cơ sở

Sai lầm phổ biến:

```text
MWG target +10% → chọn CW leverage cao nhất
```

Thiếu:

- CW còn bao nhiêu ngày,
- break-even bao xa,
- spread bao nhiêu,
- thanh khoản thế nào,
- implied volatility có đang quá đắt không,
- delta/gamma hiệu dụng.

### 5.2. CW score nên có

```json
{
  "underlying": "MWG",
  "cw": "CMWGxxxx",
  "daysToMaturity": 45,
  "moneyness": "near_the_money",
  "breakEvenDistancePct": 7.2,
  "spreadPct": 2.5,
  "liquidityScore": 68,
  "timeDecayPenalty": 22,
  "underlyingUpsideScore": 75,
  "finalCWScore": 61
}
```

### 5.3. Rule thực tế

- Tránh CW quá gần đáo hạn nếu không phải trade rất ngắn.
- Tránh spread quá rộng.
- Tránh CW thanh khoản thấp.
- Không mua CW chỉ vì leverage cao.
- Luôn so break-even với target cổ phiếu cơ sở.

---

## 6. Checklist triển khai CW module

- [ ] Tính days to maturity.
- [ ] Tính moneyness.
- [ ] Tính break-even.
- [ ] Tính spread/liquidity penalty.
- [ ] Tính time decay penalty.
- [ ] Kết hợp với signal của underlying.
- [ ] Cảnh báo CW rủi ro cao.

---

## 7. Bài tập cho Hòa Đại ka

1. Anh dùng CW để swing 3–10 ngày hay giữ lâu hơn?
2. Anh chấp nhận spread tối đa bao nhiêu?
3. Anh ưu tiên an toàn hay leverage cao?

Nếu áp dụng ngay, Tiểu đệ đề xuất: **nâng CW ranking hiện tại thành score có time decay + spread + break-even + liquidity**.
