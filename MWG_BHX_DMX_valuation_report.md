# Báo cáo định giá nhanh MWG / BHX / ĐMX

_Thời điểm lập: 31/05/2026_

## 1. Phạm vi và lưu ý

Báo cáo này dùng các thông tin public đã kéo được trong phiên làm việc để định giá sơ bộ theo phương pháp SOTP.

**Quan trọng:** Đây chưa phải định giá kiểm toán/fairness opinion. Một số input là dữ liệu công khai từ CafeF/MWG, một số là giả định định giá do Tiểu đệ đặt để chạy kịch bản. Các giả định được ghi rõ riêng.

---

## 2. Dữ liệu nguồn đã xác nhận

### 2.1 MWG hợp nhất - KQKD 2025 từ CafeF

Nguồn: CafeF - Kết quả hoạt động kinh doanh MWG 2025  
Link: https://cafef.vn/du-lieu/bao-cao-tai-chinh/mwg/incsta/2025/0/0/0/0/ket-qua-hoat-dong-kinh-doanh.chn

| Chỉ tiêu | Giá trị 2025 |
|---|---:|
| Doanh thu thuần | 155.928 tỷ đồng |
| Lợi nhuận gộp | 31.002 tỷ đồng |
| Lợi nhuận trước thuế | 8.633 tỷ đồng |
| Lợi nhuận sau thuế | 7.073 tỷ đồng |
| LNST công ty mẹ | 7.034 tỷ đồng |

### 2.2 BHX - dữ liệu public đã tìm được

Nguồn chính: các bài CafeF về BHX/MWG cập nhật 2026.

| Chỉ tiêu | Giá trị |
|---|---:|
| Doanh thu Q1/2026 BHX | khoảng 13.100 tỷ đồng |
| Lợi nhuận Q1/2026 BHX | gần 400 tỷ đồng |
| Biên LNST Q1/2026 ước tính | khoảng 3,05% |
| Kế hoạch doanh thu 2026 BHX | khoảng 55.500 tỷ đồng |
| Kế hoạch lợi nhuận 2026 BHX | khoảng 1.800 tỷ đồng |
| Biên LNST kế hoạch 2026 | khoảng 3,24% |
| Cửa hàng cuối tháng 4/2026 | khoảng 2.963 cửa hàng |
| Doanh thu 4T2026 | gần 18.000 tỷ đồng, tăng khoảng 20% YoY |

Nguồn tham khảo:
- https://cafef.vn/mo-4-cua-hang-moi-ngay-bach-hoa-xanh-lai-lon-188260427225827223.chn
- https://cafef.vn/lanh-dao-mwg-noi-gi-ve-muc-tieu-ipo-bach-hoa-xanh-188260513152149545.chn
- https://cafef.vn/bach-hoa-xanh-chinh-thuc-co-mat-tai-ha-noi-8-cua-hang-dau-tien-dat-o-dau-188260526100013257.chn

### 2.3 ĐMX - dữ liệu public đã tìm được

Nguồn chính: MWG/CafeF về IPO ĐMX.

| Chỉ tiêu | Giá trị |
|---|---:|
| LNST Q1/2026 ĐMX | khoảng 2.219 tỷ đồng |
| Tăng trưởng doanh thu Q1/2026 | khoảng +30% YoY |
| Tăng trưởng LNST Q1/2026 | khoảng +49% YoY |
| Hệ thống cuối T4/2026 | 2.005 cửa hàng ĐMX, 927 TGDD, 85 Topzone, 222 EraBlue |
| Dịch vụ thợ 2025 - doanh thu | 2.576 tỷ đồng |
| Dịch vụ thợ 2025 - LNST | 201 tỷ đồng |

