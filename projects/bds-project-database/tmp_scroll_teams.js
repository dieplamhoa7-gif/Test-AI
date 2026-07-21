const wsUrl = 'ws://127.0.0.1:18800/devtools/page/2E3F806C8EBE1BB2359728A6959BA047';
const ws = new WebSocket(wsUrl);
let id = 1;
function send(method, params={}) {
  return new Promise((resolve,reject)=>{
    const mid=id++;
    const timer=setTimeout(()=>reject(new Error('timeout '+method)),10000);
    const on=(ev)=>{
      const msg=JSON.parse(ev.data);
      if(msg.id===mid){ clearTimeout(timer); ws.removeEventListener('message', on); resolve(msg); }
    };
    ws.addEventListener('message', on);
    ws.send(JSON.stringify({id:mid,method,params}));
  });
}
ws.addEventListener('open', async()=>{
  try{
    await send('Runtime.enable');
    const expr = `(() => {
      const candidates = [...document.querySelectorAll('[role="main"], [role="list"], [data-tid*="message"], div')]
        .filter(el => el.scrollHeight > el.clientHeight + 200)
        .sort((a,b)=>(b.scrollHeight-b.clientHeight)-(a.scrollHeight-a.clientHeight));
      const target = candidates.find(el => /mở rộng đường LVV|maps\\.app\\.goo|Type a message|Translate/.test(el.innerText||'')) || candidates[0];
      if (target) {
        target.scrollTop = Math.max(0, target.scrollTop - Math.floor(target.clientHeight*0.8));
        target.dispatchEvent(new Event('scroll',{bubbles:true}));
      }
      return {found: !!target, scrollTop: target?.scrollTop, clientHeight: target?.clientHeight, scrollHeight: target?.scrollHeight, text: (target?.innerText || document.body.innerText).slice(0,12000)};
    })()`;
    const res = await send('Runtime.evaluate',{expression:expr, returnByValue:true, awaitPromise:true});
    console.log(JSON.stringify(res.result.result.value,null,2));
  } catch(e){ console.error(e); process.exitCode=1; }
  ws.close();
});
