# LH Investment After-Close Update Pipeline

Mục tiêu: gom các bước cập nhật dữ liệu sau phiên vào một nơi để bot/GitHub Actions chạy lúc 15:30 ICT mỗi ngày giao dịch, không làm web back về version cũ.

## Lịch chạy

- GitHub Actions: `.github/workflows/refresh-eod-stocks-lh.yml`
- Cron: `30 8 * * 1-5` UTC = `15:30` Asia/Saigon, thứ 2-6.

## Entry point

```bash
python lh_after_close_update/run_lh_after_close_update.py
```

Runner này gọi pipeline gốc:

```bash
python run_after_close_output_lh.py
```

Sau đó chạy guard chống rollback:

```bash
python lh_after_close_update/verify_no_old_version_regression.py
```

## Các file liên quan

- `run_after_close_output_lh.py` — pipeline chính sau phiên.
- `update_popup_ichimoku_all_symbols.py` — tính lại Mây Ichimoku / Trạng thái mây / Tenkan-Kijun cho popup cổ phiếu theo Day/Hour/Week/Month khi đủ dữ liệu.
- `build_firebase_cache_site.py` — chỉ refresh data; HTML phải hard-lock, không rebuild frontend.
- `verify_lh_final_frontend_markers.py` — guard marker frontend final.
- `lh_after_close_update/verify_no_old_version_regression.py` — guard bổ sung chống back version cũ.
- `lh_after_close_update/file_manifest.json` — manifest để bot khác biết các file update chính.

## Nguyên tắc an toàn

1. Không sửa layout/frontend nếu không có yêu cầu rõ.
2. `firebase_public/*.html` là bản final/canonical.
3. Nếu cần cập nhật popup, sửa output JSON (`market_data.json`, `market_watch.json`) hoặc script tính data, không sửa HTML.
4. Sau build/deploy phải verify marker final:
   - `20260621-lh-final-chartfix-1936`
   - `wyckoffDetailPane`
   - `loadWyckoffMethod`
   - `stockVolBox`
   - `loadAutoChart`
   - `Ichimoku`
5. `build_firebase_cache_site.py` phải giữ hard-skip HTML: `HARD-SKIPPED`.
