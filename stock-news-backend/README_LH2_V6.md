# LH2 v6 — Leader Momentum Breakout (walk-forward) — 2026-06-06

## TL;DR
Mục tiêu **winrate > 70% VÀ avg return > 5% đồng thời là KHÔNG đạt được một cách bền vững** trên VN100 2023–2026 trong khung long-only breakout. Đây không phải lỗi tham số — nó là trần thống kê của dữ liệu, được chứng minh bằng grid/random search hơn 300.000 tổ hợp (entry + exit). Con số 75% / +6.2% của LH2 v5 chỉ đến từ **12 lệnh** (gần như toàn bộ rơi vào sóng tăng 2023, 0 lệnh năm 2025–2026) → đó là small-sample overfit, không tái lập được out-of-sample.

LH2 v6 vì vậy chọn **cấu hình robust nhất** (dương cả in-sample lẫn out-of-sample, ≥20 lệnh) thay vì ép một con số ảo.

## Vì sao mục tiêu bất khả thi (bằng chứng)
Win rate bị quyết định chủ yếu bởi *exit* (vị trí target/stop), còn avg return bị giới hạn bởi phân phối lợi nhuận của pool breakout. Hai đại lượng này trade-off với nhau. Đường biên đạt được (sau cooldown, toàn kỳ 2023–2026):

| Ràng buộc số lệnh | Max win-rate đạt được | Max avg-return đạt được |
|---|---|---|
| ≥ 8 lệnh  | 88.9% (nhưng avg chỉ +1.15%) | WR 77.8% @ avg +3.68% |
| ≥ 12 lệnh | ~66.7% @ avg ~+0.8% | WR 57% @ avg +3.1% |
| ≥ 20 lệnh | **~65–67%** | WR ~52% @ avg ~+4.3% |
| ≥ 40 lệnh | ~59% | WR ~52% @ avg ~+4.3% |

Số tổ hợp đạt đồng thời WR≥70% & avg≥5% với ≥12 lệnh: **0**. Pool breakout thô (3.959 tín hiệu) có WR nền chỉ 33% / avg ~0% — siết tới ngưỡng 70% WR buộc số lệnh tụt xuống <10 (overfit).

## Bộ chỉ báo (đã mở rộng so với v4/v5)
Giữ lõi momentum-breakout của LH2, bổ sung và thay thế:
- **RS-rank percentile** (xếp hạng `ret20` cross-sectional theo từng ngày) — thay band RS tuyệt đối `9–12` của v4/v5 vốn phụ thuộc regime nên "chết" ở 2025–2026.
- **ADX14** (sức mạnh xu hướng), **RSI14** (lọc vùng quá mua), **ATR%** + **distance-from-MA20 theo ATR** (chống mua đuổi khi đã giãn xa), **MACD hist**, **Bollinger-width percentile** (volatility squeeze trước breakout), **nearHigh252** (sát đỉnh 52 tuần), **MA50 alignment**, **market regime** (index > MA50), **breadth**, **OBV slope**, **VWAP slope**, **volume ratio**, **rangePos60**.
- **Exit**: classic target/stop + failure-exit (cắt sớm khi breakout không follow-through), tùy chọn **ATR trailing**.

## Kết quả walk-forward (anchored: IS 2023–2024 → OOS 2025–2026)

### Preset `BALANCED` (mặc định, khuyến nghị) — exit classic
| Cửa sổ | Lệnh | Win-rate | Avg net % | Σ net % |
|---|---|---|---|---|
| IS 2023–2024 | 11 | 63.6% | +4.21% | +46.4 |
| OOS 2025–2026 | 13 | 53.9% | +3.85% | +50.0 |
| **FULL 2023–nay** | **24** | **58.3%** | **+4.02%** | **+96.4** |

Theo năm: 2023 `3 lệnh/100%/+8.0%` · 2024 `8/50%/+2.8%` · 2025 `10/50%/+3.55%` · 2026-ytd `3/66.7%/+4.83%`. Có lệnh ở **mọi năm**, dương expectancy ở cả IS và OOS → robust, không overfit.

### Preset `HIGH_FREQ` (ưu tiên tần suất + win-rate OOS) — exit ATR-trailing
| Cửa sổ | Lệnh | Win-rate | Avg net % |
|---|---|---|---|
| IS 2023–2024 | 28 | 57.1% | +0.26% |
| OOS 2025–2026 | 40 | 65.0% | +2.20% |
| **FULL** | **68** | **61.8%** | **+1.40%** |

### So với baseline cũ
- LH2 v4: 58 lệnh, WR 44.8%, avg +1.7%.
- LH2 v5: 12 lệnh, WR 75%, avg +6.2% — **small-sample, 0 lệnh 2025–2026** (overfit).
- **LH2 v6 BALANCED: 24 lệnh, WR 58.3%, avg +4.02%, robust IS↔OOS** → cải thiện thực chất cả expectancy lẫn tính ổn định so với v4, và đáng tin hơn hẳn v5.

## Cách chạy
```
python build_lh2_v6.py                 # BALANCED (mặc định)
python build_lh2_v6.py --preset HIGH_FREQ
```
Cần `vn100_history_from_2023.json` đặt cạnh script (hoặc trong `./data/`). Output: `lh2_v6_<preset>_backtest.json` (kèm chi tiết từng lệnh + walk-forward) và `lh2_v6_<preset>_today_scan.json` (tín hiệu phiên mới nhất). Giả định: phí round-trip 0.5%/lệnh, entry = giá close phiên kế tiếp, một mã không mở chồng lệnh (cooldown).

## Khuyến nghị hướng đi tiếp (để thực sự nâng trần WR/return)
1. **Bỏ ràng buộc long-only breakout-chasing**: thử **pullback/retest entry** (mua khi giá kiểm định lại nền sau breakout) — thường nâng WR mà không hy sinh nhiều avg.
2. **Position sizing theo ATR/volatility** + quản trị rủi ro danh mục thay vì tối ưu WR per-trade (Kelly-fraction, risk parity).
3. **Mở rộng universe & lịch sử** (toàn HOSE, dữ liệu trước 2023) để có cỡ mẫu đủ cho ngưỡng WR≥70 có ý nghĩa thống kê.
4. **Ensemble/regime-switch**: dùng BALANCED khi regime risk-on, hạ tần suất khi index < MA50.

> Lưu ý: đây là khung phân tích định lượng phục vụ ra quyết định, không phải khuyến nghị mua/bán cá nhân hóa. Kết quả backtest không đảm bảo hiệu suất tương lai.
