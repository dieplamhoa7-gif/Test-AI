# Microsoft Teams raw extraction — Bee || Phân Tích Đầu Tư

Extracted by Tiểu đệ from Microsoft Teams web UI.

## Source chat

- Chat/group: `Bee || Phân Tích Đầu Tư`
- Platform: Microsoft Teams / SharePoint / OneDrive
- Status: Browser access works; chat is virtualized, full history must be collected via search/attachments/messages in batches.

## Important attachments discovered in visible/search panel

These appear to be high-value BĐS project source documents:

1. `Báo cáo FS Diamond Garden— 12_6_2026 1.pdf`
2. `23.12.11_DA 5.1ha_Kinh Do-TP.ThuDuc-3.700 nguoi.pdf`
3. `22052026_R&D_120 Đặng Văn Bi, Thủ Đức.pdf`
4. `Lô đất phường Phú Thọ Hòa.pdf`

## Links/messages visible

- `Link mở rộng đường LVV`
- Google Maps short link: `https://maps.app.goo.gl/qDbb6mJHvwhXw4Az6`

## File access attempts

### 23.12.11_DA 5.1ha_Kinh Do-TP.ThuDuc-3.700 nguoi.pdf

Opened from Teams into SharePoint/OneDrive.

Observed OneDrive URL:

```text
https://belgroupvn-my.sharepoint.com/personal/khoa_le_nkpros_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fkhoa%5Fle%5Fnkpros%5Fvn%2FDocuments%2FMicrosoft%20Teams%20Chat%20Files%2F23%2E12%2E11%5FDA%205%2E1ha%5FKinh%20Do%2DTP%2EThuDuc%2D3%2E700%20nguoi%2Epdf&parent=%2Fpersonal%2Fkhoa%5Fle%5Fnkpros%5Fvn%2FDocuments%2FMicrosoft%20Teams%20Chat%20Files&ga=1
```

Observed SharePoint embed URL contains UniqueId:

```text
bbb49c96-d7e7-437a-b324-73df03f92e4b
```

Teams/OneDrive showed options:
- Open in Browser
- Download
- Share
- Copy link

Clicking Download did not create a visible file in `C:\Users\HoaD-CVDT\Downloads` during the first attempt. Need continue with Copy link/Open/sharepoint direct fetch or viewer/OCR.

## Preliminary project candidates

### BDS-TEAMS-0001 — Kinh Đô / TP Thủ Đức 5.1ha

- Source document: `23.12.11_DA 5.1ha_Kinh Do-TP.ThuDuc-3.700 nguoi.pdf`
- Inferred from filename only until PDF content is parsed:
  - Area: `5.1 ha` = `51,000 m2`
  - Location: TP Thủ Đức
  - Population: `3,700 người`
- Needs extraction:
  - exact project name
  - address/coordinates
  - project type
  - planning: floors, FAR/HS SDĐ, population confirmation
  - legal status
  - land asking price
  - product selling price
  - cost/revenue/effectiveness

### BDS-TEAMS-0002 — Diamond Garden

- Source document: `Báo cáo FS Diamond Garden— 12_6_2026 1.pdf`
- Likely contains FS/financial feasibility report.
- Needs parse for project economics.

### BDS-TEAMS-0003 — 120 Đặng Văn Bi, Thủ Đức

- Source document: `22052026_R&D_120 Đặng Văn Bi, Thủ Đức.pdf`
- Needs parse for R&D/project info.

### BDS-TEAMS-0004 — Lô đất phường Phú Thọ Hòa

- Source document: `Lô đất phường Phú Thọ Hòa.pdf`
- Needs parse.

## Next extraction workflow

1. Use Copy link/Open in Browser for each attachment.
2. Download/source-read PDF where possible.
3. If download blocked, use Teams/SharePoint PDF viewer screenshots + OCR/page text.
4. Populate `projects_from_teams_draft.csv`.
5. Use `LH BDS/bds_engine/google_maps_geocoder.py` for addresses/map links.
6. Use `LH BDS/bds_engine/guland_playwright_scraper.py` and related scrapers for planning/price enrichment.
