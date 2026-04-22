from __future__ import annotations

import hashlib
import json
import random
from statistics import NormalDist

from src.ab_test.power_analysis import calculate_sample_size
from src.common.config import ROOT, settings


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
    treatment_rate = settings.ab_baseline_task_success * (1 + settings.ab_min_detectable_effect + 0.015)
    treatment_successes = [1 if rng.random() < treatment_rate else 0 for _ in range(treatment_total)]

    control_latency = [rng.gauss(1980, 180) for _ in range(control_total)]
    treatment_latency = [rng.gauss(2140, 200) for _ in range(treatment_total)]
    treatment_error = [1 if rng.random() < 0.021 else 0 for _ in range(treatment_total)]
    treatment_cost = [max(0.0, rng.gauss(0.0138, 0.0013)) for _ in range(treatment_total)]

    stats_result = two_proportion_ztest(
        sum(control_successes),
        control_total,
        sum(treatment_successes),
        treatment_total,
    )
    sorted_latency = sorted(treatment_latency)
    latency_index = min(len(sorted_latency) - 1, round(0.99 * (len(sorted_latency) - 1)))
    p99_latency = float(sorted_latency[latency_index])
    error_guardrail = float(sum(treatment_error) / len(treatment_error)) <= settings.ab_error_guardrail_rate
    cost_guardrail = float(sum(treatment_cost) / len(treatment_cost)) <= settings.ab_cost_guardrail
    latency_guardrail = p99_latency <= settings.ab_latency_guardrail_ms

    if stats_result["significant"] and stats_result["absolute_lift"] > 0 and all([latency_guardrail, error_guardrail, cost_guardrail]):
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
        "p99_treatment_latency_ms": p99_latency,
        "treatment_error_rate": float(sum(treatment_error) / len(treatment_error)),
        "treatment_cost_per_query": float(sum(treatment_cost) / len(treatment_cost)),
        "guardrails": {
            "latency_pass": latency_guardrail,
            "error_pass": error_guardrail,
            "cost_pass": cost_guardrail,
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
