from pathlib import Path
import re
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Hide the intro/title/status strip: icon, title, workflow description, job status pill.
css='.report-hero .hero-head{display:none!important}.report-hero{margin-top:18px}.tickerbar{margin-top:0}'
if '.report-hero .hero-head{display:none!important}' not in s:
    s=s.replace('</style>', css+'\n  </style>')
# Do not show stale "old job lost" state on load; clear old local job and return idle screen.
new_func="function renderLostJob(job){try{localStorage.removeItem('lh_model3_last_job');localStorage.removeItem('lh_model3_last_start')}catch(_){}if(timer)clearInterval(timer);if(uiTimer)clearInterval(uiTimer);current=null;lastJob=null;renderEmpty();$('runModel3').disabled=false}"
s=re.sub(r"function renderLostJob\(job\).*?\n\$\('ticker'\)\.addEventListener", new_func+"\n$('ticker').addEventListener", s, flags=re.S)
p.write_text(s,encoding='utf-8')
