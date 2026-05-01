# RS / V3 Architecture

## 1) RS engine riêng

Mục tiêu: tách toàn bộ công thức R/S khỏi `_calc_technical()` để chạy riêng, nhẹ hơn, xuất file output dùng lại.

- Module: `app/rs_levels.py`
- Hàm chính: `calc_rs_levels_only(...)`
- Script build cache: `build_rs_levels_only_cache.py`
- Output: `data/rs_levels_only_cache.json`

### Hàm R/S đang dùng

`app/rs_levels.py` đang dùng lại/tách riêng các công thức liên quan từ `app.market_data`:

- `_pivot_levels`
- `_pivot_from_recent`
- `_to_ohlc`
- `_build_support_resistance`
- `_safe_number`

Bên trong `_build_support_resistance` có các công thức phụ:

- `_swing_levels`
- `_volume_levels`
- `_vwap_value`
- `_donchian_levels`
- `_atr_value`
- `_dedupe_levels`
- `_strongest_levels`

### Chỉ báo/field RS output

- `pivotDay`
- `supportDay`, `resistanceDay`
- `supportDay2`, `resistanceDay2`
- `supportLevelsDay`, `resistanceLevelsDay`
- `nearSupportDay`, `nextSupportDay`
- `nearResistanceDay`, `nextResistanceDay`
- `activeSupportDay`, `activeResistanceDay`
- `supportZoneDay`, `resistanceZoneDay`
- `srStatusDay`
- `pivotWeek`, `supportWeek`, `resistanceWeek`
- `supportLevelsWeek`, `resistanceLevelsWeek`
- `activeSupportWeek`, `activeResistanceWeek`, `srStatusWeek`
- `pivotMonth`, `supportMonth`, `resistanceMonth`
- `supportLevelsMonth`, `resistanceLevelsMonth`
- `activeSupportMonth`, `activeResistanceMonth`, `srStatusMonth`
- `atr`
- `vwapDay`
- `donchianHighDay`, `donchianLowDay`, `donchianMidDay`
- `marketStructureDay`
- `ma20Anchor`, `ma50Anchor`, `ma200Anchor`

### Công thức RS gồm

- Pivot S/R
- Swing high/low
- Volume-by-price levels
- VWAP
- Donchian high/low/mid + market structure
- Fibonacci 0.382 / 0.5 / 0.618 trong candidate R/S
- MA20/50/200 anchor
- ATR để gom zone và tạo vùng hỗ trợ/kháng cự

## 2) V3 / calc không tính lại RS

Mục tiêu tiếp theo: V3/calc chỉ đọc `data/rs_levels_only_cache.json` để lấy R/S.

### File V3

- Gốc archived: `archive_unused_strategy_files/20260430_200953/backtest_confirmed_support_v3.py`
- Rerun hiện tại + full indicator snapshot: `rerun_v3_original_with_full_indicators.py`
- Export setup: `build_v3_setups_with_future.py`
- Optimize từ saved setups: `optimize_v3_from_saved_setups.py`

### Chỉ báo V3 gốc thực sự dùng để lọc lệnh

- R/S zone từ RS output
- `resistanceLevelsDay` từ RS output
- MA20
- MA50
- RSI14
- MACD line
- MACD signal
- MACD histogram
- Volume
- Volume average 20
- ATR14
- ret5
- future candles để backtest

### Full PTKT snapshot có thể tham chiếu, nhưng không phải filter gốc V3

- ADX14
- +DI / -DI
- MA200
- Bollinger upper/lower/percent
- VWAP
- Donchian high/low/mid
- Market structure
- Volume ratio
- Divergence
- Effective trend
- Signal score
- Risk reward
- Fibonacci levels nằm trong RS candidates

### Chưa thấy field trực tiếp trong `_calc_technical()` hiện tại

- Ichimoku direct fields
- Keltner direct fields
- ROC20 direct field

Nếu cần dùng 3 nhóm này, phải thêm công thức riêng vào indicator engine/cache, không nên trộn vào RS engine.

## Next implementation

1. Giữ `app/rs_levels.py` là RS-only engine.
2. Mở rộng `build_rs_levels_only_cache.py` cho phép truyền danh sách mã / output path / exclude.
3. Patch V3 để đọc `data/rs_levels_only_cache.json` thay vì gọi `_calc_technical()` để lấy R/S.
4. Nếu cần full indicator, tạo indicator cache riêng, ví dụ `data/indicator_cache.json`, không tính R/S trong đó nữa.
