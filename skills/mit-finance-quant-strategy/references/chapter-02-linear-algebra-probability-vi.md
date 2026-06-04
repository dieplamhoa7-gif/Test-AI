# Chương 2 — Linear Algebra, Probability và Stochastic Processes: nền móng cho model cổ phiếu

Nguồn video:

4. Lecture 2 — Linear Algebra  
   https://www.youtube.com/watch?v=0uimNNIuUyY
5. Lecture 4 — Linear Algebra (cont.); Probability Theory  
   https://www.youtube.com/watch?v=mtXTs2U1uMA
6. Lecture 5 — Probability Theory (cont.); Stochastic Processes I  
   https://www.youtube.com/watch?v=wMGEKMHsOKE
7. Lecture 6 — Stochastic Processes I (cont.); Regression Analysis  
   https://www.youtube.com/watch?v=yIn8Y_CSwPk

---

## 1. Tại sao chương này quan trọng?

Nếu Chương 1 nói “tài chính định lượng là gì”, thì Chương 2 là bộ công cụ toán đầu tiên để làm model thật.

Trong đầu tư cổ phiếu, ta luôn xử lý nhiều biến cùng lúc:

- giá,
- volume,
- RSI,
- MACD,
- MA,
- ADX,
- Bollinger,
- RS ngành,
- thị trường chung,
- tin tức,
- valuation,
- volatility.

Linear algebra giúp tổ chức các biến này thành vector/ma trận. Probability giúp hiểu bất định. Stochastic process giúp hiểu giá là chuỗi ngẫu nhiên có cấu trúc, không phải đường thẳng.

---

## 2. Linear Algebra — tư duy vector/ma trận

### 2.1. Tóm tắt dễ hiểu

Linear algebra là ngôn ngữ của dữ liệu nhiều chiều. Một cổ phiếu tại một ngày có thể xem như một vector feature:

```text
x_t = [return_5d, return_20d, RSI, MACD, volume_ratio, ATR, RS, distance_to_support, ...]
```

Một danh sách nhiều cổ phiếu nhiều ngày tạo thành ma trận:

```text
X = rows: quan sát, columns: features
```

Model machine learning, regression, PCA, portfolio optimization đều dựa trên cấu trúc này.

### 2.2. Khái niệm chính

**Vector**

Một danh sách số biểu diễn một điểm trong không gian nhiều chiều. Với cổ phiếu, vector có thể là bộ indicator của một mã tại một ngày.

**Matrix**

Bảng số. Ví dụ:

- ma trận return của 100 mã trong 500 ngày,
- ma trận feature của các tín hiệu,
- ma trận covariance giữa các cổ phiếu.

**Dot product**

Đo mức độ hai vector cùng hướng. Trong model tuyến tính:

```text
score = w · x
```

Trong đó:

- `x` là feature,
- `w` là trọng số,
- score là điểm tín hiệu.

**Eigenvalues / Eigenvectors**

Cốt lõi của PCA. Dùng để tìm các hướng biến động chính trong dữ liệu.

### 2.3. Áp dụng cho cổ phiếu

**1. Feature vector cho mỗi mã**

Mỗi mã nên có vector chuẩn:

```json
{
  "symbol": "MWG",
  "features": {
    "rs20": 0.72,
    "rsi14": 58,
    "macdHistSlope": 0.13,
    "volumeRatio20": 1.4,
    "atrPct": 2.8,
    "distSupportPct": 2.1,
    "patternScore": 64,
    "marketRegime": "neutral"
  }
}
```

**2. Tránh nhồi indicator trùng nhau**

RSI, Stochastic, Williams %R đều là momentum oscillator. Nếu đưa cả ba vào model mà không kiểm soát, model tưởng có nhiều bằng chứng nhưng thật ra chỉ là cùng một thông tin lặp lại.

Linear algebra/PCA giúp phát hiện feature trùng.

**3. Covariance/correlation cho danh mục**

Không nên mua 5 mã cùng ngành/cùng factor rồi tưởng là đa dạng hóa. Cần đo tương quan:

```text
corr(MWG, FRT), corr(SSI, VND), corr(HPG, NKG)
```

Nếu tương quan cao, risk danh mục thực tế cao hơn số lượng mã cho thấy.

---

## 3. Probability — xác suất là ngôn ngữ của trading

### 3.1. Tóm tắt dễ hiểu

Trong tài chính, không có gì chắc chắn. Một tín hiệu tốt chỉ làm tăng xác suất, không đảm bảo kết quả.

Do đó, mọi chiến lược nên được mô tả bằng phân phối kết quả:

- xác suất lời,
- xác suất lỗ,
- lời trung bình,
- lỗ trung bình,
- tail risk,
- số ngày giữ lệnh.

### 3.2. Khái niệm chính

**Random variable — biến ngẫu nhiên**

Return sau 10 phiên là một biến ngẫu nhiên:

```text
R_10 = (Price_{t+10} / Price_t) - 1
```

Ta không biết trước giá trị, nhưng có thể ước lượng phân phối từ quá khứ.

**Expected value — kỳ vọng**

