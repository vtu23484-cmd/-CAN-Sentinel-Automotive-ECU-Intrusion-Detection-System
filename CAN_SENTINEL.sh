#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

while true; do
    echo
    echo "======================================"
    echo "       CAN SENTINEL CONTROL MENU"
    echo "======================================"
    echo "  1) Week 1 - CAN traffic logger"
    echo "  2) Week 2 - Train detection model"
    echo "  3) Week 3 - Live local dashboard"
    echo "  4) Week 4 - Advanced tests and report"
    echo "  5) Exit"
    echo "======================================"
    read -r -p "Choose an option: " choice

    case "$choice" in
        1) bash "$ROOT/week1.sh" ;;
        2) bash "$ROOT/week2.sh" ;;
        3) bash "$ROOT/week3.sh" ;;
        4) bash "$ROOT/week4.sh" ;;
        5) echo "Exiting CAN Sentinel."; exit 0 ;;
        *) echo "Invalid option. Choose 1 to 5." ;;
    esac
done
