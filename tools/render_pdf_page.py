import sys
from pathlib import Path
import fitz

pdf = Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\2026_06_01_TTr_16378_SNNMT_To_trinh_va_phu_luc_he_so_K1_hop_nhat.pdf')
out_dir = Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\exports\k1_evidence_pages')
out_dir.mkdir(parents=True, exist_ok=True)
page_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
out = out_dir / f'k1_page_{page_no}.png'
doc = fitz.open(pdf)
page = doc.load_page(page_no - 1)
pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
pix.save(out)
print(out)
