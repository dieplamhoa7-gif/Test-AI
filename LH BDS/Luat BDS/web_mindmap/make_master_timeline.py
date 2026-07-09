import json, pathlib
out=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap")
d=json.loads((out/'process_mindmap_data.json').read_text(encoding='utf-8'))
lines=[]
lines.append('# Master timeline phát triển dự án BĐS')
lines.append('')
lines.append(f"Nguồn: {d['doc_count']} văn bản markdown trong `{d['source_dir']}`")
lines.append('')
lines.append('## Timeline tổng thể')
for t in d['master_timeline']:
    lines.append(f"### {t['phase']} — {t['step']}")
    lines.append(f"- Output: {t['outputs']}")
    lines.append(f"- Phụ thuộc: {t['depends']}")
    lines.append('')
lines.append('## Checklist theo bước kèm trích dẫn tiêu biểu')
for s in d['process']:
    lines.append(f"### {s['name']}")
    lines.append(f"- Cần có: {s['need']}")
    lines.append('- Trích dẫn/nguồn tiêu biểu:')
    for e in s['evidence'][:8]:
        lines.append(f"  - **{e['article']}** — `{e['source_file']}`")
        lines.append(f"    - Tóm tắt: {e['summary']}")
    lines.append('')
(out/'MASTER_TIMELINE.md').write_text('\n'.join(lines),encoding='utf-8')
print(out/'MASTER_TIMELINE.md')
