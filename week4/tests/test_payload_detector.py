import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.payload_detector import PayloadDetector

detector = PayloadDetector(
    repetition_threshold=0.90,
    minimum_frames=10
)

# Learn from varied synthetic baseline payloads.
normal_frames = [
    {
        "can_id": "101",
        "data": bytes([i, i + 1])
    }
    for i in range(20)
]

print("\n[TEST 1] Learning normal payload distribution")
print(detector.learn_baseline(normal_frames))

# Test repeated synthetic payloads offline.
repeated_frames = [
    {"can_id": "101", "data": bytes([0x7F, 0xFF])}
    for _ in range(20)
]

print("\n[TEST 2] Checking repeated payload pattern")
findings = detector.analyze(repeated_frames)
print("Findings:", findings)

assert "101" in detector.baselines
assert findings, "Payload concentration was not detected"

print("\n[SUCCESS] Payload detector test passed.")
