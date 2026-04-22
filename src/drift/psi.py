"""
Population Stability Index (PSI) implementation.

PSI measures how much a distribution has shifted between a reference window
and a current window.  Conventional thresholds:
  PSI < 0.10  → stable (no action needed)
  0.10–0.20   → moderate drift (investigate)
  PSI ≥ 0.20  → significant drift (act immediately)

Laplace smoothing (+1 pseudo-count per bin) avoids log(0) when a bin is
empty in either window, which is common with small sample sizes.
"""
from __future__ import annotations

import math


def _build_edges(reference: list[float], bins: int) -> list[float]:
    minimum = min(reference)
    maximum = max(reference)
    width = (maximum - minimum) / bins or 1.0
    return [minimum + (index * width) for index in range(bins + 1)]


def _histogram(values: list[float], edges: list[float]) -> list[int]:
    counts = [0 for _ in range(len(edges) - 1)]
    for value in values:
        for index in range(len(edges) - 1):
            lower = edges[index]
            upper = edges[index + 1]
            if index == len(edges) - 2:
                in_bin = lower <= value <= upper
            else:
                in_bin = lower <= value < upper
            if in_bin:
                counts[index] += 1
                break
    return counts


def calculate_psi(reference: list[float], current: list[float], bins: int = 10) -> float:
    edges = _build_edges(reference, bins)
    ref_counts = _histogram(reference, edges)
    cur_counts = _histogram(current, edges)
    ref_pct = [(count + 1) / (len(reference) + bins) for count in ref_counts]
    cur_pct = [(count + 1) / (len(current) + bins) for count in cur_counts]
    return sum((cur - ref) * math.log(cur / ref) for ref, cur in zip(ref_pct, cur_pct))


def classify_psi(value: float, moderate_threshold: float, significant_threshold: float) -> str:
    if value >= significant_threshold:
        return "significant"
    if value >= moderate_threshold:
        return "moderate"
    return "stable"
