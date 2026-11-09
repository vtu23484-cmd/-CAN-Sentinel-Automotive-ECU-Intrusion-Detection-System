#!/usr/bin/env python3
"""CAN Sentinel 2.0 behavioural detection engine.

Designed for isolated virtual CAN testing on vcan0.
Does not transmit CAN frames or control vehicle systems.
"""

import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "week3" / "incidents.db"

# Initial profiles based on the project's simulated ECU traffic.
# These are configurable assumptions, not universal vehicle specifications.
ECU_PROFILES = {
    "101": {
        "name": "Steering ECU",
        "expected_dlc": 2,
        "normal_rate": 5,
        "max_rate": 15,
    },
    "102": {
        "name": "RPM ECU",
        "expected_dlc": 2,
        "normal_rate": 2,
        "max_rate": 8,
    },
}


class BehavioralDetector:

    def __init__(self, database=DATABASE):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(self.database)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_database(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    can_ids TEXT NOT NULL,
                    frame_count INTEGER NOT NULL,
                    reasons TEXT NOT NULL,
                    ml_score REAL,
                    details TEXT NOT NULL
                )
            """)

            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_timestamp
                ON incidents(timestamp)
            """)

    @staticmethod
    def _severity(score):
        if score >= 80:
            return "CRITICAL"
        if score >= 55:
            return "HIGH"
        if score >= 30:
            return "MEDIUM"
        if score > 0:
            return "LOW"
        return "NORMAL"

    def analyze_window(self, rows, ml_result=None):
        """Analyse one populated time window and optionally combine ML output."""

        if not rows:
            return None

        counts = Counter()
        dlc_errors = []
        unknown_ids = set()
        payload_counts = Counter()

        for row in rows:
            can_id = str(row["can_id"]).upper().removeprefix("0X").zfill(3)
            data = bytes(row["data"])
            dlc = len(data)

            counts[can_id] += 1
            payload_counts[(can_id, data)] += 1

            profile = ECU_PROFILES.get(can_id)

            if profile is None:
                unknown_ids.add(can_id)
            elif dlc != profile["expected_dlc"]:
                dlc_errors.append({
                    "can_id": can_id,
                    "expected": profile["expected_dlc"],
                    "actual": dlc,
                })

        total = len(rows)
        reasons = []
        evidence = []
        score = 0

        # Rule 1: unknown CAN identifiers.
        if unknown_ids:
            reasons.append("unknown_CAN_ID")
            evidence.append({
                "type": "unknown_identifier",
                "can_ids": sorted(unknown_ids),
            })
            score += 30

        # Rule 2: unexpected payload lengths.
        if dlc_errors:
            reasons.append("unexpected_DLC")
            evidence.append({
                "type": "dlc_mismatch",
                "frames": dlc_errors,
            })
            score += 35

        # Rule 3: ECU message-rate deviations.
        for can_id, count in counts.items():
            profile = ECU_PROFILES.get(can_id)

            if profile and count > profile["max_rate"]:
                reasons.append("high_" + can_id + "_ID_rate")
                evidence.append({
                    "type": "frequency_anomaly",
                    "can_id": can_id,
                    "ecu": profile["name"],
                    "observed_frames": count,
                    "expected_rate": profile["normal_rate"],
                    "configured_limit": profile["max_rate"],
                })
                score += 40

        # Rule 4: suspicious repetition.
        # Repetition alone is not considered an attack. It must be
        # accompanied by an unusually high message rate.
        for (can_id, payload), count in payload_counts.items():
            profile = ECU_PROFILES.get(can_id)

            if (
                profile
                and total > profile["max_rate"]
                and count >= 10
                and count / total >= 0.80
            ):
                reasons.append("suspicious_payload_repetition")
                evidence.append({
                    "type": "repetition_pattern",
                    "can_id": can_id,
                    "repeated_frames": count,
                    "payload_hex": payload.hex().upper(),
                })
                score += 25
                break

        # Rule 5: combine existing Isolation Forest result.
        ml_score = None

        if ml_result is not None:
            ml_score = ml_result.get("ml_score")

            if ml_result.get("ml_alert", 0):
                reasons.append("isolation_forest_anomaly")
                score += 10

            if ml_result.get("frequency_alert", 0):
                # Existing Week 2 guardrail is supporting evidence.
                evidence.append({
                    "type": "week2_frequency_guardrail",
                    "reasons": ml_result.get("reasons", ""),
                })

        # Keep risk score bounded.
        score = min(score, 100)
        severity = self._severity(score)

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "risk_score": score,
            "frame_count": total,
            "can_ids": sorted(counts),
            "reasons": sorted(set(reasons)),
            "ml_score": ml_score,
            "evidence": evidence,
            "id_counts": dict(counts),
        }

        if score > 0:
            self._save_incident(result)

        return result

    def _save_incident(self, result):
        with self._connect() as db:
            db.execute("""
                INSERT INTO incidents (
                    timestamp, severity, risk_score,
                    can_ids, frame_count, reasons,
                    ml_score, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result["timestamp"],
                result["severity"],
                result["risk_score"],
                json.dumps(result["can_ids"]),
                result["frame_count"],
                json.dumps(result["reasons"]),
                result["ml_score"],
                json.dumps(result["evidence"]),
            ))

    def recent_incidents(self, limit=50):
        limit = max(1, min(int(limit), 500))

        with self._connect() as db:
            db.row_factory = sqlite3.Row
            records = db.execute("""
                SELECT * FROM incidents
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return [dict(record) for record in records]

    def incident_summary(self):
        with self._connect() as db:
            total = db.execute(
                "SELECT COUNT(*) FROM incidents"
            ).fetchone()[0]

            rows = db.execute("""
                SELECT severity, COUNT(*)
                FROM incidents
                GROUP BY severity
            """).fetchall()

        return {
            "total_incidents": total,
            "by_severity": dict(rows),
        }


if __name__ == "__main__":
    detector = BehavioralDetector()
    print("[OK] CAN Sentinel behavioural engine initialized.")
    print("[OK] ECU profiles:", len(ECU_PROFILES))
    print("[OK] Incident database:", DATABASE)
    print("[OK] Detection rules: frequency, unknown IDs, DLC, repetition, ML")
