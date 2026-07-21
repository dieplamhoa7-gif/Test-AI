import json, re
from pathlib import Path
base=Path(__file__).parent
p=base/'teams_candidate_chunks.json'
data=json.load(open(p,encoding='utf-8'))
keys=re.compile(r'(dự án|khu đất|quỹ đất|FS|IRR|NPV|doanh thu|tổng mức đầu tư|giá chào|giá bán|quy hoạch|pháp lý|diện tích|ha|m2|maps\.app|goo\.gl/maps|cao tầng|khu công nghiệp|resort|khách sạn|văn phòng)',re.I)
out=[]
for idx,c in enumerate(data, start=1):
    if idx<=177: continue
    txt=c.get('text','')
    if keys.search(txt):
        clean=re.sub(r'\s+',' ',txt).strip()
        out.append(f"### CHUNK {idx}\n{clean[:2200]}\n")
(base/'new_chunks_178_plus_review.md').write_text('\n'.join(out),encoding='utf-8')
print({'candidate_review_chunks':len(out),'out':str(base/'new_chunks_178_plus_review.md')})
