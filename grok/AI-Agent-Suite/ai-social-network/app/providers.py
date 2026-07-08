"""Provider layer cho 4 AI: Claude, Grok, ChatGPT (text) và Gemini (image).

Mỗi AI có 2 cách hiện thực dùng chung interface:
  - real: gọi REST API thật
  - mock: trả lời giả lập offline (không cần key, không tốn tiền)

Factory get_text_agent()/get_image_agent() chọn bản phù hợp theo CONFIG.mode_for().
"""
from __future__ import annotations

import base64
import html
import json
import shlex
import subprocess
import tempfile
import textwrap
from typing import Any

import os
import time

import requests

from app.config import CONFIG

# Hồ sơ hiển thị từng AI trên "bảng tin"
PROFILE = {
    "claude":  {"name": "Claude",  "handle": "@claude",  "color": "#d97757", "avatar": "C"},
    "grok":    {"name": "Grok",    "handle": "@grok",    "color": "#1d9bf0", "avatar": "G"},
    "grokx":   {"name": "GrokX",   "handle": "@grokx",   "color": "#111827", "avatar": "X"},
    "chatgpt": {"name": "ChatGPT", "handle": "@chatgpt", "color": "#10a37f", "avatar": "O"},
    "gemini":  {"name": "Gemini",  "handle": "@gemini",  "color": "#9168f0", "avatar": "✦"},
}


# --------------------------------------------------------------------------- #
# Interface
# --------------------------------------------------------------------------- #
class TextAgent:
    agent_id = "ai"

    def complete(self, prompt: str, system: str = "") -> str:
        raise NotImplementedError


class ImageAgent:
    agent_id = "gemini"

    def generate(self, prompt: str) -> dict[str, Any]:
        """Trả về {'caption': str, 'image': data-URI hoặc URL, 'note': str}."""
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# REAL providers (REST)
# --------------------------------------------------------------------------- #
class ClaudeReal(TextAgent):
    agent_id = "claude"

    def complete(self, prompt: str, system: str = "") -> str:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CONFIG.anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CONFIG.claude_model,
                "max_tokens": 1200,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json().get("content", []))


def _openai_compat_content(response: requests.Response) -> str:
    """Read normal OpenAI JSON or SSE-style `data:` chunks from 9router."""
    ctype = response.headers.get("content-type", "")
    text = response.text
    if "data:" in text and ("text/event-stream" in ctype or text.lstrip().startswith("data:")):
        parts: list[str] = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                d = json.loads(payload)
            except json.JSONDecodeError:
                continue
            choice = (d.get("choices") or [{}])[0]
            delta = choice.get("delta") or {}
            msg = choice.get("message") or {}
            parts.append(delta.get("content") or msg.get("content") or "")
        return "".join(parts).strip()
    d = response.json()
    choice = d["choices"][0]
    return (choice.get("message") or {}).get("content") or (choice.get("delta") or {}).get("content") or ""


class OpenAICompatReal(TextAgent):
    """Dùng chung cho OpenAI-compatible APIs: OpenAI, xAI, 9router."""

    def __init__(self, agent_id: str, base_url: str, api_key: str, model: str) -> None:
        self.agent_id = agent_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = int(os.getenv("SUPERLH_OPENAI_COMPAT_TIMEOUT", "150"))
        self.retries = int(os.getenv("SUPERLH_OPENAI_COMPAT_RETRIES", "0"))

    def complete(self, prompt: str, system: str = "") -> str:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        last_exc: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": msgs, "temperature": 0.4},
                    timeout=self.timeout,
                )
                r.raise_for_status()
                return _openai_compat_content(r)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exc = exc
                if attempt >= self.retries:
                    break
                time.sleep(2 * (attempt + 1))
        assert last_exc is not None
        raise last_exc


class GrokBridgeReal(TextAgent):
    agent_id = "grok"

    def complete(self, prompt: str, system: str = "") -> str:
        full = (system + "\n\n" + prompt) if system else prompt
        r = requests.post(
            f"{CONFIG.grok_bridge_url.rstrip('/')}/chat",
            json={"prompt": full, "timeout": 120},
            timeout=135,
        )
        r.raise_for_status()
        d = r.json()
        return d.get("response") or d.get("text") or json.dumps(d)


class TerminalReal(TextAgent):
    """Generic terminal/CLI adapter. Command receives full prompt via stdin.

    If the command contains {prompt}, the prompt is shell-quoted into the command
    instead of stdin. Use only with trusted local commands from .env.
    """

    def __init__(self, agent_id: str, command: str, timeout: int = 180) -> None:
        self.agent_id = agent_id
        self.command = command
        self.timeout = timeout

    def complete(self, prompt: str, system: str = "") -> str:
        if not self.command:
            raise ValueError(f"Missing terminal command for {self.agent_id}")
        full = (system + "\n\n" + prompt) if system else prompt
        if "{prompt_file}" in self.command:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
                f.write(full)
                prompt_file = f.name
            cmd = self.command.replace("{prompt_file}", '"' + prompt_file.replace('"', '\\"') + '"')
            proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=self.timeout)
        elif "{prompt}" in self.command:
            cmd = self.command.replace("{prompt}", shlex.quote(full))
            proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=self.timeout)
        else:
            proc = subprocess.run(self.command, input=full, shell=True, text=True,
                                  capture_output=True, timeout=self.timeout)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or f"{self.agent_id} terminal failed").strip())
        return proc.stdout.strip()


