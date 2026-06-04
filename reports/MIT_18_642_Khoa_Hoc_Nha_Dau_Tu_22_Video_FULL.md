# MIT 18.642 — Khóa học cho nhà đầu tư chứng khoán & LH Investment


## Module 01 — Tổng quan khóa học & cách tư duy tài chính định lượng

Nguồn: Lecture 1 Parts I–II

### Bài học chính

- Tài chính không phải là đoán giá, mà là ra quyết định dưới bất định.
- Một tài sản là quyền hưởng dòng tiền hoặc payoff trong tương lai.
- Nhà đầu tư phải luôn hỏi: lợi nhuận kỳ vọng là gì, rủi ro là gì, xác suất bao nhiêu, sai khi nào?

### Giải thích
MIT 18.642 bắt đầu bằng việc đặt nền cho tư duy định lượng. Thị trường tài chính gồm cổ phiếu, trái phiếu, phái sinh, quỹ, hàng hóa, tiền tệ và nhiều sản phẩm lai. Điểm chung của tất cả sản phẩm là chúng có payoff trong tương lai và payoff đó bất định. Vì vậy, tài chính định lượng không tìm một câu trả lời chắc chắn, mà xây khung để định giá, đo xác suất, đo rủi ro và chọn quyết định có kỳ vọng tốt nhất.

