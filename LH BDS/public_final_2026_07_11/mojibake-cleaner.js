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
    ['c?n','cần'],['C?n','Cần'],['d?i chi?u','đối chiếu'],['D?i chi?u','Đối chiếu'],['c?nh b\uFFFDo','cảnh báo'],['C?nh b\uFFFDo','Cảnh báo'],['phuong','phương'],['d?a phuong','địa phương']    ['Tra c��cu','Tra cứu'],['tra c��cu','tra cứu'],['Tra c?u','Tra cứu'],
    ['quy ho���ch','quy hoạch'],['Quy ho���ch','Quy hoạch'],['quy ho?ch','quy hoạch'],
    ['t��?a �`��T','tọa độ'],['T��?a �`��T','Tọa độ'],['t?a d?','tọa độ'],
    ['L��-i','Lỗi'],['l��-i','lỗi'],
    ['Ch��a','Chưa'],['ch��a','chưa'],
    ['d��_ li���u','dữ liệu'],['D��_ li���u','Dữ liệu'],['d? li?u','dữ liệu'],
    ['�?ang','Đang'],['dang','đang'],
    ['Tra c��cu','Tra cứu'],
    ['K���t qu���','Kết quả'],['k���t qu���','kết quả'],
    ['v��< trA-','vị trí'],['V��< trA','Vị trí'],
    ['�`��" A�n','Dự án'],['d? �n','dự án'],
    ['ch��cc n��ng','chức năng'],['Ch��cc n��ng','Chức năng'],
    ['Di���n tA-ch','Diện tích'],['di?n t?ch','diện tích'],
    ['T?ng cao','Tầng cao'],
    ['M�?XD','MĐXD'],['M?XD','MĐXD'],
    ['HSSD�?','HSSDD'],
    ['Quy ho���ch xA�y d���ng','Quy hoạch xây dựng'],
    ['Ngu��"n','Nguồn'],['ngu��"n','nguồn'],
    ['M��Y','Mở'],['m��y','mở'],
    ['ki���m ch��cng','kiểm chứng'],
    ['Ph����?ng','Phường'],['ph����?ng','phường'],
    ['Qu��-n','Quận'],['qu��n','quận'],
    ['Th��< tr����?ng','Thị trường'],
    ['Ngh�ca v��� tA�i chA-nh','Nghĩa vụ tài chính'],
    ['FS hi���u qu���','FS hiệu quả'],
    ['PhA�p lA�','Pháp lý'],
    ['H��" s��','Hồ sơ'],
    ['C��ng','Công'],['c��ng','công'],
    ['th�ng tin','thông tin'],
    ['b?n d?','bản đồ'],
    ['B?n d?','Bản đồ']
    // End extra quyhoach pairs

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


// Extra: force clean on result boxes after any update
setInterval(() => {
  try {
    const boxes = document.querySelectorAll('#locationBox,#planningBox,#indicatorBox,#sourceBox,#riskBox');
    boxes.forEach(b => { if (b) window.LH_cleanDom(b); });
  } catch(_) {}
}, 1500);


// Force clean the quyhoach result areas right after data arrives
(function(){
  const origLookup = window.lookup;
  if (typeof window.lookup === 'function') {
    window.lookup = function() {
      origLookup.apply(this, arguments);
      setTimeout(() => {
        try { if (window.LH_cleanDom) LH_cleanDom(); } catch(e){}
        const boxes = ['locationBox','planningBox','indicatorBox','sourceBox','riskBox'];
        boxes.forEach(id => {
          const el = document.getElementById(id);
          if (el) LH_cleanDom(el);
        });
      }, 300);
    };
  }
  // Also run periodically
  setInterval(() => {
    try {
      const boxes = document.querySelectorAll('#locationBox,#planningBox,#indicatorBox,#sourceBox,#riskBox,.source-result,.qh-result-card');
      boxes.forEach(b => LH_cleanDom(b));
    } catch(e){}
  }, 1200);
})();

