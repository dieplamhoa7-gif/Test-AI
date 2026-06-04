# MIT 18.642 — 22 video, 44 trang giảng dạy


## Video 01 — Lecture 1, Part I: Introduction of the Class
### Trang 1
Video mở đầu giới thiệu mục tiêu của môn: dùng toán học để hiểu và giải quyết vấn đề tài chính thực tế. Đây là khóa học nối giữa nền tảng toán và ứng dụng trên thị trường tài chính.
Các mảng toán xuất hiện xuyên suốt gồm đại số tuyến tính, xác suất, thống kê, quá trình ngẫu nhiên, hồi quy, chuỗi thời gian, PCA, tối ưu hóa, mô hình biến động, định giá phái sinh và machine learning.
Điểm quan trọng là mô hình không phải sự thật tuyệt đối. Mô hình là bản đồ rút gọn, giúp ta ra quyết định trong điều kiện thiếu chắc chắn.

### Công thức
```

```
### Trang 2
Với nhà đầu tư, bài này đặt nền cho tư duy: không hỏi “chắc tăng không”, mà hỏi xác suất, payoff, rủi ro, điều kiện sai và cách kiểm định.
Một hệ thống tài chính tốt phải nói rõ giả định. Nếu giả định sai, kết luận cũng có thể sai.
Bài học cần nhớ: tài chính định lượng là kỷ luật biến dữ liệu thành quyết định có kiểm chứng, không phải trang trí bằng công thức.

## Video 02 — Lecture 1, Part II: Introduction of Financial Markets, Financial Terms and Concepts
### Trang 1
Video giới thiệu các loại tài sản và khái niệm tài chính: equity, fixed income, derivatives, alternatives, risk, return, liquidity, market participants.
Cổ phiếu là quyền sở hữu doanh nghiệp, trái phiếu là công cụ nợ, phái sinh là hợp đồng có giá trị phụ thuộc tài sản cơ sở. Mỗi loại có nguồn lợi nhuận và rủi ro khác nhau.
Thị trường tài chính không chỉ có giá. Nó có thanh khoản, chi phí giao dịch, spread, margin, leverage và ràng buộc pháp lý.

### Công thức
```

```
### Trang 2
Nhà đầu tư phải hiểu sản phẩm trước khi dùng. Một cổ phiếu, trái phiếu và chứng quyền không thể phân tích bằng cùng một khung đơn giản.
Return luôn phải đi cùng risk. Lợi nhuận cao hơn thường đi cùng biến động, mất thanh khoản, đòn bẩy hoặc rủi ro sự kiện.
Bài học cần nhớ: trước khi định giá hoặc trading, phải biết mình đang sở hữu loại payoff nào và rủi ro nằm ở đâu.

## Video 03 — Lecture 1, Part III: Bond “Mathematics”
### Trang 1
Video giảng về chiết khấu dòng tiền, lãi suất, yield và định giá trái phiếu. Một dòng tiền tương lai có giá trị hiện tại thấp hơn vì tiền có giá trị thời gian.
Công thức nền: PV = CF/(1+r)^t. Giá trái phiếu là tổng present value của coupon và mệnh giá đáo hạn.
Khi yield tăng, giá trái phiếu giảm. Khi yield giảm, giá trái phiếu tăng. Đây là quan hệ ngược chiều nền tảng.

### Công thức
```

```
### Trang 2
Duration đo độ nhạy của giá trái phiếu với thay đổi yield: %ΔPrice ≈ -Duration × ΔYield. Convexity sửa sai số khi biến động yield lớn.
Dù học về trái phiếu, tư duy chiết khấu áp dụng cho mọi tài sản có dòng tiền, kể cả cổ phiếu. Cổ phiếu tăng trưởng xa tương lai nhạy với lãi suất hơn.
Bài học cần nhớ: lãi suất là trọng lực của định giá tài chính.

## Video 04 — Lecture 2: Linear Algebra
### Trang 1
Video xây nền đại số tuyến tính: vector, matrix, linear combination, rank, basis, eigenvalues/eigenvectors. Trong tài chính, dữ liệu nhiều chiều gần như luôn được biểu diễn bằng vector và matrix.
Một tài sản có thể xem là vector đặc trưng: return, volatility, factor exposure, liquidity. Một danh mục là tổ hợp tuyến tính của nhiều tài sản.
Ma trận giúp mô tả nhiều quan sát cùng lúc: nhiều cổ phiếu, nhiều ngày, nhiều biến.

