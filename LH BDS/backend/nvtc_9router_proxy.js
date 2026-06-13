// Local-only 9Router proxy for NVTC Dao Tri web app.
// Keeps the BDS 9Router key out of browser HTML/localStorage.
// Usage: node nvtc_9router_proxy.js
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = Number(process.env.NVTC_PROXY_PORT || 8787);
const LOCAL_9ROUTER_BASE = process.env.NINEROUTER_BASE_URL || 'http://localhost:20128/v1';
const FALLBACK_MODEL = process.env.NINEROUTER_BDS_MODEL || process.env.NINEROUTER_MODEL || 'APIBDS';
const PRIVATE_KEY_FILE = path.join(__dirname, '9router_private_keys', '9router_split_keys_private.txt');
let lookupHcmPlanning = null, summarize = null, lookupK1LandFee = null;
let readQhVietPopupText = null, parseQhVietPopupText = null, readGulandPopupText = null, parseGulandPopupText = null;
try { ({ lookupHcmPlanning, summarize } = require('./bds_planning_checker')); } catch (_) { try { ({ lookupHcmPlanning, summarize } = require('../../bds_planning_checker')); } catch (__) {} }
try { ({ lookupK1LandFee } = require('./k1_land_fee_lookup')); } catch (_) { try { ({ lookupK1LandFee } = require('../../k1_land_fee_lookup')); } catch (__) {} }
try { ({ readQhVietPopupText, readGulandPopupText } = require('./planning_browser_popups')); } catch (_) { try { ({ readQhVietPopupText, readGulandPopupText } = require('../../planning_browser_popups')); } catch (__) {} }
try { ({ parseQhVietPopupText } = require('./qhviet_popup_parser')); } catch (_) { try { ({ parseQhVietPopupText } = require('../../qhviet_popup_parser')); } catch (__) {} }
try { ({ parseGulandPopupText } = require('./guland_popup_parser')); } catch (_) { try { ({ parseGulandPopupText } = require('../../guland_popup_parser')); } catch (__) {} }

function findExistingPath(...paths) {
  for (const p of paths) { try { if (p && fs.existsSync(p)) return p; } catch (_) {} }
  return paths.find(Boolean) || '';
}

function k1SourcePage(page) {
  const n = Number(page || 0);
  if (!Number.isFinite(n) || n <= 0) return null;
  const jsonPath = findExistingPath(
    path.join(__dirname, 'exports', 'k1_pdf_relevant_extract.json'),
    path.join(__dirname, '..', 'exports', 'k1_pdf_relevant_extract.json'),
    path.join(__dirname, '..', '..', 'exports', 'k1_pdf_relevant_extract.json')
  );
  const rows = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  const hits = rows.filter(r => Number(r.page) === n || Number(r.pageNo) === n || Number(r.page_index) === n);
  return { page: n, count: hits.length, rows: hits.slice(0, 25), text: hits.map(r => r.text || r.raw || r.content || '').filter(Boolean).join('\n\n') };
}

