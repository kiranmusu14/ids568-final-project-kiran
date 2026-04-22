#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="python3"
if [[ -x "venv/bin/python" ]]; then
  PYTHON_BIN="venv/bin/python"
elif command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
fi

required_files=(
  "README.md"
  "requirements.txt"
  "setup_env.sh"
  "setup_env.bat"
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
  "logs/audit_trail.jsonl"
  "visualizations/dashboard-export.png"
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
  src/generate_project_artifacts.py

echo "Checking audit log integrity..."
"$PYTHON_BIN" - <<'PY'
from src.governance.audit_trail import verify_audit_log
assert verify_audit_log(), "Audit trail hash chain verification failed"
print("Audit trail integrity verified.")
PY

echo "Submission sanity checks passed."