### Công thức
```

```
### Trang 2
Eigenvalues và eigenvectors rất quan trọng vì sau này dẫn tới PCA, covariance matrix và factor analysis.
Nhà đầu tư không cần tính tay mọi thứ, nhưng cần hiểu rằng nhiều chỉ báo trên chart thực ra là các chiều dữ liệu trong một vector.
Bài học cần nhớ: muốn làm model tài chính nghiêm túc, phải đưa dữ liệu về ma trận sạch.

## Video 05 — Lecture 4: Linear Algebra (cont.); Probability Theory
### Trang 1
Video nối đại số tuyến tính với xác suất. Tài chính không chỉ là con số cố định mà là biến ngẫu nhiên. Return tương lai, lỗ/lãi, default, volatility đều bất định.
Các khái niệm nền gồm random variable, probability distribution, expectation, variance, covariance, correlation.
Covariance/correlation cho biết hai biến đi cùng nhau thế nào — rất quan trọng trong danh mục.

### Công thức
```

```
### Trang 2
Expectation là trung bình có trọng số xác suất, nhưng nhà đầu tư cũng phải nhìn dispersion/tail risk. Hai chiến lược cùng expected return có thể có rủi ro rất khác.
Correlation không phải causation. Hai cổ phiếu cùng tăng không có nghĩa một cái gây ra cái kia; có thể cùng chịu market factor.
Bài học cần nhớ: tài chính là bài toán xác suất có tương quan, không phải từng mã độc lập.

## Video 06 — Lecture 5: Probability Theory (cont.); Stochastic Processes I
### Trang 1
Video chuyển từ biến ngẫu nhiên đơn lẻ sang quá trình ngẫu nhiên theo thời gian. Giá tài sản là chuỗi P0, P1, P2,... chứ không phải một điểm độc lập.
Các ý quan trọng gồm random walk, martingale intuition, Markov chain, path dependence và gambler’s ruin.
Gambler’s ruin nhắc rằng kể cả game có xác suất tưởng ổn, quản trị vốn sai vẫn có thể cháy tài khoản.

### Công thức
```

```
### Trang 2
Stochastic process giúp nhà đầu tư hiểu rằng đường đi quan trọng. Một lệnh có thể cuối kỳ lời nhưng trong quá trình chịu drawdown lớn khiến không thể nắm giữ.
Time order cực kỳ quan trọng. Không được đánh giá dữ liệu tài chính như dữ liệu độc lập không thứ tự.
Bài học cần nhớ: giá là một đường đi ngẫu nhiên; risk nằm cả trong path chứ không chỉ kết quả cuối.

## Video 07 — Lecture 6: Stochastic Processes I (cont.); Regression Analysis
### Trang 1
Video bắt đầu hồi quy. Regression dùng biến giải thích để mô hình hóa biến mục tiêu, ví dụ dùng factor/indicator để giải thích return.
Mô hình tuyến tính cơ bản có dạng y = a + b1x1 + b2x2 + error. Error đại diện phần chưa giải thích được.
Trong tài chính, error thường lớn vì thị trường nhiễu và chịu nhiều biến không quan sát được.

### Công thức
```

```
### Trang 2
Regression không phải máy dự đoán chắc chắn. Nó là công cụ kiểm định quan hệ và ước lượng độ mạnh yếu của feature.
Cần cẩn thận multicollinearity, overfit, outlier và in-sample đẹp nhưng out-of-sample tệ.
Bài học cần nhớ: regression giúp hỏi “feature này có thông tin không?”, không phải “công thức này chắc thắng không?”.

## Video 08 — Lecture 7: Linear Rates, Products, and Models
### Trang 1
Video đi vào thị trường lãi suất: SOFR/LIBOR, yield curve, forwards, swaps, discount factors và mô hình rate.
Lãi suất không chỉ là một con số. Đường cong lãi suất thể hiện lãi suất theo nhiều kỳ hạn khác nhau.
Các sản phẩm như interest rate swaps cho phép trao đổi dòng tiền lãi suất cố định và thả nổi.

### Công thức
```

```
### Trang 2
Trong thực tế, định giá fixed income phụ thuộc cách xây dựng yield curve và discount curve. Sai curve thì sai valuation.
Với nhà đầu tư cổ phiếu, bài này giúp hiểu rate regime ảnh hưởng định giá, tín dụng, ngân hàng, BĐS, cổ phiếu tăng trưởng và thanh khoản.
Bài học cần nhớ: lãi suất là một cấu trúc theo kỳ hạn; market regime không thể tách khỏi rate regime.

