---
name: macro-data-hub
description: Use this when Hòa asks for the latest Vietnam macro database, macro web data, SBV/OMO/interbank data status, or how to refresh/push macro data into reports/web.
---

# Macro Data Hub — Latest Vietnam Macro Database

## Goal
Maintain one canonical, continuously refreshed database for the VN macro web/report stack.

The hub consolidates daily macro snapshots into machine-readable JSON/CSV and mirrors them to the static macro web folder.

## Canonical files

Internal database:

- `FA/data/macro_data_hub/latest.json` — latest full database
- `FA/data/macro_data_hub/latest.csv` — flat table for Excel/manual checks
- `FA/data/macro_data_hub/macro_data_hub_YYYY-MM-DD.json` — dated archive

Web/static mirror:

- `Vi mo/data/macro_data_hub/latest.json`
- `Vi mo/data/macro_data_hub/latest.csv`
- `Vi mo/data/macro_data_hub/macro_data_hub_YYYY-MM-DD.json`
- `Vi mo/macro_data_hub_manifest.json`

If the macro web folder is deployed, the web should read:

```js
fetch('data/macro_data_hub/latest.json')
```

or first read manifest:

```js
fetch('macro_data_hub_manifest.json')
```

## Refresh command

From workspace root:

```powershell
cd FA
python build_macro_data_hub.py
```

This command:

1. Reads newest `FA/data/history/YYYY-MM-DD.json` snapshot.
2. Builds `FA/data/macro_data_hub/latest.json` + CSV + dated archive.
3. Mirrors the same database to `Vi mo/data/macro_data_hub/`.
4. Writes `Vi mo/macro_data_hub_manifest.json` for the web.

## Report build command

```powershell
cd FA
python build_report.py --date YYYY-MM-DD --out reports\vn_macro_report_YYYYMMDD.html
```

`build_report.py` is patched to read `FA/data/macro_data_hub/latest.json` and to fall back from old Pinetree timeline CSV to `FA/data/history/*.json` snapshots if the CSV is absent.

## Current dataset groups in hub

- `pinetree_daily`: interbank ON, deposit 12M, gov bonds, FX, VN indices, foreign flow, turnover, headline macro market fields.
- `vcb_fx`: VCB buy/sell FX rates for USD/EUR/CNY/JPY/GBP/KRW/SGD/AUD.
- `global_markets`: VIX, S&P500, Nasdaq, US10Y, DXY, Brent, Gold and 1D changes.
- `sbv_liquidity`: OMO/reverse repo, T-bill fields, total liquidity net, OMO rate, policy-rate placeholders.
- `sbv_interbank`: official SBV interbank rates when parse works; fallback to Pinetree ON when SBV PDF is blocked.
- `worldbank`: annual lagged macro indicators.
- `tradingeconomics_visible`: public visible page snapshot count/status.
- `fiinprox_excel`: FiinProX imported macro timeline summary.

## SBV logic

Primary issue: SBV official PDF may be blocked/rejected or parse-empty. Do not let this break the database.

Current fallback chain in `FA/macro/fetchers/sbv_rates.py`:

1. SBV weekly PDF official parser.
2. Pinetree latest daily snapshot for VND overnight interbank.
3. `FA/data/manual_override.json` if provided.

The fallback file glob must be `????-??-??.json` because snapshots are saved as `YYYY-MM-DD.json`.

## Quick checks

```powershell
cd FA
python macro\fetchers\sbv_rates.py pinetree
python build_macro_data_hub.py
python -m py_compile build_macro_data_hub.py build_report.py macro\fetchers\sbv_rates.py
```

Expected: `build_macro_data_hub.py` prints JSON like:

```json
{"status":"ok","datasets":7,"indicators":69,"out":"...FA/data/macro_data_hub","webOut":"...Vi mo/data/macro_data_hub"}
```

Dataset/indicator counts can grow as new sources are added.

## When Hòa asks “database mới nhất có gì?”

Read `FA/data/macro_data_hub/latest.json` and summarize:

- date / generatedAt
- dataset count / indicator count
- SBV OMO and interbank status
- missing indicators (`status: missing` rows)
- web mirror location

Keep the answer short unless asked for details.

## Commit/deploy discipline

After changing the macro hub pipeline:

1. Run refresh + compile checks.
2. Commit only relevant files, avoiding unrelated workspace noise.
3. If deploy tooling exists for `Vi mo/`, deploy after user approval if it publishes externally.
