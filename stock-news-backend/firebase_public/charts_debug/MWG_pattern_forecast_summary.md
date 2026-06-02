# MWG — Pattern & Forecast Summary

> **Research-only, not financial advice.** Forecast mang tính xác suất/kịch bản.

- Nguồn: `MWG_daily_from_2023.csv` (daily, 845 nến)
- Ngày cuối: **2026-05-29** — Giá cuối: **76.3**
- Engine: TA-Lib=False, scipy=True
- **Thiên hướng tổng hợp: `NEUTRAL`** (bull 4255.3 vs bear 5044.2)

## Tín hiệu nổi bật
**Tăng:** support-cluster(100,high), support-cluster(100,high), support-cluster(100,high), support-cluster(100,high), support-trendline(100,high)
**Giảm:** resistance-cluster(100,high), resistance-cluster(100,high), resistance-cluster(100,high), resistance-cluster(100,high), resistance-trendline(100,high)

## Vùng giá quan trọng
- Hỗ trợ: [76.12, 75.87, 75.4, 75.3]
- Kháng cự: [78.75, 79.63, 81.15, 81.9]

## Dự báo (regression log-close + ATR band)
- **5 phiên**: 76.26 (vùng 72.24–80.27) → 2026-06-03
- **10 phiên**: 76.23 (vùng 70.56–81.91) → 2026-06-08
- **20 phiên**: 76.2 (vùng 68.17–84.23) → 2026-06-18

**Kịch bản:**
- Bullish: **87.06** — falling-wedge target
- Base: **76.2** — 20-bar trend regression (damped)
- Bearish: **70.87** — triple-top target

## Mẫu hình phát hiện theo tầng tin cậy

