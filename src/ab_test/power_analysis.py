"""
Sample-size calculation for a two-proportion A/B test.

Uses the arcsine-transformation formula (Cohen 1988) which is more
accurate than the normal-approximation formula for proportions near 0 or 1.
All experiment parameters are loaded from .env so the calculation stays
reproducible without hard-coded constants.
"""
from __future__ import annotations

import math
from statistics import NormalDist

from src.common.config import settings


def calculate_sample_size(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = settings.ab_alpha,
    power: float = settings.ab_power,
) -> int:
    treatment_rate = baseline_rate * (1 + minimum_detectable_effect)
    effect_size = 2 * (
        math.asin(math.sqrt(treatment_rate)) - math.asin(math.sqrt(baseline_rate))
    )
    normal = NormalDist()
    z_alpha = normal.inv_cdf(1 - alpha / 2)
    z_power = normal.inv_cdf(power)
    n_per_group = 2 * ((z_alpha + z_power) / effect_size) ** 2
    return math.ceil(n_per_group)


if __name__ == "__main__":
    n = calculate_sample_size(
        settings.ab_baseline_task_success,
        settings.ab_min_detectable_effect,
    )
    print(f"Required sample size per group: {n}")
