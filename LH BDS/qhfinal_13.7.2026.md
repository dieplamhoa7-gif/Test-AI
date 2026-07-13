# QH Final - 13.7.2026

## Mục tiêu chốt

Trang Quy hoạch của LH Real Estate dùng lại **layout cũ/ban đầu**, bỏ QH Việt khỏi UI và flow tự động, thêm nguồn chính thức **GIS Xây dựng TP.HCM**, đồng thời bật lại **Guland** để đối chiếu.

Live URL:

- https://lhrealestate.web.app/quyhoach.html

## Trạng thái frontend

File chính:

- `public_final_2026_07_11/quyhoach.html`

Yêu cầu đã chốt:

- Giữ layout cũ gồm các khối:
  - Kết quả vị trí
  - Đồ án quy hoạch
  - Chỉ tiêu ô đất / chức năng đất
  - 3 nguồn đối chiếu
  - Cảnh báo kiểm tra
- Bỏ QH Việt khỏi frontend/UI.
- Không còn text kiểu `Bo qua (includeQhViet=false)` hoặc block QH Việt.
- Thêm GIS Xây dựng TP.HCM làm nguồn chính thức.
- Bật lại Guland trong request chính để đối chiếu.

Request frontend hiện dùng:

```js
includeQhViet: false
includeGuland: true
```

HTML live đã kiểm:

```js
{
  hasNoAutoText: false,
  hasIncludeGulandTrue: true,
  hasQHViet: false
}
```

## Trạng thái backend

File chính:

- `backend/planning_server.js`
- `backend/gisxaydung_client.js`
- `backend/guland_popup_parser.js`

Backend `/planning/lookup` hiện trả thêm:

- `gisxaydung`
- `planning.exact_indicators`
- `raw.official_lots`

GIS Xây dựng TP.HCM là nguồn chính thức tự động.

Endpoint/layer chính đã dùng:

- `https://api-gisxaydung.tphcm.gov.vn/arcm/rest/services/HCM/ThuaDat/FeatureServer/0/query`
- `HCM/SuDungDat_QHPK_HCM/FeatureServer/2`
- `HCM/SuDungDat_QHPK_HCM/FeatureServer/3`
- `HCM/QHCTinh_SDD_2025/FeatureServer/1`

## Kết quả test tọa độ mẫu

Tọa độ mẫu:

```txt
10.708963884321415, 106.73778019006706
```

GIS Xây dựng trả:

```json
{
  "gisOk": true,
  "chuc_nang_dat": "Đất ở hiện hữu cải tạo giữ lại",
  "ma_quy_uoc": "NNO",
  "tang_cao": "3",
  "mat_do_xay_dung": 40,
  "he_so_su_dung_dat": null,
  "dan_so_lo_o_pho": "514",
  "dien_tich": 31860,
  "to_thua": "18/68",
  "dien_tich_thua": 629.9,
  "phuong_xa": "Phường Phú Thuận"
}
```

Guland qua tunnel trả OK:

```json
{
  "gulandOk": true,
  "planning": [
    {
      "code": "ODT",
      "area_m2": 2355.39,
      "land_use": "Đất ở đô thị",
      "height": "3",
      "density": 40,
      "far": null
    },
    {
      "code": "DGT",
      "area_m2": 160.41,
      "land_use": "Đất giao thông"
    },
    {
      "code": null,
      "land_use": "Đất ở hiện hữu cải tạo giữ lại",
      "area_m2": 2515.8,
      "kind": "construction_planning"
    }
  ]
}
```

## Commits liên quan

Các commit quan trọng đã tạo:

- `757ad8ea8 Add GIS Xay dung planning lookup`
- `4fe9b3f4d Implement automated GIS planning flow` *(đã bị thay bằng rollback layout cũ sau đó)*
- `bdf8a392b Fix planning page missing stylesheet`
- `7ac8f326c Rebalance planning page into result tables` *(đã bị thay bằng rollback layout cũ sau đó)*
- `449797162 Restore original planning page layout`
- `d8e34f7b3 Keep old planning layout with GIS source`
- `cb1c9d34c Enable Guland in planning page`

Commit hiện tại cần giữ làm trạng thái final:

- `cb1c9d34c Enable Guland in planning page`

## Lưu ý vận hành

- Không redeploy Cloudflare Worker vì repo thiếu source Worker đầy đủ.
- Chỉ deploy Firebase hosting khi đổi frontend.
- Backend local/tunnel phải chạy để web live gọi `/planning/lookup`.
- QH Việt không dùng nữa trong flow hiện tại.
- Nếu Guland chậm/treo, kiểm backend parser/browser trước, không đổi layout frontend lớn.

## Deploy

Firebase hosting:

```bash
firebase deploy --only hosting:lhrealestate --project hoa-investment
```

Site:

```txt
https://lhrealestate.web.app
```
