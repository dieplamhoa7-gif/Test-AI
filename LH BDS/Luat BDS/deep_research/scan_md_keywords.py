import pathlib
src=pathlib.Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\_converted_md_from_docx')
keys=['chấp thuận chủ trương đầu tư','đấu thầu lựa chọn nhà đầu tư','đấu giá quyền sử dụng đất','giao đất, cho thuê đất','chuyển mục đích sử dụng đất','giá đất','nghĩa vụ tài chính','bất động sản hình thành trong tương lai','công khai thông tin','bảo lãnh','cấp giấy chứng nhận','quy hoạch chi tiết','giấy phép xây dựng','nghiệm thu','đánh giá tác động môi trường','giấy phép môi trường']
for k in keys:
    print('\nKEY',k)
    hits=[]
    for f in src.glob('*.md'):
        txt=f.read_text(encoding='utf-8',errors='ignore')
        low=txt.lower(); kk=k.lower()
        if kk in low:
            pos=low.find(kk)
            start=max(0,txt.rfind('Điều ',0,pos))
            line=txt[start:start+320].replace('\n',' ')
            hits.append((f.name,line))
    for name,line in hits[:10]: print(name,line)
    print('hits',len(hits))
