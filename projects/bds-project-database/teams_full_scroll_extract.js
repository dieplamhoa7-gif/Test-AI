const fs = require('fs');
const path = require('path');
const wsUrl = 'ws://127.0.0.1:18800/devtools/page/2E3F806C8EBE1BB2359728A6959BA047';
const outDir = 'C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database/teams_batches';
fs.mkdirSync(outDir, {recursive:true});
const ws = new WebSocket(wsUrl);
let id = 1;
function send(method, params={}) {
  return new Promise((resolve,reject)=>{
    const mid=id++;
    const timer=setTimeout(()=>reject(new Error('timeout '+method)),15000);
    const on=(ev)=>{ const msg=JSON.parse(ev.data); if(msg.id===mid){ clearTimeout(timer); ws.removeEventListener('message', on); resolve(msg); } };
    ws.addEventListener('message', on);
    ws.send(JSON.stringify({id:mid,method,params}));
  });
}
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
function norm(s){ return (s||'').replace(/\s+/g,' ').trim(); }
ws.addEventListener('open', async()=>{
  const seen = new Set();
  const summary = [];
  try{
    await send('Runtime.enable');
    for(let i=1;i<=60;i++){
      const expr = `(() => {
        const candidates = [...document.querySelectorAll('[role="main"], [role="list"], [data-tid*="message"], div')]
          .filter(el => el.scrollHeight > el.clientHeight + 200)
          .sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight));
        const target = candidates.find(el => /Type a message|Translate|Message by|Báo cáo|dự án|DA |FS |maps\.app\.goo|www\.google/.test(el.innerText||'')) || candidates[0];
        const before = target ? target.scrollTop : null;
        const textBefore = (target?.innerText || document.body.innerText || '').slice(0,50000);
        if (target) {
          target.scrollTop = Math.max(0, target.scrollTop - Math.floor(target.clientHeight*0.85));
          target.dispatchEvent(new Event('scroll',{bubbles:true}));
        }
        return {found: !!target, before, after: target?.scrollTop, clientHeight: target?.clientHeight, scrollHeight: target?.scrollHeight, text: textBefore};
      })()`;
      const res = await send('Runtime.evaluate',{expression:expr, returnByValue:true, awaitPromise:true});
      const val = res?.result?.result?.value || {};
      const text = val.text || '';
      const key = norm(text).slice(0,500);
      const file = path.join(outDir, `batch_${String(i).padStart(3,'0')}.txt`);
      fs.writeFileSync(file, text, 'utf8');
      summary.push({i, before: val.before, after: val.after, len: text.length, duplicate: seen.has(key), file});
      seen.add(key);
      console.log(JSON.stringify(summary[summary.length-1]));
      if (val.after === 0 && i > 2) break;
      await sleep(2500);
    }
    fs.writeFileSync(path.join(outDir,'summary.json'), JSON.stringify(summary,null,2),'utf8');
  } catch(e){ console.error(e); process.exitCode=1; }
  ws.close();
});
