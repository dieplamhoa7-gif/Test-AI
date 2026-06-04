from pathlib import Path
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REPORTS=Path('reports'); REPORTS.mkdir(exist_ok=True)

content = r'''# MIT 18.642 — Bài học trước, áp dụng sau

Bản tiếng Việt cho Hòa Đại ka.

Cách đọc:

1. Đọc phần **Bài học gốc** để hiểu MIT dạy gì.
2. Đọc phần **Ý nghĩa cho nhà đầu tư** để hiểu tư duy thị trường.
3. Cuối cùng mới đọc phần **Áp dụng vào LH Investment** để biết có thể biến thành feature/backtest/risk rule nào.

---

# Chương 1 — Nhập môn tài chính định lượng và Bond Mathematics

## A. Bài học gốc

Chương đầu của MIT 18.642 giới thiệu mục tiêu của môn học: dùng toán học để giải quyết các vấn đề tài chính thực tế. Đây không phải môn “học công thức để dự đoán giá”, mà là môn giúp ta mô hình hóa dòng tiền, rủi ro, xác suất, lãi suất, danh mục, phái sinh và quyết định đầu tư.

Môn học nối hai phần:

- Toán nền: linear algebra, probability, stochastic processes, regression, time series, optimization.
- Ứng dụng tài chính: bond, rates, portfolio, volatility, Black-Scholes, machine learning, risk management.

Phần Bond Mathematics dạy cách định giá dòng tiền tương lai. Một dòng tiền trong tương lai có giá trị hiện tại:

```text
PV = CF / (1 + r)^t
```

Một trái phiếu có nhiều dòng tiền:

```text
Bond Price = Σ Coupon_t / (1+y)^t + Face Value / (1+y)^T
```

Khi yield/lãi suất tăng, giá trái phiếu giảm. Khi yield giảm, giá trái phiếu tăng.

Duration đo độ nhạy của giá trái phiếu với thay đổi lãi suất:

```text
%ΔPrice ≈ -Duration × ΔYield
```

Convexity sửa phần sai lệch của duration khi lãi suất thay đổi lớn.

## B. Ý nghĩa cho nhà đầu tư

Bài học lớn nhất: tài sản tài chính là dòng tiền/rủi ro/xác suất được quy đổi về hiện tại. Cổ phiếu cũng vậy, dù dòng tiền không cố định như trái phiếu.

Lãi suất là “trọng lực” của tài chính:

- Lãi suất tăng → định giá bị ép, đặc biệt cổ phiếu tăng trưởng/duration dài.
- Lãi suất giảm → risk appetite thường tốt hơn, định giá dễ mở rộng hơn.

Một trade tốt không phải trade có câu chuyện hay nhất, mà là trade có kỳ vọng lời/lỗ tốt:

```text
Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

Win rate cao chưa chắc tốt. Nếu lỗ trung bình quá lớn, chiến lược vẫn tệ.

## C. Áp dụng vào LH Investment

- Mỗi chiến lược nên có expected value, không chỉ BUY/WATCH.
- Market regime/lãi suất/tỷ giá/thanh khoản nên là bối cảnh nền.
- Với cổ phiếu growth hoặc P/E cao, nên có `rateSensitiveScore`.
- Backtest cần báo: win rate, avg win, avg loss, EV, max drawdown.
- Với chứng quyền/CW, không chỉ nhìn cổ phiếu cơ sở; phải tính thời gian, volatility, spread, break-even.

---

# Chương 2 — Linear Algebra, Probability và Stochastic Processes

## A. Bài học gốc

Linear Algebra là ngôn ngữ của dữ liệu nhiều chiều. Một cổ phiếu tại một thời điểm có thể biểu diễn thành vector:

```text
x_t = [return_20d, RSI, MACD, volume_ratio, ATR, distance_to_support, ...]
```

Nhiều cổ phiếu trong nhiều ngày tạo thành ma trận feature. Regression, PCA, portfolio optimization và ML đều dựa trên ma trận này.

Probability dạy rằng kết quả đầu tư là bất định. Ta không nên hỏi “chắc chắn tăng không?”, mà hỏi:

```text
P(tăng 6% trong 20 ngày | điều kiện hiện tại) là bao nhiêu?
```

Stochastic Processes xem giá là chuỗi biến ngẫu nhiên theo thời gian:

```text
P_1, P_2, ..., P_t
```

Giá có noise, trend, mean reversion, volatility clustering và regime change.

## B. Ý nghĩa cho nhà đầu tư

Mỗi tín hiệu chỉ nên hiểu là tăng xác suất, không phải đảm bảo. Một mã có setup đẹp vẫn có thể sai vì thị trường xấu, tin bất ngờ, thanh khoản yếu hoặc volatility tăng.

Nếu nhiều indicator kể cùng một câu chuyện, ta không được tính là nhiều bằng chứng độc lập. Ví dụ RSI, Stochastic, Williams %R đều thuộc nhóm momentum oscillator.

Dữ liệu chứng khoán có thứ tự thời gian. Không được random split như bài toán ảnh/text thông thường.

## C. Áp dụng vào LH Investment

- Tạo feature matrix chuẩn cho VN100.
- Mỗi mã/ngày là một vector feature.
- Tính correlation giữa indicator để loại tín hiệu trùng.
- Dùng time-series split, không random split.
- Mỗi setup cần precision/EV theo horizon 5/10/20/60 ngày.
- Thêm market regime vào mọi output chiến lược.

---

# Chương 3 — Regression, Time Series và PCA

## A. Bài học gốc

Regression kiểm tra quan hệ giữa feature và kết quả tương lai. Ví dụ:

```text
future_return_20d = a + b1*RS20 + b2*RSI + b3*volume_ratio + b4*dist_support + error
```

Mục tiêu không phải tạo công thức thần kỳ, mà là kiểm định feature nào có thông tin thật.

Time Series Analysis nhắc rằng dữ liệu tài chính không độc lập đơn giản. Giá và return thay đổi theo regime, volatility clustering, trend và chu kỳ.

PCA tìm các hướng biến động chính trong dữ liệu. Trong tài chính, PCA dùng để giảm nhiễu, tìm factor, loại feature trùng và phân tích rủi ro danh mục.

## B. Ý nghĩa cho nhà đầu tư

Nếu một indicator chỉ đẹp trong quá khứ nhưng không ổn định ngoài mẫu, đừng tin. Nếu coefficient đổi dấu liên tục, feature đó không đáng dùng làm lõi.

Một model tốt cần thắng baseline đơn giản. Nếu dùng ML phức tạp mà không hơn rule đơn giản, chưa đáng đưa vào hệ thống.

PCA/correlation giúp tránh “ảo giác nhiều tín hiệu”. 10 indicator trùng nhau không bằng 3 factor độc lập.

## C. Áp dụng vào LH Investment

- Build `research_feature_matrix_vn100`.
- Thêm labels `futureReturn5d/10d/20d/60d`.
- Chạy regression để kiểm định feature.
- Chạy correlation/PCA để gom 40 indicator thành vài nhóm factor.
- Backtest walk-forward theo thời gian.
- Báo cáo feature nào giữ, feature nào bỏ.

---

# Chương 4 — Portfolio, Risk và Volatility

## A. Bài học gốc

Portfolio Management không chỉ là chọn mã tốt. Nó là bài toán phân bổ vốn giữa nhiều tài sản sao cho return/risk hợp lý.

Rủi ro danh mục phụ thuộc vào:

- volatility từng mã,
- correlation giữa các mã,
- tỷ trọng,
- ngành,
- thị trường chung.

Volatility Modeling dạy rằng biến động không cố định. Sau giai đoạn biến động mạnh, thị trường thường tiếp tục biến động mạnh — gọi là volatility clustering.

ATR, realized volatility, Bollinger width... là cách đo biến động thực dụng.

## B. Ý nghĩa cho nhà đầu tư

Mua 5 mã cùng ngành không phải đa dạng hóa thật. Ví dụ SSI, VND, HCM, VCI, MBS đều phụ thuộc lớn vào ngành chứng khoán và thanh khoản thị trường.

Stop-loss cố định cho mọi mã là thô. Mã ATR 1.5% khác mã ATR 5%.

Position size nên phụ thuộc vào volatility và confidence.

## C. Áp dụng vào LH Investment

- Thêm `atrPct`, `realizedVol20`, `volRegime`.
- Thêm `positionSizeHint`.
- Cảnh báo sector concentration.
- Tính correlation giữa các mã trong watchlist/danh mục.
- Backtest strategy theo volatility regime.
- Ranking nên là risk-adjusted score, không chỉ upside score.

---

# Chương 5 — Derivatives, Black-Scholes và Chứng quyền/CW

## A. Bài học gốc

Derivative là sản phẩm có giá trị phụ thuộc tài sản cơ sở. Option/CW phụ thuộc vào:

```text
S = giá tài sản cơ sở
K = giá thực hiện
T = thời gian còn lại
r = lãi suất
σ = volatility
```

Black-Scholes dạy rằng giá option không chỉ phụ thuộc hướng đi của cổ phiếu, mà còn phụ thuộc volatility và thời gian.

Risk-neutral valuation là cách định giá theo nguyên tắc không-arbitrage, không có nghĩa là thị trường không rủi ro.

## B. Ý nghĩa cho nhà đầu tư

CW không thể phân tích như cổ phiếu thường. Cổ phiếu cơ sở tăng nhưng CW vẫn có thể không tăng nếu:

- gần đáo hạn,
- spread rộng,
- thanh khoản kém,
- break-even quá xa,
- implied volatility đắt,
- time decay mạnh.

Không nên chọn CW chỉ vì leverage cao.

## C. Áp dụng vào LH Investment

CW ranking nên có:

- underlying signal score,
- days to maturity,
- moneyness,
- break-even distance,
- spread penalty,
- liquidity penalty,
- time decay penalty,
- final CW score.

Nếu thiếu các biến này, CW score dễ gây hiểu nhầm.

---

# Chương 6 — Machine Learning và Stochastic Calculus

## A. Bài học gốc

Machine Learning có thể học quan hệ phức tạp giữa nhiều feature, nhưng trong tài chính rất dễ overfit vì dữ liệu nhiễu và regime thay đổi.

ML workflow đúng cần:

- label rõ,
- feature sạch,
- split theo thời gian,
- baseline đơn giản,
- OOS test,
- explainability.

Stochastic Calculus là nền toán cho quá trình ngẫu nhiên liên tục, option pricing và SDE. Với cổ phiếu thường, không nhất thiết đưa Ito calculus vào pipeline hằng ngày, nhưng cần hiểu để nắm bản chất option/volatility/risk.

## B. Ý nghĩa cho nhà đầu tư

ML không thay thế kỷ luật đầu tư. ML chỉ khuếch đại chất lượng dữ liệu: dữ liệu sạch thì tốt hơn, dữ liệu bẩn thì sai tinh vi hơn.

Đừng dùng model đen nếu không biết nó đúng vì sao và sai khi nào.

Stochastic calculus nhắc rằng giá là quá trình ngẫu nhiên, nên risk phải được quản trị động theo thời gian.

## C. Áp dụng vào LH Investment

- Trước ML: build feature matrix, EV backtest, regime split.
- ML nên dùng để rank xác suất, không tự phán BUY mù.
- Model đầu tiên nên là logistic regression hoặc gradient boosting nhẹ.
- Phải so với rule baseline.
- Output ML phải có explanation và confidence calibration.

---

# Chương 7 — Roadmap triển khai vào hệ thống LH Investment

## A. Bài học gốc

Toàn bộ khóa MIT dẫn đến một tư duy: tài chính định lượng là quá trình biến dữ liệu thành quyết định có kiểm định, có xác suất, có rủi ro và có kỷ luật.

Không có bước nào đứng riêng:

- Toán giúp tạo feature.
- Xác suất giúp đo edge.
- Time series giúp kiểm định đúng thời gian.
- Portfolio giúp quản trị vốn.
- Volatility giúp đặt stop/size.
- Derivatives giúp hiểu CW.
- ML giúp rank nếu dữ liệu đủ sạch.

## B. Ý nghĩa cho nhà đầu tư

Một hệ thống tốt không chỉ trả lời “mua mã nào?”. Nó phải trả lời:

- Vì sao mua?
- Xác suất thắng bao nhiêu?
- Sai khi nào?
- Lỗ tối đa kỳ vọng bao nhiêu?
- Nên mua tỷ trọng bao nhiêu?
- Có bị trùng ngành/trùng factor không?
- Thị trường hiện tại có phù hợp không?

## C. Áp dụng vào LH Investment

Thứ tự triển khai đề xuất:

1. Feature matrix VN100.
2. Merge chart pattern cache vào feature matrix.
3. Add future return labels 5/10/20/60 ngày.
4. Backtest 3 chiến lược theo EV và regime.
5. Correlation/PCA để loại indicator trùng.
6. Portfolio risk: sector cap, correlation warning, position size.
7. CW scoring: break-even, time decay, spread, liquidity.
8. ML ranking nhẹ, OOS nghiêm.

Kết luận:

```text
Từ indicator + rule + cảm tính
sang
feature matrix + probability + expected value + regime + risk-adjusted ranking
```

Bước đáng làm nhất tiếp theo: **build feature matrix VN100**.
'''

