#!/usr/bin/env python3
"""Capture SocketCAN from candump -L into the EXACT original Week 1 CSV columns."""
import argparse
import csv
import os
import re
import select
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PATTERN = re.compile(r"^\((\d+(?:\.\d+)?)\)\s+vcan0\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)$")
HEADERS = ["timestamp_utc", "elapsed_seconds", "can_id", "dlc", "data_hex", "message_type"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seconds", type=float, default=23)
    p.add_argument("--out", default=str(Path(__file__).parent / "results" / "live_capture.csv"))
    a = p.parse_args()
    if not 1 <= a.seconds <= 300:
        p.error("--seconds must be between 1 and 300")
    output = Path(a.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        process = subprocess.Popen(["candump", "-L", "vcan0"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, bufsize=0)
    except FileNotFoundError:
        sys.exit("candump not installed. Run: sudo apt install can-utils")
    start = time.monotonic()
    received = 0
    buffered = b""
    try:
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(HEADERS)
            print(f"Capturing vcan0 for {a.seconds:.0f} seconds to {output}", flush=True)
            while time.monotonic() - start < a.seconds:
                if process.poll() is not None:
                    sys.exit("candump exited. Check that vcan0 exists and is UP.")
                ready, _, _ = select.select([process.stdout], [], [], .10)
                if not ready:
                    continue
                block = os.read(process.stdout.fileno(), 65536)
                if not block:
                    continue
                buffered += block
                while b"\n" in buffered:
                    raw_line, buffered = buffered.split(b"\n", 1)
                    line = raw_line.decode("ascii", errors="replace").strip()
                    match = PATTERN.match(line)
                    if not match:
                        continue
                    epoch, can_id, payload = match.groups()
                    if len(payload) % 2 or len(payload) > 16:
                        continue
                    try:
                        raw = bytes.fromhex(payload)
                    except ValueError:
                        continue
                    can_id = can_id.upper().zfill(3)
                    message_type = {"101": "STEERING", "102": "RPM"}.get(can_id, "UNKNOWN")
                    stamp = datetime.fromtimestamp(float(epoch), tz=timezone.utc).isoformat(timespec="milliseconds")
                    writer.writerow([stamp, f"{time.monotonic()-start:.6f}", can_id,
                                     len(raw), " ".join(f"{b:02X}" for b in raw), message_type])
                    stream.flush()
                    received += 1
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    print(f"Captured {received} frames. Saved to {output}")


if __name__ == "__main__":
    main()
