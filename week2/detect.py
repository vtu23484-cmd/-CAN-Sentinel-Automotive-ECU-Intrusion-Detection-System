#!/usr/bin/env python3
"""Evaluate a real vcan0 CSV capture using the trained Week 2 model."""
import argparse
from pathlib import Path
from pipeline import RESULTS, MODEL_FILE, classify, load_csv, load_model, save_csv, sessions, window_features

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True, help="CSV recorded by week2/capture.py or original logger")
    p.add_argument("--model", default=str(MODEL_FILE))
    p.add_argument("--out", default=str(RESULTS / "live_detection.csv"))
    a = p.parse_args()
    model = load_model(a.model)
    chunks = sessions(load_csv(a.csv))
    detections = []
    for index, chunk in enumerate(chunks, 1):
        windows = window_features(chunk)
        for result in classify(model, windows):
            result["session"] = index
            # Unlabeled real captures are unknown, not verified normal.
            result["label"] = "unknown"
            detections.append(result)
    save_csv(a.out, detections)
    print(f"Sessions={len(chunks)} Windows={len(detections)} Alerts={sum(r['alert'] for r in detections)}")
    for row in detections:
        if row["alert"]:
            print(f"ALERT t={row['window_start_seconds']:.1f}s ID101={row['steering_frames']} "
                  f"ID102={row['rpm_frames']} ML={row['ml_alert']} "
                  f"Rule={row['frequency_alert']} Reason={row['reasons']}")
    print("Saved:", Path(a.out).resolve())
