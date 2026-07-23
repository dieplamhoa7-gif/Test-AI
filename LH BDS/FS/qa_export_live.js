const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ acceptDownloads: true });
  await p.goto('https://lhrealestate.web.app/fs.html?qa=' + Date.now(), { waitUntil: 'load', timeout: 120000 });
  await p.waitForTimeout(3000);
  const info = await p.evaluate(() => ({ sheets: buildSheets(P, SCHED, COST, COLL, true, COLL_SH).map(x => x.name), R: LASTR }));
  fs.writeFileSync('outputs/web_engine_latest.json', JSON.stringify(info.R, null, 2));
  const downloadPromise = p.waitForEvent('download');
  await p.evaluate(() => exportFull());
  const download = await downloadPromise;
  const out = 'C:/Users/HoaD-CVDT/.openclaw/workspace/LH BDS/FS/outputs/FS_FULL_live_native.xlsx';
  await download.saveAs(out);
  console.log(JSON.stringify({ out, sheets: info.sheets }));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
