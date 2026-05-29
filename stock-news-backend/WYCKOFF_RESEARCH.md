# WYCKOFF_RESEARCH.md

## Mục tiêu
Chuẩn hóa cách dùng **Wyckoff** trong repo này để:

1. Phân tích cấu trúc cung/cầu của cổ phiếu
2. Gắn nhãn các sự kiện Wyckoff có thể đo được
3. Suy ra **xác suất kịch bản cho vài nến/phiên tiếp theo**
4. Tạo feature cho backtest / ML / chart overlay

> Lưu ý quan trọng: Wyckoff **không dự đoán chính xác từng cây nến** theo kiểu tất định.
> Cách đúng là dùng Wyckoff để ước lượng:
> - xác suất tiếp diễn / hồi / phá vỡ giả / thất bại
> - chất lượng support / resistance
> - xác suất xuất hiện một cú SOS / SOW / spring / upthrust tiếp theo

---

## 1) Wyckoff là gì?
Wyckoff là framework đọc thị trường dựa trên:

- **Supply vs Demand**
- **Cause vs Effect**
- **Effort vs Result**

Nó không phải indicator đơn lẻ như RSI/MACD.

### 3 luật cốt lõi

#### 1. Supply vs Demand
- cầu > cung → giá tăng
- cung > cầu → giá giảm

#### 2. Cause vs Effect
- vùng tích lũy/phân phối là **cause**
- cú tăng/giảm sau đó là **effect**

#### 3. Effort vs Result
- volume lớn mà giá đi ít → hấp thụ / phân phối / cản mạnh
- volume lớn và spread rộng cùng chiều → xu hướng khỏe hơn

---

## 2) Mục tiêu áp dụng vào repo này
Trong repo LH Investment, Wyckoff nên được dùng theo 4 lớp:

### Lớp A — Structure
- Trading range
- Pivot highs / lows
- Spring / Upthrust
- SOS / SOW
- LPS / LPSY
- Breakout / false breakout / reclaim

### Lớp B — Effort / Result
- Volume spike vs MA20
- Spread rộng/hẹp
- Close nằm gần high/low
- Effort lớn nhưng result nhỏ
- Dry-up volume tại vùng kiểm định

### Lớp C — Zone Quality
- Support / resistance cluster
- Số lần touch hợp lệ
- Break penalty
- Reclaim quality
- Reaction quality sau touch

### Lớp D — Context
- Relative strength với VNINDEX / VN100
- Trend nền của mã
- Volatility regime
- Market breadth / risk-on risk-off

---

## 3) Các event Wyckoff cần chuẩn hóa

## 3.1 Accumulation-side events

### PS — Preliminary Support
Điều kiện gợi ý:
- đang trong downtrend ngắn-trung hạn
- xuất hiện nến giảm spread lớn + volume tăng
- sau đó tốc độ rơi chậm lại

### SC — Selling Climax
Điều kiện gợi ý:
- low mới đáng kể sau nhịp giảm mạnh
- spread lớn
- volume cực cao so với MA20/MA50
- close hồi khỏi low đáng kể

### AR — Automatic Rally
- sau SC có nhịp bật nhanh
- độ dốc tăng rõ
- volume vẫn khá cao

### ST — Secondary Test
- quay lại gần vùng SC
- spread hẹp hơn SC
- volume thấp hơn SC
- tốt hơn nếu low không thủng sâu SC

### Spring / Shakeout
- xuyên xuống dưới đáy range / support
- nhưng đóng lại trong/ở trên vùng hỗ trợ
- volume không nhất thiết luôn cực đại, nhưng hành vi reclaim phải rõ

### Test
- quay lại kiểm tra vùng spring / support
- volume thấp hơn
- downside spread hẹp hơn

### SOS — Sign of Strength
- bứt lên khỏi vùng range / vượt đỉnh gần
- spread tốt, close khỏe
- volume xác nhận

### LPS — Last Point of Support
- pullback sau SOS
- hồi về vùng hỗ trợ mới
- volume giảm, không breakdown

---

## 3.2 Distribution-side events

### PSY — Preliminary Supply
- uptrend trước đó kéo dài
- nến tăng mạnh nhưng bắt đầu xuất hiện áp lực cung

