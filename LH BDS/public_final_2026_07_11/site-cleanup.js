// LH Real Estate — Vietnamese-first cleanup + light taste default
(function(){
  function cleanup(){
    document.body && document.body.classList.remove('hightech');
    document.querySelectorAll('#langEnBtn,.lang-en,.en-only,.language-toggle,.lang-toggle').forEach(el=>el.remove());
    document.querySelectorAll('button,a,span,div').forEach(el=>{
      const t=(el.textContent||'').trim();
      if(t==='EN'||t==='English'||t==='ENG') el.remove();
    });
    document.documentElement.lang='vi';
  }
  cleanup();
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',cleanup,{once:true});
  else setTimeout(cleanup,0);
  window.addEventListener('load',()=>{ cleanup(); setTimeout(cleanup,50); setTimeout(cleanup,300); },{once:true});
})();
