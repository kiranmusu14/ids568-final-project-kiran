# Experiment Specification

## Experiment Name

`rag_topk_experiment`

## Hypothesis

Increasing retrieval `top-k` from 3 to 4 will improve task completion for compliance research queries by at least 7% relative lift without violating latency, error-rate, or cost guardrails.

## Variants

- Variant A: `top-k=3`, current orchestration policy
- Variant B: `top-k=4`, same prompt template and answer policy

## Success Metrics

The experiment evaluates four distinct metric categories. Each category lists the specific metric used, how it is measured, the decision threshold, and which decision rule it feeds.

### 1. Business KPI — Task Completion Rate (primary)

- Metric: fraction of users who finish a compliance lookup without re-querying within the same session
- Measurement: `successes / (successes + reformulations)` aggregated per variant from session logs
- Threshold: ship if relative lift ≥ 7% with two-sided p-value < 0.05 and 95% CI excluding zero
- Decision feed: drives the primary `SHIP_B` / `KEEP_A` / `RUN_MORE_DATA` outcome

### 2. Accuracy — Retrieval Quality Score (secondary)

- Metric: mean retriever relevance score for the top-k chunks returned per query
- Measurement: average of `RETRIEVAL_SCORE` histogram observations from Prometheus per variant; in this repository's offline simulation, the equivalent per-variant means are emitted under `quality_metrics` in `visualizations/ab_test_results.json`
- Threshold: must not regress more than 0.05 absolute vs control; investigate if regression
- Decision feed: blocks `SHIP_B` if accuracy regresses materially even with positive primary lift

### 3. Latency — p99 End-to-End Response Time (guardrail)

- Metric: 99th percentile of `request_latency_seconds` per variant
- Measurement: Prometheus histogram_quantile over the experiment window
- Threshold: p99 ≤ `AB_LATENCY_GUARDRAIL_MS` (default 2,300 ms)
- Decision feed: hard guardrail — failure forces `RUN_MORE_DATA` regardless of primary lift

### 4. Groundedness — Empty Retrieval Rate + Evaluated Groundedness Spot Check

- Operational metric: `empty_retrieval_total / request_total` rate from Prometheus, mirrored in the simulation as per-variant empty-retrieval rates
- Threshold (operational): ≤ `EMPTY_RETRIEVAL_ALERT_THRESHOLD` (default 0.15)
- Evaluated metric: groundedness rubric score on a sampled review batch; the repository simulates this evaluated spot check because a human/LLM judge service is outside the local reproducibility scope
- Threshold (evaluated): mean groundedness ≥ 0.80 on the review sample
- Decision feed: groundedness is not the primary online decision metric because it requires an evaluator pipeline, but the operational empty-retrieval rate is treated as a guardrail and a regression in the evaluated sample blocks rollout

### Additional Operational Guardrails

- Request error rate ≤ `AB_ERROR_GUARDRAIL_RATE` (default 0.03)
- Cost per query ≤ `AB_COST_GUARDRAIL` (default $0.015)

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
