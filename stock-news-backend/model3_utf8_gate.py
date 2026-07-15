# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import Any
from vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report, has_vietnamese_quality_issue


def clean_model3_text(text: Any) -> str:
    return repair_vietnamese_text(str(text or ""))


def assert_model3_utf8_quality(text: Any, label: str = "model3") -> str:
    fixed = clean_model3_text(text)
    q = vietnamese_quality_report(fixed)
    # Hard fail on actual mojibake/replacement chars; tolerate a few unaccented acronyms/English words.
    if int(q.get("mojibake_markers", 0)) > 0 or int(q.get("replacement_chars", 0)) > 0:
        raise ValueError(f"{label} UTF-8 quality gate failed: {q}")
    return fixed


def write_model3_text(path: str | Path, text: Any, label: str = "model3") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(assert_model3_utf8_quality(text, label), encoding="utf-8", newline="\n")
