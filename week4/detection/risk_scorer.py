#!/usr/bin/env python3
"""CAN Sentinel Week 4 unified risk scoring."""

class RiskScorer:
    def score(self, findings):
        risk = 0
        reasons = []

        for finding in findings:
            finding_type = finding.get("finding")

            if finding_type == "timing_deviation":
                risk += 40
                reasons.append("ECU timing deviation")

            elif finding_type == "payload_concentration":
                risk += 30
                reasons.append("Unusual payload concentration")

        risk = min(risk, 100)

        if risk >= 80:
            severity = "CRITICAL"
        elif risk >= 55:
            severity = "HIGH"
        elif risk >= 30:
            severity = "MEDIUM"
        elif risk > 0:
            severity = "LOW"
        else:
            severity = "NORMAL"

        return {
            "risk_score": risk,
            "severity": severity,
            "reasons": reasons,
        }
