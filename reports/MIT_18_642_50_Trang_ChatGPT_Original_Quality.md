# MIT 18.642 — PDF 50 trang chất lượng, bản gốc của Tiểu đệ


## 01. Lecture 1 Part I — Introduction of the Class

### Video này dạy gì
Video mở đầu đặt khung cho toàn khóa: toán học được dùng như ngôn ngữ để mô tả sản phẩm tài chính, rủi ro, xác suất và quyết định đầu tư. Người học được chuẩn bị cho một khóa vừa có phần lý thuyết toán, vừa có phần ứng dụng từ các chuyên gia thị trường.

### Ý phải nắm
- Tài chính định lượng không phải là đoán giá, mà là mô hình hóa quyết định dưới bất định.
- Một mô hình tốt phải nói rõ giả định, dữ liệu đầu vào, giới hạn và cách kiểm định.
- Các chủ đề của khóa liên kết với nhau: linear algebra → probability → regression/PCA/time series → portfolio/derivatives/ML.

### Diễn giải
- Giảng viên nhấn mạnh đây là khóa ứng dụng, không chỉ thuần lý thuyết. Toán được học vì nó giúp định nghĩa vấn đề rõ hơn.
- Người học phải quen với việc một vấn đề tài chính có nhiều lớp: sản phẩm, payoff, dữ liệu, rủi ro, mô hình và thị trường thực tế.
- Điểm quan trọng là không thần thánh hóa công thức. Công thức là bản đồ; thị trường thực tế luôn có nhiễu, chi phí và ràng buộc.

### Công thức
```
Decision quality = model clarity + data quality + validation + risk control
```

### Nhà đầu tư cần hiểu
Nhà đầu tư nên học cách đặt câu hỏi đúng: xác suất thắng bao nhiêu, payoff thế nào, sai khi nào, và có kiểm chứng bằng dữ liệu chưa.

### Không nên hiểu sai
Không nên hiểu khóa học như bộ công thức tạo tín hiệu mua bán chắc thắng.


## 02. Lecture 1 Part II — Financial Markets, Terms and Concepts

### Video này dạy gì
Video này giới thiệu cấu trúc thị trường tài chính và các loại sản phẩm chính: cổ phiếu, trái phiếu, phái sinh, quỹ/alternative assets. Mỗi loại tài sản có payoff, rủi ro và cơ chế định giá riêng.

### Ý phải nắm
- Cổ phiếu là quyền sở hữu; trái phiếu là dòng tiền nợ; phái sinh là hợp đồng phụ thuộc tài sản cơ sở.
- Risk-return phải đi cùng liquidity, cost và market structure.
- Nhà đầu tư cần hiểu sản phẩm trước khi dùng mô hình định lượng.

### Diễn giải
- Thị trường tài chính là cơ chế chuyển vốn và phân bổ rủi ro giữa các bên.
- Sản phẩm khác nhau sinh lời từ nguồn khác nhau: business growth, coupon, leverage, volatility, liquidity premium.
- Các thuật ngữ như alpha, beta, hedge, leverage, arbitrage, liquidity không phải trang trí; chúng mô tả bản chất payoff và rủi ro.

### Công thức
```
Net return = gross return - fees - spread - slippage - financing cost
```

### Nhà đầu tư cần hiểu
Trước khi mua cổ phiếu/CW/trái phiếu, phải biết mình đang mua loại rủi ro nào và dòng payoff đến từ đâu.

### Không nên hiểu sai
Không dùng cùng một checklist cho cổ phiếu cơ sở và chứng quyền/phái sinh.


## 03. Lecture 1 Part III — Bond Mathematics

### Video này dạy gì
Video giảng nền tảng định giá dòng tiền: present value, lãi kép, lãi liên tục, yield, bond pricing, duration và convexity. Đây là phần nền cho mọi định giá tài chính.

### Ý phải nắm
- Tiền trong tương lai cần được chiết khấu về hiện tại.
- Khi yield tăng, giá trái phiếu giảm.
- Duration và DV01 đo độ nhạy giá với lãi suất; convexity xử lý độ cong của quan hệ giá-yield.