function readBdsKey() {
  const envKey = process.env.BDS_9ROUTER_API_KEY || process.env.NINEROUTER_API_KEY || process.env.OPENAI_API_KEY;
  if (envKey) return envKey.trim();
  try {
    const txt = fs.readFileSync(PRIVATE_KEY_FILE, 'utf8');
    const m = txt.match(/^\s*BDS_9ROUTER_API_KEY\s*=\s*(.+?)\s*$/m) || txt.match(/^\s*NINEROUTER_API_KEY\s*=\s*(.+?)\s*$/m);
    return m ? m[1].trim().replace(/^['"]|['"]$/g, '') : '';
  } catch { return ''; }
}


function cleanVietnameseText(x) {
  if (typeof x !== 'string') return x;
  const bad = String.fromCharCode(0xfffd);
  const moji = (...codes) => String.fromCharCode(...codes);
  return x
    .replaceAll('Phư' + bad + 'ng', 'Phường').replaceAll('phư' + bad + 'ng', 'phường')
    .replaceAll('Qu' + bad + 'n', 'Quận').replaceAll('qu' + bad + 'n', 'quận')
    .replaceAll('Huy' + bad + 'n', 'Huyện').replaceAll('huy' + bad + 'n', 'huyện')
    .replaceAll('Th' + bad + 'nh phố', 'Thành phố').replaceAll('th' + bad + 'nh phố', 'thành phố')
    .replaceAll('Đ' + bad + 'ng', 'Đông').replaceAll('đ' + bad + 'ng', 'đông')
    .replaceAll('T' + bad + 'y', 'Tây').replaceAll('t' + bad + 'y', 'tây')
    .replaceAll('B' + bad + 'o', 'Báo').replaceAll('b' + bad + 'o', 'báo').replaceAll('c' + bad + 'o', 'cáo')
    .replaceAll('gi' + bad, 'giá').replaceAll('Gi' + bad, 'Giá')
    .replaceAll('dữ li' + bad + 'u', 'dữ liệu').replaceAll('d' + bad + ' liệu', 'dữ liệu')
    .replaceAll('d' + bad + ' án', 'dự án').replaceAll('D' + bad + ' án', 'Dự án').replaceAll('dự ' + bad + 'n', 'dự án')
    .replaceAll('vị tr' + bad, 'vị trí').replaceAll('tiện ' + bad + 'ch', 'tiện ích').replaceAll('hạ t' + bad + 'ng', 'hạ tầng')
    .replaceAll('ph' + bad + 'n tích', 'phân tích').replaceAll('kiểm ch' + bad + 'ng', 'kiểm chứng')
    .replaceAll('ngu' + bad + 'n', 'nguồn').replaceAll('đề xu' + bad + 't', 'đề xuất')
    .replaceAll('trung b' + bad + 'nh', 'trung bình').replaceAll('da g' + bad + 'm VAT', 'đã gồm VAT')
    .replaceAll('so s' + bad + 'nh', 'so sánh')
    .replaceAll(moji(84,63,111), 'Tạo').replaceAll(moji(68,63,32,108,105,63,117), 'Dữ liệu').replaceAll(moji(100,63,32,108,105,63,117), 'dữ liệu')
    .replaceAll('Dang', 'Đang')
    .replaceAll(moji(84,104,195,32,110,104), 'Thành').replaceAll(moji(116,104,195,32,110,104), 'thành')
    .replaceAll(moji(112,104,225,187,8216), 'phố').replaceAll(moji(72,225,187,8220), 'Hồ').replaceAll(moji(67,104,195,173), 'Chí')
    .replaceAll('CÃ¡ch', 'Cách').replaceAll('Máº¡ng', 'Mạng').replaceAll('ThÃ¡ng', 'Tháng').replaceAll('TÃ¡m', 'Tám')
    .replaceAll('PhÆ°á»\uFFFDng', 'Phường').replaceAll('HÃ²a', 'Hòa').replaceAll('HÆ°ng', 'Hưng').replaceAll('ThÃ nh', 'Thành').replaceAll('phá»‘', 'phố')
    .replaceAll('Ä\uFFFDá»©c', 'Đức').replaceAll('ĐứcTám', 'Đức Tám')
    .replaceAll('Tháng ủ Đức Tám', 'Tháng Tám').replaceAll('Tháng Thủ Đức Tám', 'Tháng Tám').replaceAll('Thà nh', 'Thành').replaceAll('thà nh', 'thành')
    .replaceAll('Thá»§ Ä\uFFFDức', 'Thủ Đức').replaceAll('Thá»§ Đức', 'Thủ Đức').replaceAll('Thủ Ä\uFFFDức', 'Thủ Đức')
    .replaceAll('ThÃ nh phố', 'Thành phố').replaceAll('ThA\uFFFDnh phố', 'Thành phố').replaceAll('ThA\uFFFDnh ph\uFFFD\uFFFD', 'Thành phố')
    .replaceAll('PhÆ°á»\uFFFDng', 'Phường').replaceAll('phÆ°á»\uFFFDng', 'phường').replaceAll('Phưá»\uFFFDng', 'Phường').replaceAll('phưá»\uFFFDng', 'phường')
    .replaceAll('HÃ²a', 'Hòa').replaceAll('HoÃ ', 'Hoà').replaceAll('HÃưng', 'Hưng')
    .replaceAll('Ä\uFFFDức', 'Đức').replaceAll('Ä‘ức', 'đức')
    .replaceAll('Ä‘', 'đ').replaceAll('Ä\uFFFD', 'Đ').replaceAll('Æ°', 'ư').replaceAll('Æ¡', 'ơ')
    .replaceAll('á»§', 'ủ').replaceAll('á»©', 'ứ').replaceAll('á»«', 'ừ').replaceAll('á»­', 'ử').replaceAll('á»¯', 'ữ').replaceAll('á»±', 'ự')
    .replaceAll('á»™', 'ộ').replaceAll('á»“', 'ồ').replaceAll('á»‘', 'ố').replaceAll('á»•', 'ổ').replaceAll('á»—', 'ỗ')
    .replaceAll('á»›', 'ớ').replaceAll('á»\uFFFD', 'ờ').replaceAll('á»Ÿ', 'ở').replaceAll('á»£', 'ợ')
    .replaceAll('áº¡', 'ạ').replaceAll('áº£', 'ả').replaceAll('áº¥', 'ấ').replaceAll('áº§', 'ầ').replaceAll('áº©', 'ẩ').replaceAll('áº«', 'ẫ').replaceAll('áº­', 'ậ')
    .replaceAll('áº¯', 'ắ').replaceAll('áº±', 'ằ').replaceAll('áº³', 'ẳ').replaceAll('áºµ', 'ẵ').replaceAll('áº·', 'ặ')
    .replaceAll('á»‹', 'ị').replaceAll('á»‰', 'ỉ').replaceAll('á»‡', 'ệ').replaceAll('á»ƒ', 'ể').replaceAll('áº¿', 'ế')
    .replaceAll('Ã¡', 'á').replaceAll('Ã ', 'à').replaceAll('Ã¢', 'â').replaceAll('Ã£', 'ã').replaceAll('Ã©', 'é').replaceAll('Ã¨', 'è').replaceAll('Ãª', 'ê')
    .replaceAll('Ã­', 'í').replaceAll('Ã¬', 'ì').replaceAll('Ã³', 'ó').replaceAll('Ã²', 'ò').replaceAll('Ã´', 'ô').replaceAll('Ãµ', 'õ').replaceAll('Ãº', 'ú').replaceAll('Ã¹', 'ù').replaceAll('Ã½', 'ý')
    .replaceAll('batdongsan.com.vn', 'batdongsan.com.vn')
    .replaceAll(moji(196,63), 'Đ').replaceAll(moji(196,8216), 'đ')
    .replaceAll('ThÃ¡ng á»§ Ä\uFFFDá»©cTÃ¡m', 'Tháng Tám').replaceAll('Tháng ủ ĐứcTám', 'Tháng Tám').replaceAll('Tháng ủ Đức Tám', 'Tháng Tám').replaceAll('Tháng Thủ ĐứcTám', 'Tháng Tám').replaceAll('Tháng Thủ Đức Tám', 'Tháng Tám')
    .replaceAll('Phường Hòa Hưng Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh').replaceAll('Phường Hòa Hưng, Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('Hòa Hưng, Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh').replaceAll('Hòa Hưng Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('Phường Hòa Hưng Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('Phường Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('Hòa Hưng, Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('Thành phố Hồ Chí Minh Thành phố Thủ Đức', 'Thành phố Hồ Chí Minh')
    .replaceAll('Thành phố Hồ Chí Minh, Thành phố Thủ Đức', 'Thành phố Hồ Chí Minh')
    .replaceAll('Phường Hòa Hưng, Thành phố Hồ Chí Minh, Phường Hòa Hưng, Thành phố Hồ Chí Minh', 'Phường Hòa Hưng, Thành phố Hồ Chí Minh')
    .replaceAll('\uFFFDức', 'Đức').replaceAll('\uFFFDỨc', 'Đức').replaceAll('\uFFFD đức', ' Đức')
    .replaceAll('Tháng ĐứcTám', 'Tháng Tám').replaceAll('Tháng Đức Tám', 'Tháng Tám')
    .replaceAll('Tháng \uFFFDứcTám', 'Tháng Tám').replaceAll('Tháng \uFFFDức Tám', 'Tháng Tám')
    .replaceAll('Thà nh', 'Thành').replaceAll('thà nh', 'thành');
}
function cleanVietnameseObject(obj) {
  if (typeof obj === 'string') return cleanVietnameseText(obj);
  if (Array.isArray(obj)) return obj.map(cleanVietnameseObject);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k,v] of Object.entries(obj)) out[cleanVietnameseText(k)] = cleanVietnameseObject(v);
    return out;
  }
  return obj;
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS, GET');
  res.setHeader('Access-Control-Allow-Headers', 'content-type, authorization');
}

function findExistingPath(candidates){
  const list = Array.isArray(candidates) ? candidates : Array.from(arguments);
  return list.find(p => { try { return p && fs.existsSync(p); } catch { return false; } }) || list[0];
}
function pythonExe(){ return process.env.PYTHON || findExistingPath([path.join(process.env.LOCALAPPDATA || '', 'Python', 'bin', 'python.exe'), path.join(process.env.LOCALAPPDATA || '', 'Microsoft', 'WindowsApps', 'py.exe'), 'py']); }

function runBdsWebValuation(payload, timeoutMs = 720000, jobId = '') {
  return new Promise((resolve, reject) => {
    const bdsDir = findExistingPath([path.join(__dirname, 'BDS_Ver2_9router_test'), path.join(__dirname, '..', '..', 'BDS_Ver2_9router_test')]);
    const script = path.join(bdsDir, 'web_valuation_api.py');
    const py = spawn(pythonExe(), [script], {
      cwd: bdsDir,
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, BDS_JOB_ID: jobId, BDS_CHROME_PROFILE: path.join(bdsDir, 'logs', `chrome_profile_${jobId}`), BDS_GMAPS_PROFILE: path.join(bdsDir, 'logs', `gmaps_profile_${jobId}`) },
    });
    let out = '', err = '';
    const t = setTimeout(() => { try { py.kill(); } catch {} reject(new Error('BDS valuation timeout')); }, timeoutMs);
    py.stdout.on('data', d => out += d.toString('utf8'));
    py.stderr.on('data', d => err += d.toString('utf8'));
    py.on('error', e => { clearTimeout(t); reject(e); });
    py.on('close', code => {
      clearTimeout(t);
      if (code !== 0) return reject(new Error(`BDS valuation exited ${code}: ${err || out}`));
      try { resolve(cleanVietnameseObject(JSON.parse(out))); } catch (e) { reject(new Error(`BDS valuation bad JSON: ${e.message}; stderr=${err}; stdout=${out.slice(0,1000)}`)); }
    });
    py.stdin.end(JSON.stringify(payload || {}), 'utf8');
  });
}


const notebookJobs = new Map();
function safeId(){ return Date.now().toString(36)+Math.random().toString(36).slice(2,8); }
function readJsonBody(req, maxBytes = 25 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let body = ''; let size = 0;
    req.on('data', chunk => { size += chunk.length; if (size > maxBytes) { reject(new Error('payload_too_large')); try { req.destroy(); } catch {} } else body += chunk; });
    req.on('end', () => { try { resolve(JSON.parse(body || '{}')); } catch (e) { reject(e); } });
    req.on('error', reject);
  });
}
async function renderHtmlToPdf(html, outPath) {
  const { chromium } = require('playwright');
  const tmpHtml = outPath.replace(/\.pdf$/i, '.html');
  fs.writeFileSync(tmpHtml, html || '', 'utf8');
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const fileUrl = 'file:///' + tmpHtml.replace(/\\/g, '/');
    await page.goto(fileUrl, { waitUntil: 'load', timeout: 120000 });
    await page.pdf({ path: outPath, format: 'A4', printBackground: true, margin: { top: '10mm', right: '10mm', bottom: '10mm', left: '10mm' } });
  } finally { await browser.close(); }
}

