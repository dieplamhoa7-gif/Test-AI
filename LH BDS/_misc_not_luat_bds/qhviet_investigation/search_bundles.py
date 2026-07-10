from pathlib import Path
terms=['web-v1-api','atob','btoa','Crypto','decrypt','encrypt','url_to_point','checkparcel','plan_detail','plan_info','parcel','thua','thửa','mat_do','tang_cao','HSSD','MĐXD','mật độ','tầng']
for p in Path(__file__).parent.glob('*.js'):
    txt=p.read_text(encoding='utf-8',errors='ignore')
    low=txt.lower()
    hits=[t for t in terms if t.lower() in low]
    if not hits: continue
    print('\nFILE',p.name,'hits',hits)
    for t in hits:
        i=low.find(t.lower())
        print('TERM',t,'@',i, txt[max(0,i-250):i+500].replace('\n',' ')[:1000])
