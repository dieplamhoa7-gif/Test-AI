# Schema database dự án BĐS

## 1. Bảng `projects`

Thông tin tổng quan từng dự án/deal.

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---:|---:|---|
| project_id | text | yes | Mã dự án duy nhất, ví dụ `BDS-0001` |
| project_name | text | yes | Tên dự án/deal |
| source_chat | text | no | Nguồn: Teams chat/channel nào |
| source_message_link | text | no | Link message Teams nếu có |
| source_excerpt | text | no | Trích đoạn gốc quan trọng |
| status | enum | yes | new / screening / checking_planning / underwriting / negotiating / rejected / approved / monitoring |
| priority | enum | no | low / medium / high / urgent |
| province_city | text | yes | Tỉnh/TP |
| district | text | no | Quận/huyện/TP trực thuộc |
| ward | text | no | Phường/xã |
| address | text | yes | Địa chỉ mô tả |
| latitude | decimal | no | Vĩ độ |
| longitude | decimal | no | Kinh độ |
| map_url | text | no | Google Maps/Apple Maps link |
| land_area_m2 | number | yes | Diện tích đất m2 |
| gross_floor_area_m2 | number | no | Tổng sàn dự kiến |
| saleable_area_m2 | number | no | Diện tích thương phẩm |
| project_type | enum | yes | apartment / townhouse / villa / mixed_use / land_lot / industrial / commercial / hotel / other |
| land_type | text | no | Loại đất hiện trạng |
| planned_land_use | text | no | Chức năng quy hoạch |
| max_floors | number | no | Tầng cao tối đa |
| far | number | no | Hệ số sử dụng đất / HS SDĐ |
| building_density_pct | number | no | Mật độ xây dựng % |
| population | number | no | Dân số chỉ tiêu |
| planning_source | text | no | Nguồn quy hoạch |
| planning_checked_at | date | no | Ngày kiểm tra quy hoạch |
| legal_status | enum | yes | unknown / clean_title / compensation_pending / planning_pending / 1_500_done / permit_done / under_dispute / other |
| legal_notes | text | no | Ghi chú pháp lý |
| asking_land_price_total | number | no | Giá chào đất tổng, VND |
| asking_land_price_per_m2 | number | no | Giá chào đất/m2 đất |
| expected_product_selling_price_per_m2 | number | no | Giá bán sản phẩm/m2 thương phẩm |
| expected_product_selling_price_note | text | no | Ghi chú giá bán sản phẩm |
| total_land_cost | number | no | Tổng chi phí đất |
| total_development_cost_ex_land | number | no | Tổng chi phí phát triển chưa gồm đất |
| total_project_cost | number | no | Tổng chi phí dự án gồm đất |
| total_revenue | number | no | Tổng doanh thu |
| gross_profit | number | no | Lợi nhuận gộp = doanh thu - tổng chi phí |
| gross_margin_pct | number | no | Biên lợi nhuận gộp % |
| profit_per_land_m2 | number | no | Lợi nhuận/m2 đất |
| residual_land_value_total | number | no | Giá trị đất thặng dư |
| residual_land_value_per_m2 | number | no | Giá trị đất thặng dư/m2 |
| irr_pct | number | no | IRR nếu có timeline dòng tiền |
| payback_months | number | no | Thời gian hoàn vốn |
| key_risks | text | no | Rủi ro chính |
| next_actions | text | no | Việc cần làm tiếp |
| owner | text | no | Người phụ trách |
| created_at | datetime | yes | Ngày tạo record |
| updated_at | datetime | yes | Ngày cập nhật |

## 2. Bảng `cost_items`

Chi tiết chi phí từng dự án.

| Field | Kiểu | Mô tả |
|---|---:|---|
| project_id | text | Link tới `projects.project_id` |
| cost_category | enum | land / compensation / land_use_fee / legal / planning_design / construction / infrastructure / finance / sales_marketing / management / contingency / tax_fee / other |
| cost_item | text | Tên đầu mục |
| basis | enum | total / per_land_m2 / per_gfa_m2 / per_saleable_m2 / pct_revenue / pct_construction / custom |
| quantity | number | Khối lượng |
| unit | text | m2, %, tháng, gói... |
| unit_cost | number | Đơn giá |
| amount | number | Thành tiền |
| cost_per_land_m2 | number | Quy đổi/m2 đất |
| cost_per_saleable_m2 | number | Quy đổi/m2 thương phẩm |
| notes | text | Ghi chú |
| source | text | Nguồn số liệu |

## 3. Bảng `revenue_items`

Chi tiết doanh thu theo dòng sản phẩm.

| Field | Kiểu | Mô tả |
|---|---:|---|
| project_id | text | Link tới `projects.project_id` |
| product_type | enum | apartment / townhouse / villa / shophouse / retail / office / land_lot / parking / other |
| quantity | number | Số căn/lô/m2 |
| area_m2 | number | Diện tích bán/cho thuê |
| selling_price_per_m2 | number | Giá bán/m2 |
| selling_price_per_unit | number | Giá bán/căn/lô nếu dùng |
| revenue | number | Doanh thu |
| absorption_note | text | Ghi chú tốc độ bán |
| notes | text | Ghi chú |
| source | text | Nguồn số liệu |

## 4. Công thức hiệu quả cơ bản

- `asking_land_price_per_m2 = asking_land_price_total / land_area_m2`
- `total_project_cost = total_land_cost + total_development_cost_ex_land`
- `gross_profit = total_revenue - total_project_cost`
- `gross_margin_pct = gross_profit / total_revenue * 100`
- `profit_per_land_m2 = gross_profit / land_area_m2`
- `residual_land_value_total = total_revenue - required_profit - total_development_cost_ex_land`
- `residual_land_value_per_m2 = residual_land_value_total / land_area_m2`

## 5. Map fields tối thiểu

Để cắm bản đồ, mỗi record cần tối thiểu:

- `project_id`
- `project_name`
- `address`
- `latitude`
- `longitude`
- `project_type`
- `status`
- `land_area_m2`
- `asking_land_price_per_m2`
- `gross_margin_pct`
