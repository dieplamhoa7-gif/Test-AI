const wsUrl = 'ws://127.0.0.1:18800/devtools/page/2E3F806C8EBE1BB2359728A6959BA047';
const ws = new WebSocket(wsUrl);
let id=1;
function send(method, params={}){return new Promise((resolve,reject)=>{const mid=id++; const timer=setTimeout(()=>reject(new Error('timeout '+method)),20000); const on=ev=>{const msg=JSON.parse(ev.data); if(msg.id===mid){clearTimeout(timer); ws.removeEventListener('message',on); resolve(msg)}}; ws.addEventListener('message',on); ws.send(JSON.stringify({id:mid,method,params}));});}
ws.addEventListener('open', async()=>{
 try{
  await send('Runtime.enable');
  const expr=`(() => {
    const all=[...document.querySelectorAll('body, [role="main"], [role="list"], [data-tid], div, iframe')];
    return all.map((el,idx)=>({idx, tag:el.tagName, role:el.getAttribute('role'), tid:el.getAttribute('data-tid'), cls:(el.className||'').toString().slice(0,120), scrollTop:el.scrollTop, clientHeight:el.clientHeight, scrollHeight:el.scrollHeight, textLen:(el.innerText||'').length, sample:(el.innerText||'').slice(0,250)}))
      .filter(x=>x.textLen>0 || x.scrollHeight>x.clientHeight+200 || x.tag==='IFRAME')
      .sort((a,b)=>(b.textLen-a.textLen)||((b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight)))
      .slice(0,60);
  })()`;
  const res=await send('Runtime.evaluate',{expression:expr, returnByValue:true});
  console.log(JSON.stringify(res.result.result.value,null,2));
 } catch(e){console.error(e); process.exitCode=1;} finally {ws.close();}
});
