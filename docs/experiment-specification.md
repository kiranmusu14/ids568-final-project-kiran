# Experiment Specification

## Experiment Name

`rag_topk_experiment`

## Hypothesis

Increasing retrieval `top-k` from 3 to 4 will improve task completion for compliance research queries by at least 7% relative lift without violating latency, error-rate, or cost guardrails.

## Variants

- Variant A: `top-k=3`, current orchestration policy
- Variant B: `top-k=4`, same prompt template and answer policy

## Success Metrics

- Primary metric: task completion rate without re-query
- Secondary observable metric: average retrieval score
- Guardrails: p99 latency, request error rate, and cost per query
- Governance note: groundedness is documented as an evaluated metric, but not used as the primary online metric because it would require annotation or an external judge pipeline

## Randomization Method

Users are deterministically assigned with a hash of `user_id` and experiment name. That keeps the assignment stable across repeated sessions and avoids contamination from users seeing both variants.

## Power Analysis

Inputs are loaded from `.env`:

- Baseline task success: `0.61`
- Minimum detectable effect: `0.07`
- Alpha: `0.05`
- Power: `0.80`

Using the two-proportion sample-size formula from Module 8, the required sample size is computed in `src/ab_test/power_analysis.py`. The simulation uses that computed sample size per group rather than a hand-entered constant. Under the current assumptions, the experiment needs roughly 2,000 users per arm (computed: 2,003), which is enough to detect a practical improvement while keeping false positives controlled.

## Duration Justification

Because this repository uses simulated traffic, duration is expressed as the amount of traffic required to collect the sample. In a live environment, duration would depend on daily eligible user volume. The correct operational framing is therefore "run until sample size is met" instead of "run for a fixed number of days regardless of exposure."

## Statistical Evaluation Plan

- Primary test: two-proportion z-test on task completion
- Confidence interval: 95% CI on absolute lift
- Decision rule:
  - Ship B if lift is positive, statistically significant, and all guardrails pass
  - Keep A if lift is negative
  - Run more data if lift is promising but guardrails or confidence remain inconclusive

## Multiple Comparisons and Stopping Rules

This experiment tests a single pre-registered primary hypothesis (task completion rate) against a fixed sample size computed before the experiment starts. Because there is one primary test and the sample size is fixed in advance, no multiple-comparisons correction (Bonferroni, Holm, or Benjamini-Hochberg) is required for the primary decision. If secondary metrics such as average retrieval score or cost per query were elevated to co-primary status after seeing the data, a correction would be mandatory to control the family-wise error rate.

The experiment uses a fixed-sample design rather than a sequential (group-sequential or always-valid) design. This means the primary z-test is applied once at full sample size, not at interim checkpoints. Peeking at results before sample collection is complete and stopping early based on significance would inflate the Type I error rate above the nominal α = 0.05 level. In a live deployment, a sequential design with an alpha-spending function (e.g., O'Brien-Fleming) would be appropriate if early stopping for efficacy is operationally desirable.
