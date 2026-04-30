"""
A/B experiment simulation for the rag_topk_experiment.

Variant assignment uses a deterministic MD5 hash of (user_id, experiment_name)
so each user always sees the same variant across sessions, preventing
contamination from users experiencing both arms.  The simulation uses the
sample size computed by power_analysis.py rather than a hand-entered constant,
so changing .env parameters automatically adjusts the experiment scale.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from statistics import NormalDist

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ab_test.power_analysis import calculate_sample_size
from src.common.config import ROOT, settings


def _clamp_probability(value: float) -> float:
    return min(1.0, max(0.0, value))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round(percentile * (len(ordered) - 1)))
    return float(ordered[index])


def assign_variant(user_id: str, experiment_name: str, control_weight: float = 0.5) -> str:
    hash_value = hashlib.md5(f"{user_id}:{experiment_name}".encode("utf-8")).hexdigest()
    ratio = int(hash_value[:8], 16) / (16**8)
    return "control" if ratio < control_weight else "treatment"


def two_proportion_ztest(control_success: int, control_total: int, treatment_success: int, treatment_total: int) -> dict[str, float | bool]:
    p_control = control_success / control_total
    p_treatment = treatment_success / treatment_total
    pooled = (control_success + treatment_success) / (control_total + treatment_total)
    standard_error = (pooled * (1 - pooled) * ((1 / control_total) + (1 / treatment_total))) ** 0.5
    z_stat = (p_treatment - p_control) / standard_error
    normal = NormalDist()
    p_value = 2 * (1 - normal.cdf(abs(z_stat)))
    ci_half_width = 1.96 * (
        (p_control * (1 - p_control) / control_total)
        + (p_treatment * (1 - p_treatment) / treatment_total)
    ) ** 0.5
    return {
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < settings.ab_alpha),
        "absolute_lift": float(p_treatment - p_control),
        "relative_lift": float((p_treatment - p_control) / p_control),
        "ci_low": float((p_treatment - p_control) - ci_half_width),
        "ci_high": float((p_treatment - p_control) + ci_half_width),
    }


def run_experiment(seed: int = 568) -> dict[str, object]:
    rng = random.Random(seed)
    n_per_group = calculate_sample_size(
        settings.ab_baseline_task_success,
        settings.ab_min_detectable_effect,
    )
    total_users = n_per_group * 2
    user_ids = [f"user_{index:05d}" for index in range(total_users)]
    assignments = [assign_variant(user_id, "rag_topk_experiment") for user_id in user_ids]

    control_total = sum(1 for variant in assignments if variant == "control")
    treatment_total = total_users - control_total

    control_successes = [1 if rng.random() < settings.ab_baseline_task_success else 0 for _ in range(control_total)]
    treatment_rate = settings.ab_baseline_task_success * (
        1 + settings.ab_min_detectable_effect + settings.ab_treatment_extra_lift
    )
    treatment_successes = [1 if rng.random() < treatment_rate else 0 for _ in range(treatment_total)]

    control_latency = [
        rng.gauss(settings.ab_control_latency_mean_ms, settings.ab_control_latency_std_ms)
        for _ in range(control_total)
    ]
    treatment_latency = [
        rng.gauss(settings.ab_treatment_latency_mean_ms, settings.ab_treatment_latency_std_ms)
        for _ in range(treatment_total)
    ]
    treatment_error = [1 if rng.random() < settings.ab_treatment_error_rate else 0 for _ in range(treatment_total)]
    treatment_cost = [
        max(0.0, rng.gauss(settings.ab_treatment_cost_mean, settings.ab_treatment_cost_std))
        for _ in range(treatment_total)
    ]
    control_error = [1 if rng.random() < settings.ab_control_error_rate else 0 for _ in range(control_total)]
    control_cost = [
        max(0.0, rng.gauss(settings.ab_control_cost_mean, settings.ab_control_cost_std))
        for _ in range(control_total)
    ]
    control_retrieval_scores = [
        _clamp_probability(rng.gauss(settings.ab_control_retrieval_score_mean, settings.ab_control_retrieval_score_std))
        for _ in range(control_total)
    ]
    treatment_retrieval_scores = [
        _clamp_probability(rng.gauss(settings.ab_treatment_retrieval_score_mean, settings.ab_treatment_retrieval_score_std))
        for _ in range(treatment_total)
    ]
    control_empty_retrieval = [
        1 if rng.random() < settings.ab_control_empty_retrieval_rate else 0
        for _ in range(control_total)
    ]
    treatment_empty_retrieval = [
        1 if rng.random() < settings.ab_treatment_empty_retrieval_rate else 0
        for _ in range(treatment_total)
    ]
    review_n = min(settings.ab_groundedness_review_sample, control_total, treatment_total)
    control_groundedness = [
        _clamp_probability(rng.gauss(settings.ab_control_groundedness_mean, settings.ab_groundedness_std))
        for _ in range(review_n)
    ]
    treatment_groundedness = [
        _clamp_probability(rng.gauss(settings.ab_treatment_groundedness_mean, settings.ab_groundedness_std))
        for _ in range(review_n)
    ]

    stats_result = two_proportion_ztest(
        sum(control_successes),
        control_total,
        sum(treatment_successes),
        treatment_total,
    )
    p99_control_latency = _percentile(control_latency, 0.99)
    p99_latency = _percentile(treatment_latency, 0.99)
    error_guardrail = float(sum(treatment_error) / len(treatment_error)) <= settings.ab_error_guardrail_rate
    cost_guardrail = float(sum(treatment_cost) / len(treatment_cost)) <= settings.ab_cost_guardrail
    latency_guardrail = p99_latency <= settings.ab_latency_guardrail_ms
    retrieval_score_control = _mean(control_retrieval_scores)
    retrieval_score_treatment = _mean(treatment_retrieval_scores)
    retrieval_guardrail = (
        retrieval_score_treatment
        >= retrieval_score_control - settings.ab_retrieval_regression_guardrail
    )
    empty_retrieval_rate_control = float(sum(control_empty_retrieval) / len(control_empty_retrieval))
    empty_retrieval_rate_treatment = float(sum(treatment_empty_retrieval) / len(treatment_empty_retrieval))
    empty_retrieval_guardrail = empty_retrieval_rate_treatment <= settings.empty_retrieval_alert_threshold
    groundedness_control = _mean(control_groundedness)
    groundedness_treatment = _mean(treatment_groundedness)
    groundedness_guardrail = groundedness_treatment >= settings.ab_groundedness_guardrail

    all_guardrails_pass = all(
        [
            latency_guardrail,
            error_guardrail,
            cost_guardrail,
            retrieval_guardrail,
            empty_retrieval_guardrail,
            groundedness_guardrail,
        ]
    )

    if stats_result["significant"] and stats_result["absolute_lift"] > 0 and all_guardrails_pass:
        recommendation = "SHIP_B"
    elif stats_result["significant"] and stats_result["absolute_lift"] > 0:
        recommendation = "RUN_MORE_DATA"
    else:
        recommendation = "KEEP_A"

    result = {
        "sample_size_per_group": n_per_group,
        "control_total": control_total,
        "treatment_total": treatment_total,
        "control_success_rate": float(sum(control_successes) / len(control_successes)),
        "treatment_success_rate": float(sum(treatment_successes) / len(treatment_successes)),
        "p99_control_latency_ms": p99_control_latency,
        "p99_treatment_latency_ms": p99_latency,
        "control_error_rate": float(sum(control_error) / len(control_error)),
        "treatment_error_rate": float(sum(treatment_error) / len(treatment_error)),
        "control_cost_per_query": float(_mean(control_cost)),
        "treatment_cost_per_query": float(sum(treatment_cost) / len(treatment_cost)),
        "quality_metrics": {
            "control_retrieval_score": float(retrieval_score_control),
            "treatment_retrieval_score": float(retrieval_score_treatment),
            "retrieval_score_delta": float(retrieval_score_treatment - retrieval_score_control),
            "control_empty_retrieval_rate": empty_retrieval_rate_control,
            "treatment_empty_retrieval_rate": empty_retrieval_rate_treatment,
            "control_groundedness_score": float(groundedness_control),
            "treatment_groundedness_score": float(groundedness_treatment),
            "groundedness_review_sample": review_n,
        },
        "guardrails": {
            "latency_pass": latency_guardrail,
            "error_pass": error_guardrail,
            "cost_pass": cost_guardrail,
            "retrieval_score_pass": retrieval_guardrail,
            "empty_retrieval_pass": empty_retrieval_guardrail,
            "groundedness_pass": groundedness_guardrail,
        },
        "statistics": stats_result,
        "recommendation": recommendation,
    }
    output_path = ROOT / "visualizations" / "ab_test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2))