### Công thức
```
Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

### Ý nghĩa nhà đầu tư
Là nhà đầu tư chứng khoán, anh không nên chỉ hỏi “MWG có tăng không?”. Câu hỏi đúng là: nếu mua MWG hôm nay, trong 20 phiên tới xác suất lời >6% là bao nhiêu, xác suất lỗ >5% là bao nhiêu, mức lời/lỗ trung bình ra sao, và điều kiện nào làm kèo này sai?

### Hiểu sai

- Nhầm tín hiệu kỹ thuật với sự chắc chắn.
- Chỉ nhìn upside mà bỏ qua drawdown và thanh khoản.
- Không phân biệt trade ngắn hạn với đầu tư dài hạn.

### Bài tập

- Chọn 3 mã anh đang quan tâm và viết ra: lý do mua, điểm sai, target, stop, horizon.
- Với mỗi mã, ước lượng nếu đúng lời bao nhiêu %, nếu sai lỗ bao nhiêu %.

## Module 02 — Bond Math — Lãi suất, chiết khấu, duration, convexity

Nguồn: Lecture 1 Part III

### Bài học chính

- Tiền hôm nay đáng giá hơn tiền tương lai.
- Lãi suất tăng làm giảm present value.
- Duration đo độ nhạy của giá với lãi suất.
- Convexity giúp hiểu sai lệch khi lãi suất biến động lớn.

### Giải thích
Bond Math là nền móng định giá tài sản. Một dòng tiền trong tương lai phải được chiết khấu về hiện tại. Trái phiếu có coupon và principal, giá là tổng present value của các dòng tiền đó. Khi yield tăng, mẫu số chiết khấu tăng nên giá trái phiếu giảm. Duration cho biết giá nhạy thế nào với yield. Tư duy này cũng áp dụng cho cổ phiếu: cổ phiếu tăng trưởng có dòng tiền xa tương lai nên giống tài sản duration dài, rất nhạy với lãi suất.

### Công thức
```
PV = CF/(1+r)^t
Bond Price = Σ Coupon_t/(1+y)^t + Face/(1+y)^T
%ΔPrice ≈ -Duration × ΔYield
```

### Ý nghĩa nhà đầu tư
Khi lãi suất/tiền gửi tăng, cổ phiếu P/E cao, câu chuyện tăng trưởng xa tương lai dễ bị nén định giá. Ngược lại khi lãi suất giảm, dòng tiền rẻ hơn và risk appetite có thể cải thiện. Nhà đầu tư Việt Nam nên nhìn lãi suất huy động, tín dụng, tỷ giá như bối cảnh nền cho thị trường.

### Hiểu sai

- Nghĩ cổ phiếu không liên quan lãi suất.
- Chỉ nhìn lợi nhuận doanh nghiệp mà quên P/E có thể bị nén.
- Mua CW dài/short time decay mà không hiểu time value.

### Bài tập

- So sánh một cổ phiếu growth P/E cao và một cổ phiếu dividend/cashflow ổn định khi lãi suất tăng.
- Ghi lại 3 ngành nhạy lãi suất: ngân hàng, BĐS, chứng khoán/growth.

## Module 03 — Linear Algebra — Vector, matrix, factor và danh mục

Nguồn: Lecture 2 + Lecture 4

### Bài học chính

- Mỗi cổ phiếu/ngày là một vector đặc trưng.
- Nhiều cổ phiếu nhiều ngày tạo thành ma trận dữ liệu.
- Covariance/correlation đo mức đi cùng nhau.
- Eigen/PCA giúp tìm factor chính.

### Giải thích
Linear algebra biến dữ liệu thị trường thành dạng máy có thể học. Ví dụ MWG ngày hôm nay có vector: return 20 ngày, RSI, MACD, volume ratio, ATR%, khoảng cách tới hỗ trợ, khoảng cách tới kháng cự, pattern score. Nếu làm cho 120 mã trong 800 ngày, ta có ma trận hàng chục nghìn dòng. Từ ma trận này có thể chạy regression, PCA, ML, portfolio optimization.

### Công thức
```
x_t = [ret20, RSI, MACD, volumeRatio, ATR%, distSupport, distResistance]
X = stock-date observations × features
```

### Ý nghĩa nhà đầu tư
Khi anh nhìn nhiều chỉ báo trên chart, thực chất anh đang nhìn một vector. Vấn đề là nhiều chỉ báo trùng nhau. RSI, Stochastic, Williams %R đều là momentum oscillator. Nếu cả 3 cùng xanh, không có nghĩa là 3 bằng chứng độc lập.

### Hiểu sai

- Đếm nhiều indicator trùng nhau thành nhiều tín hiệu độc lập.
- Không chuẩn hóa dữ liệu trước khi so sánh.
- Không có feature matrix nên model chỉ là cảm tính có code.

### Bài tập

- Viết vector 10 feature cho một mã anh đang theo dõi.
- Đánh dấu feature nào thuộc trend, momentum, volume, volatility, support/resistance.

## Module 04 — Xác suất & stochastic process — nghĩ theo phân phối, không nghĩ theo chắc chắn

Nguồn: Lecture 4 + 5 + 6

### Bài học chính

- Return tương lai là biến ngẫu nhiên.
- Giá là một quá trình theo thời gian, không phải một điểm.
- Tín hiệu chỉ làm thay đổi xác suất có điều kiện.
- Backtest phải giữ thứ tự thời gian.

### Giải thích
Probability dạy kỳ vọng, phương sai, phân phối, xác suất có điều kiện. Stochastic process dạy rằng giá cổ phiếu là chuỗi biến ngẫu nhiên theo thời gian. Một setup đẹp không đảm bảo thắng; nó chỉ có thể làm xác suất thắng cao hơn hoặc payoff tốt hơn. Vì dữ liệu có thứ tự thời gian, không được random shuffle khi đánh giá chiến lược.

### Công thức
```
P(hit target | setup present)
E[R | setup] = Σ p_i × r_i
```

### Ý nghĩa nhà đầu tư
Thay vì nói “mã này chắc vượt đỉnh”, hãy nói “trong quá khứ, setup tương tự có 54% xác suất đạt +6% trong 20 phiên, avgWin 9%, avgLoss -4%, EV dương”. Cách nói này giúp anh biết có nên đánh và đánh bao nhiêu.

### Hiểu sai

- Lấy vài ví dụ thắng rồi tin setup.
- Không tính sample size.
- Dùng dữ liệu tương lai vô tình trong feature.

### Bài tập

- Với một setup anh thích, tìm ít nhất 30 mẫu quá khứ và ghi thắng/thua.
- Tính win rate, avg win, avg loss.

## Module 05 — Regression Analysis — kiểm định feature nào thật sự có edge

Nguồn: Lecture 6 + 8 + 11

### Bài học chính

- Regression đo quan hệ giữa feature và future return.
- Coefficient không ổn định thì không đáng tin.
- In-sample đẹp chưa chắc out-of-sample tốt.
- Residual và outlier rất quan trọng.

### Giải thích
Regression là công cụ để kiểm xem các feature như RSI, ATR, khoảng cách tới hỗ trợ có liên quan future return không. Nhưng regression trong tài chính rất dễ bị nhiễu, multicollinearity và overfit. Do đó phải xem coefficient ổn định qua thời gian không, top/bottom quintile có khác biệt không, và OOS có giữ được không.

### Công thức
```
futureReturn20d = a + b1*distSupport + b2*distResistance + b3*ATR + b4*RSI + error
```

### Ý nghĩa nhà đầu tư
Nếu một indicator được quảng cáo rất hay nhưng khi kiểm định không tạo spread giữa nhóm tốt và nhóm xấu, nó chỉ là trang trí. Feature tốt phải giúp phân biệt nhóm có kỳ vọng tốt hơn.

### Hiểu sai

- Tin R² cao trong sample nhỏ.
- Tối ưu tham số trên toàn bộ lịch sử rồi tưởng là khách quan.
- Không kiểm regime.

### Bài tập

- Chia dữ liệu thành 2023-2024 train, 2025 validate, 2026 test.
- Kiểm một feature: nhóm top 20% và bottom 20% có future return khác nhau không?

## Module 06 — PCA trong Finance — bớt ảo giác nhiều tín hiệu

Nguồn: Lecture 9

### Bài học chính

- PCA tìm hướng biến động chính trong dữ liệu.
- Eigenvalue cho biết factor giải thích bao nhiêu variance.
- PCA giúp giảm trùng lặp indicator.
- Danh mục có thể bị chi phối bởi market factor/sector factor.

### Giải thích
PCA lấy ma trận dữ liệu và tìm các trục chính giải thích biến động. Trong tài chính, PC1 thường giống market factor, các PC sau có thể giống sector/style factor. Với indicator, PCA/correlation giúp thấy RSI/Stoch/Williams cùng một nhóm, ATR/realized vol/Bollinger width cùng một nhóm.

### Công thức
```
X ≈ PC1 + PC2 + ... + noise
```

### Ý nghĩa nhà đầu tư
Nếu danh mục có 10 mã nhưng tất cả đều cùng factor chứng khoán/thanh khoản, anh tưởng phân tán nhưng thực ra đang all-in một yếu tố. PCA/correlation giúp nhìn rủi ro ẩn đó.

### Hiểu sai

- Cộng điểm indicator trùng nhau làm score phình giả.
- Không biết portfolio bị một factor chi phối.
- Dùng PCA nhưng không hiểu ý nghĩa kinh tế.

### Bài tập

- Nhóm 20 indicator thành 5 nhóm: trend, momentum, volume, volatility, SR.
- Trong danh mục hiện tại, đánh dấu mã nào cùng ngành/cùng beta thị trường.

## Module 07 — Rates Products & Yield Curve — đọc môi trường lãi suất

Nguồn: Lecture 7

### Bài học chính

- Yield curve là cấu trúc lãi suất theo kỳ hạn.
- Forward rate là kỳ vọng/định giá lãi suất tương lai.
- Swaps và hedging dùng để quản trị rate risk.
- Rate regime ảnh hưởng sector khác nhau.

### Giải thích
Lecture về rates đi sâu vào sản phẩm lãi suất như SOFR/LIBOR, swaps, curve construction. Với nhà đầu tư cổ phiếu, không cần trade swap, nhưng cần hiểu môi trường lãi suất ảnh hưởng định giá, tín dụng, thanh khoản và khẩu vị rủi ro.

### Công thức
```
Discount factor = 1/(1+r_t)^t
```

### Ý nghĩa nhà đầu tư
Ngân hàng có thể hưởng lợi từ NIM trong vài giai đoạn, BĐS chịu áp lực khi tín dụng/lãi suất căng, chứng khoán phụ thuộc thanh khoản. Vì vậy cùng một signal kỹ thuật nhưng hiệu quả khác nhau theo rate regime.

### Hiểu sai

- Dùng một chiến lược cho mọi macro regime.
- Bỏ qua tín dụng và thanh khoản khi phân tích BĐS/chứng khoán.

### Bài tập

- Ghi lại lãi suất tiền gửi 12 tháng, tỷ giá, thanh khoản thị trường hàng tuần.
- Đánh dấu sector nào hưởng lợi/bị hại khi rate tăng.

## Module 08 — Time Series Analysis — horizon, regime shift và stationarity

Nguồn: Lecture 12

### Bài học chính

- Chuỗi thời gian có autocorrelation và regime shift.
- Stationarity là giả định mạnh, thường bị phá vỡ.
- Một feature có thể tốt 5 ngày nhưng tệ 60 ngày.
- Forecast phải gắn horizon.

### Giải thích
Time series analysis nghiên cứu dữ liệu theo thời gian: AR, MA, ARMA, stationarity, trend, cycle. Trong chứng khoán, thị trường đổi chế độ: bull, bear, sideway, high volatility. Model cố định dễ hỏng khi regime đổi.

### Công thức
```
R_t = a + b R_{t-1} + error
```

### Ý nghĩa nhà đầu tư
Anh phải phân biệt trade T+ ngắn hạn, swing 20 phiên, trend 60 phiên. Một setup breakout có thể tốt 10-20 phiên nhưng không nói gì về đầu tư 1 năm.

### Hiểu sai

- Trộn timeframe trong một score.
- Backtest 2023 rồi áp 2026 không kiểm regime.
- Không đo time-to-target.

### Bài tập

- Với một chiến lược, tính kết quả 5d, 10d, 20d, 60d riêng.
- Kiểm xem chiến lược tốt nhất ở horizon nào.

## Module 09 — Portfolio Management & Counterparty Risk — chọn mã chưa đủ, phải phân bổ vốn

Nguồn: Lecture 10 + 13

### Bài học chính

- Danh mục phụ thuộc covariance, không chỉ số lượng mã.
- Diversification thật là khác nguồn rủi ro.
- Optimization cần constraints thực tế.
- Concentration risk có thể giết tài khoản.

### Giải thích
Portfolio management dùng expected return vector và covariance matrix để phân bổ vốn. Counterparty risk optimization dạy tư duy exposure, concentration, dependency. Với cổ phiếu, risk tương tự là tập trung ngành, beta thị trường, thanh khoản và các mã cùng factor.

### Công thức
```
Portfolio variance = wᵀ Σ w
```

### Ý nghĩa nhà đầu tư
Mua SSI, VND, HCM, VCI, MBS không phải là 5 kèo độc lập. Đó là một kèo lớn vào ngành chứng khoán/thanh khoản. Position size phải giảm nếu correlation cao.

### Hiểu sai

- Danh mục nhiều mã nhưng cùng ngành.
- Không có sector cap.
- Mã volatility cao nhưng size như mã phòng thủ.

### Bài tập

- Tính tỷ trọng danh mục theo ngành.
- Đặt rule: không quá X% vào một sector nếu market regime xấu.

## Module 10 — Volatility Modeling — biến động là risk và cũng là cơ hội

Nguồn: Lecture 19

### Bài học chính

- Volatility thay đổi và có clustering.
- ATR% là thước đo thực dụng cho cổ phiếu.
- Vol cao tăng cơ hội hit target nhưng cũng tăng drawdown.
- Stop và position size nên theo volatility.

### Giải thích
Volatility modeling dạy rằng biến động không cố định. Sau cú sốc, thị trường thường tiếp tục biến động mạnh. Volatility ảnh hưởng option pricing, stop-loss, sizing và xác suất chạm target/stop.

### Công thức
```
RealizedVol20 = std(daily returns 20d) × sqrt(252)
ATR% = ATR14 / Close
```

### Ý nghĩa nhà đầu tư
Không nên dùng stop 5% cho mọi mã. Mã ATR 1.5% và mã ATR 5% khác nhau hoàn toàn. Vol cao có thể trade được nhưng size phải nhỏ hơn và stop/target phải hợp lý.

### Hiểu sai

- Thấy vol cao là mua vì “sắp chạy”.
- Đặt stop quá gần với mã biến động mạnh.
- Không tính gap risk.

### Bài tập

- Tính ATR% cho 5 mã anh hay xem.
- So sánh target/stop có phù hợp ATR không.

## Module 11 — Black-Scholes, Options và Chứng quyền CW

Nguồn: Lecture 21

### Bài học chính

- Option/CW phụ thuộc S, K, T, r, σ.
- Time decay làm CW mất giá theo thời gian.
- Break-even quan trọng hơn leverage đẹp.
- Greeks giúp hiểu rủi ro option.

### Giải thích
Black-Scholes cho thấy giá option không chỉ phụ thuộc cổ phiếu cơ sở tăng hay giảm. Nó còn phụ thuộc thời gian còn lại, volatility, lãi suất, strike và moneyness. Risk-neutral valuation là logic định giá không-arbitrage, không phải bảo rằng đời thực không rủi ro.

### Công thức
```
Call = S N(d1) - K e^{-rT} N(d2)
Inputs: S, K, T, r, σ
```

### Ý nghĩa nhà đầu tư
Với CW, anh có thể đúng cổ phiếu cơ sở nhưng vẫn không lời nếu CW gần đáo hạn, spread rộng, thanh khoản thấp, break-even xa hoặc theta ăn mòn. Vì vậy CW score phải khác stock score.

### Hiểu sai

- Chọn CW vì leverage cao nhất.
- Không nhìn ngày đáo hạn.
- Không tính break-even và spread.

### Bài tập

- Lấy 3 CW cùng underlying, so sánh daysToMaturity, spread, break-even.
- Chỉ chọn CW nếu underlying signal đủ mạnh và break-even hợp lý.

## Module 12 — AI, Machine Learning, Event Markets & Stochastic Calculus

Nguồn: Lecture 18 + 20 + 23 + 24 + 25

### Bài học chính

- ML cần dữ liệu sạch, label rõ, OOS nghiêm.
- Event markets biến biến cố thành xác suất.
- Stochastic calculus là nền cho option/vol/path risk.
- Model nên xuất probability, không xuất chắc chắn.

### Giải thích
Các lecture cuối mở rộng sang AI/ML, event contracts và stochastic calculus. ML trong finance dễ overfit vì noise và regime shift. Event market dạy cách nghĩ về biến cố như xác suất. Stochastic calculus/SDE cho hiểu sâu về path, volatility và option pricing.

### Công thức
```
dS = μSdt + σSdW
Model output: P(hit target), P(drawdown), Expected Return
```

### Ý nghĩa nhà đầu tư
ML hữu ích nếu dùng để rank xác suất và giải thích feature. Nó nguy hiểm nếu anh tin nó như hộp đen. Với event như KQKD, chính sách, chia cổ tức, cần eventRiskFlag riêng vì kỹ thuật thường có thể bị phá.

### Hiểu sai

- Train ML trước khi có feature matrix sạch.
- Random split dữ liệu time series.
- Không calibration xác suất.

### Bài tập

- Viết label rõ: hit +6% trong 20 phiên hay futureReturn20d?
- So sánh model ML với rule baseline đơn giản trước khi tin.