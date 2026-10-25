"""CAN-Sentinel Week 2: read the *unchanged* Week 1 logger CSV format.

No hardware or sockets are used by this module. Native vcan injection is attacker.c.
"""
import csv
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
WEEK2 = Path(__file__).resolve().parent
RESULTS = WEEK2 / "results"
MODEL_FILE = RESULTS / "isolation_forest.joblib"
DEFAULT_BASELINE = ROOT / "can_traffic_demo.csv"

COLUMNS = ("timestamp_utc", "elapsed_seconds", "can_id", "dlc", "data_hex", "message_type")
FEATURES = (
    "total_frames", "steering_frames", "rpm_frames", "other_frames",
    "mean_gap_ms", "std_gap_ms", "can_id_entropy", "payload_entropy"
)


def load_csv(path):
    """Validate and normalize rows from teammate's CAN logger."""
    path = Path(path)
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not set(COLUMNS).issubset(reader.fieldnames or []):
            raise ValueError(f"CSV must include: {', '.join(COLUMNS)}")
        rows = []
        for number, raw in enumerate(reader, 2):
            try:
                seconds = float(raw["elapsed_seconds"])
                if not math.isfinite(seconds) or seconds < 0:
                    raise ValueError("invalid elapsed time")
                can_id = raw["can_id"].strip().upper().removeprefix("0X").zfill(3)
                int(can_id, 16)
                data = bytes.fromhex(raw["data_hex"])
                dlc = int(raw["dlc"])
                if not 0 <= dlc <= 8 or len(data) != dlc:
                    raise ValueError("invalid DLC/payload length")
            except (ValueError, TypeError, OverflowError) as error:
                raise ValueError(f"{path.name} line {number}: {error}") from error
            rows.append({
                "timestamp_utc": raw["timestamp_utc"], "t": seconds,
                "can_id": can_id, "dlc": dlc, "data": data,
                "message_type": raw["message_type"], "injected": False
            })
    if not rows:
        raise ValueError(f"No CAN records found in {path}")
    return rows


def sessions(rows, reset_tolerance=0.10):
    """Week 1 files may append sessions with elapsed_seconds starting over."""
    chunks = []
    current = []
    last = None
    for row in rows:
        if last is not None and row["t"] < last - reset_tolerance:
            if current:
                chunks.append(current)
            current = []
        current.append(row)
        last = row["t"]
    if current:
        chunks.append(current)
    return chunks


def normal_only(rows):
    return [r for r in rows if r["can_id"] in {"101", "102"} and r["dlc"] == 2]


def choose_baseline(rows):
    """Choose longest clean segment, never merge elapsed timers of different captures."""
    chunks = [normal_only(x) for x in sessions(rows)]
    candidates = [chunk for chunk in chunks if len(chunk) >= 30]
    if not candidates:
        raise ValueError("No sufficiently long normal ECU capture with IDs 101/102 was found")
    return max(candidates, key=lambda x: (x[-1]["t"] - x[0]["t"], len(x)))


