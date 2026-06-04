MIT 18.642
Topics in Mathematics with Applications in Finance
Training Guide dành cho Nhà đầu tư Chứng khoán & hệ thống LH Investment
Fall 2024 · Massachusetts Institute of Technology · 22 public video transcripts processed
Nguồn | MIT 18.642 Fall 2024 public playlist transcripts
Mục tiêu | Biến kiến thức toán tài chính thành feature, backtest, risk rule, portfolio logic và CW scoring
Cách đọc | Bài học gốc trước → ý nghĩa đầu tư → áp dụng vào LH Investment
Nguyên tắc đỏ | No look-ahead · OOS/walk-forward · Expected Value · Regime-aware · Risk-first
Prepared by Tiểu đệ for Hòa Đại ka

# MỤC LỤC TỔNG QUAN

Module | Nội dung | Lecture
Module 1 | Giới thiệu khóa học & thị trường tài chính | Lecture 1 Parts I–III
Module 2 | Bond Math — lãi suất, chiết khấu, duration, convexity | Lecture 1 Part III
Module 3 | Linear Algebra trong tài chính | Lecture 2 + 4
Module 4 | Probability & Stochastic Processes I | Lecture 4 + 5 + 6
Module 5 | Regression Analysis & PCA | Lecture 6 + 8 + 9 + 11
Module 6 | Rates products & fixed income models | Lecture 7
Module 7 | Time Series Analysis | Lecture 12
Module 8 | Portfolio, Counterparty Risk & Risk Optimization | Lecture 10 + 13
Module 9 | Volatility Modeling | Lecture 19
Module 10 | Black-Scholes, Options & CW | Lecture 21
Module 11 | AI, Machine Learning & Event Markets | Lecture 18 + 20 + 23
Module 12 | Stochastic Calculus & SDE | Lecture 14 + 24 + 25
Module 13 | Roadmap training model LH Investment | Ứng dụng tổng hợp

# EXECUTIVE SUMMARY — ANH CẦN NHỚ GÌ?

**MIT 18.642 không dạy đi tìm một chỉ báo thần kỳ.** Khóa học dạy cách biến thị trường thành bài toán xác suất, dòng tiền, thời gian, rủi ro, danh mục và kiểm định định lượng.
Với LH Investment, bài học cốt lõi là chuyển từ “indicator + cảm tính” sang “feature matrix + probability + expected value + regime + risk-adjusted ranking”.
• Mọi tín hiệu phải có horizon: 5d/10d/20d/60d.
• Mọi backtest phải tránh look-ahead bias.
• Win rate không đủ; phải có expected value, avgWin, avgLoss.
• Model phải biết nó sai khi nào: wrongIf/invalidation.
• Không dùng ML phức tạp trước khi feature/backtest cơ bản sạch.

# MODULE 1 — GIỚI THIỆU KHÓA HỌC & THỊ TRƯỜNG TÀI CHÍNH

**Nguồn:** Lecture 1 Parts I–II–III

## 1. Bài học gốc

Khóa học đặt nền: tài chính là hệ thống các tài sản, dòng tiền, rủi ro, xác suất và định giá. Investor không nên hỏi “mã này chắc tăng không”, mà hỏi xác suất, payoff, drawdown, thanh khoản, chi phí và bối cảnh thị trường.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Tài sản | claim trên dòng tiền/trạng thái tương lai
Return | lợi nhuận phải đi cùng risk
Arbitrage | neo logic định giá
Market structure | thanh khoản/chi phí/slippage quan trọng

## 3. Áp dụng vào LH Investment

• Thêm liquidityScore, marketRegime, sectorRegime, slippageRisk.
• Output khuyến nghị phải có why/wrongIf/horizon/risk.
• Không chỉ hiển thị indicator; phải hỗ trợ quyết định.

# MODULE 2 — BOND MATH: LÃI SUẤT, CHIẾT KHẤU, DURATION

**Nguồn:** Lecture 1 Part III — Vasily Strela

## 1. Bài học gốc

Bond math dạy quy đổi dòng tiền tương lai về hiện tại. Lãi suất là trọng lực của tài chính: rate tăng thì present value giảm, đặc biệt với tài sản duration dài như cổ phiếu tăng trưởng.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
PV | CF/(1+r)^t
Bond Price | PV coupons + PV principal
Duration | độ nhạy giá với yield
Convexity | sửa sai số duration khi yield đổi lớn

## 3. Áp dụng vào LH Investment

• Thêm rateSensitiveScore, valuationDurationRisk, peCompressionRisk.
• Cổ phiếu growth/P/E cao cần cảnh báo khi rate regime xấu.
• CW/option phải tính time value và discounting.

# MODULE 3 — LINEAR ALGEBRA TRONG TÀI CHÍNH

