# -*- coding: utf-8 -*-
from pathlib import Path
p=Path(__file__).with_name('tpre_flowchart_popup.html')
s=p.read_text(encoding='utf-8')
old="""subs.forEach(s=>{const p=DATA.phases.find(x=>x.id===s[0]); const it=p.items[0]; const obj={phase:p,item:{...it,code:s[2],title:s[3],summary:'Node chi ti?t theo ma luu d? PDF. N?i dung ph�p ly k? th?a t? m?c ch�nh v� s? ti?p t?c du?c t�ch s�u theo h? so/th? t?c ri�ng.',owner:p.lane}}; ALL.push(obj); const [col]=layout[s[0]]; f.insertAdjacentHTML('beforeend',`<div class="node small ${s[1]} ${col} ${s[4]}" onclick="openNode(${ALL.length-1})"><span class="code">${esc(s[2])}</span><h3>${esc(s[3])}</h3></div>`)});"""
new="""subs.forEach(s=>{const p=DATA.phases.find(x=>x.id===s[0]||x.id.split('.')[0]===s[0]); if(!p||!p.items||!p.items[0]) return; const it=p.items[0]; const obj={phase:p,item:{...it,code:s[2],title:s[3],summary:'Node chi tiết theo mã lưu đồ PDF. Nội dung pháp lý kế thừa từ mốc chính và được tách sâu theo hồ sơ/thủ tục riêng.',owner:p.lane}}; ALL.push(obj); const [col]=layout[s[0]]||layout[p.id]||['col1']; f.insertAdjacentHTML('beforeend',`<div class="node small ${s[1]} ${col} ${s[4]}" onclick="openNode(${ALL.length-1})"><span class="code">${esc(s[2])}</span><h3>${esc(s[3])}</h3></div>`)});"""
if old in s:
    s=s.replace(old,new)
else:
    s=s.replace("const p=DATA.phases.find(x=>x.id===s[0]); const it=p.items[0];", "const p=DATA.phases.find(x=>x.id===s[0]||x.id.split('.')[0]===s[0]); if(!p||!p.items||!p.items[0]) return; const it=p.items[0];")
    s=s.replace("summary:'Node chi ti?t theo ma luu d? PDF. N?i dung ph�p ly k? th?a t? m?c ch�nh v� s? ti?p t?c du?c t�ch s�u theo h? so/th? t?c ri�ng.'", "summary:'Node chi tiết theo mã lưu đồ PDF. Nội dung pháp lý kế thừa từ mốc chính và được tách sâu theo hồ sơ/thủ tục riêng.'")
    s=s.replace("const [col]=layout[s[0]];", "const [col]=layout[s[0]]||layout[p.id]||['col1'];")
old_fn_start=s.find('function phasePlaybookBlock')
old_fn_end=s.find('function procedureBlock', old_fn_start)
if old_fn_start!=-1 and old_fn_end!=-1:
    fn="""function phasePlaybookBlock(it){const d=it.phase_detail; if(!d) return ''; const groups=[['Mục tiêu phase',[d.objective]],['Phạm vi việc phải làm',d.scope],['Hồ sơ cần có',d.dossier],['Quy trình triển khai',d.procedure],['Output cần chốt',d.output],['Rủi ro trọng yếu',d.risks]]; return `<div class=\"playbookBox\"><h4>Playbook triển khai từng phase</h4><div class=\"playbookGrid\">${groups.map(g=>`<div class=\"playbookCard\"><b>${esc(g[0])}</b>${lines(g[1]||[])}</div>`).join('')}</div></div>`}\n"""
    s=s[:old_fn_start]+fn+s[old_fn_end:]
p.write_text(s,encoding='utf-8')
for out in [p.parents[0].parent/'FINAL_BDS_LEGAL_WEB/tpre_flowchart_popup.html', p.parents[0].parent/'FINAL_BDS_LEGAL_WEB/index.html', Path('deploy_bds_legal_process/public/bds-legal-process/index.html')]:
    out=Path(out)
    if out.exists(): out.write_text(s,encoding='utf-8')
print('patched ui e2e fixes')