## Video 09 — Lecture 8: Regression Analysis (cont.)
### Trang 1
Video đào sâu regression: OLS, goodness of fit, residuals, statistical significance, model diagnostics và practical pitfalls.
Một mô hình có R² cao chưa chắc hữu dụng cho trading nếu nó không ổn định hoặc không dự báo được ngoài mẫu.
Residual analysis giúp xem model bỏ sót cấu trúc nào: nonlinear, outlier, regime change.

### Công thức
```

```
### Trang 2
Trong tài chính, statistical significance không đồng nghĩa economic significance. Một hiệu ứng rất nhỏ có thể có p-value đẹp nhưng không đủ bù chi phí giao dịch.
Cần phân biệt explanatory model và predictive model. Giải thích quá khứ tốt chưa chắc dự báo tương lai tốt.
Bài học cần nhớ: kiểm định phải đi cùng ý nghĩa kinh tế và out-of-sample.

## Video 10 — Lecture 9: Principal Component Analysis in Finance
### Trang 1
Video giảng PCA trong tài chính. PCA tìm các hướng biến động chính trong dữ liệu bằng eigenvectors/eigenvalues của covariance/correlation matrix.
Trong yield curve, PCA thường tìm ra các factor như level, slope, curvature. Trong equity, PCA có thể tách market factor, sector factor, idiosyncratic movement.
PCA giúp giảm chiều dữ liệu và loại nhiễu.

### Công thức
```

```
### Trang 2
Với nhà đầu tư, PCA dạy rằng nhiều tài sản/indicator có thể cùng chịu một factor. Danh mục nhìn có vẻ đa dạng nhưng thực ra cùng một nguồn rủi ro.
PCA không tự động tạo chiến lược. Nó là công cụ hiểu cấu trúc biến động và giảm trùng lặp.
Bài học cần nhớ: đừng đếm nhiều biến trùng nhau thành nhiều bằng chứng độc lập.

## Video 11 — Lecture 10: Counterparty Risk Optimization
### Trang 1
Video nói về rủi ro đối tác và tối ưu hóa exposure. Trong tài chính tổ chức, rủi ro không chỉ là giá thị trường đi ngược mà còn là đối tác không thực hiện nghĩa vụ.
Các khái niệm gồm exposure, default probability, collateral, netting, wrong-way risk và optimization under constraints.
Tối ưu hóa phải tôn trọng ràng buộc thực tế, không chỉ nghiệm toán đẹp.

### Công thức
```

```
### Trang 2
Với nhà đầu tư cá nhân, bài này chuyển hóa thành tư duy concentration risk: quá tập trung ngành, broker, thanh khoản, margin hoặc một macro factor.
Wrong-way risk tương tự việc mua cổ phiếu BĐS dùng margin đúng lúc tín dụng siết — risk tăng cùng lúc tài sản giảm.
Bài học cần nhớ: risk có thể nằm ở cấu trúc exposure, không chỉ từng mã riêng lẻ.

## Video 12 — Lecture 11: Regression Analysis (cont.)
### Trang 1
Video tiếp tục các vấn đề thực hành của regression: lựa chọn biến, tương tác giữa biến, kiểm định giả định, outlier và ổn định hệ số.
Một feature có thể có tác dụng khác nhau theo regime. Ví dụ volatility cao có thể tốt cho breakout nhưng xấu cho mean reversion.
Linear model có thể bỏ sót quan hệ phi tuyến.

### Công thức
```

```
### Trang 2
Nhà đầu tư nên dùng regression như kính hiển vi kiểm feature, không phải hộp đen quyết định mua bán.
Cần hỏi: coefficient có ổn định qua thời gian không? Feature có còn hiệu quả sau chi phí không? Có hoạt động trong thị trường giảm không?
Bài học cần nhớ: feature tốt phải ổn định, có ý nghĩa kinh tế và chịu được kiểm định theo regime.

## Video 13 — Lecture 13: Portfolio Management
### Trang 1
Video giảng portfolio management: expected return, covariance matrix, diversification, efficient frontier, constraints và quản trị danh mục thực tế.
Danh mục không phải chỉ là danh sách cổ phiếu tốt. Rủi ro danh mục phụ thuộc tỷ trọng và mức tương quan giữa các tài sản.
Công thức nền: portfolio variance = wᵀΣw.

