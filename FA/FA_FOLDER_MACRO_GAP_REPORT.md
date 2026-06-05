# FA folder macro files - fields and source gaps

Scope: `C:/Users/HoaD-CVDT/.openclaw/workspace/FA` only.

## Files found

- `FiinProX_Can can thuong mai_20262_20260605.xlsx`
- `FiinProX_DE_Du_lieu_vi_mo_20260605 (1).xlsx`
- `FiinProX_DE_Du_lieu_vi_mo_20260605 (2).xlsx`
- `FiinProX_DE_Du_lieu_vi_mo_20260605 (3).xlsx`
- `FiinProX_DE_Du_lieu_vi_mo_20260605.xlsx`
- `FiinProX_Lai suat huy dong cua cac ngan hang_20266_20260605.xlsx`
- `FiinProX_Lai suat thong ke cua NHNN_20266_20260605.xlsx`
- `FiinProX_Nghiep vu thi truong mo_20200604_20260604_20260605.xlsx`

## Macro data in these Excel files

| File | Main data fields | Does our source pipeline already fetch it? | Gap status |
|---|---|---|---|
| `FiinProX_Can can thuong mai_20262_20260605.xlsx` | Balance of payments/current account; goods export FOB; goods import FOB; net goods; services export/import/net; investment income; quarterly USD data from Q3/2021 onward | Not in current LH macro pipeline | **Gap**: no BOP/trade-balance fetcher yet. Need FiinProX export, GSO/customs/SBV/BOP source. |
| `FiinProX_DE_Du_lieu_vi_mo_20260605*.xlsx` | Monetary and macro data: M2, deposits by economic org/residents, likely credit/macro monthly series; plus FX weekly sheets and other macro sheets | Partly: USD/VND can be fetched via Pinetree/VCB; WorldBank slow macro exists; no full M2/deposit/credit monthly pipeline | **Major gap**: M2, deposits, credit/monthly macro series from FiinProX not currently automated except limited/free substitutes. |
| `FiinProX_Lai suat huy dong cua cac ngan hang_20266_20260605.xlsx` | Deposit rates by banks/terms | Only Pinetree has one deposit 12M snapshot, not bank-by-bank/term history | **Gap**: need bank deposit-rate history source or keep FiinProX/manual import. |
| `FiinProX_Lai suat thong ke cua NHNN_20266_20260605.xlsx` | SBV/statistical interest rates/policy rates | `FA/macro/fetchers/sbv_rates.py` exists but must verify success; current old pipeline only had unreliable SBV probe | **Partial/gap**: fetcher exists in FA folder, but need test/normalize/history before saying source is live. |
| `FiinProX_Nghiep vu thi truong mo_20200604_20260604_20260605.xlsx` | Open market operations/OMO from 2020-06-04 to 2026-06-04 | `FA/macro/fetchers/sbv_omo.py` exists; old LH pipeline did not have OMO data | **High-value gap/partial**: Excel has exactly the OMO history we lacked. Need import it and validate fetcher. |

## Code/data already present inside FA folder

- `FA/macro/daily_runner.py`
- `FA/macro/source_probe.py`
- `FA/macro/fetchers/pinetree.py`
- `FA/macro/fetchers/sbv_omo.py`
- `FA/macro/fetchers/sbv_rates.py`
- `FA/macro/fetchers/vcb_fx.py`
- `FA/macro/fetchers/vnstock_market.py`
- `FA/macro/fetchers/worldbank_macro.py`
- `FA/macro/fetchers/yfinance_global.py`
- `FA/macro/scoring/regime_score.py`
- `FA/macro/storage/macro_history.py`
- `FA/data/source_registry.json`
- `FA/data/manual_override.json`
- `FA/data/history/2026-06-05.json`
- `FA/macro_report.js`
- `FA/claude_handoff/vn_macro_research_pack_2026-06-05.zip`

## Answer to Đại ka

Earlier I had **not** included these FA folder files. After entering `workspace/FA`, the key missing/high-value files are the FiinProX Excel exports, especially OMO, SBV rates, deposit rates, M2/deposits/credit, and BOP/trade balance. These are richer than the old Pinetree snapshot and should be imported into the macro source registry/history.
