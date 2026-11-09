#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "===== CAN SENTINEL | WEEK 4 ====="

if [[ ! -x .venv/bin/python ]]; then
    echo "Python environment missing. Run ./week2.sh first."
    exit 1
fi

PY="$ROOT/.venv/bin/python"

if [[ ! -f week4/models/baseline.json ]]; then
    echo "Week 4 baseline is missing. Creating it..."
    "$PY" week4/models/save_baseline.py
fi

echo
echo "[1/4] Running Week 4 test suite..."
bash week4/run_tests.sh

echo
echo "[2/4] Testing saved baseline..."
"$PY" week4/tests/test_saved_baseline.py

echo
echo "[3/4] Running model comparison..."
"$PY" week4/tests/test_model_comparison.py

echo
echo "[4/4] Exporting forensic incident report..."
"$PY" -m week4.reports.export_forensics

echo
echo "Week 4 checks completed."
echo "Forensic report: week4/reports/forensic_report.json"