class GeminiTextReal(TextAgent):
    agent_id = "gemini"

    def complete(self, prompt: str, system: str = "") -> str:
        full = (system + "\n\n" + prompt) if system else prompt
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{CONFIG.gemini_text_model}:generateContent?key={CONFIG.google_key}")
        r = requests.post(url, json={"contents": [{"parts": [{"text": full}]}]}, timeout=120)
        r.raise_for_status()
        parts = r.json()["candidates"][0]["content"].get("parts", [])
        return "".join(p.get("text", "") for p in parts)


class GeminiReal(ImageAgent):
    agent_id = "gemini"

    def generate(self, prompt: str) -> dict[str, Any]:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{CONFIG.gemini_image_model}:generateContent?key={CONFIG.google_key}")
        try:
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=120)
            r.raise_for_status()
            parts = r.json()["candidates"][0]["content"]["parts"]
            for p in parts:
                inline = p.get("inlineData") or p.get("inline_data")
                if inline and inline.get("data"):
                    mime = inline.get("mimeType", "image/png")
                    return {"caption": prompt, "image": f"data:{mime};base64,{inline['data']}", "note": ""}
            text = " ".join(p.get("text", "") for p in parts)
            return {"caption": prompt, "image": _placeholder_svg(prompt), "note": text or "Không có ảnh trả về."}
        except Exception as e:  # noqa: BLE001
            return {"caption": prompt, "image": _placeholder_svg(prompt), "note": f"Lỗi Gemini: {e}"}


# --------------------------------------------------------------------------- #
# MOCK providers
# --------------------------------------------------------------------------- #
def _task_of(prompt: str) -> str:
    marker = "NHIỆM VỤ:"
    if marker in prompt:
        return prompt.split(marker, 1)[1].strip().splitlines()[0].strip()
    return prompt.strip().splitlines()[0][:120]


class ClaudeMock(TextAgent):
    agent_id = "claude"

    def complete(self, prompt: str, system: str = "") -> str:
        task = _task_of(prompt)
        if "REVIEW" in prompt or "nhận xét" in prompt.lower():
            return textwrap.dedent(f"""\
                Nhận xét cuối cho "{task}":

                ✅ Điểm mạnh
                • Bám sát yêu cầu, có hướng đi rõ ràng và lý do chọn.
                • Kết hợp được góc nhìn ý tưởng (Claude), phản biện (Grok) và bản tổng hợp dùng được ngay (ChatGPT).

                ⚠️ Cần cải thiện
                • Bổ sung số liệu/dẫn chứng cụ thể trước khi công bố.
                • Làm rõ đối tượng mục tiêu và ngân sách để chốt phương án.

                🎯 Đánh giá: 8/10 — Sẵn sàng dùng sau khi bổ sung dữ liệu thực tế. [Claude · mock]""")
        return textwrap.dedent(f"""\
            Brainstorm cho "{task}":

            🎯 Thông điệp cốt lõi
            • Một câu cô đọng nói lên giá trị chính của "{task}".
            • Đối tượng quan tâm nhất và điều họ muốn nghe.

            💡 Ba hướng tiếp cận
            1. An toàn — bám chuẩn mực, dễ được chấp nhận rộng rãi.
            2. Sáng tạo — có điểm nhấn khác biệt, dễ nhớ.
            3. Táo bạo — gây chú ý mạnh, chấp nhận rủi ro để nổi bật.

            ❓ Cần làm rõ: ngân sách/giới hạn? kênh triển khai? tông giọng?

            → Phân công: Grok kiểm chứng tính khả thi, Gemini minh hoạ hướng đã chọn, ChatGPT chấp bút bản cuối. [Claude · mock]""")


class GrokMock(TextAgent):
    agent_id = "grok"

    def complete(self, prompt: str, system: str = "") -> str:
        task = _task_of(prompt)
        return textwrap.dedent(f"""\
            Suy luận & phản biện cho "{task}":

            • Giả định đang dùng: liệt kê điều kiện cho là đúng.
            • Ưu điểm hướng sáng tạo: dễ nhớ, lan toả, tạo nhận diện.
            • Đánh đổi: tốn nguồn lực thiết kế, có rủi ro "khó hiểu" với nhóm bảo thủ.
            • Phản biện: nếu mục tiêu là chuyển đổi nhanh, hướng an toàn lại hiệu quả hơn.

            → Khuyến nghị có điều kiện: chọn SÁNG TẠO nếu ưu tiên nhận diện thương hiệu;
              chọn AN TOÀN nếu ưu tiên chuyển đổi tức thì. (độ tin cậy: trung bình) [Grok · mock]""")


class GrokXMock(GrokMock):
    agent_id = "grokx"


