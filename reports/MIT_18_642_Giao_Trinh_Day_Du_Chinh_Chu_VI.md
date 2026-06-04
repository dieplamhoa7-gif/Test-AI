# MIT 18.642 — Giáo trình đầy đủ, chỉnh chu cho nhà đầu tư

Bản này được Tiểu đệ biên soạn lại từ bộ transcript MIT 18.642 đã tải trong workspace. Mục tiêu là giảng lại nội dung theo mạch bài học, đầy trang và đủ ý hơn các bản rút gọn trước.


# Video 01 — Lecture 1, Part I: Introduction of the Class

**Chủ đề trọng tâm:** Tổng quan lớp học  
**Transcript:** `mit_18_642_transcripts\01_b8u2CQLQBVU.json` · 10,569 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Tổng quan lớp học" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Môn học mở đầu bằng việc giải thích vì

sao tài chính hiện đại cần toán học. Người học không chỉ học công thức, mà học cách đặt vấn đề: sản phẩm tài

chính tạo ra payoff nào, rủi ro nào có thể xảy ra, dữ liệu nào đo được, mô hình nào hợp lý, và kiểm định ra

sao. Đây là nền để một nhà đầu tư chuyển từ trực giác rời rạc sang tư duy có cấu trúc.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Môn học mở đầu bằng việc giải thích vì sao tài chính hiện đại cần toán học. Người học không chỉ học công thức,

mà học cách đặt vấn đề: sản phẩm tài chính tạo ra payoff nào, rủi ro nào có thể xảy ra, dữ liệu nào đo được,

mô hình nào hợp lý, và kiểm định ra sao. Đây là nền để một nhà đầu tư chuyển từ trực giác rời rạc sang tư duy

có cấu trúc. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là

không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian

của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu

bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Tổng quan lớp học" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Tổng quan lớp học" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 02 — Lecture 1, Part II: Introduction of Financial Markets, Financial Terms and Concepts

**Chủ đề trọng tâm:** Thị trường tài chính và thuật ngữ  
**Transcript:** `mit_18_642_transcripts\02_z4p87TPCnQc.json` · 24,712 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Thị trường tài chính và thuật ngữ" trong cấu trúc tổng thể của MIT

18.642. Điểm cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ

đề này vào khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Video giới thiệu

các lớp tài sản, vai trò của người tham gia thị trường, khái niệm equity, fixed income, derivatives,

alternatives, liquidity, leverage, hedge, arbitrage, alpha và beta. Nội dung quan trọng nhất là mỗi sản phẩm

tài chính có dòng payoff và rủi ro riêng, nên không thể phân tích mọi thứ bằng cùng một checklist.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Video giới thiệu các lớp tài sản, vai trò của người tham gia thị trường, khái niệm equity, fixed income,

derivatives, alternatives, liquidity, leverage, hedge, arbitrage, alpha và beta. Nội dung quan trọng nhất là

mỗi sản phẩm tài chính có dòng payoff và rủi ro riêng, nên không thể phân tích mọi thứ bằng cùng một

checklist. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là

không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian

của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu

bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Net return = gross return - fees - spread - slippage
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Thị trường tài chính và thuật ngữ" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy.

Nếu bài liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy

xem các mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay,

break-even và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo

horizon nào và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Thị trường tài chính và thuật ngữ" trong toàn bộ toolkit tài

chính định lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm,

biểu diễn dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định

đầu tư.

# Video 03 — Lecture 1, Part III: Bond “Mathematics”

**Chủ đề trọng tâm:** Bond mathematics  
**Transcript:** `mit_18_642_transcripts\03_NZ3Mva95UsQ.json` · 12,064 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Bond mathematics" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Bài trái phiếu dạy present value,

discounting, yield, duration, DV01, convexity và yield curve. Đây là một trong các nền tảng quan trọng nhất vì

