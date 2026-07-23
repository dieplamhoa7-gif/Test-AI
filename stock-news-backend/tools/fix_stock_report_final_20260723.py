from pathlib import Path
import re
p = Path('firebase_public/stock-report.html')
s = p.read_text(encoding='utf-8', errors='replace')
# Remove report nav/menu only; keep final stock-like header/body/theme from 634d9e74e
s = re.sub(r'\n\s*<nav class="main-tabs".*?</nav>\s*', '\n', s, flags=re.S|re.I)
s = re.sub(r'\s*\.main-tabs\{.*?body\.light-theme \.chip-btn\.active\{.*?\}\s*', '\n    ', s, flags=re.S)
# Replace fixed labels with JS unicode escapes so source survives Windows shells and browser renders Vietnamese correctly.
def sub(pattern, repl):
    global s
    s = re.sub(pattern, lambda m: repl, s, flags=re.S)
sub(r"const sectionLabels=.*?;", "const sectionLabels={news:'Tin t\\u1ee9c & t\\u00e1c \\u0111\\u1ed9ng',technical:'Ch\\u1ec9 b\\u00e1o LHInvestment / PTKT',fundamental:'C\\u01a1 b\\u1ea3n & v\\u0129 m\\u00f4',scenario:'K\\u1ecbch b\\u1ea3n \\u0111\\u1ea7u t\\u01b0',bull_bear:'T\\u0103ng gi\\u00e1 / Gi\\u1ea3m gi\\u00e1 / Ch\\u1ea5t x\\u00fac t\\u00e1c',risk:'R\\u1ee7i ro & quan \\u0111i\\u1ec3m',followup:'K\\u1ebf ho\\u1ea1ch theo d\\u00f5i',quick_summary:'T\\u00f3m t\\u1eaft \\u0111i\\u1ec1u h\\u00e0nh',word:'Xu\\u1ea5t Word',notebooklm:'NotebookLM / PDF online'};")
sub(r"const phases=.*?;", "const phases=[['Pha 1 \\u2014 D\\u1eef li\\u1ec7u n\\u1ec1n',['news','technical','fundamental']],['Pha 2 \\u2014 Lu\\u1eadn \\u0111i\\u1ec3m \\u0111\\u1ea7u t\\u01b0',['scenario','bull_bear','risk','followup']],['Pha 3 \\u2014 K\\u1ebft xu\\u1ea5t',['quick_summary','word','notebooklm']]];")
sub(r"const scopeDefs=.*?;", "const scopeDefs=[{key:'data',name:'Data/Freshness',weight:15,desc:'Sync DB + freshness gate',sections:[]},{key:'news',name:'Grok News',weight:20,desc:'Tin t\\u1ee9c/catalyst c\\u00f3 t\\u00e1c \\u0111\\u1ed9ng',sections:['news']},{key:'analysis',name:'Analysis',weight:35,desc:'TA, fundamental, scenario, risk',sections:['technical','fundamental','scenario','bull_bear','risk','followup','quick_summary']},{key:'word',name:'Word',weight:20,desc:'DOCX upload xong m\\u1edbi \\u0111\\u1ea1t',sections:['word']},{key:'notebook',name:'NotebookLM',weight:10,desc:'Ph\\u1ee5 tr\\u1ee3, l\\u1ed7i kh\\u00f4ng ch\\u1eb7n Word',sections:['notebooklm']}];")
# Build marker
s = re.sub(r"const BUILD=.*?;", "const BUILD='20260723-final-yesterday-header-no-menu-labels';", s)
p.write_text(s, encoding='utf-8')
