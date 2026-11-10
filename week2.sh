#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "===== CAN SENTINEL | WEEK 2 ====="

echo "[1/5] Checking system dependencies..."
if ! command -v python3 >/dev/null 2>&1 || ! command -v gcc >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip build-essential
fi

echo "[2/5] Preparing Python environment..."
if [[ ! -x .venv/bin/python ]]; then
    python3 -m venv .venv
fi

PY="$ROOT/.venv/bin/python"

echo "[3/5] Installing/checking Python requirements..."
"$PY" -m pip install -r week2/requirements.txt

echo "[4/5] Building simulated ECU programs..."
bash week2/build.sh

echo "[5/5] Training Isolation Forest..."
"$PY" week2/train.py --csv can_traffic_demo.csv

echo
echo "===== WEEK 2 COMPLETED ====="
echo "Model: week2/results/isolation_forest.joblib"
echo "No attack traffic was started."
