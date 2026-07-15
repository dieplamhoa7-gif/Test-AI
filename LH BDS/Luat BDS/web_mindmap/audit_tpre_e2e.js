const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const base = process.cwd();
const dataPath = path.join(base, 'LH BDS', 'Luat BDS', 'web_mindmap', 'tpre_bds_flow.json');
const htmlPath = path.join(base, 'LH BDS', 'Luat BDS', 'web_mindmap', 'tpre_flowchart_popup.html');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const required = {
  I: ['Luật Đầu tư','Luật Đất đai','Luật Nhà ở','Luật Quy hoạch'],
  II: ['Luật Đất đai','NĐ 102','NĐ 103'],
  III: ['Luật Đầu tư','Luật Đất đai'],
  IV: ['Luật Quy hoạch','Luật Nhà ở','Luật Kiến trúc'],
  V: ['Luật Đất đai','NĐ 102','NĐ 103','NĐ 71','NĐ 101'],
  VI: ['Luật Xây dựng','Luật BVMT','Luật PCCC','Luật Tài nguyên nước','Luật Điện lực'],
  VII: ['Luật Xây dựng','NĐ quản lý chất lượng','Luật An toàn'],
  VIII: ['Luật KDBĐS','NĐ 96','Thông tư NHNN','Luật Nhà ở','Luật Bảo vệ quyền lợi người tiêu dùng'],
  IX: ['NĐ quản lý chất lượng','Luật PCCC','Luật BVMT'],
  X: ['NĐ 101','NĐ quản lý chất lượng','Luật KDBĐS','Bộ luật Dân sự'],
  XI: ['NĐ quản lý chất lượng','NĐ 101','Luật KDBĐS','Luật Quản lý, sử dụng tài sản công']
};
let issues=[];
for (const ph of data.phases) {
  const pref = ph.id.split('.')[0];
  const item = ph.items[0];
  const docs = item.legal_basis.map(l => `${l.doc} ${l.article}`).join(' | ');
  const phaseReq = [...(required[pref]||[])];
  if (ph.id === 'III.2') phaseReq.push('Luật Đấu giá');
  if (ph.id === 'III.3') phaseReq.push('Luật Đấu thầu');
  const miss = phaseReq.filter(r => !docs.toLowerCase().includes(r.toLowerCase()));
  if (miss.length) issues.push({phase: ph.id, type:'missing-required-law', miss, docs});
  if (!item.phase_detail) issues.push({phase: ph.id, type:'missing-phase-detail'});
  if (!item.statutory_timeline?.length) issues.push({phase: ph.id, type:'missing-timeline'});
  if (!item.legal_basis?.length) issues.push({phase: ph.id, type:'missing-laws'});
  for (const l of item.legal_basis) {
    const txt = JSON.stringify(l);
    if (txt.includes('??') || txt.includes('Lu?t ') || txt.includes('N? ')) issues.push({phase: ph.id, type:'mojibake', doc:l.doc});
    if (!l.points || l.points.length < 3) issues.push({phase: ph.id, type:'thin-law', doc:l.doc});
  }
}
console.log('DATA_PHASES', data.phases.length);
console.log('DATA_ISSUES', JSON.stringify(issues, null, 2));

(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1200}});
  const errors=[];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type()==='error') errors.push(msg.text()); });
  const targetUrl = process.env.TPRE_URL || 'http://127.0.0.1:8879/tpre_flowchart_popup.html';
  await page.goto(targetUrl, {waitUntil:'networkidle'});
  await page.waitForSelector('.node', {timeout:10000});
  const count = await page.locator('.node').count();
  const modalResults=[];
  for (let i=0;i<count;i++) {
    await page.locator('.node').nth(i).evaluate(el => el.click());
    await page.waitForSelector('#modal.open', {timeout:5000});
    const code = await page.locator('#mcode').innerText().catch(()=>'?');
    const text = await page.locator('#modal').innerText();
    const hasPlaybookBox = await page.locator('#modal .playbookBox').count().then(n => n > 0).catch(()=>false);
    modalResults.push({code, hasPlaybook:hasPlaybookBox || text.includes('Playbook'), hasTimeline:text.includes('Thời gian') || text.includes('Timeline'), hasLaw:text.includes('Luật') || text.includes('NĐ'), len:text.length});
    await page.keyboard.press('Escape').catch(()=>{});
    await page.evaluate(() => document.getElementById('modal')?.classList.remove('open'));
  }
  await browser.close();
  const uiIssues = modalResults.filter(r => !r.hasLaw || !r.hasTimeline || r.len < 500);
  console.log('UI_NODES', count);
  console.log('UI_ERRORS', JSON.stringify(errors, null, 2));
  console.log('UI_ISSUES', JSON.stringify(uiIssues, null, 2));
  console.log('UI_SAMPLE', JSON.stringify(modalResults.slice(0,5), null, 2));
  if (issues.length || errors.length || uiIssues.length) process.exitCode = 2;
})();