mọi tài sản tài chính đều có yếu tố chiết khấu dòng tiền/rủi ro về hiện tại.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Bài trái phiếu dạy present value, discounting, yield, duration, DV01, convexity và yield curve. Đây là một

trong các nền tảng quan trọng nhất vì mọi tài sản tài chính đều có yếu tố chiết khấu dòng tiền/rủi ro về hiện

tại. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không

nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của

tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài

nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
PV = CF/(1+r)^t; Bond Price = Σ Coupon/(1+y)^t + Face/(1+y)^T
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Bond mathematics" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Bond mathematics" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 04 — Lecture 2: Linear Algebra

**Chủ đề trọng tâm:** Linear algebra  
**Transcript:** `mit_18_642_transcripts\04_0uimNNIuUyY.json` · 38,572 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Linear algebra" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Đại số tuyến tính biến dữ liệu tài

chính thành vector và matrix. Một cổ phiếu, một danh mục hay một ngày giao dịch đều có thể biểu diễn bằng

vector; nhiều quan sát tạo thành ma trận. Đây là nền cho covariance, PCA, regression và tối ưu danh mục.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Đại số tuyến tính biến dữ liệu tài chính thành vector và matrix. Một cổ phiếu, một danh mục hay một ngày giao

dịch đều có thể biểu diễn bằng vector; nhiều quan sát tạo thành ma trận. Đây là nền cho covariance, PCA,

regression và tối ưu danh mục. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình.

Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá

trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến

mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo

regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
x = [return, volatility, liquidity, beta]; Portfolio return = wᵀr
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Linear algebra" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan

xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong

tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Linear algebra" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 05 — Lecture 4: Linear Algebra (cont.); Probability Theory

**Chủ đề trọng tâm:** Probability theory  
**Transcript:** `mit_18_642_transcripts\05_mtXTs2U1uMA.json` · 40,830 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Probability theory" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Xác suất giúp nhà đầu tư nói về

phân phối kết quả thay vì một kết quả chắc chắn. Expectation, variance, covariance, correlation, skewness,

kurtosis và conditional probability là các khái niệm cốt lõi.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Xác suất giúp nhà đầu tư nói về phân phối kết quả thay vì một kết quả chắc chắn. Expectation, variance,

covariance, correlation, skewness, kurtosis và conditional probability là các khái niệm cốt lõi. Trong bài

giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào

công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói

về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về

volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
E[X]=Σpᵢxᵢ; Var(X)=E[(X-E[X])²]; Cov(X,Y)=E[(X-E[X])(Y-E[Y])]
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Probability theory" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Probability theory" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 06 — Lecture 5: Probability Theory (cont.); Stochastic Processes I

**Chủ đề trọng tâm:** Stochastic processes I  
**Transcript:** `mit_18_642_transcripts\06_wMGEKMHsOKE.json` · 40,279 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Stochastic processes I" trong cấu trúc tổng thể của MIT 18.642. Điểm

cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào

khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Giá tài sản là quá trình ngẫu

nhiên theo thời gian. Random walk, martingale, Markov chain và gambler’s ruin giúp hiểu vì sao path, drawdown

và quản trị vốn quan trọng.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Giá tài sản là quá trình ngẫu nhiên theo thời gian. Random walk, martingale, Markov chain và gambler’s ruin

giúp hiểu vì sao path, drawdown và quản trị vốn quan trọng. Trong bài giảng, giảng viên thường bắt đầu bằng

trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Markov: P(X_{t+1}|X_t, history)=P(X_{t+1}|X_t)
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Stochastic processes I" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài

liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các

mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even

và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào

và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Stochastic processes I" trong toàn bộ toolkit tài chính định

lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn

dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 07 — Lecture 6: Stochastic Processes I (cont.); Regression Analysis

**Chủ đề trọng tâm:** Regression analysis I  
**Transcript:** `mit_18_642_transcripts\07_yIn8Y_CSwPk.json` · 40,838 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Regression analysis I" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Hồi quy dùng để kiểm định quan hệ

