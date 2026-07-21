from pathlib import Path
import subprocess
repo=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace')
project=repo/'LH BDS'
out=project/'public_final_2026_07_11'/'quyhoach.html'
git_path='LH BDS/public_final_2026_07_11/quyhoach.html'
# This commit predates the PowerShell re-encoding corruption and contains valid UTF-8 Vietnamese.
data=subprocess.check_output(['git','show',f'5e18588e9:{git_path}'],cwd=repo)
text=data.decode('utf-8-sig')
# Keep QHViet disabled as requested.
text=text.replace('includeGuland:true,includeQhViet:true','includeGuland:true,includeQhViet:false')
text=text.replace('includeGuland:false,includeQhViet:true','includeGuland:false,includeQhViet:false')
text=text.replace('const gis=j.gisxaydung||j.qhviet||{};','const gis=j.gisxaydung||{};')
# Live tunnel fallbacks, config remains first candidate.
import json
cfg=json.loads((project/'public_final_2026_07_11'/'api-config.json').read_text(encoding='utf-8-sig'))
qh=cfg.get('qhApiBase','')
text=text.replace("const API_FALLBACKS_QH=['https://closely-hearts-locking-funny.trycloudflare.com'];",f"const API_FALLBACKS_QH=['{qh}','https://peninsula-bull-impression-concentration.trycloudflare.com','https://bicycle-shelf-ellis-prevention.trycloudflare.com','https://gibson-elderly-introduction-hazards.trycloudflare.com'];")
# Make Guland request enabled and display direct parsed fields/raw text (clean UTF-8 source).
text=text.replace("body:JSON.stringify({...c,includeGuland:false,includeQhViet:false})","body:JSON.stringify({...c,includeGuland:true,includeQhViet:false})",1)
# Remove missing cleaner script: page is now genuinely UTF-8.
text=text.replace('<script src="mojibake-cleaner.js"></script>','')
out.write_text(text,encoding='utf-8',newline='\n')
print('restored',out,'bytes',out.stat().st_size,'qh',qh)
print('bad markers',sum(text.count(x) for x in ['Ã','Â','á»','Ä‘','�']))