### Diễn giải
- Bond price là tổng hiện giá của coupon và principal. Yield to maturity là tỷ suất chiết khấu làm giá trị hiện tại bằng giá thị trường.
- Duration cho xấp xỉ tuyến tính khi yield đổi nhỏ; convexity cải thiện khi yield đổi lớn.
- Yield curve chứa thông tin kỳ hạn: ngắn, trung, dài hạn có lãi suất khác nhau và phản ánh kỳ vọng/ưu tiên thanh khoản/rủi ro.

### Công thức
```
PV = CF/(1+r)^t
Bond Price = Σ Coupon_t/(1+y)^t + Face/(1+y)^T
ΔP/P ≈ -Duration × Δy + 0.5 × Convexity × (Δy)^2
```

### Nhà đầu tư cần hiểu
Lãi suất là trọng lực định giá. Cổ phiếu tăng trưởng/P/E cao thường nhạy hơn với lãi suất vì dòng tiền kỳ vọng nằm xa tương lai.

### Không nên hiểu sai
Đừng nghĩ bond math chỉ dùng cho trái phiếu; nó là nền tư duy chiết khấu của mọi tài sản.


## 04. Lecture 2 — Linear Algebra

### Video này dạy gì
Video xây nền đại số tuyến tính: vector, matrix, basis, rank, linear transformation, eigenvalues/eigenvectors. Trong tài chính, dữ liệu nhiều tài sản/nhiều đặc trưng được biểu diễn bằng ma trận.

### Ý phải nắm
- Một tài sản hoặc một ngày giao dịch có thể xem như vector feature.
- Danh mục là tổ hợp tuyến tính của nhiều tài sản.
- Eigenvectors/eigenvalues là nền cho PCA và phân tích covariance.

### Diễn giải
- Vector giúp mô tả một đối tượng bằng nhiều chiều: return, volatility, liquidity, sector, beta.
- Matrix giúp mô tả toàn bộ universe: nhiều mã, nhiều ngày, nhiều biến.
- Covariance matrix cho biết tài sản cùng biến động ra sao; đây là nguyên liệu của portfolio optimization.

### Công thức
```
x_stock = [return, volatility, beta, liquidity, sector_score]
Portfolio return = wᵀr
```

### Nhà đầu tư cần hiểu
Nếu muốn xây model cổ phiếu, bước đầu không phải ML mà là ma trận dữ liệu sạch: hàng là stock-date, cột là feature.

### Không nên hiểu sai
Không nên nhồi nhiều indicator trùng ý nghĩa rồi tưởng là có nhiều bằng chứng độc lập.


## 05. Lecture 4 — Linear Algebra continued; Probability Theory

### Video này dạy gì
Video chuyển từ biểu diễn dữ liệu sang xác suất. Return, default, volatility và payoff là random variables có distribution, expectation, variance và correlation.

### Ý phải nắm
- Expectation là trung bình có trọng số xác suất, không phải kết quả chắc chắn.
- Variance/covariance đo rủi ro và liên hệ giữa biến.
- Correlation giúp hiểu diversification nhưng không chứng minh nhân quả.

### Diễn giải
- Xác suất cho phép nói về tập hợp kết quả có thể xảy ra thay vì một dự báo duy nhất.
- Trong nhiều tài sản, covariance matrix trở thành cầu nối giữa probability và linear algebra.
- Distribution shape quan trọng: skewness và kurtosis/tail risk ảnh hưởng lớn đến đầu tư.

### Công thức
```
E[X] = Σ p_i x_i
Var(X)=E[(X-E[X])²]
Cov(X,Y)=E[(X-E[X])(Y-E[Y])]
```

### Nhà đầu tư cần hiểu
Một chiến lược tốt không chỉ có return trung bình cao, mà phải có phân phối lỗ/lãi chịu được.

