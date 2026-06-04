# Chương 4 — Portfolio, Risk và Volatility: từ chọn mã sang quản trị danh mục

Nguồn video:

- Lecture 10 — Counterparty Risk Optimization
- Lecture 13 — Portfolio Management
- Lecture 19 — Volatility Modeling
- Lecture 18 — Data Science and AI in Biomedical Portfolios

---

## 1. Ý chính

Một model chọn cổ phiếu tốt chưa đủ. Nếu không quản trị danh mục, anh có thể chọn đúng nhiều mã nhưng vẫn rủi ro vì:

- các mã cùng ngành,
- tương quan cao,
- volatility cao,
- liquidity thấp,
- thị trường chung xấu,
- position size quá lớn.

Chương này chuyển trọng tâm từ “mã nào tốt?” sang “nên nắm bao nhiêu, cùng với mã nào, trong điều kiện rủi ro nào?”.

---

## 2. Portfolio Management

### 2.1. Không chỉ ranking từng mã

Nếu web xếp hạng:

```text
1. SSI
2. VND
3. HCM
4. VCI
5. MBS
```

thì nhìn có vẻ 5 mã, nhưng thực ra gần như một bet vào ngành chứng khoán. Danh mục không đa dạng.

### 2.2. Rủi ro danh mục

Rủi ro danh mục phụ thuộc:

- volatility từng mã,
- correlation giữa các mã,
- tỷ trọng từng mã,
- rủi ro ngành,
- rủi ro thị trường.

### 2.3. Position sizing

Không nên mỗi mã đều tỷ trọng bằng nhau. Có thể sizing theo:

- confidence,
- volatility,
- liquidity,
- distance to stop,
- market regime.

Ví dụ:

```text
position_size ∝ confidence / volatility
```

Mã volatility cao thì giảm size.

---

## 3. Counterparty/Risk Optimization

Counterparty risk trong tài chính tổ chức là rủi ro đối tác không thực hiện nghĩa vụ. Với nhà đầu tư cá nhân, tư duy này chuyển thành:

- rủi ro sàn/hệ thống,
- rủi ro margin,
- rủi ro thanh khoản,
- rủi ro broker/API/data,
- rủi ro một nhóm tài sản quá tập trung.

Bài học: không chỉ tối ưu return, phải tối ưu return sau khi trừ rủi ro vận hành và rủi ro hệ thống.

---

## 4. Volatility Modeling

### 4.1. Volatility là gì?

Volatility đo độ biến động. Trong trading, volatility quyết định:

- stop loss nên rộng bao nhiêu,
- target có thực tế không,
- position size,
- khả năng gap,
- xác suất bị quét stop.

### 4.2. Volatility clustering

Biến động thường tụ cụm: sau giai đoạn biến động mạnh, thị trường thường tiếp tục biến động mạnh.

Vì vậy không nên dùng stop cố định 6% cho mọi mã/mọi regime. Mã ATR 1.5% khác mã ATR 5%.

### 4.3. ATR-based stop

Một cách thực tế:

```text
stop = entry - k × ATR
```

hoặc với long:

```text
stop_pct = max(min_stop, k × ATR_pct)
```

Tùy strategy mà chọn `k`.

---

## 5. Áp dụng vào LH Investment

### 5.1. Thêm volatility regime

Mỗi mã nên có:

```json
{
  "atrPct": 3.2,
  "realizedVol20": 28.5,
  "volRegime": "high",
  "stopByATR": 6.4
}
```

### 5.2. Thêm portfolio warning

Khi web/model đề xuất nhiều mã, cảnh báo:

- quá nhiều cùng ngành,
- tương quan cao,
- volatility danh mục cao,
- quá nhiều mã thanh khoản thấp,
- nhiều mã cùng phụ thuộc VNINDEX.

### 5.3. Risk-adjusted ranking

Không chỉ score theo upside. Nên dùng:

```text
risk_adjusted_score = expected_return / expected_risk
```

hoặc:

```text
score = signal_score × confidence - risk_penalty
```

### 5.4. Checklist triển khai

- [ ] Tính ATR% cho mọi mã.
- [ ] Tính realized volatility 20/60 ngày.
- [ ] Tính correlation giữa các mã.
- [ ] Thêm sector cap.
- [ ] Thêm position size hint.
- [ ] Thêm risk warning trong output strategy.
- [ ] Backtest theo volatility regime.

---

## 6. Bài tập cho Hòa Đại ka

1. Anh muốn stop mặc định theo % hay theo ATR?
2. Mỗi ngành tối đa bao nhiêu % danh mục?
3. Khi market volatility cao, anh muốn giảm size bao nhiêu?

Nếu áp dụng ngay, Tiểu đệ đề xuất: **thêm `atrPct`, `volRegime`, `positionSizeHint`, `sectorRiskWarning` vào strategy cache**.
