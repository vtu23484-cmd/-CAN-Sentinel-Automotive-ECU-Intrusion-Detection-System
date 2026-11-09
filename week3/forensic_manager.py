#!/usr/bin/env python3
"""CAN Sentinel forensic incident management and CSV export."""

import argparse
import csv
import json
import sqlite3
from pathlib import Path

from week3.behavioral_detector import DATABASE


def get_incidents(severity=None, reason=None, limit=100):
    query = "SELECT * FROM incidents WHERE 1=1"
    params = []

    if severity and severity.upper() != "ALL":
        query += " AND severity = ?"
        params.append(severity.upper())

    if reason:
        query += " AND reasons LIKE ?"
        params.append(f"%{reason}%")

    query += " ORDER BY id DESC LIMIT ?"
    params.append(max(1, min(int(limit), 1000)))

    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(query, params)]


def export_csv(rows, output):
    if not rows:
        print("No incidents to export.")
        return

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "id", "timestamp", "severity", "risk_score",
        "can_ids", "frame_count", "reasons", "ml_score", "details"
    ]

    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Exported {len(rows)} incidents to {output}")


def main():
    parser = argparse.ArgumentParser(
        description="CAN Sentinel forensic incident manager"
    )
    parser.add_argument("--severity", default="ALL")
    parser.add_argument("--reason")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--export", metavar="CSV_FILE")
    args = parser.parse_args()

    rows = get_incidents(args.severity, args.reason, args.limit)

    print(f"\nCAN SENTINEL FORENSIC REPORT")
    print(f"Matching incidents: {len(rows)}\n")

    for item in rows:
        print(
            f"ID={item['id']} | "
            f"{item['timestamp']} | "
            f"{item['severity']} | "
            f"Risk={item['risk_score']} | "
            f"CAN IDs={item['can_ids']}"
        )
        print(f"  Reasons: {item['reasons']}")
        print(f"  Evidence: {item['details']}\n")

    if args.export:
        export_csv(rows, args.export)


if __name__ == "__main__":
    main()