### Không nên hiểu sai
Không được đánh giá chiến lược chỉ bằng vài ví dụ thắng hoặc win rate đơn giản.


## 06. Lecture 5 — Probability continued; Stochastic Processes I

### Video này dạy gì
Video giới thiệu quá trình ngẫu nhiên: giá tài sản là chuỗi biến ngẫu nhiên theo thời gian. Các ý như random walk, martingale, Markov chain và gambler’s ruin rất quan trọng.

### Ý phải nắm
- Time order là bản chất của dữ liệu tài chính.
- Path risk quan trọng: drawdown giữa đường có thể phá chiến lược.
- Gambler’s ruin cho thấy quản trị vốn sai có thể làm cháy tài khoản dù xác suất không quá xấu.

### Diễn giải
- Random walk mô tả chuyển động không dễ dự đoán bằng quá khứ đơn giản.
- Martingale là khái niệm kỳ vọng tương lai bằng hiện tại dưới thông tin sẵn có.
- Markov chain mô tả xác suất chuyển trạng thái, hữu ích cho credit rating hoặc market regime.

### Công thức
```
P(X_{t+1}=j | X_t=i, history) = P(X_{t+1}=j | X_t=i)
```

### Nhà đầu tư cần hiểu
Backtest phải tôn trọng thứ tự thời gian. Một lệnh không chỉ có kết quả cuối, mà còn có max drawdown và thời gian chịu lỗ.

### Không nên hiểu sai
Không random shuffle dữ liệu time series rồi tin kết quả OOS.


## 07. Lecture 6 — Stochastic Processes continued; Regression Analysis

### Video này dạy gì
Video bắt đầu hồi quy: dùng biến giải thích để mô hình hóa biến mục tiêu. Trong tài chính, regression giúp kiểm định feature/factor có liên hệ với return hay không.

### Ý phải nắm
- Hồi quy tuyến tính có dạng y = Xβ + ε.
- Coefficient cho biết hướng/độ mạnh quan hệ, nhưng chỉ đáng tin nếu giả định và validation ổn.
- Error/residual chứa phần model chưa giải thích.

### Diễn giải
- Regression là công cụ phân tích, không phải lời cam kết dự báo.
- Feature có thể bị nhiễu, outlier hoặc liên hệ giả do cùng chịu một factor.
- Trong dữ liệu tài chính, cần kiểm stability và out-of-sample, không chỉ fit in-sample.

### Công thức
```
future_return = α + β₁x₁ + β₂x₂ + ... + ε
```

### Nhà đầu tư cần hiểu
Dùng regression để hỏi: indicator này có giúp phân biệt nhóm future return tốt hơn không?

### Không nên hiểu sai
Không nên thấy coefficient đẹp trong quá khứ rồi đưa ngay vào chiến lược live.


## 08. Lecture 7 — Linear Rates, Products, and Models

### Video này dạy gì
Video đi sâu vào thị trường lãi suất: benchmark rates, yield curve, forward rates, swaps, discount curve và hedging. Đây là lecture ứng dụng fixed income/rates.

### Ý phải nắm
- Lãi suất là một đường cong theo kỳ hạn, không phải một con số duy nhất.
- Interest rate swaps trao đổi dòng tiền fixed/floating.
- Curve construction và discounting quyết định định giá sản phẩm rates.

### Diễn giải
- LIBOR/SOFR và benchmark rates là nền của nhiều hợp đồng tài chính.
- Forward rate phản ánh điều kiện lãi suất hàm ý trong tương lai.
- DV01/hedging giúp đo và kiểm soát exposure khi lãi suất dịch chuyển.

### Công thức
```
Discount factor D(t)=1/(1+r_t)^t
Swap value ≈ PV(fixed leg) - PV(floating leg)
```

### Nhà đầu tư cần hiểu
Rate regime ảnh hưởng cổ phiếu qua cost of capital, thanh khoản, tín dụng, định giá sector ngân hàng/BĐS/growth.

### Không nên hiểu sai
Không xem lãi suất như biến nền khi phân tích định giá thị trường.


