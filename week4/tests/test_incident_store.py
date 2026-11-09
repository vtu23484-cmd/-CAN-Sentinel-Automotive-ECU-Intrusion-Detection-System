import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.incident_manager import IncidentManager
from week4.detection.incident_store import IncidentStore

manager = IncidentManager()
store = IncidentStore("week4/results/test_incidents.db")

test_result = {
    "status": "ANOMALY",
    "finding_count": 1,
    "findings": [
        {"can_id": "101", "finding": "timing_deviation"}
    ],
    "risk": {
        "risk_score": 90,
        "reasons": ["ECU timing deviation"]
    }
}

incident = manager.create_incident(test_result)

print("\n[TEST 1] Saving incident")
incident_id = store.save(incident)
print("Saved incident ID:", incident_id)

print("\n[TEST 2] Retrieving incident history")
history = store.get_recent()

for record in history:
    print(record)

assert incident_id > 0
assert history
assert history[0]["priority"] == "CRITICAL"

print("\n[SUCCESS] Incident storage test passed.")
