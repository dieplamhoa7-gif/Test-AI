# -*- coding: utf-8 -*-
"""Fail-fast UTF-8/mojibake gate for Model3 sources and generated outputs.
Run before deploy/publish. Exits non-zero if actual mojibake/replacement chars remain.
"""
from __future__ import annotations
from pathlib import Path
import sys
from vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / 'hybrid_agent_framework.py',
    ROOT / 'model3_docx_formatter.py',
    ROOT / 'model3_lhinvestment_context.py',
    ROOT / 'model3_utf8_gate.py',
    ROOT / 'app' / 'pipeline_api.py',
    ROOT / 'app' / 'web_app.py',
]
for p in (ROOT / 'outputs' / 'model3').glob('*') if (ROOT / 'outputs' / 'model3').exists() else []:
    if p.suffix.lower() in {'.html', '.txt', '.md', '.json'}:
        TARGETS.append(p)

bad: list[str] = []
for p in TARGETS:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8', errors='replace')
    fixed = repair_vietnamese_text(text)
    q = vietnamese_quality_report(fixed)
    if q.get('mojibake_markers') or q.get('replacement_chars'):
        bad.append(f"{p.relative_to(ROOT)}: {q}")

if bad:
    print('MODEL3 UTF-8 GATE FAILED')
    print('\n'.join(bad))
    sys.exit(2)
print('MODEL3 UTF-8 GATE OK')
