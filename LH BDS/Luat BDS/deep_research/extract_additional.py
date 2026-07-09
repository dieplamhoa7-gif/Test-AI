import zipfile, re, pathlib, json, subprocess, os, sys
from xml.etree import ElementTree as ET
add=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\Additional")
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\deep_research\additional_text")
out.mkdir(parents=True,exist_ok=True)

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def docx_text(p):
    with zipfile.ZipFile(p) as z:
        xml=z.read('word/document.xml')
    root=ET.fromstring(xml)
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paras=[]
    for para in root.findall('.//w:p',ns):
        texts=[t.text or '' for t in para.findall('.//w:t',ns)]
        if texts: paras.append(''.join(texts))
    return '\n'.join(paras)

def antiword_text(p):
    try:
        r=subprocess.run(['antiword',str(p)],capture_output=True,text=True,timeout=60)
        if r.returncode==0 and r.stdout.strip(): return r.stdout
    except Exception: pass
    # fallback: read binary, extract ascii/utf16-ish chunks
    data=p.read_bytes()
    for enc in ['utf-16le','utf-8','cp1258','latin1']:
        try:
            s=data.decode(enc,errors='ignore')
            if len(re.findall(r'[A-Za-zÀ-ỹ]{3,}',s))>50: return s
        except Exception: pass
    return ''
items=[]
for p in sorted(add.iterdir()):
    if not p.is_file(): continue
    if p.suffix.lower()=='.docx': text=docx_text(p)
    elif p.suffix.lower()=='.doc': text=antiword_text(p)
    else: text=p.read_text(encoding='utf-8',errors='ignore')
    txt_path=out/(p.stem+'.txt')
    txt_path.write_text(text,encoding='utf-8',errors='ignore')
    lines=[clean(x) for x in text.splitlines() if clean(x)]
    title=next((x for x in lines[:80] if re.search(r'^(LUẬT|NGHỊ ĐỊNH|THÔNG TƯ|QUYẾT ĐỊNH|KẾT LUẬN|CÔNG VĂN)',x,re.I)), lines[0] if lines else p.name)
    items.append({'file':p.name,'text_file':str(txt_path),'chars':len(text),'title':title[:300],'head':lines[:12]})
(out/'additional_manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(items,ensure_ascii=False,indent=2)[:4000])