function startNotebookAutomation(job, promptPath) {
  try {
    const outPath = job.pdfPath.replace(/\.pdf$/i, '.notebooklm.json');
    job.automationOutPath = outPath;
    job.status = 'running';
    job.stage = 'notebooklm_upload';
    job.message = 'Đã tạo PDF, đang mở NotebookLM bằng browser automation...';
    const script = path.join(__dirname, 'notebooklm_automation.js');
    const child = spawn(process.execPath, [script, job.pdfPath, promptPath || path.join(__dirname, 'LH_RD_NotebookLM_MasterPrompt.md'), outPath], { cwd: __dirname, windowsHide: false, stdio: 'ignore', detached: true });
    child.unref();
  } catch (e) {
    job.status = 'ready_pdf';
    job.stage = 'manual_notebooklm';
    job.message = 'Đã tạo PDF nhưng không khởi động được NotebookLM automation: ' + String(e && e.message || e);
  }
}
function syncNotebookJobFromAutomation(job) {
  if (!job?.automationOutPath || !fs.existsSync(job.automationOutPath)) return;
  try {
    const got = JSON.parse(fs.readFileSync(job.automationOutPath, 'utf8'));
    job.stage = got.stage || job.stage;
    job.message = got.message || job.message;
    job.notebookUrl = got.notebookUrl || job.notebookUrl;
    if (got.reportText) job.reportText = got.reportText;
    if (got.status === 'done') job.status = 'done';
    else if (got.status === 'needs_login') job.status = 'needs_login';
    else if (got.status === 'timeout') job.status = 'timeout';
    else if (got.status === 'error') { job.status = 'error'; job.error = got.message || got.error || 'automation_error'; }
    else if (job.status !== 'done') job.status = 'running';
  } catch (_) {}
}

async function startNotebookPdfJob(payload) {
  const id = safeId();
  const dir = path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', 'notebooklm');
  fs.mkdirSync(dir, { recursive: true });
  const pdfPath = path.join(dir, `lh_rd_notebooklm_${id}.pdf`);
  const job = { id, status: 'running', stage: 'render_pdf', message: 'Đang tạo PDF giữ nguyên map/đồ thị...', pdfPath, notebookUrl: 'https://notebooklm.google.com/', reportText: '', error: null };
  notebookJobs.set(id, job);
  renderHtmlToPdf(String(payload.html || ''), pdfPath).then(() => {
    if (payload.autoNotebookLM !== false) startNotebookAutomation(job, payload.promptPath);
    else { job.status = 'ready_pdf'; job.stage = 'manual_notebooklm'; job.message = 'Đã tạo PDF. Anh có thể tải PDF để upload NotebookLM.'; }
  }).catch(e => { job.status = 'error'; job.stage = 'error'; job.error = String(e && e.message || e); job.message = job.error; });
  return id;
}

