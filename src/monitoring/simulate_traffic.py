from __future__ import annotations

import random
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.config import settings
from src.monitoring.service import _simulate_rag


QUERIES = [
    "What retention control applies to customer chat transcripts?",
    "Summarize the latest privacy policy change for vendor exports.",
    "Which controls mitigate prompt injection in the agent planner?",
    "Explain the escalation rule for unsupported compliance requests.",
    "What documents support the audit trail integrity design?",
]


def run_simulation(iterations: int = 200, seed: int = settings.simulation_seed) -> list[dict[str, object]]:
    rng = random.Random(seed)
    records = []
    for _ in range(iterations):
        query = rng.choice(QUERIES)
        records.append(_simulate_rag(query, rng=rng))
    return records


if __name__ == "__main__":
    traffic = run_simulation()
    failures = sum(1 for row in traffic if row["empty_retrieval"])
    print(f"Simulated requests: {len(traffic)}")
    print(f"Empty retrieval events: {failures}")
