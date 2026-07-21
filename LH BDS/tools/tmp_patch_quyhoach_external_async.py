from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8')
s=s.replace("body:JSON.stringify({...c,includeGuland:false,includeQhViet:true})", "body:JSON.stringify({...c,includeGuland:false,includeQhViet:false})", 1)
s=s.replace("body:JSON.stringify({...c,includeGuland:true,includeQhViet:false})", "body:JSON.stringify({...c,includeGuland:true,includeQhViet:true})", 1)
p.write_text(s,encoding='utf-8')
print('initial primary only; external async both')