## 09. Lecture 8 — Regression Analysis continued

### Video này dạy gì
Video đào sâu OLS diagnostics, goodness-of-fit, residuals, statistical significance và practical pitfalls. Nó nhấn mạnh rằng fit đẹp không đồng nghĩa dự báo tốt.

### Ý phải nắm
- R² cao không đảm bảo có trading edge.
- Residual analysis giúp phát hiện model sai cấu trúc.
- Ý nghĩa thống kê phải đi cùng ý nghĩa kinh tế.

### Diễn giải
- Một coefficient có thể statistically significant nhưng lợi nhuận kỳ vọng quá nhỏ sau phí giao dịch.
- Outlier có thể làm méo regression; multicollinearity làm hệ số khó diễn giải.
- Cần kiểm mô hình trên dữ liệu ngoài mẫu và qua nhiều regime.

### Công thức
```
R² = 1 - SS_res/SS_tot
t-stat = estimate / standard_error
```

### Nhà đầu tư cần hiểu
Khi đọc một model, hãy hỏi: hiệu ứng có đủ lớn để kiếm tiền sau phí không, và có sống sót ngoài mẫu không?

### Không nên hiểu sai
Không đánh đồng p-value đẹp với chiến lược kiếm tiền.


## 10. Lecture 9 — Principal Component Analysis in Finance

### Video này dạy gì
Video giảng PCA trong finance: dùng eigen decomposition để tìm các hướng biến động chính. PCA giúp giảm chiều, phát hiện factor và xử lý dữ liệu nhiều biến.

### Ý phải nắm
- Principal components là các hướng giải thích variance lớn nhất.
- Trong yield curve, PCA thường ra level/slope/curvature.
- Trong cổ phiếu, PCA giúp tách market factor/sector factor/idiosyncratic risk.

### Diễn giải
- PCA sắp xếp thông tin theo mức độ giải thích variance.
- Nó không tự tạo alpha, nhưng giúp hiểu cấu trúc dữ liệu và tránh trùng lặp indicator.
- PCA cần diễn giải kinh tế; component toán học không phải lúc nào cũng có ý nghĩa đầu tư rõ.

### Công thức
```
Covariance matrix Σ → eigenvectors v_i, eigenvalues λ_i
PC_i = X v_i
```

### Nhà đầu tư cần hiểu
Nếu nhiều mã/indicator cùng một factor, anh đang có rủi ro tập trung ẩn.

### Không nên hiểu sai
Không dùng PCA như hộp đen; phải hiểu factor đại diện cho điều gì.


## 11. Lecture 10 — Counterparty Risk Optimization

### Video này dạy gì
Video nói về exposure, default, collateral, netting, wrong-way risk và optimization. Đây là rủi ro đối tác trong finance tổ chức, nhưng tư duy áp dụng rộng cho risk concentration.

### Ý phải nắm
- Risk không chỉ là giá đi ngược, mà còn là cấu trúc exposure.
- Wrong-way risk xảy ra khi exposure tăng đúng lúc đối tác/rủi ro xấu đi.
- Optimization phải có constraints thực tế.

### Diễn giải
- Collateral và netting giúp giảm exposure.
- Quantile/tail risk quan trọng hơn chỉ nhìn trung bình.
- Trong danh mục, rủi ro tương tự là tập trung sector, margin, thanh khoản hoặc cùng macro factor.

### Công thức
```
Expected loss ≈ Exposure × Probability of Default × Loss Given Default
```

### Nhà đầu tư cần hiểu
Hãy xem danh mục như mạng exposure: ngành, beta, thanh khoản, margin, broker, macro sensitivity.

### Không nên hiểu sai
Không nghĩ mua nhiều mã là đủ an toàn nếu tất cả cùng một nguồn rủi ro.


## 12. Lecture 11 — Regression Analysis continued

### Video này dạy gì
Video tiếp tục các vấn đề thực hành của regression: feature selection, interactions, nonlinearities, outliers và regime dependency.

