#!/usr/bin/env node
/**
 * lh_tunnel_publish.js  (REBUILT 2026-07-11)
 *
 * Muc dich: cham dut loi "R&D/Quy hoach khong chay sau khi tunnel restart".
 * Quick tunnel Cloudflare doi URL moi lan khoi dong lai. Script nay:
 *   1) Spawn cloudflared cho backend R&D (port 8787) va Quy hoach (neu co).
 *   2) Bat URL https://*.trycloudflare.com tu log cloudflared.
 *   3) Health-check URL do; khi OK -> ghi vao <DEPLOY_DIR>/api-config.json
 *      (rdApiBase / qhApiBase) roi chay `firebase deploy --only hosting`.
 *   4) cloudflared chet -> tu spawn lai -> lap lai buoc 2-3.
 * Nho vay frontend luon doc duoc URL tunnel hien tai qua /api-config.json,
 * KHONG can sua tay HTML moi lan restart.
 *
 * Cau hinh qua bien moi truong (deu co default):
 *   RD_PORT=8787              Cong backend R&D (rd_api_server.py)
 *   QH_PORT=                  Cong backend Quy hoach (bo trong neu chua co)
 *   DEPLOY_DIR=public_final_2026_07_11
 *   FIREBASE_SITE=lhrealestate
 *   CLOUDFLARED=cloudflared   Duong dan cloudflared neu khong nam trong PATH
 *   SKIP_DEPLOY=0             Dat =1 neu chi muon ghi api-config.json, tu deploy tay
 *
 * Chay:  node tools/lh_tunnel_publish.js
 */
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DEPLOY_DIR = process.env.DEPLOY_DIR || 'public_final_2026_07_11';
const CONFIG_PATH = path.join(ROOT, DEPLOY_DIR, 'api-config.json');
const FIREBASE_SITE = process.env.FIREBASE_SITE || 'lhrealestate';
const FIREBASE_PROJECT = process.env.FIREBASE_PROJECT || 'hoa-investment';
const FIREBASE_CONFIG = process.env.FIREBASE_CONFIG || 'firebase.json';
const CLOUDFLARED = process.env.CLOUDFLARED || 'cloudflared';
const LOCAL_HOST = process.env.LOCAL_HOST || '127.0.0.1';
const SKIP_DEPLOY = process.env.SKIP_DEPLOY === '1';
const WORKER = 'https://lh-realestate-api.lhrealestate.workers.dev';

const ROLES = [];
if (process.env.RD_PORT !== '') ROLES.push({ role: 'rd', port: process.env.RD_PORT || '8787', needFlag: 'hasBdsWebApi' });
if (process.env.QH_PORT) {
  const qhPort = process.env.QH_PORT;
  const rdPort = process.env.RD_PORT || '8787';
  // QH may be served by the same BDS/R&D backend, whose /health exposes hasBdsWebApi
  // but not hasPlanning. In that common setup, plain ok:true is enough.
  ROLES.push({ role: 'qh', port: qhPort, needFlag: qhPort === rdPort ? '' : 'hasPlanning' });
}

const state = {}; // role -> current published url
const procs = {}; // role -> active cloudflared child process
const healthFails = {}; // role -> consecutive public health failures
const HEALTH_INTERVAL_MS = Number(process.env.HEALTH_INTERVAL_MS || 30000);
const HEALTH_FAIL_LIMIT = Number(process.env.HEALTH_FAIL_LIMIT || 3);
const RESTART_DELAY_MS = Number(process.env.RESTART_DELAY_MS || 5000);

function log(...a) { console.log(new Date().toISOString(), ...a); }

