# Submission Checklist Audit

This audit cross-references the Final Project Specification, the Submission Checklist, and the Module 8 LLM/RAG adaptation guidance against the current repository contents.

## Checklist Audit

- PASS: Component 1 metrics instrumentation code exists in [src/monitoring/instrumentation.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/monitoring/instrumentation.py) and is integrated through [src/monitoring/service.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/monitoring/service.py).
- PASS: Component 1 collector configuration exists in [dashboards/prometheus.yml](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/dashboards/prometheus.yml).
- PASS: Component 1 dashboard configuration exists in [dashboards/grafana-dashboard.json](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/dashboards/grafana-dashboard.json).
- PASS: Component 1 dashboard screenshot/export exists in [visualizations/dashboard-export.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/visualizations/dashboard-export.png).
- PASS: Component 1 interpretation document exists in [docs/dashboard-interpretation.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/dashboard-interpretation.md) and addresses system health, bottlenecks, and alert triggers.
- PASS: Module 8 RAG monitoring adaptation is satisfied because TTFT, token throughput, and retrieval scores are instrumented in [src/monitoring/instrumentation.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/monitoring/instrumentation.py).

- PASS: Component 2 experiment specification exists in [docs/experiment-specification.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/experiment-specification.md).
- PASS: Component 2 hypothesis, success metrics, randomization method, and required sample size justification are explicitly documented in [docs/experiment-specification.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/experiment-specification.md).
- PASS: Component 2 power analysis code exists in [src/ab_test/power_analysis.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/ab_test/power_analysis.py).
- PASS: Component 2 simulation code generating A/B outcomes exists in [src/ab_test/simulate_experiment.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/ab_test/simulate_experiment.py).
- PASS: Component 2 statistical evaluation exists in [src/ab_test/simulate_experiment.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/ab_test/simulate_experiment.py) and the generated artifact [visualizations/ab_test_results.json](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/visualizations/ab_test_results.json).
- PASS: Component 2 recommendation memo exists in [docs/recommendation-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/recommendation-memo.md).

- PASS: Component 3 system card exists in [docs/model-card.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/model-card.md).
- PASS: Component 3 performance metrics, training data description, limitations, ethical risks, intended use, and out-of-scope use are covered in [docs/model-card.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/model-card.md).
- PASS: Component 3 lineage diagram exists in [docs/lineage-diagram.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/lineage-diagram.png).
- PASS: Component 3 risk register exists in [docs/risk-register.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-register.md) and includes bias, robustness, privacy, and compliance categories.
- PASS: Component 3 audit trail exists in [logs/audit_trail.jsonl](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/logs/audit_trail.jsonl).
- PASS: Component 3 tamper detection is implemented in [src/governance/audit_trail.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/governance/audit_trail.py) and exercised by [verify_submission.sh](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/verify_submission.sh).
- PASS: Module 8 system-card guidance is followed because [docs/model-card.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/model-card.md) documents observable system details rather than unverifiable vendor internals.

- PASS: Component 4 drift scripts exist in [src/drift/psi.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/drift/psi.py) and [src/drift/analyze_drift.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/drift/analyze_drift.py).
- PASS: Component 4 drift visualization exists in [visualizations/drift-over-time.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/visualizations/drift-over-time.png).
- PASS: Component 4 diagnostic report exists in [docs/drift-diagnostic-report.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/drift-diagnostic-report.md) and addresses the most-drifted features, impact, and recommended intervention.
- PASS: Module 8 RAG drift adaptation is satisfied because PSI is applied to query-length and retrieval-score distributions in [src/drift/analyze_drift.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/drift/analyze_drift.py).

