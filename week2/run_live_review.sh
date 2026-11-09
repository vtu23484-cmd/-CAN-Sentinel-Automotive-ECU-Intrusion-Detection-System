#!/usr/bin/env bash
# Original Week 1 ECUs + Week 2 C injector and ML model on LIVE virtual CAN
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
mkdir -p week2/results
printf '\n[1/6] Configure vcan0 virtual CAN network\n'
bash week2/setup_vcan.sh
printf '\n[2/6] Compile original Steering/RPM ECU programs and new C attacker\n'
bash week2/build.sh
printf '\n[3/6] Train Isolation Forest on Week 1 normal traffic data\n'
"$PYTHON" week2/train.py --csv can_traffic_demo.csv
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || :; done
}
trap cleanup EXIT
printf '\n[4/6] Capture actual CAN frames; start normal ECUs\n'
"$PYTHON" week2/capture.py --seconds 23 --out week2/results/live_capture.csv >week2/results/capture.log 2>&1 & capture_pid=$!; pids+=("$capture_pid")
sleep 0.5
./week2/steering_ecu >week2/results/steering.log 2>&1 & pids+=("$!")
./week2/rpm_ecu >week2/results/rpm.log 2>&1 & pids+=("$!")
printf 'Collecting normal traffic for five seconds...\n'
sleep 5
printf '\n[5/6] Send high-frequency synthetic CAN injection: 60 frames/sec x 8 sec\n'
./week2/attacker --seconds 8 --rate 60 --id 101 | tee week2/results/attack_send.log
printf 'Finishing CAN capture...\n'
if ! wait "$capture_pid"; then cat week2/results/capture.log; exit 1; fi
printf '\n[6/6] Run ML detection, sent/received audit and HTML report\n'
"$PYTHON" week2/detect.py --csv week2/results/live_capture.csv
"$PYTHON" week2/audit.py --capture week2/results/live_capture.csv --send-log week2/results/attack_send.log
"$PYTHON" week2/live_report.py
printf '\nDONE. Open week2/results/LIVE_MID_REVIEW.html\n'
