#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "===== CAN SENTINEL | WEEK 1 ====="
echo "Preparing isolated virtual CAN interface..."
bash week2/setup_vcan.sh

if ! command -v candump >/dev/null 2>&1; then
    echo "Installing can-utils..."
    sudo apt-get update
    sudo apt-get install -y can-utils
fi

echo
echo "Starting CAN traffic logger on vcan0."
echo "Press Ctrl+C to stop capturing."
"$ROOT/.venv/bin/python" can_logger.py
