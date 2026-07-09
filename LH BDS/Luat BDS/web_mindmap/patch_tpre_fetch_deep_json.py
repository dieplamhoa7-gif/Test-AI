from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\tpre_flowchart_popup.html')
s=p.read_text(encoding='utf-8')
# add css if not present
if '.deepLegalBox' not in s:
    s=s.replace('.fullChecklist{grid-column:1/-1;border:1px solid #dbeafe;background:#f8fbff;border-radius:18px;padding:16px}', '.deepLegalBox{grid-column:1/-1;border:1px solid #b2f2bb;background:#f6fff7;border-radius:18px;padding:16px}.deepLegalBox h4{margin:0 0 12px;text-transform:uppercase;font-size:12px;letter-spacing:.08em;color:#2b8a3e}.deepGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.deepCard{background:white;border:1px solid #d3f9d8;border-radius:14px;padding:12px}.deepCard b{display:block;color:#2b8a3e;margin-bottom:8px}.fullChecklist{grid-column:1/-1;border:1px solid #dbeafe;background:#f8fbff;border-radius:18px;padding:16px}')
    s=s.replace('@media(max-width:900px){.expertGrid,.formulaGrid,.checkGrid,.howtoGrid{grid-template-columns:1fr}}', '@media(max-width:900px){.expertGrid,.formulaGrid,.checkGrid,.howtoGrid,.deepGrid{grid-template-columns:1fr}}')
# global DEEP and fetch
s=s.replace('let DATA, ALL=[];', "let DATA, ALL=[], DEEP={};")
s=s.replace("fetch('tpre_bds_flow.json').then(r=>r.json()).then(d=>{DATA=d;build()});", "Promise.all([fetch('tpre_bds_flow.json').then(r=>r.json()),fetch('tpre_legal_deep_modules.json').then(r=>r.json()).catch(()=>({}))]).then(([d,deep])=>{DATA=d;DEEP=deep||{};build()});")
# insert render function before fullChecklistBlock
if 'function deepLegalBlock' not in s:
    insert="""function deepLegalBlock(code,id){const arr=DEEP[id]||[]; if(!arr.length) return ''; return `<div class=\"deepLegalBox\"><h4>Pháp lý chuyên sâu — tách từ module JSON</h4><div class=\"deepGrid\">${arr.map(g=>`<div class=\"deepCard\"><b>${esc(g.title)}</b>${lines(g.items)}</div>`).join('')}</div></div>`}\n"""
    s=s.replace('function fullChecklistBlock', insert+'function fullChecklistBlock')
# add block in modal
s=s.replace('${fullChecklistBlock(it.code||p.id,p.id)}${gapBlock(it.code||p.id,p.id)}${howtoBlock(it.code||p.id,p.id)}', '${fullChecklistBlock(it.code||p.id,p.id)}${deepLegalBlock(it.code||p.id,p.id)}${gapBlock(it.code||p.id,p.id)}${howtoBlock(it.code||p.id,p.id)}')
# gentle UI upgrade stable
s=s.replace('background:linear-gradient(180deg,#eef4ff,#fbfcff 35%,#f6f8fb)', 'background:radial-gradient(circle at 10% 0%,rgba(25,103,210,.16),transparent 30%),radial-gradient(circle at 88% 6%,rgba(112,72,232,.12),transparent 28%),linear-gradient(180deg,#eef4ff,#fbfcff 35%,#f6f8fb)')
s=s.replace('border-radius:22px;box-shadow:var(--shadow);padding:18px', 'border-radius:28px;box-shadow:0 28px 80px rgba(31,44,71,.18);padding:22px')
s=s.replace('border-radius:24px;box-shadow:0 30px 110px rgba(0,0,0,.35)', 'border-radius:30px;box-shadow:0 40px 130px rgba(0,0,0,.38)')
s=s.replace('max-width:1120px', 'max-width:1240px')
p.write_text(s,encoding='utf-8')
print('patched fetch deep json')
