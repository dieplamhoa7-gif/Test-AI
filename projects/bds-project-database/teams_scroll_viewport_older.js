const fs = require('fs');
const path = require('path');
const wsUrl = 'ws://127.0.0.1:18800/devtools/page/2E3F806C8EBE1BB2359728A6959BA047';
const outDir = 'C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database/teams_batches';
fs.mkdirSync(outDir, {recursive:true});
const ws = new WebSocket(wsUrl);
let id=1;
function send(method, params={}){return new Promise((resolve,reject)=>{const mid=id++; const timer=setTimeout(()=>reject(new Error('timeout '+method)),30000); const on=ev=>{const msg=JSON.parse(ev.data); if(msg.id===mid){clearTimeout(timer); ws.removeEventListener('message',on); resolve(msg)}}; ws.addEventListener('message',on); ws.send(JSON.stringify({id:mid,method,params}));});}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
function norm(s){return (s||'').replace(/\s+/g,' ').trim();}
async function evalExpr(expression){const res=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true}); return res?.result?.result?.value;}
const extractExpr = `(() => {
 const target=document.querySelector('[data-tid="message-pane-list-viewport"]');
 const root=target || document.querySelector('[data-tid="message-pane-body"]') || document.body;
 const text=(root.innerText||document.body.innerText||'').slice(0,80000);
 const dates=[...text.matchAll(/(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\\s+[A-Za-z]+\\s+\\d{1,2},?\\s+\\d{4}|\\b\\d{1,2}\/\\d{1,2}\/\\d{4}\\s+\\d{1,2}:\\d{2}\\s+[AP]M|\\b\\d{1,2}\/\\d{1,2}\/\\d{4}/g)].slice(0,20).map(m=>m[0]);
 return {found:!!target, scrollTop:target?.scrollTop??null, clientHeight:target?.clientHeight??null, scrollHeight:target?.scrollHeight??null, len:text.length, dates, text};
})()`;
const upExpr = `(() => {
 const target=document.querySelector('[data-tid="message-pane-list-viewport"]');
 if(!target) return {found:false};
 const before=target.scrollTop;
 target.scrollTop=Math.max(0,target.scrollTop-Math.floor(target.clientHeight*0.8));
 target.dispatchEvent(new Event('scroll',{bubbles:true}));
 target.dispatchEvent(new WheelEvent('wheel',{deltaY:-1200,bubbles:true,cancelable:true}));
 return {found:true,before,after:target.scrollTop,clientHeight:target.clientHeight,scrollHeight:target.scrollHeight};
})()`;
ws.addEventListener('open',async()=>{
 const seen=new Set(); const summary=[]; let stale=0;
 try{
  await send('Runtime.enable');
  for(let i=917;i<=1500;i++){
   const val=await evalExpr(extractExpr)||{};
   const text=val.text||''; const key=norm(text).slice(0,1200); const duplicate=seen.has(key);
   const file=path.join(outDir,`batch_${String(i).padStart(3,'0')}.txt`);
   fs.writeFileSync(file,text,'utf8');
   seen.add(key); stale=duplicate?stale+1:0;
   const row={i,found:val.found,scrollTop:val.scrollTop,clientHeight:val.clientHeight,scrollHeight:val.scrollHeight,len:text.length,dates:val.dates,duplicate,stale,file};
   summary.push(row); console.log(JSON.stringify(row));
   if(stale>=15 && val.scrollTop===0) break;
   for(let k=0;k<3;k++){await evalExpr(upExpr); await sleep(2200);} 
   // extra wait at top to let Teams prepend older messages
   const cur=await evalExpr(`(() => {const t=document.querySelector('[data-tid="message-pane-list-viewport"]'); return {top:t?.scrollTop??null,height:t?.scrollHeight??null};})()`);
   if(cur && cur.top===0) await sleep(7000);
  }
  fs.writeFileSync(path.join(outDir,'summary_viewport_older.json'),JSON.stringify(summary,null,2),'utf8');
 }catch(e){console.error(e); process.exitCode=1;} finally{ws.close();}
});
