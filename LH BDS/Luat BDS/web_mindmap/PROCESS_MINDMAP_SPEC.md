# Spec: Web process-mindmap pháp lý phát triển dự án BĐS

## Ý tưởng của Hòa Đại ka

Không chỉ làm mindmap phân loại văn bản luật. Cần build một **web process-mindmap** đi từ tổng thể đến chi tiết:

> Tổng thể là quy trình để phát triển một dự án BĐS cần các bước nào; mỗi bước cần thêm gì, điều kiện gì, hồ sơ gì, cơ quan nào xử lý, có phụ thuộc bước nào; mỗi bước đều phải trích điều luật và ghi tóm tắt đủ ý, đủ detail. Nếu có master timeline thì ghi vào.

## Sản phẩm cần có

### 1. Master process / master timeline

Một timeline tổng thể từ lúc nghiên cứu quỹ đất đến bàn giao/sổ/vận hành.

Khung hiện tại:

| Phase | Bước | Output chính | Phụ thuộc |
|---|---|---|---|
| P0 | Rà soát quỹ đất & quy hoạch | Báo cáo pháp lý đất, quy hoạch, phương án tiếp cận đất, risk register | — |
| P1 | Quy hoạch/chương trình phát triển | Văn bản quy hoạch/chỉ tiêu/quy hoạch chi tiết hoặc xác nhận phù hợp | P0 |
| P2 | Chủ trương đầu tư & lựa chọn NĐT | Chấp thuận chủ trương/chấp thuận NĐT/kết quả đấu giá-đấu thầu | P1 |
| P3 | Đất đai & GPMB | Thu hồi/bồi thường/tái định cư; giao đất/thuê đất/chuyển mục đích | P2 |
| P4 | Nghĩa vụ tài chính | Thông báo và chứng từ hoàn thành tiền sử dụng đất/tiền thuê đất/thuế phí | P3 |
| P5 | Môi trường/PCCC/hạ tầng | ĐTM/GPMT, thẩm duyệt PCCC, thỏa thuận đấu nối | P2-P4, có thể song song một phần |
| P6 | Thiết kế & giấy phép xây dựng | Thẩm định thiết kế, giấy phép xây dựng, điều kiện khởi công | P3-P5 |
| P7 | Thi công & nghiệm thu | Biên bản nghiệm thu, hoàn công, nghiệm thu PCCC/hạ tầng | P6 |
| P8 | Kinh doanh/huy động vốn | Thông báo đủ điều kiện bán, bảo lãnh, hợp đồng, hồ sơ bán hàng | P4-P7 tùy loại sản phẩm |
| P9 | Cấp sổ/bàn giao/vận hành | GCN cho người mua, bàn giao, vận hành, bảo trì, hậu kiểm | P7-P8 |

### 2. Mỗi bước phải có các lớp thông tin

Mỗi node/bước trong web cần có:

1. **Mục tiêu của bước**
2. **Điều kiện trigger** — khi nào phải làm bước này
3. **Hồ sơ cần chuẩn bị**
4. **Cơ quan tiếp nhận/xử lý/phê duyệt**
5. **Thời hạn nếu văn bản có quy định**
6. **Output/pháp lý đầu ra**
7. **Bước phụ thuộc trước/sau**
8. **Điều luật trích dẫn**
   - Tên văn bản
   - Số điều/khoản/điểm
   - Trích đoạn nguồn
   - Tóm tắt đủ ý, không quá ngắn
9. **Rủi ro/checkpoint thực tế**
10. **Ghi chú áp dụng** — dự án nhà ở, khu đô thị, đấu giá/đấu thầu, đất hỗn hợp, lấn biển, nhà ở xã hội, chung cư...

### 3. Giao diện web mong muốn

- Trang chính hiển thị **master timeline/process**.
- Click một phase để drill-down vào các thủ tục con.
- Click thủ tục con để mở panel chi tiết gồm hồ sơ, điều kiện, cơ quan, thời hạn, output, trích điều.
- Có search theo:
  - tên bước
  - điều luật
  - từ khóa hồ sơ
  - cơ quan
  - loại dự án
- Có trạng thái màu:
  - Xanh: bước chính
  - Vàng: bước có thể song song
  - Đỏ: checkpoint rủi ro/phụ thuộc mạnh
