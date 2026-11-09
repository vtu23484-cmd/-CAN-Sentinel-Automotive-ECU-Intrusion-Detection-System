#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.advanced_engine import AdvancedDetectionEngine
from week4.detection.live_adapter import LiveAdapter

engine = AdvancedDetectionEngine()
engine.load_baseline(ROOT / "week4/models/baseline.json")

adapter = LiveAdapter(
    engine,
    database="week4/results/test_live_adapter.db"
)

# Synthetic Week 3-style frame window.
rows = [
    {
        "can_id": "101",
        "t": 100.0 + i * 0.005,
        "data": bytes([0x7F, 0xFF]),
    }
    for i in range(20)
]

print("[TEST] Passing Week 3 frames into Week 4")
result = adapter.analyze_window(rows)

print("Detection:", result["detection"])
print("Saved incident ID:", result["incident_id"])

assert result["detection"]["status"] == "ANOMALY"
assert result["incident_id"] is not None

print("[SUCCESS] Live adapter integration test passed.")
