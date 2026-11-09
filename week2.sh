#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "===== CAN SENTINEL | WEEK 2 ====="

if [[ ! -x .venv/bin/python ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

PY="$ROOT/.venv/bin/python"

if ! "$PY" -c 'import can, numpy, pandas, sklearn, joblib' >/dev/null 2>&1; then
    echo "Installing Week 2 Python dependencies..."
    "$PY" -m pip install -r week2/requirements.txt
fi

echo "Building simulated ECU programs..."
bash week2/build.sh

echo "Training the detection model using the demo baseline..."
"$PY" week2/train.py --csv can_traffic_demo.csv

echo
echo "Week 2 training completed."
echo "Model location: week2/results/isolation_forest.joblib"
echo "No attack traffic was started."
