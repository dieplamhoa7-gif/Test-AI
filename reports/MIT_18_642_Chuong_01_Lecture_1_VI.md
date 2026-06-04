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
