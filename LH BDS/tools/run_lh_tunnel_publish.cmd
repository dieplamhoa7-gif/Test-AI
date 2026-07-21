@echo off
set RD_PORT=8787
set QH_PORT=8788
set DEPLOY_DIR=public_final_2026_07_11
set FIREBASE_SITE=lhrealestate
set FIREBASE_PROJECT=hoa-investment
set FIREBASE_CONFIG=firebase.json
set HEALTH_INTERVAL_MS=30000
set HEALTH_FAIL_LIMIT=3
cd /d "C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS"
node tools\lh_tunnel_publish.js
