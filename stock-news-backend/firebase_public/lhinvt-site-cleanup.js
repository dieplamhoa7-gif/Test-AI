// LHINVT — Vietnamese-first. Keep dark theme intact; polish only light mode.
(function(){
  function preferredTheme(){
    try { return localStorage.getItem('lh-theme') || localStorage.getItem('theme') || ''; } catch(e){ return ''; }
  }
  function syncThemeClass(){
    if(!document.body) return;
    const pref = preferredTheme();
    document.body.classList.add('lh-light-taste');
    if(pref === 'dark' || document.body.classList.contains('dark')) {
      if(document.body.classList.contains('light')) document.body.classList.remove('light');
      if(!document.body.classList.contains('dark')) document.body.classList.add('dark');
      return;
    }
    if(!document.body.classList.contains('light')) document.body.classList.add('light');
    if(document.body.classList.contains('dark')) document.body.classList.remove('dark');
  }
  function cleanup(){
    document.documentElement.lang='vi';
    syncThemeClass();
    document.querySelectorAll('#langEnBtn,.en-only,.lang-en').forEach(el=>el.remove());
    document.querySelectorAll('button,a,span,div').forEach(el=>{
      const t=(el.textContent||'').trim();
      if(t==='EN'||t==='English'||t==='ENG') el.remove();
    });
    document.querySelectorAll('.lang-toggle').forEach(el=>{
      const kids=[...el.children].filter(c=>!['EN','English','ENG'].includes((c.textContent||'').trim()));
      if(kids.length<=1) el.remove();
    });
  }
  cleanup();
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',cleanup,{once:true});
  else setTimeout(cleanup,0);
  window.addEventListener('load',()=>{cleanup();setTimeout(cleanup,100);setTimeout(cleanup,500);},{once:true});
})();
