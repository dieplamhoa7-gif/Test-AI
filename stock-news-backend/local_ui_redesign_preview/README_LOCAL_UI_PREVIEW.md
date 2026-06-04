# LH Investment Local UI Redesign Preview

Created: 2026-06-04

This folder is a local-only copy of `stock-news-backend/firebase_public/` for UI experimentation.

## Safety

- Production Firebase files are not modified by this preview.
- No deploy command was run.
- No build/regeneration script was run.
- Changes are surgical CSS/HTML polish in this copied folder only.

## Preview URL

A local Node static server can serve this directory at:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\local_ui_redesign_preview
node -e "const http=require('http'),fs=require('fs'),path=require('path');const root=process.cwd();const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'};http.createServer((req,res)=>{let u=decodeURIComponent(req.url.split('?')[0]); if(u==='/'||u==='/stocks')u='/stocks.html'; let p=path.join(root,u); if(!p.startsWith(root)){res.writeHead(403);return res.end('forbidden')} fs.readFile(p,(e,d)=>{if(e){res.writeHead(404);return res.end('not found')} res.writeHead(200,{'content-type':types[path.extname(p).toLowerCase()]||'application/octet-stream'});res.end(d)})}).listen(8787,'127.0.0.1',()=>console.log('local ui preview http://127.0.0.1:8787/stocks.html'))"
```

Open:

`http://127.0.0.1:8787/stocks.html`

## Design direction

Inspired by the added skills:

- `frontend-craft-skill`
- `ui-arsenal`
- `avoid-ai-design`
- `design-linear`
- `design-stripe`
- `design-robinhood`

## What changed in the preview

- Local preview safety banner.
- Wider dashboard container.
- Glass/finance dashboard background.
- Sticky pill-style tabs.
- Better cards, hover states, shadow hierarchy.
- Improved market/index/sector card visual density.
- Better modal/chart spacing.
- Mobile responsive refinement.
- Reduced-motion accessibility guard.

## V2 prototype

A stronger redesign prototype was added at:

http://127.0.0.1:8787/stocks-redesign-v2.html`n
This version is intentionally different from the classic UI: left sidebar, hero cockpit, KPI cards, watchlist table, chart focus area, strategy cards, and news panel.

