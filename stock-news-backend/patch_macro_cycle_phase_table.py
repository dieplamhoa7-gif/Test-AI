from pathlib import Path

p = Path("firebase_public/macro.html")
s = p.read_text(encoding="utf-8")

old_html = '\n <div class="layout">'
new_html = '''
 <div class="card" id="cycleEvidenceCard" style="margin-top:14px">
  <h3>Vì sao hiện tại là cuối chu kỳ mở rộng?</h3>
  <div class="cap">Đánh giá đa biến từ chính dữ liệu trên dashboard; không dựa vào một chỉ tiêu đơn lẻ.</div>
  <div id="cycleEvidence" style="margin-top:10px"></div>
 </div>
 <div class="card" id="cyclePhaseTableCard" style="margin-top:14px">
  <h3>Bảng phân tích các giai đoạn chu kỳ vĩ mô và VN-Index</h3>
  <div class="cap">Thống kê theo khoảng thời gian đã tô nền trên chart. Lợi suất và drawdown VN-Index được tính trực tiếp từ chuỗi tháng của dashboard.</div>
  <div id="cyclePhaseTable" style="overflow-x:auto;margin-top:10px"></div>
 </div>
 <div class="layout">'''
if old_html not in s:
    raise SystemExit("Macro layout anchor not found")
s = s.replace(old_html, new_html, 1)