- Có link/ngữ cảnh file nguồn để đội pháp lý kiểm tra lại.

## File đã tạo hiện tại

Thư mục:

`C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap`

Các file chính:

- `process_mindmap.html` — bản web process-map hiện tại
- `process_mindmap_data.json` — dữ liệu process-map
- `MASTER_TIMELINE.md` — master timeline markdown
- `build_process_mindmap.py` — script build process-map từ markdown nguồn
- `index.html` — bản mindmap phân loại văn bản ban đầu
- `mindmap_data.json` — dữ liệu mindmap phân loại văn bản

Nguồn văn bản:

`C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx`

Hiện đã đọc/index 61 file markdown.

## Tình trạng hiện tại

Bản hiện tại đã có:

- 10 bước quy trình P0-P9
- Master timeline
- Trích dẫn điều luật tự động theo keyword
- Tóm tắt đoạn điều luật
- Giao diện click bước/click trích dẫn

Nhưng đây mới là bản **auto-extract**. Cần refine để thành bản **legal-grade**.

## Việc cần làm tiếp để đạt chuẩn legal-grade

### Giai đoạn 1 — Làm sạch trích dẫn

- Loại các trích dẫn nhiễu, ví dụ điều mẫu biểu/giấy biên nhận bị match nhầm.
- Ưu tiên luật gốc và nghị định hướng dẫn chính.
- Mỗi bước giữ 5-12 điều thật sự quan trọng.
- Tách rõ điều/khoản/điểm nếu parse được.

### Giai đoạn 2 — Chuẩn hóa checklist từng bước

Với từng phase P0-P9, tạo checklist chuẩn:

```json
{
  "phase": "P2",
  "step": "Chấp thuận chủ trương đầu tư / lựa chọn nhà đầu tư",
  "objective": "...",
  "triggers": ["..."],
  "required_documents": ["..."],
  "authority": ["..."],
  "statutory_timeline": ["..."],
  "outputs": ["..."],
  "dependencies": ["P1"],
  "legal_basis": [
    {
      "document": "...",
      "article": "Điều ...",
      "clause": "Khoản ...",
      "quote": "...",
      "summary": "..."
    }
  ],
  "risks": ["..."]
}
```

### Giai đoạn 3 — Build web bản 2

- UI process timeline rõ hơn.
- Có filter loại dự án:
  - Nhà ở thương mại
  - Khu đô thị
  - Nhà ở xã hội
  - Dự án có đấu giá đất
  - Dự án đấu thầu lựa chọn nhà đầu tư
  - Dự án nhận chuyển nhượng quyền sử dụng đất
  - Dự án có chuyển mục đích sử dụng đất
  - Dự án chung cư
- Có export markdown/JSON cho từng bước.
- Có node “song song” và “điều kiện rẽ nhánh”.

### Giai đoạn 4 — Kết hợp NotebookLM khi auth sẵn sàng

NotebookLM hiện đang báo auth stale. Khi đăng nhập lại được:

1. Import các file markdown hoặc nguồn chính vào NotebookLM.
2. Query từng phase để NotebookLM hỗ trợ lọc điều luật chính.
3. Dùng output NotebookLM để đối chiếu với script auto-extract.
4. Ghi lại vào `process_mindmap_data_refined.json`.

## Ghi chú vận hành

- Không xóa bản auto-extract; giữ làm bản baseline.
- Mọi bản refine nên ghi version:
  - `process_mindmap_v1_auto.html`
  - `process_mindmap_v2_refined.html`
  - `process_mindmap_data_refined.json`
- Khi thêm văn bản mới vào `_converted_md_from_docx`, chạy lại script build rồi refine phần changed.

## Nguyên tắc nội dung

- Không viết chung chung kiểu “theo quy định pháp luật”.
- Mỗi bước phải chỉ ra **cần làm gì, vì sao phải làm, căn cứ điều nào, output là gì**.
- Tóm tắt phải đủ ý để người đọc hiểu nhanh, nhưng luôn giữ trích nguồn để kiểm chứng.
- Nếu điều luật không chắc áp dụng cho mọi loại dự án, ghi rõ điều kiện áp dụng.
- Phân biệt rõ:
  - điều kiện pháp lý bắt buộc
  - hồ sơ thủ tục
  - bước thực tế trong triển khai dự án
  - rủi ro/checkpoint cần luật sư xác nhận
