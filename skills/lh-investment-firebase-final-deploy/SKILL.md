# LH Investment Firebase Final Deploy

## Purpose

Fix the recurring LH Investment Firebase issue where:

- web deploy "goes back" to an older version
- chart popup does not load
- final approved HTML gets overwritten by a rebuild
- `lightweight-charts.standalone.production.js` or `firebase_public/data/charts/*.json` disappears from live hosting

Use this skill whenever Hòa Đại ka asks to:

- fix LH Investment web on Firebase
- redeploy the final version
- fix chart not loading
- stop Firebase from reverting to the old version
- "deploy bản final hôm qua"

## Root Cause Pattern

The final approved frontend may live directly in:

- `stock-news-backend/firebase_public/stocks.html`
- `stock-news-backend/firebase_public/index.html`
- sometimes other committed static files under `firebase_public/`

But `build_firebase_cache_site.py` can regenerate HTML from:

- `stock-news-backend/app/dashboard_template.py`

If that template is older than the approved final static HTML, then running the build script will overwrite the final frontend and make the live site look like it reverted.

A second failure mode is that rebuild/deploy may omit static assets required by chart UI, especially:

- `firebase_public/lightweight-charts.standalone.production.js`
- `firebase_public/data/charts/*.json`

When those are missing, the popup opens but the chart cannot render.

## Golden Rule

If Hòa Đại ka asks to restore the **final approved version**, treat `firebase_public/` as canonical first.

Do **not** blindly rebuild HTML from `dashboard_template.py`.

## Standard Recovery Procedure

### 1) Identify the approved final commit

Inspect git history for `stock-news-backend/firebase_public/stocks.html` and related files.

Useful commands:

```powershell
git log --oneline -- stock-news-backend/firebase_public/stocks.html
git show <commit> -- stock-news-backend/firebase_public/stocks.html
```

In the known incident, the approved final commit was:

- `bfcd023` — `Add dedicated Wyckoff method panel to stock detail`

### 2) Verify whether live is missing the final markers

Fetch live HTML and check for expected markers.

Examples:

- `wyckoffDetailPane`
- `loadWyckoffMethod`
- `stockVolBox`
- `stockMacdBox`
- `stockRsiBox`
- `lightweight-charts`

If these are absent on live but present in the approved `firebase_public/stocks.html`, the live site is on the wrong version.

### 3) Verify chart dependencies

Check whether live has:

- `/lightweight-charts.standalone.production.js`
- `/data/charts/MWG.json`
- `/data/charts/index.json`

If any of these return 404, chart rendering will fail.

### 4) Restore the final static site from git

If restoring the known final version, checkout the canonical static files from the approved commit.

Examples:

```powershell
git checkout bfcd023 -- stock-news-backend/firebase_public/stocks.html stock-news-backend/firebase_public/index.html
```

If needed, restore the whole static tree:

```powershell
git checkout bfcd023 -- stock-news-backend/firebase_public
```

If Windows errors because directories were deleted, recreate them first:

```powershell
New-Item -ItemType Directory -Force -Path stock-news-backend\firebase_public | Out-Null
New-Item -ItemType Directory -Force -Path stock-news-backend\firebase_public\data | Out-Null
New-Item -ItemType Directory -Force -Path stock-news-backend\firebase_public\data\charts | Out-Null
New-Item -ItemType Directory -Force -Path stock-news-backend\firebase_public\assets | Out-Null
```

Then rerun the checkout.

### 5) Lock the build script so it cannot overwrite final HTML

Primary fix path requested by Hòa Đại ka:

- keep JSON/data rebuilding
- prevent HTML regeneration unless explicitly forced

Patch `stock-news-backend/build_firebase_cache_site.py` so `build_html()` returns early unless `ALLOW_HTML_REBUILD=1`.

Behavior after fix:

- `python build_firebase_cache_site.py` updates JSON/cache files
- final HTML in `firebase_public/*.html` remains untouched

### 6) Rebuild data only

After the lock is in place:

```powershell
python build_firebase_cache_site.py
```

Expected safe result:

- JSON files update
- `firebase_public/stocks.html` remains the approved final version
- `lightweight-charts.standalone.production.js` remains present
- `firebase_public/data/charts/` remains present

### 7) Deploy Firebase Hosting

```powershell
firebase deploy --only hosting
```

Project used in the known incident:

- Firebase project: `lhinvestment`
- Hosting URL: `https://lhinvestment.web.app`

### 8) Verify after deploy

Verify live hosting directly, not just by browser eyeballing.

Check:

```powershell
https://lhinvestment.web.app/stocks
https://lhinvestment.web.app/lightweight-charts.standalone.production.js
https://lhinvestment.web.app/data/charts/MWG.json
https://lhinvestment.web.app/data/charts/index.json
```

Expected:

- JS library returns 200
- chart JSON returns 200
- live HTML contains final markers

## Known Final Markers

These markers strongly indicate the approved final chart/stock popup build:

- `wyckoffDetailPane`
- `loadWyckoffMethod`
- `renderWyckoffMethodPanel`
- `data-analysis-tab="wyckoff"`
- `stockVolBox`
- `stockMacdBox`
- `stockRsiBox`
- `lightweight-charts.standalone.production.js`

## Important Warnings

- Do not assume `dashboard_template.py` is the source of truth.
- Do not delete `firebase_public/` unless you are ready to restore it from git immediately.
- If chart files are gone, deploying only HTML is not enough.
- Always verify live URLs after deploy.
- If user asks for "bản final hôm qua", prefer restoring committed `firebase_public/` from the target commit.

## Minimal Action Checklist

1. Identify final commit in git.
2. Confirm final markers in `firebase_public/stocks.html`.
3. Confirm chart assets exist locally.
4. Lock `build_firebase_cache_site.py` against HTML overwrite.
5. Rebuild data only.
6. Deploy hosting.
7. Verify live HTML + JS + chart JSON.

## When User Says "fix theo cách cũ"

Interpret it as:

- restore final static `firebase_public` version
- keep build script from regenerating HTML
- preserve chart library and chart JSON assets
- deploy and verify live