// Extra aggressive clean for the land use heading and indicator section
setTimeout(function() {
  try {
    var boxes = document.querySelectorAll('h2, #indicatorBox, .qh-result-card');
    boxes.forEach(function(box) {
      if (box && box.innerHTML) {
        var html = box.innerHTML;
        html = html.replace(/Chá»‰ tiÃªu Ã´ Ä‘áº¥t \/ chá»©c nÄƒng Ä‘áº¥t/g, 'Chỉ tiêu ô đất / chức năng đất');
        html = html.replace(/Chỉ tiÃªu Ã´ Ä‘áº¥t \/ chá»©c nÄƒng Ä‘áº¥t/g, 'Chỉ tiêu ô đất / chức năng đất');
        if (html !== box.innerHTML) box.innerHTML = html;
      }
    });
    // Also run the main clean
    if (window.LH_cleanDom) LH_cleanDom();
  } catch(e) {}
}, 800);

// === Ultra QH specific aggressive fix for user-reported mojibake (title, headings, status) ===
(function(){
  function qhFix(){
    try{
      // Title
      if (document.title && /Quy ho/i.test(document.title)) {
        document.title = document.title.replace(/Quy ho[^ ]*ch/i, 'Quy hoạch');
      }
      // All h2 + specific cards
      document.querySelectorAll('h2, #indicatorBox, .qh-result-card, label, #locationBox, #planningBox, #sourceBox, #riskBox').forEach(function(el){
        if (!el) return;
        var t = el.innerText || el.textContent || '';
        if (!t) return;
        var before = t;
        // Broad heading fix
        t = t.replace(/Ch[ỉiI�? ]*ti[�? ]*u\s*ô?\s*đ[âa]?t\s*\/\s*ch[�? ]*c\s*n[�? ]*ng\s*đ[âa]?t/gi, 'Chỉ tiêu ô đất / chức năng đất');
        t = t.replace(/Ch[?ỉ ]*tiêu\s*ô\s*đất\s*\/\s*chức năng đất/gi , 'Chỉ tiêu ô đất / chức năng đất');
        // Common dynamic
        t = t.replace(/B[�?a]n n[�?a]y hi[�?e]n th[�?i] k[�?e]t qu[�?a] nh[�?u] bot Quyhoach/gi, 'Bản này hiển thị kết quả như bot Quyhoach');
        t = t.replace(/K[�?e]t qu[�?a] v[�?i] tr[�?i]/gi, 'Kết quả vị trí');
        t = t.replace(/D[�?u] [�?a]n Quy ho[�?a]ch/gi, 'Dự án Quy hoạch');
        t = t.replace(/3 ngu[�?o]n d[�?o]i chi[�?e]u/gi, '3 nguồn đối chiếu');
        t = t.replace(/C[�?a]nh b[�?a]o ki[�?e]m tra/gi, 'Cảnh báo kiểm tra');
        if (t !== before) {
          if (el.innerText != null) el.innerText = t;
          else if (el.textContent != null) el.textContent = t;
        }
      });
      // Run main cleaner too
      if (window.LH_cleanDom) window.LH_cleanDom(document.body);
    }catch(e){}
  }
  // Run early and often
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', qhFix);
  } else {
    qhFix();
  }
  setTimeout(qhFix, 150);
  setTimeout(qhFix, 500);
  setTimeout(qhFix, 1200);
  setInterval(qhFix, 1800);
  // Also patch lookup if present
  var origL = window.lookup;
  if (typeof origL === 'function') {
    window.lookup = function(){ origL.apply(this, arguments); setTimeout(qhFix, 250); setTimeout(qhFix, 800); };
  }
})();