- PASS: Component 5 system boundary diagram exists in [docs/system-boundary-diagram.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/system-boundary-diagram.png).
- PASS: Component 5 structured governance review exists in [docs/governance-review.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/governance-review.md) and covers data security, retrieval risks, hallucination points, tool-misuse pathways, and compliance concerns.
- PASS: Component 5 risk matrix exists in [docs/risk-matrix.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-matrix.md).
- PASS: Component 5 CTO memo exists in [docs/cto-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/cto-memo.md).
- PASS: Module 8 RAG-specific risk guidance is satisfied because LLM/RAG risks such as prompt injection, stale retrieval, and trust-boundary PII exposure are documented in [docs/risk-register.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-register.md), [docs/governance-review.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/governance-review.md), and [docs/risk-matrix.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-matrix.md).

- PASS: `README.md` exists at [README.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/README.md).
- PASS: The README includes a system overview, deliverable links, setup/reproduction instructions, and a lessons-learned reflection in [README.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/README.md).
- PASS: Pinned dependencies exist in [requirements.txt](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/requirements.txt).
- PASS: Mac/Linux setup automation exists in [setup_env.sh](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/setup_env.sh).
- PASS: Windows setup automation exists in [setup_env.bat](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/setup_env.bat).
- PASS: Thresholds and configuration are externalized through [.env.example](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/.env.example) and loaded by [src/common/config.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/common/config.py).
- PASS: Automated sanity checks exist in [verify_submission.sh](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/verify_submission.sh).
- PASS: Local verification succeeded via `./verify_submission.sh`, including file existence, Python syntax, and audit-log integrity checks.

- PARTIAL: The repository naming requirement appears intended, but this audit cannot independently confirm the final remote GitHub repository name beyond the local folder path.
- PARTIAL: The `git tag submission && git push --tags` checklist item is not yet proven by repository state in this local audit.
- PASS: Total repository size is under 100 MB based on local measurement of `38M`.

## Rubric Evidence Map

- Component 1 instrumentation evidence: [src/monitoring/instrumentation.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/monitoring/instrumentation.py)
- Component 1 dashboard evidence: [dashboards/grafana-dashboard.json](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/dashboards/grafana-dashboard.json), [visualizations/dashboard-export.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/visualizations/dashboard-export.png)
- Component 1 interpretation evidence: [docs/dashboard-interpretation.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/dashboard-interpretation.md)

- Component 2 design evidence: [docs/experiment-specification.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/experiment-specification.md)
- Component 2 simulation evidence: [src/ab_test/simulate_experiment.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/ab_test/simulate_experiment.py)
- Component 2 sample-size evidence: [src/ab_test/power_analysis.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/ab_test/power_analysis.py)
- Component 2 memo evidence: [docs/recommendation-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/recommendation-memo.md)

- Component 3 system card evidence: [docs/model-card.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/model-card.md)
- Component 3 lineage evidence: [docs/lineage-diagram.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/lineage-diagram.png)
- Component 3 risk evidence: [docs/risk-register.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-register.md)
- Component 3 audit evidence: [logs/audit_trail.jsonl](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/logs/audit_trail.jsonl), [src/governance/audit_trail.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/governance/audit_trail.py)

- Component 4 drift-code evidence: [src/drift/psi.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/drift/psi.py), [src/drift/analyze_drift.py](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/src/drift/analyze_drift.py)
- Component 4 visualization evidence: [visualizations/drift-over-time.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/visualizations/drift-over-time.png)
- Component 4 interpretation evidence: [docs/drift-diagnostic-report.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/drift-diagnostic-report.md)

- Component 5 diagram evidence: [docs/system-boundary-diagram.png](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/system-boundary-diagram.png)
- Component 5 review evidence: [docs/governance-review.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/governance-review.md)
- Component 5 matrix evidence: [docs/risk-matrix.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-matrix.md)
- Component 5 memo evidence: [docs/cto-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/cto-memo.md)

## Remaining Manual Fixes

1. Confirm the remote repository name exactly matches `ids568-final-project-[your_netid]`.
2. Run `git tag submission` and `git push --tags` when you are ready to submit.
3. Repository size has been measured locally at `38M`, which is within the checklist limit.
