from __future__ import annotations

from orch.config import CONFIG

CAPABILITIES = {
    'sonnet': 'Suy luận sâu, lập kế hoạch, kiến trúc, phân tích tinh tế, review chất lượng.',
    'haiku': 'Nhanh & rẻ: trích xuất, tóm tắt, kiểm tra sơ bộ, lint, so khớp đơn giản.',
    'codex': 'Sinh & chạy code, tính toán định lượng, thuật toán, xử lý dữ liệu có cấu trúc.',
    'gemini': 'Đa phương thức, long-context, tổng hợp nguồn lớn, ý kiến độc lập.',
    'kiro': 'Spec-driven: viết đặc tả, dựng khung dự án, tài liệu kỹ thuật có cấu trúc.',
}

TYPE_DEFAULT = {
    'analysis': 'sonnet', 'reasoning': 'sonnet', 'research': 'gemini', 'factual': 'gemini',
    'math': 'codex', 'code': 'codex', 'data': 'codex', 'writing': 'sonnet',
    'spec': 'kiro', 'summary': 'haiku', 'extract': 'haiku',
}

ALL_AGENTS = list(CAPABILITIES.keys())

def capabilities_block() -> str:
    return '\n'.join(f'- {k}: {v}' for k, v in CAPABILITIES.items())

def default_agent(kind: str) -> str:
    return TYPE_DEFAULT.get((kind or '').lower(), 'sonnet')

def pick_verifier(worker: str) -> str:
    order = ['gemini', 'sonnet', 'codex', 'kiro', 'haiku']
    for a in order:
        if a != worker:
            return a
    return 'sonnet'

def second_verifier(worker: str, first: str) -> str:
    order = ['sonnet', 'gemini', 'codex', 'kiro', 'haiku']
    for a in order:
        if a not in {worker, first}:
            return a
    return 'codex'
