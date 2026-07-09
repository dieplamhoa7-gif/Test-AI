import re, json, html
from pathlib import Path
src=Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx")
out=Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
out.mkdir(parents=True, exist_ok=True)

STEPS=[
 {"id":"s00","name":"0. Chiến lược & rà soát pháp lý ban đầu","keywords":["phù hợp quy hoạch","thông tin quy hoạch","kế hoạch sử dụng đất","đấu giá","đấu thầu","chấp thuận chủ trương đầu tư","nhà đầu tư"],"need":"Xác định quỹ đất, hiện trạng pháp lý, quy hoạch, chỉ tiêu sơ bộ, hình thức tiếp cận đất và rủi ro pháp lý."},
 {"id":"s01","name":"1. Quy hoạch / chỉ tiêu / chương trình phát triển","keywords":["quy hoạch xây dựng","quy hoạch đô thị","quy hoạch chi tiết","1/500","chỉ tiêu quy hoạch","chương trình phát triển nhà ở","khu đô thị"],"need":"Làm rõ căn cứ quy hoạch, chỉ tiêu sử dụng đất, mật độ, tầng cao, dân số, hạ tầng và sự phù hợp với chương trình/kế hoạch phát triển nhà ở."},
 {"id":"s02","name":"2. Chấp thuận chủ trương đầu tư / lựa chọn nhà đầu tư","keywords":["chấp thuận chủ trương đầu tư","chấp thuận nhà đầu tư","lựa chọn nhà đầu tư","đấu thầu lựa chọn nhà đầu tư","đấu giá quyền sử dụng đất","dự án đầu tư có sử dụng đất"],"need":"Xác lập quyền triển khai dự án: quyết định/chấp thuận chủ trương, hình thức lựa chọn NĐT, năng lực, ký quỹ/bảo đảm thực hiện."},
 {"id":"s03","name":"3. Giao đất, cho thuê đất, chuyển mục đích, thu hồi/bồi thường","keywords":["giao đất","cho thuê đất","chuyển mục đích sử dụng đất","thu hồi đất","bồi thường","hỗ trợ tái định cư","giải phóng mặt bằng"],"need":"Hoàn tất thủ tục đất đai để có quyền sử dụng đất hợp pháp cho dự án; xử lý thu hồi, bồi thường, tái định cư nếu có."},
 {"id":"s04","name":"4. Nghĩa vụ tài chính đất đai / giá đất / thuế phí","keywords":["tiền sử dụng đất","tiền thuê đất","giá đất","bảng giá đất","nghĩa vụ tài chính","thuế","lệ phí trước bạ","khấu trừ"],"need":"Xác định và hoàn thành tiền sử dụng đất/tiền thuê đất, giá đất cụ thể, thuế phí và các khoản tài chính liên quan."},
 {"id":"s05","name":"5. Môi trường, PCCC, hạ tầng kỹ thuật & đấu nối","keywords":["đánh giá tác động môi trường","bảo vệ môi trường","phòng cháy chữa cháy","pccc","đấu nối hạ tầng","cấp nước","thoát nước","điện lực"],"need":"Có phê duyệt/xác nhận môi trường, PCCC và thỏa thuận đấu nối hạ tầng kỹ thuật trước khi/đồng thời với thiết kế - xây dựng."},
 {"id":"s06","name":"6. Thiết kế, thẩm định, giấy phép xây dựng","keywords":["thiết kế cơ sở","thẩm định thiết kế","giấy phép xây dựng","khởi công","quản lý chất lượng công trình","nghiệm thu"],"need":"Hoàn thiện hồ sơ thiết kế, thẩm định chuyên ngành, cấp phép xây dựng và điều kiện khởi công."},
 {"id":"s07","name":"7. Thi công, nghiệm thu, hoàn công","keywords":["thi công xây dựng","giám sát thi công","nghiệm thu hoàn thành","hoàn công","bàn giao công trình","quản lý chất lượng"],"need":"Quản lý thi công theo thiết kế/giấy phép; nghiệm thu từng phần và hoàn thành công trình/hạ tầng."},
 {"id":"s08","name":"8. Huy động vốn, bán/cho thuê mua BĐS hình thành trong tương lai","keywords":["huy động vốn","bất động sản hình thành trong tương lai","đủ điều kiện bán","bảo lãnh ngân hàng","hợp đồng mua bán","kinh doanh bất động sản"],"need":"Đảm bảo điều kiện kinh doanh, bảo lãnh, thông báo đủ điều kiện bán/cho thuê mua, mẫu hợp đồng và giới hạn huy động vốn."},
 {"id":"s09","name":"9. Cấp GCN/sổ, bàn giao, vận hành, hậu kiểm","keywords":["cấp giấy chứng nhận","giấy chứng nhận quyền sử dụng đất","quyền sở hữu nhà ở","bàn giao nhà","quản lý vận hành","bảo trì","chung cư"],"need":"Cấp sổ cho chủ đầu tư/người mua, bàn giao nhà/công trình, lập ban quản trị/quỹ bảo trì/vận hành và xử lý hậu kiểm."},
]

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def split_articles(text):
    matches=list(re.finditer(r'(?m)^\s*(Điều\s+\d+[a-zA-Z]?\.\s+[^\n]+)', text))
    arts=[]
    for i,m in enumerate(matches):
        start=m.start(); end=matches[i+1].start() if i+1<len(matches) else min(len(text), start+6000)
        block=text[start:end].strip()
        title=clean(m.group(1))
        body=clean(block[len(m.group(1)):])[:1800]
        arts.append({"title":title,"body":body,"text":clean(block)[:2600]})
    return arts

