# MIT 18.642 — Bài giảng chuyên nghiệp cho nhà đầu tư


## 01. Mở khóa học: Tài chính định lượng là gì?
Nguồn: Lecture 1 Part I

### Mở bài
Mục tiêu của video đầu tiên là đặt bối cảnh: tài chính hiện đại không chỉ dựa vào cảm giác thị trường, mà dựa vào khả năng mô hình hóa dữ liệu, rủi ro và quyết định. Giảng viên giới thiệu tinh thần của MIT 18.642: dùng toán để hiểu sản phẩm tài chính, xây mô hình, kiểm định và ứng dụng trong thực tế.

### Giảng cho nhà đầu tư
Sau bài này, anh cần hiểu: mô hình là công cụ, không phải lời tiên tri. Một nhà đầu tư giỏi không hỏi “chắc tăng không?”, mà hỏi “xác suất bao nhiêu, lời/lỗ kỳ vọng thế nào, sai khi nào?”.

### Công thức
```
Expected Value = P(thắng) × Lãi trung bình - P(thua) × Lỗ trung bình - Chi phí
```

### Takeaway
Hãy xem mọi khuyến nghị đầu tư như một giả thuyết cần kiểm định.


## 02. Bản đồ thị trường tài chính
Nguồn: Lecture 1 Part II

### Mở bài
Video này giải thích các loại tài sản và thuật ngữ nền: cổ phiếu, trái phiếu, phái sinh, quỹ, hàng hóa, tiền tệ, rủi ro, lợi nhuận, thanh khoản và cấu trúc thị trường. Đây là phần giúp người học biết mình đang phân tích loại payoff nào.

### Giảng cho nhà đầu tư
Cổ phiếu là quyền sở hữu doanh nghiệp. Trái phiếu là công cụ nợ. Phái sinh là hợp đồng phụ thuộc tài sản cơ sở. Mỗi loại có cách sinh lời, rủi ro và cách định giá khác nhau.

### Công thức
```
Return phải luôn đi kèm Risk, Liquidity và Cost
```

### Takeaway
Đừng dùng một cách phân tích duy nhất cho cổ phiếu, trái phiếu và chứng quyền.


## 03. Bond Math: lãi suất là trọng lực của định giá
Nguồn: Lecture 1 Part III

### Mở bài
Bài này giảng present value, discounting, yield, duration và convexity. Ý tưởng rất quan trọng: tiền trong tương lai phải được chiết khấu về hiện tại. Khi lãi suất tăng, giá trị hiện tại của dòng tiền giảm.

### Giảng cho nhà đầu tư
Dù ví dụ là trái phiếu, tư duy này áp dụng cho mọi tài sản. Cổ phiếu tăng trưởng có dòng tiền xa tương lai nên rất nhạy với lãi suất. Duration giúp đo độ nhạy đó.

### Công thức
```
PV = CF/(1+r)^t
%ΔPrice ≈ -Duration × ΔYield
```

### Takeaway
Khi lãi suất đổi, định giá thị trường đổi — kể cả doanh nghiệp chưa đổi.


## 04. Linear Algebra: đưa thị trường về vector và ma trận
Nguồn: Lecture 2

### Mở bài
Video này giảng vector, matrix, linear combination, eigenvalues/eigenvectors và vai trò của đại số tuyến tính trong tài chính. Dữ liệu thị trường nhiều chiều nên phải được biểu diễn thành ma trận.

### Giảng cho nhà đầu tư
Một cổ phiếu trong một ngày là một vector đặc trưng. Một danh mục là tổ hợp tuyến tính. Nhiều mã trong nhiều ngày tạo thành ma trận để hồi quy, PCA, tối ưu danh mục và ML.

### Công thức
```
x = [return, volatility, liquidity, factor exposure]
X = observations × features
```

### Takeaway
Muốn model tốt, trước tiên phải có ma trận dữ liệu sạch.


