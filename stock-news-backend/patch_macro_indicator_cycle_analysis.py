from pathlib import Path

p = Path("firebase_public/macro.html")
s = p.read_text(encoding="utf-8")
old = """ const ph=curPhase(M[li]);

 const pos=(lv-mn)/((mx-mn)||1)*100;

 document.getElementById('facAnalysis').innerHTML=`<h4>🔎 Phân tích chỉ tiêu: ${IND[k].label}</h4>

 <p>${INOTE[k]||''}</p>

 <p><b>Số liệu:</b> hiện tại <b>${fmt(lv,u)}</b> (kỳ ${M[li]}); ${tr} — thay đổi 3 tháng ${c3==null?'–':(c3>0?'+':'')+(Math.round(c3*100)/100)}, 12 tháng ${c12==null?'–':(c12>0?'+':'')+(Math.round(c12*100)/100)}. Trong kỳ 2021–nay: thấp nhất ${fmt(mn,u)}, cao nhất ${fmt(mx,u)}, bình quân ${fmt(avg,u)} → đang ở mức <b>${pos>66?'cao':(pos<33?'thấp':'trung bình')}</b> (${Math.round(pos)}% biên độ).</p>

 <p><b>Bối cảnh chu kỳ:</b> nền kinh tế đang ở pha <b style="color:${ph.col}">${ph.name}</b>. ${ph.desc}</p>`;
"""
new = """ const ph=curPhase(M[li]);

 const pos=(lv-mn)/((mx-mn)||1)*100;
 const level=pos>66?'cao':(pos<33?'thấp':'trung bình');

 function cycleRead(k,v,c3,c12,pos){
  const rising=c3!=null&&c3>0,falling=c3!=null&&c3<0,high=pos>66,low=pos<33;
  const reads={
   credit_yoy:()=>v>=16?`Tín dụng ${fmt(v,u)} tăng nhanh và ở vùng ${level}; lực cầu vốn hỗ trợ tăng trưởng nhưng làm pha mở rộng nóng hơn. Khi tín dụng vượt xa M2, rủi ro căng thanh khoản và lãi suất tăng.`:`Tín dụng ở mức ${level}; ${rising?'đang gia tốc, hỗ trợ pha mở rộng':falling?'đang giảm tốc, báo hiệu xung lực tăng trưởng yếu đi':'chưa tạo tín hiệu đổi pha rõ'}.`,
   m2_yoy:()=>`M2 ở vùng ${level} và ${rising?'đang tăng tốc':'đang '+(falling?'giảm tốc':'đi ngang')}. ${v<10?'Thanh khoản tiền tệ tăng chậm; nếu tín dụng tăng nhanh hơn M2, đây là tín hiệu cuối mở rộng và áp lực vốn.':'Thanh khoản đang hỗ trợ hoạt động kinh tế và tài sản rủi ro.'}`,
   dep_tckt_yoy:()=>`Tiền gửi tổ chức ở vùng ${level}; ${falling?'dòng tiền doanh nghiệp suy yếu/rút khỏi hệ thống, bất lợi cho thanh khoản':'đà tăng tiền gửi giúp ổn định nguồn vốn ngân hàng'}.`,
   dep_res_yoy:()=>`Tiền gửi dân cư ở vùng ${level}; ${rising?'tiền quay lại kênh tiết kiệm, có thể cạnh tranh với cổ phiếu':'dòng tiền tiết kiệm không tăng mạnh, áp lực cạnh tranh vốn thấp hơn'}.`,
   vnibor_on:()=>`Lãi suất qua đêm ở vùng ${level} và ${rising?'đang tăng':'đang '+(falling?'hạ':'ổn định')}; ${high||v>4?'thanh khoản liên ngân hàng căng, phù hợp trạng thái cuối mở rộng/phòng thủ':'chưa cho thấy căng thẳng thanh khoản lớn'}.`,
   vnibor_1m:()=>`VNIBOR 1 tháng ở vùng ${level}; ${rising?'chi phí vốn ngắn hạn tăng, tín hiệu thắt chặt hơn':'áp lực vốn kỳ hạn ngắn đang dịu lại'}.`,
   policy:()=>`Lãi suất điều hành ${fmt(v,u)} và ${rising?'đang tăng — chính sách chuyển sang thắt chặt':falling?'đang giảm — chính sách nới lỏng hỗ trợ phục hồi':'đang giữ ổn định; cần đọc cùng CPI, tỷ giá và thanh khoản để xác nhận pha'}.`,
   deposit:()=>`Lãi suất huy động ở vùng ${level} và ${rising?'đang tăng; chi phí vốn và sức hút tiền gửi tăng, bất lợi cho định giá cổ phiếu':'không tăng mạnh; áp lực chi phí vốn chưa xấu thêm'}.`,
   lending:()=>`Lãi suất cho vay ở vùng ${level}; ${rising?'chi phí vốn tăng, có thể làm chậm đầu tư và lợi nhuận':'đang ổn định/giảm, hỗ trợ tăng trưởng'}.`,
   cpi_yoy:()=>`CPI ${fmt(v,u)} ${v>4.5?'vượt ngưỡng tham chiếu 4,5%, xác nhận áp lực quá nhiệt và thu hẹp dư địa nới lỏng':'vẫn trong vùng kiểm soát'}. ${rising?'Đà giá còn tăng nên rủi ro thắt chặt cao hơn.':falling?'Đà giá hạ nhiệt là tín hiệu tích cực cho chu kỳ.':''}`,
   core_yoy:()=>`Lạm phát cơ bản ở vùng ${level}; ${rising?'áp lực giá nền đang lan rộng, tín hiệu cầu nóng':'áp lực giá nền đang dịu/ổn định'}.`,
   cpi_mom:()=>`CPI tháng ${fmt(v,u)}; ${rising?'động lượng giá ngắn hạn tăng, cần đề phòng lan sang CPI YoY':'động lượng giá chưa tăng thêm'}.`,
   gdp_growth:()=>`GDP ${fmt(v,u)} ở vùng ${level}; ${v>=6.5?'tăng trưởng thực còn mạnh nên nền kinh tế vẫn trong pha mở rộng, chưa phải suy thoái':'tăng trưởng đã yếu, cần theo dõi nguy cơ chuyển sang giảm tốc'}.`,
   gdp_growth_ff:()=>`GDP ở vùng ${level}; ${v>=6.5?'nền tăng trưởng còn mạnh, củng cố pha mở rộng':'động lực tăng trưởng không còn mạnh'}.`,
   gdp_growth_q_ff:()=>`GDP quý ở vùng ${level}; ${v>=6.5?'sản lượng tiếp tục mở rộng mạnh':'xung lực sản lượng đang yếu'}.`,
   iip_yoy:()=>`IIP ở vùng ${level} và ${rising?'đang tăng tốc':'đang '+(falling?'giảm tốc':'ổn định')}; ${v>7?'sản xuất còn mở rộng tốt':'động lực công nghiệp cần theo dõi thêm'}.`,
   iip_index_vietstock:()=>`Chỉ số IIP ở vùng ${level}; ${rising?'sản xuất công nghiệp đang cải thiện':'sản xuất chưa gia tốc'}, phản ánh trực tiếp sức khỏe pha tăng trưởng.`,
   retail:()=>`Bán lẻ ở vùng ${level}; ${rising?'cầu nội địa đang mở rộng':'cầu nội địa đang chậm lại'}, qua đó ${rising?'hỗ trợ':'làm yếu'} pha tăng trưởng.`,
   exports:()=>`Xuất khẩu ở vùng ${level}; ${rising?'cầu bên ngoài cải thiện, hỗ trợ sản xuất và tăng trưởng':'đà xuất khẩu suy yếu, là lực cản chu kỳ'}.`,
   fdi_disb:()=>`FDI giải ngân ở vùng ${level}; ${rising?'dòng vốn thực cải thiện, hỗ trợ tăng trưởng và tỷ giá':'dòng vốn chưa tăng, đóng góp cho chu kỳ yếu hơn'}.`,
   fdi_reg:()=>`FDI đăng ký ở vùng ${level}; ${rising?'kỳ vọng đầu tư tương lai cải thiện':'pipeline đầu tư tương lai đang chậm lại'}.`,
   usdvnd:()=>`USD/VND ${fmt(v,u)} ở vùng ${level} và ${rising?'đang tăng':'đang '+(falling?'hạ':'ổn định')}; ${high||rising?'áp lực mất giá hạn chế dư địa nới lỏng và làm trạng thái cuối mở rộng rủi ro hơn':'áp lực tỷ giá đang dịu'}.`,
   fx_central:()=>`Tỷ giá trung tâm ở vùng ${level}; ${rising?'NHNN đang cho phép mặt bằng tỷ giá tăng, phản ánh áp lực ngoại hối':'áp lực điều hành tỷ giá chưa tăng thêm'}.`,
   pubinv_12m:()=>`Đầu tư công ở vùng ${level}; ${rising?'tài khóa tiếp tục nâng đỡ tăng trưởng':'xung lực tài khóa đang giảm'}, là biến đối trọng với rủi ro thắt chặt tiền tệ.`,
   omo_net:()=>`OMO ${v>0?'bơm ròng':'hút ròng'} ${fmt(Math.abs(v),u)}; ${v>0?'NHNN đang đỡ thanh khoản ngắn hạn, nhưng đây chưa tự động là một chu kỳ nới lỏng mới':'thanh khoản bị rút bớt, tín hiệu phòng thủ/thắt chặt hơn'}.`,
   omo_inject:()=>`Quy mô bơm OMO ở vùng ${level}; ${rising?'NHNN tăng hỗ trợ thanh khoản ngắn hạn':'mức hỗ trợ không tăng thêm'}.`,
   omo_withdraw:()=>`Quy mô hút/đáo hạn OMO ở vùng ${level}; ${rising?'áp lực rút thanh khoản tăng':'áp lực rút thanh khoản đang giảm'}.`,
   mp_reverse_repo_net:()=>`Reverse repo ròng ${v>0?'dương, đang bơm thanh khoản':'âm, đang hút thanh khoản'}; đây là tín hiệu điều tiết ngắn hạn cần đọc cùng lãi suất liên ngân hàng.`,
   mp_total_net:()=>`Tổng thanh khoản NHNN ${v>0?'đang bơm ròng, giúp giảm căng thẳng ngắn hạn':'đang hút ròng, làm điều kiện tiền tệ chặt hơn'}.`,
   mp_tbill_net:()=>`Tín phiếu ròng ${v<0?'cho thấy hút thanh khoản':'không cho thấy hút ròng'}; tác động trực tiếp đến điều kiện tiền tệ ngắn hạn.`,
   mp_policy_refi:()=>`Lãi suất tái cấp vốn ${fmt(v,u)}; ${rising?'tăng là tín hiệu thắt chặt':'ổn định/giảm chưa xác nhận áp lực thắt chặt mới'}.`,
   mp_interbank_on:()=>`Lãi suất liên ngân hàng qua đêm ở vùng ${level}; ${rising?'đang tăng, cho thấy thanh khoản căng hơn':'đang ổn định/hạ, giúp giảm rủi ro thanh khoản'}.`
  };
  return (reads[k]?reads[k]():`${IND[k].label} đang ở vùng ${level}, ${tr}; chỉ tiêu này ${rising?'đóng góp theo hướng gia tốc':'chưa cho thấy gia tốc'} cho chu kỳ.`)+` Kết hợp toàn bộ dashboard, pha chung hiện tại là <b style="color:${ph.col}">${ph.name}</b>.`;
 }
 const cycleText=cycleRead(k,lv,c3,c12,pos);

 document.getElementById('facAnalysis').innerHTML=`<h4>🔎 Phân tích chỉ tiêu: ${IND[k].label}</h4>

 <p>${INOTE[k]||''}</p>

 <p><b>Số liệu:</b> hiện tại <b>${fmt(lv,u)}</b> (kỳ ${M[li]}); ${tr} — thay đổi 3 tháng ${c3==null?'–':(c3>0?'+':'')+(Math.round(c3*100)/100)}, 12 tháng ${c12==null?'–':(c12>0?'+':'')+(Math.round(c12*100)/100)}. Trong kỳ 2021–nay: thấp nhất ${fmt(mn,u)}, cao nhất ${fmt(mx,u)}, bình quân ${fmt(avg,u)} → đang ở mức <b>${level}</b> (${Math.round(pos)}% biên độ).</p>

 <p><b>Bối cảnh chu kỳ theo chỉ tiêu đang chọn:</b> ${cycleText}</p>`;
"""
if old not in s:
    raise SystemExit("Target analyzeInd block not found; no change made")
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("patched macro per-indicator cycle analysis")
