from pathlib import Path
p=Path('app/dashboard_template.py')
s=p.read_text(encoding='utf-8')
first=s.index("    function strategyVisualSvg(style='primary') {")
second=s.index("    function strategyVisualSvg(style='primary') {", first+1)
s=s[:first]+s[second:]
p.write_text(s, encoding='utf-8')
print('removed duplicate strategy funcs')