// R&D page labels/status/progress mojibake hardener.
(function(){
  const rdPairs = [
    ['K?t qu? nghi�n c?u','Kết quả nghiên cứu'],['Quy tr�nh ph�n t�ch','Quy trình phân tích'],
    ['X�c d?nh v? tr� v� ph?m vi so s�nh','Xác định vị trí và phạm vi so sánh'],['T�m ngu?n d? li?u th? tru?ng','Tìm nguồn dữ liệu thị trường'],['D?c m?u tin v� gi� rao','Đọc mẫu tin và giá rao'],['T?ng h?p b�o c�o v� b?n d?','Tổng hợp báo cáo và bản đồ'],
    ['Chua ch?y.','Chưa chạy.'],['Thu� nh�','Thuê nhà'],['Van ph�ng','Văn phòng'],['S�n thuong m?i','Sàn thương mại'],['Chung cu','Chung cư'],
    ['Dang x?p h�ng x? ly','Đang xếp hàng xử lý'],['Dang kh?i t?o AI R&D','Đang khởi tạo AI R&D'],['AI R&D dang ch?y ph�n t�ch chung cu/th? tru?ng','AI R&D đang chạy phân tích chung cư/thị trường'],['Dang x�c d?nh v? tr�','Đang xác định vị trí'],['Dang ch?n t�i s?n/khu v?c so s�nh','Đang chọn tài sản/khu vực so sánh'],['Dang x�c d?nh tuy?n du?ng v� khu v?c','Đang xác định tuyến đường và khu vực'],['Dang t�m ngu?n d? li?u th? tru?ng','Đang tìm nguồn dữ liệu thị trường'],['Dang t�m m?u tin theo tuy?n du?ng','Đang tìm mẫu tin theo tuyến đường'],['Dang d?c m?u tin v� gi� rao','Đang đọc mẫu tin và giá rao'],['Dang ki?m tra gi� th? tru?ng','Đang kiểm tra giá thị trường'],['AI dang u?c t�nh gi� c� nhan ki?m ch?ng','AI đang ước tính giá có nhãn kiểm chứng'],['Dang t?ng h?p nh?n d?nh','Đang tổng hợp nhận định'],['Dang ph�n t�ch gi� b�n d? ki?n','Đang phân tích giá bán dự kiến'],['Dang d?ng b?n d? ki?m ch?ng','Đang dựng bản đồ kiểm chứng'],['Ho�n t?t b�o c�o','Hoàn tất báo cáo'],['Dang x? ly b�o c�o','Đang xử lý báo cáo'],
    ['Ma b�o c�o','Mã báo cáo'],['ph�t','phút'],['Bu?c d?c d? li?u th? tru?ng c� th? m?t 1-2 ph�t d? ki?m tra m?u tin v� ngu?n gi�.','Bước đọc dữ liệu thị trường có thể mất 1-2 phút để kiểm tra mẫu tin và nguồn giá.'],
    ['Dang kh?i t?o b�o c�o R&D...','Đang khởi tạo báo cáo R&D...'],['T?a d? chua d�ng','Tọa độ chưa đúng'],['Kh�ng t?o du?c b�o c�o','Không tạo được báo cáo'],['Kh�ng d?c du?c tr?ng th�i b�o c�o','Không đọc được trạng thái báo cáo'],['B�o c�o l?i','Báo cáo lỗi'],['L?i:','Lỗi:'],
    ['Ho�n t?t b�o c�o R&D th? tru?ng','Hoàn tất báo cáo R&D thị trường'],['Gi� trung b�nh d? xu?t','Giá trung bình đề xuất'],['da g?m VAT','đã gồm VAT'],['Ch? d? / d? tin c?y','Chế độ / độ tin cậy'],['Dang ki?m ch?ng','Đang kiểm chứng'],['M?u gi� / t?ng m?u','Mẫu giá / tổng mẫu'],['D?c di?m t?a d?','Đặc điểm tọa độ'],['B?n d? ki?m ch?ng','Bản đồ kiểm chứng'],['B�o c�o chi ti?t','Báo cáo chi tiết'],['Kh�ng c� n?i dung b�o c�o.','Không có nội dung báo cáo.'],['Xu?t b?n tr�nh b�y NotebookLM','Xuất bản trình bày NotebookLM']
  ];
  function fixText(s){ if(!s) return s; let o=String(s); for(const [a,b] of rdPairs) o=o.split(a).join(b); return o; }
  function fixNode(n){
    if(!n) return;
    if(n.nodeType===Node.TEXT_NODE){ const v=fixText(n.nodeValue); if(v!==n.nodeValue) n.nodeValue=v; return; }
    if(n.nodeType===Node.ELEMENT_NODE){ ['placeholder','title','aria-label','value'].forEach(a=>{ if(n.hasAttribute&&n.hasAttribute(a)){ const v=n.getAttribute(a), x=fixText(v); if(x!==v)n.setAttribute(a,x); }}); }
  }
  function run(root=document.body){ try{ fixNode(root); const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT); let n; while((n=w.nextNode())) fixNode(n); }catch(_){} }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>run()); else run();
  setTimeout(run,200); setTimeout(run,1000); setInterval(run,1500);
  try{ new MutationObserver(ms=>ms.forEach(m=>{fixNode(m.target); m.addedNodes&&m.addedNodes.forEach(run)})).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['placeholder','title','aria-label','value']}); }catch(_){}
})();