const bdsJobs = new Map();
function readBdsJobProgress(jobId) {
  try {
    const p = path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', `bds_job_${jobId}.json`);
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (_) {}
  return null;
}
function startBdsJob(payload) {
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2,8);
  const job = { id, status:'running', createdAt:Date.now(), result:null, error:null, stage:'queued', message:'Đã nhận job R&D, chuẩn bị chạy BDS_bot stack...', warnings:[] };
  bdsJobs.set(id, job);
  runBdsWebValuation(payload, 720000, id).then(result => {
    if (result?.map_png_base64) {
      try {
        const mp = path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', `bds_map_${id}.png`);
        fs.writeFileSync(mp, Buffer.from(result.map_png_base64, 'base64'));
        result.map_url = `/bds/valuation/map/${id}`;
        delete result.map_png_base64;
      } catch (e) { result.warnings = [...(result.warnings || []), 'Không lưu được map image: ' + String(e.message || e)]; }
    }
    job.status = result?.ok ? 'done' : 'error'; job.result = result; job.error = result?.ok ? null : (result?.error || 'valuation failed'); job.stage = job.status; job.message = job.status === 'done' ? 'Hoàn tất R&D giống BDS_bot.' : job.error;
  }).catch(e => { job.status='error'; job.error=String(e && e.message || e); job.result={ok:false,error:job.error}; job.stage='error'; job.message=job.error; });
  return id;
}

function legalRootDir(){
  const candidates = [
    path.join(__dirname, 'docs', 'legal_research'),
    path.join(__dirname, '..', 'docs', 'legal_research'),
    path.join(__dirname, 'LH BDS', 'docs', 'legal_research'),
    path.join(process.cwd(), 'LH BDS', 'docs', 'legal_research')
  ];
  return candidates.find(p=>fs.existsSync(p)) || candidates[0];
}
function walkLegalFiles(dir, out=[]){
  if(!fs.existsSync(dir)) return out;
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir, ent.name);
    if(ent.isDirectory()) walkLegalFiles(p,out); else if(/\.(md|json)$/i.test(ent.name)) out.push(p);
  }
  return out;
}
function loadLegalExclusions(root){
  const p=path.join(root,'structured_streams','duplicate_exclusions.json');
  if(!fs.existsSync(p)) return new Set();
  try{ const j=JSON.parse(fs.readFileSync(p,'utf8')); return new Set((j.exclude||[]).map(e=>e.path)); }
  catch(_){ return new Set(); }
}
function scoreLegalDoc(q, text, rel){
  const terms=String(q||'').toLowerCase().match(/[a-z0-9à-ỹđ]+/g)||[];
  const hay=(rel+'\n'+text.slice(0,5000)).toLowerCase();
  let score=0;
  for(const t of terms){ if(t.length<2) continue; if(hay.includes(t)) score += rel.toLowerCase().includes(t)?3:1; }
  return score;
}

function routeBoostLegalDoc(q, rel, text){
  const qq=String(q||'').toLowerCase();
  const rr=String(rel||'').toLowerCase();
  let b=0;
  const isFuture=/hình thành trong tương lai|hinh thanh trong tuong lai|mở bán|mo ban|đưa vào kinh doanh|dua vao kinh doanh/.test(qq);
  const isKdbds=/kinh doanh bất động sản|kinh doanh bds|bất động sản|bds|mở bán|nhà ở hình thành/.test(qq);
  const isLand=/đất đai|giao đất|cho thuê đất|chuyển mục đích|giấy chứng nhận|tiền sử dụng đất|tiền thuê đất|giá đất/.test(qq);
  const isInvest=/đầu tư|chủ trương đầu tư|chấp thuận|lựa chọn nhà đầu tư|đấu thầu|dự án có sử dụng đất/.test(qq);
  if(isKdbds && /luat_kdbds_2023_29_2023_qh15_full\.md|nd_96_2024_nd_cp_full\.md|luat_kd_bds_fast_index\.md/.test(rr)) b+=120;
  if(isFuture && /luat_kdbds_2023_29_2023_qh15_full\.md|nd_96_2024_nd_cp_full\.md|future_property_sale_articles|conditions_for_sale_future_property/.test(rr)) b+=160;
  if(isLand && /luat_dat_dai_2024_31_2024_qh15_full\.md|nd_101_2024_nd_cp_full\.md|nd_102_2024_nd_cp_full\.md|nd_103_2024_nd_cp_full\.md|nd_71_2024_nd_cp_full\.md|nd_88_2024_nd_cp_full\.md|luat_dat_dai_fast_index/.test(rr)) b+=140;
  if(isInvest && /luat_dau_tu_2020_61_2020_qh14_full\.md|luat_dau_thau_2023_22_2023_qh15_full\.md|nd_23_2024_nd_cp_full\.md|luat_dau_tu_fast_index/.test(rr)) b+=140;
  return b;
}


