const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const PUBLIC = path.join(ROOT, 'public');
const files = fs.readdirSync(PUBLIC).filter(f => /\.(html|js|css)$/i.test(f)).map(f => path.join(PUBLIC, f));

const replacements = [
  ['á»‹','ị'],['á»‰','ỉ'],['á»‡','ệ'],['á»ƒ','ể'],['á»�','ề'],['áº¿','ế'],['áº¹','ẹ'],['áº»','ẻ'],['áº½','ẽ'],
  ['á»™','ộ'],['á»“','ồ'],['á»‘','ố'],['á»•','ổ'],['á»—','ỗ'],['á»£','ợ'],['á»�','ờ'],['á»›','ớ'],['á»Ÿ','ở'],['á»¡','ỡ'],
  ['á»¥','ụ'],['á»§','ủ'],['á»©','ứ'],['á»«','ừ'],['á»­','ử'],['á»¯','ữ'],['á»±','ự'],
  ['á»³','ỳ'],['á»·','ỷ'],['á»¹','ỹ'],
  ['áº¡','ạ'],['áº£','ả'],['áº£','ả'],['áº£','ả'],['áº¥','ấ'],['áº§','ầ'],['áº©','ẩ'],['áº«','ẫ'],['áº­','ậ'],
  ['áº¯','ắ'],['áº±','ằ'],['áº³','ẳ'],['áºµ','ẵ'],['áº·','ặ'],['áº¡','ạ'],['áº£','ả'],['áº¥','ấ'],['áº§','ầ'],
  ['Ã¡','á'],['Ã ','à'],['Ã¢','â'],['Ã£','ã'],['Ã¤','ä'],['Ã©','é'],['Ã¨','è'],['Ãª','ê'],['Ã­','í'],['Ã¬','ì'],
  ['Ã³','ó'],['Ã²','ò'],['Ã´','ô'],['Ãµ','õ'],['Ãº','ú'],['Ã¹','ù'],['Ã½','ý'],['Ã€','À'],['Ã�','Á'],['Ã‚','Â'],
  ['Ä‘','đ'],['Ä�','Đ'],['Æ°','ư'],['Æ¡','ơ'],['Æ¯','Ư'],['Æ ','Ơ'],
  ['Â²','²'],['Â°','°'],['Â·','·'],['Â ',' '],['â€“','–'],['â€”','—'],['â€¦','…'],['â€œ','“'],['â€','”'],['â€˜','‘'],['â€™','’'],
  ['â‚«','₫'],['â‰¥','≥'],['â‰¤','≤'],['â†’','→'],
  ['vá»±c','vực'],['cÅ©','cũ'],['má»›i','mới'],['thá»a','thửa'],['Lá»—i','Lỗi'],['bá»™','bộ'],['dá»±','dự'],['rá»™ng','rộng'],
  ['CÆ¡','Cơ'],['hÆ¡n','hơn'],['Tá»·','Tỷ'],['tá»·','tỷ'],['phá»‘','phố'],['Bá»™','Bộ'],
  ['Phưá»�ng','Phường'],['phưá»�ng','phường'],['PhÆ°á»�ng','Phường'],['phÆ°á»�ng','phường'],
  ['ThA�nh ph��`','Thành phố'],['ThA�nh ph��','Thành phố'],['bA�n','bán'],
  ['B�o','Báo'],['b�o','báo'],['T?o','Tạo'],['t?o','tạo'],['D? li?u','Dữ liệu'],['d? li?u','dữ liệu'],['Quy ho?ch','Quy hoạch'],['quy ho?ch','quy hoạch'],
  ['Nghia v?','Nghĩa vụ'],['t�i ch�nh','tài chính'],['Ph�p ly','Pháp lý'],['D?u tu','Đầu tư'],['d? �n','dự án'],['D? �n','Dự án'],
  ['H? so','Hồ sơ'],['h? so','hồ sơ'],['R?i ro','Rủi ro'],['r?i ro','rủi ro'],['Chua','Chưa'],['chua','chưa'],['Dang','Đang'],['dang','đang'],
  ['Ki?m','Kiểm'],['ki?m','kiểm'],['ngu?n','nguồn'],['Ngu?n','Nguồn'],['gi�','giá'],['Gi�','Giá'],['m?u','mẫu'],['M?u','Mẫu'],
  ['d? xu?t','đề xuất'],['D? xu?t','Đề xuất'],['trung b�nh','trung bình'],['Trung b�nh','Trung bình'],['so s�nh','so sánh'],['So s�nh','So sánh'],
  ['v? tr�','vị trí'],['V? tr�','Vị trí'],['t?a d?','tọa độ'],['T?a d?','Tọa độ'],['d?c di?m','đặc điểm'],['D?c di?m','Đặc điểm'],
  ['ho�n t?t','hoàn tất'],['Ho�n t?t','Hoàn tất'],['x? ly','xử lý'],['X? ly','Xử lý'],['l?i','lỗi'],['L?i','Lỗi'],
  ['c?n','cần'],['C?n','Cần'],['th�m','thêm'],['Th�m','Thêm'],['d?','để'],['D?','Để'],['du?ng','đường'],['Du?ng','Đường'],
  ['phu?ng','phường'],['Phu?ng','Phường'],['do?n','đoạn'],['Do?n','Đoạn'],['don gi�','đơn giá'],['Don gi�','Đơn giá'],
  ['di?n t�ch','diện tích'],['Di?n t�ch','Diện tích'],['hi?n tr?ng','hiện trạng'],['Hi?n tr?ng','Hiện trạng'],['m?','mở'],['M?','Mở'],
  ['n?t','nút'],['N?t','Nút'],['l?ch s?','lịch sử'],['L?ch s?','Lịch sử'],['luu','lưu'],['Luu','Lưu'],
  ['chu?n','chuẩn'],['Chu?n','Chuẩn'],['s�u','sâu'],['S�u','Sâu'],['r�','rõ'],['R�','Rõ'],['ch�','chú'],['Ch�','Chú']
];

function fix(s){
  let out = s;
  for(const [a,b] of replacements) out = out.split(a).join(b);
  return out;
}
function scan(s){
  const re = /.{0,24}(?:\uFFFD|Ã|Â|Ä|Æ|á»|áº|â€|â€“|â€”|â€¦|A�|\?i|\?u|\?n|\?ng|\?c|\?p|\?t).{0,24}/g;
  return [...s.matchAll(re)].map(m=>m[0]).filter(x=>!/https?:|\?auto=|\?w=|\?:|\?\)|\?\.|\?\]|\?\{|\?\//.test(x));
}

let totalChanged=0;
for(const f of files){
  const before = fs.readFileSync(f,'utf8');
  const after = fix(before);
  if(after !== before){ fs.writeFileSync(f, after, 'utf8'); totalChanged++; }
}
console.log('changed files', totalChanged);
for(const f of files){
  const s = fs.readFileSync(f,'utf8');
  const hits = scan(s);
  if(hits.length){
    console.log('\nBAD', path.basename(f), hits.length);
    for(const h of hits.slice(0,40)) console.log(' ', h.replace(/\n/g,' '));
  }
}
