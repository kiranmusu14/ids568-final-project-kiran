# IDS 568 Final Project: Agentic RAG Compliance Repository

This repository contains a production-style, agentic RAG pipeline submission for the IDS 568 Final Project. It is organized to match the required evidence locations from the project specification, submission checklist, and Module 8 adaptation guidance for LLM/RAG systems.

## System Overview

The system simulates a compliance-oriented agentic RAG workflow:

1. A FastAPI service receives a user query.
2. A retriever returns scored knowledge chunks.
3. The orchestration layer selects a tool plan.
4. The response generator emits an answer with simulated TTFT and token throughput.
5. Monitoring captures observable signals for operations, governance, and drift analysis.

## Repository Map

- `src/monitoring/`: FastAPI instrumentation, metrics emission, synthetic traffic
- `src/ab_test/`: power analysis, deterministic assignment, simulation, statistics
- `src/drift/`: PSI calculations, drift analysis, anomaly signals
- `src/governance/`: audit trail with tamper detection
- `docs/`: interpretation, memos, governance packet, risk review
- `dashboards/`: Prometheus and Grafana configuration
- `logs/`: audit trail outputs
- `visualizations/`: dashboard export, drift charts, experiment charts

## Setup

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

## Reproduction

The repository is designed to reproduce its outputs in under 10 minutes on a clean machine:

1. Create and activate the virtual environment.
2. Install pinned dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Run `python -m src.generate_project_artifacts`.
5. Run `./verify_submission.sh`.

The setup scripts prefer Python 3.13 when it is available because that interpreter path was validated during local reproducibility testing.

## Deliverable Links

- Monitoring interpretation: [docs/dashboard-interpretation.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/dashboard-interpretation.md)
- A/B experiment specification: [docs/experiment-specification.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/experiment-specification.md)
- A/B recommendation memo: [docs/recommendation-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/recommendation-memo.md)
- System card: [docs/model-card.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/model-card.md)
- Risk register: [docs/risk-register.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-register.md)
- Drift diagnostic report: [docs/drift-diagnostic-report.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/drift-diagnostic-report.md)
- Governance review: [docs/governance-review.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/governance-review.md)
- Risk matrix: [docs/risk-matrix.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/risk-matrix.md)
- CTO memo: [docs/cto-memo.md](/Users/kiran14/Documents/IDS%20568/Ids568-final-project/-ids568-final-project-kiran/docs/cto-memo.md)

## Lessons Learned

Across the milestone sequence, the biggest shift was from model-centric validation to system-centric accountability. The final repository connects observability, governance, experimentation, drift, and executive risk communication around one agentic RAG workflow so that operational decisions can be justified with observable evidence rather than intuition.
