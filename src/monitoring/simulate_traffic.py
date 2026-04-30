from __future__ import annotations

import random
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.config import settings
from src.monitoring.instrumentation import REQUEST_COUNT, REQUEST_LATENCY
from src.monitoring.service import _simulate_rag


QUERIES = [
    "What retention control applies to customer chat transcripts?",
    "Summarize the latest privacy policy change for vendor exports.",
    "Which controls mitigate prompt injection in the agent planner?",
    "Explain the escalation rule for unsupported compliance requests.",
    "What documents support the audit trail integrity design?",
]


def run_simulation(iterations: int = 200, seed: int = settings.simulation_seed) -> list[dict[str, object]]:
    """Drive the RAG simulation outside the FastAPI route.

    The route handler in service.py records request latency once at the
    boundary; when running the simulator directly we have to record it
    here so the metric is exercised exactly once per simulated request.
    """
    rng = random.Random(seed)
    records = []
    for _ in range(iterations):
        query = rng.choice(QUERIES)
        result = _simulate_rag(query, rng=rng)
        REQUEST_LATENCY.labels(route="/query").observe(result["latency_seconds"])
        REQUEST_COUNT.labels(route="/query", status="success").inc()
        records.append(result)
    return records


if __name__ == "__main__":
    traffic = run_simulation()
    failures = sum(1 for row in traffic if row["empty_retrieval"])
    print(f"Simulated requests: {len(traffic)}")
    print(f"Empty retrieval events: {failures}")
