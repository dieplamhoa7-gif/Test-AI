# Hướng dẫn học MIT 18.642 bằng tiếng Việt cho Hòa Đại ka


---

Mục tiêu: biến kiến thức toán tài chính thành quy tắc cụ thể cho model, backtest, quản trị rủi ro và danh mục LH Investment.


---

# Chương 1 — MIT 18.642 Lecture 1: Tài chính định lượng bắt đầu từ đâu?

Nguồn video:

1. Lecture 1, Part I — Introduction of the Class  
   https://www.youtube.com/watch?v=b8u2CQLQBVU
2. Lecture 1, Part II — Introduction of Financial Markets, Financial Terms and Concepts  
   https://www.youtube.com/watch?v=z4p87TPCnQc
3. Lecture 1, Part III — Bond "Mathematics"  
   https://www.youtube.com/watch?v=NZ3Mva95UsQ

Ghi chú cho Hòa Đại ka: Chương này là bài nhập môn. Giá trị chính không nằm ở công thức phức tạp, mà ở cách MIT đặt vấn đề: **toán tài chính không phải để dự đoán chắc chắn, mà để mô hình hóa rủi ro, dòng tiền, xác suất và quyết định đầu tư trong điều kiện bất định.**

---

## 1. Lecture 1 Part I — Môn học này dạy điều gì?

### 1.1. Tóm tắt dễ hiểu

Lecture 1 Part I giới thiệu mục tiêu của môn học: dùng toán học để giải quyết các bài toán tài chính thực tế. Môn học không chỉ là lý thuyết toán, cũng không chỉ là kể chuyện thị trường. Nó nằm ở giao điểm:

- toán ứng dụng,
- dữ liệu,
- xác suất,
- mô hình định lượng,
- kinh nghiệm thực tế từ ngành tài chính.

Giảng viên nhấn mạnh lớp học sẽ có hai phần:

1. **Phần toán học nền tảng** — linear algebra, probability, stochastic processes, regression, time series, optimization...
2. **Phần ứng dụng tài chính thực tế** — bond, rates, portfolio, volatility, Black-Scholes, machine learning, risk management...

Ý quan trọng: tài chính là nơi toán học gặp dữ liệu nhiễu, con người, thị trường và rủi ro thật. Vì vậy không được học toán kiểu “công thức đẹp là xong”. Phải hỏi: công thức đó dùng để ra quyết định gì, rủi ro gì, sai ở đâu, kiểm định thế nào.

### 1.2. Bài học chính

**Bài học 1 — Toán trong tài chính là công cụ ra quyết định, không phải máy tiên tri.**

Trong đầu tư cổ phiếu, nhiều người muốn một mô hình cho câu trả lời tuyệt đối: “mai tăng hay giảm?”. Cách tiếp cận định lượng đúng hơn là:

- xác suất tăng là bao nhiêu,
- nếu đúng thì lời bao nhiêu,
- nếu sai thì lỗ bao nhiêu,
- tín hiệu có lặp lại trong quá khứ không,
- trong regime nào tín hiệu hỏng,
- danh mục chịu rủi ro tổng thể ra sao.

**Bài học 2 — Tài chính định lượng phải nối được từ lý thuyết sang pipeline.**

Một ý tưởng chỉ đáng dùng khi biến thành dữ liệu/feature/rule/backtest được. Ví dụ:

- “cổ phiếu khỏe” → phải định nghĩa bằng RS, trend, volume, volatility, drawdown.
- “rủi ro cao” → phải đo bằng ATR, gap risk, support distance, liquidity, concentration.
- “mẫu hình đẹp” → phải đo bằng pattern score, số lần chạm, recency, target/stop, xác suất sau backtest.

**Bài học 3 — Người làm model phải biết thị trường thật.**

Nếu chỉ nhìn công thức mà không hiểu spread, thanh khoản, phí, slippage, lô giao dịch, T+ settlement, quy định thị trường, thì backtest rất dễ đẹp giả.

### 1.3. Áp dụng cho hệ thống cổ phiếu của anh

Với web/model LH Investment, chương này gợi ý một nguyên tắc thiết kế:

> Mọi module phải trả lời được 3 câu: tín hiệu là gì, rủi ro là gì, và kiểm định ra sao.

Nên phân lớp pipeline như sau:

1. **Data layer**
   - OHLCV,
   - dữ liệu tài chính,
   - tin tức,
   - ngành,
   - thị trường chung.

