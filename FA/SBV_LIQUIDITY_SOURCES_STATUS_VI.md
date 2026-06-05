# Trạng thái nguồn SBV liquidity: tín phiếu, reverse repo, lãi suất

Ngày kiểm tra: 2026-06-05

## Nguồn đã xác định

1. **Nghiệp vụ thị trường mở / Reverse Repo**
   - URL: `https://www.sbv.gov.vn/vi/web/sbv_portal/nghiệp-vụ-thị-trường-mở`
   - Truy cập được bằng Chrome.
   - Scrape được bảng visible.
   - Ngày dữ liệu mới nhất test: 04/06/2026.

2. **Thông tin chào bán tín phiếu NHNN**
   - URL đúng không dấu: `https://www.sbv.gov.vn/vi/web/sbv_portal/thong-tin-chao-ban-tin-phieu-nhnn`
   - Truy cập được bằng Chrome.
   - Trang hiện hiển thị **thông báo chào bán**, không phải kết quả phát hành thực tế.
   - Ô `Khối lượng Tín phiếu NHNN phát hành (theo mệnh giá) (nếu công bố) (VNĐ)` hiện trống trong lần test.
   - Vì vậy code để `tbillIssueBn = null`, không fake số.

3. **Diễn biến thị trường ngoại tệ và thị trường liên ngân hàng tuần**
   - Article tìm được từ SBV homepage:
     `Diễn biến thị trường ngoại tệ và thị trường liên ngân hàng tuần từ 25-29.5.2026`
   - PDF link tìm được:
     `https://www.sbv.gov.vn/documents/20117/0/25-29.5.2026.pdf/3b4c3a06-501d-4082-f83d-246e4949fdbe?t=1780476384602`
   - Chrome article truy cập được, nhưng PDF download bằng request bị timeout từ môi trường hiện tại.
   - Code đã có browser fallback để tìm article/PDF mỗi ngày, nếu tải được sẽ parse ON/1W/2W/1M/3M/6M/9M.

## File code mới

- `FA/macro/fetchers/sbv_liquidity.py`

Module này tổng hợp:

- OMO / Reverse Repo phát hành
- Tín phiếu chào bán
- Policy rates placeholder
- Interbank rates từ SBV weekly PDF qua fallback
- Summary daily liquidity

Output:

- `FA/data/sbv_liquidity/latest.json`
- `FA/data/sbv_liquidity/YYYY-MM-DD.json`

Đã tích hợp vào daily runner:

- `FA/macro/daily_runner.py`
- Snapshot key: `sbvLiquidity`

## Test output hiện tại

Từ `FA/data/sbv_liquidity/latest.json`:

```json
{
  "date": "2026-06-04",
  "reverseRepoIssueBn": 3000.0,
  "reverseRepoMaturityBn": null,
  "reverseRepoOutstandingBn": null,
  "reverseRepoNetBn": 3000.0,
  "tbillIssueBn": null,
  "tbillMaturityBn": null,
  "tbillOutstandingBn": null,
  "tbillNetBn": null,
  "totalLiquidityNetBn": 3000.0,
  "omoRate": 4.5,
  "discountRate": null,
  "refinancingRate": null
}
```

## Những dòng trong ảnh đã/đang xử lý

| Chỉ số | Trạng thái |
|---|---|
| Reverse Repo KL phát hành | Đã scrape được từ OMO page |
| Reverse Repo KL đáo hạn | Chưa có, cần rolling maturity schedule |
| Reverse Repo KL lưu hành | Chưa có, cần rolling outstanding từ lịch sử phát hành/đáo hạn |
| Bơm hút ròng Reverse Repo | Đã có phần phát sinh ngày, hiện `reverseRepoNetBn` |
| Tín phiếu KL phát hành | Nguồn có, nhưng trang SBV hiện không công bố khối lượng trong ô visible |
| Tín phiếu KL đáo hạn | Chưa có, cần lịch sử phát hành + kỳ hạn để tính đáo hạn |
| Tín phiếu KL lưu hành | Chưa có, cần rolling outstanding hoặc nguồn công bố riêng |
| Bơm hút ròng tín phiếu | Chưa tính vì thiếu phát hành/đáo hạn thực tế |
| Tổng bơm hút ròng | Có tạm phần OMO; đầy đủ cần tín phiếu |
| Lãi suất OMO/Reverse Repo | Đã có `omoRate` |
| Lãi suất tái chiết khấu | Chưa visible trên home; cần source cụ thể hoặc manual/source khác |
| Lãi suất tái cấp vốn | Chưa visible trên home; cần source cụ thể hoặc manual/source khác |
| Lãi suất BQ liên NH ON/1W/2W/1M/3M/6M/9M | PDF source đã tìm được; download hiện timeout, parser fallback đã gắn để thử daily |

## Kết luận

Đã làm đầy đủ phần có thể scrape công khai ngay từ SBV visible page. Những field còn `null` không phải bỏ sót code đơn giản, mà do nguồn visible hiện chưa công bố đủ hoặc PDF download đang timeout. Không được tự bịa số.

Bước tiếp theo để hoàn thiện 100%:

1. Tìm nguồn kết quả phát hành tín phiếu thực tế, không chỉ thông báo chào bán.
2. Nếu không có public result page, dùng FiinProX/manual export làm backfill cho tín phiếu.
3. Dùng lịch sử phát hành + kỳ hạn để tự tính đáo hạn/lưu hành.
4. Thử PDF download bằng Chrome download thật hoặc endpoint mirror để parse đủ interbank kỳ hạn.
5. Bổ sung nguồn policy rates chính thức nếu box `Lãi suất` của SBV không expose text.
