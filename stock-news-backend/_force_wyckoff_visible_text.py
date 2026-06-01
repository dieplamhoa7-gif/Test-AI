from pathlib import Path
p=Path('firebase_public/wyckoff-board.html')
lines=p.read_text(encoding='utf-8', errors='replace').splitlines()
out=[]
for line in lines:
    stripped=line.strip()
    if '<div class="title">' in line:
        out.append('      <div class="title">WYCKOFF BOARD STRUCTURE MAP</div>')
    elif '<div class="subtitle">' in line and 'Frontend' in line:
        out.append('      <div class="subtitle">Full-history Wyckoff board - long data from 2023 - overlay index remapped to current chart</div>')
    elif '<label class="chip">' in line and 'symbolSel' in line:
        out.append('      <label class="chip">Symbol <select id="symbolSel"></select></label>')
    elif '<div class="footer">' in line:
        out.append('      <div class="footer">SC / AR / ST / Spring / Test Spring anchor to real candles when event data exists. Support 6M + support 1Y stay fixed.</div>')
    elif '<h3>' in line and 'zonesList' not in line:
        if 'Support / Resistance' in line or 'Wyckoff Events' in line:
            out.append(line)
        elif 'scenarioList' in line:
            out.append(line)
        elif 'K' in line or '?' in line:
            # Replace first unknown Vietnamese section headings by order based on current output length/context.
            text=''.join(out[-3:])
            if 'verdict' in text or 'verdictText' in ''.join(lines[max(0, len(out)-2):len(out)+4]):
                out.append('        <h3>Verdict</h3>')
            else:
                out.append(line)
        else:
            out.append(line)
    elif 'id="verdictText"' in line:
        out.append('        <div class="muted" id="verdictText">Waiting for real breakout from the range to confirm the next move.</div>')
    else:
        out.append(line)
s='\n'.join(out)+'\n'
# Robust final known broken replacements anywhere.
s=s.replace('<h3>K?t lu?n</h3>','<h3>Verdict</h3>')
s=s.replace('<h3>Tr?ng th�i hi?n t?i</h3>','<h3>Current Status</h3>')
s=s.replace('<h3>K?ch b?n & h�nh d?ng</h3>','<h3>Scenario & Action</h3>')
s=s.replace("'MWG gi? logic cu D?i ka da ung'", "'MWG keeps approved legacy logic'")
s=s.replace("'C�c ma kh�c da chuy?n sang template gi?ng MWG'", "'Other symbols use MWG-like template'")
p.write_text(s, encoding='utf-8')
print('forced visible text')
