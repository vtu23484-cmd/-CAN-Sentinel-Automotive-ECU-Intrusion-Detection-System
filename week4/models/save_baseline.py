#!/usr/bin/env python3

import json
from pathlib import Path

from learn_baseline import load_baseline
from week4.detection.advanced_engine import AdvancedDetectionEngine

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "week4" / "models" / "baseline.json"

frames = load_baseline()
engine = AdvancedDetectionEngine()
baseline = engine.learn(frames)

with OUTPUT.open("w", encoding="utf-8") as file:
    json.dump(baseline, file, indent=4)

print("[SUCCESS] Baseline saved:", OUTPUT)
print("Frames used:", len(frames))
