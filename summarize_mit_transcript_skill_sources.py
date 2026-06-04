import json
from pathlib import Path
s=json.loads(Path('mit_18_642_transcripts_summary.json').read_text(encoding='utf-8'))
lines=['# MIT 18.642 transcript source audit','', 'Tiểu đệ đã xử lý transcript cho các video public sau. Đây là cơ sở tạo skill và giáo trình tiếng Việt.', '']
for item in s:
    status='OK' if item.get('ok') else 'FAIL'
    lines.append(f"{item['index']:02d}. [{status}] {item['title']} — `{item['id']}` — chars: {item.get('chars')} — `{item.get('path')}`")
lines.append('')
lines.append(f"Total public transcript OK: {sum(1 for x in s if x.get('ok'))}/{len(s)}")
lines.append('')
lines.append('Ghi chú: đây là đọc transcript, không phải xem từng khung hình/slide video.')
Path('reports/MIT_18_642_transcript_source_audit.md').write_text('\n'.join(lines),encoding='utf-8')
print('reports/MIT_18_642_transcript_source_audit.md')
