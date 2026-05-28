from pathlib import Path
p = Path('firebase_public/stocks-candle.html')
s = p.read_text(encoding='utf-8')
if 'CANDLE TEST PAGE - Trendline bám theo nến' not in s:
    s = s.replace('body {', 'body {\n      outline: 4px solid rgba(78,240,192,.28);', 1)
    banner = '<div style="margin:0 0 14px; padding:14px 16px; border-radius:18px; border:2px solid rgba(78,240,192,.45); background:linear-gradient(135deg, rgba(78,240,192,.18), rgba(100,181,255,.12)); color:#c9fff1; font-size:15px; font-weight:900; text-transform:uppercase; letter-spacing:.04em;">CANDLE TEST PAGE - Trendline bám theo nến (MWG D thử nghiệm)</div>'
    s = s.replace('<div class="shell">', '<div class="shell">' + banner, 1)
    s = s.replace('INVESTMENT INFORMATION', 'CANDLE TEST • INVESTMENT INFORMATION', 1)
p.write_text(s, encoding='utf-8')
print('patched', 'CANDLE TEST PAGE - Trendline bám theo nến' in s)