def doc_title(text,p):
    for l in text.splitlines():
        l=clean(re.sub(r'^#+\s*','',l))
        if l: return l[:220]
    return p.stem

docs=[]
for p in sorted(src.glob('*.md')):
    text=p.read_text(encoding='utf-8',errors='ignore')
    docs.append({"file":p.name,"title":doc_title(text,p),"text":text,"articles":split_articles(text)})

process=[]
for step in STEPS:
    evid=[]
    kws=[k.lower() for k in step['keywords']]
    for d in docs:
        hay=(d['title']+' '+d['file']).lower()
        # article hits first
        for a in d['articles']:
            low=(a['title']+' '+a['body']).lower()
            score=sum(3 if k in a['title'].lower() else 1 for k in kws if k in low)
            if score:
                evid.append({"score":score,"source_file":d['file'],"source_title":d['title'],"article":a['title'],"quote":a['text'][:900],"summary":clean(a['body'])[:450]})
        # doc-level fallback
        score=sum(1 for k in kws if k in d['text'][:12000].lower() or k in hay)
        if score and not any(e['source_file']==d['file'] for e in evid[-8:]):
            evid.append({"score":score,"source_file":d['file'],"source_title":d['title'],"article":"Văn bản liên quan / cần đọc chi tiết","quote":clean(d['text'][:1200]),"summary":"Văn bản có nội dung liên quan đến bước này; cần rà điều khoản chi tiết khi lập checklist hồ sơ."})
    evid=sorted(evid,key=lambda x:(-x['score'],x['source_file'],x['article']))[:18]
    process.append({**step,"evidence":evid})

timeline=[
 {"phase":"P0","step":"Rà soát quỹ đất & quy hoạch","outputs":"Báo cáo pháp lý đất, quy hoạch, phương án tiếp cận đất, risk register","depends":"—"},
 {"phase":"P1","step":"Quy hoạch/chương trình phát triển","outputs":"Văn bản quy hoạch/chỉ tiêu/quy hoạch chi tiết hoặc xác nhận phù hợp","depends":"P0"},
 {"phase":"P2","step":"Chủ trương đầu tư & lựa chọn NĐT","outputs":"Chấp thuận chủ trương/chấp thuận NĐT/kết quả đấu giá-đấu thầu","depends":"P1"},
 {"phase":"P3","step":"Đất đai & GPMB","outputs":"Thu hồi/bồi thường/tái định cư; giao đất/thuê đất/chuyển mục đích","depends":"P2"},
 {"phase":"P4","step":"Nghĩa vụ tài chính","outputs":"Thông báo và chứng từ hoàn thành tiền sử dụng đất/tiền thuê đất/thuế phí","depends":"P3"},
 {"phase":"P5","step":"Môi trường/PCCC/hạ tầng","outputs":"ĐTM/GPMT, thẩm duyệt PCCC, thỏa thuận đấu nối","depends":"P2-P4, có thể song song một phần"},
 {"phase":"P6","step":"Thiết kế & giấy phép xây dựng","outputs":"Thẩm định thiết kế, giấy phép xây dựng, điều kiện khởi công","depends":"P3-P5"},
 {"phase":"P7","step":"Thi công & nghiệm thu","outputs":"Biên bản nghiệm thu, hoàn công, nghiệm thu PCCC/hạ tầng","depends":"P6"},
 {"phase":"P8","step":"Kinh doanh/huy động vốn","outputs":"Thông báo đủ điều kiện bán, bảo lãnh, hợp đồng, hồ sơ bán hàng","depends":"P4-P7 tùy loại sản phẩm"},
 {"phase":"P9","step":"Cấp sổ/bàn giao/vận hành","outputs":"GCN cho người mua, bàn giao, vận hành, bảo trì, hậu kiểm","depends":"P7-P8"},
]

