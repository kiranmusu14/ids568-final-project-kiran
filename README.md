# IDS 568 Final Project: Agentic RAG Compliance Repository

This repository contains a production-style, agentic RAG pipeline submission for the IDS 568 Final Project. It is organized to match the required evidence locations from the project specification, submission checklist, and Module 8 adaptation guidance for LLM/RAG systems.

## System Overview

The system simulates a compliance-oriented agentic RAG workflow:

1. A FastAPI service receives a user query.
2. A retriever returns scored knowledge chunks.
3. The orchestration layer selects a tool plan.
4. The response generator emits an answer with simulated TTFT and token throughput.
5. Monitoring captures observable signals for operations, governance, and drift analysis.

Key design choices:
- All simulation parameters are externalized to `.env` — no hardcoded constants in source code.
- Prometheus metrics use a counter (`empty_retrieval_total`) for empty-retrieval events so the rate is computed correctly in Grafana via PromQL, not stored as a per-request gauge.
- Request latency is observed exactly once per request at the route boundary (or once per offline simulated request), preventing double-counting.
- The audit trail is a single valid JSON document (`logs/audit-trail.json`) with a hash-chained event array verifiable by `src/governance/audit_trail.py`.

## Repository Map

```
src/
  common/config.py          — centralized settings loaded from .env
  monitoring/
    instrumentation.py      — Prometheus metric definitions
    service.py              — FastAPI app with /query and /metrics endpoints
    simulate_traffic.py     — offline traffic simulator
  ab_test/
    power_analysis.py       — sample size calculation from .env parameters
    simulate_experiment.py  — A/B simulation with statistical evaluation
  drift/
    psi.py                  — PSI implementation with Laplace smoothing
    analyze_drift.py        — per-distribution drift + outlier detection
  governance/
    audit_trail.py          — hash-chained audit log writer and verifier
  generate_project_artifacts.py — regenerates all output artifacts

docs/                       — all written deliverables
dashboards/                 — Prometheus and Grafana configuration
logs/                       — audit trail output
visualizations/             — drift charts, dashboard exports, metrics endpoint screenshot, experiment charts
tests/                      — unit tests for statistics, drift, and audit behaviors
```

## Setup

Use Python 3.13 for the most reliable clean install. The pinned dependency set
uses `pydantic-core==2.23.4`, which has prebuilt wheels for Python 3.13; Python
3.14 may try to build from source and fail on systems without a compatible PyO3
toolchain. The setup script automatically prefers `python3.13` when it is
available.

Mac/Linux:

```bash
./setup_env.sh
cp .env.example .env
source venv/bin/activate
python -m src.generate_project_artifacts
./verify_submission.sh
```

Windows:

```bat
setup_env.bat
copy .env.example .env
venv\Scripts\activate
python -m src.generate_project_artifacts
bash verify_submission.sh
```

`verify_submission.sh` will bootstrap `.env` from `.env.example` automatically if `.env` is absent, so a fresh clone works without the manual copy step.

## Reproduction

The repository reproduces all outputs in under 10 minutes on a clean machine:

