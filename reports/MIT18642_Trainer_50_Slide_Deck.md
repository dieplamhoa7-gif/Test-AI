# MIT 18.642 Trainer — 50 slide deck


## MIT 18.642 Finance Trainer
Slide deck 50 trang dành cho nhà đầu tư chứng khoán Việt Nam. Mục tiêu: học có hệ thống các khái niệm toán tài chính MIT 18.642 và biết cách áp dụng vào HOSE/HNX/VN30.

Ứng dụng: Học để xây hệ thống quyết định đầu tư dựa trên dữ liệu, không dựa vào cảm tính.

Takeaway: Lý thuyết phải đi kèm ví dụ số và ứng dụng đầu tư.


## Cách học theo skill
Mỗi topic được học theo 6 bước: tại sao cần biết, khái niệm, công thức, ví dụ số, ứng dụng đầu tư, câu hỏi kiểm tra.

Takeaway: Không học công thức rời rạc; học để ra quyết định tốt hơn.


## Bản đồ 12 modules
12 modules bao phủ toàn bộ 22 video: markets, bond math, linear algebra, probability, regression/PCA, rates, time series, portfolio risk, stochastic calculus, Black-Scholes, volatility/ML, systematic trading.


## Module 01 — Giới thiệu & thị trường tài chính: Tại sao cần biết?
Tư duy tài chính định lượng, cấu trúc thị trường, buy-side/sell-side, sản phẩm cơ bản. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Nhà đầu tư VN cần phân biệt payoff của cổ phiếu, trái phiếu và CW trước khi dùng model.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 01 — Khái niệm cốt lõi
Khái niệm chính của module: Tư duy tài chính định lượng, cấu trúc thị trường, buy-side/sell-side, sản phẩm cơ bản. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
Equity · Fixed Income · Derivatives · FX · Commodities
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 01 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Nhà đầu tư VN cần phân biệt payoff của cổ phiếu, trái phiếu và CW trước khi dùng model. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Nhà đầu tư VN cần phân biệt payoff của cổ phiếu, trái phiếu và CW trước khi dùng model.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 02 — Bond Math — Toán học trái phiếu: Tại sao cần biết?
Time value of money, present value, YTM, duration, DV01, convexity, yield curve. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Dùng yield curve/WACC để hiểu định giá cổ phiếu, nhất là ngân hàng, BĐS, cổ phiếu growth.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 02 — Khái niệm cốt lõi
Khái niệm chính của module: Time value of money, present value, YTM, duration, DV01, convexity, yield curve. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
P=Σ C/(1+y)^t + M/(1+y)^n
D_mod=D_mac/(1+y)
DV01=D_mod*P*0.0001
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 02 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Dùng yield curve/WACC để hiểu định giá cổ phiếu, nhất là ngân hàng, BĐS, cổ phiếu growth. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Dùng yield curve/WACC để hiểu định giá cổ phiếu, nhất là ngân hàng, BĐS, cổ phiếu growth.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 03 — Đại số tuyến tính trong tài chính: Tại sao cần biết?
Vector trọng số, covariance matrix, eigenvalues, SVD, no-arbitrage, risk-neutral measure. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Danh mục VN30 là vector trọng số; covariance cho biết mua nhiều mã có thật sự giảm rủi ro không.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 03 — Khái niệm cốt lõi
Khái niệm chính của module: Vector trọng số, covariance matrix, eigenvalues, SVD, no-arbitrage, risk-neutral measure. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
R_p=w^T R
σ_p²=w^T Σ w
Σv=λv
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 03 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Danh mục VN30 là vector trọng số; covariance cho biết mua nhiều mã có thật sự giảm rủi ro không. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Danh mục VN30 là vector trọng số; covariance cho biết mua nhiều mã có thật sự giảm rủi ro không.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 04 — Xác suất & quá trình ngẫu nhiên I: Tại sao cần biết?
Không gian xác suất, moments, fat tails, martingale, gambler’s ruin, Markov chains. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Một setup cổ phiếu chỉ làm thay đổi xác suất, không tạo chắc chắn. Quản trị vốn tránh gambler’s ruin.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 04 — Khái niệm cốt lõi
Khái niệm chính của module: Không gian xác suất, moments, fat tails, martingale, gambler’s ruin, Markov chains. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
E[X], Var(X), Skewness, Kurtosis
E[X_{t+1}|F_t]=X_t
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 04 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Một setup cổ phiếu chỉ làm thay đổi xác suất, không tạo chắc chắn. Quản trị vốn tránh gambler’s ruin. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Một setup cổ phiếu chỉ làm thay đổi xác suất, không tạo chắc chắn. Quản trị vốn tránh gambler’s ruin.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 05 — Regression Analysis & PCA: Tại sao cần biết?
OLS, Gauss-Markov, CAPM, Fama-French, Ridge/Lasso, PCA, factor loading. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Kiểm indicator bằng OOS, IC, alpha, không chỉ nhìn chart đẹp. PCA giúp gom indicator trùng.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 05 — Khái niệm cốt lõi
Khái niệm chính của module: OLS, Gauss-Markov, CAPM, Fama-French, Ridge/Lasso, PCA, factor loading. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
β_hat=(X^T X)^-1 X^T Y
R_i-R_f=α+β(R_m-R_f)+ε
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 05 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Kiểm indicator bằng OOS, IC, alpha, không chỉ nhìn chart đẹp. PCA giúp gom indicator trùng. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Kiểm indicator bằng OOS, IC, alpha, không chỉ nhìn chart đẹp. PCA giúp gom indicator trùng.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 06 — Lãi suất tuyến tính & fixed income: Tại sao cần biết?
LIBOR→SOFR, FRA, IRS, bootstrapping yield curve, DV01 hedge, electronic trading. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Rate regime ảnh hưởng mạnh đến bank, BĐS, chứng khoán, cổ phiếu vay nợ cao.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 06 — Khái niệm cốt lõi
Khái niệm chính của module: LIBOR→SOFR, FRA, IRS, bootstrapping yield curve, DV01 hedge, electronic trading. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
N_hedge=-DV01_portfolio/DV01_instrument
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 06 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Rate regime ảnh hưởng mạnh đến bank, BĐS, chứng khoán, cổ phiếu vay nợ cao. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Rate regime ảnh hưởng mạnh đến bank, BĐS, chứng khoán, cổ phiếu vay nợ cao.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 07 — Time Series Analysis: Tại sao cần biết?
Stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration, pairs trading. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Không random split dữ liệu cổ phiếu. Mọi tín hiệu phải ghi horizon 5/10/20/60 phiên.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 07 — Khái niệm cốt lõi
Khái niệm chính của module: Stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration, pairs trading. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
AR(1): X_t=φX_{t-1}+ε_t
Half-life=ln(2)/|ln(1+φ)|
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 07 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Không random split dữ liệu cổ phiếu. Mọi tín hiệu phải ghi horizon 5/10/20/60 phiên. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Không random split dữ liệu cổ phiếu. Mọi tín hiệu phải ghi horizon 5/10/20/60 phiên.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 08 — Portfolio & Risk Management: Tại sao cần biết?
Markowitz, efficient frontier, VaR, CVaR, Kelly, Black-Litterman, counterparty risk. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Không all-in nhiều mã cùng ngành. Cần sector cap, correlation cap, position sizing.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 08 — Khái niệm cốt lõi
Khái niệm chính của module: Markowitz, efficient frontier, VaR, CVaR, Kelly, Black-Litterman, counterparty risk. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
IR=IC*sqrt(N)
Kelly f*=μ/σ²
CVaR=E[Loss|Loss>VaR]
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 08 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Không all-in nhiều mã cùng ngành. Cần sector cap, correlation cap, position sizing. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Không all-in nhiều mã cùng ngành. Cần sector cap, correlation cap, position sizing.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 09 — Stochastic Calculus: Tại sao cần biết?
Wiener process, quadratic variation, Itô integral, Itô lemma, GBM, SDE, Monte Carlo. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Dùng scenario distribution cho CW/options; không tin một đường forecast duy nhất.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 09 — Khái niệm cốt lõi
Khái niệm chính của module: Wiener process, quadratic variation, Itô integral, Itô lemma, GBM, SDE, Monte Carlo. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
dS=μSdt+σSdW
S_T=S_0 exp[(μ-σ²/2)T+σW_T]
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 09 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Dùng scenario distribution cho CW/options; không tin một đường forecast duy nhất. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Dùng scenario distribution cho CW/options; không tin một đường forecast duy nhất.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 10 — Black-Scholes & Option/CW: Tại sao cần biết?
BS PDE, risk-neutral valuation, Greeks, put-call parity, implied vol, smile/skew. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Chọn CW phải xét maturity, break-even, spread, liquidity, theta, IV — không chỉ leverage.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 10 — Khái niệm cốt lõi
Khái niệm chính của module: BS PDE, risk-neutral valuation, Greeks, put-call parity, implied vol, smile/skew. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
C=S*N(d1)-K*e^{-rT}*N(d2)
C-P=S-Ke^{-rT}
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 10 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Chọn CW phải xét maturity, break-even, spread, liquidity, theta, IV — không chỉ leverage. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Chọn CW phải xét maturity, break-even, spread, liquidity, theta, IV — không chỉ leverage.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 11 — Volatility Modeling, ML & AI: Tại sao cần biết?
GARCH, volatility clustering, ML pipeline, walk-forward, lookahead bias, AMH. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: ML trong finance phải OOS/walk-forward, calibration, kiểm phí giao dịch và regime shift.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 11 — Khái niệm cốt lõi
Khái niệm chính của module: GARCH, volatility clustering, ML pipeline, walk-forward, lookahead bias, AMH. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
σ_t²=ω+αε_{t-1}²+βσ_{t-1}²
IC=Corr(signal,return)
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 11 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: ML trong finance phải OOS/walk-forward, calibration, kiểm phí giao dịch và regime shift. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: ML trong finance phải OOS/walk-forward, calibration, kiểm phí giao dịch và regime shift.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Module 12 — Systematic Trading & Prediction Markets: Tại sao cần biết?
Factor investing, momentum/value/quality/low-vol, prediction markets, breadth, risk limits. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.

