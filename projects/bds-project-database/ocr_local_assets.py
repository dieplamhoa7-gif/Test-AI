import json,re,sys
from pathlib import Path
from PIL import Image
import pytesseract
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
imgs=list(BASE.glob('*.png'))+list(BASE.glob('*.jpg'))+list(BASE.glob('*.jpeg'))
outdir=BASE/'ocr_outputs'; outdir.mkdir(exist_ok=True)
rows=[]
for img in imgs:
    try:
        im=Image.open(img)
        text=pytesseract.image_to_string(im, lang='vie+eng', config='--psm 6')
    except Exception as e:
        text=f'OCR_ERROR: {e}'
    (outdir/(img.stem+'.txt')).write_text(text,encoding='utf-8')
    rows.append({'file':img.name,'chars':len(text),'head':re.sub(r'\s+',' ',text[:300])})
print(json.dumps(rows,ensure_ascii=False,indent=2))
