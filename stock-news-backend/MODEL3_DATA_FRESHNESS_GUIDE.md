# Model3 Data Freshness Guide

Purpose: ensure every Model3 web/worker report uses the newest canonical data after Hòa Đại ka rebuilds database/data.

## Canonical source

Main canonical repo:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
```

Runtime worker clone:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\render_backend_work\stock-news-backend
```

The runtime clone must never be treated as source of truth. It only copies from canonical before each job.

## Version manifest

After each database/data build, update:

```text
data/model3_data_manifest.json
```

Required shape:

```json
{
  "version": "YYYY-MM-DDTHH:mm:ss+07:00",
  "updatedAt": "YYYY-MM-DDTHH:mm:ss+07:00",
  "files": [
    "data/lhinvt_stock_chart.db",
    "data/market_data.json",
    "data/v3_full_indicator_cache_v2.json",
    "data/lh_canonical_indicators_daily.json",
    "data/strategy_results_cache.json"
  ]
}
```

The worker reads this manifest on every job and syncs listed files into the runtime clone. If new canonical artifacts are added later, add them to `files[]` instead of patching worker code.

## Mandatory freshness checks

Before exporting Word/DOCX, worker must verify:

1. `lhinvt_stock_chart.db` has latest ticker row.
2. `strategy_results_cache.json` is today's/latest strategy build.
3. `lh_canonical_indicators_daily.json` matches the current DB/strategy build.
4. If ticker is absent from top BUY/WATCH strategy cache, Model3 must evaluate LH1-LH4 on-demand from `lh_canonical_indicators_daily.json`.
5. Macro context must include freshness metadata. If stale, report must explicitly say macro data is stale or trigger refresh first.

## Macro data source

Model3 macro context currently reads:

```text
FA/data/macro_data_hub/latest.json
Vi mo/data/macro_data_hub/latest.json
```

Build script:

```text
FA/build_macro_data_hub.py
```

This script reads latest snapshot from:

```text
FA/data/history/YYYY-MM-DD.json
```

and mirrors output to `Vi mo/data/macro_data_hub/`.

Important: `build_macro_data_hub.py` only packages the latest existing history snapshot. It does not itself fetch a newer snapshot. If `FA/data/history` has no file for today/latest market date, macro hub will remain stale.

## Current rule for AI/worker

- Always include `macroAgeDays` and `freshnessWarning` in macro context.
- If `freshnessWarning == "MACRO_STALE"`, do not phrase macro data as current.
- Either refresh macro history first, or write: "Dữ liệu vĩ mô đang stale; chỉ dùng như bối cảnh tham chiếu".

## Telegram group/database note

If fresh macro database is posted in Telegram group `Macro, investment 3`, OpenClaw needs a resolvable chat target/chat_id or a forwarded message from that group. Once available, AI can inspect the posted database path/content and update the canonical macro files or guide accordingly.
