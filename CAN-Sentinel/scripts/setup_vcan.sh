#!/usr/bin/env bash
set -euo pipefail
IFACE="${1:-vcan0}"
if ! sudo -n true 2>/dev/null; then
  echo "This script needs sudo privileges. Run: sudo $0 ${IFACE}" >&2
  exit 1
fi
modprobe vcan || true
if ip link show "$IFACE" >/dev/null 2>&1; then
  echo "$IFACE already exists; bringing it up."
else
  ip link add dev "$IFACE" type vcan
fi
ip link set up "$IFACE"
echo "Virtual CAN interface ready: $IFACE"
ip -details link show "$IFACE"
