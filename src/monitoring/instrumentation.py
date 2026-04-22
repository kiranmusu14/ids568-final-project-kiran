from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from src.common.config import settings


REGISTRY = CollectorRegistry()

REQUEST_COUNT = Counter(
    "request_total",
    "Total requests handled by the RAG service",
    ["route", "status"],
    namespace=settings.prometheus_namespace,
    registry=REGISTRY,
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "End-to-end request latency",
    ["route"],
    namespace=settings.prometheus_namespace,
    buckets=settings.request_latency_buckets,
    registry=REGISTRY,
)
REQUEST_ERRORS = Counter(
    "request_errors_total",
    "Request failures by error class",
    ["route", "error_type"],
    namespace=settings.prometheus_namespace,
    registry=REGISTRY,
)
TTFT_SECONDS = Histogram(
    "ttft_seconds",
    "Time to first token for generated responses",
    ["route"],
    namespace=settings.prometheus_namespace,
    buckets=settings.ttft_buckets,
    registry=REGISTRY,
)
TOKEN_THROUGHPUT = Gauge(
    "token_throughput_tps",
    "Generated token throughput in tokens per second",
    ["route"],
    namespace=settings.prometheus_namespace,
    registry=REGISTRY,
)
RETRIEVAL_SCORE = Histogram(
    "retrieval_score",
    "Retriever chunk relevance scores",
    ["route"],
    namespace=settings.prometheus_namespace,
    buckets=(0.0, 0.2, 0.4, 0.55, 0.7, 0.85, 1.0),
    registry=REGISTRY,
)
EMPTY_RETRIEVAL_RATE = Gauge(
    "empty_retrieval_rate",
    "Fraction of requests with no chunk above the score threshold",
    ["route"],
    namespace=settings.prometheus_namespace,
    registry=REGISTRY,
)
QUERY_LENGTH = Histogram(
    "query_length_tokens",
    "Query length measured in approximate tokens",
    ["route"],
    namespace=settings.prometheus_namespace,
    buckets=(5, 10, 20, 40, 80, 120),
    registry=REGISTRY,
)


def metrics_payload() -> bytes:
    return generate_latest(REGISTRY)
