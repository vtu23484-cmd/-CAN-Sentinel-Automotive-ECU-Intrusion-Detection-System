#!/usr/bin/env python3
"""Train on actual Week 1 CSV, without altering teammate's files."""
import argparse
from pipeline import DEFAULT_BASELINE, MODEL_FILE, train

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", default=str(DEFAULT_BASELINE), help="Week 1 normal CSV")
    p.add_argument("--model", default=str(MODEL_FILE))
    args = p.parse_args()
    bundle, baseline, training, heldout = train(args.csv, args.model)
    print("CAN-Sentinel Week 2 Isolation Forest training")
    print("Baseline rows:", len(baseline))
    print("Training windows:", len(training))
    print("Held-out windows:", len(heldout))
    print("Per-ID count limits:", bundle["thresholds"])
    print("Model saved to:", args.model)