anchor = "renderPhaseTL();\n\n\n\nselFac('credit_yoy');"
js = r'''function phaseMetricAvg(key,i0,i1){
 const a=IND[key]&&IND[key].series;if(!a)return null;const z=a.slice(i0,i1+1).filter(Number.isFinite);return z.length?z.reduce((x,y)=>x+y,0)/z.length:null;
}
function phaseVniStats(i0,i1){
 const z=DATA.vni.slice(i0,i1+1).map((v,j)=>({v,i:i0+j})).filter(x=>Number.isFinite(x.v));
 if(z.length<2)return {ret:null,dd:null,start:null,end:null};
 const start=z[0].v,end=z[z.length-1].v;let peak=start,dd=0;
 z.forEach(x=>{peak=Math.max(peak,x.v);dd=Math.min(dd,(x.v/peak-1)*100)});
 return {ret:(end/start-1)*100,dd,start,end};
}
function pct(v,d=1){return v==null?'–':(v>0?'+':'')+v.toFixed(d)+'%'}
function phaseImpact(st,p){
 if(st.ret==null)return 'Thiếu dữ liệu VN-Index trong giai đoạn.';
 if(st.ret>15&&st.dd>-15)return 'Thuận lợi: tăng trưởng/thanh khoản hỗ trợ định giá; VN-Index tăng với drawdown được kiểm soát.';
 if(st.ret>0&&st.dd<=-15)return 'Tăng nhưng biến động lớn: cơ hội còn, song rủi ro điều chỉnh đã cao và cần hạ đòn bẩy.';
 if(st.ret<=-15)return 'Bất lợi/risk-off: lợi nhuận kỳ vọng giảm, định giá co lại và VN-Index chịu drawdown mạnh.';
 return 'Trung tính đến thận trọng: chỉ số thiếu xu hướng rõ, ưu tiên chọn lọc doanh nghiệp và quản trị rủi ro.';
}
function renderCycleEvidence(){
 const lv=k=>IND[k]?lastVal(IND[k].series)[1]:null;
 const gdp=lv('gdp_growth'),iip=lv('iip_yoy'),cpi=lv('cpi_yoy'),cr=lv('credit_yoy'),m2=lv('m2_yoy'),usd=lv('usdvnd'),dep=lv('deposit'),omo=lv('omo_net');
 const gap=Number.isFinite(cr)&&Number.isFinite(m2)?cr-m2:null;
 const rows=[
  ['Tăng trưởng thực',`GDP ${fmt(gdp,'%')}; IIP ${fmt(iip,'%')}`,gdp>=6.5&&iip>=7?'Mở rộng mạnh':'Giảm tốc',gdp>=6.5&&iip>=7?'Kinh tế thực còn tăng mạnh → chưa phải suy thoái.':'Động lực sản lượng suy yếu.'],
  ['Lạm phát',`CPI ${fmt(cpi,'%')}`,cpi>4.5?'Quá nóng':'Kiểm soát',cpi>4.5?'Vượt 4,5% → thu hẹp dư địa nới lỏng, gây áp lực lên định giá.':'Chưa tạo sức ép thắt chặt lớn.'],
  ['Tín dụng – cung tiền',`Tín dụng ${fmt(cr,'%')} / M2 ${fmt(m2,'%')}`,gap>8?'Khe hở rộng '+gap.toFixed(1)+'đ%':'Cân bằng hơn',gap>8?'Tín dụng chạy nhanh hơn nguồn tiền → dấu hiệu điển hình cuối mở rộng, dễ căng thanh khoản.':'Nguồn tiền theo kịp tín dụng hơn.'],
  ['Tỷ giá',`USD/VND ${fmt(usd,'VND')}`,usd>=26000?'Áp lực cao':'Ổn định',usd>=26000?'Tỷ giá cao hạn chế khả năng giảm lãi suất và tăng rủi ro dòng vốn ngoại.':'Áp lực ngoại hối thấp hơn.'],
  ['Lãi suất huy động',`${fmt(dep,'%')}`,dep>=5.5?'Chi phí vốn tăng':'Hỗ trợ',dep>=5.5?'Tiền gửi cạnh tranh hơn với cổ phiếu; chi phí vốn doanh nghiệp/ngân hàng khó giảm sâu.':'Mặt bằng vốn còn hỗ trợ tài sản rủi ro.'],
  ['Thanh khoản NHNN',`OMO ròng ${fmt(omo,'tỷ')}`,omo>0?'Bơm hỗ trợ ngắn hạn':'Hút/không hỗ trợ',omo>0?'Giảm căng thẳng tức thời, nhưng không đảo ngược tín hiệu lạm phát–tỷ giá để xác nhận nới lỏng mới.':'Điều kiện tiền tệ chặt hơn.']
 ];
 const yes=rows.filter(r=>['Quá nóng','Áp lực cao'].includes(r[2])||r[2].startsWith('Khe hở')||r[2].startsWith('Chi phí')).length;
 document.getElementById('cycleEvidence').innerHTML=`<div style="padding:11px 12px;border-left:4px solid #fbbf24;background:rgba(251,191,36,.08);border-radius:8px;margin-bottom:10px"><b style="color:#fbbf24">Kết luận: Cuối mở rộng / Quá nhiệt — phòng thủ</b><div style="margin-top:5px;color:var(--mut);line-height:1.6">Tăng trưởng vẫn mạnh nhưng ${yes} nhóm cảnh báo đồng thời xuất hiện: lạm phát vượt ngưỡng, khe hở tín dụng–M2 rộng, tỷ giá cao và chi phí vốn tăng. Đây là sự kết hợp “sản lượng còn tốt nhưng điều kiện tài chính xấu dần” — đặc trưng của cuối pha mở rộng. Chưa gọi là suy thoái vì GDP và IIP chưa co lại.</div></div><div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12px;min-width:760px"><thead><tr><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Trụ cột</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Dữ liệu chart</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Tín hiệu</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Ý nghĩa chu kỳ</th></tr></thead><tbody>${rows.map(r=>`<tr><td style="padding:8px;border-bottom:1px solid var(--line)"><b>${r[0]}</b></td><td style="padding:8px;border-bottom:1px solid var(--line)">${r[1]}</td><td style="padding:8px;border-bottom:1px solid var(--line);color:${['Mở rộng mạnh','Bơm hỗ trợ ngắn hạn','Kiểm soát','Hỗ trợ'].includes(r[2])?'#34d399':'#fb7185'}"><b>${r[2]}</b></td><td style="padding:8px;border-bottom:1px solid var(--line);color:var(--mut)">${r[3]}</td></tr>`).join('')}</tbody></table></div>`;
}
function renderCyclePhaseTable(){
 const rows=(DATA.phases||[]).map(p=>{let i0=M.indexOf(p.s),i1=M.indexOf(p.e);if(i0<0)i0=0;if(i1<0)i1=M.length-1;const st=phaseVniStats(i0,i1);const g=phaseMetricAvg('gdp_growth_ff',i0,i1),c=phaseMetricAvg('cpi_yoy',i0,i1),cr=phaseMetricAvg('credit_yoy',i0,i1),m2=phaseMetricAvg('m2_yoy',i0,i1);return {p,st,g,c,cr,m2}});
 document.getElementById('cyclePhaseTable').innerHTML=`<table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:980px"><thead><tr><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Giai đoạn</th><th style="padding:8px;border-bottom:1px solid var(--line)">GDP TB</th><th style="padding:8px;border-bottom:1px solid var(--line)">CPI TB</th><th style="padding:8px;border-bottom:1px solid var(--line)">Tín dụng TB</th><th style="padding:8px;border-bottom:1px solid var(--line)">M2 TB</th><th style="padding:8px;border-bottom:1px solid var(--line)">VN-Index</th><th style="padding:8px;border-bottom:1px solid var(--line)">Max drawdown</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--line)">Tác động/diễn giải</th></tr></thead><tbody>${rows.map(x=>`<tr><td style="padding:8px;border-bottom:1px solid var(--line);min-width:180px"><b style="color:${x.p.col}">${x.p.name}</b><div style="color:var(--mut2)">${x.p.s} → ${x.p.e}</div></td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line)">${fmt(x.g,'%')}</td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line)">${fmt(x.c,'%')}</td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line)">${fmt(x.cr,'%')}</td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line)">${fmt(x.m2,'%')}</td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line);color:${x.st.ret>=0?'#34d399':'#fb7185'}"><b>${pct(x.st.ret)}</b><div style="color:var(--mut2)">${x.st.start==null?'–':Math.round(x.st.start).toLocaleString('vi')} → ${x.st.end==null?'–':Math.round(x.st.end).toLocaleString('vi')}</div></td><td style="text-align:center;padding:8px;border-bottom:1px solid var(--line);color:#fb7185">${pct(x.st.dd)}</td><td style="padding:8px;border-bottom:1px solid var(--line);color:var(--mut);min-width:280px">${phaseImpact(x.st,x.p)}</td></tr>`).join('')}</tbody></table><div style="font-size:10.5px;color:var(--mut2);margin-top:8px">Lưu ý: đây là thống kê mô tả trên dữ liệu tháng của dashboard, không khẳng định quan hệ nhân quả và không phải dự báo lợi suất.</div>`;
}

renderPhaseTL();
renderCycleEvidence();
renderCyclePhaseTable();



selFac('credit_yoy');'''
if anchor not in s:
    raise SystemExit("renderPhaseTL anchor not found")
s = s.replace(anchor, js, 1)
p.write_text(s, encoding="utf-8")
print("added macro cycle evidence and phase/VN-Index table")
