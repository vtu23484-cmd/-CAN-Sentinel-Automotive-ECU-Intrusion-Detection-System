"""Per-CAN-ID feature extraction with bounded rolling state."""
import math
from collections import defaultdict, deque
import numpy as np

FEATURE_NAMES = ["id_rate_1s", "interarrival_ms", "dlc", "payload_entropy"]

def payload_entropy(hex_data: str) -> float:
    try:
        raw = bytes.fromhex(hex_data)
    except (ValueError, TypeError):
        raw = b""
    if not raw:
        return 0.0
    counts = [raw.count(i) for i in range(256)]
    n = len(raw)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)

class FeatureBuilder:
    """Features are calculated per arbitration ID to avoid cross-ID rate pollution."""
    def __init__(self, window_seconds=1.0, history=1000):
        self.window_seconds = float(window_seconds)
        self.history = int(history)
        self.times_by_id = defaultdict(lambda: deque(maxlen=self.history))
        self.last_by_id = {}

    def transform(self, frame: dict):
        ts = float(frame.get("timestamp", 0))
        can_id = int(frame.get("can_id", -1))
        times = self.times_by_id[can_id]
        while times and ts - times[0] > self.window_seconds:
            times.popleft()
        times.append(ts)
        previous = self.last_by_id.get(can_id)
        delta_ms = 0.0 if previous is None else max(0.0, (ts - previous) * 1000.0)
        self.last_by_id[can_id] = ts
        return np.array([float(len(times)), delta_ms, float(frame.get("dlc", 0)), payload_entropy(str(frame.get("data", "")))], dtype=float)