class ChatGPTMock(TextAgent):
    agent_id = "chatgpt"

    def complete(self, prompt: str, system: str = "") -> str:
        task = _task_of(prompt)
        return textwrap.dedent(f"""\
            SẢN PHẨM CUỐI — "{task}"

            1. Tóm tắt: chốt theo hướng sáng tạo có kiểm soát, bám thông điệp cốt lõi.
            2. Đề xuất chính: nêu phương án cụ thể, ngắn gọn, dễ thực thi.
            3. Triển khai (3 bước): chuẩn bị nội dung → sản xuất → đo lường & tối ưu.
            4. Lưu ý: kiểm chứng số liệu, cân nhắc A/B test trước khi mở rộng.

            (Tổng hợp từ brainstorm của Claude và phân tích của Grok.) [ChatGPT · mock]""")


class GeminiMock(ImageAgent):
    agent_id = "gemini"

    def generate(self, prompt: str) -> dict[str, Any]:
        task = _task_of(prompt)
        return {
            "caption": f"Ảnh minh hoạ cho: {task}",
            "image": _placeholder_svg(task),
            "note": "[Gemini · mock] Ảnh giả lập. Cắm GOOGLE_API_KEY + mode=real để sinh ảnh thật.",
        }


def _placeholder_svg(text: str) -> str:
    """Tạo một ảnh SVG placeholder (data-URI) để feed luôn có gì đó hiển thị."""
    safe = html.escape((text or "AI image")[:60])
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'>
  <defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
    <stop offset='0' stop-color='#9168f0'/><stop offset='1' stop-color='#1d9bf0'/>
  </linearGradient></defs>
  <rect width='640' height='360' fill='url(#g)'/>
  <text x='320' y='175' font-family='sans-serif' font-size='26' fill='white'
    text-anchor='middle'>✦ Gemini</text>
  <text x='320' y='210' font-family='sans-serif' font-size='16' fill='white'
    opacity='0.9' text-anchor='middle'>{safe}</text>
</svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #
def get_text_agent(agent_id: str) -> TextAgent:
    mode = CONFIG.mode_for(agent_id)
    if mode == "real":
        if agent_id == "claude":
            if CONFIG.claude_real_provider == "9router":
                if not CONFIG.router9_api_key:
                    return ClaudeMock()
                return OpenAICompatReal("claude", CONFIG.router9_base_url,
                                        CONFIG.router9_api_key, CONFIG.claude_model)
            if not CONFIG.anthropic_key:
                return ClaudeMock()
            return ClaudeReal()
        if agent_id == "chatgpt":
            if CONFIG.chatgpt_real_provider == "9router":
                if not CONFIG.router9_api_key:
                    return ChatGPTMock()
                return OpenAICompatReal("chatgpt", CONFIG.router9_base_url,
                                        CONFIG.router9_api_key, CONFIG.chatgpt_model)
            if not CONFIG.openai_key:
                return ChatGPTMock()
            return OpenAICompatReal("chatgpt", "https://api.openai.com/v1",
                                    CONFIG.openai_key, CONFIG.chatgpt_model)
        if agent_id == "kiro":
            if not CONFIG.router9_api_key:
                return ChatGPTMock()
            return OpenAICompatReal("kiro", CONFIG.router9_base_url,
                                    CONFIG.router9_api_key, CONFIG.kiro_model)
        if agent_id == "gemini":
            if CONFIG.gemini_real_provider == "9router":
                if not CONFIG.router9_api_key:
                    return ChatGPTMock()
                return OpenAICompatReal("gemini", CONFIG.router9_base_url,
                                        CONFIG.router9_api_key, CONFIG.gemini_text_model)
            if CONFIG.google_key:
                return GeminiTextReal()
            return ChatGPTMock()
        if agent_id == "grokx":
            if not CONFIG.grokx_terminal_command:
                return GrokXMock()
            return TerminalReal("grokx", CONFIG.grokx_terminal_command)
        if agent_id == "grok":
            if CONFIG.grok_real_provider == "terminal":
                if not CONFIG.grok_terminal_command:
                    return GrokMock()
                return TerminalReal("grok", CONFIG.grok_terminal_command)
            if CONFIG.grok_real_provider == "bridge":
                return GrokBridgeReal()
            if CONFIG.grok_real_provider == "9router":
                if not CONFIG.router9_api_key:
                    return GrokMock()
                return OpenAICompatReal("grok", CONFIG.router9_base_url,
                                        CONFIG.router9_api_key, CONFIG.xai_model)
            if not CONFIG.xai_key:
                return GrokMock()
            return OpenAICompatReal("grok", "https://api.x.ai/v1",
                                    CONFIG.xai_key, CONFIG.xai_model)
    # mặc định mock
    return {"claude": ClaudeMock, "grok": GrokMock, "grokx": GrokXMock, "chatgpt": ChatGPTMock,
            "kiro": ChatGPTMock, "gemini": ChatGPTMock}[agent_id]()


def get_image_agent() -> ImageAgent:
    if CONFIG.mode_for("gemini") == "real" and CONFIG.google_key:
        return GeminiReal()
    return GeminiMock()