### Ý phải nắm
- Feature có thể chỉ hoạt động trong một điều kiện thị trường.
- Interaction terms giúp mô hình hóa tác động phụ thuộc regime.
- Regularization/selection cần đi kèm validation.

### Diễn giải
- Ví dụ: volatility cao có thể tốt cho breakout nhưng xấu cho mean reversion.
- Một biến có thể đổi dấu tác động khi market regime đổi.
- Mô hình nên được kiểm theo thời gian, theo sector và theo volatility regime.

### Công thức
```
return ~ feature + regime + feature×regime + ε
```

### Nhà đầu tư cần hiểu
Không hỏi feature có tốt không chung chung; hỏi nó tốt trong regime nào, horizon nào, sample size bao nhiêu.

### Không nên hiểu sai
Không lấy kết quả toàn mẫu rồi áp cho mọi thị trường.


## 13. Lecture 13 — Portfolio Management

### Video này dạy gì
Video giảng expected return, covariance matrix, efficient frontier, diversification, constraints và quản lý danh mục thực tế.

### Ý phải nắm
- Danh mục tối ưu phụ thuộc return kỳ vọng và covariance.
- Diversification thật là giảm nguồn rủi ro chung, không chỉ tăng số mã.
- Constraints thực tế như thanh khoản, tỷ trọng, mandate, drawdown rất quan trọng.

### Diễn giải
- Markowitz mean-variance là khung kinh điển: tối ưu return cho một mức risk hoặc giảm risk cho một mức return.
- Efficient frontier mô tả tập danh mục không bị thống trị.
- Trong thực tế, estimation error của expected return rất lớn nên risk controls thường quan trọng hơn tối ưu quá mức.

### Công thức
```
Portfolio return = wᵀμ
Portfolio variance = wᵀΣw
```

### Nhà đầu tư cần hiểu
Chọn mã chỉ là một phần. Position size và correlation quyết định danh mục sống được hay không.

### Không nên hiểu sai
Không all-in nhiều mã cùng ngành rồi gọi là đa dạng hóa.


## 14. Lecture 14 — Stochastic Processes II

### Video này dạy gì
Video mở rộng quá trình ngẫu nhiên, continuous-time intuition, Brownian motion/path thinking và vai trò của đường đi trong finance.

### Ý phải nắm
- Terminal return không đủ; path quyết định drawdown và khả năng nắm giữ.
- Hitting time/time under water là metric quan trọng.
- Continuous-time models là nền cho derivative pricing.

### Diễn giải
- Stochastic process II chuẩn bị cho stochastic calculus và option pricing.
- Path-dependent thinking giúp hiểu vì sao cùng return cuối kỳ nhưng trải nghiệm đầu tư rất khác.
- Risk phải đo trong quá trình, không chỉ tại cuối horizon.

### Công thức
```
Path metrics: max drawdown, max runup, time-to-target, time-under-water
```

### Nhà đầu tư cần hiểu
Một chiến lược lãi 10% nhưng drawdown 25% giữa đường có thể không phù hợp.

### Không nên hiểu sai
Không chỉ nhìn return cuối kỳ rồi bỏ qua đường đi.


## 15. Lecture 12 — Time Series Analysis

### Video này dạy gì
Video giảng stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, fitting và forecast. Dữ liệu tài chính cần xử lý theo thời gian.

### Ý phải nắm
- Price thường không stationarity; return có thể gần stationarity hơn.
- AR/MA mô hình hóa phụ thuộc quá khứ và shock quá khứ.
- Horizon và regime shift quyết định độ tin cậy forecast.

### Diễn giải
- ACF/PACF giúp chọn lag structure.
- ARIMA thêm differencing để xử lý non-stationary series.
- Cointegration/pairs trading dựa trên quan hệ cân bằng dài hạn giữa chuỗi.

### Công thức
```
AR(1): X_t = c + φX_{t-1}+ε_t
MA(1): X_t = μ + ε_t + θε_{t-1}
```

