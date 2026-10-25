#!/usr/bin/env bash
# ONE COMMAND: original C/SocketCAN Week 2 demonstration, Ubuntu / WSL2 only
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
printf '\n======== CAN-SENTINEL | WEEK 2 + MID REVIEW =========\n'
printf 'Virtual CAN interface only: vcan0 (not a vehicle).\n'
if ! command -v sudo >/dev/null 2>&1; then
 echo 'ERROR: This must be run in Ubuntu/Linux with sudo privileges.' >&2; exit 1
fi
need_apt=0
for command in gcc ip modprobe candump python3; do
  if ! command -v "$command" >/dev/null 2>&1; then need_apt=1; fi
done
if ! python3 -m venv --help >/dev/null 2>&1; then need_apt=1; fi
if [ "$need_apt" -eq 1 ]; then
  printf '\n[SETUP] Installing required Linux tools (first run only)...\n'
  sudo apt-get update
  sudo apt-get install -y build-essential kmod can-utils iproute2 python3 python3-venv python3-pip
fi
if [ ! -f .venv/bin/python ]; then
  printf '\n[SETUP] Creating isolated Python environment...\n'
  python3 -m venv .venv
fi
PY="$ROOT/.venv/bin/python"
if ! "$PY" -c 'import sklearn, joblib, numpy' >/dev/null 2>&1; then
  printf '\n[SETUP] Installing Isolation Forest dependencies...\n'
  "$PY" -m pip install -r week2/requirements.txt
fi
printf '\n[RUN] Running actual virtual CAN frame capture, attacker and detection...\n'
PYTHON="$PY" bash week2/run_live_review.sh
printf '\n[FINISHED] Output in week2/results/\n'
printf 'Main report: week2/results/LIVE_MID_REVIEW.html\n'
