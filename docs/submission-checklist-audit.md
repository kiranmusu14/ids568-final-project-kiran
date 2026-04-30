# Submission Checklist Audit

This audit cross-references the IDS 568 final-project checklist against the current repository contents using repo-relative evidence paths.

## Checklist Audit

- PASS: Component 1 metrics instrumentation is implemented in [src/monitoring/instrumentation.py](../src/monitoring/instrumentation.py) and integrated through [src/monitoring/service.py](../src/monitoring/service.py).
- PASS: Component 1 collector config exists in [dashboards/prometheus.yml](../dashboards/prometheus.yml).
- PASS: Component 1 Grafana dashboard config exists in [dashboards/grafana-dashboard.json](../dashboards/grafana-dashboard.json).
- PASS: Component 1 dashboard export exists in [visualizations/dashboard-export.png](../visualizations/dashboard-export.png).
- PASS: Component 1 interpretation covers health, bottlenecks, retrieval risk, and alert triggers in [docs/dashboard-interpretation.md](dashboard-interpretation.md).
- PASS: Component 1 RAG-specific monitoring covers TTFT, token throughput, retrieval score, query length, response length, and empty-retrieval rate.

- PASS: Component 2 experiment spec exists in [docs/experiment-specification.md](experiment-specification.md).
- PASS: Component 2 hypothesis, variants, metrics, randomization, sample size, duration, statistics, and stopping rules are documented in [docs/experiment-specification.md](experiment-specification.md).
- PASS: Component 2 power analysis is implemented in [src/ab_test/power_analysis.py](../src/ab_test/power_analysis.py).
- PASS: Component 2 simulation and decision logic are implemented in [src/ab_test/simulate_experiment.py](../src/ab_test/simulate_experiment.py).
- PASS: Component 2 generated output exists in [visualizations/ab_test_results.json](../visualizations/ab_test_results.json) and includes task success, statistical tests, latency/error/cost guardrails, retrieval-score guardrail, empty-retrieval guardrail, and groundedness spot-check output.
- PASS: Component 2 recommendation memo exists in [docs/recommendation-memo.md](recommendation-memo.md) and matches the generated `RUN_MORE_DATA` outcome.

- PASS: Component 3 system card exists in [docs/model-card.md](model-card.md).
- PASS: Component 3 system card covers performance metrics, training/knowledge data, limitations, ethical risks, intended use, and out-of-scope use.
- PASS: Component 3 lineage diagram exists in [docs/lineage-diagram.png](lineage-diagram.png).
- PASS: Component 3 risk register exists in [docs/risk-register.md](risk-register.md) and includes bias, robustness, privacy, and compliance categories.
- PASS: Component 3 audit trail exists in [logs/audit-trail.json](../logs/audit-trail.json) as a single valid JSON document.
- PASS: Component 3 tamper detection is implemented in [src/governance/audit_trail.py](../src/governance/audit_trail.py) and verified by [verify_submission.sh](../verify_submission.sh).

- PASS: Component 4 PSI and anomaly logic are implemented in [src/drift/psi.py](../src/drift/psi.py) and [src/drift/analyze_drift.py](../src/drift/analyze_drift.py).
- PASS: Component 4 drift visualization exists in [visualizations/drift-over-time.png](../visualizations/drift-over-time.png).
- PASS: Component 4 generated drift summary exists in [visualizations/drift_summary.json](../visualizations/drift_summary.json).
- PASS: Component 4 diagnostic report exists in [docs/drift-diagnostic-report.md](drift-diagnostic-report.md) and ties drift to grounding risk, model impact, and retrieval-first intervention.

- PASS: Component 5 system boundary diagram exists in [docs/system-boundary-diagram.png](system-boundary-diagram.png).
- PASS: Component 5 governance review exists in [docs/governance-review.md](governance-review.md) and covers data security, retrieval risks, hallucination risk points, tool misuse, and compliance.
- PASS: Component 5 risk matrix exists in [docs/risk-matrix.md](risk-matrix.md) with likelihood, severity, score, priority, and mitigations.
- PASS: Component 5 CTO memo exists in [docs/cto-memo.md](cto-memo.md) and gives executive-ready action items.

- PASS: README exists at [README.md](../README.md) and includes system overview, setup, reproduction, deliverable links, and lessons learned.
- PASS: Dependencies are pinned in [requirements.txt](../requirements.txt).
- PASS: Setup scripts exist for Mac/Linux and Windows: [setup_env.sh](../setup_env.sh), [setup_env.bat](../setup_env.bat).
- PASS: Automated verification exists in [verify_submission.sh](../verify_submission.sh).
- PASS: Repository size is under 100 MB.
- PASS: Git remote naming has been verified as `ids568-final-project-kiran`.
- PASS: Git tag `submission` is present locally and pushed to the configured remote.

## Rubric Evidence Map

- Component 1: [src/monitoring/instrumentation.py](../src/monitoring/instrumentation.py), [src/monitoring/service.py](../src/monitoring/service.py), [dashboards/grafana-dashboard.json](../dashboards/grafana-dashboard.json), [visualizations/dashboard-export.png](../visualizations/dashboard-export.png), [docs/dashboard-interpretation.md](dashboard-interpretation.md)
- Component 2: [docs/experiment-specification.md](experiment-specification.md), [src/ab_test/power_analysis.py](../src/ab_test/power_analysis.py), [src/ab_test/simulate_experiment.py](../src/ab_test/simulate_experiment.py), [visualizations/ab_test_results.json](../visualizations/ab_test_results.json), [docs/recommendation-memo.md](recommendation-memo.md)
- Component 3: [docs/model-card.md](model-card.md), [docs/lineage-diagram.png](lineage-diagram.png), [docs/risk-register.md](risk-register.md), [logs/audit-trail.json](../logs/audit-trail.json), [src/governance/audit_trail.py](../src/governance/audit_trail.py)
- Component 4: [src/drift/psi.py](../src/drift/psi.py), [src/drift/analyze_drift.py](../src/drift/analyze_drift.py), [visualizations/drift-over-time.png](../visualizations/drift-over-time.png), [visualizations/drift_summary.json](../visualizations/drift_summary.json), [docs/drift-diagnostic-report.md](drift-diagnostic-report.md)
- Component 5: [docs/system-boundary-diagram.png](system-boundary-diagram.png), [docs/governance-review.md](governance-review.md), [docs/risk-matrix.md](risk-matrix.md), [docs/cto-memo.md](cto-memo.md)

## Remaining Manual Notes

1. The project is intentionally synthetic: traffic, A/B outcomes, drift data, and diagrams are reproducible local artifacts rather than production exports.
2. Python 3.13 is the recommended interpreter for a clean install with the pinned dependency set.
