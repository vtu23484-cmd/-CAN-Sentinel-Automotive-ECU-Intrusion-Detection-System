#!/usr/bin/env python3

import json
import math
import os
import signal
import socket
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from week2.pipeline import window_features, load_model, classify
from week3.behavioral_detector import BehavioralDetector
from week4.detection.advanced_engine import AdvancedDetectionEngine
from week4.detection.live_adapter import LiveAdapter

ROOT = Path(__file__).resolve().parent.parent
SOCKET_PATH = "/tmp/can_sentinel.sock"
MODEL_PATH = ROOT / "week2/results/isolation_forest.joblib"
BASELINE_PATH = ROOT / "week4/models/baseline.json"

running = True
LIVE_STATUS_PATH = ROOT / "week3" / "live_status.json"
LIVE_STATUS = {
    "running": False, "frames": 0, "steering": 0, "rpm": 0,
    "other": 0, "risk_score": 0, "severity": "NORMAL",
    "reasons": [], "vcan": True, "sniffer": False, "model": False
}


def save_live_status(**updates):
    LIVE_STATUS.update(updates)
    temporary = LIVE_STATUS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(LIVE_STATUS))
    temporary.replace(LIVE_STATUS_PATH)


def stop_handler(signum, frame):
    global running
    running = False


def process_window(bundle, bucket, rows, detector, week4_adapter):
    if not rows:
        return

    features = window_features(
        rows,
        origin=float(bucket),
        window_seconds=1.0
    )

    if not features:
        return

    results = classify(bundle, features)

    for result in results:
        behavior = detector.analyze_window(rows, ml_result=result)
        week4_result = week4_adapter.analyze_window(rows)
        week4_detection = week4_result["detection"]
        week4_risk = week4_detection["risk"]

        combined_alert = bool(
            result["alert"] or behavior["risk_score"] > 0
            or week4_detection["status"] == "ANOMALY"
        )

        status = "ALERT" if combined_alert else "NORMAL"
        save_live_status(
            running=True,
            risk_score=behavior["risk_score"],
            severity=behavior["severity"],
            reasons=behavior["reasons"],
            week4_risk_score=week4_risk["risk_score"],
            week4_severity=week4_risk["severity"],
            week4_reasons=week4_risk["reasons"],
            week4_incident_id=week4_result["incident_id"],
            model=True
        )

        reasons = sorted(set(
            ([x for x in result["reasons"].split(",") if x != "none"])
            + behavior["reasons"]
            + week4_risk["reasons"]
        ))

        print(
            f"[{status}] "
            f"frames={result['total_frames']} "
            f"steering={result['steering_frames']} "
            f"rpm={result['rpm_frames']} "
            f"other={result['other_frames']} "
            f"ML score={result['ml_score']} "
            f"reasons={','.join(reasons) or 'none'} "
            f"severity={behavior['severity']} "
            f"risk_score={behavior['risk_score']} "
            f"WEEK4 risk={week4_risk['risk_score']} "
            f"WEEK4 severity={week4_risk['severity']} "
            f"incident_id={week4_result['incident_id']}",
            flush=True
        )


def main():
    global running

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    if not MODEL_PATH.is_file():
        print(f"ERROR: ML model not found: {MODEL_PATH}", file=sys.stderr)
        return 1

    print("[1/3] Loading existing Week 2 ML model...", flush=True)
    bundle = load_model(MODEL_PATH)
    print("[OK] Isolation Forest model loaded.", flush=True)
    detector = BehavioralDetector()
    if not BASELINE_PATH.is_file():
        print(f"ERROR: Week 4 baseline not found: {BASELINE_PATH}", file=sys.stderr)
        return 1
    week4_engine = AdvancedDetectionEngine()
    week4_engine.load_baseline(BASELINE_PATH)
    week4_adapter = LiveAdapter(week4_engine)
    print("[OK] Week 4 advanced detection engine loaded.", flush=True)
    save_live_status(
        running=True, frames=0, steering=0, rpm=0, other=0,
        risk_score=0, severity="NORMAL", reasons=[],
        vcan=True, sniffer=False, model=True
    )
    print("[OK] Behavioural detection engine loaded.", flush=True)

    if os.path.lexists(SOCKET_PATH):
        if not stat.S_ISSOCK(os.lstat(SOCKET_PATH).st_mode):
            print(
                f"ERROR: {SOCKET_PATH} exists but is not a socket. "
                "Refusing to remove it.",
                file=sys.stderr
            )
            return 1
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        server.bind(SOCKET_PATH)
        os.chmod(SOCKET_PATH, 0o600)
        server.listen(1)

        print(f"[2/3] Listening at {SOCKET_PATH}", flush=True)
        print("[3/3] Waiting for the C sniffer...", flush=True)

        server.settimeout(1.0)

        while running:
            try:
                connection, _ = server.accept()
                break
            except socket.timeout:
                continue
        else:
            return 0

        with connection:
            print("[CONNECTED] C sniffer connected.", flush=True)

            buffer = b""
            current_bucket = None
            current_rows = []
            received = 0

            while running:
                chunk = connection.recv(4096)

                if not chunk:
                    break

                buffer += chunk

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)

                    if not line.strip():
                        continue

                    try:
                        message = json.loads(line)

                        if message.get("type") != "frame":
                            continue

                        timestamp = float(message["timestamp"])
                        if not math.isfinite(timestamp) or timestamp < 0:
                            raise ValueError("Invalid timestamp")

                        can_id = str(message["can_id"]).upper()
                        dlc = int(message["dlc"])
                        data = bytes.fromhex(message["data"])

                        if not 0 <= dlc <= 8 or len(data) != dlc:
                            raise ValueError("Invalid CAN payload length")

                        row = {
                            "t": timestamp,
                            "can_id": can_id,
                            "data": data
                        }

                        bucket = math.floor(timestamp)

                        if current_bucket is None:
                            current_bucket = bucket

                        elif bucket != current_bucket:
                            process_window(bundle, current_bucket, current_rows, detector, week4_adapter)
                            current_rows = []
                            current_bucket = bucket

                        current_rows.append(row)
                        received += 1
                        counts = {
                            "frames": LIVE_STATUS["frames"] + 1,
                            "steering": LIVE_STATUS["steering"] + int(can_id.upper().replace("0X", "") in ("101", "00000101")),
                            "rpm": LIVE_STATUS["rpm"] + int(can_id.upper().replace("0X", "") in ("102", "00000102")),
                            "other": LIVE_STATUS["other"] + int(can_id.upper().replace("0X", "") not in ("101", "102", "00000101", "00000102"))
                        }
                        save_live_status(**counts, running=True, sniffer=True)

                        payload = data.hex(" ").upper() or "(empty)"
                        print(
                            f"[RX] ID={can_id} DLC={dlc} DATA={payload}",
                            flush=True
                        )

                    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
                        print(f"[INVALID FRAME] {error}", file=sys.stderr, flush=True)

            if current_rows:
                process_window(bundle, current_bucket, current_rows, detector, week4_adapter)

            print(f"[DISCONNECTED] Total received frames: {received}", flush=True)
            save_live_status(running=False, sniffer=False)

    finally:
        server.close()
        if os.path.lexists(SOCKET_PATH):
            if stat.S_ISSOCK(os.lstat(SOCKET_PATH).st_mode):
                os.unlink(SOCKET_PATH)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
