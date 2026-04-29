"""
FastAPI service for the IDS 568 Agentic RAG monitoring demonstration.

_simulate_rag() approximates the latency profile and retrieval behavior of a
real RAG pipeline using parameterized Gaussian distributions loaded from .env.
All metric observations happen inside this function so that a single /query
call exercises every LLM/RAG-specific Prometheus metric defined in
instrumentation.py.  The /metrics endpoint is consumed by Prometheus's
pull-based scraper.
"""
from __future__ import annotations

import random
import time
from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.common.config import settings
from src.monitoring.instrumentation import (
    EMPTY_RETRIEVAL_RATE,
    QUERY_LENGTH,
    REQUEST_COUNT,
    REQUEST_ERRORS,
    REQUEST_LATENCY,
    RETRIEVAL_SCORE,
    RESPONSE_LENGTH,
    TOKEN_THROUGHPUT,
    TTFT_SECONDS,
    metrics_payload,
)


app = FastAPI(title=settings.app_name, version=settings.app_version)


class QueryRequest(BaseModel):
    user_id: str
    query: str


def _simulate_rag(query: str, rng: random.Random | None = None) -> dict[str, Any]:
    rng = rng or random
    route = "/query"
    token_count = max(6, len(query.split()) * 2)
    retrieval_scores = sorted(
        [
            max(
                settings.sim_retrieval_score_min,
                min(
                    settings.sim_retrieval_score_max,
                    rng.gauss(settings.sim_retrieval_score_mean, settings.sim_retrieval_score_std),
                ),
            )
            for _ in range(settings.retrieval_top_k)
        ],
        reverse=True,
    )
    ttft = max(settings.sim_ttft_min_seconds, rng.gauss(settings.sim_ttft_mean_seconds, settings.sim_ttft_std_seconds))
    generation_seconds = max(
        settings.sim_generation_min_seconds,
        rng.gauss(settings.sim_generation_mean_seconds, settings.sim_generation_std_seconds),
    )
    total_latency = ttft + generation_seconds
    throughput = token_count / generation_seconds
    empty_retrieval = float(max(retrieval_scores) < settings.retrieval_score_threshold)
    response_tokens = max(
        settings.sim_response_token_min,
        round(
            rng.gauss(
                settings.sim_response_token_base + (token_count * settings.sim_response_token_query_multiplier),
                settings.sim_response_token_std,
            )
        ),
    )

    QUERY_LENGTH.labels(route=route).observe(token_count)
    RESPONSE_LENGTH.labels(route=route).observe(response_tokens)
    TTFT_SECONDS.labels(route=route).observe(ttft)
    REQUEST_LATENCY.labels(route=route).observe(total_latency)
    TOKEN_THROUGHPUT.labels(route=route).set(throughput)
    EMPTY_RETRIEVAL_RATE.labels(route=route).set(empty_retrieval)
    for score in retrieval_scores:
        RETRIEVAL_SCORE.labels(route=route).observe(score)

    answer = (
        "Compliance summary: retrieved policy evidence, tool checks, and answer synthesis "
        f"completed with prompt template {settings.prompt_template_version}."
    )
    return {
        "answer": answer,
        "ttft_seconds": round(ttft, 3),
        "latency_seconds": round(total_latency, 3),
        "token_throughput_tps": round(throughput, 2),
        "response_length_tokens": response_tokens,
        "retrieval_scores": [round(score, 3) for score in retrieval_scores],
        "empty_retrieval": bool(empty_retrieval),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


@app.post("/query")
def query(payload: QueryRequest) -> dict[str, Any]:
    route = "/query"
    started = time.perf_counter()
    try:
        result = _simulate_rag(payload.query)
        REQUEST_COUNT.labels(route=route, status="success").inc()
        return result
    except Exception as exc:
        REQUEST_COUNT.labels(route=route, status="error").inc()
        REQUEST_ERRORS.labels(route=route, error_type=type(exc).__name__).inc()
        raise
    finally:
        REQUEST_LATENCY.labels(route=route).observe(max(0.001, time.perf_counter() - started))


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(metrics_payload().decode("utf-8"))