### Tier 1 — tin cậy (105)
- **support-cluster** [bullish, high, score 100, active] — 8 pivot chạm vùng support
- **support-cluster** [bullish, high, score 100, active] — 6 pivot chạm vùng support
- **support-cluster** [bullish, high, score 100, active] — 5 pivot chạm vùng support
- **support-cluster** [bullish, high, score 100, active] — 5 pivot chạm vùng support
- **resistance-cluster** [bearish, high, score 100, active] — 7 pivot chạm vùng resistance
- **resistance-cluster** [bearish, high, score 100, active] — 6 pivot chạm vùng resistance
- **resistance-cluster** [bearish, high, score 100, active] — 5 pivot chạm vùng resistance
- **resistance-cluster** [bearish, high, score 100, active] — 8 pivot chạm vùng resistance
- **support-trendline** [bullish, high, score 100, active] — Trendline 6 chạm, 0 vi phạm
- **resistance-trendline** [bearish, high, score 100, active] — Trendline 6 chạm, 0 vi phạm
- **support-cluster** [bullish, high, score 99.7, active] — 4 pivot chạm vùng support
- **resistance-cluster** [bearish, high, score 97.0, active] — 4 pivot chạm vùng resistance
- **support-cluster** [bullish, high, score 96.1, active] — 6 pivot chạm vùng support
- **support-cluster** [bullish, high, score 93.9, active] — 5 pivot chạm vùng support
- **resistance-cluster** [bearish, high, score 93.6, active] — 4 pivot chạm vùng resistance
- **support-cluster** [bullish, high, score 91.2, active] — 4 pivot chạm vùng support
- **support-cluster** [bullish, high, score 85.3, active] — 6 pivot chạm vùng support
- **resistance-cluster** [bearish, high, score 82.9, active] — 4 pivot chạm vùng resistance
- **triple-bottom** [bullish, high, score 76.0, active] → target 64.31 — 3 đáy ~57.1, neckline 60.7
- **triple-bottom** [bullish, high, score 76.0, active] → target 65.11 — 3 đáy ~57.7, neckline 61.4
- **triple-bottom** [bullish, high, score 76.0, active] → target 67.38 — 3 đáy ~58.6, neckline 63.0
- **triple-bottom** [bullish, high, score 76.0, active] → target 66.69 — 3 đáy ~59.3, neckline 63.0
- **triple-bottom** [bullish, high, score 76.0, active] → target 66.61 — 3 đáy ~60.0, neckline 63.3
- **triple-bottom** [bullish, high, score 76.0, active] → target 72.57 — 3 đáy ~60.3, neckline 66.4
- **triple-bottom** [bullish, high, score 76.0, active] → target 71.6 — 3 đáy ~65.4, neckline 68.5
- **triple-bottom** [bullish, high, score 76.0, active] → target 69.24 — 3 đáy ~59.9, neckline 64.6
- **triple-top** [bearish, high, score 76.0, active] → target 70.87 — 3 đỉnh ~84.1, neckline 77.5
- **triple-top** [bearish, high, score 76.0, active] → target 75.67 — 3 đỉnh ~89.5, neckline 82.6
- **triple-top** [bearish, high, score 76.0, active] → target 78.63 — 3 đỉnh ~89.0, neckline 83.8
- **triple-top** [bearish, high, score 76.0, active] → target 79.37 — 3 đỉnh ~88.2, neckline 83.8
- **triple-top** [bearish, high, score 76.0, active] → target 77.8 — 3 đỉnh ~94.2, neckline 86.0
- **support-cluster** [bullish, high, score 75.1, active] — 2 pivot chạm vùng support
- **resistance-cluster** [bearish, high, score 72.9, active] — 2 pivot chạm vùng resistance
- **resistance-cluster** [bearish, high, score 70.9, active] — 3 pivot chạm vùng resistance
- **double-bottom** [bullish, medium, score 68.0, active] → target 56.38 — 2 đáy ~40.3, neckline 48.3
- **double-bottom** [bullish, medium, score 68.0, active] → target 50.48 — 2 đáy ~42.6, neckline 46.5
- **double-bottom** [bullish, medium, score 68.0, active] → target 56.61 — 2 đáy ~47.5, neckline 52.0
- **double-bottom** [bullish, medium, score 68.0, active] → target 66.0 — 2 đáy ~60.0, neckline 63.0
- **double-bottom** [bullish, medium, score 68.0, active] → target 72.24 — 2 đáy ~60.6, neckline 66.4
- **double-bottom** [bullish, medium, score 68.0, active] → target 68.55 — 2 đáy ~58.6, neckline 63.6
- **double-bottom** [bullish, medium, score 68.0, active] → target 63.89 — 2 đáy ~56.2, neckline 60.0
- **double-bottom** [bullish, medium, score 68.0, active] → target 64.17 — 2 đáy ~57.9, neckline 61.0
- **double-bottom** [bullish, medium, score 68.0, active] → target 77.9 — 2 đáy ~64.3, neckline 71.1
- **double-top** [bearish, medium, score 68.0, active] → target 71.5 — 2 đỉnh ~84.7, neckline 78.1
- **double-top** [bearish, medium, score 68.0, active] → target 70.4 — 2 đỉnh ~84.6, neckline 77.5
- **double-top** [bearish, medium, score 68.0, active] → target 78.85 — 2 đỉnh ~88.0, neckline 83.4
- **triple-bottom** [bullish, medium, score 66.0, active] → target 88.27 — 3 đáy ~74.5, neckline 81.4
- **triple-bottom** [bullish, medium, score 66.0, active] → target 87.5 — 3 đáy ~75.3, neckline 81.4
- **triple-bottom** [bullish, medium, score 66.0, active] → target 82.53 — 3 đáy ~75.9, neckline 79.2
- **triple-bottom** [bullish, medium, score 66.0, forming] → target 96.23 — 3 đáy ~79.6, neckline 87.9
- **triple-bottom** [bullish, medium, score 66.0, active] → target 89.03 — 3 đáy ~77.4, neckline 83.2
- **triple-bottom** [bullish, medium, score 66.0, active] → target 95.37 — 3 đáy ~77.0, neckline 86.2
- **triple-bottom** [bullish, medium, score 66.0, forming] → target 95.33 — 3 đáy ~84.5, neckline 89.9
- **triple-bottom** [bullish, medium, score 66.0, forming] → target 94.93 — 3 đáy ~84.9, neckline 89.9
- **triple-top** [bearish, medium, score 66.0, forming] → target 53.75 — 3 đỉnh ~61.4, neckline 57.6
- **triple-top** [bearish, medium, score 66.0, forming] → target 53.0 — 3 đỉnh ~62.2, neckline 57.6
- **triple-top** [bearish, medium, score 66.0, forming] → target 56.24 — 3 đỉnh ~63.1, neckline 59.7
- **triple-top** [bearish, medium, score 66.0, forming] → target 54.87 — 3 đỉnh ~65.0, neckline 60.0
- **triple-top** [bearish, medium, score 66.0, forming] → target 50.41 — 3 đỉnh ~65.1, neckline 57.8
- **triple-top** [bearish, medium, score 66.0, forming] → target 53.5 — 3 đỉnh ~60.9, neckline 57.2
- **triple-top** [bearish, medium, score 66.0, forming] → target 50.61 — 3 đỉnh ~60.6, neckline 55.6
- **triple-top** [bearish, medium, score 66.0, forming] → target 53.33 — 3 đỉnh ~64.8, neckline 59.0
- **triple-top** [bearish, medium, score 66.0, forming] → target 64.24 — 3 đỉnh ~70.8, neckline 67.5
- **triple-top** [bearish, medium, score 66.0, forming] → target 58.47 — 3 đỉnh ~71.9, neckline 65.2
- **triple-top** [bearish, medium, score 66.0, forming] → target 58.27 — 3 đỉnh ~72.1, neckline 65.2
- **triple-top** [bearish, medium, score 66.0, active] → target 67.77 — 3 đỉnh ~79.6, neckline 73.7
- **triple-top** [bearish, medium, score 66.0, active] → target 65.6 — 3 đỉnh ~85.4, neckline 75.5
- **triple-top** [bearish, medium, score 66.0, active] → target 65.07 — 3 đỉnh ~83.3, neckline 74.2
- **resistance-cluster** [bearish, medium, score 62.1, active] — 2 pivot chạm vùng resistance
- **double-bottom** [bullish, medium, score 58.0, active] → target 87.95 — 2 đáy ~74.8, neckline 81.4
- **double-bottom** [bullish, medium, score 58.0, active] → target 89.6 — 2 đáy ~76.8, neckline 83.2
- **double-bottom** [bullish, medium, score 58.0, active] → target 94.6 — 2 đáy ~77.8, neckline 86.2
- **double-bottom** [bullish, medium, score 58.0, active] → target 92.4 — 2 đáy ~75.4, neckline 83.9
- **double-bottom** [bullish, medium, score 58.0, forming] → target 95.4 — 2 đáy ~81.6, neckline 88.5
- **double-top** [bearish, medium, score 58.0, forming] → target 57.52 — 2 đỉnh ~63.0, neckline 60.2
- **double-top** [bearish, medium, score 58.0, forming] → target 55.04 — 2 đỉnh ~64.9, neckline 60.0
- **double-top** [bearish, medium, score 58.0, forming] → target 56.74 — 2 đỉnh ~65.9, neckline 61.3
- **double-top** [bearish, medium, score 58.0, forming] → target 51.07 — 2 đỉnh ~64.5, neckline 57.8
- **double-top** [bearish, medium, score 58.0, forming] → target 59.99 — 2 đỉnh ~69.2, neckline 64.6
- **double-top** [bearish, medium, score 58.0, forming] → target 58.02 — 2 đỉnh ~67.2, neckline 62.6
- **double-top** [bearish, medium, score 58.0, forming] → target 55.86 — 2 đỉnh ~61.3, neckline 58.6
- **double-top** [bearish, medium, score 58.0, forming] → target 50.82 — 2 đỉnh ~60.4, neckline 55.6
- **double-top** [bearish, medium, score 58.0, forming] → target 54.95 — 2 đỉnh ~61.4, neckline 58.2
- **double-top** [bearish, medium, score 58.0, forming] → target 53.63 — 2 đỉnh ~64.5, neckline 59.0
- **double-top** [bearish, medium, score 58.0, forming] → target 58.0 — 2 đỉnh ~72.4, neckline 65.2
- **double-top** [bearish, medium, score 58.0, forming] → target 63.35 — 2 đỉnh ~72.7, neckline 68.0
- **double-top** [bearish, medium, score 58.0, active] → target 66.0 — 2 đỉnh ~85.0, neckline 75.5
- **death-cross** [bearish, low, score 56.0, active] — SMA20 cắt xuống SMA50
- **Marubozu** [bearish, low, score 55.0, completed] — 
- **Marubozu** [bullish, low, score 55.0, completed] — 
- **Doji** [neutral, low, score 55.0, completed] — 
- **Marubozu** [bearish, low, score 55.0, completed] — 
- **Bearish Engulfing** [bearish, low, score 55.0, completed] — 
- **Marubozu** [bullish, low, score 55.0, completed] — 
- **Shooting Star** [bearish, low, score 55.0, completed] — 
- **Hammer** [bullish, low, score 55.0, completed] — 
- **Bullish Engulfing** [bullish, low, score 55.0, completed] — 
- **Marubozu** [bearish, low, score 55.0, completed] — 
- **Bearish Engulfing** [bearish, low, score 55.0, completed] — 
- **Marubozu** [bearish, low, score 55.0, completed] — 
- **Hammer** [bullish, low, score 55.0, completed] — 
- **Marubozu** [bearish, low, score 55.0, completed] — 
- **Bearish Engulfing** [bearish, low, score 55.0, completed] — 
- **resistance-cluster** [bearish, low, score 54.6, active] — 3 pivot chạm vùng resistance
- **resistance-cluster** [bearish, low, score 49.6, active] — 4 pivot chạm vùng resistance

