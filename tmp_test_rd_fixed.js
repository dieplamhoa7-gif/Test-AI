const API_BASE='https://architects-non-skirts-learners.trycloudflare.com';
(async()=>{
const c={lat:10.788423362693855,lon:106.69143208535428};
const pr=await fetch(API_BASE+'/planning/lookup',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c)});const pj=await pr.json();
const loc=pj.location||{}, pp=pj.planning?.planning_project||{};
const prompt=`Bạn là analyst R&D bất động sản cho LH Real Estate. Dựa trên dữ liệu lookup thật bên dưới, hãy lập báo cáo ngắn nhưng thực dụng bằng tiếng Việt.\n\nDỮ LIỆU LOOKUP KHÔNG ĐƯỢC ĐOÁN LẠI:\nTọa độ: 10.788423362693855, 106.69143208535428\nĐịa chỉ/geocode: ${loc.display_name||''}\nĐường: ${loc.road||''}\nPhường/xã: ${loc.ward||loc.suburb||''}\nQuận/khu vực quy hoạch: ${pp.TenQH||loc.district||loc.city||''}\nĐồ án quy hoạch: ${pp.TenDoAn||''}\nSố QĐ: ${pp.SoQD||''}\nNgày duyệt: ${pp.NgayDuyet||''}\nTrạng thái: ${pp.TrangThai||''}\n\nTIÊU CHÍ R&D:\nGiao dịch: Mua\nLoại tài sản: Đất/Nhà phố\nMĐSDĐ: ODT\nĐặc tính: Mặt tiền\n\nYêu cầu cấu trúc:\n1) Nhận định vị trí/khu vực theo đúng dữ liệu lookup, không tự đổi sang khu vực khác\n2) Comparable/khu vực nên tìm nguồn rao bán\n3) Yếu tố pháp lý/quy hoạch cần kiểm\n4) Khoảng giá tham khảo nếu có căn cứ, nếu không có thì nói rõ cần dữ liệu\n5) Checklist hành động tiếp theo.\nKhông bịa số chính thức; phân biệt rõ giả định và dữ liệu cần xác minh.`;
const r=await fetch(API_BASE+'/v1/chat/completions',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({model:'APIBDS',messages:[{role:'user',content:prompt}],max_tokens:1000})});
const j=await r.json(); console.log(j.choices?.[0]?.message?.content||JSON.stringify(j));
})().catch(e=>{console.error(e);process.exit(1)});
