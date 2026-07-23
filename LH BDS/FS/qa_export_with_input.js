const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const input = 'C:/Users/HoaD-CVDT/Downloads/FS_INPUT_2026-07-23.xlsx';
  const out = 'C:/Users/HoaD-CVDT/.openclaw/workspace/LH BDS/FS/outputs/FS_FULL_input_2026-07-23_native.xlsx';
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ acceptDownloads: true });
  await p.goto('file:///C:/Users/HoaD-CVDT/.openclaw/workspace/LH%20BDS/public_final_2026_07_11/fs.html?qa=' + Date.now(), { waitUntil: 'load', timeout: 120000 });
  await p.setInputFiles('#file-imp', input);
  await p.waitForTimeout(4000);
  const R = await p.evaluate(() => LASTR);
  fs.writeFileSync('outputs/web_engine_input_2026-07-23.json', JSON.stringify(R, null, 2));
  const dp = p.waitForEvent('download');
  await p.evaluate(() => exportFull());
  const dl = await dp;
  await dl.saveAs(out);
  console.log(JSON.stringify({out, NPV:R.NPV, IRReq:R.IRReq, IRRprj:R.IRRprj, NPVsale:R.NPVsale}));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