data={"root":"Quy trình phát triển dự án BĐS","source_dir":str(src),"doc_count":len(docs),"process":process,"master_timeline":timeline}
(out/'process_mindmap_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

html_doc='''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Process Mindmap Pháp lý BĐS</title><style>
:root{--bg:#07111f;--panel:#0e1b2d;--text:#eaf2ff;--muted:#9fb3c8;--line:#2d4d73;--accent:#7dd3fc;--gold:#fbbf24;--green:#86efac;--red:#fca5a5}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#102647,#07111f 55%);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}header{position:sticky;top:0;z-index:5;background:rgba(7,17,31,.9);backdrop-filter:blur(10px);border-bottom:1px solid #213a59;padding:14px 18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}h1{font-size:20px;margin:0}.badge{background:var(--accent);color:#06111f;border-radius:999px;padding:4px 9px;font-weight:800;font-size:12px}input{flex:1;min-width:260px;background:#081525;color:var(--text);border:1px solid #2a4666;border-radius:10px;padding:10px 12px}main{display:grid;grid-template-columns:430px 1fr;gap:16px;padding:16px}@media(max-width:980px){main{grid-template-columns:1fr}}.panel{background:rgba(14,27,45,.82);border:1px solid #203a58;border-radius:16px;padding:14px;box-shadow:0 10px 30px #0005}.muted{color:var(--muted)}.step{border:1px solid #28476a;border-radius:14px;margin:10px 0;overflow:hidden}.step summary{cursor:pointer;padding:12px 14px;background:#10243c;font-weight:850}.step.active summary{background:#17395d;color:#fff}.need{padding:10px 14px;color:#cfe7ff;border-top:1px solid #203a58}.ev{padding:10px 14px;border-top:1px solid #1d344f;cursor:pointer}.ev:hover{background:#132a45}.ev .art{font-weight:750}.file{font-family:ui-monospace,Consolas,monospace;color:var(--green);font-size:12px}.quote{white-space:pre-wrap;background:#071525;border-left:3px solid var(--gold);padding:12px;border-radius:10px;color:#e8f1ff;line-height:1.5}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}@media(max-width:780px){.grid{grid-template-columns:1fr}}.card{border:1px solid #29496d;border-radius:12px;padding:10px;background:#0b1a2c}.timeline{display:grid;grid-template-columns:90px 1fr;gap:8px}.phase{color:#06111f;background:var(--gold);border-radius:9px;padding:7px;text-align:center;font-weight:900}.tlitem{border-left:2px solid #31587f;padding:0 0 12px 12px}.pill{display:inline-block;border:1px solid #31587f;border-radius:999px;padding:3px 8px;margin:3px;color:#cfe7ff;font-size:12px}svg{width:100%;height:620px;background:rgba(5,12,22,.52);border:1px solid #203a58;border-radius:16px}.node{cursor:pointer}.node circle{fill:#123150;stroke:#7dd3fc;stroke-width:1.5}.node.root circle{fill:#fbbf24;stroke:#fde68a}.node text{fill:#eaf2ff;font-size:12px}.link{stroke:#31587f;stroke-width:1.5;fill:none;opacity:.8}</style></head><body><header><h1>Process Mindmap Pháp lý BĐS</h1><span class="badge" id="count"></span><input id="q" placeholder="Tìm bước, điều luật, hồ sơ, nghĩa vụ..."/><span class="muted">Tổng thể → bước → điều khoản → tóm tắt</span></header><main><section class="panel"><h2>Master process</h2><div id="steps"></div></section><section><svg id="map"></svg><div class="panel" id="detail"><h2>Master timeline</h2><div id="timeline"></div></div></section></main><script>
let DATA, active=null; const esc=s=>(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
function renderSteps(f=''){f=f.toLowerCase(); let html=''; DATA.process.forEach((s,i)=>{let ev=s.evidence.filter(e=>!f||JSON.stringify(e).toLowerCase().includes(f)||s.name.toLowerCase().includes(f)||s.need.toLowerCase().includes(f)); if(f&&!ev.length&&!s.name.toLowerCase().includes(f))return; html+=`<details class="step ${active===s.id?'active':''}" open><summary onclick="setTimeout(()=>showStep('${s.id}'),0)">${esc(s.name)} <span class="muted">(${ev.length} trích dẫn)</span></summary><div class="need"><b>Cần:</b> ${esc(s.need)}</div>`; ev.forEach((e,j)=>html+=`<div class="ev" onclick="showEvidence('${s.id}',${j})"><div class="art">${esc(e.article)}</div><div class="file">${esc(e.source_file)}</div><div class="muted">${esc(e.summary)}</div></div>`); html+='</details>'}); document.getElementById('steps').innerHTML=html; drawMap();}
function timeline(){document.getElementById('timeline').innerHTML='<div class="timeline">'+DATA.master_timeline.map(t=>`<div class="phase">${esc(t.phase)}</div><div class="tlitem"><b>${esc(t.step)}</b><br><span class="muted">Output: ${esc(t.outputs)}</span><br><span class="muted">Depends: ${esc(t.depends)}</span></div>`).join('')+'</div>'}
function showStep(id){active=id; const s=DATA.process.find(x=>x.id===id); document.getElementById('detail').innerHTML=`<h2>${esc(s.name)}</h2><p><b>Mục tiêu/cần có:</b> ${esc(s.need)}</p><div class="grid">${s.evidence.slice(0,8).map(e=>`<div class="card"><b>${esc(e.article)}</b><br><span class="file">${esc(e.source_file)}</span><p class="muted">${esc(e.summary)}</p></div>`).join('')}</div>`; drawMap();}
function showEvidence(id,idx){active=id; const s=DATA.process.find(x=>x.id===id); const e=s.evidence[idx]; document.getElementById('detail').innerHTML=`<h2>${esc(s.name)}</h2><p><span class="pill">${esc(e.source_title)}</span><span class="pill file">${esc(e.source_file)}</span></p><h3>${esc(e.article)}</h3><p><b>Tóm tắt:</b> ${esc(e.summary)}</p><h3>Trích điều / đoạn nguồn</h3><div class="quote">${esc(e.quote)}</div>`; drawMap();}
function drawMap(){const svg=document.getElementById('map'),w=svg.clientWidth||900,h=svg.clientHeight||620; svg.innerHTML=''; function el(n,a){const e=document.createElementNS('http://www.w3.org/2000/svg',n); for(const k in a)e.setAttribute(k,a[k]); return e} function line(x1,y1,x2,y2){svg.appendChild(el('path',{class:'link',d:`M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}`}))} function node(x,y,label,cls,id){const g=el('g',{class:'node '+cls,transform:`translate(${x},${y})`}); const c=el('circle',{r:cls==='root'?10:7}); if(id===active){c.setAttribute('stroke','#fbbf24');c.setAttribute('stroke-width','4')} g.appendChild(c); const t=el('text',{x:12,dy:'0.32em'}); t.textContent=label; g.appendChild(t); if(id)g.addEventListener('click',()=>showStep(id)); svg.appendChild(g)} const rx=55,ry=h/2,sx=260,ex=590; node(rx,ry,DATA.root,'root'); DATA.process.forEach((s,i)=>{const y=(i+1)*h/(DATA.process.length+1); line(rx,ry,sx,y); node(sx,y,s.name.replace(/^\d+\.\s*/,''),'step',s.id); s.evidence.slice(0,3).forEach((e,j)=>{const yy=y+(j-1)*22; line(sx,y,ex,yy); node(ex,yy,e.article.slice(0,52),'ev',s.id)})})}
fetch('process_mindmap_data.json').then(r=>r.json()).then(d=>{DATA=d; document.getElementById('count').textContent=d.doc_count+' văn bản'; renderSteps(); timeline(); document.getElementById('q').oninput=e=>renderSteps(e.target.value); addEventListener('resize',drawMap)});
</script></body></html>'''
(out/'process_mindmap.html').write_text(html_doc,encoding='utf-8')
print('Built', out/'process_mindmap.html')
print('Docs', len(docs), 'Steps', len(process), 'Citations', sum(len(s['evidence']) for s in process))
