import json
from pathlib import Path
from datetime import datetime
import pandas as pd

base = Path(__file__).resolve().parent
files = sorted(base.glob('part_*_manual_records.json'))
parts = []
rows=[]
fin_rows=[]
skip_rows=[]
for fp in files:
    d=json.load(open(fp,encoding='utf-8'))
    part=d.get('part')
    if part is not None:
        parts.append(int(part))
    for r in d.get('records',[]):
        rows.append({
            'part': part,
            'id': r.get('id',''),
            'decision': r.get('decision',''),
            'project_name': r.get('project_name',''),
            'report_date': r.get('report_date',''),
            'source_chunks': ', '.join(r.get('source_chunks',[])),
            'source_file': r.get('source_file',''),
            'sender': r.get('sender',''),
            'location': r.get('location',''),
            'map_url': r.get('map_url',''),
            'scale': r.get('scale',''),
            'legal_planning': r.get('legal_planning',''),
            'business_notes': r.get('business_notes',''),
            'excerpt': r.get('excerpt','')
        })
        for fi in r.get('financial_items',[]) or []:
            fin_rows.append({
                'part': part,
                'record_id': r.get('id',''),
                'project_name': r.get('project_name',''),
                'label': fi.get('label',''),
                'value': fi.get('value',''),
                'source_chunk': fi.get('source_chunk','')
            })
    for s in d.get('review_or_skip',[]) or []:
        skip_rows.append({'part':part,'chunk_id':s.get('chunk_id',''),'reason':s.get('reason','')})

part_label = f'{min(parts):02d}_{max(parts):02d}' if parts else 'none'
out = base / f'manual_records_parts_{part_label}_view_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as writer:
    pd.DataFrame(rows).to_excel(writer, sheet_name='records', index=False)
    pd.DataFrame(fin_rows).to_excel(writer, sheet_name='financial_items', index=False)
    pd.DataFrame(skip_rows).to_excel(writer, sheet_name='review_skip', index=False)
    summary = pd.DataFrame([
        {'metric':'parts_included','value': ', '.join(str(json.load(open(f,encoding='utf-8')).get('part')) for f in files)},
        {'metric':'record_count','value': len(rows)},
        {'metric':'financial_item_count','value': len(fin_rows)},
        {'metric':'review_skip_count','value': len(skip_rows)},
        {'metric':'generated_at','value': datetime.now().isoformat(timespec='seconds')},
    ])
    summary.to_excel(writer, sheet_name='summary', index=False)
    for ws in writer.book.worksheets:
        ws.freeze_panes = 'A2'
        for col in ws.columns:
            max_len = 0
            letter = col[0].column_letter
            for cell in col[:80]:
                val = '' if cell.value is None else str(cell.value)
                max_len = max(max_len, min(len(val), 80))
            ws.column_dimensions[letter].width = max(10, min(max_len + 2, 60))
print(out)
