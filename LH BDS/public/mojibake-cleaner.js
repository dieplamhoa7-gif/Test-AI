// LH Real Estate Vietnamese mojibake cleaner.
// Presentation-only: cleans visible DOM text/labels without touching app logic.
(function(){
  const pairs = [
    ['hÆ¡n','hơn'],['CÆ¡','Cơ'],['cÅ©','cũ'],['má»›i','mới'],['vá»±c','vực'],['bá»™','bộ'],['Tá»·','Tỷ'],['tá»·','tỷ'],['thá»a','thửa'],['Lá»—i','Lỗi'],['dá»±ng','dựng'],['dá»±','dự'],['dá»¯','dữ'],['rá»™ng','rộng'],['phá»‘','phố'],['Bá»™','Bộ'],
    ['Ä‘','đ'],['Ä\uFFFD','Đ'],['Æ°','ư'],['Æ¡','ơ'],['Æ¯','Ư'],['Æ ','Ơ'],
    ['á»‹','ị'],['á»‰','ỉ'],['á»‡','ệ'],['á»ƒ','ể'],['á»\uFFFD','ề'],['áº¿','ế'],['áº¹','ẹ'],['áº»','ẻ'],['áº½','ẽ'],['á»™','ộ'],['á»“','ồ'],['á»‘','ố'],['á»•','ổ'],['á»—','ỗ'],['á»£','ợ'],['á»\uFFFD','ờ'],['á»›','ớ'],['á»Ÿ','ở'],['á»¡','ỡ'],['á»¥','ụ'],['á»§','ủ'],['á»©','ứ'],['á»«','ừ'],['á»­','ử'],['á»¯','ữ'],['á»±','ự'],['á»³','ỳ'],['á»·','ỷ'],['á»¹','ỹ'],
    ['áº¡','ạ'],['áº£','ả'],['áº¥','ấ'],['áº§','ầ'],['áº©','ẩ'],['áº«','ẫ'],['áº­','ậ'],['áº¯','ắ'],['áº±','ằ'],['áº³','ẳ'],['áºµ','ẵ'],['áº·','ặ'],
    ['Ã¡','á'],['Ã ','à'],['Ã¢','â'],['Ã£','ã'],['Ã©','é'],['Ã¨','è'],['Ãª','ê'],['Ã­','í'],['Ã¬','ì'],['Ã³','ó'],['Ã²','ò'],['Ã´','ô'],['Ãµ','õ'],['Ãº','ú'],['Ã¹','ù'],['Ã½','ý'],
    ['Â²','²'],['Â°','°'],['Â·','·'],['Â ',' '],['â€“','–'],['â€”','—'],['â€¦','…'],['â€œ','“'],['â€','”'],['â€˜','‘'],['â€™','’'],['â‚«','₫'],['â‰¥','≥'],['â‰¤','≤'],['â†’','→'],
    ['Phưá»\uFFFDng','Phường'],['phưá»\uFFFDng','phường'],['PhÆ°á»\uFFFDng','Phường'],['phÆ°á»\uFFFDng','phường'],['ThA\uFFFDnh ph\uFFFD\uFFFD`','Thành phố'],['ThA\uFFFDnh ph\uFFFD\uFFFD','Thành phố'],['bA\uFFFDn','bán'],['\uFFFDức','Đức'],['\uFFFDỨc','Đức'],['Tháng \uFFFDứcTám','Tháng Tám'],['Tháng \uFFFDức Tám','Tháng Tám'],
    // Common broken text emitted by older frontend/API result blocks.
    ['B\uFFFDo c\uFFFDo','Báo cáo'],['b\uFFFDo c\uFFFDo','báo cáo'],['D? li?u','Dữ liệu'],['d? li?u','dữ liệu'],['T?o','Tạo'],['t?o','tạo'],
    ['T?ng quan','Tổng quan'],['H? so','Hồ sơ'],['h? so','hồ sơ'],['d? \uFFFDn','dự án'],['D? \uFFFDn','Dự án'],['T\uFFFDn d? \uFFFDn','Tên dự án'],
    ['Quy ho?ch','Quy hoạch'],['quy ho?ch','quy hoạch'],['C?ng quy ho?ch','Cổng quy hoạch'],['ngu?n ch\uFFFDnh','nguồn chính'],['Ngu?n ch\uFFFDnh','Nguồn chính'],
    ['M? ki?m ch?ng','Mở kiểm chứng'],['ki?m ch?ng','kiểm chứng'],['Ki?m ch?ng','Kiểm chứng'],['M? ngu?n','Mở nguồn'],['ngu?n','nguồn'],['Ngu?n','Nguồn'],
    ['Khu v?c','Khu vực'],['khu v?c','khu vực'],['v?c','vực'],['D?a ch?','Địa chỉ'],['d?a ch?','địa chỉ'],['v? tr\uFFFD','vị trí'],['V? tr\uFFFD','Vị trí'],
    ['Ch?c nang','Chức năng'],['ch?c nang','chức năng'],['M\uFFFD quy u?c','Mã quy ước'],['T?ng cao','Tầng cao'],['Tr?ng th\uFFFDi','Trạng thái'],
    ['Da d?c du?c','Đã đọc được'],['Chua d?c du?c','Chưa đọc được'],['chua d?c du?c','chưa đọc được'],['kh\uFFFDng c\uFFFD d? li?u','không có dữ liệu'],
    ['Khu v?c cu','Khu vực cũ'],['Khu v?c m?i','Khu vực mới'],['M\uFFFD t?','Mô tả'],['T?/th?a','Tờ/thửa'],['Di?n t\uFFFDch th?a','Diện tích thửa'],
    ['Hi?n tr?ng','Hiện trạng'],['hi?n tr?ng','hiện trạng'],['lo?i d?t','loại đất'],['Lo?i d?t','Loại đất'],['Quy ho?ch x\uFFFDy d?ng','Quy hoạch xây dựng'],
    ['D? r?ng du?ng','Độ rộng đường'],['Hu?ng m?t ti?n','Hướng mặt tiền'],['Du?ng','Đường'],['du?ng','đường'],['d?t','đất'],['D?t','Đất'],
    ['th?a','thửa'],['m?t ti?n','mặt tiền'],['di?n t\uFFFDch','diện tích'],['Di?n t\uFFFDch','Diện tích'],['th\uFFFDng tin','thông tin'],['Th\uFFFDng tin','Thông tin'],
    ['ph\uFFFDp ly','pháp lý'],['Ph\uFFFDp ly','Pháp lý'],['l?i','lỗi'],['L?i','Lỗi'],['Kh\uFFFDng tra du?c','Không tra được'],['Dang','Đang'],['dang','đang'],['x? ly','xử lý'],['X? ly','Xử lý'],
    ['c?n','cần'],['C?n','Cần'],['d?i chi?u','đối chiếu'],['D?i chi?u','Đối chiếu'],['c?nh b\uFFFDo','cảnh báo'],['C?nh b\uFFFDo','Cảnh báo'],['phuong','phương'],['d?a phuong','địa phương']
  ];
  function clean(s){
    if(typeof s !== 'string' || !s) return s;
    let out = s;
    for(const [a,b] of pairs) out = out.split(a).join(b);
    // Post-fix collisions caused by older '?' mojibake patterns.
    out = out.split('Cầng quy hoạch').join('Cổng quy hoạch')
      .split('cầng quy hoạch').join('cổng quy hoạch')
      .split('Khu vực cu').join('Khu vực cũ')
      .split('khu vực cu').join('khu vực cũ')
      .split('nguồn chành').join('nguồn chính')
      .split('Nguồn chành').join('Nguồn chính')
      .split('dự án quy hoạch dạng b??').join('dự án quy hoạch đồng bộ')
      .split('Thuộc dự án quy hoạch dạng b??').join('Thuộc dự án quy hoạch đồng bộ')
      .split('Tháng ĐứcTám').join('Tháng Tám')
      .split('Tháng Đức Tám').join('Tháng Tám')
      .split('Tháng ủ ĐứcTám').join('Tháng Tám')
      .split('Tháng ủ Đức Tám').join('Tháng Tám')
      .split('Phường Hòa Hưng Thành phố Hồ Chí Minh Thành phố Thủ Đức').join('Phường Hòa Hưng, Thành phố Hồ Chí Minh')
      .split('Phường Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức').join('Phường Hòa Hưng, Thành phố Hồ Chí Minh')
      .split('Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức').join('Hòa Hưng, Thành phố Hồ Chí Minh')
      .split('Thành phố Hồ Chí Minh Thành phố Thủ Đức').join('Thành phố Hồ Chí Minh')
      .split('Thành phố Hồ Chí Minh, Thành phố Thủ Đức').join('Thành phố Hồ Chí Minh')
      .split('Phường Hòa Hưng, Thành phố Hồ Chí Minh, Phường Hòa Hưng, Thành phố Hồ Chí Minh').join('Phường Hòa Hưng, Thành phố Hồ Chí Minh');
    return out;
  }
  function cleanNodeText(node){
    if(node.nodeType === Node.TEXT_NODE){
      const v = clean(node.nodeValue);
      if(v !== node.nodeValue) node.nodeValue = v;
      return;
    }
    if(node.nodeType === Node.ELEMENT_NODE){
      for(const attr of ['placeholder','title','aria-label','value']){
        if(node.hasAttribute && node.hasAttribute(attr)){
          const v = node.getAttribute(attr), c = clean(v);
          if(c !== v) node.setAttribute(attr, c);
        }
      }
    }
  }
  function cleanAll(root=document.body){
    if(!root) return;
    cleanNodeText(root);
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let n; while((n=w.nextNode())) cleanNodeText(n);
  }
  window.LH_cleanText = clean;
  window.LH_cleanDom = cleanAll;
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => cleanAll()); else cleanAll();
  const mo = new MutationObserver(ms => { for(const m of ms){ for(const n of m.addedNodes) cleanAll(n); if(m.target) cleanNodeText(m.target); } });
  try{ mo.observe(document.documentElement, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:['placeholder','title','aria-label','value']}); }catch(_){ }
})();