### BC — Buying Climax
- giá tăng mạnh / gap / spread rộng
- volume rất lớn
- close không còn quá khỏe hoặc dễ có upper wick

### AR — Automatic Reaction
- sau BC có nhịp giảm nhanh đầu tiên

### ST
- retest lại vùng BC
- thường lực tăng kém hơn, spread/volume không đẹp bằng BC

### UT / UTAD
- vượt đỉnh range / vượt kháng cự
- nhưng thất bại, đóng lại bên dưới
- xác suất bull trap cao

### SOW — Sign of Weakness
- breakdown hỗ trợ range với spread giảm + volume xác nhận

### LPSY
- hồi yếu sau SOW
- không reclaim được kháng cự cũ

---

## 4) Mapping sang machine-readable features

## 4.1 Bar-level features
Mỗi bar nên có các feature sau:

- `spread = high - low`
- `body = abs(close - open)`
- `close_pos = (close - low) / max(1e-9, high - low)`
- `upper_wick = high - max(open, close)`
- `lower_wick = min(open, close) - low`
- `vol_rel20 = volume / MA(volume,20)`
- `range_rel20 = spread / MA(spread,20)`
- `true_range_rel20`
- `ret_1d`, `ret_3d`, `ret_5d`

## 4.2 Zone-level features
Cho mỗi support/resistance zone:

- `touch_count`
- `valid_touch_count`
- `avg_reaction_after_touch`
- `break_count_body`
- `wick_penetration_count`
- `reclaim_count`
- `vol_on_touch_rel`
- `dry_test_score`
- `bounce_quality`
- `rejection_quality`

## 4.3 Structure-level features
- `range_width_pct`
- `range_age_bars`
- `distance_to_range_low`
- `distance_to_range_high`
- `spring_score`
- `upthrust_score`
- `sos_score`
- `sow_score`
- `lps_score`
- `lpsy_score`
- `absorption_score`
- `distribution_score`
- `cause_width_score`

---

## 5) Không dự đoán “nến tiếp theo” theo kiểu cứng
Thay vào đó, với mỗi mã/ngày, ta nên tạo xác suất cho các kịch bản sau:

### Kịch bản bullish
- `p_markup_3_10d`: xác suất có nhịp tăng đáng kể trong 3–10 phiên tới
- `p_sos_next`: xác suất xuất hiện SOS sớm
- `p_successful_reclaim`: xác suất giữ được reclaim trên support

### Kịch bản bearish
- `p_markdown_3_10d`: xác suất giảm đáng kể trong 3–10 phiên tới
- `p_sow_next`: xác suất xuất hiện SOW
- `p_failed_breakout`: xác suất breakout hiện tại thất bại

### Kịch bản neutral/chop
- `p_range_continue`: xác suất giá tiếp tục dao động trong range
- `p_false_break_both_sides`: xác suất quét hai đầu range rồi quay lại

Đây là cách dùng Wyckoff đúng cho máy.

---

## 6) Rule-based scoring đề xuất

## 6.1 Spring score
Ví dụ:

- low xuyên dưới support: +20
- close quay lại trên support: +20
- lower wick dài: +10
- vol_rel20 > 1.2: +10
- phiên sau không follow-through xuống: +15
- test lại với volume thấp: +15
- nếu body breakdown sâu và không reclaim: -25

Chuẩn hóa thành thang 0–100.

## 6.2 Upthrust score
- high vượt resistance/range high: +20
- close đóng lại dưới resistance: +20
- upper wick dài: +10
- vol_rel20 cao: +10
- phiên sau giảm xác nhận: +15
- retest thất bại: +15
- nếu breakout giữ được bằng close mạnh: -25

## 6.3 SOS score
- close vượt range high / pivot high: +20
- spread > MA spread: +15
- volume xác nhận: +15
- close near high: +10
- pullback nông sau breakout: +15
- không bị reject mạnh: +10

## 6.4 SOW score
- close thủng support/range low: +20
- spread giảm lớn: +15
- volume xác nhận: +15
- close near low: +10
- retest hồi yếu: +15
- không reclaim nhanh: +10

---

## 7) ML framing đề xuất
Wyckoff hợp nhất khi dùng làm feature cho ML hoặc ranking model.

### Label đề xuất

#### Bullish label
`label_markup_10d = 1` nếu:
- return 10 ngày > +5%
- và max drawdown trong 10 ngày > -4% không bị vi phạm sâu

