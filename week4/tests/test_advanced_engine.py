import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.advanced_engine import AdvancedDetectionEngine

engine = AdvancedDetectionEngine()

# Synthetic baseline: varied payloads at 100 ms intervals.
baseline = [
    {
        "can_id": "101",
        "timestamp": i * 0.1,
        "data": bytes([i, i + 1])
    }
    for i in range(20)
]

print("\n[TEST 1] Learning normal ECU behaviour")
print(engine.learn(baseline))

# Synthetic abnormal timing and repeated payload.
abnormal = [
    {
        "can_id": "101",
        "timestamp": 3.0 + i * 0.005,
        "data": bytes([0x7F, 0xFF])
    }
    for i in range(20)
]

print("\n[TEST 2] Combined anomaly detection")
result = engine.analyze(abnormal)
print(result)

assert result["status"] == "ANOMALY"
assert result["finding_count"] >= 2

print("\n[SUCCESS] Advanced detection engine test passed.")
