from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\public_final_2026_07_11\quyhoach.html')
s=p.read_text(encoding='utf-8')
# Remove the empty GIS card from sourceBox output only.
start="block('2. GIS Xây dựng TP.HCM - nguồn đối chiếu'"
i=s.find(start)
if i<0: raise SystemExit('GIS block not found')
# Find balanced block(...) expression followed by comma.
depth=0; quote=None; esc=False; end=None
for k in range(i,len(s)):
    ch=s[k]
    if quote:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch==quote: quote=None
        continue
    if ch in "'\"`": quote=ch; continue
    if ch=='(': depth+=1
    elif ch==')':
        depth-=1
        if depth==0:
            end=k+1
            if end<len(s) and s[end]==',': end+=1
            break
if end is None: raise SystemExit('GIS block end not found')
s=s[:i]+s[end:]
# Renumber source headings.
s=s.replace("block('3. Guland - tách chỉ tiêu từ popup/map'","block('2. Guland - thông tin từ popup/map'")
s=s.replace("block('4. Google Maps / OSM - định vị'","block('3. Google Maps / OSM - định vị'")
# Truthful Guland status: full only when parsed indicators exist.
old="kv('Trạng thái',j.guland?.ok?'Đã đọc được':'Chưa đọc được: '+(j.guland?.error||'không có dữ liệu'))"
new="kv('Trạng thái',((gv?.parcel?.map_sheet||gv?.parcel?.land_code||(gv?.planning||[]).length)?'Đã bóc được chỉ tiêu':(j.guland?.ok?'Đọc được vị trí/popup, chưa bóc được chỉ tiêu':'Chưa đọc được: '+(j.guland?.error||'không có dữ liệu'))))"
s=s.replace(old,new)
p.write_text(s,encoding='utf-8',newline='\n')
print('patched truthful source cards')
