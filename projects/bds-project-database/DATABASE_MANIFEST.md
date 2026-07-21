# BĐS Teams Database Manifest

Source chat: Microsoft Teams — `Bee || Phân Tích Đầu Tư`

Extraction coverage confirmed from Teams web:

- Earliest visible chat event/message: `7/18/2022 3:31 PM`
- Latest captured period: July 2026
- Extraction method: read-only DOM `innerText` from Teams message viewport; no chat input/send/react actions.

## Database layers

### 1. `teams_candidate_chunks_with_dates.json`

Raw parsed BĐS-related Teams chunks with structured date fields.

Important fields:

- `source_file`: raw scroll batch file
- `sender`: parsed sender when available
- `report_date`: ISO date inferred from Teams timestamp/date heading
- `report_datetime_raw`: original Teams timestamp/date heading
- `text`: raw Teams-rendered text chunk

Current count: 1001 records.

### 2. `teams_candidate_chunks_with_dates.md`

Human-readable review version of the JSON chunks.

### 3. `project_mentions_from_teams_full.csv`

Mention-level database. Each row is a project/deal-related message chunk with extracted facts.

Important fields:

- `mention_id`
- `chunk_id`
- `source_file`
- `source_chat`
- `report_date`
- `report_datetime_raw`
- `sender`
- `project_name_hint`
- `map_urls`
- `land_area_mentions`
- `price_mentions`
- `far_mentions`
- `population_mentions`
- `irr_mentions`
- `npv_mentions`
- `excerpt`

Use this as the source-of-truth extracted database because it preserves the Teams message text/date.

### 4. `project_master_candidates_from_mentions.csv`

Auto-grouped project/deal candidates built from mentions. This is a review/mastering table, not final deduped truth yet.

Important fields:

- `candidate_key`
- `existing_project_id`
- `project_name_candidate`
- `mention_count`
- `first_report_date`
- `latest_report_date`
- `map_urls`
- `land_area_mentions`
- `price_mentions`
- `sample_excerpt`

Current count: 271 candidates.

### 5. `projects_from_teams_draft.csv`

Earlier manually curated master draft. Currently 41 rows and now includes:

- `report_date`
- `report_datetime_raw`

Only a few rows were automatically backfilled because many old summaries do not exactly match raw Teams chunks. Do not treat blank dates here as missing source date; use mention DB/chunks for source timestamp lookup.

## Limitations

- Message text is captured from Teams-rendered DOM and should reflect visible Teams text.
- PDF/image/attachment contents are not fully OCR/parsed yet unless their text appeared in Teams message preview.
- Teams virtualized chat required scroll batches; the earliest group creation message captured is 18/07/2022, indicating full chat timeline for this group.

## Build scripts

- `parse_teams_batches_with_dates.py`: parses raw batch files into date-aware chunks.
- `build_project_mentions_db.py`: extracts mention-level facts from chunks.
- `build_project_master_candidates.py`: groups mention hints into project/deal candidates.
- `add_report_dates_to_projects.py`: adds/backfills report date columns into curated draft CSV.
