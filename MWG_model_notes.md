# MWG valuation model notes (bản đầu)

## 1) Mục tiêu
Dựng model Excel định giá cơ bản cho MWG theo 2 trục:
- DCF hợp nhất
- SOTP theo segment: TGDD / ĐMX / BHX / khác

Kèm một sheet riêng để phân tích tác động IPO ĐMX tới định giá MWG.

## 2) Logic định giá đề xuất

### DCF hợp nhất
Phù hợp khi muốn nhìn MWG như một consolidated retail platform.
Biến số quan trọng:
- tăng trưởng doanh thu
- EBIT margin hồi phục
- capex
- NWC
- WACC
- terminal growth

### SOTP
Rất quan trọng với MWG vì profile từng mảng khác nhau:
- TGDD: mảng mature, tăng trưởng thấp hơn, multiple thấp hơn
- ĐMX: mảng điện máy lớn, có thể tách định giá rõ hơn nếu IPO
- BHX: optionality cao nhất, biên lợi nhuận thấp nhưng upside nếu scale thành công
- mảng khác: giá trị thấp hơn / tùy chọn

## 3) IPO ĐMX tác động đến MWG như thế nào?

### Tác động tích cực tiềm năng
1. **Crystallize value**
   - Khi ĐMX IPO, thị trường sẽ gán định giá trực tiếp cho ĐMX.
   - Trước IPO, giá trị ĐMX thường bị “chìm” trong định giá hợp nhất MWG.
   - Vì vậy IPO có thể mở khóa valuation gap nếu market gán multiple cao hơn mức nhà đầu tư đang ngầm áp cho MWG.

2. **Cash proceeds**
   - Nếu IPO có phần primary hoặc secondary sale, MWG/ĐMX nhận tiền mặt.
   - Tiền này có thể dùng để:
     - giảm nợ
     - tài trợ BHX
     - đầu tư logistics / công nghệ
   - DCF sẽ hưởng lợi qua net debt thấp hơn hoặc tăng tốc đầu tư growth.

3. **Minh bạch segment**
   - Sau IPO, báo cáo và kỳ vọng cho ĐMX minh bạch hơn.
   - Dễ dùng SOTP hơn thay vì áp 1 corporate multiple cho tất cả.

4. **Định vị lại MWG**
   - MWG có thể được thị trường nhìn như holding / platform bán lẻ đa mảng, thay vì chỉ là retailer điện thoại.

### Rủi ro / điểm cần chú ý
1. **Nếu định giá IPO thấp**
   - ĐMX có thể tạo “anchor” valuation thấp hơn kỳ vọng.
   - Điều này làm SOTP của MWG không tăng nhiều như kỳ vọng.

2. **Dilution / control discount**
   - Nếu bán tỷ lệ quá lớn hoặc cấu trúc nắm giữ phức tạp, thị trường có thể áp discount.

3. **One-off vs sustainable value**
   - Nếu tiền IPO chỉ là one-off mà không cải thiện ROIC dài hạn, tác động định giá bền vững sẽ hạn chế.

## 4) BHX vận hành kinh doanh như thế nào?
BHX là chuỗi grocery / minimart hiện đại, logic vận hành khác hẳn TGDD/ĐMX.

### Key drivers
- doanh thu/cửa hàng
- số lượng cửa hàng
- mix hàng tươi sống vs FMCG
- shrinkage / hao hụt
- logistics lạnh / khô
- productivity lao động
- chi phí thuê mặt bằng
- private label / sức mua với nhà cung cấp

### Vì sao BHX quan trọng trong valuation MWG?
- Đây là mảng có optionality lớn nhất.
- Nếu BHX đạt EBIT margin dương và tăng trưởng doanh thu/cửa hàng tốt, multiple EV/Sales có thể cao hơn mảng retail truyền thống.
- Nếu BHX tiếp tục tiêu hao vốn và biên yếu, BHX sẽ kéo định giá MWG xuống.

## 5) Triển vọng kinh tế Việt Nam liên quan đến MWG

### Thuận lợi
- tăng thu nhập bình quân
- urbanization
- modern trade penetration còn dư địa
- nhu cầu nâng cấp điện thoại / điện máy theo chu kỳ
- hạ tầng thanh toán và delivery phát triển

### Rủi ro
- cầu tiêu dùng yếu nếu thu nhập thực không cải thiện
- lãi suất / tín dụng tiêu dùng co hẹp
- áp lực tỷ giá lên hàng điện tử nhập khẩu
- cạnh tranh giá trong grocery retail

## 6) Thị phần BHX / doanh thu bán lẻ thực phẩm
Về định lượng chính xác, cần cập nhật từ:
- báo cáo MWG
- dữ liệu thị trường modern trade
- báo cáo ngành bán lẻ / FMCG

Nhận định chiến lược:
- thị trường grocery Việt Nam vẫn rất phân mảnh
- kênh truyền thống vẫn chiếm tỷ trọng lớn
- modern grocery còn dư địa tăng
- BHX cạnh tranh với WinMart, Co.op, chuỗi minimart khác và chợ truyền thống

Do đó trong valuation:
- base case: BHX được định giá EV/Sales vừa phải
- bull case: nếu chứng minh được unit economics tốt và tăng trưởng bền
- bear case: nếu market coi BHX là mảng margin thấp, capital intensive

## 7) File Excel đã tạo
- `MWG_valuation_model_basic.xlsx`

## 8) Trạng thái hiện tại
- File Excel là **khung model chạy được**.
- Dữ liệu lịch sử trong sheet `Historical_FS` và assumptions hiện là **placeholder hợp lý** để anh và em có structure làm việc ngay.
- Bước tiếp theo cần làm để ra model dùng được:
  1. cập nhật BCTC chính thức MWG (doanh thu, EBIT, NPAT, nợ, tiền mặt, shares)
  2. cập nhật số liệu BHX, store count, doanh thu/cửa hàng
  3. cập nhật giá MWG hiện tại và multiples so sánh
  4. xây thêm case IPO ĐMX theo nhiều mức valuation

## 9) Khuyến nghị bước tiếp theo
Em nên làm tiếp cho anh:
- bản v2 với dữ liệu BCTC thực kéo từ nguồn công khai
- thêm so sánh multiples với FRT / DGW / WinCommerce tương tự khả dụng
- thêm dashboard summary và output target price