let ADVISOR_INDEX_CACHE=null;
function foldLegalText(s){
  return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d');
}
function advisorTokens(s){
  const words=(foldLegalText(s).match(/[a-z0-9]+/g)||[]).filter(w=>w.length>1 || /^\d+$/.test(w));
  const stop=new Set('va la cua cac co duoc trong theo voi den tu ve nay do khi deu mot nhung nguoi viec quy dinh tai phai cho khong neu thi sau truoc hoac'.split(' '));
  const toks=words.filter(w=>!stop.has(w));
  for(let i=0;i<words.length-1;i++) toks.push(words[i]+'_'+words[i+1]);
  return toks;
}
function legalAdvisorIndexPath(){
  const candidates=[
    path.join(__dirname,'..','Luat BDS','legal-ai-advisor','data','index.json'),
    path.join(__dirname,'Luat BDS','legal-ai-advisor','data','index.json'),
    path.join(process.cwd(),'Luat BDS','legal-ai-advisor','data','index.json'),
    path.join(process.cwd(),'LH BDS','Luat BDS','legal-ai-advisor','data','index.json')
  ];
  return candidates.find(p=>fs.existsSync(p));
}
function loadAdvisorIndex(){
  if(ADVISOR_INDEX_CACHE) return ADVISOR_INDEX_CACHE;
  const p=legalAdvisorIndexPath();
  if(!p) return null;
  try{ const j=JSON.parse(fs.readFileSync(p,'utf8')); ADVISOR_INDEX_CACHE=j; return j; }
  catch(_){ return null; }
}
function scoreAdvisorChunk(q, c){
  const qTokens=new Set(advisorTokens(q));
  const field=(((c.dieu_title||'')+' ')*4)+' '+(c.doc_no||'')+' '+(c.doc_title||'')+' '+(c.text||'');
  const hayTokens=new Set(advisorTokens(field));
  let s=0;
  for(const t of qTokens){ if(hayTokens.has(t)) s += t.includes('_') ? 4 : 1; }
  const qq=foldLegalText(q); const doc=foldLegalText((c.doc_no||'')+' '+(c.doc_title||'')+' '+(c.source_file||''));
  if(/hinh thanh trong tuong lai|mo ban|dua vao kinh doanh/.test(qq) && /(29\/2023|96\/2024|kinh doanh bat dong san)/.test(doc)) s+=35;
  if(/chuyen nhuong du an|chuyen giao du an/.test(qq) && /(29\/2023|96\/2024|kinh doanh bat dong san)/.test(doc)) s+=35;
  if(/dat dai|giao dat|cho thue dat|giay chung nhan|tien su dung dat|gia dat/.test(qq) && /(31\/2024|101\/2024|102\/2024|103\/2024|71\/2024|88\/2024)/.test(doc)) s+=30;
  if(/dau tu|chu truong dau tu|lua chon nha dau tu|dau thau/.test(qq) && /(61\/2020|22\/2023|23\/2024|dau tu|dau thau)/.test(doc)) s+=30;
  if(String(c.doc_no||'').toLowerCase().includes('qh')) s*=1.08;
  return s;
}
function searchAdvisorChunks(question, limit=8){
  const idx=loadAdvisorIndex();
  if(!idx || !Array.isArray(idx.chunks)) return [];
  const rows=[];
  for(const c of idx.chunks){
    const score=scoreAdvisorChunk(question,c);
    if(score>0) rows.push({score, c});
  }
  rows.sort((a,b)=>b.score-a.score);
  return rows.slice(0,limit).map((r,i)=>{
    const c=r.c;
    const title=[c.doc_type,c.doc_no,c.doc_title].filter(Boolean).join(' - ');
    const article=c.dieu ? ('Điều '+c.dieu+(c.dieu_title?'. '+c.dieu_title:'')) : '';
    const source='legal-ai-advisor:'+[c.doc_no,c.source_file,'dieu_'+(c.dieu||'')].filter(Boolean).join('|');
    const excerpt=[title, c.issued_date?('Ngày ban hành: '+c.issued_date):'', c.chuong?('Chương '+c.chuong+(c.chuong_title?' - '+c.chuong_title:'')):'', article, c.text].filter(Boolean).join('\n');
    return {path:source, score:Math.round(r.score+220), excerpt, advisor:true, meta:c};
  });
}

