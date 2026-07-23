from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT/'firebase_public/cw.html', ROOT/'firebase_public/warrants.html']
old = """let items=[]; try{const r=await fetch('/data/warrants_data.json?ts='+Date.now(),{cache:'no-store'}); const p=await r.json(); items=(Array.isArray(p.items)?p.items:p).map(x=>({...x,code:String(x.code||'').toUpperCase()}));}catch(e){}"""
new = """let items=[]; try{const r=await fetch('/data/warrants_data.json?ts='+Date.now(),{cache:'no-store'}); const p=await r.json(); items=(Array.isArray(p.items)?p.items:p).map(x=>({...x,code:String(x.code||'').toUpperCase()}));}catch(e){}
    async function refreshStandaloneLiveCw(){
      const codes=[...new Set([...document.querySelectorAll('[data-warrant]')].map(el=>String(el.dataset.warrant||'').toUpperCase()).filter(Boolean))].slice(0,120);
      if(!codes.length) return;
      const fresh=await Promise.all(codes.map(async code=>{try{return [code, await fetchVpsQuote(code)]}catch(_){return [code,null]}}));
      const by=new Map(items.map(x=>[String(x.code||'').toUpperCase(),x]));
      fresh.forEach(([code,q])=>{ if(!q) return; const old=by.get(code)||{}; const price=Number(q.lastPrice||q.marketPrice||q.price||0), ref=Number(q.refPrice||old.refPrice||0); by.set(code,{...old,...q,code,lastPrice:price,marketPrice:price,refPrice:ref,change:Number(q.change||0),changePct:Number(q.changePct||0),volume:Number(q.volume||0),bid:Number(q.bid||old.bid||0),ask:Number(q.ask||old.ask||0),realtimeUpdatedAt:new Date().toISOString()}); });
      items=[...by.values()]; const st=document.getElementById('warrantStatus')||document.querySelector('#apiStatus'); if(st)st.textContent='CW realtime VPS • '+new Date().toLocaleTimeString('vi-VN');
    }
    setInterval(()=>refreshStandaloneLiveCw().catch(()=>{}),15000); setTimeout(()=>refreshStandaloneLiveCw().catch(()=>{}),800);"""
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if old not in s:
        print('anchor missing', p)
        continue
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
    print('patched',p.relative_to(ROOT))