## 05. Xác suất: đầu tư là trò chơi phân phối kết quả
Nguồn: Lecture 4

### Mở bài
Video nối đại số tuyến tính với xác suất: random variable, distribution, expectation, variance, covariance và correlation. Đây là nền để hiểu return và risk.

### Giảng cho nhà đầu tư
Một quyết định đầu tư không tạo ra một kết quả chắc chắn; nó tạo ra một phân phối kết quả. Kỳ vọng cao nhưng tail risk lớn vẫn có thể nguy hiểm.

### Công thức
```
E[R] = Σ pᵢrᵢ
Var(R) = E[(R-E[R])²]
```

### Takeaway
Đừng chỉ nhìn lợi nhuận trung bình; hãy nhìn phân phối và rủi ro đuôi.


## 06. Stochastic Process: giá là một đường đi ngẫu nhiên
Nguồn: Lecture 5

### Mở bài
Video chuyển từ biến ngẫu nhiên sang quá trình ngẫu nhiên: random walk, martingale, Markov chain, gambler’s ruin. Giá tài sản là chuỗi biến động theo thời gian.

### Giảng cho nhà đầu tư
Điểm cuối không đủ. Đường đi quyết định drawdown, khả năng chịu đựng và nguy cơ cháy vốn. Gambler’s ruin nhắc rằng quản trị vốn sai có thể phá hủy cả chiến lược có edge.

### Công thức
```
P₀, P₁, P₂, ... Pₜ
```

### Takeaway
Trong trading, path risk quan trọng không kém target.


## 07. Regression I: kiểm định quan hệ giữa feature và return
Nguồn: Lecture 6

### Mở bài
Video bắt đầu hồi quy: y = a + bx + error. Regression giúp kiểm tra biến giải thích có liên quan biến mục tiêu không.

### Giảng cho nhà đầu tư
Trong tài chính, hồi quy hữu ích để kiểm feature, nhưng không phải công thức chắc thắng. Error lớn, noise lớn, outlier và regime change làm mô hình dễ sai.

### Công thức
```
futureReturn = a + b₁feature₁ + b₂feature₂ + error
```

### Takeaway
Regression trả lời “feature có thông tin không?”, không trả lời “chắc mua được không?”.


## 08. Rates Products: đường cong lãi suất và sản phẩm rates
Nguồn: Lecture 7

### Mở bài
Video đi vào SOFR/LIBOR, yield curve, forwards, swaps và discount curve. Đây là phần fixed income/rates chuyên sâu.

### Giảng cho nhà đầu tư
Đường cong lãi suất thể hiện giá vốn theo từng kỳ hạn. Các sản phẩm rates dùng curve để định giá và hedge. Với cổ phiếu, rate regime ảnh hưởng thanh khoản, định giá và sector rotation.

### Công thức
```
Discount Factor = 1/(1+rₜ)^t
```

### Takeaway
Thị trường cổ phiếu không tách rời môi trường lãi suất.


## 09. Regression II: diagnostics, residuals và overfit
Nguồn: Lecture 8

### Mở bài
Video đào sâu OLS, goodness of fit, residuals, statistical significance và practical pitfalls. Một mô hình fit quá khứ tốt chưa chắc dự báo tốt.

### Giảng cho nhà đầu tư
Cần phân biệt ý nghĩa thống kê và ý nghĩa kinh tế. Một coefficient có p-value đẹp nhưng payoff quá nhỏ sau phí thì không đáng dùng.

### Công thức
```
R² cao ≠ trading edge cao
```

### Takeaway
Out-of-sample quan trọng hơn vẻ đẹp in-sample.


## 10. PCA: tìm factor chính và bớt ảo giác indicator
Nguồn: Lecture 9

### Mở bài
Video giảng Principal Component Analysis trong finance. PCA tìm các hướng biến động chính trong dữ liệu bằng eigenvectors/eigenvalues.

