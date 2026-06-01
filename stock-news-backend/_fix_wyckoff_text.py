from pathlib import Path
p=Path('firebase_public/wyckoff-board.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Replace broken visible header/sidebar text with ASCII-safe labels.
repls = {
    'PHAN TICH C?U TRUC - WYCKOFF BOARD': 'WYCKOFF BOARD STRUCTURE MAP',
    'Frontend m?i theo style b?ng ph�n t�ch � d�ng d? li?u Wyckoff c?a m�nh � MWG gi? logic cu, ma kh�c d�ng full timeframe': 'New frontend in board-analysis style - using internal Wyckoff data - MWG keeps legacy logic - other symbols use full timeframe',
    'SC / AR / ST / Spring / Test Spring b�m v�o n?n th?t n?u d? li?u event c�. V�ng support 6M + support 1Y du?c gi? c? d?nh.': 'SC / AR / ST / Spring / Test Spring anchor to real candles when event data exists. Support 6M + support 1Y stay fixed.',
    'K?t lu?n': 'Verdict',
    'Dang ch? breakout th?t kh?i range d? x�c nh?n hu?ng ti?p theo.': 'Waiting for a real breakout from the range to confirm the next move.',
    'Tr?ng th�i hi?n t?i': 'Current Status',
    'K?ch b?n & h�nh d?ng': 'Scenario & Action',
    'Ma <select id="symbolSel"></select>': 'Symbol <select id="symbolSel"></select>',
    "'MWG gi? logic cu D?i ka da ung'": "'MWG keeps the legacy logic already approved'",
    "'C�c ma kh�c da chuy?n sang template gi?ng MWG'": "'Other symbols now use the MWG-like template'",
    "'D?i x�c nh?n ro hon t? c?u tr�c Wyckoff.'": "'Wait for clearer confirmation from Wyckoff structure.'",
    "'Tr?ng th�i k?t lu?n ch�nh'": "'Main conclusion state'",
    "'H�nh d?ng ch�nh hi?n t?i'": "'Current main action'",
    "'Phase Wyckoff hi?n t?i'": "'Current Wyckoff phase'",
    "'Channel/c?u tr�c Wyckoff b? sung'": "'Extra Wyckoff channel/structure'",
    "'Bi�n Trading Range ch�nh'": "'Main trading range'",
    "'M?c x�c nh?n n?u vu?t qua'": "'Bull confirmation level'",
    "'M?c l�m view hi?n t?i sai'": "'Invalidation level'",
    "'Gi� d�ng c?a g?n nh?t'": "'Latest close price'",
    "'Chua c� event Wyckoff th?t s? quan tr?ng trong cache hi?n t?i.'": "'No major Wyckoff event found in current cache.'",
    "'Selling Climax - b�n m?nh g?n d�y range, volume/spread l?n'": "'Selling Climax - heavy selling near range low with large volume/spread'",
    "'Automatic Rally - nh?p h?i m?nh sau SC'": "'Automatic Rally - strong rebound after SC'",
    "'Secondary Test - test l?i d�y sau SC/AR'": "'Secondary Test - retest after SC/AR'",
    "'Th?ng h? tr? r?i k�o ngu?c tr? l?i range'": "'Break below support then reclaim back into range'",
    "'Retest sau Spring, thu?ng volume y?u hon'": "'Retest after Spring, usually weaker volume'",
    "'Shake-out - qu�t du?i h? tr? r?i h?i l?i'": "'Shake-out - sweep below support then recover'",
    "'Sign of Strength - t�n hi?u m?nh l�n / break t?t'": "'Sign of Strength - strong upside signal / good break'",
    "'Last Point of Support - di?m d? cu?i sau break l�n'": "'Last Point of Support - final support point after breakout'",
    "'Upthrust - vu?t c?n gi? r?i roi l?i'": "'Upthrust - false breakout above resistance then drop back'",
    "'Upthrust After Distribution - b?y breakout cu?i ph�n ph?i'": "'Upthrust After Distribution - late breakout trap in distribution'",
    "'Sign of Weakness - t�n hi?u y?u di / breakdown'": "'Sign of Weakness - weakness signal / breakdown'",
    "'Last Point of Supply - di?m h?i y?u cu?i trong xu hu?ng xu?ng'": "'Last Point of Supply - weak rebound point in downtrend'",
    'K?ch b?n ch�nh:': 'Main scenario:',
    'Bull confirm khi vu?t': 'Bull confirm above',
    'Ch? bull confirm ro hon': 'Waiting for clearer bull confirm',
    'Sai view n?u th?ng': 'View invalid below',
    'Chua c� invalidate ro': 'No clear invalidation yet',
    'Channel b? sung:': 'Extra channel:',
}
for a,b in repls.items():
    s=s.replace(a,b)
# broader line replacements for complex JS tooltip strings
s=s.replace("const ztip=z.type==='support'?'Demand zone - v�ng c?u/h? tr?, click d? l�m s�ng v�ng tr�n chart':'Supply zone - v�ng cung/kh�ng c?, click d? l�m s�ng v�ng tr�n chart';", "const ztip=z.type==='support'?'Demand zone - click to highlight this area on chart':'Supply zone - click to highlight this area on chart';")
p.write_text(s, encoding='utf-8')
print('done')
