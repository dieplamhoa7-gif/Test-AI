# BĐS Map Dashboard

Local static web dashboard for the Teams BĐS database.

## Run

From this folder:

```powershell
python -m http.server 8765
```

Open:

```text
http://127.0.0.1:8765/index.html
```

## Features

- Leaflet/OpenStreetMap interactive map.
- Markers for projects/deals with resolved coordinates.
- Popup shows key investment fields: report date, area, price/cost, selling price, FAR, population, IRR.
- Sidebar project table.
- Clicking a table row zooms/focuses the map marker.
- Search/filter by project text, status, type.

## Data source

- `projects_data.js` generated from:
  - `project_master_candidates_from_mentions.csv`
  - `projects_from_teams_draft.csv`
  - `map_link_resolution_all.json`

Current first-pass limitation: only projects/deals with resolved coordinates are shown. More markers will appear after resolving additional Google Maps links/geocoding addresses.
