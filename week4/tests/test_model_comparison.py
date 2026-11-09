import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.models.model_comparison import compare_models

# Synthetic normal training windows.
normal = [
    {
        "label": 0,
        "total_frames": 7,
        "steering_frames": 5,
        "rpm_frames": 2,
        "other_frames": 0,
        "mean_gap_ms": 140,
        "std_gap_ms": 30,
        "can_id_entropy": 0.86,
        "payload_entropy": 3.2,
    }
    for _ in range(40)
]

# Synthetic injected training windows.
abnormal = [
    {
        "label": 1,
        "total_frames": 60,
        "steering_frames": 60,
        "rpm_frames": 0,
        "other_frames": 0,
        "mean_gap_ms": 16,
        "std_gap_ms": 2,
        "can_id_entropy": 0.0,
        "payload_entropy": 0.1,
    }
    for _ in range(40)
]

training = normal[:30] + abnormal[:30]
testing = normal[30:] + abnormal[30:]

print("\n[TEST] Comparing ML models")
results = compare_models(training, testing)

for name, result in results.items():
    print(f"\n{name}")
    print("Confusion matrix:", result["confusion_matrix"])
    print("Accuracy:", round(
        result["classification_report"]["accuracy"], 3
    ))

assert "Isolation Forest" in results
assert "Random Forest" in results

print("\n[SUCCESS] Model comparison test completed.")
