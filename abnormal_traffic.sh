#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "CAN SENTINEL - WEEK 3 ABNORMAL TRAFFIC"
echo "Checking virtual CAN interface..."

if ! ip link show vcan0 >/dev/null 2>&1; then
    echo "Setting up vcan0..."
    bash week2/setup_vcan.sh
fi

echo "Starting synthetic attack simulation..."
./week2/attacker --seconds 8 --rate 60 --id 101

echo "Abnormal traffic simulation completed."
