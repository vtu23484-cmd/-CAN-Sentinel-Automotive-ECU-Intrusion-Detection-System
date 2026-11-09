import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.timing_detector import TimingDetector

detector = TimingDetector(minimum_samples=5, deviation_ratio=3.0)

# Synthetic normal ECU traffic: one frame every 100 ms.
normal_frames = [
    {"can_id": "101", "timestamp": i * 0.1}
    for i in range(10)
]

print("\n[TEST 1] Learning normal ECU timing")
baseline = detector.learn_baseline(normal_frames)
print("Learned baseline:", baseline)

# Synthetic abnormal traffic: messages arrive every 5 ms.
abnormal_frames = [
    {"can_id": "101", "timestamp": 2.0 + i * 0.005}
    for i in range(10)
]

print("\n[TEST 2] Checking abnormal ECU timing")
findings = detector.analyze(abnormal_frames)
print("Detection findings:", findings)

assert "101" in baseline, "Baseline learning failed"
assert findings, "Timing anomaly was not detected"

print("\n[SUCCESS] Both timing detector tests passed.")
