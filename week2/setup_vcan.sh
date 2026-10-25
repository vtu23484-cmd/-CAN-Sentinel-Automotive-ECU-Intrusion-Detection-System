#!/usr/bin/env bash
set -euo pipefail
if ! command -v ip >/dev/null; then echo 'Missing iproute2'; exit 1; fi
if ! ip link show vcan0 >/dev/null 2>&1; then
  sudo modprobe vcan 2>/dev/null || true
  if ! sudo ip link add dev vcan0 type vcan; then
    echo 'ERROR: Unable to create vcan0 (kernel support and CAP_NET_ADMIN required).' >&2
    echo 'Try Windows PowerShell: wsl --update, then wsl --shutdown and reopen Ubuntu.' >&2
    echo 'If still unsupported, use a Linux VM or your teammate Ubuntu machine.' >&2
    exit 1
  fi
fi
sudo ip link set dev vcan0 up
ip -brief link show vcan0