def entropy(values):
    counts = Counter(values)
    if not counts:
        return 0.0
    total = sum(counts.values())
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def window_features(rows, *, origin=None, window_seconds=1.0):
    """Create one record for each populated one-second interval; preserve empty windows."""
    if not rows:
        return []
    origin = min(r["t"] for r in rows) if origin is None else origin
    groups = defaultdict(list)
    for row in rows:
        offset = row["t"] - origin
        if offset < -1e-8:
            continue
        bucket = int(max(0.0, offset) // window_seconds)
        groups[bucket].append(row)
    result = []
    if not groups:
        return []
    for bucket in range(max(groups) + 1):
        group = sorted(groups.get(bucket, []), key=lambda r: r["t"])
        ids = [r["can_id"] for r in group]
        timestamps = [r["t"] for r in group]
        gaps = [(y - x) * 1000.0 for x, y in zip(timestamps, timestamps[1:])]
        data_bytes = [b for row in group for b in row["data"]]
        mean = sum(gaps) / len(gaps) if gaps else 0.0
        variance = sum((x - mean)**2 for x in gaps) / len(gaps) if gaps else 0.0
        result.append({
            "window": bucket,
            "window_start_seconds": round(origin + bucket * window_seconds, 4),
            "label": int(any(r.get("injected") for r in group)),
            "total_frames": len(group),
            "steering_frames": ids.count("101"),
            "rpm_frames": ids.count("102"),
            "other_frames": len(ids) - ids.count("101") - ids.count("102"),
            "mean_gap_ms": mean,
            "std_gap_ms": math.sqrt(variance),
            "can_id_entropy": entropy(ids),
            "payload_entropy": entropy(data_bytes)
        })
    return result


def split_baseline(windows, train_fraction=0.6):
    if len(windows) < 20:
        raise ValueError("Need 20+ seconds of clean baseline traffic for reliable training")
    cut = max(12, min(len(windows) - 8, int(len(windows) * train_fraction)))
    return windows[:cut], windows[cut:]


def vectorize(windows, names=FEATURES):
    return np.asarray([[row[name] for name in names] for row in windows], dtype=float)


def train(baseline_path=DEFAULT_BASELINE, model_path=MODEL_FILE):
    original = load_csv(baseline_path)
    baseline = choose_baseline(original)
    features = window_features(baseline)
    training, heldout = split_baseline(features)
    X = vectorize(training)
    scaler = StandardScaler().fit(X)
    model = IsolationForest(n_estimators=250, contamination=0.10, random_state=42)
    model.fit(scaler.transform(X))
    limits = {
        "101": max(15, 3 * max(x["steering_frames"] for x in training)),
        "102": max(8, 3 * max(x["rpm_frames"] for x in training)),
    }
    bundle = {"model": model, "scaler": scaler, "features": FEATURES,
              "thresholds": limits, "baseline_file": str(baseline_path),
              "training_windows": len(training), "holdout_windows": len(heldout),
              "baseline_rows": len(baseline),
              "baseline_start": baseline[0]["t"],
              "cut_time": heldout[0]["window_start_seconds"]}
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    return bundle, baseline, training, heldout


def load_model(path=MODEL_FILE):
    # joblib/pickle can execute code: load only files created by this project.
    return joblib.load(path)


def classify(bundle, windows):
    if not windows:
        raise ValueError("No feature windows available")
    X = bundle["scaler"].transform(vectorize(windows, bundle["features"]))
    predictions = bundle["model"].predict(X)
    scores = bundle["model"].decision_function(X)
    result = []
    for row, prediction, score in zip(windows, predictions, scores):
        reasons = []
        if row["steering_frames"] > bundle["thresholds"]["101"]:
            reasons.append("high_steering_ID_rate")
        if row["rpm_frames"] > bundle["thresholds"]["102"]:
            reasons.append("high_RPM_ID_rate")
        if row["other_frames"] > 0:
            reasons.append("unknown_CAN_ID")
        ml = prediction == -1
        guardrail = bool(reasons)
        result.append({**row, "ml_alert": int(ml),
                       "frequency_alert": int(guardrail),
                       "alert": int(ml or guardrail),
                       "ml_score": round(float(score), 6),
                       "reasons": ",".join(reasons) or ("isolation_forest" if ml else "none")})
    return result


def save_csv(path, rows):
    if not rows:
        raise ValueError("Cannot save empty results")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_injected_capture(baseline, cut_time, attack_offset=5, attack_seconds=8, rate=60, can_id="101"):
    """Synthetic data ONLY for repeatable offline tests, not a real CAN bus."""
    heldout = [dict(r) for r in baseline if r["t"] >= cut_time]
    if not heldout:
        raise ValueError("Baseline has no held-out section")
    attack_start = heldout[0]["t"] + attack_offset
    if attack_start + attack_seconds > heldout[-1]["t"] - 0.1:
        raise ValueError("Held-out recording is too short for the selected attack duration")
    try:
        epoch = datetime.fromisoformat(heldout[0]["timestamp_utc"].replace("Z", "+00:00"))
    except ValueError:
        epoch = datetime.now(timezone.utc)
    payload = bytes.fromhex("7FFF")
    simulated = []
    for i in range(int(rate * attack_seconds)):
        t = attack_start + i / rate
        timestamp = (epoch + timedelta(seconds=t - heldout[0]["t"])).isoformat(timespec="milliseconds")
        simulated.append({"timestamp_utc": timestamp, "t": t, "can_id": can_id,
                          "dlc": 2, "data": payload, "message_type": "SIMULATED_ATTACK",
                          "injected": True})
    mixed = sorted(heldout + simulated, key=lambda r: r["t"])
    return mixed, len(simulated)


def raw_csv(path, rows):
    output = []
    for r in rows:
        output.append({
            "timestamp_utc": r["timestamp_utc"],
            "elapsed_seconds": f'{r["t"]:.6f}',
            "can_id": r["can_id"],
            "dlc": r["dlc"],
            "data_hex": " ".join(f"{byte:02X}" for byte in r["data"]),
            "message_type": r["message_type"]
        })
    save_csv(path, output)


def metrics(results, flag="alert"):
    tp = sum(x["label"] == 1 and x[flag] == 1 for x in results)
    fp = sum(x["label"] == 0 and x[flag] == 1 for x in results)
    tn = sum(x["label"] == 0 and x[flag] == 0 for x in results)
    fn = sum(x["label"] == 1 and x[flag] == 0 for x in results)
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "precision": round(precision, 4), "recall": round(recall, 4),
            "false_positive_rate": round(fpr, 4)}
