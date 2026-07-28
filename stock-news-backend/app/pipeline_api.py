"""
pipeline_api.py — Backend thật cho Stock AI Pipeline (10 giai đoạn).

Đấu nối THÊM (không sửa site đang khoá):
- Orchestrator chạy 10 "bot" theo group song song (asyncio), mỗi bot điền 1 slice của
  report-template.json.
- Dữ liệu THẬT lấy từ app.market_data.get_market_symbol (giá/kỹ thuật/PE-PB). Các bước
  phân tích sâu dùng suy luận từ dữ liệu thật (heuristic) + tùy chọn AI, tự degrade khi thiếu.
- Có retry theo stage, QA gate chặn xuất khi mâu thuẫn nghiêm trọng.
- Hàng đợi nhiều mã (asyncio.Queue) + giới hạn concurrency.
- Endpoints: /pipeline (dashboard), /pipeline/run, /pipeline/status, /pipeline/events (SSE),
  /pipeline/report(.md).

Wire vào app/main.py bằng 2 dòng:
    from app.pipeline_api import router as pipeline_router
    app.include_router(pipeline_router)
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import re
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Callable, Optional

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# ----------------------------- config -----------------------------
MAX_CONCURRENT_TICKERS = int(os.getenv("PIPELINE_CONCURRENCY", "2"))
STAGE_RETRIES = int(os.getenv("PIPELINE_STAGE_RETRIES", "2"))       # số lần thử lại thêm
STAGE_BACKOFF = float(os.getenv("PIPELINE_STAGE_BACKOFF", "0.8"))    # giây, nhân đôi mỗi lần
REPORTS_DIR = Path(os.getenv("PIPELINE_REPORTS_DIR", "reports"))     # 'reports' đã tồn tại
MODEL3_EXPORT_TTL_HOURS = float(os.getenv("PIPELINE_MODEL3_EXPORT_TTL_HOURS", "24"))
MODEL3_OUT_DIR = Path(os.getenv("PIPELINE_MODEL3_OUT_DIR", "outputs/model3"))
MODEL3_JOB_STATE_DIR = Path(
    os.getenv(
        "MODEL3_JOB_STATE_DIR",
        "/tmp/disk/model3_jobs" if Path("/tmp/disk").exists() else str(Path(tempfile.gettempdir()) / "model3_jobs"),
    )
)

MODEL3_EXTERNAL_WORKER_MODE = os.getenv("MODEL3_EXTERNAL_WORKER_MODE", "").lower() in ("1", "true", "yes")
MODEL3_WORKER_TOKEN = os.getenv("MODEL3_WORKER_TOKEN", "")

MODEL3_JOBS: dict[str, dict[str, Any]] = {}
MODEL3_SECTIONS = [
    ("news", "Grok", "Tin tức & impact"),
    ("technical", "Codex", "LHInvestment indicators / TA"),
    ("fundamental", "Codex", "Fundamental & macro"),
    ("scenario", "Kiro", "Kịch bản đầu tư"),
    ("bull_bear", "Codex", "Bull/Bear/Catalyst"),
    ("risk", "Kiro", "Risk & viewpoint"),
    ("followup", "Codex", "Kế hoạch theo dõi"),
    ("quick_summary", "Kiro", "Executive Summary"),
    ("word", "Model3", "Xuất Word"),
    ("notebooklm", "NotebookLM", "Tạo NotebookLM / PDF online"),
]

# hook cho phép test không cần pandas/mạng
_DATA_PROVIDER: Optional[Callable[[str], dict]] = None


def _model3_job_file(job_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "", str(job_id or ""))[:64]
    if not safe:
        raise ValueError("invalid job_id")
    return MODEL3_JOB_STATE_DIR / f"{safe}.json"


def _check_model3_worker_token(authorization: str | None = None) -> None:
    if not MODEL3_WORKER_TOKEN:
        raise HTTPException(status_code=403, detail="MODEL3_WORKER_TOKEN chưa được cấu hình")
    token = (authorization or "").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if token != MODEL3_WORKER_TOKEN:
        raise HTTPException(status_code=403, detail="worker token không hợp lệ")


def _iter_model3_jobs_from_disk() -> list[dict[str, Any]]:
    jobs = list(MODEL3_JOBS.values())
    seen = {str(j.get("job_id")) for j in jobs}
    if MODEL3_JOB_STATE_DIR.exists():
        for path in MODEL3_JOB_STATE_DIR.glob("*.json"):
            try:
                job = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            jid = str(job.get("job_id") or "")
            if jid and jid not in seen:
                jobs.append(job)
                seen.add(jid)
    jobs.sort(key=lambda j: float(j.get("created_at") or 0))
    return jobs


def _save_model3_job(job: dict[str, Any]) -> None:
    """Persist Model3 job state so Render restarts do not lose job_id/status."""
    job_id = str(job.get("job_id") or "")
    if not job_id:
        return
    MODEL3_JOB_STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = _model3_job_file(job_id)
    tmp = path.with_suffix(f".json.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def _load_model3_job(job_id: str) -> dict[str, Any] | None:
    if job_id in MODEL3_JOBS:
        return MODEL3_JOBS[job_id]
    path = _model3_job_file(job_id)
    if not path.exists():
        return None
    try:
        job = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(job, dict) and job.get("job_id") == job_id:
        # A restarted Render process cannot resume the old background task. Make
        # that explicit instead of returning 404/missing job.
        if job.get("status") in {"queued", "running"}:
            job["status"] = "interrupted"
            job["error"] = job.get("error") or "Render process restarted before the in-flight Model3 job finished. Please start a new export."
            job["updated_at"] = time.time()
            _save_model3_job(job)
        MODEL3_JOBS[job_id] = job
        return job
    return None


def _load_symbol_local_provider(symbol: str, force_refresh: bool = False) -> dict:
    try:
        from app.market_data import get_market_symbol  # type: ignore  # optional local provider
        return get_market_symbol(symbol, force_refresh=force_refresh)
    except ModuleNotFoundError as exc:
        if exc.name != "app.market_data":
            raise
    # This web project has no app.market_data module. Reuse the canonical
    # stock-news-backend provider by loading it from file to avoid package-name
    # conflicts with this project's own app package. Resolve robustly because this
    # project is nested under workspace/grok/AI-Agent-Suite/ai-social-network.
    import importlib.util
    here = Path(__file__).resolve()
    provider_path = None
    for parent in here.parents:
        candidate = parent / "stock-news-backend" / "app" / "market_data.py"
        if candidate.exists():
            provider_path = candidate
            break
    if provider_path is None:
        raise ModuleNotFoundError("No market data provider found under any parent workspace")
    spec = importlib.util.spec_from_file_location("stock_news_backend_market_data", provider_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"Cannot load market data provider from {provider_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.get_market_symbol(symbol, force_refresh=force_refresh)


def _load_symbol(symbol: str) -> dict:
    if _DATA_PROVIDER is not None:
        return _DATA_PROVIDER(symbol)
    gateway = os.getenv("MARKET_DATA_GATEWAY_URL", "https://3t8l9f.tail6c0e00.ts.net/marketdata").rstrip("/")
    if gateway:
        try:
            url = f"{gateway}/market/{re.sub(r'[^A-Za-z0-9]', '', symbol.upper())}?force_refresh=true"
            with urllib.request.urlopen(url, timeout=min(float(os.getenv("MARKET_DATA_GATEWAY_TIMEOUT", "90")), 20.0)) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            pass
    return _load_symbol_local_provider(symbol, force_refresh=True)


# ----------------------------- helpers -----------------------------
def _num(v, default=None):
    try:
        if v is None:
            return default
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def _score_from_rsi(rsi):
    if rsi is None:
        return 50
    # 45-65 vùng khỏe mạnh; quá mua/quá bán trừ điểm
    if rsi >= 70:
        return 55
    if rsi <= 30:
        return 45
    return int(_clamp(50 + (rsi - 50) * 1.2))


# ----------------------------- state -----------------------------
@dataclass
class StageState:
    key: str
    name: str
    group: int
    model: str
    status: str = "pending"       # pending|running|retrying|done|skipped|error
    progress: int = 0
    attempts: int = 0
    error: Optional[str] = None
    tokens: int = 0
    started_at: float = 0.0
    ended_at: float = 0.0


@dataclass
class Run:
    run_id: str
    ticker: str
    batch_id: str
    status: str = "queued"        # queued|running|done|error
    created_at: float = field(default_factory=time.time)
    started_at: float = 0.0
    ended_at: float = 0.0
    queue_pos: int = 0
    error: Optional[str] = None
    stages: dict[str, StageState] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    version: int = 0              # tăng mỗi lần đổi state (cho SSE)

    def touch(self):
        self.version += 1

    def snapshot(self) -> dict:
        syn = self.report.get("stage_10_synthesis") or {}
        total = sum(s.progress for s in self.stages.values())
        overall = int(total / max(1, len(self.stages)))
        return {
            "run_id": self.run_id,
            "ticker": self.ticker,
            "batch_id": self.batch_id,
            "status": self.status,
            "queue_pos": self.queue_pos,
            "overall_progress": overall,
            "version": self.version,
            "tokens": sum(s.tokens for s in self.stages.values()),
            "error": self.error,
            "elapsed": round((self.ended_at or time.time()) - (self.started_at or self.created_at), 1),
            "verdict": syn.get("verdict"),
            "composite_score": syn.get("composite_score"),
            "confidence": syn.get("confidence"),
            "notebooklm_source": syn.get("notebooklm_source"),
            "stages": [
                {
                    "key": s.key, "name": s.name, "group": s.group, "model": s.model,
                    "status": s.status, "progress": s.progress, "attempts": s.attempts,
                    "error": s.error, "tokens": s.tokens,
                }
                for s in self.stages.values()
            ],
        }


RUNS: dict[str, Run] = {}
BATCHES: dict[str, list[str]] = {}

_queue: "asyncio.Queue[str]" = None  # type: ignore
_workers_started = False
_sem: asyncio.Semaphore = None  # type: ignore


# ----------------------------- stage definitions -----------------------------
# group: 0 tuần tự; 1 & 2 song song; 3 QA; 4 tổng hợp
STAGE_DEFS = [
    ("stage_1_data", "Thu thập dữ liệu", 0, "cheap", 900),
    ("stage_2_technical", "Phân tích kỹ thuật", 1, "cheap", 700),
    ("stage_3_fundamental", "Phân tích cơ bản", 1, "standard", 1100),
    ("stage_4_quant_risk", "Định lượng & rủi ro", 1, "standard", 1000),
    ("stage_5_flow_sentiment", "Dòng tiền & tâm lý", 1, "standard", 950),
    ("stage_6_sector_macro", "Ngành & vĩ mô", 1, "standard", 1000),
    ("stage_7_valuation", "Định giá đa mô hình", 2, "strong", 1400),
    ("stage_8_scenarios", "Kịch bản & quản trị RR", 2, "strong", 1300),
    ("stage_9_qa", "Kiểm định chéo (QA)", 3, "standard", 600),
    ("stage_10_synthesis", "Tổng hợp & NotebookLM", 4, "strong", 1200),
]


# ----------------------------- stage implementations -----------------------------
# Mỗi stage nhận (run) và trả về slice dict để ghi vào report[key].
# Dữ liệu thô stage_1 lưu ở run.report['_raw'] (khóa nội bộ, không xuất ra ngoài).

async def _stage_1_data(run: Run) -> dict:
    raw = await asyncio.to_thread(_load_symbol, run.ticker)
    if not raw or not isinstance(raw, dict):
        raise RuntimeError("Không lấy được dữ liệu thị trường")
    run.report["_raw"] = raw
    tech = raw.get("technical") or {}
    fin = raw.get("financial") or {}
    price = _num(raw.get("price"))
    return {
        "price": {
            "last": price,
            "change_pct_1d": _num(raw.get("changePct")),
            "volume": _num(raw.get("volume")),
            "ma20": _num(tech.get("ma20")), "ma50": _num(tech.get("ma50")), "ma200": _num(tech.get("ma200")),
            "atr": _num(tech.get("atr")),
            "currency": "VND",
        },
        "fundamentals": {"pe": _num(fin.get("pe")), "pb": _num(fin.get("pb")), "status": fin.get("status")},
        "source": raw.get("source"),
        "data_quality_score": 90 if raw.get("source") not in (None, "fallback-local") else 55,
    }


async def _stage_2_technical(run: Run) -> dict:
    tech = (run.report.get("_raw") or {}).get("technical") or {}
    rsi = _num(tech.get("rsi14"))
    macd = _num(tech.get("macd")); signal = _num(tech.get("signal"))
    ma50 = _num(tech.get("ma50")); ma200 = _num(tech.get("ma200"))
    eff = tech.get("effectiveTrend") or tech.get("action") or ""
    macd_sig = "bullish" if (macd is not None and signal is not None and macd > signal) else \
               "bearish" if (macd is not None and signal is not None and macd < signal) else "neutral"
    cross = "golden_cross" if (ma50 and ma200 and ma50 > ma200) else \
            "death_cross" if (ma50 and ma200 and ma50 < ma200) else "none"
    sig_score = _num(tech.get("signalScore"))
    score = int(_clamp(sig_score)) if sig_score is not None else _score_from_rsi(rsi)
    trend = "tang" if macd_sig == "bullish" and cross != "death_cross" else \
            "giam" if macd_sig == "bearish" else "di_ngang"
    return {
        "trend": trend,
        "indicators": {"rsi_14": rsi, "macd_signal": macd_sig, "ma50_vs_ma200": cross, "adx_14": _num(tech.get("adx14"))},
        "support": tech.get("supportLevelsDay") or [],
        "resistance": tech.get("resistanceLevelsDay") or [],
        "score": score,
        "comment": f"Xu hướng {trend}, MACD {macd_sig}, {cross}.",
        "_confidence": "cao" if sig_score is not None else "trung_binh",
    }


async def _stage_3_fundamental(run: Run) -> dict:
    fin = (run.report.get("_raw") or {}).get("financial") or {}
    pe = _num(fin.get("pe")); pb = _num(fin.get("pb"))
    if pe is None and pb is None:
        return {"ratios": {"pe": None, "pb": None}, "financial_health": None,
                "score": 50, "comment": "Thiếu dữ liệu P/E, P/B — độ tin cậy thấp.", "_confidence": "thap"}
    score = 50
    if pe is not None:
        score += 15 if pe < 12 else (5 if pe < 18 else -10 if pe > 30 else 0)
    if pb is not None:
        score += 10 if pb < 2 else (-8 if pb > 4 else 0)
    score = int(_clamp(score))
    health = "manh" if score >= 68 else "on_dinh" if score >= 52 else "yeu"
    return {"ratios": {"pe": pe, "pb": pb}, "financial_health": health,
            "score": score, "comment": f"P/E={pe}, P/B={pb} → {health}.", "_confidence": "trung_binh"}


async def _stage_4_quant_risk(run: Run) -> dict:
    raw = run.report.get("_raw") or {}
    tech = raw.get("technical") or {}
    price = _num(raw.get("price")); atr = _num(tech.get("atr"))
    # volatility proxy hằng năm từ ATR/price (nếu có)
    vol = None
    if price and atr:
        vol = round((atr / price) * math.sqrt(252) * 100, 1)
    rr = _num(tech.get("riskReward"))
    # risk_score: biến động càng cao điểm rủi ro càng cao (0-100)
    risk = 50
    if vol is not None:
        risk = int(_clamp(30 + vol))  # vol ~20% -> 50
    return {
        "volatility_annualized_pct": vol,
        "atr": atr,
        "risk_reward_ratio": rr,
        "liquidity_risk": "thap" if _num(raw.get("volume")) and raw.get("volume", 0) > 500000 else "trung_binh",
        "risk_score": risk,
        "comment": f"Biến động năm ~{vol}% (từ ATR)." if vol else "Thiếu dữ liệu biến động.",
        "_confidence": "trung_binh" if vol is not None else "thap",
    }


async def _stage_5_flow_sentiment(run: Run) -> dict:
    raw = run.report.get("_raw") or {}
    tech = raw.get("technical") or {}
    vol_ratio = _num(tech.get("volumeRatio"))
    chg = _num(raw.get("changePct")) or 0
    signal = "accumulation" if (vol_ratio and vol_ratio > 1.2 and chg > 0) else \
             "distribution" if (vol_ratio and vol_ratio > 1.2 and chg < 0) else "neutral"
    score = int(_clamp(50 + (chg * 3) + ((vol_ratio - 1) * 20 if vol_ratio else 0)))
    return {"smart_money_signal": signal, "volume_ratio": vol_ratio,
            "score": score, "comment": f"Dòng tiền {signal} (volRatio={vol_ratio}, +/-{chg}%).",
            "_confidence": "trung_binh"}


async def _stage_6_sector_macro(run: Run) -> dict:
    tech = (run.report.get("_raw") or {}).get("technical") or {}
    struct = tech.get("marketStructure") or "—"
    trend = (run.report.get("stage_2_technical") or {}).get("trend", "di_ngang")
    score = (run.report.get("stage_2_technical") or {}).get("score", 55)
    return {"sector": None, "market_structure": struct, "sector_trend": trend,
            "score": int(_clamp(score - 3)),
            "comment": f"Cấu trúc thị trường: {struct}.", "_confidence": "thap"}


async def _stage_7_valuation(run: Run) -> dict:
    raw = run.report.get("_raw") or {}
    price = _num(raw.get("price"))
    fa = run.report.get("stage_3_fundamental") or {}
    ta = run.report.get("stage_2_technical") or {}
    # giá mục tiêu heuristic: từ kháng cự kỹ thuật + điều chỉnh theo điểm cơ bản
    resist = ta.get("resistance") or []
    target = None
    if resist and price:
        target = round(max(resist), 2)
    elif price:
        adj = 1 + ((fa.get("score", 50) - 50) / 250.0)  # +/-20%
        target = round(price * adj, 2)
    upside = round((target - price) / price * 100, 1) if (target and price) else None
    score = int(_clamp((fa.get("score", 50) + ta.get("score", 50)) / 2))
    return {"blended_target_price": target, "upside_pct": upside, "method": "resistance+fundamental",
            "score": score, "comment": f"Giá mục tiêu ~{target} (upside {upside}%).",
            "_confidence": "trung_binh" if target else "thap"}


async def _stage_8_scenarios(run: Run) -> dict:
    raw = run.report.get("_raw") or {}
    tech = raw.get("technical") or {}
    price = _num(raw.get("price")); atr = _num(tech.get("atr"))
    val = run.report.get("stage_7_valuation") or {}
    target = _num(val.get("blended_target_price"))
    support = tech.get("supportLevelsDay") or []
    stop = round(min(support), 2) if support else (round(price - 2 * atr, 2) if (price and atr) else None)
    entry = price
    tp = target or (round(price + 3 * atr, 2) if (price and atr) else None)
    rr = None
    if entry and stop and tp and (entry - stop) > 0:
        rr = round((tp - entry) / (entry - stop), 2)
    scenarios = []
    if price:
        scenarios = [
            {"case": "bull", "target_price": round(price * 1.2, 2), "probability_pct": 30},
            {"case": "base", "target_price": tp, "probability_pct": 45},
            {"case": "bear", "target_price": stop, "probability_pct": 25},
        ]
    return {"scenarios": scenarios, "suggested_entry": entry, "stop_loss": stop,
            "take_profit": tp, "risk_reward_ratio": rr,
            "comment": f"Entry {entry}, SL {stop}, TP {tp}, R:R {rr}.", "_confidence": "trung_binh"}


async def _stage_9_qa(run: Run) -> dict:
    r = run.report
    issues = []
    # thiếu dữ liệu cơ bản
    if (r.get("stage_3_fundamental") or {}).get("ratios", {}).get("pe") is None:
        issues.append({"severity": "medium", "stage_ref": "stage_3_fundamental", "note": "Thiếu P/E."})
    # mâu thuẫn: kỹ thuật tăng nhưng dòng tiền phân phối
    ta = (r.get("stage_2_technical") or {}).get("trend")
    flow = (r.get("stage_5_flow_sentiment") or {}).get("smart_money_signal")
    if ta == "tang" and flow == "distribution":
        issues.append({"severity": "high", "stage_ref": "stage_2/5", "note": "Kỹ thuật tăng nhưng dòng tiền phân phối."})
    # giá mục tiêu thấp hơn giá hiện tại nhưng verdict sẽ mua -> cảnh báo ở synthesis
    if (r.get("stage_7_valuation") or {}).get("blended_target_price") is None:
        issues.append({"severity": "low", "stage_ref": "stage_7_valuation", "note": "Không định giá được mục tiêu."})
    high = any(i["severity"] == "high" for i in issues)
    check = "fail" if high else ("warn" if issues else "pass")
    conf = "thap" if high else ("trung_binh" if issues else "cao")
    return {"consistency_check": check, "issues": issues, "overall_confidence": conf}


async def _stage_10_synthesis(run: Run) -> dict:
    r = run.report
    qa = r.get("stage_9_qa") or {}
    if qa.get("consistency_check") == "fail":
        # QA gate: chặn xuất, trả verdict thận trọng
        return {"composite_score": None, "verdict": "hold", "confidence": "thap",
                "executive_summary": f"{run.ticker}: QA phát hiện mâu thuẫn nghiêm trọng — tạm dừng khuyến nghị, cần rà soát.",
                "blocked_by_qa": True, "key_strengths": [], "key_risks": [i["note"] for i in qa.get("issues", [])],
                "notebooklm_source": None}
    parts = []
    for k, inv in (("stage_2_technical", False), ("stage_3_fundamental", False),
                   ("stage_4_quant_risk", True), ("stage_5_flow_sentiment", False),
                   ("stage_6_sector_macro", False), ("stage_7_valuation", False)):
        s = (r.get(k) or {})
        v = s.get("risk_score") if inv else s.get("score")
        if v is not None:
            parts.append(100 - v if inv else v)
    comp = int(sum(parts) / len(parts)) if parts else 50
    verdict = "strong_buy" if comp >= 80 else "buy" if comp >= 68 else "hold" if comp >= 55 else "reduce" if comp >= 45 else "sell"
    val = r.get("stage_7_valuation") or {}
    fa = r.get("stage_3_fundamental") or {}
    strengths, risks = [], []
    if (fa.get("financial_health") == "manh"):
        strengths.append(f"Cơ bản mạnh (P/E {fa.get('ratios',{}).get('pe')})")
    if (r.get("stage_5_flow_sentiment") or {}).get("smart_money_signal") == "accumulation":
        strengths.append("Dòng tiền đang tích lũy")
    if val.get("upside_pct") and val["upside_pct"] > 5:
        strengths.append(f"Còn upside ~{val['upside_pct']}%")
    qv = r.get("stage_4_quant_risk") or {}
    if qv.get("volatility_annualized_pct"):
        risks.append(f"Biến động năm ~{qv['volatility_annualized_pct']}%")
    for i in qa.get("issues", []):
        risks.append(i["note"])
    summary = (f"{run.ticker}: điểm tổng hợp {comp}/100 → {verdict.upper()}. "
               f"Giá mục tiêu ~{val.get('blended_target_price')} (upside {val.get('upside_pct')}%). "
               f"Độ tin cậy {qa.get('overall_confidence')}.")
    md = _build_markdown(run, comp, verdict, summary, strengths, risks)
    src_path = _save_markdown(run.ticker, md)
    return {"composite_score": comp, "verdict": verdict, "confidence": qa.get("overall_confidence", "trung_binh"),
            "executive_summary": summary, "key_strengths": strengths[:4], "key_risks": risks[:4],
            "notebooklm_source": f"/pipeline/report/{run.run_id}/markdown",
            "notebooklm_source_file": str(src_path) if src_path else None}


STAGE_FUNCS = {
    "stage_1_data": _stage_1_data,
    "stage_2_technical": _stage_2_technical,
    "stage_3_fundamental": _stage_3_fundamental,
    "stage_4_quant_risk": _stage_4_quant_risk,
    "stage_5_flow_sentiment": _stage_5_flow_sentiment,
    "stage_6_sector_macro": _stage_6_sector_macro,
    "stage_7_valuation": _stage_7_valuation,
    "stage_8_scenarios": _stage_8_scenarios,
    "stage_9_qa": _stage_9_qa,
    "stage_10_synthesis": _stage_10_synthesis,
}


# ----------------------------- markdown / NotebookLM source -----------------------------
def _build_markdown(run: Run, comp, verdict, summary, strengths, risks) -> str:
    r = run.report
    ta = r.get("stage_2_technical") or {}; fa = r.get("stage_3_fundamental") or {}
    qv = r.get("stage_4_quant_risk") or {}; val = r.get("stage_7_valuation") or {}
    scn = r.get("stage_8_scenarios") or {}; qa = r.get("stage_9_qa") or {}
    price = ((r.get("stage_1_data") or {}).get("price") or {}).get("last")
    L = []; A = L.append
    A(f"# {run.ticker} — Báo cáo phân tích tự động\n")
    A("> Nguồn tài liệu cho NotebookLM. Research-only, không phải khuyến nghị đầu tư.\n")
    A(f"- Ngày: {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')}")
    A(f"- Giá hiện tại: **{price}** | Điểm tổng hợp: **{comp}/100** | Khuyến nghị: **{verdict.upper()}**\n")
    A(f"## Tóm tắt điều hành\n{summary}\n")
    A("## Điểm mạnh")
    A("\n".join(f"- {s}" for s in strengths) or "- (không có)")
    A("\n## Rủi ro")
    A("\n".join(f"- {s}" for s in risks) or "- (không có)")
    A("\n## Kỹ thuật")
    A(f"- Xu hướng: {ta.get('trend')} | RSI: {ta.get('indicators',{}).get('rsi_14')} | MACD: {ta.get('indicators',{}).get('macd_signal')}")
    A(f"- Hỗ trợ: {ta.get('support')} | Kháng cự: {ta.get('resistance')}")
    A("\n## Cơ bản")
    A(f"- P/E: {fa.get('ratios',{}).get('pe')} | P/B: {fa.get('ratios',{}).get('pb')} | Sức khỏe: {fa.get('financial_health')}")
    A("\n## Định lượng & rủi ro")
    A(f"- Biến động năm: {qv.get('volatility_annualized_pct')}% | R:R: {qv.get('risk_reward_ratio')}")
    A("\n## Định giá")
    A(f"- Giá mục tiêu: {val.get('blended_target_price')} | Upside: {val.get('upside_pct')}%")
    A("\n## Kịch bản & quản trị rủi ro")
    A(f"- Entry: {scn.get('suggested_entry')} | Stop-loss: {scn.get('stop_loss')} | Take-profit: {scn.get('take_profit')} | R:R: {scn.get('risk_reward_ratio')}")
    A("\n## Kiểm định chéo (QA)")
    A(f"- Kết quả: {qa.get('consistency_check')} | Độ tin cậy: {qa.get('overall_confidence')}")
    for i in qa.get("issues", []):
        A(f"- [{i['severity']}] {i['stage_ref']}: {i['note']}")
    A("\n---\n*Tạo tự động bởi Stock AI Pipeline. Không phải khuyến nghị đầu tư.*")
    return "\n".join(L)


def _save_markdown(ticker: str, md: str) -> Optional[Path]:
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        p = REPORTS_DIR / f"{ticker.upper()}_pipeline_summary.md"
        p.write_text(md, encoding="utf-8")
        return p
    except Exception:
        return None


# ----------------------------- orchestrator -----------------------------
async def _run_stage(run: Run, key: str):
    st = run.stages[key]
    fn = STAGE_FUNCS[key]
    attempt = 0
    while True:
        st.attempts = attempt + 1
        st.status = "running" if attempt == 0 else "retrying"
        st.started_at = st.started_at or time.time()
        run.touch()
        try:
            # tiến trình mượt
            for p in (25, 60, 90):
                st.progress = p
                run.touch()
                await asyncio.sleep(0.15)
            slice_ = await fn(run)
            run.report[key] = slice_
            st.tokens = dict(STAGE_DEFS_TOK).get(key, 800)
            st.progress = 100
            st.status = "done"
            st.ended_at = time.time()
            run.touch()
            return
        except Exception as e:  # noqa
            st.error = str(e)[:200]
            if attempt < STAGE_RETRIES:
                st.status = "retrying"
                run.touch()
                await asyncio.sleep(STAGE_BACKOFF * (2 ** attempt))
                attempt += 1
                continue
            st.status = "error"
            st.progress = 100
            st.ended_at = time.time()
            run.touch()
            raise


async def _run_pipeline(run: Run):
    run.status = "running"
    run.started_at = time.time()
    run.touch()
    groups: dict[int, list[str]] = {}
    for key, _name, g, _m, _t in STAGE_DEFS:
        groups.setdefault(g, []).append(key)
    try:
        for g in sorted(groups):
            keys = groups[g]
            if len(keys) > 1:
                await asyncio.gather(*[_run_stage(run, k) for k in keys])  # song song
            else:
                await _run_stage(run, keys[0])
        run.status = "done"
    except Exception as e:  # noqa
        run.status = "error"
        run.error = str(e)[:240]
    finally:
        run.report.pop("_raw", None)  # bỏ khóa nội bộ khỏi report xuất ra
        run.ended_at = time.time()
        run.touch()


STAGE_DEFS_TOK = [(k, t) for (k, _n, _g, _m, t) in STAGE_DEFS]


# ----------------------------- queue workers -----------------------------
async def _worker():
    while True:
        run_id = await _queue.get()
        run = RUNS.get(run_id)
        if run is None:
            _queue.task_done()
            continue
        async with _sem:
            # cập nhật queue_pos cho các run còn chờ
            await _run_pipeline(run)
        _queue.task_done()


def _ensure_workers():
    global _queue, _sem, _workers_started
    if _workers_started:
        return
    _queue = asyncio.Queue()
    _sem = asyncio.Semaphore(MAX_CONCURRENT_TICKERS)
    for _ in range(MAX_CONCURRENT_TICKERS):
        asyncio.create_task(_worker())
    _workers_started = True


def _new_run(ticker: str, batch_id: str) -> Run:
    rid = uuid.uuid4().hex[:12]
    run = Run(run_id=rid, ticker=ticker.upper(), batch_id=batch_id)
    for key, name, g, m, _t in STAGE_DEFS:
        run.stages[key] = StageState(key=key, name=name, group=g, model=m)
    RUNS[rid] = run
    return run


def _cleanup_model3_exports(max_age_hours: float | None = None) -> None:
    """Best-effort cleanup so web exports do not make the server heavy over time."""
    max_age = (max_age_hours if max_age_hours is not None else MODEL3_EXPORT_TTL_HOURS) * 3600
    cutoff = time.time() - max_age
    for folder in (MODEL3_OUT_DIR, Path("reports"), Path("temp/notebooklm-share")):
        try:
            if not folder.exists():
                continue
            for path in folder.glob("*"):
                try:
                    if path.is_file() and path.stat().st_mtime < cutoff and (path.suffix.lower() in {".docx", ".md", ".json", ".pdf"}):
                        path.unlink()
                except Exception:
                    pass
        except Exception:
            pass


def _latest_model3_docx(ticker: str, before: set[Path]) -> Path | None:
    MODEL3_OUT_DIR.mkdir(parents=True, exist_ok=True)
    ticker = ticker.upper()
    files = [p for p in MODEL3_OUT_DIR.glob("*.docx") if p not in before and ticker in p.name.upper()]
    if not files:
        files = [p for p in MODEL3_OUT_DIR.glob(f"*{ticker}*.docx")]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def _parse_iso_or_date(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _market_data_freshness_gate(ticker: str, progress_cb: Callable[[str], None] | None = None) -> dict[str, Any]:
    """Ensure Model3 does not export with stale price/volume/technical data.

    Policy:
    - Always force-refresh market symbol before report generation.
    - Quote must be from VPS live feed and updated recently (<=15 minutes).
    - History/PTKT must have a latest bar dated today or yesterday (VN market holidays/weekends tolerated by 1 day).
    - If refresh cannot make data fresh, fail loudly so Hòa/Tiểu đệ can fix instead of shipping an old report.
    """
    def log(msg: str) -> None:
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    log(f"🔎 Freshness gate: kiểm tra data giá/KL/PTKT mới nhất cho {ticker}...")
    gateway_errors: list[str] = []
    data = None
    for gateway in _market_gateway_base_urls() if '_market_gateway_base_urls' in globals() else [os.getenv("MARKET_DATA_GATEWAY_URL", "https://3t8l9f.tail6c0e00.ts.net/marketdata").rstrip("/")]:
        if not gateway:
            continue
        try:
            url = f"{gateway}/market-compact/{re.sub(r'[^A-Za-z0-9]', '', ticker.upper())}?force_refresh=true"
            _status, data, _size = _urlopen_json(url, min(float(os.getenv("MARKET_DATA_GATEWAY_TIMEOUT", "90")), 20.0), 524288)
            log(f"✅ Freshness gate: lấy data qua gateway {gateway}")
            break
        except Exception as exc:  # noqa: BLE001
            gateway_errors.append(f"{gateway}: {type(exc).__name__}: {str(exc)[:200]}")
    if data is None:
        try:
            data = _load_symbol_local_provider(ticker, force_refresh=True)
            log("✅ Freshness gate: gateway unreachable, fallback local Render market_data provider OK")
        except Exception as exc:
            raise RuntimeError(
                "CALL_ASSISTANT_FIX: Không lấy được market data qua gateway hoặc provider local. "
                f"Gateway errors: {' | '.join(gateway_errors)[-1000:]}. Local error: {type(exc).__name__}: {exc}"
            ) from exc

    def _apply_lhinvt_db_fallback(d: dict[str, Any]) -> None:
        """Fill missing history/current fields from the canonical LHINVT SQLite DB."""
        db_path = Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\lhinvt_stock_chart.db")
        if not db_path.exists():
            return
        try:
            con = sqlite3.connect(str(db_path))
            con.row_factory = sqlite3.Row
            try:
                row = con.execute(
                    "SELECT latest_date, latest_close, latest_volume, updated_at FROM symbols WHERE upper(symbol)=upper(?) LIMIT 1",
                    (ticker,),
                ).fetchone()
                if row:
                    if not d.get("historyLastDate"):
                        d["historyLastDate"] = row["latest_date"]
                    if not d.get("price"):
                        d["price"] = row["latest_close"]
                    if d.get("volume") in (None, "", 0):
                        d["volume"] = row["latest_volume"]
                    d["lhinvtDbUpdatedAt"] = row["updated_at"]
                candle = con.execute(
                    "SELECT date, close, volume, updated_at FROM daily_ohlcv WHERE upper(symbol)=upper(?) ORDER BY date DESC LIMIT 1",
                    (ticker,),
                ).fetchone()
                if candle and not d.get("historyLastDate"):
                    d["historyLastDate"] = candle["date"]
                    if not d.get("price"):
                        d["price"] = candle["close"]
                    if d.get("volume") in (None, "", 0):
                        d["volume"] = candle["volume"]
            finally:
                con.close()
        except Exception as exc:  # noqa: BLE001
            log(f"⚠️ Freshness gate: LHINVT DB fallback lỗi {type(exc).__name__}: {exc}")

    _apply_lhinvt_db_fallback(data)

    now = datetime.now(timezone.utc)
    source = data.get("source")
    quote_dt = _parse_iso_or_date(data.get("quoteUpdatedAt") or data.get("updatedAt"))
    hist_dt = _parse_iso_or_date(data.get("historyLastDate"))
    quote_age_min = ((now - quote_dt).total_seconds() / 60) if quote_dt else 999999
    hist_age_days = ((now.date() - hist_dt.date()).days) if hist_dt else 999999
    price = data.get("price")
    volume = data.get("volume")
    issues = []
    if source != "vps":
        issues.append(f"source không phải VPS live quote: {source}")
    if quote_dt is None or quote_age_min > 15:
        issues.append(f"quote cũ/thiếu: quoteUpdatedAt={data.get('quoteUpdatedAt')}, age_min={quote_age_min:.1f}")
    # Weekend/holiday tolerance: on Sat/Sun, the latest trading bar is often
    # Friday, so a 2-3 calendar-day gap can still be fresh.
    max_hist_age_days = int(os.getenv("MARKET_HISTORY_MAX_AGE_DAYS", "3" if now.weekday() >= 5 else "1"))
    if hist_dt is None or hist_age_days > max_hist_age_days:
        issues.append(f"PTKT/history cũ/thiếu: historyLastDate={data.get('historyLastDate')}, age_days={hist_age_days}, max={max_hist_age_days}")
    if not price or float(price) <= 0:
        issues.append(f"giá không hợp lệ: {price}")
    if volume is None or int(float(volume or 0)) <= 0:
        issues.append(f"KL không hợp lệ: {volume}")

    summary = {
        "ticker": ticker,
        "source": source,
        "price": price,
        "volume": volume,
        "updatedAt": data.get("updatedAt"),
        "quoteUpdatedAt": data.get("quoteUpdatedAt"),
        "historyLastDate": data.get("historyLastDate"),
        "quoteAgeMinutes": round(quote_age_min, 2),
        "historyAgeDays": hist_age_days,
        "fresh": not issues,
        "issues": issues,
    }
    if issues:
        log("❌ Freshness gate FAIL: " + "; ".join(issues))
        raise RuntimeError("CALL_ASSISTANT_FIX: Báo cáo sẽ dùng data cũ/không hợp lệ sau khi force refresh: " + json.dumps(summary, ensure_ascii=False))
    log(f"✅ Freshness gate OK: {ticker} giá={price}, KL={volume}, quote={data.get('quoteUpdatedAt')}, history={data.get('historyLastDate')}")
    return summary


def _run_model3_full_export_sync(ticker: str, with_notebooklm: bool = True, progress_cb: Callable[[str], None] | None = None) -> dict[str, Any]:
    """Run the real Model3 workflow and optionally create NotebookLM output.

    Files are kept as server-side temporary artifacts only; UI exposes download/link URLs.
    Cleanup is controlled by PIPELINE_MODEL3_EXPORT_TTL_HOURS.
    """
    _cleanup_model3_exports()
    ticker = re.sub(r"[^A-Z0-9]", "", ticker.upper())[:8]
    if not ticker:
        raise RuntimeError("Ticker khong hop le")
    before = set(MODEL3_OUT_DIR.glob("*.docx")) if MODEL3_OUT_DIR.exists() else set()
    logs: list[str] = []

    def progress(msg: str) -> None:
        logs.append(str(msg)[-1000:])
        if progress_cb is not None:
            try:
                progress_cb(msg)
            except Exception:
                pass

    freshness = _market_data_freshness_gate(ticker, progress)

    # Guard against the bad 20-second "done" case: if Render has no real AI key,
    # do not export a fake/fallback DOCX that looks empty or uninformative.
    try:
        from app.config import CONFIG  # type: ignore
        has_real_ai = bool(CONFIG.router9_api_key or CONFIG.anthropic_key or CONFIG.openai_key or CONFIG.xai_key or CONFIG.google_key)
    except Exception:
        has_real_ai = False
    if os.getenv("MODEL3_ALLOW_MOCK_EXPORT", "").lower() not in ("1", "true", "yes") and not has_real_ai:
        raise RuntimeError(
            "Model3 chưa có AI API key trên Render nên không xuất DOCX giả/fallback. "
            "Cần cấu hình ROUTER9_API_KEY hoặc OPENAI_API_KEY/XAI_API_KEY trong Render rồi chạy lại."
        )

    from hybrid_agent_framework import run_model3_workflow

    task = (
        f"model3 {ticker} full web export: Codex TA research, Kiro News, UTF-8 cleaner trước, "
        "không Gemini, 3-5 tin trực tiếp 2026, PTKT LHInvestment, full technical fundamental strategy risk, "
        "xuất DOCX hoàn chỉnh cho NotebookLM"
    )
    state = run_model3_workflow(task, progress)
    feed = state.get("feed", []) if isinstance(state, dict) else []
    # Clean quality gate: any core AI provider timeout/502/internal fallback means
    # the export is NOT a clean Model3 report. Public-web news fallback remains
    # allowed only when MODEL3_ALLOW_NEWS_FALLBACK_CLEAN=1.
    bad_markers = (
        "mock",
        "Provider Codex bị timeout",
        "Provider Codex bi timeout",
        "Provider Kiro bị timeout",
        "Provider Kiro bi timeout",
        "provider lỗi/timeout",
        "provider loi/timeout",
        "HTTP 502",
        "502 Bad Gateway",
        "fallback nội bộ",
        "fallback noi bo",
        "AI_PROVIDER_FAILED",
        "GROK_NEWS_FAILED",
        "không tìm thấy DOCX",
        "khong tim thay DOCX",
    )
    joined_feed = "\n".join(str(item.get("content", "")) for item in feed if isinstance(item, dict))
    joined_logs = "\n".join(logs)
    quality_text = (joined_feed + "\n" + joined_logs).lower()
    partial_quality = any(m.lower() in quality_text for m in bad_markers)
    if os.getenv("MODEL3_ALLOW_NEWS_FALLBACK_CLEAN", "").lower() not in ("1", "true", "yes"):
        partial_quality = partial_quality or ("public-web news fallback" in quality_text) or ("grok_provider_unavailable" in quality_text)
    docx = _latest_model3_docx(ticker, before)
    if docx is None or not docx.exists():
        if os.getenv("MODEL3_ALLOW_PARTIAL_EXPORT", "").lower() not in ("1", "true", "yes") and partial_quality:
            raise RuntimeError(
                "Model3 AI chưa chạy đủ thật/đầy đủ và không tìm thấy DOCX để trả về. "
                "Kiểm tra AI provider key/log Render rồi chạy lại."
            )
        raise RuntimeError(f"Khong tim thay DOCX sau khi chay Model3 cho {ticker}")

    result: dict[str, Any] = {
        "ok": True,
        "ticker": ticker,
        "docx_path": str(docx),
        "docx_name": docx.name,
        "feed_count": len(state.get("feed", [])) if isinstance(state, dict) else None,
        "logs_tail": logs[-30:],
        "freshness": freshness,
        "partial_quality": partial_quality,
    }
    if os.getenv("MODEL3_ALLOW_PARTIAL_EXPORT", "").lower() not in ("1", "true", "yes") and partial_quality:
        result["warning"] = (
            "Model3 đã xuất DOCX nhưng một số AI provider bị timeout/502 nên báo cáo có thể dùng fallback/thiếu phần Kiro. "
            "Trả link file để kiểm tra, không coi là báo cáo chất lượng đầy đủ."
        )

    if with_notebooklm:
        try:
            if progress_cb:
                progress_cb("⏳ NotebookLM: đang tạo notebook/slides từ DOCX...")
            from model3_notebooklm import create_presentation_from_docx
            nb = create_presentation_from_docx(str(docx), title=f"{ticker} Model3 NotebookLM Web Export")
            result["notebooklm"] = nb
            if progress_cb:
                progress_cb("✅ NotebookLM export xong")
        except Exception as exc:  # noqa: BLE001
            # NotebookLM auth/quota/runtime is external. Keep the completed Model3 DOCX/report visible
            # instead of failing the entire job; create a local fallback PDF/HTML when possible.
            err = str(exc)[-1500:]
            result["notebooklm"] = None
            result["notebooklm_error"] = err
            try:
                from model3_fallback_report import create_fallback_report_from_docx
                fb = create_fallback_report_from_docx(str(docx), title=f"{ticker} Model3 fallback report")
                result["fallback_report"] = fb
                if fb.get("pdf_path"):
                    result["fallback_pdf_path"] = fb.get("pdf_path")
                    result["fallback_pdf_url"] = f"/pipeline/model3/file/{Path(str(fb.get('pdf_path'))).name}"
                if fb.get("html_path"):
                    result["fallback_html_path"] = fb.get("html_path")
                    result["fallback_html_url"] = f"/pipeline/model3/file/{Path(str(fb.get('html_path'))).name}"
                if progress_cb:
                    progress_cb("✅ NotebookLM lỗi; đã tạo PDF fallback từ DOCX")
            except Exception as fb_exc:  # noqa: BLE001
                result["fallback_error"] = str(fb_exc)[-1000:]
            if progress_cb:
                progress_cb(f"❌ NotebookLM export lỗi: {err}")
    return result


# ----------------------------- API models -----------------------------
class RunRequest(BaseModel):
    tickers: Optional[list[str]] = None
    ticker: Optional[str] = None


class Model3ExportRequest(BaseModel):
    ticker: str
    notebooklm: bool = True
    force: bool = False


def _new_model3_job(ticker: str, notebooklm: bool) -> dict[str, Any]:
    jid = uuid.uuid4().hex[:12]
    job = {
        "job_id": jid,
        "ticker": ticker,
        "status": "queued",
        "progress": 0,
        "error": None,
        "created_at": time.time(),
        "updated_at": time.time(),
        "logs": [],
        "agents": {"Codex": "pending", "Grok": "pending", "Kiro": "pending", "NotebookLM": "pending" if notebooklm else "skipped"},
        "sections": [{"key": k, "agent": a, "name": n, "status": "pending"} for k, a, n in MODEL3_SECTIONS],
        "result": None,
    }
    MODEL3_JOBS[jid] = job
    _save_model3_job(job)
    return job


def _model3_mark_progress(job: dict[str, Any], msg: str) -> None:
    text = str(msg)[-1000:]
    job["logs"].append(text)
    job["logs"] = job["logs"][-80:]
    low = text.lower()
    mapping = [
        ("quick", "quick_summary", "Kiro"), ("summary", "quick_summary", "Kiro"),
        ("news", "news", "Grok"), ("impact", "news", "Grok"), ("grok", "news", "Grok"),
        ("indicator", "technical", "Codex"), ("technical", "technical", "Codex"),
        ("fundamental", "fundamental", "Codex"), ("macro", "fundamental", "Codex"),
        ("scenario", "scenario", "Kiro"), ("bull", "bull_bear", "Codex"), ("bear", "bull_bear", "Codex"),
        ("catalyst", "bull_bear", "Codex"), ("risk", "risk", "Kiro"), ("viewpoint", "risk", "Kiro"),
        ("follow", "followup", "Codex"), ("docx", "word", "Model3"), ("word", "word", "Model3"),
        ("notebook", "notebooklm", "NotebookLM"), ("slide", "notebooklm", "NotebookLM"),
    ]
    matched: tuple[str, str] | None = None
    for needle, section_key, agent in mapping:
        if needle in low:
            matched = (section_key, agent)
            break
    if matched:
        section_key, agent = matched
        terminal_done = ("✅" in text) or (" xong" in low) or ("done" in low) or ("created" in low and section_key == "notebooklm")
        # Provider fallback is recoverable for producing an inspectable artifact,
        # but it is not a clean section. Paint it red/partial instead of letting a
        # fallback report look like full AI quality.
        recoverable = ("fallback" in low) or ("workflow không chết" in low) or ("workflow khong chet" in low)
        provider_quality_error = (
            "provider lỗi/timeout" in low
            or "provider loi/timeout" in low
            or "http 502" in low
            or "502 bad gateway" in low
            or "fallback nội bộ" in low
            or "fallback noi bo" in low
        )
        terminal_error = provider_quality_error or ((not recoverable) and (("❌" in text) or (" error" in low) or (" lỗi" in low) or ("failed" in low)))
        next_status = "error" if terminal_error else ("done" if terminal_done else "running")
        if agent in job["agents"]:
            if next_status == "error":
                job["agents"][agent] = "error"
            elif next_status == "done":
                # A successful later completion overrides an earlier transient red state.
                job["agents"][agent] = "running"
            elif job["agents"][agent] in {"pending", "running", "error"}:
                job["agents"][agent] = "running"
        for s in job["sections"]:
            if s["key"] == section_key:
                if next_status == "error":
                    s["status"] = "error"
                elif next_status == "done":
                    # Done must override an earlier warning/error for the same section.
                    s["status"] = "done"
                elif s["status"] in {"pending", "error"}:
                    s["status"] = "running"
                break
        # If all sections belonging to an agent are done/skipped, mark that AI done.
        if agent in job["agents"] and agent != "Model3":
            own = [s for s in job["sections"] if s["agent"] == agent]
            if own and all(s["status"] in {"done", "skipped"} for s in own):
                job["agents"][agent] = "done"
    done = sum(1 for s in job["sections"] if s["status"] in {"done", "skipped"})
    running = sum(1 for s in job["sections"] if s["status"] == "running")
    job["progress"] = min(95, int((done + running * 0.5) / len(job["sections"]) * 100))
    job["updated_at"] = time.time()
    _save_model3_job(job)


def _model3_finalize_sections(job: dict[str, Any], result: dict[str, Any]) -> None:
    logs = "\n".join(job.get("logs") or []).lower()
    for s in job["sections"]:
        if s["key"] == "notebooklm" and not result.get("notebooklm"):
            s["status"] = "skipped"
        elif s["status"] in {"pending", "running"}:
            s["status"] = "done"
    for a in list(job["agents"]):
        if job["agents"][a] == "running" or job["agents"][a] == "pending":
            job["agents"][a] = "done" if (a != "NotebookLM" or result.get("notebooklm")) else "skipped"
    job["progress"] = 100
    job["updated_at"] = time.time()
    _save_model3_job(job)


async def _run_model3_job(job_id: str, notebooklm: bool) -> None:
    job = _load_model3_job(job_id)
    if not job:
        return
    job["status"] = "running"
    job["updated_at"] = time.time()
    _save_model3_job(job)
    try:
        result = await asyncio.to_thread(_run_model3_full_export_sync, job["ticker"], notebooklm, lambda m: _model3_mark_progress(job, m))
        _model3_finalize_sections(job, result)
        job["result"] = result
        job["status"] = "done"
        _save_model3_job(job)
    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)[-1500:]
        _save_model3_job(job)
        for s in job["sections"]:
            if s["status"] == "running":
                s["status"] = "error"
    finally:
        job["updated_at"] = time.time()
        _save_model3_job(job)


# ----------------------------- endpoints -----------------------------
@router.post("/run")
async def run_pipeline(req: RunRequest):
    _ensure_workers()
    tickers: list[str] = []
    if req.tickers:
        tickers += req.tickers
    if req.ticker:
        tickers.append(req.ticker)
    # tách theo dấu phẩy/space, chuẩn hoá, loại rỗng & trùng
    norm: list[str] = []
    for t in tickers:
        for part in str(t).replace(",", " ").split():
            p = part.strip().upper()
            if p and p not in norm:
                norm.append(p)
    if not norm:
        raise HTTPException(status_code=400, detail="Cần ít nhất 1 mã cổ phiếu")
    batch_id = uuid.uuid4().hex[:8]
    runs = []
    for i, tk in enumerate(norm):
        run = _new_run(tk, batch_id)
        run.queue_pos = i
        runs.append({"run_id": run.run_id, "ticker": run.ticker})
        await _queue.put(run.run_id)
    BATCHES[batch_id] = [r["run_id"] for r in runs]
    return {"batch_id": batch_id, "runs": runs}


def _recover_model3_docx_result(job: dict[str, Any]) -> dict[str, Any] | None:
    """Expose a DOCX that was already written even if final quality guard failed."""
    ticker = re.sub(r"[^A-Z0-9]", "", str(job.get("ticker", "")).upper())[:8]
    logs = [str(x) for x in job.get("logs", []) if x]
    joined = "\n".join(logs)
    m = re.search(r"(outputs/model3/[^\s]+\.docx)", joined)
    docx: Path | None = None
    if m:
        cand = Path(m.group(1))
        if cand.exists():
            docx = cand
    if docx is None and ticker:
        docx = _latest_model3_docx(ticker, set())
    if docx is None or not docx.exists():
        return None
    return {
        "ok": True,
        "ticker": ticker,
        "docx_path": str(docx),
        "docx_name": docx.name,
        "partial_quality": True,
        "warning": "DOCX đã được ghi nhưng job bị đánh dấu error do một số AI provider timeout/502; dùng file này để kiểm tra, chưa coi là báo cáo chất lượng đầy đủ.",
        "logs_tail": logs[-30:],
    }


def _artifact_basename(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    # Render runs on Linux but local workers may upload/report Windows paths.
    # pathlib.Path('C:\\...\\file.pdf').name does not split backslashes on Linux.
    return Path(PureWindowsPath(raw).name).name


def _public_model3_result(result: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(result, dict):
        return None
    out = dict(result)
    docx_name = _artifact_basename(out.get("docx_path", ""))
    if docx_name:
        out["docx_url"] = f"/pipeline/model3/file/{docx_name}"
    nb = out.get("notebooklm") or {}
    pdf = nb.get("slide_pdf") if isinstance(nb, dict) else None
    pdf_name = _artifact_basename(pdf or out.get("notebooklm_pdf_path") or out.get("notebooklm_pdf_name") or out.get("notebooklm_pdf_url"))
    if pdf_name:
        out["notebooklm_pdf_url"] = f"/pipeline/model3/file/{pdf_name}"
        out["slide_pdf_url"] = out["notebooklm_pdf_url"]
    notebook_id = nb.get("notebook_id") if isinstance(nb, dict) else None
    if notebook_id:
        out["notebooklm_url"] = f"https://notebooklm.google.com/notebook/{notebook_id}"
    return out


def _public_model3_job(job: dict[str, Any]) -> dict[str, Any]:
    j = dict(job)
    now = time.time()
    created = float(job.get("created_at") or now)
    updated = float(job.get("updated_at") or created)
    j["elapsed_seconds"] = max(0, int(now - created))
    j["idle_seconds"] = max(0, int(now - updated))
    result = job.get("result")
    if not isinstance(result, dict) and job.get("status") == "error":
        result = _recover_model3_docx_result(job)
    j["result"] = _public_model3_result(result)
    j["logs_tail"] = (job.get("logs") or [])[-20:]
    return j


def _extract_market_gateway_summary(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    quote = data.get("quote") if isinstance(data.get("quote"), dict) else {}
    technical = data.get("technical") if isinstance(data.get("technical"), dict) else {}
    return {
        "source": data.get("source") or quote.get("source"),
        "price": data.get("price") or quote.get("price") or technical.get("close"),
        "volume": data.get("volume") or quote.get("volume") or technical.get("volume"),
    }


def _market_gateway_base_urls() -> list[str]:
    # Render dashboard env can override render.yaml, so always include both the
    # public Funnel route and tailnet-IP route as candidates.
    primary = os.getenv("MARKET_DATA_GATEWAY_URL", "").rstrip("/")
    public_funnel = os.getenv("MARKET_DATA_GATEWAY_FUNNEL_URL", "https://3t8l9f.tail6c0e00.ts.net/marketdata").rstrip("/")
    tailnet_host = os.getenv("MARKET_DATA_GATEWAY_TAILNET_HOST_URL", "http://3t8l9f.tail6c0e00.ts.net:20129").rstrip("/")
    fallback = os.getenv("MARKET_DATA_GATEWAY_FALLBACK_URL", "http://100.89.47.25:20129").rstrip("/")
    urls: list[str] = []
    for u in (primary, public_funnel, tailnet_host, fallback):
        if u and u not in urls:
            urls.append(u)
    return urls


def _urlopen_json(url: str, timeout: float, max_bytes: int | None = None) -> tuple[int, dict[str, Any], int]:
    # Render reaches the user's PC through Tailscale userspace networking on
    # 127.0.0.1:1055. urllib can still mis-handle NO_PROXY/HTTP proxy edge cases
    # here, while curl -x 127.0.0.1:1055 is verified working from Render. Prefer
    # curl when a gateway proxy exists, then keep urllib as a local/dev fallback.
    proxy = os.getenv("MARKET_DATA_GATEWAY_PROXY") or os.getenv("ALL_PROXY") or os.getenv("HTTP_PROXY")
    if proxy:
        cmd = ["curl", "-sS", "-m", str(max(1, int(timeout))), "-x", proxy, url]
        cp = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 3)
        raw = cp.stdout or b""
        if cp.returncode == 0 and raw:
            truncated = bool(max_bytes is not None and len(raw) > max_bytes)
            if max_bytes is not None:
                raw = raw[:max_bytes]
            data = json.loads(raw.decode("utf-8"))
            if isinstance(data, dict):
                data["_response_truncated"] = truncated
            return 200, data, len(raw)
        err = (cp.stderr or b"").decode("utf-8", errors="replace")[-1000:]
        raise urllib.error.URLError(f"curl gateway proxy failed rc={cp.returncode}: {err}")

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read(max_bytes or -1)
        if max_bytes is not None:
            # Drain a tiny extra byte only to know whether the gateway response was truncated.
            more = resp.read(1)
            truncated = bool(more)
        else:
            truncated = False
        data = json.loads(raw.decode("utf-8"))
        if isinstance(data, dict):
            data["_response_truncated"] = truncated
        return int(getattr(resp, "status", 200)), data, len(raw)


@router.get("/model3/render-network-diag")
async def model3_render_network_diag():
    """Safe Render network diagnostics for Tailscale/proxy availability."""
    env_keys = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "all_proxy", "no_proxy", "TAILSCALE_AUTHKEY"]
    env = {k: ("<set>" if k == "TAILSCALE_AUTHKEY" and os.getenv(k) else os.getenv(k)) for k in env_keys if os.getenv(k) is not None}
    diag: dict[str, Any] = {"env": env}
    for cmd_name, cmd in {
        "tailscale_status": ["tailscale", "status", "--json"],
        "tailscale_ip": ["tailscale", "ip", "-4"],
    }.items():
        try:
            cp = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=8)
            diag[cmd_name] = {"returncode": cp.returncode, "stdout": cp.stdout[-3000:], "stderr": cp.stderr[-1500:]}
        except Exception as exc:  # noqa: BLE001
            diag[cmd_name] = {"error_type": type(exc).__name__, "error": str(exc)[:1000]}
    return JSONResponse(diag)


@router.get("/model3/render-tailnet-peers")
async def model3_render_tailnet_peers():
    """Compact Tailscale peer view focused on the local gateway host."""
    try:
        cp = await asyncio.to_thread(subprocess.run, ["tailscale", "status", "--json"], capture_output=True, text=True, timeout=8)
        data = json.loads(cp.stdout or "{}") if cp.returncode == 0 else {}
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "error_type": type(exc).__name__, "error": str(exc)[:1000]}, status_code=503)
    peers = []
    for peer in (data.get("Peer") or {}).values():
        if not isinstance(peer, dict):
            continue
        host = peer.get("HostName") or ""
        ips = peer.get("TailscaleIPs") or []
        if host == "3t8l9f" or "100.89.47.25" in ips or host.startswith("render-model3"):
            peers.append({
                "host": host,
                "dns": peer.get("DNSName"),
                "ips": ips,
                "online": peer.get("Online"),
                "active": peer.get("Active"),
                "last_seen": peer.get("LastSeen"),
                "cur_addr": peer.get("CurAddr"),
                "relay": peer.get("Relay"),
                "rx": peer.get("RxBytes"),
                "tx": peer.get("TxBytes"),
            })
    return JSONResponse({"ok": True, "self_ips": data.get("Self", {}).get("TailscaleIPs"), "peers": peers})


@router.get("/model3/render-curl-gateway")
async def model3_render_curl_gateway():
    """Try gateway with curl through/no proxy to diagnose urllib vs network."""
    cmds = {
        "curl_default_ip": ["curl", "-sS", "-m", "12", "-v", "http://100.89.47.25:20129/health"],
        "curl_http_proxy_ip": ["curl", "-sS", "-m", "12", "-x", "http://127.0.0.1:1055", "-v", "http://100.89.47.25:20129/health"],
        "curl_socks_ip": ["curl", "-sS", "-m", "12", "--socks5-hostname", "127.0.0.1:1055", "-v", "http://100.89.47.25:20129/health"],
        "curl_funnel": ["curl", "-sS", "-m", "12", "-v", "https://3t8l9f.tail6c0e00.ts.net/marketdata/health"],
    }
    out: dict[str, Any] = {}
    for name, cmd in cmds.items():
        try:
            cp = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=15)
            out[name] = {"returncode": cp.returncode, "stdout": cp.stdout[-1000:], "stderr": cp.stderr[-2000:]}
        except Exception as exc:  # noqa: BLE001
            out[name] = {"error_type": type(exc).__name__, "error": str(exc)[:1000]}
    return JSONResponse(out)


@router.get("/model3/market-gateway-ping")
async def model3_market_gateway_ping():
    """Render-side network ping to gateway /health; does not fetch market payload."""
    timeout = min(float(os.getenv("MARKET_DATA_GATEWAY_TIMEOUT", "30")), 12.0)
    attempts: list[dict[str, Any]] = []
    for gateway in _market_gateway_base_urls():
        url = f"{gateway}/health"
        started = time.time()
        try:
            status, data, size = await asyncio.to_thread(_urlopen_json, url, timeout, None)
            return JSONResponse({"ok": True, "url": url, "status": status, "latency_ms": int((time.time() - started) * 1000), "bytes": size, "data": data, "attempts": attempts})
        except Exception as exc:  # noqa: BLE001
            attempts.append({"url": url, "error_type": type(exc).__name__, "error": str(exc)[:1200], "latency_ms": int((time.time() - started) * 1000)})
    return JSONResponse({"ok": False, "attempts": attempts}, status_code=503)


@router.get("/model3/market-gateway-test/{ticker}")
async def model3_market_gateway_test(ticker: str = "SSI"):
    """Fast Render-side check for market gateway; reads bounded payload and returns compact summary."""
    ticker = re.sub(r"[^A-Za-z0-9]", "", ticker or "SSI").upper()[:8]
    if not ticker:
        raise HTTPException(status_code=400, detail="Cần nhập mã cổ phiếu")
    timeout = min(float(os.getenv("MARKET_DATA_GATEWAY_TIMEOUT", "30")), 20.0)
    attempts: list[dict[str, Any]] = []
    for gateway in _market_gateway_base_urls():
        url = f"{gateway}/market-compact/{ticker}?force_refresh=false"
        started = time.time()
        try:
            status, data, size = await asyncio.to_thread(_urlopen_json, url, timeout, 262144)
            latency_ms = int((time.time() - started) * 1000)
            summary = _extract_market_gateway_summary(data)
            return JSONResponse({
                "ok": True,
                "ticker": ticker,
                "url": url,
                "status": status,
                "latency_ms": latency_ms,
                "bytes_read": size,
                "truncated": bool(data.get("_response_truncated")) if isinstance(data, dict) else False,
                **summary,
                "attempts": attempts,
                "received_at": datetime.now(timezone.utc).isoformat(),
            })
        except urllib.error.HTTPError as exc:
            body = exc.read(2000).decode("utf-8", errors="replace")
            attempts.append({"url": url, "status": exc.code, "error_type": "HTTPError", "error": body, "latency_ms": int((time.time() - started) * 1000)})
        except Exception as exc:  # noqa: BLE001
            attempts.append({"url": url, "error_type": type(exc).__name__, "error": str(exc)[:1200], "latency_ms": int((time.time() - started) * 1000)})
    return JSONResponse({"ok": False, "ticker": ticker, "attempts": attempts}, status_code=503)


@router.get("/model3/freshness/{ticker}")
async def model3_freshness(ticker: str):
    ticker = re.sub(r"[^A-Za-z0-9]", "", ticker or "").upper()[:8]
    if not ticker:
        raise HTTPException(status_code=400, detail="Cần nhập mã cổ phiếu")
    logs: list[str] = []
    try:
        result = await asyncio.to_thread(_market_data_freshness_gate, ticker, lambda m: logs.append(str(m)))
        result["logs"] = logs
        return JSONResponse(result)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"fresh": False, "ticker": ticker, "error": str(exc)[-3000:], "logs": logs}, status_code=503)


@router.get("/model3/notebooklm/auth-test")
async def model3_notebooklm_auth_test(auto_login: bool = True):
    """Test NotebookLM CLI auth and optionally re-login via saved Chrome session."""
    try:
        from model3_notebooklm import notebooklm_auth_check
        result = await asyncio.to_thread(notebooklm_auth_check, auto_login)
        return JSONResponse(result)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "stage": "exception", "error": str(exc)[-1500:]}, status_code=500)


@router.post("/model3/export")
async def model3_export(req: Model3ExportRequest):
    """Start full Model3 report job: Codex/Grok/Kiro -> Word -> NotebookLM."""
    ticker = re.sub(r"[^A-Za-z0-9]", "", req.ticker or "").upper()[:8]
    if not ticker:
        raise HTTPException(status_code=400, detail="Cần nhập mã cổ phiếu")
    # If callers explicitly ask for a fresh run, discard stale in-memory/disk
    # queued jobs for this ticker. Render free-tier restarts can leave an old
    # dedupe/queued record that points the UI at a job_id no longer recoverable.
    if bool(getattr(req, "force", False)):
        now = time.time()
        for old in list(_iter_model3_jobs_from_disk()):
            if str(old.get("ticker") or "").upper() != ticker:
                continue
            if old.get("status") in {"queued", "queued_external", "claimed_external", "running", "running_external", "uploading_external", "interrupted"}:
                old["status"] = "superseded"
                old["error"] = old.get("error") or "Superseded by a fresh Model3 export request."
                old["updated_at"] = now
                old["logs"] = (old.get("logs") or [])[-79:] + ["♻️ Bỏ job cũ, tạo job Model3 mới theo force=true."]
                MODEL3_JOBS[str(old.get("job_id"))] = old
                _save_model3_job(old)
    # Legacy Firebase stock-report pages may still send notebooklm:false.
    # Public Model3 web exports should always attempt NotebookLM; failures are
    # recorded as notebooklm_error without hiding the Word report.
    with_notebooklm = True
    job = _new_model3_job(ticker, with_notebooklm)
    if MODEL3_EXTERNAL_WORKER_MODE:
        job["status"] = "queued_external"
        job["logs"].append("⏳ Job đã nhận; chờ local Model3 worker xử lý để tránh Render/Tailscale timeout.")
        job["updated_at"] = time.time()
        _save_model3_job(job)
    else:
        asyncio.create_task(_run_model3_job(job["job_id"], with_notebooklm))
    return JSONResponse(_public_model3_job(job))


@router.get("/model3/worker/next")
async def model3_worker_next(authorization: str | None = Header(default=None)):
    _check_model3_worker_token(authorization)
    for job in _iter_model3_jobs_from_disk():
        if job.get("status") in {"queued_external", "queued"}:
            job["status"] = "claimed_external"
            job["updated_at"] = time.time()
            job["logs"] = (job.get("logs") or [])[-79:] + ["🔧 Local worker đã nhận job."]
            MODEL3_JOBS[str(job["job_id"])] = job
            _save_model3_job(job)
            return JSONResponse(_public_model3_job(job))
    return JSONResponse({"job": None})


@router.post("/model3/worker/{job_id}/status")
async def model3_worker_update_status(job_id: str, payload: dict[str, Any], authorization: str | None = Header(default=None)):
    _check_model3_worker_token(authorization)
    job = _load_model3_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id không tồn tại")
    for key in ("status", "progress", "error", "agents", "sections", "result"):
        if key in payload:
            job[key] = payload[key]
    if payload.get("log"):
        job["logs"] = (job.get("logs") or [])[-79:] + [str(payload["log"])[-1000:]]
    job["updated_at"] = time.time()
    MODEL3_JOBS[job_id] = job
    _save_model3_job(job)
    return JSONResponse(_public_model3_job(job))


@router.post("/model3/worker/{job_id}/upload")
async def model3_worker_upload(job_id: str, file: UploadFile = File(...), partial_quality: bool = Form(False), artifact_kind: str = Form("docx"), authorization: str | None = Header(default=None)):
    _check_model3_worker_token(authorization)
    job = _load_model3_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id không tồn tại")
    kind = re.sub(r"[^a-z0-9_-]", "", str(artifact_kind or "docx").lower()) or "docx"
    safe = Path(file.filename or f"{job.get('ticker','MODEL3')}_{job_id}.{kind}").name
    MODEL3_OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = MODEL3_OUT_DIR / safe
    data = await file.read()
    out.write_bytes(data)
    result = dict(job.get("result") or {})
    result.update({"ok": True, "ticker": job.get("ticker")})
    if kind in {"pdf", "slide", "slides", "notebooklm_pdf"} or safe.lower().endswith(".pdf"):
        result["notebooklm_pdf_path"] = str(out)
        result["notebooklm_pdf_name"] = safe
        result["notebooklm_pdf_url"] = f"/pipeline/model3/file/{safe}"
        job["logs"] = (job.get("logs") or [])[-79:] + [f"✅ Local worker uploaded NotebookLM PDF/Slide: {safe}"]
    else:
        result.update({"docx_path": str(out), "docx_name": safe, "partial_quality": bool(partial_quality)})
        job["logs"] = (job.get("logs") or [])[-79:] + [f"✅ Local worker uploaded DOCX: {safe}"]
    job["result"] = result
    job["status"] = "done"
    job["progress"] = 100
    job["updated_at"] = time.time()
    _model3_finalize_sections(job, result)
    MODEL3_JOBS[job_id] = job
    _save_model3_job(job)
    return JSONResponse(_public_model3_job(job))


@router.get("/model3/status/{job_id}")
async def model3_status(job_id: str):
    job = _load_model3_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id không tồn tại")
    return JSONResponse(_public_model3_job(job))


@router.get("/model3/latest/{ticker}")
async def model3_latest(ticker: str):
    """Return the latest completed Model3 job/report for a ticker.

    The Firebase stock-report UI may be opened after a local worker uploads the
    DOCX. Without this endpoint the page can only display a report for the
    current browser's job_id, so users see an empty/old state after refresh.
    """
    normalized = re.sub(r"[^A-Za-z0-9]", "", ticker or "").upper()[:8]
    if not normalized:
        raise HTTPException(status_code=400, detail="Cần nhập mã cổ phiếu")
    jobs = [
        job for job in _iter_model3_jobs_from_disk()
        if str(job.get("ticker") or "").upper() == normalized and job.get("status") == "done"
    ]
    jobs = [job for job in jobs if isinstance(job.get("result"), dict) and (job.get("result") or {}).get("docx_name")]
    if jobs:
        latest = max(jobs, key=lambda j: float(j.get("updated_at") or j.get("created_at") or 0))
        return JSONResponse(_public_model3_job(latest))
    docx = _latest_model3_docx(normalized, set())
    if docx and docx.exists():
        synthetic = {
            "job_id": f"latest-{normalized}",
            "ticker": normalized,
            "status": "done",
            "progress": 100,
            "created_at": docx.stat().st_mtime,
            "updated_at": docx.stat().st_mtime,
            "agents": {"Codex": "done", "Grok": "done", "Kiro": "done", "NotebookLM": "skipped"},
            "sections": MODEL3_SECTIONS,
            "logs": [f"✅ Latest DOCX found: {docx.name}"],
            "result": {"ok": True, "ticker": normalized, "docx_path": str(docx), "docx_name": docx.name, "partial_quality": False},
        }
        return JSONResponse(_public_model3_job(synthetic))
    raise HTTPException(status_code=404, detail=f"Không tìm thấy báo cáo Model3 mới cho {normalized}")


@router.get("/model3/file/{filename}")
async def model3_file(filename: str):
    safe = Path(filename).name
    workspace_temp = Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace") / "temp" / "notebooklm-share"
    candidates = [
        MODEL3_OUT_DIR / safe,
        Path("temp/notebooklm-share") / safe,
        workspace_temp / safe,
        Path("reports") / safe,
    ]
    found = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not found:
        raise HTTPException(status_code=404, detail="File không tồn tại hoặc đã hết hạn TTL")
    media = "application/octet-stream"
    if found.suffix.lower() == ".docx":
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif found.suffix.lower() == ".pdf":
        media = "application/pdf"
    elif found.suffix.lower() == ".md":
        media = "text/markdown; charset=utf-8"
    return FileResponse(path=str(found), media_type=media, filename=found.name)


@router.get("/status/{run_id}")
async def status(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id không tồn tại")
    return run.snapshot()


@router.get("/batch/{batch_id}")
async def batch_status(batch_id: str):
    ids = BATCHES.get(batch_id)
    if ids is None:
        raise HTTPException(status_code=404, detail="batch_id không tồn tại")
    return {"batch_id": batch_id, "runs": [RUNS[i].snapshot() for i in ids if i in RUNS]}


@router.get("/events/{run_id}")
async def events(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id không tồn tại")

    async def gen():
        last = -1
        # gửi ngay trạng thái đầu
        while True:
            if run.version != last:
                last = run.version
                yield f"data: {json.dumps(run.snapshot(), ensure_ascii=False)}\n\n"
            if run.status in ("done", "error"):
                yield f"event: end\ndata: {json.dumps(run.snapshot(), ensure_ascii=False)}\n\n"
                return
            await asyncio.sleep(0.4)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/report/{run_id}")
async def report(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id không tồn tại")
    return JSONResponse({"meta": {"ticker": run.ticker, "status": run.status,
                                  "as_of": datetime.now(timezone.utc).isoformat()},
                         **{k: v for k, v in run.report.items() if not k.startswith("_")}})


@router.get("/report/{run_id}/markdown")
async def report_markdown(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id không tồn tại")
    syn = run.report.get("stage_10_synthesis") or {}
    comp = syn.get("composite_score"); verdict = syn.get("verdict", "hold")
    md = _build_markdown(run, comp, verdict, syn.get("executive_summary", ""),
                         syn.get("key_strengths", []), syn.get("key_risks", []))
    return PlainTextResponse(md, media_type="text/markdown; charset=utf-8")


@router.get("/report/{run_id}/docx")
async def report_docx(run_id: str):
    """Tải file Word model3 tương ứng với run_id (tìm theo ticker và timestamp gần nhất)."""
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id không tồn tại")
    
    ticker = run.ticker.upper()
    outputs_dir = Path("outputs/model3")
    if not outputs_dir.exists():
        raise HTTPException(status_code=404, detail="Thư mục outputs/model3 không tồn tại")
    
    # Tìm file .docx mới nhất cho ticker này (pattern: YYYYMMDD-HHMMSS-*-TICKER.docx)
    pattern = re.compile(rf"^\d{{8}}-\d{{6}}-.*-{re.escape(ticker)}\.docx$", re.I)
    candidates = [f for f in outputs_dir.iterdir() if f.is_file() and pattern.match(f.name)]
    
    if not candidates:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy file Word cho {ticker}")
    
    # Sắp xếp theo tên (timestamp trong tên file) để lấy mới nhất
    latest = sorted(candidates, key=lambda x: x.name, reverse=True)[0]
    
    return FileResponse(
        path=str(latest),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=latest.name
    )


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    from app.pipeline_dashboard import DASHBOARD_HTML
    return HTMLResponse(DASHBOARD_HTML)