**Nguồn:** Lecture 2 + 4

## 1. Bài học gốc

Linear algebra là ngôn ngữ của dữ liệu nhiều chiều: mỗi cổ phiếu/ngày là một vector feature; toàn bộ VN100 theo thời gian là matrix để regression, PCA, ML và portfolio optimization.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Vector | hồ sơ 1 mã tại 1 ngày
Matrix | stock-date × features
Covariance | biến động chung
Eigen/PCA | factor chính trong dữ liệu

## 3. Áp dụng vào LH Investment

• Duy trì research_feature_matrix_vn100.json.
• Chuẩn hóa feature groups: trend/momentum/volume/volatility/SR/pattern/regime.
• Không training ML từ các cache rời rạc thiếu schema.

# MODULE 4 — PROBABILITY & STOCHASTIC PROCESSES

**Nguồn:** Lecture 4 + 5 + 6

## 1. Bài học gốc

Giá cổ phiếu là quá trình ngẫu nhiên theo thời gian, không phải điểm dự báo đơn lẻ. Tín hiệu chỉ làm thay đổi xác suất có điều kiện, không bảo đảm kết quả.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Conditional Probability | P(kết quả | setup)
Expectation | lợi nhuận kỳ vọng
Variance | rủi ro/phân tán
Stochastic Process | chuỗi biến ngẫu nhiên theo thời gian

## 3. Áp dụng vào LH Investment

• Mỗi setup phải có pHitTarget20d, pLossMoreThan5Pct20d.
• Validation phải chronological/walk-forward, không random shuffle.
• Feature tại t chỉ dùng dữ liệu <= t.

# MODULE 5 — REGRESSION ANALYSIS & PCA

**Nguồn:** Lecture 6 + 8 + 9 + 11

## 1. Bài học gốc

Regression kiểm định feature nào thực sự liên quan future return. PCA/correlation giúp loại chỉ báo trùng thông tin và tìm factor thật.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
OLS | ước lượng quan hệ tuyến tính
Residual | phần model không giải thích
Multicollinearity | feature trùng gây méo hệ số
PCA | giảm chiều/tìm factor

## 3. Áp dụng vào LH Investment

• Chạy Spearman/top-bottom quintile/OOS.
• Tạo feature_correlation_report và indicator_factor_groups.
• Pattern score chỉ là overlay nếu chưa chứng minh OOS.

# MODULE 6 — LINEAR RATES, PRODUCTS & MODELS

**Nguồn:** Lecture 7 — Mizuho/Rates

## 1. Bài học gốc

Rates products và yield curve cho thấy định giá phụ thuộc toàn bộ đường cong lãi suất, không chỉ một con số rate.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Yield curve | cấu trúc lãi suất theo kỳ hạn
Forward rate | lãi suất hàm ý tương lai
Swap | trao đổi dòng tiền lãi suất
Hedging | giảm rủi ro thay vì đoán hướng

## 3. Áp dụng vào LH Investment

• Thêm macroRateRegime/yieldCurveProxy khi có data.
• Sector ngân hàng/BĐS/growth cần phản ứng khác nhau với rate.
• Dùng regime macro làm filter, không làm tín hiệu đơn độc.

# MODULE 7 — TIME SERIES ANALYSIS

**Nguồn:** Lecture 12

## 1. Bài học gốc

Time series nhấn mạnh autocorrelation, stationarity, trend, regime shift. Một feature có thể đúng horizon 5d nhưng sai horizon 60d.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
AR/MA/ARMA | mô hình phụ thuộc quá khứ
Stationarity | tính ổn định thống kê
Regime shift | thị trường đổi luật chơi
Forecast horizon | khung thời gian dự báo

## 3. Áp dụng vào LH Investment

• Mọi output phải có horizon.
• Backtest tách 5/10/20/60d.
• Không gom mọi horizon vào một score mơ hồ.

# MODULE 8 — PORTFOLIO & COUNTERPARTY/RISK OPTIMIZATION

**Nguồn:** Lecture 10 + 13

## 1. Bài học gốc

Danh mục không chỉ là chọn mã tốt. Risk phụ thuộc covariance, correlation, sector exposure, liquidity và constraints.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Expected return vector | lợi nhuận kỳ vọng từng tài sản
Covariance matrix | mức độ đi cùng nhau
Efficient frontier | return/risk tối ưu
Concentration risk | rủi ro tập trung

## 3. Áp dụng vào LH Investment

• Thêm positionSizeHint, sectorCapWarning, correlationWarning.
• Mua 5 mã cùng ngành không phải diversification.
• Size = confidence × volatility × regime × liquidity.

# MODULE 9 — VOLATILITY MODELING

**Nguồn:** Lecture 19

