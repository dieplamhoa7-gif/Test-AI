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
    const timer=setTimeout(()=>reject(new Error('timeout '+method)),30000);
    const on=(ev)=>{ const msg=JSON.parse(ev.data); if(msg.id===mid){ clearTimeout(timer); ws.removeEventListener('message', on); resolve(msg); } };
    ws.addEventListener('message', on);
    ws.send(JSON.stringify({id:mid,method,params}));
  });
}
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
function norm(s){ return (s||'').replace(/\s+/g,' ').trim(); }
function esc(s){ return JSON.stringify(s); }
async function evalExpr(expression){
  const res = await send('Runtime.evaluate',{expression, returnByValue:true, awaitPromise:true});
  return res?.result?.result?.value;
}
const extractExpr = `(() => {
  const candidates = [...document.querySelectorAll('[role="main"], [role="list"], [data-tid*="message"], div')]
    .filter(el => el.scrollHeight > el.clientHeight + 200)
    .sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight));
  const target = candidates.find(el => /Type a message|Translate|Message by|Báo cáo|dự án|DA |FS |maps\\.app\\.goo|www\\.google|\d{1,2}\/\d{1,2}\/\d{4}/.test(el.innerText||'')) || candidates[0];
  const text = (target?.innerText || document.body.innerText || '').slice(0,50000);
  return {found:!!target,before:target?.scrollTop??null,clientHeight:target?.clientHeight??null,scrollHeight:target?.scrollHeight??null,text};
})()`;
const forceOlderExpr = `(() => {
  const candidates = [...document.querySelectorAll('[role="main"], [role="list"], [data-tid*="message"], div')]
    .filter(el => el.scrollHeight > el.clientHeight + 200)
    .sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight));
  const target = candidates.find(el => /Type a message|Translate|Message by|Báo cáo|dự án|DA |FS |maps\\.app\\.goo|www\\.google|\d{1,2}\/\d{1,2}\/\d{4}/.test(el.innerText||'')) || candidates[0];
  if (!target) return {found:false};
  target.focus?.();
  const before = target.scrollTop;
  target.scrollTop = 0;
  target.dispatchEvent(new Event('scroll',{bubbles:true}));
  target.dispatchEvent(new WheelEvent('wheel',{deltaY:-3000,bubbles:true,cancelable:true}));
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'PageUp',code:'PageUp',bubbles:true}));
  document.dispatchEvent(new KeyboardEvent('keyup',{key:'PageUp',code:'PageUp',bubbles:true}));
  return {found:true,before,after:target.scrollTop,clientHeight:target.clientHeight,scrollHeight:target.scrollHeight};
})()`;
ws.addEventListener('open', async()=>{
  const seen = new Set();
  const summary = [];
  let stale = 0;
  try{
    await send('Runtime.enable');
    // seed seen with latest saved top-ish files to detect movement
    for (let j=880;j<=916;j++) {
      const p=path.join(outDir,`batch_${String(j).padStart(3,'0')}.txt`);
      if (fs.existsSync(p)) seen.add(norm(fs.readFileSync(p,'utf8')).slice(0,1000));
    }
    for(let i=917;i<=1300;i++){
      for (let k=0;k<6;k++) { await evalExpr(forceOlderExpr); await sleep(2500); }
      const val = await evalExpr(extractExpr) || {};
      const text = val.text || '';
      const key = norm(text).slice(0,1000);
      const duplicate = seen.has(key);
      const file = path.join(outDir, `batch_${String(i).padStart(3,'0')}.txt`);
      fs.writeFileSync(file, text, 'utf8');
      seen.add(key);
      if (duplicate) stale++; else stale=0;
      const row={i,before:val.before,clientHeight:val.clientHeight,scrollHeight:val.scrollHeight,len:text.length,duplicate,stale,file};
      summary.push(row);
      console.log(JSON.stringify(row));
      // stop only after many cycles at top with identical text; this means no older data is loading
      if (stale>=12) break;
    }
    fs.writeFileSync(path.join(outDir,'summary_older_after_top.json'), JSON.stringify(summary,null,2),'utf8');
  } catch(e){ console.error(e); process.exitCode=1; }
  ws.close();
});
