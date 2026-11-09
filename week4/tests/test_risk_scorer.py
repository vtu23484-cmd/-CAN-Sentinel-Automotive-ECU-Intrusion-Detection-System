import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.risk_scorer import RiskScorer

scorer = RiskScorer()

findings = [
    {"finding": "timing_deviation"},
    {"finding": "payload_concentration"},
]

result = scorer.score(findings)

print("\n[TEST] Unified risk scoring")
print(result)

assert result["risk_score"] == 70
assert result["severity"] == "HIGH"

print("\n[SUCCESS] Risk scoring test passed.")
