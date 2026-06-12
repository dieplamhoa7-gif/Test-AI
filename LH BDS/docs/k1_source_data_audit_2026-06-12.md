# K1 / NVTC Source Data Audit - 2026-06-12

## Trigger
User reported that road `Điện Biên Phủ` missed the segment `Đinh Tiên Hoàng - Hai Bà Trưng` in NVTC lookup.

## Source checked
- Raw extracted source: `exports/k1_pdf_relevant_extract.json`
- Runtime parser: `k1_land_fee_lookup.js`

## Finding
The source data is not missing the segment. Page 20 contains:

```text
5 ĐIỆN BIÊN PHỦ CẦU ĐIỆN BIÊN PHỦ ĐINH TIÊN HOÀNG 234.100 163.900 140.500 1,67 1,67 1,67 1,67
  ĐINH TIÊN HOÀNG HAI BÀ TRƯNG 225.800 158.100 135.500 1,59 1,59 1,59 1,59
```

## Root cause
The old parser expected each row to repeat STT + road name. The K1/PDF tables often use continuation rows under the same road without repeating the road name. Those continuation rows were not picked up in direct lookup alternatives.

## Fix applied
Patched `k1_land_fee_lookup.js` in `extractRoadDirectCandidatesFromPage()` so that when a requested road is found on a source page, the parser scans the road block and extracts multiple price/K rows, including continuation rows.

Also added guards against noisy OCR candidates where the segment begins with leaked numbers or another road row.

## Verified example
For geo road `Điện Biên Phủ`, ward `Tân Định`, lookup now returns:

- Main candidate:
  - Segment: `CẦU ĐIỆN BIÊN PHỦ ĐINH TIÊN HOÀNG`
  - Residential: `234.100` nghìn đồng/m²
  - TMDV: `163.900` nghìn đồng/m²
  - SXKD: `140.500` nghìn đồng/m²
  - K: `1,67`
- Alternative / selectable segment:
  - Segment: `ĐINH TIÊN HOÀNG HAI BÀ TRƯNG`
  - Residential: `225.800` nghìn đồng/m²
  - TMDV: `158.100` nghìn đồng/m²
  - SXKD: `135.500` nghìn đồng/m²
  - K: `1,59`

## Audit note
A broader attempt to make the global `extractStreetEntries()` parse all continuation rows caused over-matching because the raw PDF extraction is line-collapsed and many Vietnamese street names have multi-word first tokens (`Nguyễn`, `Hoàng`, `Đinh`, etc.). That produced false roads like `NGUYỄN`, `HOÀNG`, `ĐIỆN`, so it was reverted.

Current safe approach:
- Keep global parser conservative.
- For NVTC coordinate lookup, use direct road-specific parser; it can safely scan continuation rows because the road name is already known from geocoder.

## Remaining risk
Some continuation rows may still need road-specific lookup context to be discovered. Avoid relying on a full global road index for continuation rows until a proper table extraction/indexer is built from page geometry or manually normalized tables.

## Recommended next hardening
Build a normalized K1 table index offline with fields:

```text
page, wardHeader, stt, road, segmentFrom, segmentTo, priceResidential, priceCommercial, priceBusiness, kResidential, kCommercial, kBusiness, kAgricultural, raw
```

This should use either:
1. geometry-aware PDF table extraction, or
2. road-block parser seeded by known road/STT boundaries per page.

For now, runtime NVTC lookup is fixed for the reported missing-continuation class.
