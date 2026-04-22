# Recommendation Memo

The simulated A/B test produces a recommendation of `RUN_MORE_DATA`. The treatment (top-k=4) delivers a statistically significant improvement in task completion — 8.9% relative lift (absolute lift 5.5 pp, 95% CI [2.6 pp, 8.5 pp], z=3.68, p=0.00023) — and both the error-rate guardrail (1.75% vs. 3.0% ceiling) and cost guardrail ($0.0138 vs. $0.015 ceiling) pass cleanly. The statistical case for Variant B is strong.

The blocking issue is the p99 latency guardrail. Treatment p99 latency reached 2,616 ms against a 2,300 ms ceiling, a 14% overage. Because the guardrail failed, the decision rule in `src/ab_test/simulate_experiment.py` correctly outputs `RUN_MORE_DATA` rather than `SHIP_B`. This is the expected behavior: a better primary metric does not override an operational safety ceiling.

My recommendation is to collect one additional traffic sample targeted at latency-sensitive workloads. If p99 latency can be brought below 2,300 ms — through caching, timeout tuning, or routing improvements — then the statistical and guardrail evidence together support an unconditional `SHIP_B`. The next experiment should also segment long-form compliance queries separately, because that traffic slice is most likely to benefit from the additional retrieved evidence and is also the main driver of the latency overrun.
