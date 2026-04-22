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
    TOKEN_THROUGHPUT,
    TTFT_SECONDS,
    metrics_payload,
)


app = FastAPI(title=settings.app_name, version=settings.app_version)


class QueryRequest(BaseModel):
    user_id: str
    query: str


def _simulate_rag(query: str) -> dict[str, Any]:
    route = "/query"
    token_count = max(6, len(query.split()) * 2)
    retrieval_scores = sorted([max(0.05, min(0.99, random.gauss(0.68, 0.18))) for _ in range(settings.retrieval_top_k)], reverse=True)
    ttft = max(0.04, random.gauss(0.19, 0.05))
    generation_seconds = max(0.2, random.gauss(1.35, 0.25))
    total_latency = ttft + generation_seconds
    throughput = token_count / generation_seconds
    empty_retrieval = float(max(retrieval_scores) < settings.retrieval_score_threshold)

    QUERY_LENGTH.labels(route=route).observe(token_count)
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
