#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.advanced_engine import AdvancedDetectionEngine

BASELINE_PATH = ROOT / "week4/models/baseline.json"

engine = AdvancedDetectionEngine()

print("\n[TEST 1] Loading saved ECU baseline")
baseline = engine.load_baseline(BASELINE_PATH)

print("Timing profiles:", baseline["timing_baseline"])
print("Payload profiles:", baseline["payload_baseline"])

assert "101" in engine.timing.baselines
assert "102" in engine.timing.baselines

print("\n[TEST 2] Detecting synthetic abnormal traffic")

abnormal_frames = [
    {
        "can_id": "101",
        "timestamp": 100.0 + i * 0.005,
        "data": bytes([0x7F, 0xFF])
    }
    for i in range(20)
]

result = engine.analyze(abnormal_frames)
print("Detection result:", result)

assert result["status"] == "ANOMALY"
assert result["finding_count"] > 0

print("\n[SUCCESS] Saved baseline loading and detection passed.")
