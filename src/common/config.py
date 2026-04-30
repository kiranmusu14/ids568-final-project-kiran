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
    llm_temperature: float = _get_float("LLM_TEMPERATURE", 0.2)
    chunk_size: int = _get_int("CHUNK_SIZE", 512)
    request_latency_buckets: tuple[float, ...] = _get_tuple(
        "REQUEST_LATENCY_BUCKETS", (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)
    )
    ttft_buckets: tuple[float, ...] = _get_tuple("TTFT_BUCKETS", (0.05, 0.1, 0.2, 0.5, 1.0, 2.0))
    response_length_buckets: tuple[float, ...] = _get_tuple(
        "RESPONSE_LENGTH_BUCKETS", (25, 50, 75, 100, 150, 200)
    )
    retrieval_score_threshold: float = _get_float("RETRIEVAL_SCORE_THRESHOLD", 0.55)
    empty_retrieval_alert_threshold: float = _get_float("EMPTY_RETRIEVAL_ALERT_THRESHOLD", 0.15)
    psi_moderate_threshold: float = _get_float("PSI_MODERATE_THRESHOLD", 0.10)
    psi_significant_threshold: float = _get_float("PSI_SIGNIFICANT_THRESHOLD", 0.20)
    prompt_template_version: str = _get_env("PROMPT_TEMPLATE_VERSION", "rag-v3")
    retrieval_top_k: int = _get_int("RETRIEVAL_TOP_K", 4)
    simulation_seed: int = _get_int("SIMULATION_SEED", 568)
    sim_retrieval_score_mean: float = _get_float("SIM_RETRIEVAL_SCORE_MEAN", 0.47)
    sim_retrieval_score_std: float = _get_float("SIM_RETRIEVAL_SCORE_STD", 0.16)
    sim_retrieval_score_min: float = _get_float("SIM_RETRIEVAL_SCORE_MIN", 0.05)
    sim_retrieval_score_max: float = _get_float("SIM_RETRIEVAL_SCORE_MAX", 0.99)
    sim_ttft_mean_seconds: float = _get_float("SIM_TTFT_MEAN_SECONDS", 0.19)
    sim_ttft_std_seconds: float = _get_float("SIM_TTFT_STD_SECONDS", 0.05)
    sim_ttft_min_seconds: float = _get_float("SIM_TTFT_MIN_SECONDS", 0.04)
    sim_generation_mean_seconds: float = _get_float("SIM_GENERATION_MEAN_SECONDS", 1.35)
    sim_generation_std_seconds: float = _get_float("SIM_GENERATION_STD_SECONDS", 0.25)
    sim_generation_min_seconds: float = _get_float("SIM_GENERATION_MIN_SECONDS", 0.2)
    sim_response_token_base: float = _get_float("SIM_RESPONSE_TOKEN_BASE", 42)
    sim_response_token_query_multiplier: float = _get_float("SIM_RESPONSE_TOKEN_QUERY_MULTIPLIER", 1.2)
    sim_response_token_std: float = _get_float("SIM_RESPONSE_TOKEN_STD", 8)
    sim_response_token_min: int = _get_int("SIM_RESPONSE_TOKEN_MIN", 24)
    ab_alpha: float = _get_float("AB_ALPHA", 0.05)
    ab_power: float = _get_float("AB_POWER", 0.80)
    ab_baseline_task_success: float = _get_float("AB_BASELINE_TASK_SUCCESS", 0.61)
    ab_min_detectable_effect: float = _get_float("AB_MIN_DETECTABLE_EFFECT", 0.07)
    ab_treatment_extra_lift: float = _get_float("AB_TREATMENT_EXTRA_LIFT", 0.015)
    ab_latency_guardrail_ms: float = _get_float("AB_LATENCY_GUARDRAIL_MS", 2300)
    ab_error_guardrail_rate: float = _get_float("AB_ERROR_GUARDRAIL_RATE", 0.03)
    ab_cost_guardrail: float = _get_float("AB_COST_GUARDRAIL", 0.015)
    ab_control_latency_mean_ms: float = _get_float("AB_CONTROL_LATENCY_MEAN_MS", 1980)
    ab_control_latency_std_ms: float = _get_float("AB_CONTROL_LATENCY_STD_MS", 180)
    ab_treatment_latency_mean_ms: float = _get_float("AB_TREATMENT_LATENCY_MEAN_MS", 2140)
    ab_treatment_latency_std_ms: float = _get_float("AB_TREATMENT_LATENCY_STD_MS", 200)
    ab_control_error_rate: float = _get_float("AB_CONTROL_ERROR_RATE", 0.018)
    ab_treatment_error_rate: float = _get_float("AB_TREATMENT_ERROR_RATE", 0.021)
    ab_control_cost_mean: float = _get_float("AB_CONTROL_COST_MEAN", 0.0116)
    ab_control_cost_std: float = _get_float("AB_CONTROL_COST_STD", 0.0011)
    ab_treatment_cost_mean: float = _get_float("AB_TREATMENT_COST_MEAN", 0.0138)
    ab_treatment_cost_std: float = _get_float("AB_TREATMENT_COST_STD", 0.0013)
    ab_control_retrieval_score_mean: float = _get_float("AB_CONTROL_RETRIEVAL_SCORE_MEAN", 0.71)
    ab_control_retrieval_score_std: float = _get_float("AB_CONTROL_RETRIEVAL_SCORE_STD", 0.06)
    ab_treatment_retrieval_score_mean: float = _get_float("AB_TREATMENT_RETRIEVAL_SCORE_MEAN", 0.74)
    ab_treatment_retrieval_score_std: float = _get_float("AB_TREATMENT_RETRIEVAL_SCORE_STD", 0.06)
    ab_retrieval_regression_guardrail: float = _get_float("AB_RETRIEVAL_REGRESSION_GUARDRAIL", 0.05)
    ab_control_empty_retrieval_rate: float = _get_float("AB_CONTROL_EMPTY_RETRIEVAL_RATE", 0.12)
    ab_treatment_empty_retrieval_rate: float = _get_float("AB_TREATMENT_EMPTY_RETRIEVAL_RATE", 0.10)
    ab_groundedness_review_sample: int = _get_int("AB_GROUNDEDNESS_REVIEW_SAMPLE", 200)
    ab_control_groundedness_mean: float = _get_float("AB_CONTROL_GROUNDEDNESS_MEAN", 0.82)
    ab_treatment_groundedness_mean: float = _get_float("AB_TREATMENT_GROUNDEDNESS_MEAN", 0.84)
    ab_groundedness_std: float = _get_float("AB_GROUNDEDNESS_STD", 0.05)
    ab_groundedness_guardrail: float = _get_float("AB_GROUNDEDNESS_GUARDRAIL", 0.80)
    drift_reference_days: int = _get_int("DRIFT_REFERENCE_DAYS", 30)
    drift_current_days: int = _get_int("DRIFT_CURRENT_DAYS", 7)
    drift_reference_sample_size: int = _get_int("DRIFT_REFERENCE_SAMPLE_SIZE", 1200)
    drift_current_sample_size: int = _get_int("DRIFT_CURRENT_SAMPLE_SIZE", 600)
    drift_reference_query_length_mean: float = _get_float("DRIFT_REFERENCE_QUERY_LENGTH_MEAN", 18)
    drift_reference_query_length_std: float = _get_float("DRIFT_REFERENCE_QUERY_LENGTH_STD", 5)
    drift_current_query_length_mean: float = _get_float("DRIFT_CURRENT_QUERY_LENGTH_MEAN", 24)
    drift_current_query_length_std: float = _get_float("DRIFT_CURRENT_QUERY_LENGTH_STD", 7)
    drift_reference_retrieval_score_mean: float = _get_float("DRIFT_REFERENCE_RETRIEVAL_SCORE_MEAN", 0.72)
    drift_reference_retrieval_score_std: float = _get_float("DRIFT_REFERENCE_RETRIEVAL_SCORE_STD", 0.08)
    drift_current_retrieval_score_mean: float = _get_float("DRIFT_CURRENT_RETRIEVAL_SCORE_MEAN", 0.61)
    drift_current_retrieval_score_std: float = _get_float("DRIFT_CURRENT_RETRIEVAL_SCORE_STD", 0.12)
    drift_reference_response_length_mean: float = _get_float("DRIFT_REFERENCE_RESPONSE_LENGTH_MEAN", 64)
    drift_reference_response_length_std: float = _get_float("DRIFT_REFERENCE_RESPONSE_LENGTH_STD", 14)
    drift_current_response_length_mean: float = _get_float("DRIFT_CURRENT_RESPONSE_LENGTH_MEAN", 92)
    drift_current_response_length_std: float = _get_float("DRIFT_CURRENT_RESPONSE_LENGTH_STD", 24)
    drift_window_count: int = _get_int("DRIFT_WINDOW_COUNT", 6)
    drift_initial_query_psi: float = _get_float("DRIFT_INITIAL_QUERY_PSI", 0.04)
    drift_initial_retrieval_psi: float = _get_float("DRIFT_INITIAL_RETRIEVAL_PSI", 0.03)
    drift_initial_response_length_psi: float = _get_float("DRIFT_INITIAL_RESPONSE_LENGTH_PSI", 0.02)
    drift_initial_empty_retrieval_rate: float = _get_float("DRIFT_INITIAL_EMPTY_RETRIEVAL_RATE", 0.04)
    drift_current_empty_retrieval_rate: float = _get_float("DRIFT_CURRENT_EMPTY_RETRIEVAL_RATE", 0.17)
    audit_hash_algorithm: str = _get_env("AUDIT_HASH_ALGORITHM", "sha256")
    audit_base_timestamp: str = _get_env("AUDIT_BASE_TIMESTAMP", "2026-04-22T21:10:23+00:00")
    audit_event_spacing_seconds: int = _get_int("AUDIT_EVENT_SPACING_SECONDS", 1)
    audit_trail_filename: str = _get_env("AUDIT_TRAIL_FILENAME", "audit-trail.json")
    kb_max_doc_age_days: int = _get_int("KB_MAX_DOC_AGE_DAYS", 90)


settings = Settings()