giữa feature và outcome. Trong tài chính, nó giúp hỏi feature nào có thông tin thật, nhưng không được xem là

công thức dự báo chắc chắn.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Hồi quy dùng để kiểm định quan hệ giữa feature và outcome. Trong tài chính, nó giúp hỏi feature nào có thông

tin thật, nhưng không được xem là công thức dự báo chắc chắn. Trong bài giảng, giảng viên thường bắt đầu bằng

trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
y = Xβ + ε
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Regression analysis I" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài

liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các

mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even

và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào

và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Regression analysis I" trong toàn bộ toolkit tài chính định

lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn

dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 08 — Lecture 7: Linear Rates, Products, and Models

**Chủ đề trọng tâm:** Linear rates and products  
**Transcript:** `mit_18_642_transcripts\08_RvXwSoGDYvg.json` · 81,640 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Linear rates and products" trong cấu trúc tổng thể của MIT 18.642. Điểm

cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào

khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Bài rates đi vào yield curve,

benchmark rates, forwards, swaps, discount curves và hedging. Nó cho thấy lãi suất là hệ thống theo kỳ hạn và

ảnh hưởng sâu tới định giá.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Bài rates đi vào yield curve, benchmark rates, forwards, swaps, discount curves và hedging. Nó cho thấy lãi

suất là hệ thống theo kỳ hạn và ảnh hưởng sâu tới định giá. Trong bài giảng, giảng viên thường bắt đầu bằng

trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Discount factor D(t)=1/(1+r_t)^t
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Linear rates and products" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài

liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các

mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even

và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào

và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Linear rates and products" trong toàn bộ toolkit tài chính định

lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn

dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 09 — Lecture 8: Regression Analysis (cont.)

**Chủ đề trọng tâm:** Regression analysis II  
**Transcript:** `mit_18_642_transcripts\09_cMF_c2WNPyU.json` · 38,064 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Regression analysis II" trong cấu trúc tổng thể của MIT 18.642. Điểm

cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào

khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Phần hồi quy tiếp tục nhấn

mạnh diagnostics, residuals, p-value, R², outlier, multicollinearity và ý nghĩa kinh tế. Fit đẹp không đủ;

phải OOS và sau chi phí.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Phần hồi quy tiếp tục nhấn mạnh diagnostics, residuals, p-value, R², outlier, multicollinearity và ý nghĩa

kinh tế. Fit đẹp không đủ; phải OOS và sau chi phí. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác

rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu

tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa

biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định

và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
R²=1-SS_res/SS_tot; t-stat=estimate/se
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Regression analysis II" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài

liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các

mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even

và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào

và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Regression analysis II" trong toàn bộ toolkit tài chính định

lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn

dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 10 — Lecture 9: Principal Component Analysis in Finance

**Chủ đề trọng tâm:** PCA in finance  
**Transcript:** `mit_18_642_transcripts\10_CechARGinR4.json` · 64,549 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "PCA in finance" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. PCA tìm các hướng biến động chính, giúp

hiểu factor, giảm chiều dữ liệu và tránh đếm trùng tín hiệu. Trong yield curve có level/slope/curvature; trong

cổ phiếu có market/sector/idiosyncratic factors.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

PCA tìm các hướng biến động chính, giúp hiểu factor, giảm chiều dữ liệu và tránh đếm trùng tín hiệu. Trong

yield curve có level/slope/curvature; trong cổ phiếu có market/sector/idiosyncratic factors. Trong bài giảng,

giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức.

Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy,

điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu

tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Σv=λv; PC_i=Xv_i
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "PCA in finance" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan

xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong

tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "PCA in finance" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 11 — Lecture 10: Counterparty Risk Optimization

**Chủ đề trọng tâm:** Counterparty risk optimization  
**Transcript:** `mit_18_642_transcripts\11_VbtXo62ROC4.json` · 69,770 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Counterparty risk optimization" trong cấu trúc tổng thể của MIT 18.642.