function searchLegalDocs(question, limit=8){
  const root=legalRootDir();
  const exclusions=loadLegalExclusions(root);
  const files=walkLegalFiles(root);
  const rows=[];
  for(const f of files){
    try{
      const text=fs.readFileSync(f,'utf8');
      const rel=path.relative(root,f).replace(/\\/g,'/');
      if(exclusions.has(rel)) continue;
      const score=scoreLegalDoc(question,text,rel) + routeBoostLegalDoc(question, rel, text);
      const boosted = rel.includes('official_texts_md_full/') ? score + 60 : (rel.includes('structured_streams/') ? score + 45 : (rel.includes('official_texts_md/') ? score + 20 : score));
      if(score>0) rows.push({path:rel, score:boosted, text});
    }catch(_){ }
  }
  const advisorRows=searchAdvisorChunks(question, Math.max(limit,8));
  rows.sort((a,b)=>b.score-a.score);
  const fileRows=rows.slice(0,Math.max(0,limit-advisorRows.length)).map(r=>({path:r.path, score:r.score, excerpt:r.text.slice(0,2600)}));
  const merged=[...advisorRows, ...fileRows];
  merged.sort((a,b)=>b.score-a.score);
  return merged.slice(0,limit);
}
async function call9RouterChat(messages, temperature=0.1){
  const key=readBdsKey();
  const headers={'content-type':'application/json'};
  if(key) headers.authorization='Bearer '+key;
  const ctrl=new AbortController();
  const timer=setTimeout(()=>ctrl.abort(), Number(process.env.LEGAL_AI_TIMEOUT_MS||120000));
  let upstream;
  try{ upstream=await fetch(LOCAL_9ROUTER_BASE.replace(/\/$/,'') + '/chat/completions', {method:'POST', headers, signal:ctrl.signal, body:JSON.stringify({model:FALLBACK_MODEL, temperature, max_tokens:2200, messages})}); }
  finally{ clearTimeout(timer); }
  const text=await upstream.text();
  let json=null; try{json=JSON.parse(text)}catch(_){ }
  if(!upstream.ok) throw new Error('upstream_'+upstream.status+': '+text.slice(0,500));
  return json?.choices?.[0]?.message?.content || text;
}
async function legalAsk(payload){
  const question=String(payload?.question||payload?.q||'').trim();
  if(!question) throw new Error('question_required');
  const hits=searchLegalDocs(question, Math.min(Number(payload.limit)||8, 8));
  const context=hits.map((h,i)=>'['+(i+1)+'] '+h.path+'\n'+String(h.excerpt||'').slice(0,2200)).join('\n\n---\n\n');
  const sys=`Bạn là LH Legal & Investment AI, vai trò như luật sư/pháp chế senior chuyên dự án bất động sản Việt Nam. Nhiệm vụ: trả lời thực chiến, dễ hiểu, có căn cứ pháp lý, không lan man sang FS/cổ phiếu/tài chính nếu người hỏi không hỏi.

PHONG CÁCH TRẢ LỜI CHÍNH (answer):
- Viết giống một bản tư vấn pháp lý ngắn cho người làm dự án, không viết kiểu máy móc/checklist.
- Phần đầu phải là TÓM TẮT NGẮN: 3-6 bullet hoặc 1 đoạn 4-7 câu; câu chữ cô đọng, không dài dòng, nhưng giữ đủ ý chính, số liệu, điều kiện, mốc thời gian, cơ quan và kết quả đầu ra nếu context có.
- AI phải tự bôi đậm bằng markdown **...** các keyword tóm tắt, điều/khoản/điểm, tên luật/nghị định/thông tư, số liệu và mốc thời gian quan trọng. Ví dụ: **Điều 40 Luật KDBĐS 2023**, **khoản 2**, **15 ngày**, **UBND cấp tỉnh**.
- Sau tóm tắt, chia mục rõ nhưng gọn: I. Kết luận/định hướng; II. Điều kiện/thẩm quyền; III. Quy trình/hồ sơ; IV. Rủi ro/lưu ý.
- Nếu câu hỏi là thủ tục/quy trình, bắt buộc nêu từng bước, thời hạn xử lý, cơ quan tiếp nhận/quyết định, kết quả đầu ra; không được bỏ số ngày/mốc thời gian nếu context có.
- Mỗi ý quan trọng phải kèm căn cứ ngay trong câu: Điều mấy, khoản/điểm mấy, văn bản nào, ngày/năm nào nếu context có.
- Ngắn gọn nhưng đủ ý: ưu tiên 450-850 chữ nếu vấn đề phức tạp; câu hỏi đơn giản thì 250-450 chữ. Không nhồi quá nhiều bullet rời rạc.
- Không mở đầu bằng "theo context"; không nói như robot; không chỉ liệt kê tên điều luật.

CĂN CỨ PHÁP LÝ:
- Ưu tiên toàn văn trong official_texts_md_full và chunk Điều/Khoản từ legal-ai-advisor/structured_streams.
- Không dùng checklist/training note làm căn cứ chính nếu đã có toàn văn.
- Không bịa điều/khoản/ngày. Nếu context chưa có thì ghi rõ "chưa thấy trong bộ toàn văn đã nạp".
- citations phải chứa căn cứ chi tiết để panel phải đối chiếu được: title, article, clause, year, date, evidence, fullContent, sourcePath, needVerify.
- needVerify=false khi sourcePath là official_texts_md_full hoặc legal-ai-advisor chunk có Điều/Khoản rõ; needVerify=true nếu nguồn phụ/không rõ điều khoản.

ĐỊNH DẠNG JSON BẮT BUỘC:
Trả JSON hợp lệ, không thêm markdown ngoài JSON, với keys:
{
  "summary": "tóm tắt cực ngắn 3-6 ý, có **keyword**, **điều/khoản**, số liệu và mốc thời gian nếu có",
  "answer": "phần tư vấn chính cô đọng, có tóm tắt đầu bài, bôi đậm **keyword/Điều/Khoản/số liệu/mốc thời gian**, chia mục I/II/III giống luật sư/AI mẫu",
  "citations": [{"title":"","article":"","clause":"","year":"","date":"","evidence":"","fullContent":"","sourcePath":"","needVerify":false}],
  "risks": ["..."],
  "nextSteps": ["..."]
}`;
  const user='Câu hỏi: '+question+'\n\nContext pháp lý nội bộ:\n'+context;
  let parsed;
  try{ parsed=JSON.parse(await call9RouterChat([{role:'system',content:sys},{role:'user',content:user}],0.05)); }
  catch(e){
    parsed={
      summary:'AI tổng hợp bị chậm/timeout; trả bản tóm lược có căn cứ từ các điều/khoản liên quan nhất.',
      answer:hits.slice(0,6).map((h,i)=>{
        const lines=String(h.excerpt||'').split('\n').filter(Boolean);
        const head=lines.slice(0,4).join(' — ');
        const body=lines.slice(4).join(' ').slice(0,420);
        return '- ['+(i+1)+'] '+head+(body?' — Nội dung chính: '+body:'');
      }).join('\n'),
      citations:hits.map(h=>({title:h.path, article:'', clause:'', year:'', evidence:String(h.excerpt||'').slice(0,500), fullContent:String(h.excerpt||'').slice(0,1800), sourcePath:h.path, needVerify:!String(h.path||'').includes('legal-ai-advisor:')})),
      risks:['Bản này là chế độ dự phòng khi AI tổng hợp quá lâu; nên hỏi hẹp hơn nếu cần phân tích sâu theo hồ sơ cụ thể.'],
      nextSteps:['Hỏi tiếp theo từng nhánh: thẩm quyền, hồ sơ, điều kiện bên nhận chuyển nhượng, nghĩa vụ tài chính, hoặc rủi ro pháp lý.']
    };
  }
  if(Array.isArray(parsed.answer)) parsed.answer = parsed.answer.map(x=>'- '+String(x)).join('\n');
  else parsed.answer = String(parsed.answer || '');
  if(!Array.isArray(parsed.citations)) parsed.citations=[];
  if(!parsed.citations.length) parsed.citations=hits.map(h=>({title:h.path, article:'', clause:'', year:'', evidence:h.excerpt.slice(0,500), sourcePath:h.path, needVerify:true}));
  parsed.sources = hits.map(h=>({path:h.path, score:h.score}));
  parsed.ok=true;
  return cleanVietnameseObject(parsed);
}

