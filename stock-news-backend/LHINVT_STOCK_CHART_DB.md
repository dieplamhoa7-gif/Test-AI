# LHINVT Stock/Chart SQLite Database

Local DB for easier AI/query access:

```text
data/lhinvt_stock_chart.db

Model3 freshness gate uses this DB as the primary source before market gateway/Firebase fallback. On Render or another host, set:

```bash
LHINVT_STOCK_CHART_DB=data/lhinvt_stock_chart.db
```

Keep this DB refreshed by the daily chart/data pipeline before running Model3 reports.
```

Build/update:

```powershell
python build_lhinvt_stock_chart_db.py
```

Query helper:

```powershell
python query_lhinvt_stock_chart_db.py meta
python query_lhinvt_stock_chart_db.py latest MWG
python query_lhinvt_stock_chart_db.py ohlcv MWG --limit 20
python query_lhinvt_stock_chart_db.py chart-files MWG
python query_lhinvt_stock_chart_db.py warrants MWG
```

Main tables:

- `metadata` — DB freshness / counts.
- `symbols` — latest stock summary.
- `daily_ohlcv` — daily candles.
- `market_snapshot` — web card snapshot.
- `indicators_daily` — daily technical indicators.
- `chart_files` — local/public chart JSON freshness index.
- `warrants` — covered warrant/CW latest data.
- `news_meta` — lightweight news index.

Skill guide for AI agents:

```text
skills/lhinvt-stock-chart-db/SKILL.md
```
