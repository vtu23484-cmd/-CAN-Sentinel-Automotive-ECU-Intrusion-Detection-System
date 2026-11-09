#!/usr/bin/env python3
"""CAN Sentinel Week 4 temporal ECU behaviour detector.

Passive analysis only. No CAN transmission or vehicle control.
"""

from collections import defaultdict
from statistics import median


class TimingDetector:
    def __init__(self, minimum_samples=5, deviation_ratio=3.0):
        self.minimum_samples = minimum_samples
        self.deviation_ratio = deviation_ratio
        self.baselines = {}

    def learn_baseline(self, frames):
        """Learn median inter-arrival time for each CAN ID."""

        timestamps = defaultdict(list)

        for frame in frames:
            can_id = str(frame["can_id"]).upper().removeprefix("0X")
            timestamps[can_id].append(float(frame["timestamp"]))

        for can_id, values in timestamps.items():
            values.sort()
            intervals = [
                (values[i] - values[i - 1]) * 1000
                for i in range(1, len(values))
            ]

            if len(intervals) >= self.minimum_samples:
                self.baselines[can_id] = {
                    "median_interval_ms": median(intervals),
                    "samples": len(intervals),
                }

        return self.baselines

    def analyze(self, frames):
        """Detect unusually short or long intervals against a learned baseline."""

        grouped = defaultdict(list)

        for frame in frames:
            can_id = str(frame["can_id"]).upper().removeprefix("0X")
            grouped[can_id].append(float(frame["timestamp"]))

        findings = []

        for can_id, values in grouped.items():
            baseline = self.baselines.get(can_id)

            if not baseline or len(values) < 2:
                continue

            values.sort()
            expected = baseline["median_interval_ms"]

            if expected <= 0:
                continue

            intervals = [
                (values[i] - values[i - 1]) * 1000
                for i in range(1, len(values))
            ]

            unusual = [
                interval for interval in intervals
                if interval < expected / self.deviation_ratio
                or interval > expected * self.deviation_ratio
            ]

            if unusual:
                findings.append({
                    "can_id": can_id,
                    "expected_interval_ms": round(expected, 3),
                    "observed_intervals": len(intervals),
                    "unusual_intervals": len(unusual),
                    "minimum_interval_ms": round(min(intervals), 3),
                    "maximum_interval_ms": round(max(intervals), 3),
                    "finding": "timing_deviation",
                })

        return findings