Nguồn tham khảo:
- https://www.mwg.vn/tin-tuc/dien-may-xanh-dmx-ipo-chao-ban-hon-179-5-trieu-co-phieu-gia-du-kien-80000-dong-5002407
- https://cafef.vn/ong-doan-van-hieu-em-ban-xong-2-trieu-co-phieu-mwg-san-sang-tham-ra-ipo-dmx-188260522102043705.chn
- https://cafef.vn/tham-vong-cua-dien-may-xanh-quy-chuan-hoa-nganh-tho-sua-va-muc-tieu-doanh-thu-hon-8000-ty-dong-188260528085347871.chn

---

## 3. Giả định định giá

### 3.1 Giả định chung MWG

| Input | Giá trị | Loại dữ liệu |
|---|---:|---|
| Giá MWG giả định | 70.000 đồng/cp | Giả định/model placeholder |
| Số cổ phiếu | 1.463 triệu cp | Giả định/model placeholder, cần cập nhật nếu muốn exact |
| Market cap MWG | 102.410 tỷ đồng | Tính toán từ giá và số cổ phiếu |
| Net debt | 7.000 tỷ đồng | Giả định/model placeholder, cần thay bằng BCTC mới nhất |
| EV MWG | 109.410 tỷ đồng | Market cap + net debt |

### 3.2 Giả định định giá BHX

BHX được định giá bằng trung bình của 2 phương pháp:

1. **EV/Sales** trên doanh thu kế hoạch 2026 là 55.500 tỷ đồng.
2. **P/E** trên lợi nhuận kế hoạch 2026 là 1.800 tỷ đồng.

| Kịch bản | EV/Sales | P/E | Ghi chú |
|---|---:|---:|---|
| Bear | 0,50x | 18x | Discount vì execution risk/mở rộng nhanh |
| Base | 0,65x | 22x | Case BHX duy trì biên khoảng 3% và tăng trưởng tốt |
| Bull | 0,80x | 26x | Case market trả premium cho grocery platform/IPO option |

### 3.3 Giả định định giá ĐMX

Do chưa có đủ standalone financial statements full-year sạch, ĐMX được định giá theo range public/IPO narrative:

| Kịch bản | Giá trị ĐMX |
|---|---:|
| Bear | 32.000 tỷ đồng |
| Base | 45.000 tỷ đồng |
| Bull | 60.000 tỷ đồng |

---

## 4. Kết quả định giá SOTP

### 4.1 Bear case

| Cấu phần | Giá trị | % EV MWG |
|---|---:|---:|
| BHX | 30.075 tỷ đồng | 27,5% |
| ĐMX | 32.000 tỷ đồng | 29,2% |
| TGDD + phần còn lại implied | 47.335 tỷ đồng | 43,3% |
| **MWG EV** | **109.410 tỷ đồng** | **100,0%** |

### 4.2 Base case

| Cấu phần | Giá trị | % EV MWG |
|---|---:|---:|
| BHX | 37.838 tỷ đồng | 34,6% |
| ĐMX | 45.000 tỷ đồng | 41,1% |
| TGDD + phần còn lại implied | 26.573 tỷ đồng | 24,3% |
| **MWG EV** | **109.410 tỷ đồng** | **100,0%** |

### 4.3 Bull case

| Cấu phần | Giá trị | % EV MWG |
|---|---:|---:|
| BHX | 45.600 tỷ đồng | 41,7% |
| ĐMX | 60.000 tỷ đồng | 54,8% |
| TGDD + phần còn lại implied | 3.810 tỷ đồng | 3,5% |
| **MWG EV** | **109.410 tỷ đồng** | **100,0%** |

---

## 5. Diễn giải kết quả

### 5.1 BHX

BHX hiện có cơ sở để được định giá như một mảng tăng trưởng vì:

- doanh thu Q1/2026 khoảng 13.100 tỷ đồng;
- lợi nhuận Q1/2026 gần 400 tỷ đồng;
- biên ròng khoảng 3%;
- kế hoạch 2026 khoảng 55.500 tỷ doanh thu và 1.800 tỷ lợi nhuận;
- hệ thống tiếp tục mở rộng mạnh.

