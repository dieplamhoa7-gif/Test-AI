const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true}); const p=await b.newPage({viewport:{width:1600,height:1000}});
 await p.goto('http://127.0.0.1:8765/index.html',{waitUntil:'networkidle'});
 await p.fill('#search','Phú Quang'); await p.waitForTimeout(500);
 const cards=await p.locator('.project-card').count();
 if(cards) await p.locator('.project-card').first().click();
 await p.waitForTimeout(500);
 const out=await p.evaluate(()=>({
   cards:[...document.querySelectorAll('.project-card')].map(x=>x.innerText),
   title:document.querySelector('.detail-hero h2')?.innerText,
   sections:[...document.querySelectorAll('.info-group')].map(g=>({title:g.querySelector('h4')?.innerText,text:g.innerText.slice(0,3000)})),
   popup:document.querySelector('.leaflet-popup-content')?.innerText
 }));
 console.log(JSON.stringify(out,null,2));
 await p.screenshot({path:'phu_quang_before.png',fullPage:true}); await b.close();
})();