#### Bearish label
`label_markdown_10d = 1` nếu:
- return 10 ngày < -5%
- hoặc min excursion < -6%

#### Breakout-failure label
`label_failed_breakout = 1` nếu:
- hôm nay breakout trên resistance
- trong 5 phiên tới đóng lại dưới resistance và hiệu suất âm

### Feature groups
- Wyckoff structure scores
- RSI / ATR / volume / trend filter
- relative strength vs VN100
- distance to key zone
- volatility compression / expansion

---

## 8) Cách vẽ lên chart web
Trên `stocks.html` / local test, Wyckoff không nên làm rối chart.

Chỉ nên overlay:

- support / resistance zone quality
- icon nhỏ cho `spring`, `upthrust`, `SOS`, `SOW`, `LPS`, `LPSY`
- text summary ngắn:
  - `Wyckoff: Accumulation bias 68/100`
  - `Spring score: 74`
  - `SOS readiness: 61`
  - `Range continuation: 42`

Không nên nhồi toàn bộ phase label nếu confidence thấp.

---

## 9) Những sai lầm cần tránh

1. **Hindsight labeling**
   - nhìn quá khứ rồi gắn nhãn phase đẹp như sách

2. **Rigid schematic fitting**
   - thị trường thật không đi giống hình minh họa

3. **No context**
   - có spring nhưng thị trường chung xấu vẫn fail

4. **No quantification**
   - nói “hấp thụ”, “dry volume”, “cung cạn” nhưng không có số đo

5. **One-shot phase classifier**
   - cố gắn A/B/C/D/E ngay từ đầu thường kém ổn định

---

## 10) Khuyến nghị cho repo này

### Nên làm theo thứ tự

#### Bước 1
Xây detector cho:
- spring
- upthrust
- SOS
- SOW
- dry test
- effort-result anomaly

#### Bước 2
Biến thành score:
- `springScore`
- `upthrustScore`
- `sosScore`
- `sowScore`
- `absorptionScore`
- `distributionScore`

#### Bước 3
Backtest trên VN100:
- standalone
- làm feature cho ML
- làm filter cho SR engine hiện tại

#### Bước 4
Mới thử phase classifier:
- accumulation bias
- distribution bias
- markup readiness
- markdown readiness

---

## 11) File/code liên quan hiện có
Repo hiện đã có baseline:

- `backtest_wyckoff_sr_vn100_local.py`

Baseline này đã đi đúng hướng thực dụng:
- support zones từ pivot lows
- touches
- volume on touch
- reaction after touch
- break penalty
- setup `spring_reclaim`, `dry_test_reclaim`, `combined`

Tuy nhiên, baseline chưa đủ rộng để đại diện toàn bộ Wyckoff.

---

## 12) Kế hoạch code tiếp theo

### File 1
`wyckoff_features.py`
- tính các feature / score Wyckoff chuẩn hóa

### File 2
`backtest_wyckoff_features_vn100.py`
- test predictive value cho 3/5/10 phiên tiếp theo

### File 3
`build_wyckoff_overlay_cache.py`
- xuất cache cho web chart

### File 4
`stocks.html`
- hiển thị overlay nhẹ, không spam chart

---

## 13) Kết luận thực dụng
Wyckoff nên được dùng để trả lời các câu hỏi sau:

- Cổ phiếu đang có dấu hiệu hấp thụ hay phân phối?
- Support này có đáng tin không?
- Breakout này thật hay giả?
- Xác suất 3–10 phiên tới nghiêng về markup, markdown hay tiếp tục sideway?

Không nên dùng Wyckoff để khẳng định:

- “ngày mai chắc chắn tăng”
- “cây nến tiếp theo chắc chắn xanh”

Cách đúng là:

> **Wyckoff = framework tạo xác suất kịch bản ngắn hạn từ cấu trúc cung-cầu**

---

## 14) Quyết định cho repo LH Investment
Từ thời điểm này, trong repo này:

- Wyckoff sẽ được triển khai như **event detector + score engine**
- không coi là indicator đơn lẻ
- không cố gắn phase cứng khi confidence thấp
- ưu tiên dùng cho:
  - support/resistance quality
  - breakout validation
  - false-break detection
  - 3–10 phiên probability scoring
