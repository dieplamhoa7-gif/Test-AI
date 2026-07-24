// LHINVT — Vietnamese-first + force light taste
(function(){
  function cleanup(){
    document.documentElement.lang='vi';
    if(document.body){
      document.body.classList.add('light','lh-light-taste');
      document.body.classList.remove('dark');
    }
    document.querySelectorAll('#langEnBtn,#langViBtn,.lang-toggle,.lang-btn,[data-lang],.en-only,.lang-en').forEach(el=>el.remove());
    document.querySelectorAll('button,a,span,div').forEach(el=>{
      const t=(el.textContent||'').trim();
      if(t==='EN'||t==='VI'||t==='English'||t==='ENG') el.remove();
    });
    document.querySelectorAll('#themeToggle,.theme-toggle').forEach(el=>el.remove());
  }
  cleanup();
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',cleanup,{once:true});
  else setTimeout(cleanup,0);
  window.addEventListener('load',()=>{cleanup();setTimeout(cleanup,100);setTimeout(cleanup,500);},{once:true});
})();
