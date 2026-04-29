from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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


def _clamp(values: list[float], lower: float, upper: float) -> list[float]:
    return [min(upper, max(lower, value)) for value in values]


def _window_series(final_value: float, initial_value: float) -> list[float]:
    count = max(2, settings.drift_window_count)
    return [
        round(initial_value + ((final_value - initial_value) * ((index / (count - 1)) ** 2)), 3)
        for index in range(count)
    ]


def build_drift_report(seed: int = 568) -> dict[str, object]:
    rng = random.Random(seed)
    reference_query_length = [
        max(3.0, rng.gauss(settings.drift_reference_query_length_mean, settings.drift_reference_query_length_std))
        for _ in range(settings.drift_reference_sample_size)
    ]
    current_query_length = [
        max(3.0, rng.gauss(settings.drift_current_query_length_mean, settings.drift_current_query_length_std))
        for _ in range(settings.drift_current_sample_size)
    ]
    reference_retrieval = _clamp(
        [
            rng.gauss(settings.drift_reference_retrieval_score_mean, settings.drift_reference_retrieval_score_std)
            for _ in range(settings.drift_reference_sample_size)
        ],
        0.05,
        0.99,
    )
    current_retrieval = _clamp(
        [
            rng.gauss(settings.drift_current_retrieval_score_mean, settings.drift_current_retrieval_score_std)
            for _ in range(settings.drift_current_sample_size)
        ],
        0.05,
        0.99,
    )
    reference_response_length = [
        max(
            settings.sim_response_token_min,
            rng.gauss(settings.drift_reference_response_length_mean, settings.drift_reference_response_length_std),
        )
        for _ in range(settings.drift_reference_sample_size)
    ]
    current_response_length = [
        max(
            settings.sim_response_token_min,
            rng.gauss(settings.drift_current_response_length_mean, settings.drift_current_response_length_std),
        )
        for _ in range(settings.drift_current_sample_size)
    ]

    query_length_psi = calculate_psi(reference_query_length, current_query_length)
    retrieval_score_psi = calculate_psi(reference_retrieval, current_retrieval)
    response_length_psi = calculate_psi(reference_response_length, current_response_length)

    # Outlier and integrity anomaly detection
    query_outliers_ref = detect_outliers(reference_query_length, z_threshold=2.5)
    query_outliers_cur = detect_outliers(current_query_length, z_threshold=2.5)
    # Retrieval scores below 0.1 are near-zero relevance — treated as integrity violations
    retrieval_outliers_ref = detect_outliers(reference_retrieval, z_threshold=2.5, floor=0.1)
    retrieval_outliers_cur = detect_outliers(current_retrieval, z_threshold=2.5, floor=0.1)
    response_outliers_ref = detect_outliers(reference_response_length, z_threshold=2.5)
    response_outliers_cur = detect_outliers(current_response_length, z_threshold=2.5)

    query_windows = _window_series(query_length_psi, settings.drift_initial_query_psi)
    retrieval_windows = _window_series(retrieval_score_psi, settings.drift_initial_retrieval_psi)
    response_windows = _window_series(response_length_psi, settings.drift_initial_response_length_psi)
    empty_windows = _window_series(
        settings.drift_current_empty_retrieval_rate,
        settings.drift_initial_empty_retrieval_rate,
    )
    windows = [
        {
            "window": f"week_{index + 1}",
            "query_length_psi": query_windows[index],
            "retrieval_score_psi": retrieval_windows[index],
            "response_length_psi": response_windows[index],
            "empty_retrieval_rate": empty_windows[index],
        }
        for index in range(len(query_windows))
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
        "response_length": {
            "psi": response_length_psi,
            "severity": classify_psi(
                response_length_psi,
                settings.psi_moderate_threshold,
                settings.psi_significant_threshold,
            ),
            "outliers_reference": response_outliers_ref,
            "outliers_current": response_outliers_cur,
        },
        "windows": windows,
        "recommended_action": "Refresh the knowledge base, review new long-form queries, and tighten alerting on empty retrieval rate.",
    }
    output_path = ROOT / "visualizations" / "drift_summary.json"
    output_path.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build_drift_report(), indent=2))
