from __future__ import annotations

import asyncio
import importlib.util
import os
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

HERE = Path(__file__).resolve().parent
mod_path = HERE / 'web_valuation_api.fastmode_backup_20260626_2200.py'
spec = importlib.util.spec_from_file_location('web_valuation_api_runtime', mod_path)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

jobs: dict[str, dict[str, Any]] = {}

@app.get('/health')
def health():
    return {'ok': True, 'service': 'bds_rd_api', 'hasBdsWebApi': True, 'time': time.time()}

async def _run(job_id: str, payload: dict[str, Any]):
    jobs[job_id].update({'status': 'running', 'stage': 'run_web_valuation'})
    try:
        os.environ['BDS_JOB_ID'] = job_id
        result = await mod.run_web_valuation(payload)
        jobs[job_id].update({'ok': True, 'status': 'done', 'stage': 'done', 'result': result})
    except Exception as e:
        jobs[job_id].update({'ok': False, 'status': 'error', 'stage': 'error', 'error': f'{type(e).__name__}: {e}'})

@app.post('/bds/valuation/start')
async def start(payload: dict[str, Any]):
    job_id = 'rd_' + uuid.uuid4().hex[:12]
    jobs[job_id] = {'ok': True, 'jobId': job_id, 'status': 'queued', 'stage': 'queued', 'createdAt': time.time()}
    asyncio.create_task(_run(job_id, payload))
    return {'ok': True, 'jobId': job_id, 'status': 'queued'}

@app.get('/bds/valuation/status/{job_id}')
def status(job_id: str):
    j = jobs.get(job_id)
    if not j:
        return {'ok': False, 'status': 'error', 'error': 'job_not_found'}
    return j
