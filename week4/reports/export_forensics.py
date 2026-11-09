#!/usr/bin/env python3
"""Export CAN Sentinel incident history as a forensic JSON report."""

import json
from datetime import datetime, timezone
from pathlib import Path

from week4.detection.incident_store import IncidentStore


def export_report():
    store = IncidentStore("week4/results/incidents.db")
    incidents = store.get_recent(limit=1000)

    report = {
        "report_name": "CAN Sentinel Forensic Incident Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_incidents": len(incidents),
        "incidents": incidents,
    }

    output = Path("week4/reports/forensic_report.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("[SUCCESS] Forensic report generated:", output)
    print("Total incidents:", len(incidents))


if __name__ == "__main__":
    export_report()
