"""Client goi 9router AI (OpenAI-compatible chat completions API).

Ho tro:
- chat(): goi 1 luot chat completion, tra ve text.
- chat_json(): yeu cau model tra ve JSON, tu parse va retry neu loi.

Neu 9router cua anh dung schema khac (khong OpenAI-compatible), chi can sua
ham `_post_chat` ben duoi.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AIError(RuntimeError):
    pass


class NineRouterClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 120,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def _post_chat(
        self,
        messages,
        temperature: float = 0.2,
        response_format=None,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format is not None:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code >= 400:
                raise AIError(f"9router HTTP {r.status_code}: {r.text[:500]}")
            data = r.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise AIError(f"9router phan hoi sai format: {data}") from e

    async def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        return await self._post_chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )

    async def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> Any:
        """Yeu cau AI tra ve JSON. Co parse, co retry neu hong."""
        last_err = None
        sys_with_json = (
            system
            + "\n\nQUAN TRONG: Chi tra loi bang JSON hop le, khong markdown, "
            "khong giai thich them."
        )
        for attempt in range(max_retries + 1):
            try:
                text = await self._post_chat(
                    [
                        {"role": "system", "content": sys_with_json},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
            except AIError:
                text = await self._post_chat(
                    [
                        {"role": "system", "content": sys_with_json},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                )

            cleaned = _extract_json_block(text)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                last_err = e
                logger.warning(
                    "Parse JSON loi lan %d: %s; raw=%s",
                    attempt + 1,
                    e,
                    text[:300],
                )
                await asyncio.sleep(0.5)

        raise AIError(
            f"Khong parse duoc JSON sau {max_retries + 1} lan thu: {last_err}"
        )


def _extract_json_block(text: str) -> str:
    """Boc khoi JSON tu phan hoi."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1)
    return text



def make_role_client(default_client: NineRouterClient, api_key: str | None, base_url: str | None, model: str | None, timeout: int | None = None) -> NineRouterClient:
    """Create a role-specific client, falling back to the default config."""
    return NineRouterClient(
        api_key=api_key or default_client.api_key,
        base_url=base_url or default_client.base_url,
        model=model or default_client.model,
        timeout=timeout or default_client.timeout,
    )