### Công thức
```

```
### Trang 2
Diversification thật không phải mua nhiều mã, mà là sở hữu nhiều nguồn return/risk khác nhau. 5 mã cùng ngành có thể giống một vị thế lớn.
Trong thực tế còn có constraints: thanh khoản, giới hạn tỷ trọng, mandate, tracking error, drawdown, thuế/phí.
Bài học cần nhớ: chọn mã chỉ là nửa đầu; phân bổ vốn mới quyết định sống còn.

## Video 14 — Lecture 14: Stochastic Processes II
### Trang 1
Video mở rộng quá trình ngẫu nhiên: mô hình hóa đường đi, continuous-time intuition, Brownian motion và các tiến trình dùng trong tài chính.
Thay vì chỉ quan tâm expected return cuối kỳ, stochastic process quan tâm toàn bộ path: biến động, drawdown, hitting time.
Nhiều sản phẩm phái sinh phụ thuộc path hoặc volatility, không chỉ giá cuối.

### Công thức
```

```
### Trang 2
Nhà đầu tư nên hiểu rằng chịu đựng drawdown là một phần của chiến lược. Một strategy có return tốt nhưng path quá xấu có thể không dùng được.
Các metric như max drawdown, time underwater, time to target rất quan trọng.
Bài học cần nhớ: trong thị trường, đường đi quan trọng không kém đích đến.

## Video 15 — Lecture 12: Time Series Analysis
### Trang 1
Video giảng chuỗi thời gian: AR, MA, ARMA, stationarity, autocorrelation, trend, seasonality, fitting và forecast.
Financial time series thường nhiễu, không ổn định và dễ đổi regime. Một mô hình fit quá khứ tốt có thể hỏng khi cấu trúc thị trường đổi.
Stationarity là giả định mạnh: phân phối thống kê không đổi theo thời gian.

### Công thức
```

```
### Trang 2
Nhà đầu tư cần gắn mọi tín hiệu với horizon. Một feature có thể hữu ích 5 ngày nhưng vô nghĩa 60 ngày.
Không nên random split dữ liệu time series vì làm lẫn tương lai với quá khứ trong validation.
Bài học cần nhớ: đánh giá chiến lược theo thời gian, theo horizon, theo regime.

## Video 16 — Lecture 18: Applying Data Science and Artificial Intelligence to Managing Biomedical Portfolios
### Trang 1
Video ứng dụng AI/data science vào quản lý portfolio biomedical, nhưng bài học chung là ra quyết định trong môi trường dữ liệu phức tạp, bất định và nhiều chiều.
AI không thay domain knowledge. Dữ liệu sạch, feature đúng, label rõ và kiểm định nghiêm quan trọng hơn model hào nhoáng.
Portfolio decision cần kết hợp model, chuyên môn và risk management.

### Công thức
```

```
### Trang 2
Nhà đầu tư nên xem AI là công cụ hỗ trợ xác suất và sàng lọc, không phải người phán đúng sai tuyệt đối.
Trong tài chính, overfit rất dễ xảy ra vì tín hiệu yếu, noise lớn, regime đổi.
Bài học cần nhớ: AI tốt bắt đầu từ câu hỏi đúng và dữ liệu đúng, không phải thuật toán phức tạp nhất.

## Video 17 — Lecture 19: Volatility Modeling
### Trang 1
Video giảng volatility modeling: realized volatility, volatility clustering, ARCH/GARCH intuition và vai trò của volatility trong pricing/risk.
Volatility không cố định. Sau giai đoạn biến động mạnh, biến động thường tiếp tục cao một thời gian.
Volatility là input quan trọng trong option pricing và risk management.

### Công thức
```

```
### Trang 2
Với cổ phiếu, volatility giúp đặt stop, target và position size. Mã ATR cao không thể size như mã ATR thấp.
Vol cao có thể tăng xác suất chạm target nhưng cũng tăng xác suất chạm stop/drawdown.
Bài học cần nhớ: volatility là cả cơ hội lẫn rủi ro; phải đưa vào sizing.

