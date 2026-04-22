from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def _get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _get_float(name: str, default: float) -> float:
    return float(_get_env(name, str(default)))


def _get_int(name: str, default: int) -> int:
    return int(_get_env(name, str(default)))


def _get_tuple(name: str, default: tuple[float, ...]) -> tuple[float, ...]:
    raw = _get_env(name, ",".join(str(value) for value in default))
    return tuple(float(value.strip()) for value in raw.split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = _get_env("APP_NAME", "ids568-agentic-rag")
    app_version: str = _get_env("APP_VERSION", "1.0.0")
    app_host: str = _get_env("APP_HOST", "127.0.0.1")
    app_port: int = _get_int("APP_PORT", 8000)
    prometheus_namespace: str = _get_env("PROMETHEUS_NAMESPACE", "ids568_rag")
    request_latency_buckets: tuple[float, ...] = _get_tuple(
        "REQUEST_LATENCY_BUCKETS", (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)
    )
    ttft_buckets: tuple[float, ...] = _get_tuple("TTFT_BUCKETS", (0.05, 0.1, 0.2, 0.5, 1.0, 2.0))
    retrieval_score_threshold: float = _get_float("RETRIEVAL_SCORE_THRESHOLD", 0.55)
    empty_retrieval_alert_threshold: float = _get_float("EMPTY_RETRIEVAL_ALERT_THRESHOLD", 0.15)
    psi_moderate_threshold: float = _get_float("PSI_MODERATE_THRESHOLD", 0.10)
    psi_significant_threshold: float = _get_float("PSI_SIGNIFICANT_THRESHOLD", 0.20)
    prompt_template_version: str = _get_env("PROMPT_TEMPLATE_VERSION", "rag-v3")
    retrieval_top_k: int = _get_int("RETRIEVAL_TOP_K", 4)
    ab_alpha: float = _get_float("AB_ALPHA", 0.05)
    ab_power: float = _get_float("AB_POWER", 0.80)
    ab_baseline_task_success: float = _get_float("AB_BASELINE_TASK_SUCCESS", 0.61)
    ab_min_detectable_effect: float = _get_float("AB_MIN_DETECTABLE_EFFECT", 0.07)
    ab_latency_guardrail_ms: float = _get_float("AB_LATENCY_GUARDRAIL_MS", 2300)
    ab_error_guardrail_rate: float = _get_float("AB_ERROR_GUARDRAIL_RATE", 0.03)
    ab_cost_guardrail: float = _get_float("AB_COST_GUARDRAIL", 0.015)
    drift_reference_days: int = _get_int("DRIFT_REFERENCE_DAYS", 30)
    drift_current_days: int = _get_int("DRIFT_CURRENT_DAYS", 7)
    audit_hash_algorithm: str = _get_env("AUDIT_HASH_ALGORITHM", "sha256")
    kb_max_doc_age_days: int = _get_int("KB_MAX_DOC_AGE_DAYS", 90)


settings = Settings()
