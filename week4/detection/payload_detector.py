#!/usr/bin/env python3
"""CAN Sentinel Week 4 payload anomaly detector.

Offline/passive analysis only.
"""

from collections import Counter


class PayloadDetector:
    def __init__(self, repetition_threshold=0.90, minimum_frames=10):
        self.repetition_threshold = repetition_threshold
        self.minimum_frames = minimum_frames
        self.baselines = {}

    def learn_baseline(self, frames):
        """Learn common payloads for each CAN identifier."""
        grouped = {}

        for frame in frames:
            can_id = str(frame["can_id"]).upper().removeprefix("0X")
            payload = bytes(frame["data"]).hex().upper()
            grouped.setdefault(can_id, []).append(payload)

        for can_id, payloads in grouped.items():
            counts = Counter(payloads)
            self.baselines[can_id] = {
                "common_payload": counts.most_common(1)[0][0],
                "frequency": counts.most_common(1)[0][1] / len(payloads),
                "samples": len(payloads),
            }

        return self.baselines

    def analyze(self, frames):
        """Identify unusual payload distributions."""
        grouped = {}

        for frame in frames:
            can_id = str(frame["can_id"]).upper().removeprefix("0X")
            payload = bytes(frame["data"]).hex().upper()
            grouped.setdefault(can_id, []).append(payload)

        findings = []

        for can_id, payloads in grouped.items():
            baseline = self.baselines.get(can_id)

            if not baseline or len(payloads) < self.minimum_frames:
                continue

            repeated = Counter(payloads)
            common_payload, count = repeated.most_common(1)[0]
            ratio = count / len(payloads)

            if ratio >= self.repetition_threshold:
                findings.append({
                    "can_id": can_id,
                    "dominant_payload": common_payload,
                    "repetition_ratio": round(ratio, 3),
                    "frames_analyzed": len(payloads),
                    "finding": "payload_concentration",
                })

        return findings
