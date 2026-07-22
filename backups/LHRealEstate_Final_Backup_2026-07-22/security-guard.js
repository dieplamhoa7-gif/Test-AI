// LH Real Estate lightweight client-side protection.
// Note: browser code cannot be fully hidden; sensitive logic must stay server-side.
(function(){
  'use strict';
  var BRAND='LH Real Estate';
  try { Object.defineProperty(window,'__LH_REAL_ESTATE_OWNER__',{value:'LH Real Estate / Hòa',writable:false,configurable:false}); } catch(e) {}
  function block(e){
    try{
      var k=(e.key||'').toLowerCase();
      if(e.type==='contextmenu') return e.preventDefault(), false;
      if(e.ctrlKey && (k==='u'||k==='s'||k==='p')) return e.preventDefault(), false;
      if((e.ctrlKey&&e.shiftKey&&(k==='i'||k==='j'||k==='c')) || k==='f12') return e.preventDefault(), false;
    }catch(_){ }
  }
  document.addEventListener('contextmenu', block, {capture:true});
  document.addEventListener('keydown', block, {capture:true});
  var mark='\n\n/* '+BRAND+' protected build - unauthorized copying prohibited */';
  try { console.log('%c'+BRAND+' - protected application','color:#b38b2a;font-weight:700;font-size:16px'); } catch(e) {}
  // Add invisible watermark for copy provenance.
  try{
    var wm=document.createElement('meta'); wm.name='lh-realestate-owner'; wm.content='LH Real Estate / Hoa Investment'; document.head.appendChild(wm);
  }catch(e){}
})();