Điểm cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này

vào khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Rủi ro đối tác cho thấy

risk nằm trong exposure, collateral, default, wrong-way risk và constraints. Nhà đầu tư cá nhân có thể chuyển

hóa thành concentration risk và liquidity risk.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Rủi ro đối tác cho thấy risk nằm trong exposure, collateral, default, wrong-way risk và constraints. Nhà đầu

tư cá nhân có thể chuyển hóa thành concentration risk và liquidity risk. Trong bài giảng, giảng viên thường

bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài

nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên

cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu

là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Expected loss = Exposure × PD × LGD
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Counterparty risk optimization" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy.

Nếu bài liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy

xem các mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay,

break-even và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo

horizon nào và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Counterparty risk optimization" trong toàn bộ toolkit tài chính

định lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu

diễn dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu

tư.

# Video 12 — Lecture 11: Regression Analysis (cont.)

**Chủ đề trọng tâm:** Regression advanced  
**Transcript:** `mit_18_642_transcripts\12_RruxdEjIvv0.json` · 42,871 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Regression advanced" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Phần hồi quy nâng cao nói về

interaction, regime dependency, nonlinearities và stability. Một feature có thể tốt ở bull market nhưng xấu ở

bear/high-vol regime.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Phần hồi quy nâng cao nói về interaction, regime dependency, nonlinearities và stability. Một feature có thể

tốt ở bull market nhưng xấu ở bear/high-vol regime. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác

rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu

tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa

biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định

và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
return ~ feature + regime + feature×regime + ε
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Regression advanced" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Regression advanced" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 13 — Lecture 13: Portfolio Management

**Chủ đề trọng tâm:** Portfolio management  
**Transcript:** `mit_18_642_transcripts\13_o7OnkMdmjLg.json` · 52,721 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Portfolio management" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Quản lý danh mục dùng expected

return, covariance matrix, efficient frontier và constraints. Chọn mã tốt chưa đủ; phân bổ vốn và correlation

mới quyết định rủi ro tổng thể.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Quản lý danh mục dùng expected return, covariance matrix, efficient frontier và constraints. Chọn mã tốt chưa

đủ; phân bổ vốn và correlation mới quyết định rủi ro tổng thể. Trong bài giảng, giảng viên thường bắt đầu bằng

trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Portfolio variance = wᵀΣw
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Portfolio management" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Portfolio management" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 14 — Lecture 14: Stochastic Processes II

**Chủ đề trọng tâm:** Stochastic processes II  
**Transcript:** `mit_18_642_transcripts\14_VM29JyI1sio.json` · 38,224 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Stochastic processes II" trong cấu trúc tổng thể của MIT 18.642. Điểm

cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào

khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Bài này mở rộng path

thinking: terminal return không đủ, cần hiểu hitting time, time underwater, max drawdown và continuous-time

intuition.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Bài này mở rộng path thinking: terminal return không đủ, cần hiểu hitting time, time underwater, max drawdown

và continuous-time intuition. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình.

Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá

trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến

mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo

regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
max drawdown, time-to-target, time-under-water
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Stochastic processes II" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài

liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các

mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even

và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào

và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Stochastic processes II" trong toàn bộ toolkit tài chính định

lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn

dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 15 — Lecture 12: Time Series Analysis

**Chủ đề trọng tâm:** Time series analysis  
**Transcript:** `mit_18_642_transcripts\15_qlytPllimpQ.json` · 40,559 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Time series analysis" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Chuỗi thời gian gồm stationarity,

unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration và forecast. Dữ liệu tài chính phải được kiểm theo thời

gian/horizon.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Chuỗi thời gian gồm stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration và forecast. Dữ liệu

tài chính phải được kiểm theo thời gian/horizon. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi

mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu

tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa

biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định

