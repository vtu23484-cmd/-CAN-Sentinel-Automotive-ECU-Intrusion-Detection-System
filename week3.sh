#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "===== CAN SENTINEL | WEEK 3 ====="

bash week2/setup_vcan.sh

if [[ ! -x .venv/bin/python ]]; then
    echo "Python environment missing. Run ./week2.sh first."
    exit 1
fi

echo "Building the CAN sniffer..."
gcc -Wall -Wextra -O2 -std=gnu11 \
    week3/sniffer.c -o week3/sniffer

echo
echo "Starting the local dashboard."
echo "Open http://127.0.0.1:8765 in your browser."
echo "Keep this terminal open. Press Ctrl+C to stop the dashboard."

exec .venv/bin/python week3/web_dashboard.py
