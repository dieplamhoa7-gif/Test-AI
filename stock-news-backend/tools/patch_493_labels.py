from pathlib import Path
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8')
labels="const sectionLabels={news:'Tin t\\u1ee9c & t\\u00e1c \\u0111\\u1ed9ng',technical:'Ch\\u1ec9 b\\u00e1o LHInvestment / PTKT',fundamental:'C\\u01a1 b\\u1ea3n & v\\u0129 m\\u00f4',scenario:'K\\u1ecbch b\\u1ea3n \\u0111\\u1ea7u t\\u01b0',bull_bear:'T\\u0103ng gi\\u00e1 / Gi\\u1ea3m gi\\u00e1 / Ch\\u1ea5t x\\u00fac t\\u00e1c',risk:'R\\u1ee7i ro & quan \\u0111i\\u1ec3m',followup:'K\\u1ebf ho\\u1ea1ch theo d\\u00f5i',quick_summary:'T\\u00f3m t\\u1eaft \\u0111i\\u1ec1u h\\u00e0nh',word:'Xu\\u1ea5t Word',notebooklm:'NotebookLM / PDF online'};\n"
if 'const sectionLabels=' not in s:
    s=s.replace('function node(s){return `', labels+'function node(s){return `')
else:
    import re
    s=re.sub(r'const sectionLabels=.*?;\n', labels, s, flags=re.S)
s=s.replace('${clean(s.name||s.key)}</div><div class="by">','${sectionLabels[s.key]||clean(s.name||s.key)}</div><div class="by">')
p.write_text(s,encoding='utf-8')
