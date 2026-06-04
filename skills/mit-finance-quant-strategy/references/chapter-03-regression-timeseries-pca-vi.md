# Chương 3 — Regression, Time Series và PCA: kiểm định tín hiệu cổ phiếu

Nguồn video:

- Lecture 6 — Stochastic Processes I (cont.); Regression Analysis
- Lecture 8 — Regression Analysis (cont.)
- Lecture 11 — Regression Analysis (cont.)
- Lecture 12 — Time Series Analysis
- Lecture 9 — Principal Component Analysis in Finance

---

## 1. Vì sao chương này sát với model cổ phiếu của anh?

Đây là chương quan trọng nhất nếu mục tiêu là nâng cấp chiến lược LH Investment. Hầu hết câu hỏi thực tế của anh đều rơi vào nhóm này:

- Indicator nào thật sự có tác dụng?
- Mẫu hình nào không bị ảo?
- Feature nào trùng nhau?
- Tín hiệu có còn hiệu quả ngoài mẫu không?
- Model có overfit không?
- Có nên dùng ML hay chỉ cần rule/regression?

Regression, time series và PCA giúp trả lời bằng dữ liệu thay vì cảm tính.

---

## 2. Regression — kiểm định feature có giải thích future return không

### 2.1. Ý tưởng đơn giản

Regression tìm quan hệ giữa biến đầu vào và kết quả tương lai.

Ví dụ:

```text
future_return_20d = a + b1*RS20 + b2*RSI + b3*volume_ratio + b4*dist_support + error
```

Nếu `b1` dương ổn định và OOS tốt, relative strength có thể là feature đáng dùng. Nếu coefficient đổi dấu liên tục, feature đó không ổn.

### 2.2. Dùng regression đúng cách

Không dùng regression để “vẽ đường đẹp” trên quá khứ. Dùng để kiểm tra:

- feature có dấu hợp lý không,
- feature có ổn định qua thời gian không,
- feature có giúp hơn baseline không,
- feature có bị trùng với feature khác không.

### 2.3. Lỗi hay gặp

**1. Look-ahead bias**

Dùng dữ liệu tương lai để tạo feature tại hiện tại. Ví dụ: support/resistance tính bằng cả dữ liệu sau ngày entry.

**2. Random split time series**

Không được shuffle ngày rồi train/test. Phải split theo thời gian.

**3. Multicollinearity**

Nhiều indicator giống nhau làm model tưởng có nhiều bằng chứng. RSI, Stochastic, Williams %R có thể cùng kể một câu chuyện.

**4. Overfit**

Quá nhiều điều kiện để fit quá khứ, nhưng ra tương lai hỏng.

---

## 3. Time Series — dữ liệu tài chính là chuỗi thời gian, không phải bảng tĩnh

### 3.1. Khái niệm chính

Dữ liệu giá có thứ tự thời gian. Điều này tạo ra các vấn đề:

- autocorrelation,
- regime change,
- volatility clustering,
- non-stationarity,
- trend/seasonality.

### 3.2. Stationarity

Một chuỗi stationarity có phân phối tương đối ổn định theo thời gian. Giá cổ phiếu thường không stationarity, nhưng return có thể gần hơn.

Vì vậy model nên dùng:

- return,
- log return,
- normalized indicator,
- z-score,
- percentile,

hơn là giá tuyệt đối.

### 3.3. Walk-forward validation

Cách kiểm định đúng hơn:

```text
Train 2022-2023 → Test 2024Q1
Train 2022-2024Q1 → Test 2024Q2
Train 2022-2024Q2 → Test 2024Q3
...
```

Nếu strategy ổn qua nhiều cửa sổ thì đáng tin hơn.

---

## 4. PCA — giảm nhiễu và loại indicator trùng

### 4.1. PCA là gì?

PCA tìm các hướng biến động chính trong dữ liệu. Trong tài chính, PCA thường dùng để:

- tìm factor thị trường,
- tìm factor ngành,
- giảm số chiều feature,
- loại thông tin trùng lặp.

### 4.2. Dùng PCA cho indicator

Nếu anh có 40 indicator, nhiều indicator sẽ trùng. PCA hoặc correlation clustering giúp gom thành nhóm:

- trend factor,
- momentum factor,
- volatility factor,
- volume/money flow factor,
- support/resistance factor,
- market regime factor.

Thay vì cho model 40 biến hỗn loạn, ta cho 5–8 factor rõ nghĩa.

### 4.3. Dùng PCA cho danh mục

PCA trên return của cổ phiếu giúp biết danh mục bị kéo bởi factor nào:

- factor thị trường chung,
- factor ngân hàng,
- factor chứng khoán,
- factor bất động sản,
- factor hàng hóa/thép/dầu khí.

Nếu danh mục có 10 mã nhưng 80% risk đến từ một factor, thật ra chưa đa dạng hóa.

---

## 5. Áp dụng vào LH Investment

### 5.1. Tạo research feature matrix

Nên có file nghiên cứu:

```text
symbol,date,future_return_5d,future_return_20d,setup,rs20,rsi14,macd_hist,volume_ratio,atr_pct,dist_support,pattern_score,market_regime,sector
```

Từ bảng này có thể:

- regression,
- feature importance,
- PCA,
- backtest,
- ML.

### 5.2. Regression test cho từng feature

Mỗi feature nên được kiểm:

- correlation với future return,
- coefficient trong regression,
- ổn định qua các năm,
- tác dụng trong từng regime.

### 5.3. PCA/correlation để lọc 40 indicator

Không nên chọn 40 indicator bằng cảm giác. Nên:

1. tính correlation giữa indicators,
2. gom nhóm indicator trùng,
3. chọn đại diện mỗi nhóm,
4. backtest nhóm đại diện,
5. chỉ giữ feature tăng EV/OOS.

### 5.4. Checklist triển khai

- [ ] Tạo `research_feature_matrix` cho VN100.
- [ ] Thêm labels future return 5/10/20/60 ngày.
- [ ] Tách train/test theo thời gian.
- [ ] Tính correlation giữa features.
- [ ] Tạo regression report cho từng setup.
- [ ] Tạo PCA/factor grouping cho indicator.
- [ ] So sánh strategy với baseline buy & hold hoặc market filter đơn giản.

---

## 6. Bài tập cho Hòa Đại ka

1. Chọn 1 horizon chính cho model đầu tiên: 10 ngày hay 20 ngày?
2. Chọn metric chính: precision hay expectancy?
3. Chọn nhóm feature cốt lõi: trend, momentum, volume, support/resistance, pattern, market regime.

Nếu chỉ được làm một việc sau chương này, Tiểu đệ đề xuất: **xây feature matrix VN100 + future_return_20d rồi regression/PCA để loại indicator trùng**.
