const fs = require('fs');
const path = require('path');
const target = path.resolve(__dirname, '..', 'public_final_2026_07_11', 'fs.html');
const raw = fs.readFileSync(target, 'utf8');
const start = raw.indexOf('function taoBaoCao(selId){');
const end = raw.indexOf('\n</script>', start);
if (start < 0 || end < 0) throw new Error('Report export function bounds not found');
const replacement = `function taoBaoCao(selId){
  // Open synchronously from the tap; mobile browsers otherwise block it as a popup.
  const w=window.open('','_blank');
  try{
    const sel=document.getElementById(selId||'rep-mode'); const mode=(sel&&sel.value)||'full';
    if(w&&w.document){
      w.document.open();
      w.document.write('<!doctype html><meta charset="utf-8"><title>Đang tạo báo cáo…</title><p style="font-family:Arial;padding:28px">Đang tạo báo cáo, vui lòng chờ…</p>');
      w.document.close();
      const html=buildReportHTML(mode);
      w.document.open(); w.document.write(html); w.document.close();
    }else{
      const html=buildReportHTML(mode);
      const blob=new Blob([html],{type:'text/html'});
      const a=document.createElement('a');
      a.href=URL.createObjectURL(blob); a.download='BaoCao_FS_'+new Date().toISOString().slice(0,10)+'.html';
      document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},800);
      alert('Trình duyệt chặn tab báo cáo nên hệ thống đã tải file HTML về máy.');
    }
  }catch(e){
    if(w&&!w.closed)w.close();
    alert('Lỗi tạo báo cáo: '+e.message);
  }
}
`;
fs.writeFileSync(target, raw.slice(0, start) + replacement + raw.slice(end), 'utf8');
console.log('Patched', target);