### Giảng cho nhà đầu tư
Trong yield curve, PCA có thể cho level/slope/curvature. Trong cổ phiếu, PCA giúp thấy market factor, sector factor và loại trùng lặp indicator.

### Công thức
```
X ≈ PC1 + PC2 + ... + noise
```

### Takeaway
Nhiều tín hiệu cùng một factor không phải nhiều bằng chứng độc lập.


## 11. Counterparty Risk: rủi ro nằm trong exposure
Nguồn: Lecture 10

### Mở bài
Video nói về counterparty risk, exposure, collateral, netting, wrong-way risk và optimization. Đây là tư duy risk ở cấp tổ chức.

### Giảng cho nhà đầu tư
Với nhà đầu tư cá nhân, bài học là concentration risk: quá tập trung một ngành, một broker, margin hoặc một macro factor. Risk không chỉ nằm ở từng mã riêng lẻ.

### Công thức
```
Risk = exposure × probability × loss severity
```

### Takeaway
Hãy quản lý cấu trúc rủi ro, không chỉ từng lệnh.


## 12. Regression III: feature interaction và regime
Nguồn: Lecture 11

### Mở bài
Video tiếp tục hồi quy với lựa chọn biến, outlier, interaction, phi tuyến và ổn định hệ số. Một feature có thể chỉ hoạt động trong một regime.

### Giảng cho nhà đầu tư
Ví dụ volatility cao có thể tốt cho breakout nhưng xấu cho mean reversion. Vì vậy phải kiểm feature theo bull/bear/sideway/high-vol.

### Công thức
```
return ~ feature + regime + feature×regime
```

### Takeaway
Feature tốt phải ổn định theo thời gian và có ý nghĩa kinh tế.


## 13. Portfolio Management: chọn mã chỉ là nửa đầu
Nguồn: Lecture 13

### Mở bài
Video giảng expected return, covariance matrix, diversification, efficient frontier và constraints thực tế.

### Giảng cho nhà đầu tư
Một danh mục nhiều mã vẫn có thể rủi ro nếu các mã cùng sector/factor. Phân bổ vốn, correlation và volatility quyết định risk thật.

### Công thức
```
Portfolio Variance = wᵀΣw
```

### Takeaway
Không chỉ hỏi mua mã nào; hãy hỏi mua bao nhiêu và rủi ro danh mục là gì.


## 14. Stochastic Processes II: path, hitting time và drawdown
Nguồn: Lecture 14

### Mở bài
Video mở rộng quá trình ngẫu nhiên, nhấn mạnh continuous-time intuition và path dependence.

### Giảng cho nhà đầu tư
Một chiến lược có thể lời cuối kỳ nhưng drawdown giữa đường quá sâu. Vì thế phải đo max drawdown, time under water, time to target.

### Công thức
```
Path matters, not only terminal value
```

### Takeaway
Đường đi của lệnh quyết định khả năng nắm giữ thực tế.


## 15. Time Series: horizon và regime shift
Nguồn: Lecture 12

### Mở bài
Video giảng AR, MA, ARMA, stationarity, autocorrelation và forecast. Dữ liệu tài chính là chuỗi thời gian nhiễu và dễ đổi regime.

### Giảng cho nhà đầu tư
Một tín hiệu có thể hiệu quả trong 5 ngày nhưng không hiệu quả trong 60 ngày. Không được random split khi validate time series.

### Công thức
```
Rₜ = a + bRₜ₋₁ + error
```

### Takeaway
Mọi khuyến nghị phải gắn horizon rõ ràng.


## 16. AI/Data Science cho quyết định portfolio
Nguồn: Lecture 18

### Mở bài
Video dùng ví dụ biomedical portfolio để nói về AI/data science trong quyết định nhiều bất định.

### Giảng cho nhà đầu tư
Bài học chung: model tốt cần data tốt, label rõ, domain knowledge và risk management. AI không thay thế tư duy đầu tư.

