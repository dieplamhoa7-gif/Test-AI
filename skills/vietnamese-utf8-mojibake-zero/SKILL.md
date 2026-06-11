# Vietnamese UTF-8 / Mojibake Zero Skill

## Purpose

Use this skill for **every task that reads, writes, patches, deploys, renders, scrapes, exports, or displays Vietnamese text with diacritics**.

Goal: **avoid mojibake and UTF-8 corruption absolutely**.

Examples of forbidden broken text:

- `B�o c�o`
- `T?o b�o c�o`
- `D? li?u`
- `Phư�ng`
- `Th�nh phố`
- `Qu�n`
- `Nghia v?`
- `Quy ho?ch`
- `Dang x? ly`
- `ThÃ nh`
- `phá»‘`
- `Bá»™`
- any visible `�`

## When to Use

Use before any action involving:

- Vietnamese frontend HTML/CSS/JS.
- Vietnamese backend prompts, progress messages, logs, JSON labels, report text.
- Data transfer from AI/search/scrapers/geocoders into frontend.
- Firebase deploys or public web updates.
- PDF/HTML/NotebookLM report exports.
- Search results from Vietnamese real estate websites.
- Any script that touches Vietnamese strings.

## Hard Rules

### 1. Never patch Vietnamese strings through inline shell one-liners

Do **not** use inline PowerShell/Node/Python command strings to write Vietnamese text, especially with `-Command`, `node -e`, or long escaped strings.

Bad:

```powershell
powershell -Command "(Get-Content file.html) -replace 'Bao cao','Báo cáo' | Set-Content file.html"
```

Bad:

```bash
node -e "fs.writeFileSync('x.html','Báo cáo ...')"
```

Use instead:

- OpenClaw `write` tool with full UTF-8 file content.
- A checked-in `.js` / `.py` patch script saved as UTF-8 first, then run it.
- Exact `edit` tool replacements when both old/new text are known and short.

### 2. Always keep source files UTF-8

For every Vietnamese file:

- HTML must include:

```html
<meta charset="utf-8">
```

- Python writes must use:

```python
Path(path).write_text(text, encoding='utf-8')
open(path, 'w', encoding='utf-8')
json.dumps(obj, ensure_ascii=False)
```

- Node writes must use:

```js
fs.writeFileSync(path, text, 'utf8')
JSON.stringify(obj)
```

### 3. Clean data, not just UI

Mojibake can enter through AI/search/browser/geocoder data. Fix at all layers:

1. backend data cleaner,
2. proxy/API JSON cleaner,
3. frontend render cleaner,
4. export/PDF cleaner.

Do not assume the frontend file is the only source of broken text.

### 4. Never deploy without UTF-8 checks

Before Firebase/public deploy involving Vietnamese frontend, run:

```powershell
node tools_utf8_guard.js firebase_nvtc_public\rd.html firebase_nvtc_public\index.html firebase_nvtc_public\nvtc.html firebase_nvtc_public\quyhoach.html
```

Also run syntax checks when relevant:

```powershell
node tmp_check_rd_syntax.js
node --check nvtc_9router_proxy.js
py -m py_compile BDS_Ver2_9router_test\web_valuation_api.py
```

If any guard fails, **do not deploy**.

### 5. Extend the guard when a new broken pattern appears

If the user reports a new mojibake pattern, add it to the cleaner/guard immediately.

Known patterns to catch:

```text
�
ThÃ
phá»
Bá»
Ä
???
T?o
D? li?u
B?o
Dang
HoA
Phư�ng
Th�nh phố
Qu�n
gi�
d� án
vị tr�
tiện �ch
hạ t�ng
ph�n tích
kiểm ch�ng
ngu�n
đề xu�t
trung b�nh
đã g�m VAT
so s�nh
```

## Recommended Cleaners

### JavaScript frontend render cleaner

Use a small `cleanText()` before escaping/rendering user-visible dynamic strings:

```js
function cleanText(x) {
  return String(x || '')
    .replaceAll('Phư\uFFFDng', 'Phường')
    .replaceAll('phư\uFFFDng', 'phường')
    .replaceAll('Qu\uFFFDn', 'Quận')
    .replaceAll('Th\uFFFDnh phố', 'Thành phố')
    .replaceAll('gi\uFFFD', 'giá')
    .replaceAll('d\uFFFD án', 'dự án')
    .replaceAll('vị tr\uFFFD', 'vị trí')
    .replaceAll('tiện \uFFFDch', 'tiện ích')
    .replaceAll('hạ t\uFFFDng', 'hạ tầng')
    .replaceAll('ph\uFFFDn tích', 'phân tích')
    .replaceAll('kiểm ch\uFFFDng', 'kiểm chứng')
    .replaceAll('ngu\uFFFDn', 'nguồn')
    .replaceAll('đề xu\uFFFDt', 'đề xuất')
    .replaceAll('trung b\uFFFDnh', 'trung bình')
    .replaceAll('đã g\uFFFDm VAT', 'đã gồm VAT')
    .replaceAll('so s\uFFFDnh', 'so sánh');
}
```

Then:

```js
function esc(x) {
  return cleanText(x).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[m]));
}
```

### Python backend cleaner

Use `ftfy` when available plus explicit replacements:

```python
from ftfy import fix_text

def fix_vn_text(x):
    if not isinstance(x, str):
        return x
    try:
        x = fix_text(x)
    except Exception:
        pass
    replacements = {
        'Phư�ng': 'Phường',
        'Th�nh phố': 'Thành phố',
        'Qu�n': 'Quận',
        'gi�': 'giá',
        'd� án': 'dự án',
        'vị tr�': 'vị trí',
        'tiện �ch': 'tiện ích',
        'hạ t�ng': 'hạ tầng',
        'ph�n tích': 'phân tích',
        'kiểm ch�ng': 'kiểm chứng',
        'ngu�n': 'nguồn',
        'đề xu�t': 'đề xuất',
        'trung b�nh': 'trung bình',
        'đã g�m VAT': 'đã gồm VAT',
        'so s�nh': 'so sánh',
    }
    for a, b in replacements.items():
        x = x.replace(a, b)
    return x
```

Clean nested JSON:

```python
def clean_for_json(obj):
    if isinstance(obj, str):
        return fix_vn_text(obj)
    if isinstance(obj, list):
        return [clean_for_json(x) for x in obj]
    if isinstance(obj, dict):
        return {clean_for_json(k): clean_for_json(v) for k, v in obj.items()}
    return obj
```

## Final Checklist Before Replying "Done"

- [ ] No visible `�`, `?`-broken Vietnamese, or mojibake in changed files.
- [ ] Dynamic backend/proxy data is cleaned, not only static frontend.
- [ ] Syntax checks pass.
- [ ] UTF-8 guard passes.
- [ ] Public fetch check passes after deploy if deployed.
- [ ] Snapshot/backup copy updated if this project uses one.

## Tone for User Updates

If a UTF-8/mojibake issue is found, be direct:

> Anh đúng, lỗi không nằm ở giao diện tĩnh mà nằm ở data động từ AI/search/backend. Em đã vá ở backend + proxy + frontend và chạy guard trước deploy.

Do not claim it is fixed until checks pass.
