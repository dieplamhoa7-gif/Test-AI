# B4 Trend Pullback — mua hồi trong trend

Locked: 2026-05-01

## Vai trò

B4 là chiến lược chính hiện tại: **mua hồi trong xu hướng còn khỏe**, không phải bắt đáy.

## Nguyên tắc tách lớp

- R/S engine chỉ dùng để xác định vùng giá:
  - support/resistance
  - support zone / resistance zone
  - distance to support
  - stop/target reference
- Strategy/action chỉ dùng để xác nhận hành động:
  - Ichimoku
  - RSI
  - volume ratio
  - ROC20
  - MACD histogram recovery
  - bullish divergence như điều kiện phụ cho trend pullback
  - không bearish divergence

## Điều kiện B4 Trend Pullback

```text
Ichimoku = above_cloud
DistSupport <= 3%
RSI 48–62
Volume ratio 0.55–2.2
ROC20 từ -8 đến 12
MACD hist hồi dần 3 phiên
  hoặc có bullish divergence và MACD hist >= -0.05
BB percent <= 0.85
Không bearish divergence
```

## Exit cố định

```text
Target +6%
Chốt 50% tại +6%
Phần còn lại trailing
Stop 6%
```

## Backtest đã lưu

Script gốc:

```text
backtest_v3_two_strategies_target6.py
```

Output:

```text
data/v3_two_strategies_target6_backtest.json
```

Kết quả B4:

```text
Current180:
- 11 lệnh
- Win rate 63.64%
- Avg PnL +1.59%
- Sum PnL +17.51%

OOS prev3m:
- 32 lệnh
- Win rate 56.25%
- Avg PnL +0.51%
- Sum PnL +16.27%

Tổng:
- 43 lệnh
- 25 win / 18 loss
- Win rate khoảng 58.14%
- Sum PnL +33.78%
```

## Quyết định

Giữ B4 Trend Pullback là chiến lược chính hiện tại.

## Ghi chú về version bắt đáy

Version bắt đáy sau này **không cần xét phân kỳ dương và phân kỳ âm**.

Bắt đáy nên tập trung vào:

```text
RSI thấp / quá bán
Gần hỗ trợ thật sát
Không thủng mây dưới nếu dùng cloud filter
MACD hist hồi dần
Volume không quá yếu / không spike xấu
BB percent thấp
```

Không dùng divergence làm điều kiện bắt buộc cho version bắt đáy.
