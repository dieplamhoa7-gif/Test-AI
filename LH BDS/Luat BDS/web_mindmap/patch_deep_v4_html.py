from pathlib import Path
out=Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
html=(out/'legal_flow_drilldown_v3.html').read_text(encoding='utf-8')
html=html.replace("fetch('legal_ontology_v3.json').then(r=>r.json()).then(boot);","fetch('legal_deep_v4.json').then(r=>r.json()).then(boot);")
html=html.replace('LH BĐS Legal Ontology','LH BĐS Deep Legal Flow').replace('Ontology luật • bấm từng lớp để đi sâu','Deep research • 182 căn cứ • drill-down')
old="""<div class=\"box\"><h3>Câu hỏi/checkpoint</h3><ul>${(n.checkpoints||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div class=\"box\"><h3>Trích dẫn và tóm tắt điều luật</h3>"""
new="""<div class=\"box\"><h3>Câu hỏi/checkpoint</h3><ul>${(n.checkpoints||[]).map(x=>`<li>${esc(x)}</li>`).join('')||'<li>Đối chiếu điều kiện áp dụng theo hồ sơ dự án cụ thể.</li>'}</ul></div><div class=\"box\"><h3>Output cần chốt</h3><ul>${(n.outputs||[]).map(x=>`<li>${esc(x)}</li>`).join('')||'<li>Checklist hồ sơ, cơ quan, thời hạn và văn bản đầu ra.</li>'}</ul></div><div class=\"box\"><h3>Rủi ro chính</h3><ul>${(n.risks||[]).map(x=>`<li>${esc(x)}</li>`).join('')||'<li>Cần legal review theo loại dự án, nguồn gốc đất và địa phương.</li>'}</ul></div><div class=\"box\"><h3>Trích dẫn và tóm tắt điều luật</h3>"""
if old not in html:
    print('old snippet not found, writing without detail patch')
else:
    html=html.replace(old,new)
(out/'legal_deep_v4.html').write_text(html,encoding='utf-8')
print(out/'legal_deep_v4.html')