function readConfig() {
  try { return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')); }
  catch { return { worker: WORKER }; }
}

function writeConfigAndDeploy() {
  const cfg = readConfig();
  cfg.worker = WORKER;
  cfg.updated = new Date().toISOString();
  for (const { role } of ROLES) cfg[role + 'ApiBase'] = state[role] || '';
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(cfg, null, 2));
  log('api-config.json updated:', JSON.stringify({ rd: cfg.rdApiBase, qh: cfg.qhApiBase }));
  const deployCmd = `firebase deploy --project ${FIREBASE_PROJECT} --config ${FIREBASE_CONFIG} --only hosting:${FIREBASE_SITE}`;
  if (SKIP_DEPLOY) { log('SKIP_DEPLOY=1 -> khong deploy; nho deploy tay:', deployCmd); return; }
  try {
    execSync(deployCmd, { cwd: ROOT, stdio: 'inherit' });
    log('firebase deploy xong.');
  } catch (e) { log('firebase deploy LOI:', e.message, '-> se thu lai lan cap nhat sau.'); }
}

async function healthOk(url, needFlag) {
  try {
    const r = await fetch(url + '/health', { cache: 'no-store' });
    if (!r.ok) return false;
    const j = await r.json();
    return !!(j && j.ok && (!needFlag || j[needFlag]));
  } catch { return false; }
}

function restartRole(cfg, reason) {
  const { role } = cfg;
  log(`${role}: restart requested: ${reason}`);
  state[role] = '';
  healthFails[role] = 0;
  try { if (procs[role] && !procs[role].killed) procs[role].kill(); } catch (_) {}
  setTimeout(() => runRole(cfg), RESTART_DELAY_MS);
}

function runRole(cfg) {
  const { role, port, needFlag } = cfg;
  if (procs[role] && !procs[role].killed) return;
  log(`starting cloudflared for ${role} -> http://${LOCAL_HOST}:${port}`);
  const cf = spawn(CLOUDFLARED, ['tunnel', '--url', `http://${LOCAL_HOST}:${port}`], { shell: process.platform === 'win32' });
  procs[role] = cf;
  healthFails[role] = 0;
  let settled = false;
  const onData = async (buf) => {
    const s = buf.toString();
    const m = s.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/i);
    if (m && !settled) {
      const url = m[0];
      settled = true;
      log(`${role}: tunnel URL = ${url}; dang health-check...`);
      for (let i = 0; i < 20; i++) {
        if (await healthOk(url, needFlag)) {
          state[role] = url;
          healthFails[role] = 0;
          log(`${role}: health OK -> publish`);
          writeConfigAndDeploy();
          return;
        }
        await new Promise(r => setTimeout(r, 3000));
      }
      log(`${role}: tunnel len nhung /health chua OK (backend port ${port} da chay chua?). Van publish URL de frontend thu.`);
      state[role] = url; writeConfigAndDeploy();
    }
  };
  cf.stdout.on('data', onData);
  cf.stderr.on('data', onData);
  cf.on('exit', (code) => {
    if (procs[role] === cf) procs[role] = null;
    log(`${role}: cloudflared thoat (code ${code}); restart sau ${Math.round(RESTART_DELAY_MS/1000)}s`);
    state[role] = '';
    setTimeout(() => runRole(cfg), RESTART_DELAY_MS);
  });
}

setInterval(async () => {
  for (const cfg of ROLES) {
    const { role, needFlag } = cfg;
    const url = state[role];
    if (!url) continue;
    if (await healthOk(url, needFlag)) { healthFails[role] = 0; continue; }
    healthFails[role] = (healthFails[role] || 0) + 1;
    log(`${role}: public /health failed ${healthFails[role]}/${HEALTH_FAIL_LIMIT}: ${url}`);
    if (healthFails[role] >= HEALTH_FAIL_LIMIT) restartRole(cfg, `public tunnel health dead: ${url}`);
  }
}, HEALTH_INTERVAL_MS).unref?.();

if (!ROLES.length) { log('Chua cau hinh role nao (RD_PORT/QH_PORT). Thoat.'); process.exit(1); }
log('LH tunnel publisher khoi dong. Deploy dir:', DEPLOY_DIR, '| roles:', ROLES.map(r => r.role).join(','));
ROLES.forEach(runRole);
