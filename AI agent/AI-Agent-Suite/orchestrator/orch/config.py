from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
except Exception:
    pass


def _get(name: str, default: str = '') -> str:
    return os.getenv(name, default).strip()


@dataclass
class Config:
    api_key: str = field(default_factory=lambda: _get('OPENAI_API_KEY') or _get('9ROUTER_API_KEY') or _get('OPENROUTER_API_KEY'))
    base_url: str = field(default_factory=lambda: (_get('OPENAI_BASE_URL') or _get('9ROUTER_BASE_URL') or _get('OPENROUTER_BASE_URL') or 'https://api.9router.com/v1').rstrip('/'))
    mock: bool = field(default_factory=lambda: _get('ORCH_MOCK', '0').lower() in {'1','true','yes','on'})
    timeout: int = field(default_factory=lambda: int(_get('ORCH_TIMEOUT', '120') or '120'))
    runs_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1] / 'runs')
    model_sonnet: str = field(default_factory=lambda: _get('MODEL_SONNET') or _get('ORCH_MODEL_SONNET') or 'anthropic/claude-sonnet-4')
    model_haiku: str = field(default_factory=lambda: _get('MODEL_HAIKU') or _get('ORCH_MODEL_HAIKU') or 'anthropic/claude-3.5-haiku')
    model_codex: str = field(default_factory=lambda: _get('MODEL_CODEX') or _get('ORCH_MODEL_CODEX') or 'openai/gpt-4.1')
    model_gemini: str = field(default_factory=lambda: _get('MODEL_GEMINI') or _get('ORCH_MODEL_GEMINI') or 'google/gemini-2.5-pro')
    model_kiro: str = field(default_factory=lambda: _get('MODEL_KIRO') or _get('ORCH_MODEL_KIRO') or 'openai/gpt-4.1')

CONFIG = Config()