và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
AR(1): X_t=c+φX_{t-1}+ε_t
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Time series analysis" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Time series analysis" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 16 — Lecture 18: Applying Data Science and Artificial Intelligence to Managing Biomedical Portfolios

**Chủ đề trọng tâm:** AI and data science portfolios  
**Transcript:** `mit_18_642_transcripts\16__e2nDnV7FQs.json` · 69,137 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "AI and data science portfolios" trong cấu trúc tổng thể của MIT 18.642.

Điểm cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này

vào khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. AI/data science hỗ trợ

quyết định trong môi trường dữ liệu phức tạp. Domain knowledge, data quality, validation và risk control quan

trọng hơn model hào nhoáng.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

AI/data science hỗ trợ quyết định trong môi trường dữ liệu phức tạp. Domain knowledge, data quality,

validation và risk control quan trọng hơn model hào nhoáng. Trong bài giảng, giảng viên thường bắt đầu bằng

trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Model usefulness = data quality × validation × domain relevance
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "AI and data science portfolios" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy.

Nếu bài liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy

xem các mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay,

break-even và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo

horizon nào và được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "AI and data science portfolios" trong toàn bộ toolkit tài chính

định lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu

diễn dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu

tư.

# Video 17 — Lecture 19: Volatility Modeling

**Chủ đề trọng tâm:** Volatility modeling  
**Transcript:** `mit_18_642_transcripts\17_zapp8smQKhg.json` · 44,768 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Volatility modeling" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Volatility thay đổi theo thời

gian, có clustering, và ảnh hưởng trực tiếp đến risk, position sizing, stop-loss và option pricing. ARCH/GARCH

là tư duy mô hình hóa variance động.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Volatility thay đổi theo thời gian, có clustering, và ảnh hưởng trực tiếp đến risk, position sizing, stop-loss

và option pricing. ARCH/GARCH là tư duy mô hình hóa variance động. Trong bài giảng, giảng viên thường bắt đầu

bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi

suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là

quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động

không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
RealizedVol=std(returns)×√252; GARCH variance recursion
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Volatility modeling" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Volatility modeling" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 18 — Lecture 21: Black-Scholes Formula, Risk Neutral Valuation

**Chủ đề trọng tâm:** Black-Scholes  
**Transcript:** `mit_18_642_transcripts\18_2UCHztlWuZg.json` · 35,609 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Black-Scholes" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Black-Scholes định giá option bằng no-

arbitrage/risk-neutral valuation. Inputs gồm S, K, T, r, sigma. Greeks giúp hiểu độ nhạy. Đây là nền để hiểu

CW.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Black-Scholes định giá option bằng no-arbitrage/risk-neutral valuation. Inputs gồm S, K, T, r, sigma. Greeks

giúp hiểu độ nhạy. Đây là nền để hiểu CW. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới

đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên

cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến

giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và

có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
C = S N(d1) - K e^{-rT}N(d2); Greeks: Delta/Gamma/Vega/Theta
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Black-Scholes" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan

xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong

tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Black-Scholes" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 19 — Lecture 20: Building the First Federally (CFTC) Regulated Exchange Dedicated to Trading on Events

**Chủ đề trọng tâm:** Event markets  
**Transcript:** `mit_18_642_transcripts\19_8XrYjnDHmE4.json` · 41,234 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Event markets" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Prediction/event markets biến xác suất

sự kiện thành giá giao dịch. Với cổ phiếu, event risk gồm KQKD, chính sách, pháp lý, cổ tức, nâng hạng, M&A.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Prediction/event markets biến xác suất sự kiện thành giá giao dịch. Với cổ phiếu, event risk gồm KQKD, chính

sách, pháp lý, cổ tức, nâng hạng, M&A. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa

mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần

hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải

thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể

thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
Event price ≈ implied probability
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Event markets" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan

xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong

tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Event markets" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 20 — Lecture 23: Introduction to Machine Learning

**Chủ đề trọng tâm:** Machine learning  
**Transcript:** `mit_18_642_transcripts\20_kTsieIl_YBA.json` · 48,202 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Machine learning" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học

