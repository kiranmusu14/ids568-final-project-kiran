# Repository Fix Summary

## Audit Outcome

The repository is aligned with the target structure listed in the prompt: every required path under `src/`, `docs/`, `dashboards/`, `logs/`, and `visualizations/` exists and is non-empty, all `.py` files compile, `verify_submission.sh` passes, and total size remains well under the 100 MB ceiling. The fixes below address the specific weaknesses called out in the prompt that automated existence checks would not catch.

## What Was Fixed

### 1. Double request-latency observation (`src/monitoring/service.py`, `src/monitoring/simulate_traffic.py`)

Before this change `REQUEST_LATENCY` was observed twice per `/query` request: once inside `_simulate_rag` using the simulated `total_latency`, and again in the route handler's `finally` block using the wall-clock boundary time. The histogram was inflated by 2× and the bucket distribution mixed two different latency definitions.

Fix: removed the simulated-latency observation from `_simulate_rag`. Latency is now recorded exactly once at the route boundary (`service.py`) for HTTP traffic and once per simulated request inside `simulate_traffic.run_simulation` (which never goes through the route). Added `REQUEST_COUNT` increment to the simulator so request count and latency are both populated when the simulator runs offline.

### 2. Empty-retrieval rate metric type (`src/monitoring/instrumentation.py`, `src/monitoring/service.py`, `dashboards/grafana-dashboard.json`)

Before: `EMPTY_RETRIEVAL_RATE` was a `Gauge` set to 0 or 1 per request. Because each request overwrote the gauge value, a scrape only ever saw the latest request's binary state — there was no actual rate.

Fix: replaced with `EMPTY_RETRIEVAL_TOTAL` (Counter), incremented once per empty-retrieval event. The Grafana panel now computes the rate in PromQL:

```
sum(rate(ids568_rag_empty_retrieval_total[5m])) / sum(rate(ids568_rag_request_total[5m]))
```

The labelset is pre-initialized at module load so the metric appears in `/metrics` immediately at value 0 (standard Prometheus pattern), preventing missing-series gaps in alerting.

### 3. Experiment specification — explicit four-category success metrics (`docs/experiment-specification.md`)

Before: success metrics were a 4-line bullet list mixing primary metric and guardrails. The prompt requires explicit coverage of **latency**, **accuracy**, **groundedness**, and **business KPI** with definitions, measurement, thresholds, and decision criteria.

Fix: rewrote the Success Metrics section into four labeled subsections — Business KPI (task completion), Accuracy (retrieval quality score), Latency (p99 guardrail), Groundedness (empty-retrieval rate + evaluated sample) — each stating the metric, how it is measured, its threshold, and how it feeds the decision rule.

### 4. `verify_submission.sh` resilience to missing `.env`

Before: the script greps `.env` for `AUDIT_TRAIL_FILENAME` with `2>/dev/null`, but downstream Python code (`load_dotenv`) silently uses defaults if `.env` is missing, and a fresh-clone reviewer who skipped the `cp .env.example .env` step had no signal.

Fix: the script now bootstraps `.env` from `.env.example` automatically when `.env` is absent, falls back to reading `.env.example` for the audit filename if `.env` is still unavailable, and uses `audit-trail.json` as the final default. The `set -e` policy is preserved.

### 5. Balanced A/B enrollment (`src/ab_test/simulate_experiment.py`)

Before: the simulator hashed exactly `2 * n_per_group` users and accepted the natural imbalance from deterministic randomization. That left the treatment arm slightly below the computed target in one run.

Fix: the simulator still uses stable hash assignment, but it now continues enrollment until both control and treatment reach the computed powered sample size. The generated output now has exactly 2,003 users per arm under the current configuration.

### 6. Actual Grafana UI evidence (`dashboards/grafana-dashboard.json`, `visualizations/grafana-ui-screenshot.png`)

Before: the repository included a generated dashboard export and a live `/metrics` screenshot, but not an imported Grafana UI capture.

Fix: added a stable dashboard UID, explicit Prometheus datasource references, grid positions, and safer zero-series PromQL for the stat panels. The new `visualizations/grafana-ui-screenshot.png` was captured from a live Grafana container backed by Prometheus scraping the FastAPI `/metrics` endpoint.

### 7. Unit tests (`tests/test_core_behaviors.py`, `verify_submission.sh`)

Before: the repo had smoke checks but no dedicated test directory.

Fix: added standard-library `unittest` coverage for A/B balanced enrollment, recommendation decision logic, PSI classification, and audit-trail hash-chain verification. `verify_submission.sh` now runs these tests before regenerating artifacts.

## What Was Verified

- `find . -name "*.py" -exec python -m py_compile {} \;` — clean across `src/` (excluding `venv/`)
- `python -m src.generate_project_artifacts` — exercised via `verify_submission.sh` (artifact generation step)
- `python -m unittest discover -s tests` — covers A/B decision logic, balanced assignment, PSI classification, and audit-trail verification
- `bash verify_submission.sh` — passes end-to-end: file existence, Python syntax, unit tests, smoke test, RAG metric emission (5 required metrics present in `/metrics`), audit-trail hash-chain integrity, repo size
- Direct check that `ids568_rag_empty_retrieval_total` appears in `/metrics` after running the simulator (52 empty-retrieval events recorded across 200 simulated requests)
- `du -sh .` → **43M**, well under the 100 MB ceiling

## What Was Not Changed (and Why)

- **PSI implementation (`src/drift/psi.py`)** — already correct, with Laplace smoothing for zero-bin safety, configurable `bins`, and a separate `classify_psi` function reading thresholds from settings. No edits needed.
- **`.env.example`** — already complete, mirrors every key in `Settings` with the same defaults.
- **README links** — already use repo-relative paths in the deliverable section after the previous fix pass; no absolute machine paths remain in the deliverable list.
- **Lineage and system-boundary diagrams** — both PNGs are present and exercised by `verify_submission.sh`'s file existence check; no programmatic regeneration was needed.
- **Audit trail (`logs/audit-trail.json`)** — already covers model deploy, prompt template change, KB update, governance approval, monitoring alert, and intervention; integrity verification passes.
- **Drift weekly windows** — `analyze_drift.py` generates per-window distributions and computes PSI per window; the report explains drifted features, impact, and intervention.
- **Model card** — already contains all six required sections (Intended Use, Out-of-Scope, Observable Performance, Training/Knowledge, Limitations, Ethical Risks) with a deployment configuration table.

## Remaining Limitations

- **Diagrams are generated PNGs** from `src/generate_project_artifacts.py`. They are reproducible, but the editable source is Python drawing code rather than mermaid/graphviz.
- **Groundedness is simulated locally.** The experiment now emits a groundedness spot-check score in `visualizations/ab_test_results.json`; a real human/LLM-judge service remains out of scope for the local submission.
- **`.env` is intentionally ignored.** The committed configuration source of truth is `.env.example`; `verify_submission.sh` bootstraps `.env` from the example when needed.
