#!/usr/bin/env python3
"""CAN Sentinel Week 4 advanced detection engine."""

import json
from pathlib import Path

from week4.detection.timing_detector import TimingDetector
from week4.detection.payload_detector import PayloadDetector
from week4.detection.risk_scorer import RiskScorer


class AdvancedDetectionEngine:
    def __init__(self):
        self.timing = TimingDetector()
        self.payload = PayloadDetector()
        self.risk_scorer = RiskScorer()

    def learn(self, baseline_frames):
        return {
            "timing_baseline": self.timing.learn_baseline(baseline_frames),
            "payload_baseline": self.payload.learn_baseline(baseline_frames),
        }

    def load_baseline(self, baseline_path):
        path = Path(baseline_path)

        with path.open("r", encoding="utf-8") as file:
            baseline = json.load(file)

        self.timing.baselines = baseline["timing_baseline"]
        self.payload.baselines = baseline["payload_baseline"]

        return baseline

    def analyze(self, frames):
        timing_findings = self.timing.analyze(frames)
        payload_findings = self.payload.analyze(frames)

        findings = timing_findings + payload_findings
        risk = self.risk_scorer.score(findings)

        return {
            "status": "ANOMALY" if findings else "NORMAL",
            "finding_count": len(findings),
            "findings": findings,
            "risk": risk,
        }