### Nhà đầu tư cần hiểu
Mọi tín hiệu phải ghi rõ horizon 5d/10d/20d/60d.

### Không nên hiểu sai
Không validate time series bằng random split.


## 16. Lecture 18 — Data Science and AI for Portfolio Decisions

### Video này dạy gì
Video dùng bối cảnh biomedical portfolios để nói về quyết định đầu tư với dữ liệu phức tạp, nhiều bất định và cần AI/data science hỗ trợ.

### Ý phải nắm
- Data quality và domain knowledge quan trọng hơn model phức tạp.
- AI hỗ trợ sàng lọc và xác suất, không thay thế judgment.
- Portfolio decision cần kết hợp model với risk management.

### Diễn giải
- Biomedical investing có nhiều biến cố bất định, tương tự event-driven investing.
- AI có thể giúp tổng hợp tín hiệu nhưng cần validation và explainability.
- Adaptive thinking quan trọng vì môi trường và edge thay đổi.

### Công thức
```
Model usefulness = data quality × validation quality × domain relevance
```

### Nhà đầu tư cần hiểu
Dùng AI như trợ lý phân tích xác suất/rủi ro, không như máy phán chắc chắn.

### Không nên hiểu sai
Không train ML từ dữ liệu bẩn rồi tin kết quả vì model nghe hiện đại.


## 17. Lecture 19 — Volatility Modeling

### Video này dạy gì
Video giảng realized volatility, implied volatility, volatility clustering và ARCH/GARCH intuition. Volatility là biến trung tâm của risk và option pricing.

### Ý phải nắm
- Volatility thay đổi theo thời gian và có clustering.
- Vol cao vừa tăng cơ hội hit target vừa tăng drawdown.
- Volatility phải ảnh hưởng stop-loss và position sizing.

### Diễn giải
- Realized vol đo biến động thực tế từ returns.
- GARCH-style models cho variance phụ thuộc shock/variance quá khứ.
- Implied vol phản ánh kỳ vọng/giá thị trường option.

### Công thức
```
RealizedVol = std(returns)×√252
ATR% = ATR/Close
GARCH: σ_t² = ω + αε_{t-1}² + βσ_{t-1}²
```

### Nhà đầu tư cần hiểu
Không đặt cùng stop/size cho mã ATR 1.5% và mã ATR 5%.

### Không nên hiểu sai
Không xem volatility cao đơn giản là tín hiệu mua hoặc bán.


## 18. Lecture 21 — Black-Scholes Formula, Risk Neutral Valuation

### Video này dạy gì
Video giảng option pricing, Black-Scholes PDE/formula, risk-neutral valuation và Greeks. Đây là nền cho hiểu option và chứng quyền.

### Ý phải nắm
- Option price phụ thuộc S, K, T, r, σ.
- Risk-neutral valuation là kỹ thuật pricing no-arbitrage.
- Greeks đo các độ nhạy chính của option.

### Diễn giải
- Delta hedging dẫn tới Black-Scholes PDE trong khung giả định.
- Theta/time decay làm option mất giá theo thời gian nếu yếu tố khác không đổi.
- Volatility ảnh hưởng mạnh đến option value qua Vega.

### Công thức
```
C = S N(d1) - K e^{-rT} N(d2)
Inputs: S,K,T,r,σ
Greeks: Delta, Gamma, Vega, Theta
```

### Nhà đầu tư cần hiểu
Với CW, đúng underlying chưa đủ; cần maturity, spread, break-even, liquidity, theta, implied vol.

### Không nên hiểu sai
Không chọn CW chỉ vì leverage cao.


## 19. Lecture 20 — Regulated Exchange for Event Contracts

### Video này dạy gì
Video nói về event contracts và prediction markets: sản phẩm có payoff phụ thuộc sự kiện xảy ra hay không.

### Ý phải nắm
- Event contracts biến xác suất sự kiện thành giá giao dịch.
- Regulation/settlement rule quyết định sản phẩm có giao dịch được không.
- Event risk khác với risk biến động liên tục.