2. **Feature layer**
   - indicator,
   - support/resistance,
   - chart pattern,
   - volatility,
   - relative strength,
   - liquidity.

3. **Signal layer**
   - trend pullback,
   - support rebound,
   - breakout,
   - shakeout,
   - bottom reversal.

4. **Risk layer**
   - stop,
   - invalidation,
   - max loss,
   - volatility-adjusted size,
   - sector concentration.

5. **Validation layer**
   - walk-forward backtest,
   - out-of-sample,
   - precision,
   - expectancy,
   - drawdown,
   - số mẫu.

6. **Explanation layer**
   - vì sao mã này được chọn,
   - vì sao mã này bị loại,
   - điều kiện nào làm thesis sai.

### 1.4. Việc nên làm trong pipeline

- Chuẩn hóa mọi chiến lược thành JSON có cùng schema:
  - `signalName`
  - `entryCondition`
  - `riskCondition`
  - `stopLoss`
  - `target`
  - `confidence`
  - `evidence`
  - `backtestStats`

- Không để web chỉ hiện “BUY/WATCH”. Nên hiện thêm:
  - “Vì sao?”
  - “Sai khi nào?”
  - “Rủi ro tối đa?”
  - “Tín hiệu này trong quá khứ thắng bao nhiêu?”

---

## 2. Lecture 1 Part II — Các khái niệm thị trường tài chính

### 2.1. Tóm tắt dễ hiểu

Phần này giới thiệu các khái niệm nền của thị trường tài chính: tài sản, cổ phiếu, trái phiếu, phái sinh, lãi suất, lợi suất, rủi ro, kỳ hạn, giao dịch, định giá. Đây là “ngôn ngữ chung” trước khi bước vào công thức.

Điểm đáng chú ý là tài chính không chỉ có cổ phiếu. Một hệ thống đầu tư tốt phải hiểu các lớp tài sản liên kết với nhau:

- cổ phiếu phản ánh kỳ vọng tăng trưởng/lợi nhuận,
- trái phiếu phản ánh lãi suất và rủi ro tín dụng,
- phái sinh phản ánh kỳ vọng, volatility và bảo hiểm rủi ro,
- tiền mặt/lãi suất là baseline cho mọi định giá.

### 2.2. Các khái niệm cần nhớ

**Asset — tài sản tài chính**

Là thứ có giá trị và có thể giao dịch hoặc định giá: cổ phiếu, trái phiếu, chứng quyền, option, futures, tiền gửi, quỹ ETF...

**Return — lợi suất**

Không chỉ là giá tăng bao nhiêu, mà là phần trăm sinh lời so với vốn bỏ ra. Với chiến lược cổ phiếu, nên đo:

- return sau 5/10/20/60 phiên,
- max drawdown sau entry,
- time-to-target,
- hit rate,
- expectancy.

**Risk — rủi ro**

Không chỉ là “giảm giá”. Rủi ro gồm:

- volatility,
- drawdown,
- thanh khoản,
- gap,
- tin xấu,
- rủi ro ngành,
- rủi ro thị trường chung,
- rủi ro model sai.

**Interest rate — lãi suất**

Lãi suất là trọng lực của tài chính. Khi lãi suất tăng, định giá cổ phiếu tăng trưởng thường bị ép vì dòng tiền tương lai bị chiết khấu mạnh hơn.

**Derivative — phái sinh/chứng quyền**

Giá trị phụ thuộc vào tài sản cơ sở. Với chứng quyền, không thể chỉ nhìn cổ phiếu cơ sở tăng/giảm; còn phải nhìn:

- thời gian còn lại,
- giá thực hiện,
- volatility,
- thanh khoản,
- spread,
- time decay.

### 2.3. Bài học cho Hòa Đại ka

**Bài học 1 — Cổ phiếu không sống một mình.**

Khi model chọn cổ phiếu, nên có market context:

- VN-Index đang trend hay sideway,
- lãi suất/tỷ giá có căng không,
- nhóm ngành đang hút tiền hay bị rút tiền,
- thanh khoản thị trường có đủ không.

Nếu một mã có setup đẹp nhưng thị trường chung xấu, position size nên giảm.

**Bài học 2 — Mọi tín hiệu nên đi kèm horizon.**

Một tín hiệu có thể đúng cho 5 phiên nhưng sai cho 60 phiên. Vì vậy trong cache nên ghi rõ:

- tín hiệu ngắn hạn,
- trung hạn,
- dài hạn,
- horizon backtest.

**Bài học 3 — Với chứng quyền, phải có module riêng.**