Ứng dụng: Xây hệ thống đầu tư: signal → validation → sizing → risk limits → review định kỳ.

Takeaway: Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.


## Module 12 — Khái niệm cốt lõi
Khái niệm chính của module: Factor investing, momentum/value/quality/low-vol, prediction markets, breadth, risk limits. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.

```
Information Ratio = IC * sqrt(Breadth)
```
Takeaway: Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.


## Module 12 — Ví dụ đầu tư Việt Nam
Ví dụ áp dụng: Xây hệ thống đầu tư: signal → validation → sizing → risk limits → review định kỳ. Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.

Ứng dụng: Xây hệ thống đầu tư: signal → validation → sizing → risk limits → review định kỳ.

Takeaway: Ứng dụng tốt phải đo được và backtest được.


## Bảng công thức phải thuộc — phần 1
Nhóm định giá và lãi suất: present value, bond price, duration, DV01, convexity, yield curve. Đây là nền để hiểu WACC, DCF, lãi suất và định giá tài sản.

```
PV=CF/(1+r)^t
P=Σ C/(1+y)^t + M/(1+y)^n
DV01=D_mod*P*0.0001
```

## Bảng công thức phải thuộc — phần 2
Nhóm xác suất, regression và portfolio: expectation, variance, covariance, OLS, CAPM, portfolio variance.