## 1. Bài học gốc

Volatility thay đổi theo thời gian và có clustering. Vol cao vừa là cơ hội vừa là nguy hiểm.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Realized volatility | biến động thực tế
ATR% | biên dao động thực dụng
Vol clustering | vol cao thường kéo dài
GARCH intuition | vol động theo shock quá khứ

## 3. Áp dụng vào LH Investment

• Dùng atrPct/realizedVol20/bbWidth20.
• Vol cao không tự động xấu; dùng cho sizing/stop/risk.
• Backtest phải báo maxDrawdownAfterEntry.

# MODULE 10 — BLACK-SCHOLES, OPTIONS & CW

**Nguồn:** Lecture 21

## 1. Bài học gốc

Option/CW phụ thuộc underlying, strike, time, rate, volatility. Cổ phiếu cơ sở tăng chưa chắc CW tốt nếu time decay/spread/break-even xấu.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
S | giá tài sản cơ sở
K | giá thực hiện
T | thời gian còn lại
σ | volatility
Greeks | Delta/Gamma/Vega/Theta

## 3. Áp dụng vào LH Investment

• CW score = underlyingSignal + maturity + moneyness + breakEven + spread + liquidity + theta.
• Không rank CW theo leverage đơn thuần.
• Cảnh báo CW gần đáo hạn/spread rộng.

# MODULE 11 — AI, MACHINE LEARNING & EVENT MARKETS

**Nguồn:** Lecture 18 + 20 + 23

## 1. Bài học gốc

ML chỉ tốt khi dữ liệu/label/validation tốt. Event markets nhắc ta quy đổi biến cố thành xác suất.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Label | mục tiêu training
OOS | kiểm ngoài mẫu
Calibration | xác suất có đáng tin không
Event probability | giá/xác suất biến cố

## 3. Áp dụng vào LH Investment

• ML đầu tiên: logistic regression/GBM nhẹ.
• Output pHitTarget và pLoss, không phán chắc.
• Tin/event cần eventRiskFlag riêng.

# MODULE 12 — STOCHASTIC CALCULUS & SDE

**Nguồn:** Lecture 14 + 24 + 25

## 1. Bài học gốc

Stochastic calculus là nền cho option/volatility/path modeling. Với stock ranking hằng ngày, dùng như tư duy scenario và risk path.

## 2. Khái niệm cần nhớ

Khái niệm | Ý nghĩa
Brownian motion | nhiễu liên tục
Ito lemma | đạo hàm cho quá trình ngẫu nhiên
SDE | dS = μSdt + σSdW
Path risk | đường đi quan trọng không kém điểm cuối

## 3. Áp dụng vào LH Investment

• Thêm scenario: bull/base/bear/stop/gap.
• Tính timeToTarget/timeUnderWater nếu backtest.
• Không ép SDE phức tạp vào model nếu chưa cần.

# MODULE 13 — ROADMAP TRAINING MODEL LH INVESTMENT

Khi Hòa Đại ka bảo “em tự training model đi”, Tiểu đệ phải làm theo pipeline này, không nhảy thẳng vào ML.
Phase | Việc làm | Output
1. Data | Cập nhật OHLCV, market/sector, pattern, SR | raw cache sạch
2. Feature Matrix | Tạo feature tại từng stock-date, past-only | research_feature_matrix_vn100.json
3. Leakage Audit | Kiểm rolling windows, label tách riêng | leakage_audit.md
4. Feature Report | Correlation, top/bottom quintile, regime | research_feature_training_report.json
5. Strategy Backtest | Rule rõ ràng, chronological OOS | EV/avgWin/avgLoss/profitFactor
6. Risk Layer | ATR stop, position sizing, sector/correlation | risk_adjusted_recommendations.json
7. ML nhẹ | Logistic/GBM, calibrated probability | pHitTarget/pLoss/modelConfidence
8. Production | Chỉ deploy khi anh cho phép | Firebase/cache update

## Bảng output bắt buộc cho recommendation

{
  "symbol": "MWG",
  "horizon": "20d",
  "setup": "near_support_room_to_resistance",
  "pHitTarget6Pct": 0.0,
  "pLossMoreThan5Pct": 0.0,
  "expectedValue": 0.0,
  "avgWin": 0.0,
  "avgLoss": 0.0,
  "profitFactor": 0.0,
  "sampleSize": 0,
  "marketRegime": "",
  "volRegime": "",
  "positionSizeHint": "",
  "why": "",
  "wrongIf": ""
}

## Kết luận thực chiến

Bước đáng làm nhất hiện tại: **build rolling support/resistance features lịch sử**, sau đó backtest setup gần hỗ trợ + còn room tới kháng cự + volatility filter + market regime filter.