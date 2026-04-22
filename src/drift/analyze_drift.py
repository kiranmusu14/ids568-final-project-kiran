from __future__ import annotations

import json
import random

from src.common.config import ROOT, settings
from src.drift.psi import calculate_psi, classify_psi


def build_drift_report(seed: int = 568) -> dict[str, object]:
    rng = random.Random(seed)
    reference_query_length = [max(3.0, rng.gauss(18, 5)) for _ in range(1200)]
    current_query_length = [max(3.0, rng.gauss(24, 7)) for _ in range(600)]
    reference_retrieval = [min(0.99, max(0.05, rng.gauss(0.72, 0.08))) for _ in range(1200)]
    current_retrieval = [min(0.99, max(0.05, rng.gauss(0.61, 0.12))) for _ in range(600)]

    query_length_psi = calculate_psi(reference_query_length, current_query_length)
    retrieval_score_psi = calculate_psi(reference_retrieval, current_retrieval)

    windows = [
        {
            "window": f"week_{index}",
            "query_length_psi": value_a,
            "retrieval_score_psi": value_b,
            "empty_retrieval_rate": value_c,
        }
        for index, value_a, value_b, value_c in [
            (1, 0.04, 0.03, 0.04),
            (2, 0.06, 0.05, 0.05),
            (3, 0.08, 0.07, 0.06),
            (4, 0.11, 0.12, 0.08),
            (5, 0.16, 0.18, 0.11),
            (6, round(query_length_psi, 3), round(retrieval_score_psi, 3), 0.17),
        ]
    ]

    result = {
        "query_length": {
            "psi": query_length_psi,
            "severity": classify_psi(
                query_length_psi,
                settings.psi_moderate_threshold,
                settings.psi_significant_threshold,
            ),
        },
        "retrieval_score": {
            "psi": retrieval_score_psi,
            "severity": classify_psi(
                retrieval_score_psi,
                settings.psi_moderate_threshold,
                settings.psi_significant_threshold,
            ),
        },
        "windows": windows,
        "recommended_action": "Refresh the knowledge base, review new long-form queries, and tighten alerting on empty retrieval rate.",
    }
    output_path = ROOT / "visualizations" / "drift_summary.json"
    output_path.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build_drift_report(), indent=2))
