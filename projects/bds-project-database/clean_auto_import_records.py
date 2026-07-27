import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
MAN=BASE/'manual_10parts'
renames={
 'M01-AUTO001':'Cát Lái - Sky Habitat / H2-02',
 'M01-AUTO002':'Diamond Garden, Đào Trí, Phú Thuận, TP.HCM',
 'M01-AUTO003':'Dự án Trần Đức 1, Thuận Giao, Bình Dương',
 'M01-AUTO004':'Lô đất khách sạn cạnh TMS - 290 Võ Nguyên Giáp',
 'M01-AUTO005':'Cát Lái - Sky Habitat / H2-02',
 'M01-AUTO006':'Cát Lái - Sky Habitat / H2-02',
 'M01-AUTO007':'Cát Lái - Sky Habitat / H2-02',
 'M04-AUTO001':'Phú Gia Khiêm / PGK - phương án thấp tầng',
 'M04-AUTO002':'Phú Gia Khiêm / PGK - phương án thấp tầng',
 'M06-AUTO001':'Dự án 31 Trần Não - cao tầng',
 'M06-AUTO002':'Chung cư Phượng Hoàng, Dĩ An, Bình Dương',
 'M07-AUTO001':'Phú Gia Khiêm / PGK',
 'M07-AUTO002':'Phú Gia Khiêm / PGK - phương án 900 tỷ',
 'M07-AUTO003':'Phú Gia Khiêm / PGK',
 'M10-AUTO001':'50ha Vĩnh Tường - Yên Lạc, Vĩnh Phúc',
}
# remove exact duplicate chunks 93 (same as 91-ish) and 353 (same as 352-ish) by turning into adjacent chunks on retained records
remove_ids={'M01-AUTO007','M04-AUTO002'}
for fp in MAN.glob('part_*_manual_records.json'):
    d=json.loads(fp.read_text(encoding='utf-8'))
    records=[]
    retained={}
    for r in d.get('records',[]):
        rid=r.get('id')
        if rid in renames: r['project_name']=renames[rid]
        if rid in remove_ids: continue
        records.append(r); retained[rid]=r
    # merge removed chunks into closest retained duplicate source chunks for audit completeness
    if fp.name=='part_01_manual_records.json':
        for r in records:
            if r.get('id')=='M01-AUTO006' and '93' not in r.get('source_chunks',[]): r['source_chunks'].append('93')
    if fp.name=='part_04_manual_records.json':
        for r in records:
            if r.get('id')=='M04-AUTO001' and '353' not in r.get('source_chunks',[]): r['source_chunks'].append('353')
    d['records']=records
    fp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print({'renamed':len(renames),'removed_duplicates':len(remove_ids)})
