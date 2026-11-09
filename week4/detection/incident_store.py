#!/usr/bin/env python3
"""Persistent SQLite incident history for CAN Sentinel."""

import json
import sqlite3
from pathlib import Path


class IncidentStore:
    def __init__(self, database="week4/results/incidents.db"):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.database) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    can_ids TEXT NOT NULL,
                    finding_count INTEGER NOT NULL,
                    details TEXT NOT NULL
                )
            """)

    def save(self, incident):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute("""
                INSERT INTO incidents (
                    timestamp, priority, risk_score, status,
                    can_ids, finding_count, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                incident["timestamp"],
                incident["priority"],
                incident["risk_score"],
                incident["status"],
                json.dumps(incident["can_ids"]),
                incident["finding_count"],
                json.dumps(incident),
            ))

            return cursor.lastrowid

    def get_recent(self, limit=20):
        with sqlite3.connect(self.database) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("""
                SELECT * FROM incidents
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return [dict(row) for row in rows]
