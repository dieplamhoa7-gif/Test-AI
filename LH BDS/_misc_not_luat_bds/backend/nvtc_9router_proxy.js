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
try { ({ lookupHcmPlanning, summarize } = require('./bds_planning_checker')); } catch (_) {}
try { ({ lookupK1LandFee } = require('./k1_land_fee_lookup')); } catch (_) {}
try { ({ readQhVietPopupText, readGulandPopupText } = require('./planning_browser_popups')); } catch (_) {}
try { ({ parseQhVietPopupText } = require('./qhviet_popup_parser')); } catch (_) {}
try { ({ parseGulandPopupText } = require('./guland_popup_parser')); } catch (_) {}

function readBdsKey() {
  const envKey = process.env.BDS_9ROUTER_API_KEY || process.env.NINEROUTER_API_KEY || process.env.OPENAI_API_KEY;
  if (envKey) return envKey.trim();
  try {
    const txt = fs.readFileSync(PRIVATE_KEY_FILE, 'utf8');
    const m = txt.match(/^\s*BDS_9ROUTER_API_KEY\s*=\s*(.+?)\s*$/m) || txt.match(/^\s*NINEROUTER_API_KEY\s*=\s*(.+?)\s*$/m);
    return m ? m[1].trim().replace(/^['"]|['"]$/g, '') : '';
  } catch { return ''; }
}



function compactExternalText(text, source) {
  const t = String(text || '').replace(/^QH Việt browser:\s*/i, '').replace(/^Guland popup\/browser:\s*/i, '').replace(/\s+/g, ' ').trim();
  const parts = [];
  const add = (label, re) => { const m = t.match(re); if (m && m[1]) parts.push(`${label}: ${m[1].trim()}`); };
  if (source === 'qhviet') {
    add('Khu vực cũ', /Khu vực cũ\s+(.+?)\s+Khu vực mới/i);
    add('Khu vực mới', /Khu vực mới\s+(.+?)\s+(?:page:|Xem quy hoạch|Giao thông|Quyết định)/i);
    add('Quyết định', /Quyết định\s+(.+?)\s+Làm mờ nền/i);
  } else {
    add('Khu vực mới', /(Phường[^,]+,\s*(?:TP\.\s*)?Hồ Chí Minh \(Mới\)|Phường[^,]+,\s*Bắc Ninh \(Mới\))/i);
    add('Khu vực cũ', /\(Mới\)\s+(.+?)\s+Đăng bán/i);
    add('Tờ/thửa', /(Tờ\s*\d+\s+Thửa\s+[^,]+,\s*Diện tích\s*[\d.,]+m²)/i);
    add('Hiện trạng', /\b(ODT\s+[\d.,]+m²\s+Đất ở đô thị|Đất ở đô thị|Đất ở)\b/i);
    add('QH xây dựng', /Thông tin quy hoạch xây dựng\s+(.+?)\s+Thông tin mô tả thửa/i);
    add('Đường', /Độ rộng đường\s+([\d.,]+\s*m)/i);
    add('Cách đường chính', /Khoảng cách tới đường chính\s+([\d.,]+\s*m)/i);
    add('Hướng', /Hướng mặt tiền\s+([^\s]+(?:\s+[^\s]+)?)/i);
  }
  return parts.join(' • ');
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
    .replaceAll(moji(196,63), 'Đ').replaceAll(moji(196,8216), 'đ');
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

function runBdsWebValuation(payload, timeoutMs = 720000, jobId = '') {
  return new Promise((resolve, reject) => {
    const script = path.join(__dirname, 'BDS_Ver2_9router_test', 'web_valuation_api.py');
    const py = spawn(process.env.PYTHON || 'py', [script], {
      cwd: path.join(__dirname, 'BDS_Ver2_9router_test'),
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, BDS_JOB_ID: jobId, BDS_CHROME_PROFILE: path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', `chrome_profile_${jobId}`), BDS_GMAPS_PROFILE: path.join(__dirname, 'BDS_Ver2_9router_test', 'logs', `gmaps_profile_${jobId}`) },
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
  rows.sort((a,b)=>b.score-a.score);
  return rows.slice(0,limit).map(r=>({path:r.path, score:r.score, excerpt:r.text.slice(0,2400)}));
}
async function call9RouterChat(messages, temperature=0.1){
  const key=readBdsKey();
  const headers={'content-type':'application/json'};
  if(key) headers.authorization='Bearer '+key;
  const upstream=await fetch(LOCAL_9ROUTER_BASE.replace(/\/$/,'') + '/chat/completions', {method:'POST', headers, body:JSON.stringify({model:FALLBACK_MODEL, temperature, messages})});
  const text=await upstream.text();
  let json=null; try{json=JSON.parse(text)}catch(_){ }
  if(!upstream.ok) throw new Error('upstream_'+upstream.status+': '+text.slice(0,500));
  return json?.choices?.[0]?.message?.content || text;
}
async function legalAsk(payload){
  const question=String(payload?.question||payload?.q||'').trim();
  if(!question) throw new Error('question_required');
  const hits=searchLegalDocs(question, Number(payload.limit)||8);
  const context=hits.map((h,i)=>'['+(i+1)+'] '+h.path+'\n'+h.excerpt).join('\n\n---\n\n');
  const sys='Bạn là LH Legal & Investment AI cho pháp lý BĐS/đất đai/đầu tư tại Việt Nam, phong cách pháp chế senior/luật sư dự án BĐS. TRẢ LỜI THẲNG VÀO ĐÚNG CÂU HỎI, đào sâu bản chất pháp lý nhưng ngắn gọn, súc tích, không lan man sang FS/cổ phiếu/tài chính nếu người hỏi không hỏi. Luôn phân tích theo logic: vấn đề pháp lý cốt lõi -> điều kiện áp dụng -> căn cứ điều/khoản -> điểm nghẽn/rủi ro hồ sơ -> hướng xử lý thực tế. BẮT BUỘC chia nội dung thành 2 tầng dữ liệu JSON: (1) citations/detailedBasis = căn cứ chi tiết đầy đủ; (2) summary/answer = tóm tắt đủ ý. Với MỖI căn cứ trong citations phải có đủ tối đa các trường: title=tên luật/nghị định/thông tư/nghị quyết/VB hướng dẫn; article=Điều mấy; clause=Khoản/điểm mấy; year=năm văn bản; date=ngày ban hành hoặc ngày hiệu lực nếu context có; evidence=nội dung căn cứ ngắn; fullContent=nội dung căn cứ đầy đủ, chi tiết, sát câu hỏi; sourcePath=file nguồn; needVerify=false nếu sourcePath thuộc official_texts_md_full và evidence/fullContent lấy từ toàn văn; needVerify=true nếu dùng nguồn phụ hoặc chưa rõ điều/khoản. Phần citations/fullContent PHẢI đầy đủ, chi tiết, có nội dung điều/khoản liên quan; không chỉ ghi checklist. Phần summary/answer phải viết theo format bắt buộc: Điều mấy, khoản mấy, của nghị định/thông tư/VB hướng dẫn/nghị quyết nào, ngày mấy, nội dung là gì; sau đó mới nêu kết luận tóm tắt, ngắn hơn nhưng vẫn đủ thông tin, điều kiện/hồ sơ/rủi ro trực tiếp. Ưu tiên nguồn toàn văn official_texts_md_full và structured_streams; bỏ qua file trùng/phụ nếu đã có nguồn chính. Không bịa điều/khoản/ngày; nếu context không có thì ghi rõ chưa tìm thấy trong toàn văn đã nạp. Trả JSON hợp lệ với keys: summary, answer, citations[{title, article, clause, year, date, evidence, fullContent, sourcePath, needVerify}], risks[], nextSteps[]. Trong đó answer là phần chính hiển thị cho người dùng: phải là hướng dẫn thực chiến + dẫn chứng ngay trong câu từ điều/khoản nào của luật/nghị định/thông tư/VB hướng dẫn/nghị quyết; nhưng phải trình bày dạng gạch đầu dòng xuống hàng, mỗi bullet 1 ý, ngắn gọn, không đoạn văn dài. Giới hạn answer khoảng 8-12 bullet, mỗi bullet tối đa 2 câu. summary chỉ là tóm tắt ngắn nếu cần. Nội dung pháp lý dài/đầy đủ đưa vào citations.fullContent, không nhồi vào answer. QUAN TRỌNG: answer/summary phải viết như tư vấn pháp lý thực chiến, không chỉ trích luật khô. Phân tích phải sâu vào đúng vấn đề, chỉ giữ ý có giá trị ra quyết định; tránh giải thích giáo khoa, tránh lặp lại, tránh mở rộng ngoài phạm vi câu hỏi. Nếu câu hỏi là thủ tục/quy trình, bắt buộc tổ chức theo cấu trúc: (I) Kết luận ngắn; (II) Phân loại trường hợp/thẩm quyền nếu có; (III) Quy trình từng bước + thời hạn; (IV) Hồ sơ/tài liệu cần chuẩn bị; (V) Điều kiện/rủi ro pháp lý cần kiểm; (VI) Phân biệt khái niệm dễ nhầm nếu có. Mỗi ý quan trọng phải kèm ref ngắn trong cùng dòng: Điều mấy, khoản mấy, văn bản nào, ngày mấy. citations/fullContent vẫn là phần chi tiết đầy đủ để đối chiếu. Không thêm markdown ngoài JSON.';
  const user='Câu hỏi: '+question+'\n\nContext pháp lý nội bộ:\n'+context;
  let parsed;
  try{ parsed=JSON.parse(await call9RouterChat([{role:'system',content:sys},{role:'user',content:user}],0.05)); }
  catch(e){
    const fallback = await call9RouterChat([{role:'system',content:sys.replace('Trả JSON hợp lệ với keys: answer, citations[{title, article, clause, year, evidence, sourcePath, needVerify}], risks[], nextSteps[]. Không thêm markdown ngoài JSON.','')},{role:'user',content:user}],0.05);
    parsed={answer:fallback, citations:hits.map(h=>({title:h.path, article:'', clause:'', year:'', evidence:h.excerpt.slice(0,500), sourcePath:h.path, needVerify:true})), risks:['Cần kiểm tra văn bản gốc/cập nhật mới nhất trước khi dùng cho quyết định pháp lý.'], nextSteps:['Đối chiếu văn bản gốc và hồ sơ thực tế.']};
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
    res.writeHead(200, {'content-type':'application/json'});
    return res.end(JSON.stringify({ok:true, service:'bds_browser_planning_proxy', base:LOCAL_9ROUTER_BASE, model:FALLBACK_MODEL, hasKey:!!readBdsKey(), hasPlanning:!!(lookupHcmPlanning && summarize), hasQhViet:!!(readQhVietPopupText && parseQhVietPopupText), hasGuland:!!(readGulandPopupText && parseGulandPopupText)}));
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
        if (req.url === '/planning/lookup') {
          let qhviet = null;
          let guland = null;
          if (payload.includeQhViet !== false && readQhVietPopupText && parseQhVietPopupText) {
            try {
              const got = await Promise.race([
                readQhVietPopupText(lat, lon, geo),
                new Promise((_, rej) => setTimeout(() => rej(new Error('QH Việt timeout')), Number(process.env.QHVIET_TIMEOUT_MS || 45000))),
              ]);
              const parsed = parseQhVietPopupText(got?.text || '');
              const hasParsed = !!(parsed?.parcel?.map_sheet || parsed?.parcel?.land_code || parsed?.area_name || parsed?.old_area_name || (parsed?.planning || []).length);
              const rawText = String(got?.text || '');
              const summary = compactExternalText(rawText, 'qhviet');
              qhviet = { ok: !got?.degraded && hasParsed, summary, text: rawText || summary || JSON.stringify(parsed || {}), parsed, degraded: !hasParsed, status: hasParsed ? 'ok' : 'manual_check_required', note: hasParsed ? '' : 'Chưa bóc được popup tự động; mở QH Việt để kiểm tra thủ công.' };
            } catch (e) {
              qhviet = { ok:false, status:'manual_check_required', error:String(e && e.message || e), note:'Chưa bóc được popup tự động; mở QH Việt để kiểm tra thủ công.' };
            }
          }
          if (payload.includeGuland !== false && readGulandPopupText && parseGulandPopupText) {
            try {
              const got = await Promise.race([
                readGulandPopupText(lat, lon),
                new Promise((_, rej) => setTimeout(() => rej(new Error('Guland timeout')), Number(process.env.GULAND_TIMEOUT_MS || 45000))),
              ]);
              const parsed = parseGulandPopupText(got?.text || '');
              const hasParsed = !!(parsed?.parcel?.map_sheet || parsed?.parcel?.land_code || (parsed?.planning || []).length);
              const hasUsefulText = /Ký hiệu đất|Quy hoạch|Phường|Bắc Ninh|Bắc Giang|Dữ liệu chỉ có giá trị tham khảo/i.test(String(got?.text || ''));
              const rawText = String(got?.text || '');
              const summary = compactExternalText(rawText, 'guland');
              guland = { ok: !got?.degraded && (hasParsed || hasUsefulText), summary, text: rawText || summary || JSON.stringify(parsed || {}), parsed, degraded: !(hasParsed || hasUsefulText), status: (hasParsed || hasUsefulText) ? 'ok' : 'manual_check_required', note: (hasParsed || hasUsefulText) ? '' : 'Chưa bóc được popup tự động; mở Guland để kiểm tra thủ công.' };
            } catch (e) {
              guland = { ok:false, status:'manual_check_required', error:String(e && e.message || e), note:'Chưa bóc được popup tự động; mở Guland để kiểm tra thủ công.' };
            }
          }
          res.writeHead(200, {'content-type':'application/json; charset=utf-8'});
          return res.end(JSON.stringify({ ok:true, location: geo, planning: sum, raw, qhviet, guland }));
        }
        if (!lookupK1LandFee) throw new Error('BDS K1 modules are not available');
        const landUse = payload.landUse || 'ODT';
        const position = payload.position || 'VT1';
        const k1 = await lookupK1LandFee({ lat, lon, geoLocation: geo, text: payload.text || '', landUse, position, planningMultiplier: 1 });
        res.writeHead(200, {'content-type':'application/json'});
        res.end(JSON.stringify({ ok:true, location: geo, k1 }));
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