Không nên dùng logic cổ phiếu thường cho CW. CW cần thêm:

- moneyness,
- days to maturity,
- implied/realized volatility,
- break-even,
- leverage hiệu dụng,
- liquidity/spread.

### 2.4. Việc nên làm trong pipeline

- Thêm `marketRegime` vào mọi output chiến lược:
  - `bullish_market`, `bearish_market`, `sideway`, `high_volatility`, `low_liquidity`.

- Thêm `horizon` cho tín hiệu:
  - `swing_5_10d`, `position_20_60d`, `longer_term`.

- Với CW, không xếp hạng theo upside đơn giản. Cần score:
  - upside theo underlying,
  - time decay penalty,
  - spread penalty,
  - liquidity penalty,
  - break-even distance.

---

## 3. Lecture 1 Part III — Bond Mathematics

### 3.1. Tóm tắt dễ hiểu

Phần này nói về toán trái phiếu: giá trị hiện tại, coupon, yield, duration, convexity. Nghe có vẻ xa cổ phiếu, nhưng thực ra rất quan trọng vì nó dạy cách định giá tài sản bằng dòng tiền và lãi suất chiết khấu.

Trái phiếu là ví dụ sạch nhất của tài chính định lượng:

- có dòng tiền tương đối rõ,
- có thời điểm nhận tiền,
- có lãi suất chiết khấu,
- có độ nhạy với lãi suất.

Từ trái phiếu, ta học được cách tư duy về cổ phiếu: giá hôm nay là kỳ vọng về dòng tiền tương lai, chiết khấu về hiện tại, cộng thêm rủi ro và tâm lý thị trường.

### 3.2. Công thức/khái niệm chính

**Present Value — giá trị hiện tại**

Một dòng tiền tương lai `CF_t` có giá trị hiện tại:

```text
PV = CF_t / (1 + r)^t
```

Nếu có nhiều dòng tiền:

```text
Price = Σ CF_t / (1 + r)^t
```

Ý nghĩa: tiền nhận càng xa trong tương lai thì càng bị chiết khấu mạnh.

**Bond price — giá trái phiếu**

Giá trái phiếu bằng tổng giá trị hiện tại của coupon và principal:

```text
Bond Price = Σ Coupon_t / (1+y)^t + Face Value / (1+y)^T
```

Trong đó `y` là yield/lợi suất yêu cầu.

**Yield tăng thì giá trái phiếu giảm**

Đây là quan hệ ngược chiều:

- lãi suất/yield tăng → dòng tiền tương lai bị chiết khấu mạnh hơn → giá giảm.
- lãi suất/yield giảm → giá tăng.

**Duration — độ nhạy giá với lãi suất**

Duration đo giá trái phiếu nhạy thế nào với thay đổi lãi suất. Duration càng cao, giá càng nhạy.

Xấp xỉ:

```text
%ΔPrice ≈ -Duration × ΔYield
```

**Convexity — độ cong**

Duration là xấp xỉ tuyến tính. Convexity sửa sai khi thay đổi lãi suất lớn hơn.

### 3.3. Liên hệ với cổ phiếu

Dù cổ phiếu không có coupon cố định, logic chiết khấu vẫn áp dụng:

```text
Giá cổ phiếu ≈ PV của dòng tiền/lợi nhuận tương lai
```

Khi lãi suất tăng:

- cổ phiếu tăng trưởng xa tương lai bị ảnh hưởng mạnh,
- P/E thị trường thường bị nén,
- dòng tiền chuyển sang tài sản an toàn hơn,
- margin/risk appetite giảm.

Khi lãi suất giảm:

- định giá cổ phiếu dễ mở rộng,
- nhóm growth/đầu cơ thường nhạy hơn,
- liquidity/risk appetite cải thiện.

### 3.4. Bài học cho Hòa Đại ka

**Bài học 1 — Lãi suất là biến nền của model.**

Nếu chỉ dùng OHLCV mà bỏ qua lãi suất/tỷ giá/thanh khoản, model có thể sai regime. Một setup breakout trong môi trường tiền rẻ khác với breakout trong môi trường lãi suất căng.

**Bài học 2 — Duration có phiên bản cổ phiếu.**

Cổ phiếu tăng trưởng cao, lợi nhuận kỳ vọng nằm xa tương lai giống “duration dài”. Nó nhạy với lãi suất và kỳ vọng hơn cổ phiếu value/cashflow ổn định.

Có thể tạo feature:

