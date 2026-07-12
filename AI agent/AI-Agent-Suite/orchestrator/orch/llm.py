from __future__ import annotations

import json
import re
import requests
from orch.config import CONFIG


def _model(agent: str) -> str:
    return {
        'sonnet': CONFIG.model_sonnet,
        'haiku': CONFIG.model_haiku,
        'codex': CONFIG.model_codex,
        'gemini': CONFIG.model_gemini,
        'kiro': CONFIG.model_kiro,
    }.get(agent, CONFIG.model_sonnet)


def _mock(agent: str, prompt: str, system: str = '') -> str:
    if 'JSON' in system.upper() or 'json' in prompt.lower():
        return json.dumps({'ok': True, 'agent': agent, 'answer': f'Mock response from {agent}'}, ensure_ascii=False)
    return f'[mock:{agent}] {prompt[:800]}'


def call(agent: str, prompt: str, system: str = '') -> str:
    if CONFIG.mock or not CONFIG.api_key:
        return _mock(agent, prompt, system)
    url = CONFIG.base_url + '/chat/completions'
    headers = {'Authorization': f'Bearer {CONFIG.api_key}', 'Content-Type': 'application/json'}
    body = {
        'model': _model(agent),
        'messages': [
            {'role': 'system', 'content': system or 'Bạn là một AI trong hội đồng multi-agent. Trả lời ngắn gọn, chính xác.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
    }
    r = requests.post(url, headers=headers, json=body, timeout=CONFIG.timeout)
    r.raise_for_status()
    data = r.json()
    return data['choices'][0]['message']['content']


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r'```(?:json)?\s*(.*?)```', text, re.S | re.I)
    return m.group(1).strip() if m else text


def call_json(agent: str, prompt: str, system: str = '') -> dict:
    text = call(agent, prompt, system + '\nChỉ trả về JSON hợp lệ, không markdown.')
    raw = _strip_fences(text)
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r'\{.*\}', raw, re.S)
        if m:
            return json.loads(m.group(0))
        return {'ok': False, 'raw': text}
