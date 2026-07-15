const { chromium } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage();
 page.on('console', m=>console.log('CONSOLE',m.type(),m.text()));
 page.on('pageerror', e=>console.log('PAGEERROR',e.message));
 const resp=await page.goto('http://127.0.0.1:8787/tpre_flowchart_popup.html',{waitUntil:'domcontentloaded'});
 console.log('status', resp.status(), await page.title());
 await page.waitForTimeout(3000);
 console.log('body', (await page.locator('body').innerText().catch(e=>String(e))).slice(0,1000));
 console.log('nodes', await page.locator('.node').count());
 console.log('html', (await page.content()).slice(0,1000));
 await browser.close();
})();
