import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DATA = Path('data/news_cache.json')
OUT_DIR = Path('firebase_public/data')
REPORT_DIR = Path('firebase_public/reports')
TAG_RE = re.compile(r'<[^>]+>')


def parse_dt(raw):
    raw = str(raw or '').strip()
    for fmt in ('%a, %d %b %y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(raw.replace('GMT+7','+0700'), fmt)
        except Exception:
            pass
    return None


def clean(text, limit=500):
    text = TAG_RE.sub(' ', str(text or ''))
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:limit]


def month_key(item):
    dt = parse_dt(item.get('published_at') or item.get('fetched_at'))
    return dt.strftime('%Y%m') if dt else 'unknown'


def main():
    items = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else []
    if isinstance(items, dict):
        items = items.get('items', [])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    buckets = defaultdict(list)
    for item in items:
        buckets[month_key(item)].append(item)
    archive_index = []
    for key, rows in sorted(buckets.items(), reverse=True):
        if key == 'unknown':
            continue
        path = OUT_DIR / f'news_archive_{key}.json'
        payload = {'month': key, 'count': len(rows), 'items': rows}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        archive_index.append({'month': key, 'count': len(rows), 'path': f'/data/news_archive_{key}.json'})
    (OUT_DIR / 'news_archive_index.json').write_text(json.dumps({'items': archive_index}, ensure_ascii=False, indent=2), encoding='utf-8')

    latest = items[:50]
    cats = Counter(clean(x.get('category') or 'Khác', 80) for x in latest)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = [
        '# LH Investment - Báo cáo tin tức nhanh',
        '',
        f'Cập nhật: {now}',
        f'Tổng số tin trong cache: {len(items)}',
        '',
        '## Phân bổ nhóm tin trong 50 tin mới nhất',
    ]
    for cat, count in cats.most_common():
        lines.append(f'- {cat}: {count}')
    lines += ['', '## Top 20 tin mới nhất']
    for i, item in enumerate(items[:20], 1):
        title = clean(item.get('title'), 240)
        pub = clean(item.get('published_at') or item.get('fetched_at'), 80)
        src = clean(item.get('source'), 80)
        summary = clean(item.get('summaryAi') or item.get('summary') or item.get('snippet'), 500)
        url = clean(item.get('url'), 300)
        lines += ['', f'### {i}. {title}', f'- Thời gian: {pub}', f'- Nguồn: {src}', f'- Tóm tắt: {summary}', f'- Link: {url}']
    md = '\n'.join(lines) + '\n'
    (REPORT_DIR / 'news_report_latest.md').write_text(md, encoding='utf-8')
    html = '<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>LH Investment News Report</title><style>body{font-family:Arial,sans-serif;max-width:960px;margin:32px auto;line-height:1.6;padding:0 16px}h1,h2,h3{color:#123}li{margin:6px 0}code{background:#eee;padding:2px 4px}</style></head><body>'
    for line in lines:
        if line.startswith('# '): html += f'<h1>{clean(line[2:],1000)}</h1>'
        elif line.startswith('## '): html += f'<h2>{clean(line[3:],1000)}</h2>'
        elif line.startswith('### '): html += f'<h3>{clean(line[4:],1000)}</h3>'
        elif line.startswith('- '): html += f'<p>• {clean(line[2:],1000)}</p>'
        elif not line: html += '<br>'
        else: html += f'<p>{clean(line,1000)}</p>'
    html += '</body></html>'
    (REPORT_DIR / 'news_report_latest.html').write_text(html, encoding='utf-8')
    print(f'archives={len(archive_index)} items={len(items)} report=reports/news_report_latest.html')


if __name__ == '__main__':
    main()
