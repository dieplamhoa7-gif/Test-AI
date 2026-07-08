"""Cấu hình tập trung cho AI Social Network."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


@dataclass
class Config:
    ai_mode: str = field(default_factory=lambda: _get("AI_MODE", "mock").lower())

    claude_mode: str = field(default_factory=lambda: _get("CLAUDE_MODE"))
    grok_mode: str = field(default_factory=lambda: _get("GROK_MODE"))
    chatgpt_mode: str = field(default_factory=lambda: _get("CHATGPT_MODE"))
    gemini_mode: str = field(default_factory=lambda: _get("GEMINI_MODE"))
    grokx_mode: str = field(default_factory=lambda: _get("GROKX_MODE"))

    anthropic_key: str = field(default_factory=lambda: _get("ANTHROPIC_API_KEY"))
    openai_key: str = field(default_factory=lambda: _get("OPENAI_API_KEY"))
    google_key: str = field(default_factory=lambda: _get("GOOGLE_API_KEY"))
    xai_key: str = field(default_factory=lambda: _get("XAI_API_KEY"))

    # 9router: OpenAI-compatible gateway for Claude/ChatGPT/Kiro/Gemini text models
    router9_api_key: str = field(default_factory=lambda: _get("ROUTER9_API_KEY") or _get("NINEROUTER_API_KEY") or _get("OPENROUTER_API_KEY"))
    router9_base_url: str = field(default_factory=lambda: _get("ROUTER9_BASE_URL", "https://api.9router.com/v1"))
    claude_real_provider: str = field(default_factory=lambda: _get("CLAUDE_REAL_PROVIDER", "anthropic").lower())
    chatgpt_real_provider: str = field(default_factory=lambda: _get("CHATGPT_REAL_PROVIDER", "openai").lower())
    gemini_real_provider: str = field(default_factory=lambda: _get("GEMINI_REAL_PROVIDER", "google").lower())

    # Grok terminal mode: command receives prompt on stdin. Use {prompt} in command to pass as argument.
    grok_terminal_command: str = field(default_factory=lambda: _get("GROK_TERMINAL_COMMAND") or _get("GROK_CLI_COMMAND"))
    grokx_terminal_command: str = field(default_factory=lambda: _get("GROKX_TERMINAL_COMMAND") or _get("GROKX_CLI_COMMAND") or _get("GROK_TERMINAL_COMMAND") or _get("GROK_CLI_COMMAND"))

    grok_real_provider: str = field(default_factory=lambda: _get("GROK_REAL_PROVIDER", "xai"))
    grok_bridge_url: str = field(default_factory=lambda: _get("GROK_BRIDGE_URL", "http://127.0.0.1:19998"))

    claude_model: str = field(default_factory=lambda: _get("CLAUDE_MODEL", "claude-opus-4-8"))
    chatgpt_model: str = field(default_factory=lambda: _get("CHATGPT_MODEL", "gpt-4o"))
    xai_model: str = field(default_factory=lambda: _get("XAI_MODEL", "grok-4.1-fast"))
    gemini_text_model: str = field(default_factory=lambda: _get("GEMINI_TEXT_MODEL", "gemini-2.5-flash"))
    gemini_image_model: str = field(default_factory=lambda: _get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"))
    kiro_model: str = field(default_factory=lambda: _get("KIRO_MODEL", "kiro"))

    web_host: str = field(default_factory=lambda: _get("WEB_HOST", "127.0.0.1"))
    web_port: int = field(default_factory=lambda: int(_get("WEB_PORT", "5000")))

    def mode_for(self, agent: str) -> str:
        """Trả về 'mock' hoặc 'real' cho một AI cụ thể."""
        override = {
            "claude": self.claude_mode,
            "grok": self.grok_mode,
            "chatgpt": self.chatgpt_mode,
            "gemini": self.gemini_mode,
            "grokx": self.grokx_mode,
        }.get(agent, "")
        return (override or self.ai_mode or "mock").lower()


CONFIG = Config()