out_md = REPORTS/'MIT_18_642_Bai_Hoc_Truoc_Ap_Dung_Sau_v3.md'
out_md.write_text(content, encoding='utf-8')

font='Helvetica'
for fp in [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\calibri.ttf', r'C:\Windows\Fonts\segoeui.ttf']:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFont', fp)); font='VNFont'; break
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='VNTitle', parent=styles['Title'], fontName=font, fontSize=20, leading=26, spaceAfter=16))
styles.add(ParagraphStyle(name='VNH1', parent=styles['Heading1'], fontName=font, fontSize=16, leading=22, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name='VNH2', parent=styles['Heading2'], fontName=font, fontSize=13, leading=18, spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name='VNBody', parent=styles['BodyText'], fontName=font, fontSize=10, leading=14, spaceAfter=5, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='VNCode', parent=styles['Code'], fontName=font, fontSize=8, leading=10, leftIndent=12, backColor='#f3f4f6'))

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
story=[]; in_code=False; code=[]
for line in content.splitlines():
    if line.strip().startswith('```'):
        if not in_code: in_code=True; code=[]
        else:
            if code: story.append(Paragraph(esc('\n'.join(code)).replace('\n','<br/>'), styles['VNCode'])); story.append(Spacer(1,5))
            in_code=False
        continue
    if in_code: code.append(line); continue
    if line.startswith('# '): story.append(Paragraph(esc(line[2:]), styles['VNTitle']))
    elif line.startswith('## '): story.append(Paragraph(esc(line[3:]), styles['VNH1']))
    elif line.startswith('### '): story.append(Paragraph(esc(line[4:]), styles['VNH2']))
    elif line.strip()=='---': story.append(PageBreak())
    elif line.startswith('- '): story.append(Paragraph('• '+esc(line[2:]), styles['VNBody']))
    elif re.match(r'^\d+\. ', line): story.append(Paragraph(esc(line), styles['VNBody']))
    elif line.strip(): story.append(Paragraph(esc(line), styles['VNBody']))
    else: story.append(Spacer(1,4))
out_pdf = REPORTS/'MIT_18_642_Bai_Hoc_Truoc_Ap_Dung_Sau_v3.pdf'
doc=SimpleDocTemplate(str(out_pdf),pagesize=A4,rightMargin=1.4*cm,leftMargin=1.4*cm,topMargin=1.4*cm,bottomMargin=1.4*cm)
doc.build(story)
print(out_md, out_md.stat().st_size)
print(out_pdf, out_pdf.stat().st_size)