## Video 18 — Lecture 21: Black-Scholes Formula, Risk Neutral Valuation
### Trang 1
Video giảng Black-Scholes, risk-neutral valuation và định giá option. Option price phụ thuộc S, K, T, r, σ.
Công thức call: C = S N(d1) - K e^{-rT} N(d2). Ý nghĩa quan trọng hơn thuộc lòng công thức là hiểu input nào làm option tăng/giảm.
Risk-neutral valuation là khung no-arbitrage để định giá, không phải nói nhà đầu tư trung lập rủi ro trong đời thực.

### Công thức
```

```
### Trang 2
Với chứng quyền, cổ phiếu cơ sở tăng chưa chắc CW lời nếu time decay, spread, liquidity hoặc break-even bất lợi.
Greeks như Delta, Gamma, Vega, Theta giúp hiểu CW nhạy với underlying, volatility và thời gian.
Bài học cần nhớ: phân tích phái sinh phải tính thời gian và volatility, không chỉ đoán hướng cổ phiếu cơ sở.

## Video 19 — Lecture 20: Building the First Federally (CFTC) Regulated Exchange Dedicated to Trading on Events
### Trang 1
Video nói về sàn giao dịch event contracts được quản lý, nơi payoff phụ thuộc một sự kiện xảy ra hay không.
Event contract biến niềm tin về sự kiện thành giá/xác suất thị trường. Nó khác cổ phiếu vì payoff thường rời rạc/binary hơn.
Market design, regulation và settlement rule rất quan trọng.

### Công thức
```

```
### Trang 2
Nhà đầu tư cổ phiếu gặp event risk liên tục: KQKD, chia cổ tức, chính sách, pháp lý, dự án, nâng hạng, lãi suất.
Không nên dùng backtest kỹ thuật bình thường qua event lớn mà không đánh dấu. Event có thể phá pattern.
Bài học cần nhớ: một số rủi ro là binary/event-driven và phải được mô hình hóa riêng.

## Video 20 — Lecture 23: Introduction to Machine Learning
### Trang 1
Video giới thiệu ML: supervised learning, feature, label, train/test, classification, regression, overfitting, model evaluation.
ML học pattern từ dữ liệu, nhưng trong tài chính pattern thường yếu, nhiễu và thay đổi theo regime.
Train/test separation là bắt buộc; time-series phải split theo thời gian.

### Công thức
```

```
### Trang 2
Nhà đầu tư nên dùng ML để tạo probability/ranking, không dùng như câu trả lời chắc chắn.
Model cần calibration: nếu nói xác suất 60%, thực tế nhóm đó có thắng khoảng 60% không?
Bài học cần nhớ: ML không cứu dữ liệu bẩn; nó chỉ làm lỗi tinh vi hơn nếu validation sai.

## Video 21 — Lecture 24: Stochastic Calculus
### Trang 1
Video giới thiệu stochastic calculus, Brownian motion/Wiener process và Ito calculus. Đây là nền toán sâu cho option pricing và continuous-time finance.
Khác calculus thông thường, biến ngẫu nhiên có quadratic variation nên quy tắc đạo hàm/tích phân thay đổi. Ito lemma là công cụ trung tâm.
Mục tiêu là xử lý hàm của quá trình ngẫu nhiên.

### Công thức
```

```
### Trang 2
Nhà đầu tư không cần dùng Ito hàng ngày để chọn cổ phiếu, nhưng nên hiểu option/volatility model dựa trên nền này.
Tư duy quan trọng: giá có phần drift và phần shock ngẫu nhiên; không thể chỉ extrapolate đường thẳng.
Bài học cần nhớ: với phái sinh và risk path, toán của ngẫu nhiên liên tục rất quan trọng.

## Video 22 — Lecture 25: Stochastic Calculus (cont.); Stochastic Differential Equations
### Trang 1
Video tiếp tục stochastic calculus và stochastic differential equations. SDE mô tả biến tài chính bằng drift cộng shock ngẫu nhiên: dS = μSdt + σSdW.
Geometric Brownian Motion là mô hình cổ điển cho giá cổ phiếu, nền của Black-Scholes.
Mô hình đơn giản hóa thực tế: volatility có thể thay đổi, jump có thể xảy ra, return không hoàn toàn normal.

### Công thức
```

```
### Trang 2
Nhà đầu tư nên dùng SDE như tư duy kịch bản: base, bull, bear, shock, gap risk. Không nên tin một đường dự phóng duy nhất.
Với CW/option, đường đi, thời gian và volatility quyết định rất nhiều đến kết quả.
Bài học cần nhớ: tài chính là phân phối các kịch bản, không phải một tương lai duy nhất.