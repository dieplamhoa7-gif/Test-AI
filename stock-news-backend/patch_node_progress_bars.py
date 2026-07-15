from pathlib import Path
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8')
# Add node-level progress bar CSS if missing.
s=s.replace(".name{font-size:13px;font-weight:850}.connector", ".name{font-size:13px;font-weight:850}.nodeProgress{height:7px;border-radius:999px;background:#061023;overflow:hidden;margin-top:12px}.nodeProgress span{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--cyan),var(--green));transition:.35s}.node.running .nodeProgress span{background:linear-gradient(90deg,var(--cyan),var(--blue))}.node.error .nodeProgress span{background:var(--red)}.connector")
old="function node(s){const name=sectionLabels[s.key]||s.name||s.key;return `<div class=\"node ${cls(s.status)}\"><div class=\"nodeTop\"><div><div class=\"name\">${esc(name)}</div><div class=\"by\">${esc(s.agent||'-')}</div></div><span class=\"pill ${cls(s.status)}\">${st(s.status)}</span></div></div>`}"
new="function node(s){const name=sectionLabels[s.key]||s.name||s.key;const np=s.status==='done'||s.status==='skipped'?100:s.status==='running'?55:s.status==='error'?100:8;return `<div class=\"node ${cls(s.status)}\"><div class=\"nodeTop\"><div><div class=\"name\">${esc(name)}</div><div class=\"by\">${esc(s.agent||'-')}</div></div><span class=\"pill ${cls(s.status)}\">${st(s.status)}</span></div><div class=\"nodeProgress\"><span style=\"width:${np}%\"></span></div></div>`}"
if old not in s:
    raise SystemExit('node function pattern not found')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8',newline='\n')
print('patched node bars')