### Tier 2 — trung bình (32)
- **falling-wedge** [bullish, high, score 70.0, active] → target 87.06 — falling wedge trên 40 phiên gần nhất
- **rounding-top** [bearish, low, score 57.6, forming] — Đỉnh cong, R²=0.63
- **head-shoulders** [bearish, low, score 56.0, active] → target 69.4 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 56.0, active] → target 78.4 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 56.0, active] → target 75.5 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 56.0, active] → target 67.9 — Vai-đầu-vai, đảo chiều giảm
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 66.36 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 53.64 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 52.76 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 66.6 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 71.17 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 68.51 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 70.68 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 56.0, active] → target 77.3 — Vai-đầu-vai ngược, đảo chiều tăng
- **no-supply** [bullish, low, score 50.0, completed] — Giảm yếu, volume thấp — cung cạn
- **no-demand** [bearish, low, score 50.0, completed] — Tăng yếu, volume thấp — cầu yếu
- **head-shoulders** [bearish, low, score 48.0, forming] → target 33.03 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 40.14 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 37.95 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 54.83 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 54.22 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 52.65 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 48.9 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 55.0 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 62.0 — Vai-đầu-vai, đảo chiều giảm
- **head-shoulders** [bearish, low, score 48.0, forming] → target 68.3 — Vai-đầu-vai, đảo chiều giảm
- **inverse-head-shoulders** [bullish, low, score 48.0, forming] → target 86.0 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 48.0, forming] → target 91.7 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 48.0, forming] → target 93.2 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 48.0, forming] → target 98.2 — Vai-đầu-vai ngược, đảo chiều tăng
- **inverse-head-shoulders** [bullish, low, score 48.0, forming] → target 91.9 — Vai-đầu-vai ngược, đảo chiều tăng
- **cup-handle** [bullish, low, score 45.0, forming] → target 103.8 — Cốc sâu 17%, hồi 99% miệng cốc

### Tier 3 — experimental (tham khảo) (8)
- **elliott-impulse-down** [bearish, low, score 48.0, active] — [experimental] Gợi ý 5 sóng đẩy giảm (chưa xác nhận wave count)
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 85.2-86.0
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 84.3-84.6
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 82.0-83.2
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 79.7-82.0
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 78.8-79.0
- **fvg-bullish** [bullish, low, score 48.0, active] — [experimental] Khoảng trống giá tăng 78.8-79.1
- **fvg-bearish** [bearish, low, score 48.0, active] — [experimental] Khoảng trống giá giảm 78.3-78.8

## Đường đã vẽ trên chart
- neckline: 93
- top: 89
- bottom: 77
- left_shoulder: 27
- head: 27
- right_shoulder: 27
- resistance: 12
- support: 10
- support-trendline: 1
- resistance-trendline: 1
- upper: 1
- lower: 1
- left_rim: 1
- right_rim: 1
- wave-12345: 1

## Chart
Mở file: `MWG_patterns_forecast.html`

---
*Disclaimer: Đây là công cụ nghiên cứu kỹ thuật tự động. Không mẫu hình nào đúng 100%. Không phải khuyến nghị đầu tư.*