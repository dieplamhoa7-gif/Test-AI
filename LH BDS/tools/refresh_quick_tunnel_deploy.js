// Free quick-tunnel self-heal for LH Real Estate.
// Starts cloudflared quick tunnel, extracts the generated URL, patches public HTML,
// verifies /health + key endpoints, then deploys Firebase hosting.
// Usage: node tools/refresh_quick_tunnel_deploy.js
const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const PUBLIC = path.join(ROOT, 'public');
const PORT = process.env.NVTC_PROXY_PORT || '8787';
const URL_RE = /https:\/\/[a-z0-9-]+\.trycloudflare\.com/ig;
const STATE = path.join(ROOT, 'tools', 'quick_tunnel_state.json');

function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
function run(cmd, args, opts={}){
  const useShell = process.platform === 'win32' && cmd === 'firebase';
  const exe = useShell ? 'firebase' : cmd;
  const r = spawnSync(exe, args, { cwd: ROOT, stdio: 'inherit', shell: useShell, ...opts });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`${exe} ${args.join(' ')} failed: ${r.status}`);
}
async function fetchText(url, opt){
  const r = await fetch(url, opt);
  const t = await r.text();
  return {status:r.status, ok:r.ok, text:t};
}
async function waitHealth(base, tries=30){
  for(let i=0;i<tries;i++){
    try{
      const r = await fetchText(base + '/health', {cache:'no-store'});
      if(r.ok && /"ok"\s*:\s*true/.test(r.text)) return true;
    }catch(_){ }
    await sleep(2000);
  }
  return false;
}
function patchPublic(newUrl){
  const files = fs.readdirSync(PUBLIC).filter(f=>f.endsWith('.html'));
  let changed = 0;
  for(const f of files){
    const p = path.join(PUBLIC, f);
    let s = fs.readFileSync(p, 'utf8');
    const next = s.replace(URL_RE, newUrl);
    if(next !== s){ fs.writeFileSync(p, next, 'utf8'); changed++; }
  }
  return changed;
}
function killOldCloudflared(){
  // Best effort. Keep simple/free: kill old quick tunnels to avoid multiple conflicting URLs.
  if(process.platform === 'win32'){
    spawnSync('taskkill', ['/IM','cloudflared.exe','/F'], {stdio:'ignore'});
  }
}
async function main(){
  console.log('[1/6] Checking local backend...');
  if(!(await waitHealth(`http://localhost:${PORT}`, 3))){
    console.log('Local backend not responding. Starting backend...');
    spawn(process.execPath, ['backend\\nvtc_9router_proxy.js'], {cwd: ROOT, detached:true, stdio:'ignore', windowsHide:true}).unref();
    if(!(await waitHealth(`http://localhost:${PORT}`, 20))) throw new Error('Local backend failed /health');
  }

  console.log('[2/6] Starting fresh quick tunnel...');
  killOldCloudflared();
  const child = spawn('cloudflared', ['tunnel','--url',`http://localhost:${PORT}`,'--no-autoupdate'], {cwd: ROOT, windowsHide:true});
  let url = '';
  child.stdout.on('data', d=>{ const s=String(d); process.stdout.write(s); const m=s.match(URL_RE); if(m) url=m[m.length-1]; });
  child.stderr.on('data', d=>{ const s=String(d); process.stdout.write(s); const m=s.match(URL_RE); if(m) url=m[m.length-1]; });
  child.on('exit', code=>console.log('cloudflared exited', code));

  for(let i=0;i<40 && !url;i++) await sleep(500);
  if(!url) throw new Error('Could not extract quick tunnel URL');
  console.log('Tunnel URL:', url);

  console.log('[3/6] Verifying tunnel health...');
  if(!(await waitHealth(url, 30))) throw new Error('Tunnel health check failed: ' + url);

  console.log('[4/6] Verifying NVTC + Quy hoạch endpoints...');
  const body = JSON.stringify({lat:10.773210604342207, lon:106.67984224544506, landUse:'ODT', position:'VT1'});
  for(const ep of ['/nvtc/k1-lookup','/planning/lookup']){
    const r = await fetchText(url + ep, {method:'POST', headers:{'content-type':'application/json'}, body});
    console.log(ep, r.status, r.text.slice(0,120));
    if(!r.ok) throw new Error(`${ep} failed`);
  }

  console.log('[5/6] Patching public HTML...');
  const changed = patchPublic(url);
  fs.writeFileSync(STATE, JSON.stringify({url, pid: child.pid, updatedAt:new Date().toISOString()}, null, 2), 'utf8');
  console.log('Patched files:', changed, 'State:', STATE);

  console.log('[6/6] Deploying Firebase hosting...');
  run('firebase', ['deploy','--project','hoa-investment','--config','firebase.lhrealestate.json','--only','hosting:lhrealestate']);
  console.log('DONE. Public backend URL:', url);
  console.log('NOTE: keep this process/window running to keep quick tunnel alive. Press Ctrl+C only when you want to stop it.');
  await new Promise(() => {});
}
main().catch(e=>{ console.error('FAILED:', e && e.stack || e); process.exit(1); });
