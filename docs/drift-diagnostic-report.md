# Drift Diagnostic Report

The two features with the clearest drift are query length and retrieval-score distribution. The computed PSI values — query length PSI 1.09 and retrieval score PSI 0.82 — both substantially exceed the significant-action threshold of 0.20 configured in `.env`. A PSI above 0.20 signals structural change; values at 1.09 and 0.82 indicate the current traffic distribution has diverged severely from the reference window, not merely drifted at the margin.

The week-by-week window analysis shows a controlled escalation through weeks 1–5 (PSI 0.04 to 0.18) followed by a sharp jump in week 6 to observed levels. Query length shifted from a reference mean of approximately 18 tokens to a current mean of approximately 24 tokens with higher variance, and retrieval scores declined from a reference mean of ~0.72 to a current mean of ~0.61. The empty retrieval rate in week 6 reached 0.17, crossing the configured alert threshold of 0.15.

That combination changes the system’s likely failure mode. Rising query length paired with falling retrieval scores and a higher empty retrieval rate means the knowledge base is not covering newer, longer query shapes well. The downstream consequence is lower grounding quality, more incomplete answers, and a higher chance that the model fills evidence gaps with plausible synthesis.

## Outlier and Integrity Anomaly Analysis

In addition to PSI-based distributional drift, `src/drift/analyze_drift.py` performs outlier detection on both reference and current windows using a z-score threshold of 2.5 standard deviations, and an absolute floor check on retrieval scores (scores below 0.10 are treated as near-zero relevance integrity violations).

**Query length outliers:** The reference window (1,200 samples, mean 17.9 tokens, std 4.9) produced 17 outliers (1.42%). The current window (600 samples, mean 24.4 tokens, std 7.0) produced 8 outliers (1.33%). The outlier rate is stable, which confirms that the drift is a population-level shift — the whole distribution moved to longer queries — rather than a spike in isolated extreme values. No anomalous floor violations apply to query length.

**Retrieval score outliers and integrity check:** The reference window (mean 0.72, std 0.08) produced 17 outliers (1.42%). The current window (mean 0.61, std 0.12) produced 4 outliers (0.67%). The z-based outlier rate dropped because the distribution widened: more values are spread across the score range, making individual extremes less statistically unusual relative to the new mean. The floor violation check (score < 0.10) returned zero violations in both windows, which means the retriever has not produced catastrophically irrelevant results — the degradation is a continuous downward shift, not hard failures. The empty retrieval rate (captured in the monitoring layer) is the more sensitive leading indicator of hard retrieval failures than point-level score outliers.

**Integrity conclusion:** The drift is structural and distributional. It will not appear as isolated anomalous events in standard outlier detection because the entire population shifted. PSI is the right tool for this failure mode; z-score outlier rates alone would miss it. Both approaches together give a more complete picture: PSI detects population-level change, and the floor violation check confirms whether individual requests have crossed a hard grounding threshold.

## Recommended Intervention

The intervention should focus on retrieval before retraining or model replacement. The immediate steps are to refresh the indexed corpus, review chunking for long-form control narratives, and create a watchlist of newly emerging query themes. If PSI remains above the significant threshold after a corpus refresh, the next step is prompt and retriever tuning, followed by a fresh A/B test. Changing the model first is the wrong sequence because the observable evidence points to an upstream evidence-matching problem, not a generation-quality problem.
