from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\tpre_flowchart_popup.html')
s=p.read_text(encoding='utf-8')
if 'function gapBlock' not in s:
    gap="""function gapBlock(code,id){const g=gapFor(code,id); if(!g.length) return ''; return `<div class=\"fullChecklist\"><h4>Bổ sung sau khi so với corpus luật — các ý không được bỏ sót</h4><div class=\"checkGrid\">${g.map(x=>`<div class=\"checkGroup\"><b>${esc(x.title)}</b>${lines(x.items)}</div>`).join('')}</div></div>`}
function gapFor(code,id){const m={III:[['Route lựa chọn NĐT',['Đấu giá quyền sử dụng đất; đấu thầu lựa chọn nhà đầu tư; chấp thuận nhà đầu tư phải tách route vì hồ sơ/thời gian/rủi ro khác nhau.']]],IV:[['Đồ án quy hoạch / quy định quản lý theo đồ án',['Cần thuyết minh, bản vẽ, chỉ tiêu, quy định quản lý xây dựng; output phải dùng được cho thiết kế, đất, GPXD, định giá, bán hàng, cấp GCN.']]],V:[['Miễn, giảm, khấu trừ tài chính đất',['Ngoài công thức gốc phải kiểm tra miễn, giảm, khấu trừ GPMB, tiền đã ứng, ưu đãi; lưu bảng gross, khoản trừ, net payable và căn cứ từng khoản.']]],VI:[['GPXD / TKBVTC / PCCC / ĐTM',['Giấy phép xây dựng là mốc riêng; TKBVTC phải khớp QHCT/TKCS/PCCC/môi trường/đấu nối; PCCC gồm góp ý, thẩm duyệt, nghiệm thu; ĐTM/GPMT gồm đánh giá tác động, giấy phép, vận hành thử.']]],VIII:[['BĐS HTTTL / HĐMB / công khai thông tin',['Phải ghi đúng BĐS hình thành trong tương lai; HĐMB theo mẫu/nội dung bắt buộc; công khai thông tin trước kinh doanh; bảo lãnh kiểm đến chứng thư/cam kết.']]],X:[['Cấp Giấy chứng nhận / đăng ký đất đai',['Tách cấp GCN dự án và GCN khách hàng; cần đăng ký đất đai/tài sản, bản vẽ, hoàn công, nghiệm thu, nghĩa vụ tài chính, giải chấp, phiếu chuyển thuế.']]]};return (m[id]||[]).map(x=>({title:x[0],items:x[1]}))}
"""
    s=s.replace('function formulaBlock', gap+'function formulaBlock',1)
p.write_text(s,encoding='utf-8')
print('gapblock fixed')
