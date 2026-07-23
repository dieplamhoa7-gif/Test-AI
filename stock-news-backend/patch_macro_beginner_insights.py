from pathlib import Path

p = Path('firebase_public/macro.html')
s = p.read_text(encoding='utf-8')
anchor = '</body>'
script = r'''
<script>
/* Investor-first macro insight layer: uses only the dashboard's own series. */
(function(){
 function last(a){for(let i=a.length-1;i>=0;i--)if(Number.isFinite(a[i]))return {i:i,v:a[i]};return {i:-1,v:null}}
 function val(k){return IND[k]?last(IND[k].series).v:null}
 function month(k){const x=IND[k]?last(IND[k].series):{i:-1};return x.i>=0?M[x.i]:'–'}
 function n(v,d){return Number.isFinite(v)?v.toLocaleString('vi-VN',{maximumFractionDigits:d==null?2:d}):'–'}
 function pct(v){return Number.isFinite(v)?n(v,1)+'%':'–'}
 function delta(k,nm){const x=last(IND[k].series),a=IND[k].series;return x.i>=nm&&Number.isFinite(a[x.i-nm])?x.v-a[x.i-nm]:null}
 const gdp=val('gdp_growth'), iip=val('iip_yoy'), cpi=val('cpi_yoy'), credit=val('credit_yoy'), m2=val('m2_yoy'), usd=val('usdvnd'), dep=val('deposit'), omo=val('omo_net');
 const gap=Number.isFinite(credit)&&Number.isFinite(m2)?credit-m2:null;
 const vni=last(DATA.vni),vni3=vni.i>=3&&Number.isFinite(DATA.vni[vni.i-3])?(vni.v/DATA.vni[vni.i-3]-1)*100:null;
 const growthStrong=(gdp||0)>=6.5&&(iip||0)>=7;
 const pressure=(cpi||0)>4.5&&(gap||0)>8&&((usd||0)>=26000||(dep||0)>=5.5);
 const regime=pressure&&growthStrong?'Cuối mở rộng — ưu tiên phòng thủ':growthStrong?'Mở rộng, nhưng cần theo dõi lạm phát':'Chưa đủ dữ liệu để kết luận chắc chắn';
 const regimeColor=pressure?'#fbbf24':'#34d399';
 const oldEvidence=document.getElementById('cycleEvidence');
 if(oldEvidence)oldEvidence.innerHTML=`
  <div style="padding:13px;border-left:4px solid ${regimeColor};background:rgba(251,191,36,.08);border-radius:8px">
   <div style="font-size:16px"><b style="color:${regimeColor}">Kết luận dễ hiểu: ${regime}</b></div>
   <p style="margin:7px 0;color:var(--mut);line-height:1.65">Nói đơn giản: <b>nền kinh tế vẫn chạy tốt</b> (GDP ${pct(gdp)}, IIP ${pct(iip)}), nhưng <b>chi phí để duy trì đà tăng đang cao hơn</b>: CPI ${pct(cpi)}, tín dụng ${pct(credit)} trong khi M2 ${pct(m2)}${gap!=null?' (lệch '+n(gap,1)+' điểm %)':''}, USD/VND ${n(usd,0)}. Vì vậy chưa phải lúc kết luận suy thoái, nhưng biên an toàn của thị trường đã hẹp hơn.</p>
   <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px;margin-top:10px">
    <div style="padding:10px;background:rgba(52,211,153,.08);border-radius:7px"><b>1. Kinh tế thực</b><br><span style="color:var(--mut)">GDP ${pct(gdp)} · IIP ${pct(iip)}<br>${growthStrong?'Còn mạnh → chưa phải suy thoái.':'Chưa đủ mạnh để xác nhận mở rộng.'}</span></div>
    <div style="padding:10px;background:rgba(251,113,133,.08);border-radius:7px"><b>2. Lạm phát & tiền</b><br><span style="color:var(--mut)">CPI ${pct(cpi)} · Tín dụng–M2 ${gap==null?'–':n(gap,1)+'đ%'}<br>${(cpi||0)>4.5?'Áp lực cao → khó nới lỏng mạnh.':'Áp lực giá đang trong kiểm soát.'}</span></div>
    <div style="padding:10px;background:rgba(251,191,36,.08);border-radius:7px"><b>3. Tỷ giá & vốn</b><br><span style="color:var(--mut)">USD/VND ${n(usd,0)} · Huy động ${pct(dep)}<br>${(usd||0)>=26000?'Tỷ giá cao → thị trường nhạy cảm hơn.':'Áp lực tỷ giá chưa ở mức cao.'}</span></div>
   </div>
  </div>
  <div style="margin-top:12px;padding:11px;border:1px solid var(--line);border-radius:8px;line-height:1.65">
   <b>Nhà đầu tư mới nên hiểu gì?</b><br>
   • Không cần bán tháo chỉ vì chữ “cuối mở rộng”; kinh tế thực chưa suy thoái.<br>
   • Không nên mua đuổi hoặc dùng đòn bẩy cao: lạm phát, tỷ giá và vốn đang làm rủi ro biến động tăng.<br>
   • Ưu tiên doanh nghiệp có lợi nhuận, nợ vay hợp lý, định giá không quá cao; chia nhỏ điểm mua và có ngưỡng cắt lỗ.<br>
   • <b>Tín hiệu tốt hơn:</b> CPI hạ, USD/VND ổn định, chênh tín dụng–M2 thu hẹp, VNIBOR/lãi suất hạ. <b>Tín hiệu xấu hơn:</b> IIP/bán lẻ/xuất khẩu giảm tốc đồng thời hoặc tỷ giá/lãi suất tăng tiếp.
  </div>
  <div style="font-size:10.5px;color:var(--mut2);margin-top:8px">Kỳ dữ liệu khác nhau: GDP ${month('gdp_growth')}, IIP ${month('iip_yoy')}, CPI ${month('cpi_yoy')}, tín dụng ${month('credit_yoy')}, M2 ${month('m2_yoy')}, USD/VND ${month('usdvnd')}. Kết luận có độ tin cậy trung bình vì không phải mọi chỉ tiêu cùng kỳ.</div>`;
 const table=document.getElementById('cyclePhaseTable');
 if(table){
  const phases=(DATA.phases||[]).map(p=>{let a=M.indexOf(p.s);let b=M.indexOf(p.e);if(a<0)a=0;if(b<0)b=M.length-1;const vs=DATA.vni.slice(a,b+1).filter(Number.isFinite);let ret=null,dd=null;if(vs.length>=2){ret=(vs.at(-1)/vs[0]-1)*100;let peak=vs[0];dd=0;vs.forEach(x=>{peak=Math.max(peak,x);dd=Math.min(dd,(x/peak-1)*100)})}return {p,a,b,ret,dd}});
  const phaseRow=x=>{const end=M[Math.min(x.b,M.length-1)],incomplete=x.b===M.length-1&&end<='2026-07';const phaseGDP=(()=>{const z=(IND.gdp_growth_ff?.series||[]).slice(x.a,x.b+1).filter(Number.isFinite);return z.length?z.reduce((a,b)=>a+b,0)/z.length:null})();const phaseCPI=(()=>{const z=(IND.cpi_yoy?.series||[]).slice(x.a,x.b+1).filter(Number.isFinite);return z.length?z.reduce((a,b)=>a+b,0)/z.length:null})();return `<tr><td style="padding:9px;border-bottom:1px solid var(--line)"><b style="color:${x.p.col}">${x.p.name}</b><br><span style="color:var(--mut2)">${x.p.s} → ${incomplete?'kỳ mới nhất '+end:x.p.e}</span></td><td style="padding:9px;border-bottom:1px solid var(--line);text-align:center">${pct(phaseGDP)}</td><td style="padding:9px;border-bottom:1px solid var(--line);text-align:center">${pct(phaseCPI)}</td><td style="padding:9px;border-bottom:1px solid var(--line);text-align:center;color:${(x.ret||0)>=0?'#34d399':'#fb7185'}"><b>${x.ret==null?'–':(x.ret>0?'+':'')+n(x.ret,1)+'%'}</b></td><td style="padding:9px;border-bottom:1px solid var(--line);text-align:center;color:#fb7185">${x.dd==null?'–':n(x.dd,1)+'%'}</td><td style="padding:9px;border-bottom:1px solid var(--line);color:var(--mut)">${x.ret==null?'Thiếu chuỗi VN-Index để so sánh.':x.ret>0?'Thị trường tăng trong pha này, nhưng không chứng minh một mình vĩ mô là nguyên nhân.':'Thị trường giảm; cần xem thêm lãi suất, định giá, dòng tiền và sự kiện riêng.'}</td></tr>`};
  table.innerHTML=`<div style="padding:9px;background:rgba(34,211,238,.06);border-radius:7px;color:var(--mut);line-height:1.5"><b>Đọc bảng đúng cách:</b> đây là lịch sử quan sát, không phải bằng chứng nhân quả. GDP là chuỗi quý được hiển thị theo kỳ gần nhất, CPI là tháng; VN-Index là đóng cửa tháng nên drawdown là <b>drawdown theo tháng</b>, không phải đáy trong ngày.</div><table style="width:100%;border-collapse:collapse;font-size:12px;min-width:800px;margin-top:9px"><thead><tr><th style="text-align:left;padding:9px;border-bottom:1px solid var(--line)">Pha quan sát</th><th style="padding:9px;border-bottom:1px solid var(--line)">GDP*</th><th style="padding:9px;border-bottom:1px solid var(--line)">CPI TB</th><th style="padding:9px;border-bottom:1px solid var(--line)">VN-Index</th><th style="padding:9px;border-bottom:1px solid var(--line)">DD tháng</th><th style="text-align:left;padding:9px;border-bottom:1px solid var(--line)">Cách diễn giải</th></tr></thead><tbody>${phases.map(phaseRow).join('')}</tbody></table><div style="font-size:10.5px;color:var(--mut2);margin-top:8px">* GDP không phải dữ liệu tháng. Pha 2026 là YTD đến kỳ có dữ liệu, không phải cả năm 2026. Các nhãn pha là khung diễn giải lịch sử, cần được đánh giá lại khi có dữ liệu mới.</div>`;
 }
})();
</script>
'''
if anchor not in s:
    raise SystemExit('body closing tag not found')
p.write_text(s.replace(anchor, script + anchor, 1), encoding='utf-8')
print('added investor-first macro insights')
