# MWG Pattern Engine

Module detect mẫu hình kỹ thuật + dự báo giá cho cổ phiếu MWG (mở rộng được cho mã khác).
Map từ thư viện mẫu hình PTKT, phân 3 tầng theo độ tin cậy detect tự động.

## Cài đặt

```bash
pip install -r requirements.patterns.txt
# TA-Lib là optional — engine tự fallback sang custom detector nếu không cài được.
```

## Chạy

```bash
python run_mwg_pattern_forecast.py <đường_dẫn_csv> <thư_mục_output>
# Ví dụ:
python run_mwg_pattern_forecast.py MWG.csv exports
```

Input CSV cần cột: `time, open, high, low, close, volume` (hoặc JSON có các khóa tương tự).
Engine tự nhận diện khung thời gian (daily/weekly/monthly).

## Output

- `MWG_patterns_forecast.json` — toàn bộ pattern + forecast + summary (máy đọc).
- `MWG_patterns_forecast.html` — chart Plotly tương tác (nến + S/R + trendline + pattern + forecast band).
- `MWG_pattern_forecast_summary.md` — báo cáo tóm tắt theo tầng tin cậy.

## Phân tầng (tier)

| Tier | Nghĩa | Confidence trần |
|------|-------|-----------------|
| 1 | Rule-based rõ ràng, tin cậy | high |
| 2 | Detect được, nhạy tham số | medium |
| 3 | Experimental (harmonic/Elliott/SMC/Wyckoff) | low (khóa cứng) |

Xem `MWG_pattern_mapping.docx` để biết chi tiết pattern nào map vào hàm nào.

## Kiến trúc

```
pattern_engine/
  core.py            # load, indicators, pivot engine (có fallback TA-Lib/scipy)
  candlesticks.py    # mẫu nến (TA-Lib + custom)
  chart_patterns.py  # Tier 1-2: S/R, trendline, double/triple, H&S, triangle,
                     #   wedge, channel, darvas, cup-handle, rounding, flag,
                     #   spring/upthrust, gap, VSA, indicator
  experimental.py    # Tier 3: harmonic, Elliott, smart money, Wyckoff
  forecast.py        # trend regression + damping + ATR band + scenarios
  plot.py            # chart Plotly
run_mwg_pattern_forecast.py  # orchestrator
```

## Nguyên tắc

- **Không nhìn dữ liệu tương lai**: pivot có confirm-lag, forecast chỉ fit dữ liệu quá khứ.
- **Không bịa**: pattern không đủ bằng chứng thì không xuất.
- **Research-only**: mọi forecast là xác suất/kịch bản, không phải khuyến nghị đầu tư.

## Mở rộng

- Với dữ liệu **daily** (500+ nến), các detector Tier 3 và nhóm bị bỏ (Diamond, Pennant,
  harmonic hiếm, Elliott corrective) sẽ đáng tin hơn — chỉ cần hạ ngưỡng pivot và bật thêm.
- Đổi mã khác: chỉ cần đổi file CSV input; sửa nhãn "MWG" trong runner nếu muốn.
- Tùy chỉnh: `find_pivots(distance=...)`, `forecast(horizon=..., fit_window=...)`,
  ngưỡng trong từng detector.

## Lưu ý không ghi đè frontend

Output mặc định vào thư mục bạn chỉ định (vd `exports/`). Engine KHÔNG đụng vào
`firebase_public/*.html`. Nếu muốn đẩy JSON vào `firebase_public/data/patterns/`,
trỏ tham số output tới đó.

---

## Backtest chỉ báo (mới)

Module `backtest_indicators.py` + script `run_backtest.py` đánh giá hiệu quả từng
chỉ báo PTKT trên lịch sử, để CHỌN LỌC thay vì dùng cảm tính.

```bash
python run_backtest.py <csv_path> [symbol] [out_dir]
# Ví dụ:
python run_backtest.py MWG.csv MWG exports
```

Output: `<symbol>_indicator_backtest.json` + `.md` (bảng xếp hạng + gợi ý nhóm).

### Phương pháp (chống ảo tưởng hiệu quả)
- Long-only (hợp cổ phiếu VN không bán khống).
- Không nhìn tương lai: tín hiệu bar t → vào lệnh giá MỞ CỬA bar t+1.
- Trừ phí round-trip 0.3%/lệnh.
- So với baseline buy & hold — chỉ báo phải THẮNG việc cứ giữ mới đáng dùng.
- 2 kiểu thoát: giữ cố định N phiên (4/8/12) + thoát khi đảo chiều.
- Chỉ báo <8 lệnh đánh dấu "ít mẫu" — kết luận yếu.

### 14 chỉ báo (TA-Lib)
RSI (quá bán + cắt 50), MACD cross, Golden Cross SMA20/50, EMA12/26 cross,
Giá cắt SMA20, Stochastic, CCI, ADX +DI/-DI, Bollinger, Williams %R, MFI,
Aroon, Parabolic SAR.

### ⚠ Cảnh báo quan trọng về kết quả trên dữ liệu tuần
Với 133 nến tuần, mỗi chỉ báo chỉ sinh 1-6 tín hiệu — KHÔNG đủ mẫu để kết luận
chỉ báo nào "tốt nhất". Để backtest có giá trị thật:
- Dùng dữ liệu DAILY (~600 nến → mỗi chỉ báo 30-50 lệnh).
- Backtest trên RỔ NHIỀU MÃ, không riêng một cổ phiếu.

Phát hiện nhất quán (dù mẫu nhỏ): nhóm trend-following (Golden/EMA cross, ADX, SAR)
nhỉnh hơn nhóm mean-reversion (RSI, Stoch, CCI) trên cổ phiếu uptrend mạnh như MWG.

## Chart có nhãn mẫu hình (cập nhật)

`plot.py` giờ vẽ NHÃN CHỮ + ký hiệu cho từng mẫu hình:
- Marker: tam giác lên=đáy, tam giác xuống=đỉnh, tròn=vai, sao=đầu (H&S), mũi tên=spring/upthrust.
- Đường màu theo loại: hỗ trợ xanh, kháng cự đỏ/hồng, neckline cam đứt nét, dự báo xanh dương chấm.
- Box/zone cho Darvas, FVG, Order Block.
- Gộp pattern trùng, mở rộng trục để nhãn forecast không bị cắt.
- `render_preview.py` xuất bản PNG tĩnh (matplotlib) để xem nhanh.
