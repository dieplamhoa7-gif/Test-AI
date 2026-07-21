const { chromium } = require('playwright');
(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1600,height:1000}});
  await page.goto('http://127.0.0.1:8765/index.html',{waitUntil:'networkidle'});
  await page.waitForTimeout(1000);
  const data=await page.evaluate(()=>{
    const groups=[...document.querySelectorAll('.info-group')].map(g=>({
      title:g.querySelector('h4')?.innerText,
      rows:[...g.querySelectorAll('tr')].map(tr=>({
        label:tr.querySelector('th')?.innerText,
        renderType:tr.querySelector('td .value-list')?'list':(tr.querySelector('td .value-chips')?'chips':'plain'),
        itemCount:tr.querySelectorAll('td li, td .value-chip').length,
        value:tr.querySelector('td')?.innerText?.slice(0,350)
      }))
    }));
    return {title:document.querySelector('.detail-hero h2')?.innerText, groups};
  });
  console.log(JSON.stringify(data,null,2));
  await browser.close();
})();
