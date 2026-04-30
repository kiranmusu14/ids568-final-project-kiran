#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="python3"
if [[ -x "venv/bin/python" ]]; then
  PYTHON_BIN="venv/bin/python"
elif command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
fi

# Bootstrap .env from the example so verification works on a fresh clone
# even if the user has not run `cp .env.example .env` yet.
if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
  echo "Bootstrapped .env from .env.example"
fi

ENV_FILE=".env"
[[ -f "$ENV_FILE" ]] || ENV_FILE=".env.example"
AUDIT_TRAIL_FILENAME=$(grep '^AUDIT_TRAIL_FILENAME=' "$ENV_FILE" 2>/dev/null | cut -d= -f2 || true)
AUDIT_TRAIL_FILENAME="${AUDIT_TRAIL_FILENAME:-audit-trail.json}"

required_files=(
  "README.md"
  "requirements.txt"
  "setup_env.sh"
  "setup_env.bat"
  "tests/test_core_behaviors.py"
  "src/monitoring/instrumentation.py"
  "src/monitoring/service.py"
  "src/ab_test/power_analysis.py"
  "src/ab_test/simulate_experiment.py"
  "src/drift/psi.py"
  "src/drift/analyze_drift.py"
  "src/governance/audit_trail.py"
  "docs/dashboard-interpretation.md"
  "docs/experiment-specification.md"
  "docs/recommendation-memo.md"
  "docs/model-card.md"
  "docs/risk-register.md"
  "docs/lineage-diagram.png"
  "docs/drift-diagnostic-report.md"
  "docs/governance-review.md"
  "docs/risk-matrix.md"
  "docs/system-boundary-diagram.png"
  "docs/cto-memo.md"
  "dashboards/prometheus.yml"
  "dashboards/grafana-dashboard.json"
  "logs/${AUDIT_TRAIL_FILENAME}"
  "visualizations/dashboard-export.png"
  "visualizations/grafana-ui-screenshot.png"
  "visualizations/metrics-endpoint-screenshot.png"
  "visualizations/ab-test-summary.png"
  "visualizations/drift-over-time.png"
)

echo "Checking required files..."
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "Missing required file: $file" >&2; exit 1; }
done

echo "Running Python syntax checks..."
"$PYTHON_BIN" -m py_compile \
  src/common/config.py \
  src/monitoring/instrumentation.py \
  src/monitoring/service.py \
  src/monitoring/simulate_traffic.py \
  src/ab_test/power_analysis.py \
  src/ab_test/simulate_experiment.py \
  src/drift/psi.py \
  src/drift/analyze_drift.py \
  src/governance/audit_trail.py \
  src/generate_project_artifacts.py \
  tests/test_core_behaviors.py

echo "Running unit tests..."
"$PYTHON_BIN" -m unittest discover -s tests

echo "Running artifact generation and component smoke tests..."
"$PYTHON_BIN" src/generate_project_artifacts.py
"$PYTHON_BIN" src/ab_test/power_analysis.py >/tmp/ids568_power_analysis.txt
"$PYTHON_BIN" src/ab_test/simulate_experiment.py >/tmp/ids568_ab_results.json
"$PYTHON_BIN" src/drift/analyze_drift.py >/tmp/ids568_drift_results.json
"$PYTHON_BIN" src/monitoring/simulate_traffic.py >/tmp/ids568_monitoring_simulation.txt
"$PYTHON_BIN" src/governance/audit_trail.py >/tmp/ids568_audit_trail.txt

echo "Checking RAG-specific generated evidence..."
grep -q "ids568_rag_ttft_seconds" dashboards/grafana-dashboard.json
grep -q "ids568_rag_token_throughput_tps" dashboards/grafana-dashboard.json
grep -q "ids568_rag_retrieval_score" dashboards/grafana-dashboard.json
grep -q "ids568_rag_response_length_tokens" dashboards/grafana-dashboard.json
grep -q "response_length_psi" visualizations/drift_summary.json
"$PYTHON_BIN" - <<'PY'
from src.monitoring.instrumentation import metrics_payload
from src.monitoring.service import _simulate_rag

result = _simulate_rag("Which controls mitigate prompt injection in the agent planner?")
assert "response_length_tokens" in result
payload = metrics_payload().decode("utf-8")
for metric in [
    "ids568_rag_ttft_seconds",
    "ids568_rag_token_throughput_tps",
    "ids568_rag_retrieval_score",
    "ids568_rag_response_length_tokens",
    "ids568_rag_query_length_tokens",
]:
    assert metric in payload, f"Missing emitted metric: {metric}"
print("RAG metrics emitted.")
PY

echo "Checking audit log integrity..."
"$PYTHON_BIN" - <<'PY'
from src.governance.audit_trail import verify_audit_log
assert verify_audit_log(), "Audit trail hash chain verification failed"
print("Audit trail integrity verified.")
PY

echo "Checking repository size..."
SIZE_MB=$(du -sm . | cut -f1)
if [[ "$SIZE_MB" -ge 100 ]]; then
  echo "Repository size ${SIZE_MB}MB exceeds 100MB limit" >&2
  exit 1
fi

echo "Submission sanity checks passed."