1. Create and activate the virtual environment via `setup_env.sh` / `setup_env.bat`.
2. Install pinned dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` (or let `verify_submission.sh` do it).
4. Run `python -m src.generate_project_artifacts`.
5. Run `python -m unittest discover -s tests`.
6. Run `./verify_submission.sh` — all checks must pass with "Submission sanity checks passed."

Individual scripts can also be run directly:

```bash
python src/ab_test/power_analysis.py
python src/ab_test/simulate_experiment.py
python src/drift/analyze_drift.py
python src/monitoring/simulate_traffic.py
python src/governance/audit_trail.py
python -m unittest discover -s tests
```

## Deliverable Links

### Component 1 — Production Monitoring Dashboard
- Instrumentation code: [src/monitoring/instrumentation.py](src/monitoring/instrumentation.py)
- FastAPI service: [src/monitoring/service.py](src/monitoring/service.py)
- Grafana dashboard config: [dashboards/grafana-dashboard.json](dashboards/grafana-dashboard.json)
- Prometheus config: [dashboards/prometheus.yml](dashboards/prometheus.yml)
- Dashboard export: [visualizations/dashboard-export.png](visualizations/dashboard-export.png)
- Live Grafana UI screenshot: [visualizations/grafana-ui-screenshot.png](visualizations/grafana-ui-screenshot.png)
- Live metrics endpoint screenshot: [visualizations/metrics-endpoint-screenshot.png](visualizations/metrics-endpoint-screenshot.png)
- Interpretation document: [docs/dashboard-interpretation.md](docs/dashboard-interpretation.md)

The live Grafana screenshot was produced by running the official Docker images `prom/prometheus:v2.55.1` and `grafana/grafana-oss:11.3.0` locally, with Prometheus scraping the FastAPI `/metrics` endpoint and Grafana importing `dashboards/grafana-dashboard.json`. The repository intentionally does not include a Dockerfile or compose file; Docker was used only as a local runtime for screenshot verification.

### Component 2 — A/B Test Design & Simulation
- Experiment specification: [docs/experiment-specification.md](docs/experiment-specification.md)
- Power analysis script: [src/ab_test/power_analysis.py](src/ab_test/power_analysis.py)
- Simulation script: [src/ab_test/simulate_experiment.py](src/ab_test/simulate_experiment.py)
- A/B results: [visualizations/ab_test_results.json](visualizations/ab_test_results.json)
- Recommendation memo: [docs/recommendation-memo.md](docs/recommendation-memo.md)

### Component 3 — Model Card & Governance Packet
- System card: [docs/model-card.md](docs/model-card.md)
- Lineage diagram: [docs/lineage-diagram.png](docs/lineage-diagram.png)
- Risk register: [docs/risk-register.md](docs/risk-register.md)
- Audit trail: [logs/audit-trail.json](logs/audit-trail.json)
- Audit trail script: [src/governance/audit_trail.py](src/governance/audit_trail.py)

### Component 4 — Data Integrity & Drift Detection
- PSI implementation: [src/drift/psi.py](src/drift/psi.py)
- Drift analysis script: [src/drift/analyze_drift.py](src/drift/analyze_drift.py)
- Drift visualization: [visualizations/drift-over-time.png](visualizations/drift-over-time.png)
- Drift summary: [visualizations/drift_summary.json](visualizations/drift_summary.json)
- Diagnostic report: [docs/drift-diagnostic-report.md](docs/drift-diagnostic-report.md)

### Component 5 — AI Risk Assessment
- System boundary diagram: [docs/system-boundary-diagram.png](docs/system-boundary-diagram.png)
- Governance review: [docs/governance-review.md](docs/governance-review.md)
- Risk matrix: [docs/risk-matrix.md](docs/risk-matrix.md)
- CTO memo: [docs/cto-memo.md](docs/cto-memo.md)

## Lessons Learned

Across the milestone sequence, the biggest shift was from model-centric validation to system-centric accountability. Building this repository made concrete several lessons that are easy to state but harder to internalize:

- **Observable operations metrics are not the same as evaluated quality metrics.** Latency and throughput tell you the serving layer is healthy; they say nothing about whether the retrieved evidence is correct. The drift analysis showed that retrieval quality can degrade while infrastructure metrics look fine.
- **PSI is the right tool for population-level drift; outlier detection misses it.** When an entire distribution shifts, z-score outlier rates barely move because the threshold shifts with the mean. PSI caught the structural change that per-request anomaly detection would have reported as normal.
- **Governance artifacts need to be machine-verifiable, not just present.** A hash-chained audit trail that fails verification is worse than no audit trail — it signals that someone tried and failed. Writing the verifier before the events forced a cleaner event schema.
- **A/B test guardrails matter as much as the primary metric.** The simulation produced a statistically significant lift but a latency guardrail failure. The decision rule correctly outputs `RUN_MORE_DATA` rather than `SHIP_B`, which is the operationally safe behavior.
- **Externalizing all parameters to configuration makes experiments reproducible.** Every simulation parameter lives in `.env`, so changing the experiment scenario requires no code edits and leaves a traceable record in configuration history.
