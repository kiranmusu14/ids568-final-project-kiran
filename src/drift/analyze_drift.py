from __future__ import annotations

import json
import math
import random

from src.common.config import ROOT, settings
from src.drift.psi import calculate_psi, classify_psi


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float]) -> float:
    mu = _mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))


def detect_outliers(
    values: list[float],
    z_threshold: float = 2.5,
    floor: float | None = None,
) -> dict[str, object]:
    """Flag values beyond z_threshold standard deviations or below an absolute floor."""
    mu = _mean(values)
    sigma = _std(values) or 1.0
    high_z = [v for v in values if abs(v - mu) / sigma > z_threshold]
    floor_violations = [v for v in values if floor is not None and v < floor]
    return {
        "n_total": len(values),
        "n_outliers_z": len(high_z),
        "outlier_rate_z": round(len(high_z) / len(values), 4),
        "n_floor_violations": len(floor_violations),
        "floor_violation_rate": round(len(floor_violations) / len(values), 4) if floor is not None else None,
        "mean": round(mu, 4),
        "std": round(sigma, 4),
        "z_threshold": z_threshold,
        "floor": floor,
    }


def build_drift_report(seed: int = 568) -> dict[str, object]:
    rng = random.Random(seed)
    reference_query_length = [max(3.0, rng.gauss(18, 5)) for _ in range(1200)]
    current_query_length = [max(3.0, rng.gauss(24, 7)) for _ in range(600)]
    reference_retrieval = [min(0.99, max(0.05, rng.gauss(0.72, 0.08))) for _ in range(1200)]
    current_retrieval = [min(0.99, max(0.05, rng.gauss(0.61, 0.12))) for _ in range(600)]

    query_length_psi = calculate_psi(reference_query_length, current_query_length)
    retrieval_score_psi = calculate_psi(reference_retrieval, current_retrieval)

    # Outlier and integrity anomaly detection
    query_outliers_ref = detect_outliers(reference_query_length, z_threshold=2.5)
    query_outliers_cur = detect_outliers(current_query_length, z_threshold=2.5)
    # Retrieval scores below 0.1 are near-zero relevance — treated as integrity violations
    retrieval_outliers_ref = detect_outliers(reference_retrieval, z_threshold=2.5, floor=0.1)
    retrieval_outliers_cur = detect_outliers(current_retrieval, z_threshold=2.5, floor=0.1)

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
            "outliers_reference": query_outliers_ref,
            "outliers_current": query_outliers_cur,
        },
        "retrieval_score": {
            "psi": retrieval_score_psi,
            "severity": classify_psi(
                retrieval_score_psi,
                settings.psi_moderate_threshold,
                settings.psi_significant_threshold,
            ),
            "outliers_reference": retrieval_outliers_ref,
            "outliers_current": retrieval_outliers_cur,
        },
        "windows": windows,
        "recommended_action": "Refresh the knowledge base, review new long-form queries, and tighten alerting on empty retrieval rate.",
    }
    output_path = ROOT / "visualizations" / "drift_summary.json"
    output_path.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build_drift_report(), indent=2))
