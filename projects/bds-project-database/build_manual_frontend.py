import json
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
MANUAL = BASE / 'manual_10parts'
WEB = BASE / 'web'

AREA_RE = re.compile(r'(\d+[\d\.,]*)\s*(ha|m2|m²)', re.I)
FLOOR_RE = re.compile(r'(?:tầng cao|cao tối đa|cao|tối đa|quy mô)[^.;\n]{0,35}?(\d{1,3})\s*tầng', re.I)
DENSITY_RE = re.compile(r'(?:mđxd|mật độ xây dựng|MĐXD)\s*[:=]?\s*([\d\.,]+\s*%?)', re.I)
FAR_RE = re.compile(r'(?:hssdđ|hs sdđ|hệ số sdđ|hssd|far)\s*[:=]?\s*([\d\.,]+\s*(?:lần)?)', re.I)
POP_RE = re.compile(r'(?:dân số)\s*[:=]?\s*([\d\.,]+\s*(?:người|dân)?)', re.I)


def first_match(rx, text):
    m = rx.search(text or '')
    return m.group(1).strip() if m else ''


def collect_matches(rx, text, limit=6):
    vals = []
    for m in rx.finditer(text or ''):
        val = ' '.join(g for g in m.groups() if g).strip()
        if val and val not in vals:
            vals.append(val)
    return vals[:limit]


def split_legal(text):
    land_bits = []
    project_bits = []
    for seg in re.split(r'[;\n]+', text or ''):
        s = seg.strip()
        if not s:
            continue
        low = s.lower()
        if any(k in low for k in ['gcn', 'qsdđ', 'qsd', 'đất ', 'odt', 'cln', 'tmdv', 'skc', 'thuê đất', 'giao đất', 'chuyển mục đích', 'tsdđ']):
            land_bits.append(s)
        if any(k in low for k in ['ctđt', 'chủ trương', '1/500', '1/2000', 'gpxd', 'pháp lý đầu tư', 'đấu thầu', 'đấu giá', 'phê duyệt', 'quy hoạch', 'bàn giao', 'gpmb']):
            project_bits.append(s)
    return '； '.join(land_bits[:8]), '； '.join(project_bits[:8])


def normalize_record(r, part):
    text = '\n'.join(str(r.get(k, '')) for k in ['scale', 'legal_planning', 'business_notes', 'excerpt'])
    land_legal, project_legal = split_legal(r.get('legal_planning', ''))
    fin_items = r.get('financial_items') or []
    return {
        'id': r.get('id', ''),
        'part': part,
        'decision': r.get('decision', ''),
        'project_name': r.get('project_name', ''),
        'report_date': r.get('report_date', ''),
        'source_chunks': r.get('source_chunks', []),
        'source_file': r.get('source_file', ''),
        'sender': r.get('sender', ''),
        'location': r.get('location', ''),
        'map_url': r.get('map_url', ''),
        'scale_raw': r.get('scale', ''),
        'planning': {
            'floors': first_match(FLOOR_RE, text),
            'density': first_match(DENSITY_RE, text),
            'far': first_match(FAR_RE, text),
            'population': first_match(POP_RE, text),
            'area_mentions': collect_matches(AREA_RE, text),
            'raw': r.get('scale', '')
        },
        'legal': {
            'land': land_legal,
            'project': project_legal,
            'raw': r.get('legal_planning', '')
        },
        'financial_items': fin_items,
        'business_notes': r.get('business_notes', ''),
        'excerpt': r.get('excerpt', '')
    }

records = []
review = []
summary = []
for fp in sorted(MANUAL.glob('part_*_manual_records.json')):
    d = json.loads(fp.read_text(encoding='utf-8'))
    part = int(d.get('part') or re.search(r'part_(\d+)', fp.name).group(1))
    recs = [normalize_record(r, part) for r in d.get('records', [])]
    skips = [{**s, 'part': part} for s in d.get('review_or_skip', [])]
    records.extend(recs)
    review.extend(skips)
    summary.append({
        'part': part,
        'records': len(recs),
        'review': len(skips),
        'financial': sum(1 for r in recs if r.get('financial_items')),
        'duplicates': sum(1 for r in recs if 'duplicate' in (r.get('decision') or '').lower()),
    })

final = {
    'generated_at': datetime.now().isoformat(timespec='seconds'),
    'records': records,
    'review': review,
    'summary': summary,
    'totals': {
        'records': len(records),
        'review': len(review),
        'financial_records': sum(1 for r in records if r.get('financial_items')),
        'financial_items': sum(len(r.get('financial_items') or []) for r in records),
        'duplicates': sum(1 for r in records if 'duplicate' in (r.get('decision') or '').lower())
    }
}
(MANUAL / 'manual_records_frontend_database.json').write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding='utf-8')
(WEB / 'manual_records_frontend_database.js').write_text('window.MANUAL_RECORDS_FRONTEND_DB = ' + json.dumps(final, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(json.dumps(final['totals'], ensure_ascii=False))