### Công thức
```
Data quality > model complexity
```

### Takeaway
AI là công cụ hỗ trợ xác suất, không phải máy phán chắc chắn.


## 17. Volatility Modeling: biến động là biến sống
Nguồn: Lecture 19

### Mở bài
Video giảng realized volatility, volatility clustering, ARCH/GARCH intuition và vai trò volatility trong risk/pricing.

### Giảng cho nhà đầu tư
Volatility không cố định. Sau cú sốc, vol thường duy trì cao. Vol cao vừa tạo cơ hội hit target vừa tăng drawdown.

### Công thức
```
RealizedVol = std(returns) × √252
ATR% = ATR/Close
```

### Takeaway
Stop-loss và position size phải theo volatility.


## 18. Black-Scholes: hiểu option và chứng quyền
Nguồn: Lecture 21

### Mở bài
Video giảng Black-Scholes, risk-neutral valuation và option pricing. Option phụ thuộc S, K, T, r, σ.

### Giảng cho nhà đầu tư
Cổ phiếu cơ sở tăng chưa chắc CW lời nếu time decay, spread, break-even hoặc volatility bất lợi. Greeks giúp hiểu độ nhạy option.

### Công thức
```
Call = S N(d1) - K e^{-rT}N(d2)
```

### Takeaway
Với CW, hướng đúng chưa đủ; thời gian và volatility quyết định lớn.


## 19. Event Contracts: xác suất của biến cố
Nguồn: Lecture 20

### Mở bài
Video nói về event contracts và sàn giao dịch sự kiện được quản lý. Payoff phụ thuộc sự kiện xảy ra hay không.

### Giảng cho nhà đầu tư
Bài này giúp nhà đầu tư hiểu các rủi ro dạng binary: KQKD, chính sách, pháp lý, cổ tức, nâng hạng. Event risk cần mô hình riêng.

### Công thức
```
Price ≈ market-implied probability of event
```

### Takeaway
Không dùng technical backtest bình thường để bỏ qua event lớn.


## 20. Machine Learning: học từ dữ liệu nhưng dễ overfit
Nguồn: Lecture 23

### Mở bài
Video giới thiệu supervised learning, feature, label, train/test, classification, regression và overfitting.

### Giảng cho nhà đầu tư
Trong tài chính, ML rất dễ overfit vì dữ liệu nhiễu và regime đổi. Model nên xuất probability/ranking, không xuất chắc chắn.

### Công thức
```
Model: features → prediction/probability
```

### Takeaway
ML chỉ đáng tin khi validation theo thời gian và calibration tốt.


## 21. Stochastic Calculus I: toán cho ngẫu nhiên liên tục
Nguồn: Lecture 24

### Mở bài
Video giới thiệu Brownian motion, Wiener process và Ito calculus. Đây là nền cho option pricing và continuous-time finance.

### Giảng cho nhà đầu tư
Khác calculus thường, quá trình ngẫu nhiên có quadratic variation nên cần Ito lemma để xử lý hàm của random process.

### Công thức
```
Ito Lemma: df(Xₜ,t) includes drift + diffusion + second-order term
```

### Takeaway
Không cần dùng Ito hằng ngày, nhưng cần hiểu nền của option/volatility.


## 22. SDE: mô hình hóa drift và shock
Nguồn: Lecture 25

### Mở bài
Video tiếp tục stochastic calculus với stochastic differential equations. Mô hình cổ điển: dS = μSdt + σSdW.

### Giảng cho nhà đầu tư
SDE cho thấy giá gồm drift kỳ vọng và shock ngẫu nhiên. Thực tế có volatility thay đổi, jump và fat tail, nên không nên tin một đường dự báo duy nhất.

### Công thức
```
dS = μSdt + σSdW
```

### Takeaway
Hãy nghĩ theo phân phối kịch bản: base, bull, bear, shock, gap risk.
