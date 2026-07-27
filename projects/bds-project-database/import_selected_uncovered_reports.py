import json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent; MAN=BASE/'manual_10parts'
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
selected={
 72:'Dự án 43ha Tân Phú, Bình Dương / Kim Oanh',
 88:'Dự án Võ Văn Kiệt - cập nhật gộp 2 lô',
 99:'Dự án 5,1ha Kinh Đô / lô Quốc Lộ 13 Hiệp Bình Phước',
 361:'Dự án đấu giá 77ha Long Thành, Đồng Nai',
 529:'Dự án 1,6ha Phan Văn Hớn - độ nhạy LNTT/TMĐT',
 541:'Dự án 1,6ha Phan Văn Hớn - độ nhạy LNTT/TMĐT',
 663:'Holiday Beach Đà Nẵng - phương án vận hành khách sạn tạm thời',
 686:'Khu đất nghiên cứu Tam Hải và Tam Hòa, Núi Thành, Quảng Nam',
 687:'Dự án 2,3ha Bình Điền - Bình Chánh',
 803:'So sánh Diamond Island Q9 / Long Phước / Swan Park',
 995:'Quỹ đất 168ha Phong Phú, Bình Chánh',
}
# chunks intentionally not imported: 45 continuation/no project clear; 167/168 duplicated continuation; 538/585 duplicates of Phan Văn Hớn; 657 image-only PGK already represented by 654/661; 771 market general.
def part_for(i): return (i-1)//100+1
def compact(s): return re.sub(r'\s+',' ',s or '').strip()
added=[]
for part in sorted(set(part_for(i) for i in selected)):
    fp=MAN/f'part_{part:02d}_manual_records.json'; d=json.loads(fp.read_text(encoding='utf-8'))
    existing_ids={r.get('id') for r in d.get('records',[])}; n=1
    while f'M{part:02d}-SEL{n:03d}' in existing_ids: n+=1
    existing_chunks={str(c) for r in d.get('records',[]) for c in r.get('source_chunks',[])}
    for i,name in selected.items():
        if part_for(i)!=part or str(i) in existing_chunks: continue
        rid=f'M{part:02d}-SEL{n:03d}'; n+=1; ch=raw[i-1]; txt=compact(ch.get('text') or '')
        d.setdefault('records',[]).append({'id':rid,'source_chunks':[str(i)],'decision':'selected_uncovered_report_import','project_name':name,'report_date':ch.get('report_date',''),'source_file':ch.get('source_file',f'batch_{i:03d}.txt'),'sender':ch.get('sender',''),'location':'','map_url':'','scale':'','legal_planning':'','business_notes':'Selected from uncovered finance/report audit; verify manually.','financial_items':[],'excerpt':txt[:900]})
        added.append((part,rid,i,name))
    fp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
out=BASE/'reports'/'manual_selected_uncovered_import.md'
out.write_text('# Selected uncovered report import\n\n'+'\n'.join(f'- Part {p} · {rid} · chunk {i} · {name}' for p,rid,i,name in added),encoding='utf-8')
print({'added':len(added),'report':str(out)})
