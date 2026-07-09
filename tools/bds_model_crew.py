r"""
BDS model crew runner.

Purpose:
- Use the local OpenAI-compatible 9router endpoint with the same Kiro API key.
- Treat Kiro/Minimax/Deepseek/Qwen as worker models for legal research, frontend planning, and audit.
- This is a lightweight CrewAI-style orchestrator because native OpenClaw sub-agent allowlist currently only exposes `main`.

Usage examples:
  python tools/bds_model_crew.py --task "Deepen BDS legal ontology" --workspace "LH BDS/Luat BDS"
  python tools/bds_model_crew.py --task-file prompt.txt --out reports/crew_result.md

Notes:
- Models configured in C:\Users\HoaD-CVDT\.openclaw\openclaw.json:
  9router-openai/Kiro, Minimax, Deepseek, Qwen.
- Endpoint and key are read from openclaw.json, not hardcoded here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List

OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
DEFAULT_MODELS = ["Kiro", "Minimax", "Deepseek", "Owen"]

# Friendly names -> actual local 9router model IDs.
MODEL_ALIASES = {
    "Qwen": "kr/qwen3-coder-next",
    "Owen": "Owen",
    "Kiro": "Kiro",
    "Minimax": "Minimax",
    "Deepseek": "Deepseek",
}

ROLES = {
    "Kiro": "Chief legal architect. Build the overall ontology, spot missing legal branches, and synthesize the final plan.",
    "Minimax": "Frontend/product designer. Focus on drill-down UX, flash cards, flowchart clarity, and information hierarchy.",
    "Deepseek": "Legal researcher. Extract precise statutes, conditions, procedures, risks, and edge cases from the source corpus.",
    "Qwen": "Code and data-structure engineer. Design schemas, transformations, and robust implementation details.",
    "Owen": "QA auditor. Challenge the ontology, find gaps, identify hallucinations or weak citations, and propose fixes.",
}


def load_provider() -> Dict[str, str]:
    cfg = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8-sig"))
    provider = cfg["models"]["providers"]["9router-openai"]
    return {
        "base_url": provider["baseUrl"].rstrip("/"),
        "api_key": provider["apiKey"],
    }


def _parse_response(raw: str) -> str:
    raw = raw.strip()
    # Some local 9router models return Server-Sent Events even without stream=True.
    if raw.startswith("data:"):
        parts = []
        for line in raw.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            try:
                obj = json.loads(data)
                choice = obj.get("choices", [{}])[0]
                delta = choice.get("delta") or {}
                msg = choice.get("message") or {}
                parts.append(delta.get("content") or msg.get("content") or "")
            except Exception:
                pass
        return "".join(parts).strip()
    obj = json.loads(raw)
    choice = obj["choices"][0]
    if "message" in choice:
        return choice["message"].get("content", "")
    return choice.get("text", "")


def chat(model: str, system: str, user: str, temperature: float = 0.2, max_tokens: int = 4000) -> str:
    p = load_provider()
    url = p["base_url"] + "/chat/completions"
    actual_model = MODEL_ALIASES.get(model, model)
    payload = {
        "model": actual_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {p['api_key']}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return _parse_response(raw)


def run_crew(task: str, workspace: str, models: List[str]) -> str:
    context = f"Workspace: {workspace}\nTask: {task}\n"
    outputs = {}
    for model in models:
        role = ROLES.get(model, "Specialist worker.")
        system = (
            f"You are {model}, acting as: {role}\n"
            "Answer in Vietnamese. Be concrete, structured, and useful for building a BDS legal knowledge web. "
            "If you need sources, refer to the local legal markdown corpus conceptually; do not invent article numbers."
        )
        user = context + "\nGive your specialist analysis, proposed structure, risks, and concrete next actions."
        try:
            outputs[model] = chat(model, system, user)
        except Exception as e:
            outputs[model] = f"ERROR calling {model}: {e}"
        time.sleep(0.4)

    synthesis_prompt = (
        context
        + "\nWorker outputs:\n"
        + "\n\n".join(f"## {m}\n{txt}" for m, txt in outputs.items())
        + "\n\nSynthesize into a single execution plan and improved ontology/schema."
    )
    try:
        synthesis = chat("Kiro", ROLES["Kiro"], synthesis_prompt, temperature=0.15, max_tokens=5000)
    except Exception as e:
        synthesis = f"ERROR synthesizing with Kiro: {e}"

    return "# BDS Model Crew Result\n\n" + "\n\n".join(
        [f"## Worker: {m}\n{txt}" for m, txt in outputs.items()]
    ) + "\n\n---\n\n## Kiro synthesis\n" + synthesis + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="")
    ap.add_argument("--task-file", default="")
    ap.add_argument("--workspace", default=str(Path.cwd()))
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    task = args.task
    if args.task_file:
        task = Path(args.task_file).read_text(encoding="utf-8")
    if not task.strip():
        print("Provide --task or --task-file", file=sys.stderr)
        return 2
    models = [x.strip() for x in args.models.split(",") if x.strip()]
    result = run_crew(task, args.workspace, models)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result, encoding="utf-8")
        print(out)
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
