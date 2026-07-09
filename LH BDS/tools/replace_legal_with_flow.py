from pathlib import Path
root=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace')
flow=root/'LH BDS/Luat BDS/FINAL_BDS_LEGAL_WEB/index.html'
out=root/'LH BDS/public_final_recovered/legal.html'
s=flow.read_text(encoding='utf-8')
s=s.replace('<title>Lưu đồ đầu tư xây dựng dự án BĐS</title>','<title>LH Real Estate - Pháp lý dự án BĐS</title>')
# Add LH nav CSS and page polish before </style>
extra_css=r'''
/* LH Real Estate shell integration */
.siteTop{position:sticky;top:0;z-index:80;background:rgba(7,21,38,.94);backdrop-filter:blur(18px);border-bottom:1px solid rgba(213,173,85,.38);box-shadow:0 16px 42px rgba(7,21,38,.22)}
.siteInner{max-width:1440px;margin:auto;padding:10px 18px;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:900}.brand .logo{width:36px;height:36px;border-radius:12px;background:linear-gradient(135deg,#d5ad55,#f4dc91);color:#071526;display:grid;place-items:center;font-weight:950;box-shadow:0 10px 28px rgba(213,173,85,.28)}.nav{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}.nav a{color:#dbeafe;text-decoration:none;border:1px solid transparent;border-radius:999px;padding:8px 11px;font-weight:800;font-size:13px}.nav a:hover{background:rgba(255,255,255,.08);border-color:rgba(213,173,85,.32)}.nav a.active{background:linear-gradient(135deg,#d5ad55,#f4dc91);color:#071526}.pageHero{max-width:1440px;margin:22px auto 0;padding:0 18px}.heroPanel{position:relative;overflow:hidden;border-radius:34px;background:radial-gradient(760px 320px at 82% 0%,rgba(213,173,85,.28),transparent 62%),linear-gradient(135deg,#071526,#102542 58%,#17345f);border:1px solid rgba(213,173,85,.55);color:white;padding:32px;box-shadow:0 30px 90px rgba(7,21,38,.28)}.heroPanel:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:42px 42px;mask-image:radial-gradient(circle at 82% 8%,#000,transparent 70%);pointer-events:none}.heroPanel>*{position:relative}.heroPanel .eyebrow2{display:inline-flex;border:1px solid rgba(213,173,85,.55);background:rgba(213,173,85,.14);border-radius:999px;padding:7px 11px;color:#f8df8a;font-weight:950;font-size:12px;letter-spacing:.09em;text-transform:uppercase}.heroPanel h1{font-size:clamp(38px,5.5vw,76px);line-height:.96;letter-spacing:-.06em;margin:14px 0 10px;text-wrap:balance}.heroPanel p{max-width:980px;color:#dbeafe;font-size:18px}.top.flowTitle{display:none}.wrap{max-width:1440px!important}.board{border-radius:30px!important}.flow{min-width:1980px}.node{border-radius:18px!important}.dialog{max-width:1240px!important}.modal{z-index:120}@media(max-width:900px){.siteInner{align-items:flex-start;flex-direction:column}.nav{justify-content:flex-start}.heroPanel{padding:24px}.heroPanel h1{font-size:38px}}
'''
s=s.replace('</style>', extra_css+'\n</style>',1)
old='<body><header class="top"><h1>Lưu đồ đầu tư xây dựng dự án BĐS</h1><p>Thiết kế theo bản lưu đồ TPRE: bấm từng ô để mở popup luật liên quan, quy trình, thời gian, điều kiện, lưu ý và nguồn điều/khoản.</p></header>'
new='''<body><header class="siteTop"><div class="siteInner"><div class="brand"><div class="logo">LH</div><div>LH Real Estate</div></div><nav class="nav"><a href="index.html">Tổng quan</a><a href="nvtc.html">Nghĩa vụ tài chính</a><a href="quyhoach.html">Quy hoạch</a><a href="rd.html">R&D thị trường</a><a href="fs.html">FS hiệu quả dự án</a><a class="active" href="legal.html">Pháp lý & Đầu tư</a><a href="dossier.html">Hồ sơ dự án</a><a href="status.html">Status</a></nav></div></header><section class="pageHero"><div class="heroPanel"><span class="eyebrow2">LH Legal Project Flow</span><h1>Lưu đồ pháp lý phát triển dự án BĐS</h1><p>Thay thế AI luật cũ bằng sổ tay quy trình pháp lý: bấm từng mốc để xem điều kiện, hồ sơ, quy trình, cách tính, rủi ro và căn cứ điều khoản liên quan.</p></div></section>'''
s=s.replace(old,new)
# fallback if header was slightly different
s=s.replace('<header class="top"><h1>Lưu đồ đầu tư xây dựng dự án BĐS</h1><p>Thiết kế theo bản lưu đồ TPRE: bấm từng ô để mở popup luật liên quan, quy trình, thời gian, điều kiện, lưu ý và nguồn điều/khoản.</p></header>','<header class="top flowTitle"><h1>Lưu đồ đầu tư xây dựng dự án BĐS</h1></header>')
out.write_text(s,encoding='utf-8')
# copy required data files
for name in ['tpre_bds_flow.json','tpre_legal_deep_modules.json']:
    src=root/'LH BDS/Luat BDS/FINAL_BDS_LEGAL_WEB'/name
    if not src.exists(): src=root/'LH BDS/Luat BDS/web_mindmap'/name
    (root/'LH BDS/public_final_recovered'/name).write_text(src.read_text(encoding='utf-8'),encoding='utf-8')
print('replaced legal with flow', out)
