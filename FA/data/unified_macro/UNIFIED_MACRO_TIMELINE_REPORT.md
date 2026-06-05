# Unified Macro Timeline + Code Coverage

Scope: all Excel macro files directly under `FA/`.

- Unified timeline rows: **9798**
- Unique indicators: **125**
- Output CSV: `FA/data/unified_macro/macro_timeline_unified.csv`
- Output JSON: `FA/data/unified_macro/macro_timeline_unified.json`
- Code coverage JSON: `FA/data/unified_macro/macro_code_coverage.json`

## Rows by category

- fx: 1184 rows; 4 indicators
- macro_growth_inflation: 1908 rows; 8 indicators
- money_credit: 1330 rows; 23 indicators
- other_macro: 3668 rows; 14 indicators
- rates: 582 rows; 11 indicators
- trade_bop: 1126 rows; 65 indicators

## Code coverage status

- covered_or_partial: 80 indicators
- not_found_in_code: 45 indicators

## Important not/weakly covered items to verify

- `Bán (VND-USD) (VCB)` (fx) — 516 rows
- `LSHĐ_USD - Cá nhân (M)` (fx) — 76 rows
- `LSHĐ_USD - Tổ chức (M)` (fx) — 76 rows
- `FDI_Số dự án cấp mới (YTD) (M)` (macro_growth_inflation) — 256 rows
- `FDI_Vốn đăng ký cấp mới (YTD) (M)` (macro_growth_inflation) — 256 rows
- `10. Tín dụng và vay nợ từ IMF` (money_credit) — 18 rows
- `8.1.1.1. Tổ chức tín dụng` (money_credit) — 18 rows
- `8.1.3. Tín dụng thương mại và ứng trước` (money_credit) — 18 rows
- `8.2.1.1. Tổ chức tín dụng` (money_credit) — 18 rows
- `8.3. Tín dụng thương mại và ứng trước` (money_credit) — 18 rows
- `5.1. Cán cân vốn: Thu` (trade_bop) — 18 rows
- `5.2. Cán cân vốn: Chi` (trade_bop) — 18 rows
- `A. CÁN CÂN VÃNG LAI` (trade_bop) — 18 rows
- `B. CÁN CÂN VỐN` (trade_bop) — 18 rows

## Notes

- This is an automated first-pass parser. It preserves source_file/sheet for audit. Human validation is still required before using in production scoring.
- Existing code has fetchers for Pinetree, VCB FX, yfinance global, vnstock market, WorldBank, SBV rates, SBV OMO. However a field is only production-ready after a successful run populates `FA/data/history/YYYY-MM-DD.json` with non-null data and matching schema.