// LH local high-tech motion preview — safe, no dependencies
(function(){
  const root=document.documentElement;
  document.addEventListener('pointermove',e=>{
    root.style.setProperty('--mx', e.clientX+'px');
    root.style.setProperty('--my', e.clientY+'px');
    const cards=document.querySelectorAll('.taste-tool,.card,.panel,.kpi,.metric');
    cards.forEach(el=>{
      const r=el.getBoundingClientRect();
      if(e.clientX<r.left-80||e.clientX>r.right+80||e.clientY<r.top-80||e.clientY>r.bottom+80) return;
      const x=((e.clientX-r.left)/Math.max(r.width,1))*100;
      const y=((e.clientY-r.top)/Math.max(r.height,1))*100;
      el.style.setProperty('--sx', x+'%');
      el.style.setProperty('--sy', y+'%');
    });
  },{passive:true});
  const tiltEls=[...document.querySelectorAll('.taste-tool,.taste-figure')];
  tiltEls.forEach(el=>{
    el.addEventListener('pointermove',e=>{
      const r=el.getBoundingClientRect();
      const px=(e.clientX-r.left)/r.width-.5;
      const py=(e.clientY-r.top)/r.height-.5;
      el.style.transform=`perspective(900px) rotateX(${(-py*4).toFixed(2)}deg) rotateY(${(px*5).toFixed(2)}deg) translateY(-3px)`;
    });
    el.addEventListener('pointerleave',()=>{el.style.transform='';});
  });
  const obs=new IntersectionObserver(entries=>{
    entries.forEach(en=>{ if(en.isIntersecting) en.target.classList.add('in-view'); });
  },{threshold:.16});
  document.querySelectorAll('.taste-hero,.taste-tool,.panel,.card,.kpi').forEach(el=>{el.classList.add('reveal');obs.observe(el);});
})();
