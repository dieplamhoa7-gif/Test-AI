from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    anthropic_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    chatgpt_model: str = os.getenv("OPENAI_MODEL", os.getenv("CHATGPT_MODEL", "gpt-4o-mini"))
    xai_key: str = os.getenv("XAI_API_KEY", "")
    xai_model: str = os.getenv("XAI_MODEL", "grok-2-latest")
    google_key: str = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    gemini_text_model: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    gemini_image_model: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-1.5-flash")
    router9_api_key: str = os.getenv("ROUTER9_API_KEY", os.getenv("NINEROUTER_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    router9_base_url: str = os.getenv("ROUTER9_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.9router.com/v1"))
    kiro_model: str = os.getenv("KIRO_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    claude_real_provider: str = os.getenv("CLAUDE_REAL_PROVIDER", "router9")
    grok_real_provider: str = os.getenv("GROK_REAL_PROVIDER", "router9")
    chatgpt_real_provider: str = os.getenv("CHATGPT_REAL_PROVIDER", "router9")
    gemini_real_provider: str = os.getenv("GEMINI_REAL_PROVIDER", "mock")
    grok_bridge_url: str = os.getenv("GROK_BRIDGE_URL", "")
    grok_terminal_command: str = os.getenv("GROK_TERMINAL_COMMAND", "")
    grokx_terminal_command: str = os.getenv("GROKX_TERMINAL_COMMAND", "")

    def mode_for(self, agent_id: str) -> str:
        return os.getenv(f"{agent_id.upper()}_MODE", os.getenv("AI_PROVIDER_MODE", "real" if self.router9_api_key else "mock")).lower()


CONFIG = Config()
