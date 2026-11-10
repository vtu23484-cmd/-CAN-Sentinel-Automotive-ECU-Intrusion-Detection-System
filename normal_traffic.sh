#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "======================================"
echo " CAN SENTINEL - NORMAL ECU TRAFFIC"
echo "======================================"

echo "[1/4] Loading CAN kernel modules..."
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan

echo "[2/4] Setting up virtual CAN..."
bash week2/setup_vcan.sh

echo "[3/4] Starting ECU simulators..."

./week2/steering_ecu &
STEER_PID=$!

./week2/rpm_ecu &
RPM_PID=$!

cleanup() {
    echo
    echo "Stopping ECU simulators..."
    kill "$STEER_PID" "$RPM_PID" 2>/dev/null || true
    wait "$STEER_PID" "$RPM_PID" 2>/dev/null || true
    echo "Normal traffic stopped."
}

trap cleanup EXIT INT TERM

echo "[4/4] Normal ECU traffic is running."
echo "Dashboard: http://127.0.0.1:8765"
echo "Press Ctrl+C to stop."

wait
