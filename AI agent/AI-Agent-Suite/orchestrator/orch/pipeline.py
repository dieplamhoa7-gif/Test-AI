from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from orch import agents, llm
from orch.config import CONFIG


def plan(question: str) -> dict[str, Any]:
    prompt = f"""Câu hỏi/yêu cầu của người dùng:\n{question}\n\nHãy lập kế hoạch multi-agent tối đa 3 bước. JSON schema:\n{{"tasks":[{{"id":"t1","kind":"analysis|research|code|data|writing|spec|summary|extract|factual|math","agent":"sonnet|haiku|codex|gemini|kiro","question":"...","important":true/false}}]}}\nNăng lực agent:\n{agents.capabilities_block()}"""
    rep = llm.call_json('sonnet', prompt)
    tasks = rep.get('tasks') if isinstance(rep, dict) else None
    if not tasks:
        tasks = [{'id': 't1', 'kind': 'analysis', 'agent': 'sonnet', 'question': question, 'important': True}]
    for i, t in enumerate(tasks, 1):
        t.setdefault('id', f't{i}')
        t.setdefault('kind', 'analysis')
        if t.get('agent') not in agents.ALL_AGENTS:
            t['agent'] = agents.default_agent(t.get('kind','analysis'))
        t.setdefault('question', question)
        t.setdefault('important', True)
    return {'tasks': tasks[:3]}


def execute(task: dict[str, Any], question: str) -> dict[str, Any]:
    agent = task['agent']
    prompt = f"""Yêu cầu gốc: {question}\n\nNhiệm vụ của bạn ({task['id']} - {task.get('kind')}):\n{task.get('question')}\n\nTrả lời có cấu trúc: kết luận, luận cứ, giả định/rủi ro nếu có."""
    out = llm.call(agent, prompt)
    return {'task': task, 'agent': agent, 'output': out}


def _verify_once(item: dict[str, Any], verifier: str) -> dict[str, Any]:
    prompt = f"""Hãy kiểm định độc lập kết quả sau. Trả JSON: {{"verdict":"pass|warn|fail","issues":["..."],"confidence":0-1}}\n\nAgent làm: {item['agent']}\nNhiệm vụ: {item['task'].get('question')}\nKết quả:\n{item['output']}"""
    rep = llm.call_json(verifier, prompt)
    if 'verdict' not in rep:
        rep = {'verdict': 'warn', 'issues': [str(rep)[:1000]], 'confidence': 0.5}
    rep['verifier'] = verifier
    return rep


def verify(item: dict[str, Any]) -> list[dict[str, Any]]:
    first = agents.pick_verifier(item['agent'])
    checks = [_verify_once(item, first)]
    if item['task'].get('important'):
        second = agents.second_verifier(item['agent'], first)
        checks.append(_verify_once(item, second))
    return checks


def synthesize(question: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    blob = json.dumps(results, ensure_ascii=False, indent=2)
    prompt = f"""Yêu cầu gốc: {question}\n\nDưới đây là kết quả các agent và phần kiểm định:\n{blob}\n\nHãy tổng hợp câu trả lời cuối cùng bằng tiếng Việt, rõ ràng, nêu điểm chưa chắc nếu có. Trả JSON: {{"overall":"pass|warn|fail","red_flags":["..."],"final_answer":"..."}}"""
    rep = llm.call_json('sonnet', prompt)
    if not isinstance(rep, dict) or 'final_answer' not in rep:
        rep = {'overall': 'warn', 'red_flags': ['Không parse được JSON synthesize'], 'final_answer': llm.call('sonnet', prompt)}
    return rep


def _save(rep: dict[str, Any]) -> str:
    CONFIG.runs_dir.mkdir(parents=True, exist_ok=True)
    name = 'run_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S') + '.json'
    path = CONFIG.runs_dir / name
    path.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def run(question: str) -> dict[str, Any]:
    p = plan(question)
    results = []
    for task in p['tasks']:
        item = execute(task, question)
        item['verification'] = verify(item)
        results.append(item)
    final = synthesize(question, results)
    final['_plan'] = p
    final['_results'] = results
    final['_saved'] = _save(final)
    return final
