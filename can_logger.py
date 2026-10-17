
#!/usr/bin/env python3

import csv
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

INTERFACE = "vcan0"
OUTPUT_FILE = "data/can_traffic.csv"


def get_message_type(can_id):
    """Identify the simulated ECU from its CAN identifier."""
    if can_id == "101":
        return "STEERING"
    elif can_id == "102":
        return "RPM"
    return "UNKNOWN"


def main():
    os.makedirs("data", exist_ok=True)

    print("CAN-Sentinel Week 1 Traffic Logger")
    print(f"Interface: {INTERFACE}")
    print(f"Output: {OUTPUT_FILE}")
    print("Capturing CAN frames. Press Ctrl+C to stop.\n")

    try:
        process = subprocess.Popen(
            ["candump", "-L", INTERFACE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        print("Error: candump is not installed.")
        print("Install it with: sudo apt install can-utils")
        sys.exit(1)

    file_exists = (
        os.path.exists(OUTPUT_FILE)
        and os.path.getsize(OUTPUT_FILE) > 0
    )

    try:
        with open(
            OUTPUT_FILE, "a", newline="", encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(csv_file)

            if not file_exists:
                writer.writerow([
                    "timestamp_utc",
                    "elapsed_seconds",
                    "can_id",
                    "dlc",
                    "data_hex",
                    "message_type",
                ])

            start_time = time.monotonic()
            frame_count = 0

            for line in process.stdout:
                line = line.strip()

                # candump -L output resembles:
                # (timestamp) vcan0 101#FFE7
                parts = line.split()

                if len(parts) < 3:
                    continue

                timestamp = datetime.now(
                    timezone.utc
                ).isoformat(timespec="milliseconds")

                elapsed = round(
                    time.monotonic() - start_time, 3
                )

                frame_text = parts[-1]

                if "#" not in frame_text:
                    continue

                can_id, data_hex = frame_text.split("#", 1)

                # Remove CAN flag suffixes if present.
                can_id = can_id.upper().replace(
                    "0X", ""
                )

                if can_id.endswith(("R", "E")):
                    can_id = can_id[:-1]

                if len(data_hex) % 2 != 0:
                    continue

                try:
                    bytes.fromhex(data_hex)
                except ValueError:
                    continue

                dlc = len(data_hex) // 2

                writer.writerow([
                    timestamp,
                    elapsed,
                    can_id,
                    dlc,
                    " ".join(
                        data_hex[i:i + 2]
                        for i in range(0, len(data_hex), 2)
                    ),
                    get_message_type(can_id),
                ])

                csv_file.flush()
                frame_count += 1

                if frame_count % 10 == 0:
                    print(
                        f"Captured {frame_count} frames | "
                        f"Latest ID: {can_id} | "
                        f"Data: {data_hex}"
                    )

    except KeyboardInterrupt:
        print("\nStopping the logger...")

    finally:
        process.terminate()

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        print(f"Logger stopped. CSV saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
