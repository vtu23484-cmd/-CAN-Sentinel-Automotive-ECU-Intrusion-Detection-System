#!/usr/bin/env python3
"""Connect Week 3 frame windows to Week 4 detection and incident storage."""

from week4.detection.incident_manager import IncidentManager
from week4.detection.incident_store import IncidentStore


class LiveAdapter:
    def __init__(self, engine, database="week4/results/incidents.db"):
        self.engine = engine
        self.incident_manager = IncidentManager()
        self.incident_store = IncidentStore(database)

    def analyze_window(self, rows):
        frames = [
            {
                "can_id": row["can_id"],
                "timestamp": float(row["t"]),
                "data": bytes(row["data"]),
            }
            for row in rows
        ]

        result = self.engine.analyze(frames)
        incident_id = None

        if result["findings"]:
            incident = self.incident_manager.create_incident(result)
            incident_id = self.incident_store.save(incident)

        return {
            "detection": result,
            "incident_id": incident_id,
        }
