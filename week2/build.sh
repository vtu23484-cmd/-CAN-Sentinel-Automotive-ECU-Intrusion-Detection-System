#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gcc -Wall -Wextra -O2 -std=gnu11 "$ROOT/steering_ecu.c" -o "$ROOT/week2/steering_ecu"
gcc -Wall -Wextra -O2 -std=gnu11 "$ROOT/rpm_ecu.c" -o "$ROOT/week2/rpm_ecu"
gcc -Wall -Wextra -O2 -std=gnu11 "$ROOT/week2/attacker.c" -o "$ROOT/week2/attacker"
echo 'C programs compiled: week2/steering_ecu, week2/rpm_ecu, week2/attacker'