```text
EV = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

Một chiến lược không cần win rate quá cao nếu payoff tốt.

**Variance / volatility — độ phân tán**

Hai chiến lược cùng EV nhưng biến động khác nhau thì trải nghiệm/rủi ro khác nhau.

**Conditional probability — xác suất có điều kiện**

Quan trọng nhất cho trading:

```text
P(tăng 5% trong 20 ngày | giá gần hỗ trợ + volume tăng + thị trường tốt)
```

Không nên hỏi “cổ phiếu này có tăng không?”, mà hỏi “trong điều kiện này, xác suất tăng là bao nhiêu?”.

### 3.3. Áp dụng cho hệ thống của anh

Mỗi setup nên có thống kê xác suất riêng:

```json
{
  "setup": "support_rebound",
  "horizon": 20,
  "precision": 0.63,
  "avgWin": 0.082,
  "avgLoss": -0.041,
  "expectancy": 0.036,
  "sampleSize": 142,
  "maxDrawdownAfterEntry": -0.078
}
```

Như vậy web không chỉ nói “WATCH”, mà nói:

> Setup này trong quá khứ có precision 63%, lời trung bình 8.2%, lỗ trung bình 4.1%, expectancy 3.6% sau 20 phiên.

---

## 4. Stochastic Processes — giá là quá trình ngẫu nhiên theo thời gian

### 4.1. Tóm tắt dễ hiểu

Stochastic process là chuỗi biến ngẫu nhiên theo thời gian. Giá cổ phiếu là ví dụ điển hình:

```text
P_1, P_2, P_3, ..., P_t
```

Mỗi ngày giá thay đổi vì nhiều yếu tố: tin tức, dòng tiền, tâm lý, vĩ mô, cung cầu, noise.

Điểm quan trọng: dữ liệu tài chính không độc lập đơn giản. Nó có:

- trend,
- mean reversion,
- volatility clustering,
- regime change,
- fat tails,
- autocorrelation ở một số horizon.

### 4.2. Khái niệm chính

**Random walk**

Mô hình đơn giản: giá ngày mai bằng giá hôm nay cộng một cú sốc ngẫu nhiên.

```text
P_{t+1} = P_t + ε_t
```

Thực tế thị trường không hoàn toàn random walk, nhưng random walk là baseline để tránh ảo tưởng dự báo.

**Markov process**

Tương lai phụ thuộc vào trạng thái hiện tại, không cần nhớ toàn bộ quá khứ.

Trong trading có thể dùng trạng thái:

- trend up,
- trend down,
- sideway,
- high volatility,
- low liquidity,
- accumulation,
- distribution.

**Regime**

Thị trường thay đổi chế độ. Một indicator tốt ở uptrend có thể tệ trong sideway.

### 4.3. Áp dụng cho chiến lược

**1. Thêm regime filter**

Mỗi tín hiệu nên được backtest theo regime:

- VNINDEX uptrend,
- VNINDEX downtrend,
- VNINDEX sideway,
- volatility cao/thấp,
- thanh khoản cao/thấp.

**2. Không shuffle dữ liệu thời gian**

Khi train/test model cổ phiếu, không được random split như dữ liệu ảnh. Phải split theo thời gian:

```text
Train: 2022-2024
Validation: 2025H1
Test/OOS: 2025H2-2026
```

**3. Dùng walk-forward**

Model nên được kiểm tra theo từng cửa sổ thời gian để xem có ổn định không.

---

## 5. Bài học cho pipeline LH Investment

### 5.1. Feature matrix chuẩn

Nên tạo một bảng nghiên cứu dạng:

```text
symbol | date | future_return_20d | setup | rs20 | rsi14 | macd | atr | volume_ratio | pattern_score | market_regime | sector
```

Đây là nền cho:

- regression,
- machine learning,
- kiểm định indicator,
- ranking cổ phiếu,
- chọn feature.

### 5.2. Expected value là chỉ tiêu trung tâm

Mọi chiến lược nên có:

```text
EV = hit_rate × avg_win - (1 - hit_rate) × avg_loss - cost
```

Nếu chỉ dùng win rate thì dễ sai.

### 5.3. Correlation risk cho danh mục

Khi web đề xuất danh mục, nên cảnh báo:

- quá nhiều ngân hàng,
- quá nhiều chứng khoán,
- quá nhiều bất động sản,
- các mã tương quan cao.

### 5.4. Regime-aware strategy

Một strategy tốt phải biết khi nào không nên đánh.

Ví dụ:

```text
Nếu marketRegime = bearish và volatility high:
  - chỉ cho BUY khi setup cực mạnh
  - giảm position size
  - tăng yêu cầu volume/RS
  - stop chặt hơn
```

---

## 6. Checklist triển khai sau chương 2

- [ ] Tạo `research_feature_matrix.parquet/json` cho VN100.
- [ ] Chuẩn hóa feature vector cho mỗi mã/ngày.
- [ ] Tính correlation giữa các indicator để loại feature trùng.
- [ ] Tính correlation giữa cổ phiếu để cảnh báo danh mục.
- [ ] Mọi backtest báo thêm EV/expectancy.
- [ ] Backtest theo market regime.
- [ ] Không random split dữ liệu time series.
- [ ] Thêm `marketRegime` vào `strategy_results_cache.json`.

---

## 7. Bài tập cho Hòa Đại ka

1. Với mỗi chiến lược, anh muốn tối ưu theo chỉ tiêu nào?
   - precision,
   - expectancy,
   - max drawdown,
   - profit factor,
   - số lệnh đủ nhiều?

2. Anh muốn model ưu tiên:
   - ít lệnh nhưng chắc,
   - nhiều lệnh hơn nhưng phải lọc bằng position size,
   - hay tách riêng short-term/medium-term?

3. Với danh mục, anh muốn giới hạn tối đa mỗi ngành bao nhiêu phần trăm?

Trả lời được 3 câu này thì từ chương 2 có thể chuyển ngay sang thiết kế feature matrix và backtest chuẩn hơn.
