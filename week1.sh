#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "===== CAN SENTINEL | WEEK 1 ====="

echo "[1/5] Loading CAN kernel modules..."
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan

echo "[2/5] Checking CAN utilities..."
if ! command -v candump >/dev/null 2>&1; then
    sudo apt update
    sudo apt install can-utils -y
fi

echo "[3/5] Setting up virtual CAN..."
bash week2/setup_vcan.sh

echo "[4/5] Checking vcan0..."
ip -brief link show vcan0

echo "[5/5] Starting CAN traffic logger..."
mkdir -p data

echo "Output: data/can_traffic.csv"
echo "Press Ctrl+C to stop capturing."

exec .venv/bin/python can_logger.py