```text
equity_duration_proxy = valuation_sensitivity + growth_expectation + profit_distance
```

Thực tế đơn giản hơn:

- P/E cao,
- P/B cao,
- lợi nhuận hiện tại thấp nhưng kỳ vọng tương lai cao,
- dòng tiền âm,

→ nhạy với lãi suất hơn.

**Bài học 3 — Target/stop cũng là bài toán kỳ vọng.**

Một trade tốt không phải target xa nhất, mà là trade có:

```text
Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

Bond math dạy ta quy đổi dòng tiền/rủi ro về hiện tại; trading cũng cần quy đổi xác suất lời/lỗ thành expectancy.

### 3.5. Việc nên làm trong pipeline

**1. Thêm macro-rate context**

Trong `market_overview` hoặc macro cache nên có:

- lãi suất điều hành,
- lợi suất trái phiếu nếu có,
- tỷ giá,
- tín dụng/thanh khoản,
- VNINDEX volatility.

**2. Thêm valuation sensitivity**

Với các mã có dữ liệu cơ bản:

- P/E,
- P/B,
- ROE,
- tăng trưởng doanh thu/lợi nhuận,
- nợ vay,
- dòng tiền.

Tạo score:

```text
rate_sensitive_score
```

để biết mã nào dễ bị ảnh hưởng khi lãi suất đổi.

**3. Dùng expectancy thay vì chỉ hit rate**

Một chiến lược win rate 45% vẫn tốt nếu lời/lỗ trung bình đủ tốt. Ngược lại win rate 70% vẫn tệ nếu lỗ một lần xóa hết nhiều lần lời.

Nên mọi backtest có:

- win rate,
- avg win,
- avg loss,
- expectancy,
- max drawdown,
- profit factor,
- số lệnh.

---

## 4. Tóm tắt chương 1 cho hệ thống LH Investment

### 4.1. Những ý nên đưa vào model

1. **Market regime**
   - Thị trường chung phải là điều kiện nền cho mọi chiến lược.

2. **Horizon rõ ràng**
   - Tín hiệu 5 phiên khác tín hiệu 60 phiên.

3. **Risk-adjusted signal**
   - Không chỉ “mã này tăng được”, mà “tăng được bao nhiêu so với rủi ro?”.

4. **Expected value**
   - Xếp hạng chiến lược theo expectancy, không chỉ win rate.

5. **Macro/rate context**
   - Lãi suất/tỷ giá/liquidity ảnh hưởng valuation và risk appetite.

6. **Derivative/CW riêng**
   - Chứng quyền cần model khác cổ phiếu cơ sở.

### 4.2. Checklist nâng cấp pipeline

- [ ] Mỗi strategy output có `horizon`.
- [ ] Mỗi strategy output có `expectedValue`.
- [ ] Backtest thêm `avgWin`, `avgLoss`, `profitFactor`.
- [ ] Market cache có `marketRegime`.
- [ ] Macro cache có lãi suất/tỷ giá/liquidity nếu lấy được.
- [ ] CW ranking có time decay + spread + liquidity penalty.
- [ ] Web popup hiển thị “sai khi nào?” cho mỗi setup.

### 4.3. Bài tập cho Hòa Đại ka

Nếu anh muốn học theo kiểu áp dụng ngay, sau chương này anh chỉ cần trả lời 3 câu:

1. Anh muốn mỗi tín hiệu tối ưu cho horizon nào?
   - 5 phiên,
   - 10 phiên,
   - 20 phiên,
   - 60 phiên?

2. Anh ưu tiên gì hơn?
   - Win rate cao,
   - lời/lỗ tốt,
   - drawdown thấp,
   - ít lệnh nhưng chắc,
   - nhiều cơ hội hơn?

3. Khi thị trường chung xấu, anh muốn model:
   - dừng hẳn,
   - giảm tỷ trọng,
   - chỉ chọn mã mạnh nhất,
   - hay vẫn chạy bình thường?

Trả lời 3 câu này sẽ quyết định toàn bộ thiết kế chiến lược sau này.


---

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


---

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


---

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


---

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


---

# Chương 6 — Machine Learning, Stochastic Calculus và lộ trình áp dụng

Nguồn video:

- Lecture 23 — Introduction to Machine Learning
- Lecture 24 — Stochastic Calculus
- Lecture 25 — Stochastic Calculus (cont.); Stochastic Differential Equations
- Các lecture stochastic/probability trước đó

---

## 1. Machine Learning trong tài chính: dùng được, nhưng phải rất kỷ luật

ML trong tài chính hấp dẫn vì có thể học quan hệ phi tuyến giữa nhiều feature. Nhưng nó cũng rất dễ overfit.

Trong cổ phiếu, dữ liệu có:

- noise cao,
- regime change,
- sample size không lớn,
- feature leakage,
- survivorship bias,
- transaction cost,
- slippage.

Vì vậy ML chỉ nên là lớp hỗ trợ ranking/probability, không nên là hộp đen tự phán BUY/SELL mà không giải thích.

---

## 2. ML workflow đúng cho LH Investment

### 2.1. Label rõ ràng

Ví dụ:

```text
label = 1 nếu future_return_20d >= 6% và max_drawdown_20d >= -6%
label = 0 nếu không đạt
```

Label phải phản ánh cách trade thật.

### 2.2. Feature sạch

Feature chỉ dùng dữ liệu có tại thời điểm entry:

- indicator hiện tại,
- trend hiện tại,
- support/resistance tính đến hiện tại,
- market regime hiện tại,
- volume/liquidity hiện tại.

### 2.3. Split theo thời gian

Không random split. Dùng:

```text
train -> validation -> test OOS
```

hoặc walk-forward.

### 2.4. Baseline trước

Trước khi dùng ML, phải có baseline:

- rule-based strategy,
- logistic regression,
- simple ranking score.

ML chỉ đáng dùng nếu vượt baseline OOS.

---

## 3. Stochastic Calculus — phần nâng cao dùng để hiểu option/risk

Stochastic calculus là toán cho quá trình ngẫu nhiên liên tục, như Brownian motion, Ito calculus, SDE.

Với hệ thống cổ phiếu thường, không cần đưa trực tiếp Ito formula vào pipeline mỗi ngày. Nhưng hiểu nó giúp anh hiểu:

- vì sao option pricing cần volatility,
- vì sao giá là quá trình ngẫu nhiên,
- vì sao hedging không hoàn hảo,
- vì sao risk phải mô hình hóa động theo thời gian.

Ứng dụng trực tiếp hơn nằm ở:

- Black-Scholes/CW,
- volatility modeling,
- scenario simulation,
- risk stress test.

---

## 4. Roadmap áp dụng toàn bộ MIT 18.642 vào LH Investment

### Giai đoạn 1 — Chuẩn hóa dữ liệu và backtest

- Tạo feature matrix VN100.
- Tạo labels future return 5/10/20/60 ngày.
- Tính expected value cho từng setup.
- Backtest theo market regime.

### Giai đoạn 2 — Giảm nhiễu feature

- Correlation matrix cho indicator.
- PCA/factor grouping.
- Loại indicator trùng.
- Chọn feature đại diện theo nhóm.

### Giai đoạn 3 — Risk/portfolio

- ATR/volatility regime.
- Position sizing theo volatility/confidence.
- Sector cap.
- Correlation warning.

### Giai đoạn 4 — CW/derivative module

- Break-even.
- Moneyness.
- Time decay.
- Spread/liquidity.
- Underlying signal integration.

### Giai đoạn 5 — ML ranking

- Logistic regression / gradient boosting nhẹ.
- Probability calibration.
- OOS walk-forward.
- Explainability.

---

## 5. Checklist cuối cùng cho chiến lược chuẩn định lượng

Một chiến lược đáng đưa lên web nên có:

- [ ] điều kiện entry rõ,
- [ ] điều kiện exit rõ,
- [ ] stop/invalidation,
- [ ] horizon,
- [ ] sample size,
- [ ] precision,
- [ ] expected value,
- [ ] avg win/loss,
- [ ] max drawdown,
- [ ] market regime breakdown,
- [ ] position size hint,
- [ ] explanation: vì sao đúng,
- [ ] wrong-if: khi nào sai.

---

## 6. Bài tập cho Hòa Đại ka

Nếu anh muốn biến khóa MIT này thành việc thật, thứ tự nên làm là:

1. Build feature matrix VN100.
2. Backtest lại 3 chiến lược hiện có bằng EV + regime.
3. Lọc indicator trùng bằng correlation/PCA.
4. Thêm risk-adjusted ranking.
5. Sau đó mới ML.

Đừng nhảy ngay vào ML nếu feature/rule/backtest chưa sạch. ML chỉ phóng đại chất lượng dữ liệu: dữ liệu sạch thì tốt hơn, dữ liệu bẩn thì sai tinh vi hơn.
