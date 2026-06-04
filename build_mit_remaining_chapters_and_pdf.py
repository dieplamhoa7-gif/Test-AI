from pathlib import Path
import re

REPORTS = Path('reports')
REPORTS.mkdir(exist_ok=True)

chapters = {}

chapters['MIT_18_642_Chuong_03_Regression_TimeSeries_PCA_VI.md'] = r'''# Chương 3 — Regression, Time Series và PCA: kiểm định tín hiệu cổ phiếu

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
'''

chapters['MIT_18_642_Chuong_04_Portfolio_Risk_Volatility_VI.md'] = r'''# Chương 4 — Portfolio, Risk và Volatility: từ chọn mã sang quản trị danh mục

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
'''

chapters['MIT_18_642_Chuong_05_Derivatives_BlackScholes_CW_VI.md'] = r'''# Chương 5 — Derivatives, Black-Scholes và Chứng quyền/CW

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
'''

chapters['MIT_18_642_Chuong_06_MachineLearning_StochasticCalculus_Roadmap_VI.md'] = r'''# Chương 6 — Machine Learning, Stochastic Calculus và lộ trình áp dụng

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
'''

for name, content in chapters.items():
    (REPORTS/name).write_text(content, encoding='utf-8')
    print('wrote', REPORTS/name)

# Build combined markdown
chapter_files = [
    'MIT_18_642_Chuong_01_Lecture_1_VI.md',
    'MIT_18_642_Chuong_02_Linear_Algebra_Probability_VI.md',
    'MIT_18_642_Chuong_03_Regression_TimeSeries_PCA_VI.md',
    'MIT_18_642_Chuong_04_Portfolio_Risk_Volatility_VI.md',
    'MIT_18_642_Chuong_05_Derivatives_BlackScholes_CW_VI.md',
    'MIT_18_642_Chuong_06_MachineLearning_StochasticCalculus_Roadmap_VI.md',
]
combined = ['# Hướng dẫn học MIT 18.642 bằng tiếng Việt cho Hòa Đại ka\n', 'Mục tiêu: biến kiến thức toán tài chính thành quy tắc cụ thể cho model, backtest, quản trị rủi ro và danh mục LH Investment.\n']
for f in chapter_files:
    combined.append((REPORTS/f).read_text(encoding='utf-8'))
combined_path = REPORTS/'MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment.md'
combined_path.write_text('\n\n---\n\n'.join(combined), encoding='utf-8')
print('wrote', combined_path)

# PDF with ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_candidates = [
    r'C:\Windows\Fonts\arial.ttf',
    r'C:\Windows\Fonts\calibri.ttf',
    r'C:\Windows\Fonts\segoeui.ttf',
]
font = 'Helvetica'
for fp in font_candidates:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFont', fp))
        font = 'VNFont'
        break

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='VNTitle', parent=styles['Title'], fontName=font, fontSize=20, leading=26, spaceAfter=16))
styles.add(ParagraphStyle(name='VNH1', parent=styles['Heading1'], fontName=font, fontSize=16, leading=22, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name='VNH2', parent=styles['Heading2'], fontName=font, fontSize=13, leading=18, spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name='VNBody', parent=styles['BodyText'], fontName=font, fontSize=10, leading=14, spaceAfter=5, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='VNCode', parent=styles['Code'], fontName=font, fontSize=8, leading=10, leftIndent=12, backColor='#f3f4f6'))

pdf_path = REPORTS/'MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment.pdf'
doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=1.4*cm, leftMargin=1.4*cm, topMargin=1.4*cm, bottomMargin=1.4*cm)
story = []
text = combined_path.read_text(encoding='utf-8')

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

in_code = False
code_buf = []
for line in text.splitlines():
    if line.strip().startswith('```'):
        if not in_code:
            in_code = True; code_buf=[]
        else:
            if code_buf:
                story.append(Paragraph(esc('\n'.join(code_buf)).replace('\n','<br/>'), styles['VNCode']))
                story.append(Spacer(1, 5))
            in_code = False
        continue
    if in_code:
        code_buf.append(line)
        continue
    if line.startswith('# '):
        story.append(Paragraph(esc(line[2:]), styles['VNTitle']))
    elif line.startswith('## '):
        story.append(Paragraph(esc(line[3:]), styles['VNH1']))
    elif line.startswith('### '):
        story.append(Paragraph(esc(line[4:]), styles['VNH2']))
    elif line.strip() == '---':
        story.append(PageBreak())
    elif line.startswith('- [ ]'):
        story.append(Paragraph('☐ ' + esc(line[5:].strip()), styles['VNBody']))
    elif line.startswith('- '):
        story.append(Paragraph('• ' + esc(line[2:]), styles['VNBody']))
    elif re.match(r'^\d+\. ', line):
        story.append(Paragraph(esc(line), styles['VNBody']))
    elif line.strip():
        story.append(Paragraph(esc(line), styles['VNBody']))
    else:
        story.append(Spacer(1, 4))

doc.build(story)
print('wrote', pdf_path)