### Diễn giải
- Kalshi/event exchange là ví dụ thị trường giao dịch xác suất của biến cố.
- Trong cổ phiếu, event gồm KQKD, chính sách, pháp lý, nâng hạng, cổ tức, M&A.
- Technical pattern có thể bị phá bởi event lớn.

### Công thức
```
Event price ≈ market-implied probability (sau điều chỉnh margin/cost)
```

### Nhà đầu tư cần hiểu
Cần đánh dấu event risk riêng thay vì chỉ dùng chart/indicator.

### Không nên hiểu sai
Không dùng backtest bình thường để bỏ qua rủi ro sự kiện.


## 20. Lecture 23 — Introduction to Machine Learning

### Video này dạy gì
Video giới thiệu supervised learning, feature, label, train/test, classification/regression, overfitting, evaluation và ML trong finance.

### Ý phải nắm
- Label phải rõ: dự báo gì, horizon nào.
- Train/test phải tách theo thời gian trong finance.
- Model cần calibration và explainability.

### Diễn giải
- Classification có thể dự báo hit target; regression dự báo return.
- Overfitting là rủi ro lớn vì financial data nhiễu và non-stationary.
- Baseline đơn giản phải được so sánh trước khi tin model phức tạp.

### Công thức
```
features X → model f(X) → probability/return estimate
Calibration: predicted 60% ≈ realized 60%
```

### Nhà đầu tư cần hiểu
ML nên tạo xác suất/ranking, không thay thế quyết định risk.

### Không nên hiểu sai
Không random split hoặc tối ưu toàn mẫu rồi gọi là AI thông minh.


## 21. Lecture 24 — Stochastic Calculus

### Video này dạy gì
Video giới thiệu Brownian motion/Wiener process, Itô integral và Itô’s Lemma. Đây là nền toán cho derivatives và continuous-time finance.

### Ý phải nắm
- Stochastic calculus khác calculus thường do quadratic variation.
- Itô’s Lemma là chain rule cho quá trình ngẫu nhiên.
- Nền này dẫn tới option pricing và SDE.

### Diễn giải
- Brownian motion mô tả nhiễu liên tục với increments normal độc lập.
- Itô integral định nghĩa tích phân với process ngẫu nhiên.
- Itô’s Lemma có thêm second-order term, rất quan trọng trong Black-Scholes.

### Công thức
```
dX = μdt + σdW
df = f_t dt + f_x dX + 0.5 f_xx (dX)^2
```

### Nhà đầu tư cần hiểu
Không cần tính Itô hàng ngày, nhưng cần hiểu vì sao option/volatility models không đơn giản như đường thẳng.

### Không nên hiểu sai
Không áp stochastic calculus vào stock picking cơ bản nếu chưa cần.


## 22. Lecture 25 — Stochastic Calculus continued; SDE

### Video này dạy gì
Video tiếp tục stochastic calculus với stochastic differential equations, đặc biệt mô hình dạng drift + diffusion như geometric Brownian motion.

### Ý phải nắm
- SDE mô hình biến tài chính bằng drift và shock ngẫu nhiên.
- GBM là nền Black-Scholes nhưng không hoàn hảo.
- Mô phỏng scenario hữu ích hơn dự báo một đường duy nhất.

### Diễn giải
- dS = μSdt + σSdW mô tả giá có tăng trưởng kỳ vọng và nhiễu tỷ lệ với giá.
- Thực tế có volatility stochastic, jumps, fat tails, regime shifts.
- SDE giúp tư duy về phân phối kịch bản và path risk.

### Công thức
```
dS = μSdt + σSdW
S_t = S_0 exp((μ-0.5σ²)t + σW_t)
```

### Nhà đầu tư cần hiểu
Hãy nghĩ theo base/bull/bear/shock/gap scenario, đặc biệt khi đánh CW hoặc sản phẩm có thời gian.

### Không nên hiểu sai
Không tin một forecast path duy nhất như tương lai chắc chắn.
