"""Load cấu hình từ file .env."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from pathlib import Path
from dotenv import load_dotenv

# Web/R&D engine may run from LH BDS/bds_engine, while the working BDS credentials
# live in the original workspace BDS_Ver2_9router_test/.env. Load both without
# printing secrets.
load_dotenv()
_THIS = Path(__file__).resolve()
for _env in [
    _THIS.parents[2] / 'BDS_Ver2_9router_test' / '.env',
    _THIS.parents[2] / '.env.bds.local',
]:
    if _env.exists():
        load_dotenv(_env, override=False)


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    nineouter_api_key: str
    nineouter_base_url: str
    nineouter_model: str
    # Optional role-based 9router config. If empty, fallback to main config.
    bds_api_key: Optional[str]
    bds_base_url: Optional[str]
    bds_model: Optional[str]
    fast_api_key: Optional[str]
    fast_base_url: Optional[str]
    fast_model: Optional[str]
    report_api_key: Optional[str]
    report_base_url: Optional[str]
    report_model: Optional[str]
    max_concurrent_scrapes: int
    ai_timeout: int
    ai_fast_timeout: int


def _required(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v or v.startswith("your_"):
        raise RuntimeError(
            f"Biến môi trường {name} chưa được điền. "
            f"Anh mở file .env và điền giá trị thật vào."
        )
    return v


def _optional(name: str) -> str | None:
    v = os.getenv(name, "").strip()
    return v or None


def load_settings() -> Settings:
    return Settings(
        telegram_token=_required("TELEGRAM_BOT_TOKEN"),
        nineouter_api_key=_required("NINEROUTER_API_KEY"),
        nineouter_base_url=_required("NINEROUTER_BASE_URL").rstrip("/"),
        nineouter_model=_required("NINEROUTER_MODEL"),
        bds_api_key=_optional("NINEROUTER_BDS_API_KEY"),
        bds_base_url=(_optional("NINEROUTER_BDS_BASE_URL") or "").rstrip("/") or None,
        bds_model=_optional("NINEROUTER_BDS_MODEL"),
        fast_api_key=_optional("NINEROUTER_FAST_API_KEY"),
        fast_base_url=(_optional("NINEROUTER_FAST_BASE_URL") or "").rstrip("/") or None,
        fast_model=_optional("NINEROUTER_FAST_MODEL"),
        report_api_key=_optional("NINEROUTER_REPORT_API_KEY"),
        report_base_url=(_optional("NINEROUTER_REPORT_BASE_URL") or "").rstrip("/") or None,
        report_model=_optional("NINEROUTER_REPORT_MODEL"),
        max_concurrent_scrapes=int(os.getenv("MAX_CONCURRENT_SCRAPES", "3")),
        ai_timeout=int(os.getenv("AI_TIMEOUT", "300")),
        ai_fast_timeout=int(os.getenv("AI_FAST_TIMEOUT", "300")),
    )
