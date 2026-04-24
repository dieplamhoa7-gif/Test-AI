# Công thức PTKT không dùng AI

File chạy thật: `app/market_data.py`

## 1. Chỉ báo nền

```python
def _price_zone_state(price, rsi, bb_percent, donchian_high, donchian_low, vwap):
    near_donchian_low = bool(donchian_low and price <= donchian_low * 1.03)
    near_donchian_high = bool(donchian_high and price >= donchian_high * 0.97)
    below_vwap = bool(vwap and price < vwap)
    above_vwap = bool(vwap and price > vwap)

    if rsi <= 30 or (bb_percent is not None and bb_percent <= 0.08) or near_donchian_low:
        return "Quá bán"
    if rsi >= 70 or (bb_percent is not None and bb_percent >= 0.92) or near_donchian_high:
        return "Quá mua"
    if 30 < rsi <= 40 or (bb_percent is not None and bb_percent <= 0.2 and below_vwap):
        return "Gần quá bán"
    if 60 <= rsi < 70 or (bb_percent is not None and bb_percent >= 0.8 and above_vwap):
        return "Gần quá mua"
    return "Trung tính"
```

## 2. Xác định trạng thái xu hướng

```python
def _effective_trend(raw_trend, rsi, vwap, price, structure, macd=0, signal=0):
    structure_text = (structure or "").lower()
    below_vwap = bool(vwap and price < vwap)
    neutral_rsi = 45 <= rsi <= 55
    macd_negative = macd < signal

    if below_vwap and macd_negative and rsi < 45:
        return "Giảm", "giá dưới VWAP, MACD yếu và RSI dưới 45"
    if below_vwap and neutral_rsi and ("sideway" in structure_text or "tích" in structure_text or not structure_text):
        return "Đi ngang/tích lũy", "giá dưới VWAP, RSI quanh 50, cấu trúc chưa xác nhận xu hướng"
    if raw_trend == "Tăng" and below_vwap:
        return "Đi ngang/tích lũy", "giá dưới VWAP nên chưa xác nhận xu hướng tăng rõ"
    return raw_trend, ""
```

## 3. Cắt lỗ thông minh theo ngưỡng 6%

```python
def _smart_stop_loss(entry_price, support_levels, atr, max_loss_pct=6.0):
    ordered_levels = sorted([float(x) for x in (support_levels or []) if x and x > 0], reverse=True)
    levels = [x for x in ordered_levels if x < entry_price]
    if not levels:
        return round(max(entry_price - atr * 0.8, 0), 1), "ATR"

    max_loss_price = entry_price * (1 - max_loss_pct / 100)
    buffer = max(atr * 0.15, entry_price * 0.003)
    candidates = []

    for level in levels[:3]:
        support_idx = ordered_levels.index(level) + 1
        stop = round(max(level - buffer, 0), 1)
        loss_pct = (entry_price - stop) / entry_price * 100 if entry_price else 100
        if stop >= max_loss_price and loss_pct <= max_loss_pct:
            candidates.append((stop, f"dưới hỗ trợ {support_idx}", loss_pct))

    if candidates:
        stop, reason, loss_pct = sorted(candidates, key=lambda item: abs(max_loss_pct - item[2]))[0]
        return stop, f"{reason}, rủi ro {loss_pct:.1f}%"

    fallback = round(max(levels[0] - atr * 0.35, 0), 1)
    if fallback < max_loss_price:
        fallback = round(max_loss_price, 1)
    return fallback, "giới hạn rủi ro 6%"
```

## 4. Logic khuyến nghị

```python
strong_trend = strength in {"Mạnh", "Rất mạnh"}

if zone_state == "Quá mua":
    action = "Bán/giảm tỷ trọng"
elif zone_state == "Quá bán" and effective_trend.startswith("Giảm") and not strong_trend:
    action = "Quan sát hồi kỹ thuật"
elif zone_state == "Quá bán" and not effective_trend.startswith("Giảm"):
    action = "Khuyến mua thăm dò"
elif effective_trend == "Đi ngang/tích lũy":
    action = "Quan sát"
elif effective_trend.startswith("Tăng") and strong_trend and zone_state not in {"Gần quá mua", "Quá mua"}:
    action = "Khuyến mua"
elif effective_trend.startswith("Giảm") and strong_trend:
    action = "Bán/giảm tỷ trọng"
else:
    action = "Quan sát"
```

## 5. Format câu kết luận

```text
Trạng thái hiện tại: <Trend>, lực xu hướng <mạnh/yếu>.
Hỗ trợ <mốc hỗ trợ chính>.
Kháng cự <mốc kháng cự chính>.
<Khuyến nghị mua/bán/quan sát>.
Cắt lỗ dưới <mốc cắt lỗ>.
Mục tiêu kế tiếp <mốc mục tiêu>.
```
