from pathlib import Path
p = Path('firebase_public/wyckoff-board.html')
s = p.read_text(encoding='utf-8', errors='replace')
repls = [
    ('PHAN TICH C?U TRUC - WYCKOFF BOARD', 'WYCKOFF BOARD STRUCTURE MAP'),
    ('Frontend m?i theo style b?ng ph�n t�ch � d�ng d? li?u Wyckoff c?a m�nh � MWG gi? logic cu, ma kh�c d�ng full timeframe', 'Full-history Wyckoff board - long data from 2023 - overlay index remapped to current chart'),
    ('Ma <select id="symbolSel"></select>', 'Symbol <select id="symbolSel"></select>'),
    ('K?t lu?n', 'Verdict'),
    ('Tr?ng th�i hi?n t?i', 'Current Status'),
    ('K?ch b?n & h�nh d?ng', 'Scenario & Action'),
    ('SC / AR / ST / Spring / Test Spring b�m v�o n?n th?t n?u d? li?u event c�. V�ng support 6M + support 1Y du?c gi? c? d?nh.', 'SC / AR / ST / Spring / Test Spring anchor to real candles when event data exists. Support 6M + support 1Y stay fixed.'),
    ('Dang ch? breakout th?t kh?i range d? x�c nh?n hu?ng ti?p theo.', 'Waiting for real breakout from the range to confirm the next move.'),
    ('MWG gi? logic cu D?i ka da ung', 'MWG keeps approved legacy logic'),
    ('C�c ma kh�c da chuy?n sang template gi?ng MWG', 'Other symbols use MWG-like template'),
]
for a, b in repls:
    s = s.replace(a, b)
p.write_text(s, encoding='utf-8')
print('ascii-safe rewrite done')
