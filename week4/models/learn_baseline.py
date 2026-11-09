#!/usr/bin/env python3

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from week4.detection.advanced_engine import AdvancedDetectionEngine

CSV_PATH = ROOT / "can_traffic_demo.csv"


def load_baseline():
    frames = []

    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            frames.append({
                "can_id": row["can_id"],
                "timestamp": float(row["elapsed_seconds"]),
                "data": bytes.fromhex(row["data_hex"])
            })

    return frames


if __name__ == "__main__":
    frames = load_baseline()

    engine = AdvancedDetectionEngine()
    baseline = engine.learn(frames)

    print("[SUCCESS] Week 4 baseline learned")
    print("Frames loaded:", len(frames))
    print("ECU timing profiles:", baseline["timing_baseline"])
    print("ECU payload profiles:", baseline["payload_baseline"])
