# Kế hoạch deep research pháp lý dự án BĐS

## Mục tiêu

Xây dựng một web tri thức pháp lý về quy trình phát triển dự án BĐS tại Việt Nam, theo hướng:

1. Nghiên cứu đầy đủ nguồn luật liên quan.
2. Tách đúng tầng: luật nền → nghị định hướng dẫn → thông tư/biểu mẫu → văn bản sửa đổi/bổ sung → văn bản chuyên ngành.
3. Tổ chức thành quy trình dự án thật: tiền khả thi, quy hoạch, đầu tư/lựa chọn nhà đầu tư, đất đai/tài chính đất, xây dựng/kỹ thuật, kinh doanh, bàn giao/cấp sổ/vận hành.
4. Mỗi node có điều kiện áp dụng, hồ sơ, cơ quan, thời hạn, output, rủi ro, căn cứ điều/khoản/điểm, trích dẫn và tóm tắt.

## Nguyên tắc làm việc

- Không build UI trước khi có knowledge base đủ sâu.
- Không chỉ keyword match; cần legal curation theo từng nhóm thủ tục.
- Không bịa điều luật. Mỗi căn cứ phải có nguồn, số văn bản, điều/khoản/điểm.
- Ghi rõ văn bản còn hiệu lực, văn bản sửa đổi/bổ sung/thay thế nếu xác định được.
- Ưu tiên nguồn: file luật local, Thư Viện Pháp Luật, Cổng VBQPPL, website bộ/ngành.

## Phase 1 — Inventory nguồn luật

Tạo danh mục văn bản theo nhóm:

### A. Luật nền

- Luật Đất đai 2024
- Luật Nhà ở 2023
- Luật Kinh doanh bất động sản 2023
- Luật Đầu tư 2020 và sửa đổi/bổ sung
- Luật Đấu thầu 2023 và sửa đổi/bổ sung
- Luật Xây dựng 2014 và sửa đổi/bổ sung
- Luật Quy hoạch đô thị và nông thôn 2024
- Luật Quy hoạch 2017
- Luật Bảo vệ môi trường 2020
- Luật Phòng cháy chữa cháy và sửa đổi/bổ sung
- Luật Giá 2023
- Luật Thuế, phí, lệ phí liên quan đất/BĐS

### B. Nghị định hướng dẫn

- Nghị định hướng dẫn Luật Đất đai 2024: giao đất, cho thuê đất, chuyển mục đích, đăng ký đất đai, bồi thường/GPMB, giá đất, tiền sử dụng đất/tiền thuê đất.
- Nghị định hướng dẫn Luật Nhà ở 2023.
- Nghị định hướng dẫn Luật Kinh doanh BĐS 2023.
- Nghị định hướng dẫn Luật Đấu thầu về lựa chọn nhà đầu tư.
- Nghị định hướng dẫn Luật Đầu tư.
- Nghị định về quản lý dự án đầu tư xây dựng, giấy phép xây dựng, quản lý chất lượng, nghiệm thu.
- Nghị định về môi trường, PCCC.

### C. Thông tư / biểu mẫu

- Thông tư Bộ TNMT về hồ sơ đất đai, đăng ký đất đai, GCN.
- Thông tư Bộ Xây dựng về nhà ở, kinh doanh BĐS, quản lý vận hành chung cư, hợp đồng mẫu nếu có.
- Thông tư Bộ Tài chính về nghĩa vụ tài chính đất đai, giá đất, phí/lệ phí.
- Thông tư NHNN về bảo lãnh bán/cho thuê mua nhà ở hình thành trong tương lai.

### D. Văn bản cập nhật/sửa đổi/bổ sung

- Nghị quyết Quốc hội/Chính phủ có tác động đến đất đai, đấu thầu, đầu tư, nhà ở.
- Nghị định/Thông tư năm 2025-2026 sửa các nghị định/thông tư 2024.
- Văn bản chuyển tiếp.

## Phase 2 — Xây legal ontology

Tạo các nhóm node:

1. Master timeline dự án
2. Quy hoạch/chương trình phát triển
3. Đầu tư/chủ trương đầu tư
4. Lựa chọn nhà đầu tư
5. Đấu giá QSDĐ
6. Đấu thầu dự án có sử dụng đất
7. Thỏa thuận nhận QSDĐ/đang có QSDĐ
8. Thu hồi đất/bồi thường/GPMB
9. Giao đất/thuê đất/chuyển mục đích
10. Nghĩa vụ tài chính đất đai
11. Môi trường/PCCC/hạ tầng
12. Thiết kế/thẩm định/GPXD
13. Thi công/nghiệm thu/hoàn công
14. BĐS hình thành trong tương lai/bán hàng/huy động vốn
15. Bàn giao/cấp GCN/vận hành

## Phase 3 — Trích điều khoản

Mỗi node cần:

```json
{
  "id": "...",
  "title": "...",
  "type": "gate|decision|procedure|document|risk",
  "summary": "...",
  "applies_when": [],
  "conditions": [],
  "required_documents": [],
  "authority": [],
  "statutory_timeline": [],
  "outputs": [],
  "risks": [],
  "children": [],
  "legal_basis": [
    {
      "document": "...",
      "article": "Điều ...",
      "clause": "Khoản ...",
      "point": "Điểm ...",
      "quote": "...",
      "summary": "...",
      "source_url": "...",
      "source_file": "...",
      "status": "effective|amended|unknown"
    }
  ]
}
```

## Phase 4 — Web

Sau khi knowledge base đủ, web mới render:

- Màn đầu: master flow/gates
- Bấm gate: hiện thủ tục con
- Bấm decision: hiện các route
- Bấm route/procedure: hiện detail, điều/khoản/điểm, hồ sơ, cơ quan, thời hạn, output, rủi ro
- Bên phải: flowchart cấp hiện tại
- Có search theo điều luật/từ khóa/văn bản
- Có filter theo loại dự án: nhà ở thương mại, khu đô thị, nhà ở xã hội, chung cư, dự án có đất công, đấu giá, đấu thầu, thỏa thuận QSDĐ.

## Output từng bước

- `source_inventory.json` — danh mục văn bản.
- `source_inventory.md` — danh mục đọc được.
- `legal_basis_extracted.json` — điều khoản đã trích.
- `bds_legal_ontology_curated.json` — ontology đã curate.
- `web/` — frontend cuối.