```
E[X]=Σp_i x_i
β_hat=(X^T X)^-1X^TY
σ_p²=w^TΣw
```

## Bảng công thức phải thuộc — phần 3
Nhóm time series, volatility, option và stochastic calculus: AR(1), GARCH, Black-Scholes, GBM.

```
X_t=φX_{t-1}+ε_t
σ_t²=ω+αε²_{t-1}+βσ²_{t-1}
C=S*N(d1)-K*e^{-rT}*N(d2)
dS=μSdt+σSdW
```

## Checklist dùng cho cổ phiếu VN
Khi áp dụng vào HOSE/HNX: xác định horizon, tính liquidity/slippage, kiểm market regime, tránh lookahead bias, đo EV, kiểm drawdown, sau đó mới sizing.

Takeaway: Một signal tốt phải có xác suất, payoff, rủi ro và điều kiện sai.


## Checklist dùng cho CW/chứng quyền
Với CW: không chỉ nhìn underlying tăng. Cần days to maturity, moneyness, break-even, spread, liquidity, implied volatility, theta/time decay.

Takeaway: Đúng hướng cổ phiếu cơ sở chưa đủ để lời CW.


## Bài tập thực hành 1 — Bond Math
Tính giá trái phiếu coupon 7%, face 1,000,000 VND, maturity 5 năm, yield 7.5%. Sau đó tính duration và tác động khi yield tăng 50 bps.


## Bài tập thực hành 2 — Portfolio
Với VCB/HPG/FPT, hãy lập expected return vector, volatility, correlation matrix, tính variance equal-weight và tìm danh mục Sharpe tốt hơn.


## Bài tập thực hành 3 — Regression/PCA
Chạy CAPM regression cho HPG với VN-Index. Sau đó lấy 20 indicator kỹ thuật, tính correlation/PCA để xem indicator nào trùng thông tin.


## Bài tập thực hành 4 — Time Series
Chọn một cặp cổ phiếu cùng ngành, kiểm cointegration, tính spread z-score và backtest pairs trading với rule ±2σ.


## Roadmap học 4 tuần
Tuần 1: markets, bond math, linear algebra. Tuần 2: probability, stochastic process, regression. Tuần 3: PCA, rates, time series, portfolio. Tuần 4: volatility, Black-Scholes, ML, systematic trading.


## Kết luận
MIT 18.642 không cho một công thức thần kỳ. Giá trị của khóa học là khung tư duy: xác suất, định giá, kiểm định, rủi ro, danh mục và kỷ luật hệ thống.

Takeaway: Đầu tư tốt = hiểu payoff + đo xác suất + quản trị downside + kiểm định liên tục.
