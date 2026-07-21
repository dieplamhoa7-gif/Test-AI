from pathlib import Path
import re, json, hashlib
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
bdir=base/'teams_batches'
files=sorted(bdir.glob('batch_*.txt'))
seen=set(); chunks=[]
for f in files:
    txt=f.read_text(encoding='utf-8',errors='ignore')
    # Split by date headings / message boundaries but keep broad context
    parts=re.split(r'(?=\n(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), |\n(?:P\.ĐT|Phòng|Báo cáo|Dạ|Admin 01|Hanh T|Khoa L|Dung N|Huy M|Tai L|Thao L|Tèo)\b)', txt)
    for p in parts:
        p=p.strip()
        if len(p)<120: continue
        if not re.search(r'(dự án|DA\b|BĐS|FS\b|ha\b|m2|m²|tỷ|giá|quy hoạch|pháp lý|LNTT|IRR|NPV|Maps|maps\.app|google\.com)', p, re.I):
            continue
        key=hashlib.sha1(re.sub(r'\s+',' ',p[:2000]).encode('utf-8','ignore')).hexdigest()
        if key in seen: continue
        seen.add(key); chunks.append({'source_file':f.name,'text':p})
# Filter near-duplicates by exact normalized start
out=[]; starts=set()
for c in chunks:
    st=re.sub(r'\s+',' ',c['text'][:500]).lower()
    if st in starts: continue
    starts.add(st); out.append(c)
(base/'teams_candidate_chunks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Candidate BĐS chunks from full Teams scroll\n']
for i,c in enumerate(out,1):
    md.append(f'\n## Chunk {i} — {c["source_file"]}\n\n```text\n{c["text"][:6000]}\n```\n')
(base/'teams_candidate_chunks.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'files':len(files),'chunks':len(out)},ensure_ascii=False))
