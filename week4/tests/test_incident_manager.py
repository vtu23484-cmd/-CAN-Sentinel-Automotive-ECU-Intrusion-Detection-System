import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.incident_manager import IncidentManager

manager = IncidentManager()

high_result = {
    "status": "ANOMALY",
    "finding_count": 2,
    "findings": [
        {"can_id": "101", "finding": "timing_deviation"},
        {"can_id": "101", "finding": "payload_concentration"},
    ],
    "risk": {
        "risk_score": 70,
        "severity": "HIGH",
        "reasons": ["ECU timing deviation", "Unusual payload concentration"],
    },
}

critical_result = {
    "status": "ANOMALY",
    "finding_count": 1,
    "findings": [{"can_id": "102", "finding": "timing_deviation"}],
    "risk": {"risk_score": 90, "reasons": ["ECU timing deviation"]},
}

incidents = [
    manager.create_incident(high_result),
    manager.create_incident(critical_result),
]

print("\n[TEST] Created incidents")
for incident in incidents:
    print(incident)

prioritized = manager.prioritize(incidents)

print("\n[TEST] Priority order")
for incident in prioritized:
    print(incident["priority"], incident["risk_score"])

assert prioritized[0]["priority"] == "CRITICAL"
assert prioritized[1]["priority"] == "HIGH"

print("\n[SUCCESS] Incident prioritization test passed.")