Tuy nhiên, BHX vẫn cần discount vì:

- đang mở rộng nhanh;
- rủi ro cửa hàng mới làm giảm hiệu suất bình quân;
- biên 3% chưa cao so với MWG hợp nhất;
- chất lượng lợi nhuận cần theo dõi thêm qua nhiều quý.

**Kết luận BHX:** giá trị hợp lý sơ bộ nằm khoảng **30.000 - 45.600 tỷ đồng**, base khoảng **37.800 tỷ đồng**.

### 5.2 ĐMX

ĐMX là mảng lợi nhuận rõ nhất trong câu chuyện MWG hiện tại:

- LNST Q1/2026 khoảng 2.219 tỷ đồng;
- tăng trưởng LNST Q1/2026 khoảng 49% YoY;
- IPO ĐMX là catalyst giúp market nhìn riêng giá trị mảng điện máy/ICT;
- mảng dịch vụ thợ tạo thêm optionality, với năm 2025 đạt 2.576 tỷ doanh thu và 201 tỷ LNST.

**Kết luận ĐMX:** trong base case, định giá khoảng **45.000 tỷ đồng**; range hợp lý sơ bộ **32.000 - 60.000 tỷ đồng**.

### 5.3 MWG

Ở mức giá giả định 70.000 đồng/cp:

- market cap khoảng 102.410 tỷ;
- EV khoảng 109.410 tỷ;
- base SOTP phân bổ: ĐMX khoảng 41%, BHX khoảng 35%, phần còn lại khoảng 24%.

Điểm đáng chú ý: nếu dùng bull case cho cả BHX và ĐMX, phần implied cho TGDD + other gần như rất thấp. Điều này cho thấy bull case đang khá căng nếu market cap/EV MWG không tăng tương ứng. Vì vậy base case hợp lý hơn để tham chiếu.

---

## 6. Kết luận đầu tư sơ bộ

### Luận điểm tích cực

1. **ĐMX là profit engine rõ ràng**, có catalyst IPO.
2. **BHX đã chuyển sang giai đoạn có lãi**, biên ròng khoảng 3%, kế hoạch 2026 cho thấy quy mô lợi nhuận đáng kể.
3. MWG có thể được market nhìn lại theo SOTP thay vì chỉ là retailer hợp nhất.

### Rủi ro

1. Dữ liệu standalone của ĐMX/BHX chưa đầy đủ như BCTC công ty độc lập.
2. Net debt và số cổ phiếu cần cập nhật lại từ BCTC/latest source.
3. BHX mở rộng quá nhanh có thể kéo giảm hiệu suất cửa hàng và biên lợi nhuận.
4. Định giá ĐMX phụ thuộc vào IPO narrative và mức market sẵn sàng trả.

### Kết luận nhanh

- **BHX base valuation:** khoảng **37.800 tỷ đồng**.
- **ĐMX base valuation:** khoảng **45.000 tỷ đồng**.
- **MWG EV tại giá 70.000:** khoảng **109.400 tỷ đồng**.
- Trong base case, MWG đang được nhìn như:
  - ĐMX: **~41% EV**
  - BHX: **~35% EV**
  - TGDD + khác: **~24% EV**

---

## 7. Việc cần làm tiếp để nâng độ chính xác

1. Cập nhật giá MWG realtime và số cổ phiếu mới nhất.
2. Lấy CĐKT/LCTT 2025 từ CafeF để cập nhật net debt chính xác.
3. Tìm thêm tài liệu IPO/IR để lấy standalone doanh thu/LNST full-year của ĐMX.
4. Tìm disclosure riêng của BHX để xác nhận lợi nhuận 2025 và biên 2025.
5. Đưa báo cáo này vào Excel model thành sheet `MWG_SOTP_Public`, `BHX_Valuation`, `DMX_Valuation`.