const server = http.createServer(async (req, res) => {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }

  if (req.method === 'POST' && req.url === '/legal/ask') {
    try {
      const payload = await readJsonBody(req, 1024 * 1024);
      const result = await legalAsk(payload);
      res.writeHead(200, {'content-type':'application/json'});
      return res.end(JSON.stringify(result));
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'});
      return res.end(JSON.stringify({ok:false, error:String(e && e.message || e)}));
    }
  }
  if (req.method === 'GET' && req.url === '/health') {
    const bdsDir = findExistingPath([path.join(__dirname, 'BDS_Ver2_9router_test'), path.join(__dirname, '..', '..', 'BDS_Ver2_9router_test')]);
    const diag = {
      ok: true,
      base: LOCAL_9ROUTER_BASE,
      model: FALLBACK_MODEL,
      hasKey: !!readBdsKey(),
      renderCommit: process.env.RENDER_GIT_COMMIT || process.env.RENDER_COMMIT || null,
      python: process.env.PYTHON || null,
      cwd: process.cwd(),
      backendDir: __dirname,
      bdsDir,
      hasBdsAiClient: !!(bdsDir && fs.existsSync(path.join(bdsDir, 'ai_client.py'))),
      hasBdsWebApi: !!(bdsDir && fs.existsSync(path.join(bdsDir, 'web_valuation_api.py')))
    };
    res.writeHead(200, {'content-type':'application/json; charset=utf-8'});
    return res.end(JSON.stringify(diag));
  }
  if (req.method === 'GET' && req.url.startsWith('/nvtc/k1-source')) {
    try {
      const u = new URL(req.url, 'http://localhost');
      const data = k1SourcePage(u.searchParams.get('page'));
      if (!data) { res.writeHead(400, {'content-type':'application/json'}); return res.end(JSON.stringify({ok:false,error:'page_required'})); }
      res.writeHead(200, {'content-type':'application/json'});
      return res.end(JSON.stringify({ok:true, ...data}));
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'});
      return res.end(JSON.stringify({ok:false,error:String(e && e.message || e)}));
    }
  }
  if (req.method === 'POST' && req.url === '/notebooklm/report/start') {
    try {
      const payload = await readJsonBody(req);
      const id = await startNotebookPdfJob(payload);
      res.writeHead(200, {'content-type':'application/json'});
      return res.end(JSON.stringify({ ok:true, jobId:id, statusUrl:`/notebooklm/report/status/${id}`, pdfUrl:`/notebooklm/report/pdf/${id}` }));
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'});
      return res.end(JSON.stringify({ ok:false, error:String(e && e.message || e) }));
    }
  }
  if (req.method === 'GET' && req.url.startsWith('/notebooklm/report/status/')) {
    const id = decodeURIComponent(req.url.split('/').pop() || '');
    const job = notebookJobs.get(id);
    if (job) syncNotebookJobFromAutomation(job);
    if (!job) { res.writeHead(404, {'content-type':'application/json'}); return res.end(JSON.stringify({ok:false,error:'job_not_found'})); }
    res.writeHead(200, {'content-type':'application/json'});
    return res.end(JSON.stringify(cleanVietnameseObject({ ok:true, id, status:job.status, stage:job.stage, message:job.message, error:job.error, pdfUrl:`/notebooklm/report/pdf/${id}`, notebookUrl:job.notebookUrl, reportText:job.reportText || '' })));
  }
  if (req.method === 'GET' && req.url.startsWith('/notebooklm/report/pdf/')) {
    const id = decodeURIComponent(req.url.split('/').pop() || '');
    const job = notebookJobs.get(id);
    if (!job || !job.pdfPath || !fs.existsSync(job.pdfPath)) { res.writeHead(404, {'content-type':'application/json'}); return res.end(JSON.stringify({ok:false,error:'pdf_not_found'})); }
    res.writeHead(200, {'content-type':'application/pdf', 'content-disposition':'attachment; filename="LH-RD-NotebookLM-report.pdf"'});
    return fs.createReadStream(job.pdfPath).pipe(res);
  }
  if (req.method === 'POST' && req.url === '/nvtc/k1-search') {
    let body = '';
    req.on('data', chunk => body += chunk);
    return req.on('end', async () => {
      try {
        if (!lookupK1LandFee) throw new Error('BDS K1 modules are not available');
        const payload = JSON.parse(body || '{}');
        let ward = cleanVietnameseText(String(payload.ward || payload.phuong || '').trim());
        let road = cleanVietnameseText(String(payload.road || payload.duong || '').trim());
        let district = cleanVietnameseText(String(payload.district || '').trim());
        let city = cleanVietnameseText(String(payload.city || 'TP.HCM').trim());
        if (!ward || !road) throw new Error('ward_and_road_required');
        const hoaHungCtx = /Hòa Hưng/i.test([ward, road].join(' '));
        if (hoaHungCtx) {
          ward = 'Phường Hòa Hưng';
          city = 'Thành phố Hồ Chí Minh';
          if (/Thủ Đức/i.test(district)) district = '';
        }
        const displayParts = [road, ward, district, city].filter(Boolean);
        const geo = cleanVietnameseObject({ ward, suburb: ward, road, district, city, display_name: displayParts.join(', ') });
        const k1 = await lookupK1LandFee({ lat: null, lon: null, geoLocation: geo, text: payload.text || '', landUse: payload.landUse || 'ODT', position: payload.position || 'VT1', planningMultiplier: 1 });
        if (k1 && k1.error) {
          res.writeHead(422, {'content-type':'application/json'});
          return res.end(JSON.stringify(cleanVietnameseObject({ ok:false, location: geo, error: k1.error, k1 })));
        }
        res.writeHead(200, {'content-type':'application/json'});
        return res.end(JSON.stringify(cleanVietnameseObject({ ok:true, location: geo, k1 })));
      } catch (e) {
        res.writeHead(500, {'content-type':'application/json'});
        return res.end(JSON.stringify({ok:false, error:String(e && e.message || e)}));
      }
    });
  }

  if (req.method === 'POST' && (req.url === '/nvtc/k1-lookup' || req.url === '/planning/lookup')) {
    let body = '';
    req.on('data', chunk => body += chunk);
    return req.on('end', async () => {
      try {
        if (!lookupHcmPlanning || !summarize) throw new Error('BDS planning modules are not available');
        const payload = JSON.parse(body || '{}');
        const lat = Number(payload.lat), lon = Number(payload.lon);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new Error('lat/lon required');
        const raw = await lookupHcmPlanning(lat, lon);
        const sum = summarize(raw);
        const geo = sum.location || {};
        const geoTextForHoaHung = [geo.ward, geo.suburb, geo.neighbourhood, geo.road, geo.display_name].filter(Boolean).join(' ');
        if (/Hòa Hưng/i.test(geoTextForHoaHung)) {
          geo.ward = 'Phường Hòa Hưng';
          geo.suburb = 'Phường Hòa Hưng';
          geo.district = /Quận\s*10|Quan\s*10/i.test(String(geo.display_name || '')) ? 'Quận 10' : (geo.district && !/Thủ Đức/i.test(String(geo.district)) ? geo.district : 'Quận 10');
          geo.city = 'Thành phố Hồ Chí Minh';
          geo.display_name = cleanVietnameseText(String(geo.display_name || '').replace(/Thành phố Thủ Đức,\s*/gi, '').replace(/Thành phố Thủ Đức/gi, 'Thành phố Hồ Chí Minh'));
        }
        if (req.url === '/planning/lookup') {
          let qhviet = null;
          let guland = null;
          if (payload.includeQhViet !== false && readQhVietPopupText && parseQhVietPopupText) {
            try {
              const got = await Promise.race([
                readQhVietPopupText(lat, lon, geo),
                new Promise((_, rej) => setTimeout(() => rej(new Error('QH Việt timeout')), 70000)),
              ]);
              const parsed = parseQhVietPopupText(got?.text || '');
              const hasParsed = !!(parsed?.parcel?.map_sheet || parsed?.parcel?.land_code || parsed?.area_name || parsed?.old_area_name || (parsed?.planning || []).length);
              qhviet = { ok: !got?.degraded && hasParsed, text: got?.text || '', parsed, degraded: !hasParsed };
            } catch (e) {
              qhviet = { ok:false, error:String(e && e.message || e) };
            }
          }
          if (payload.includeGuland !== false && readGulandPopupText && parseGulandPopupText) {
            try {
              const got = await Promise.race([
                readGulandPopupText(lat, lon),
                new Promise((_, rej) => setTimeout(() => rej(new Error('Guland timeout')), 45000)),
              ]);
              const parsed = parseGulandPopupText(got?.text || '');
              const hasParsed = !!(parsed?.parcel?.map_sheet || parsed?.parcel?.land_code || (parsed?.planning || []).length);
              guland = { ok: !got?.degraded && hasParsed, text: got?.text || '', parsed, degraded: !hasParsed };
            } catch (e) {
              guland = { ok:false, error:String(e && e.message || e) };
            }
          }
          res.writeHead(200, {'content-type':'application/json'});
          return res.end(JSON.stringify(cleanVietnameseObject({ ok:true, location: geo, planning: sum, raw, qhviet, guland })));
        }
        if (!lookupK1LandFee) throw new Error('BDS K1 modules are not available');
        const landUse = payload.landUse || 'ODT';
        const position = payload.position || 'VT1';
        const k1 = await lookupK1LandFee({ lat, lon, geoLocation: geo, text: payload.text || '', landUse, position, planningMultiplier: 1 });
        if (k1 && k1.error) {
          res.writeHead(422, {'content-type':'application/json'});
          return res.end(JSON.stringify({ ok:false, location: geo, error: k1.error, k1 }));
        }
        res.writeHead(200, {'content-type':'application/json'});
        res.end(JSON.stringify(cleanVietnameseObject({ ok:true, location: geo, k1 }))); 
      } catch (e) {
        res.writeHead(500, {'content-type':'application/json'});
        res.end(JSON.stringify({ ok:false, error: String(e && e.message || e) }));
      }
    });
  }
  if (req.method === 'POST' && req.url === '/bds/valuation/start') {
    let body = '';
    req.on('data', chunk => body += chunk);
    return req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        if (!payload.location_context && lookupHcmPlanning && summarize && Number.isFinite(Number(payload.lat)) && Number.isFinite(Number(payload.lng ?? payload.lon))) {
          try {
            const rawLoc = await lookupHcmPlanning(Number(payload.lat), Number(payload.lng ?? payload.lon));
            payload.location_context = summarize(rawLoc).location || null;
          } catch (_) {}
        }
        const jobId = startBdsJob(payload);
        res.writeHead(200, {'content-type':'application/json'});
        return res.end(JSON.stringify({ok:true, jobId}));
      } catch (e) {
        res.writeHead(500, {'content-type':'application/json'});
        return res.end(JSON.stringify({ok:false, error:String(e && e.message || e)}));
      }
    });
  }
  if (req.method === 'GET' && req.url.startsWith('/bds/valuation/map/')) {
    const jobId = decodeURIComponent(req.url.split('/').pop() || '');
    const mp = path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', `bds_map_${jobId}.png`);
    if (!fs.existsSync(mp)) { res.writeHead(404, {'content-type':'application/json'}); return res.end(JSON.stringify({ok:false,error:'map_not_found'})); }
    res.writeHead(200, {'content-type':'image/png', 'cache-control':'no-store'});
    return fs.createReadStream(mp).pipe(res);
  }
  if (req.method === 'GET' && req.url.startsWith('/bds/valuation/status/')) {
    const jobId = decodeURIComponent(req.url.split('/').pop() || '');
    const job = bdsJobs.get(jobId);
    if (!job) { res.writeHead(404, {'content-type':'application/json'}); return res.end(JSON.stringify({ok:false,error:'job_not_found'})); }
    const prog = readBdsJobProgress(jobId) || {};
    res.writeHead(200, {'content-type':'application/json'});
    return res.end(JSON.stringify(cleanVietnameseObject({ok:true, jobId, status:job.status, createdAt:job.createdAt, stage:prog.stage || job.stage, message:prog.message || job.message, warnings:prog.warnings || job.warnings || [], error:job.error, result:job.status === 'done' || job.status === 'error' ? job.result : null})));
  }
  if (req.method === 'POST' && req.url === '/bds/valuation') {
    let body = '';
    req.on('data', chunk => body += chunk);
    return req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        const result = await runBdsWebValuation(payload);
        res.writeHead(result.ok ? 200 : 500, {'content-type':'application/json'});
        return res.end(JSON.stringify(cleanVietnameseObject(result)));
      } catch (e) {
        res.writeHead(500, {'content-type':'application/json'});
        return res.end(JSON.stringify({ok:false, error:String(e && e.message || e)}));
      }
    });
  }
  if (req.method !== 'POST' || req.url !== '/v1/chat/completions') {
    res.writeHead(404, {'content-type':'application/json'});
    return res.end(JSON.stringify({error:'not_found'}));
  }
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const payload = JSON.parse(body || '{}');
      payload.model = payload.model || FALLBACK_MODEL;
      if (!payload.model || /^claude/i.test(payload.model)) payload.model = FALLBACK_MODEL;
      const key = readBdsKey();
      const headers = {'content-type':'application/json'};
      if (key) headers.authorization = 'Bearer ' + key;
      const upstream = await fetch(LOCAL_9ROUTER_BASE.replace(/\/$/, '') + '/chat/completions', {
        method: 'POST', headers, body: JSON.stringify(payload)
      });
      const text = await upstream.text();
      res.writeHead(upstream.status, {'content-type': upstream.headers.get('content-type') || 'application/json'});
      res.end(text);
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'});
      res.end(JSON.stringify({error: String(e && e.message || e)}));
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`NVTC 9Router proxy listening on http://0.0.0.0:${PORT}`);
  console.log(`Forwarding to ${LOCAL_9ROUTER_BASE} with model ${FALLBACK_MODEL}`);
});


