from pathlib import Path
p=Path('firebase_public/pattern-reco.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Rê chuột vào từng mẫu hình ở bảng bên phải: đường/marker liên quan sẽ sáng lên, các tín hiệu khác tự mờ đi để dễ đọc chart.','Rê chuột vào từng mẫu hình ở bảng bên phải: đường/marker liên quan sẽ sáng lên. Với mẫu 2/3 đỉnh–đáy, chart gắn nhãn trực tiếp “Đỉnh 1/2/3” hoặc “Đáy 1/2/3” ngay tại nến.')
p.write_text(s,encoding='utf-8')
