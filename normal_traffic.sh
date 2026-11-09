#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "CAN SENTINEL - WEEK 3 NORMAL TRAFFIC"
echo "Checking virtual CAN interface..."

if ! ip link show vcan0 >/dev/null 2>&1; then
    echo "Setting up vcan0..."
    bash week2/setup_vcan.sh
fi

./week2/steering_ecu &
STEER_PID=$!

./week2/rpm_ecu &
RPM_PID=$!

cleanup() {
    echo
    echo "Stopping normal ECU traffic..."
    kill "$STEER_PID" "$RPM_PID" 2>/dev/null || true
    wait "$STEER_PID" "$RPM_PID" 2>/dev/null || true
    echo "Normal traffic stopped."
}

trap cleanup EXIT INT TERM

echo "Steering ECU and RPM ECU are running."
echo "Monitoring dashboard: http://127.0.0.1:8765"
echo "Press Ctrl+C to stop both ECUs."

wait
