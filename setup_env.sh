#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
if command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
fi

"$PYTHON_BIN" -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python - <<'PY'
import importlib
modules = [
    "fastapi",
    "uvicorn",
    "prometheus_client",
    "dotenv",
    "PIL",
]
for name in modules:
    importlib.import_module(name)
print("Environment verification passed.")
PY
