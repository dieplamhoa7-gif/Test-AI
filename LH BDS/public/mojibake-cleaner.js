// LH Real Estate Vietnamese mojibake cleaner.
// Presentation-only: cleans visible DOM text/labels without touching app logic.
(function(){
  const pairs = [
    ['hÆ¡n','hơn'],['CÆ¡','Cơ'],['cÅ©','cũ'],['má»›i','mới'],['vá»±c','vực'],['bá»™','bộ'],['Tá»·','Tỷ'],['tá»·','tỷ'],['thá»a','thửa'],['Lá»—i','Lỗi'],['dá»±ng','dựng'],['dá»±','dự'],['dá»¯','dữ'],['rá»™ng','rộng'],['phá»‘','phố'],['Bá»™','Bộ'],
    ['Ä‘','đ'],['Ä�','Đ'],['Æ°','ư'],['Æ¡','ơ'],['Æ¯','Ư'],['Æ ','Ơ'],
    ['á»‹','ị'],['á»‰','ỉ'],['á»‡','ệ'],['á»ƒ','ể'],['á»�','ề'],['áº¿','ế'],['áº¹','ẹ'],['áº»','ẻ'],['áº½','ẽ'],['á»™','ộ'],['á»“','ồ'],['á»‘','ố'],['á»•','ổ'],['á»—','ỗ'],['á»£','ợ'],['á»�','ờ'],['á»›','ớ'],['á»Ÿ','ở'],['á»¡','ỡ'],['á»¥','ụ'],['á»§','ủ'],['á»©','ứ'],['á»«','ừ'],['á»­','ử'],['á»¯','ữ'],['á»±','ự'],['á»³','ỳ'],['á»·','ỷ'],['á»¹','ỹ'],
    ['áº¡','ạ'],['áº£','ả'],['áº¥','ấ'],['áº§','ầ'],['áº©','ẩ'],['áº«','ẫ'],['áº­','ậ'],['áº¯','ắ'],['áº±','ằ'],['áº³','ẳ'],['áºµ','ẵ'],['áº·','ặ'],
    ['Ã¡','á'],['Ã ','à'],['Ã¢','â'],['Ã£','ã'],['Ã©','é'],['Ã¨','è'],['Ãª','ê'],['Ã­','í'],['Ã¬','ì'],['Ã³','ó'],['Ã²','ò'],['Ã´','ô'],['Ãµ','õ'],['Ãº','ú'],['Ã¹','ù'],['Ã½','ý'],
    ['Â²','²'],['Â°','°'],['Â·','·'],['Â ',' '],['â€“','–'],['â€”','—'],['â€¦','…'],['â€œ','“'],['â€','”'],['â€˜','‘'],['â€™','’'],['â‚«','₫'],['â‰¥','≥'],['â‰¤','≤'],['â†’','→'],
    ['Phưá»�ng','Phường'],['phưá»�ng','phường'],['PhÆ°á»�ng','Phường'],['phÆ°á»�ng','phường'],['ThA�nh ph��`','Thành phố'],['ThA�nh ph��','Thành phố'],['bA�n','bán']
  ];
  function clean(s){
    if(typeof s !== 'string' || !s) return s;
    let out = s;
    for(const [a,b] of pairs) out = out.split(a).join(b);
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
