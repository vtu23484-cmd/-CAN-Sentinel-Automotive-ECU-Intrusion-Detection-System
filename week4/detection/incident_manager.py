#!/usr/bin/env python3
"""CAN Sentinel Week 4 incident prioritization."""

from datetime import datetime, timezone


class IncidentManager:

    def create_incident(self, detection_result):
        risk = detection_result.get("risk", {})
        score = int(risk.get("risk_score", 0))

        if score >= 80:
            priority = "CRITICAL"
        elif score >= 55:
            priority = "HIGH"
        elif score >= 30:
            priority = "MEDIUM"
        elif score > 0:
            priority = "LOW"
        else:
            priority = "NORMAL"

        can_ids = sorted({
            finding.get("can_id", "UNKNOWN")
            for finding in detection_result.get("findings", [])
        })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "priority": priority,
            "risk_score": score,
            "status": detection_result.get("status", "UNKNOWN"),
            "can_ids": can_ids,
            "finding_count": detection_result.get("finding_count", 0),
            "reasons": risk.get("reasons", []),
            "findings": detection_result.get("findings", []),
        }

    @staticmethod
    def prioritize(incidents):
        order = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "NORMAL": 0,
        }

        return sorted(
            incidents,
            key=lambda item: (
                order.get(item.get("priority", "NORMAL"), 0),
                item.get("risk_score", 0)
            ),
            reverse=True
        )
