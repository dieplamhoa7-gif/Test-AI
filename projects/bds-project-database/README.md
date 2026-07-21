# BĐS Project Database

Mục tiêu: database chuẩn để gom thông tin dự án BĐS từ Microsoft Teams/chat, gắn tọa độ lên bản đồ, và tính hiệu quả dự án.

## Files

- `schema.md` — thiết kế bảng/field chi tiết.
- `projects_template.csv` — file nhập nhanh danh mục dự án.
- `cost_items_template.csv` — file nhập chi tiết chi phí theo từng đầu mục.
- `revenue_items_template.csv` — file nhập chi tiết doanh thu theo dòng sản phẩm.
- `project_status_options.csv` — danh mục trạng thái/loại dự án/pháp lý.

## Cách dùng đề xuất

1. Import/copy thông tin từ Microsoft Teams vào `projects_template.csv`.
2. Với mỗi dự án, điền `project_id` duy nhất, ví dụ `BDS-0001`.
3. Điền chi phí vào `cost_items_template.csv` theo cùng `project_id`.
4. Điền doanh thu vào `revenue_items_template.csv` theo cùng `project_id`.
5. Map dùng `latitude`, `longitude`, `address`, `map_url`.
6. Dashboard tính hiệu quả từ tổng doanh thu - tổng chi phí.