không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học,

nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. ML trong finance cần feature, label,

train/test theo thời gian, calibration, baseline và chống overfit. Model nên xuất xác suất/ranking, không phán

chắc chắn.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

ML trong finance cần feature, label, train/test theo thời gian, calibration, baseline và chống overfit. Model

nên xuất xác suất/ranking, không phán chắc chắn. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi

mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu

tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa

biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định

và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
features → model → calibrated probability
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Machine learning" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Machine learning" trong toàn bộ toolkit tài chính định lượng. Nó

không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo

xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 21 — Lecture 24: Stochastic Calculus

**Chủ đề trọng tâm:** Stochastic calculus  
**Transcript:** `mit_18_642_transcripts\21_5cruqmIF6l0.json` · 39,155 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "Stochastic calculus" trong cấu trúc tổng thể của MIT 18.642. Điểm cần

học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa

học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. Brownian motion, Itô integral và

Itô lemma là nền toán cho derivative pricing. Quan trọng là hiểu quá trình ngẫu nhiên liên tục có quy tắc khác

calculus thường.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Brownian motion, Itô integral và Itô lemma là nền toán cho derivative pricing. Quan trọng là hiểu quá trình

ngẫu nhiên liên tục có quy tắc khác calculus thường. Trong bài giảng, giảng viên thường bắt đầu bằng trực giác

rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu

tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa

biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định

và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
dX=μdt+σdW; Itô lemma includes second-order term
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "Stochastic calculus" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên

quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã

trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và

volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và

được kiểm ngoài mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "Stochastic calculus" trong toàn bộ toolkit tài chính định lượng.

Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu,

đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.

# Video 22 — Lecture 25: Stochastic Calculus (cont.); Stochastic Differential Equations

**Chủ đề trọng tâm:** SDE  
**Transcript:** `mit_18_642_transcripts\22_H4V29wkHYb4.json` · 42,387 ký tự


## 1. Mục tiêu bài học

Video này nhằm giúp anh nắm được phần "SDE" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học không phải là

thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học, nó giải quyết

vấn đề tài chính nào, và nó nối với các phần sau ra sao. Stochastic differential equations mô hình hóa drift

và random shock, ví dụ GBM dS=mu S dt + sigma S dW. Đây là cách nghĩ theo phân phối kịch bản, không phải một

đường dự báo duy nhất.

## 2. Bối cảnh bài giảng

Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu

hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp

khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công

thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và

khi nào giả định đó có thể sai.

## 3. Giảng lại nội dung chính

Stochastic differential equations mô hình hóa drift và random shock, ví dụ GBM dS=mu S dt + sigma S dW. Đây là

cách nghĩ theo phân phối kịch bản, không phải một đường dự báo duy nhất. Trong bài giảng, giảng viên thường

bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài

nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên

cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu

là biến động không cố định và có thể thay đổi theo regime.
Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận

thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu;

thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói

“setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.
Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm

định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con

người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning —

đều phải được dùng với kỷ luật kiểm định.

## 4. Công thức / mô hình cần nhớ

```
dS=μSdt+σSdW
```

Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công

thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một

công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời

“phân phối kết quả có hình dạng ra sao”.

## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán

Khi áp dụng bài "SDE" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan xác suất,

hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong tài khoản

có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và volatility trước

khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và được kiểm ngoài

mẫu chưa.

## 6. Hiểu sai thường gặp

- Nhầm mô hình với sự thật chắc chắn.
- Nhầm kết quả in-sample với năng lực dự báo thật.
- Bỏ qua chi phí, spread, slippage và thanh khoản.
- Dùng một công thức cho mọi regime thị trường.
- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.


## 7. Takeaway cuối bài

Sau video này, anh nên nắm được vai trò của "SDE" trong toàn bộ toolkit tài chính định lượng. Nó không đứng

riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo xác suất,

kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.