#!/usr/bin/env python3
"""Compare injected frame count with observed matching frames in the vcan0 capture."""
import argparse
import json
import re
from pathlib import Path
from pipeline import load_csv

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", required=True)
    p.add_argument("--send-log", required=True)
    p.add_argument("--out", default=str(Path(__file__).parent / "results" / "audit.json"))
    a = p.parse_args()
    sent_match = re.search(r"\bSENT=(\d+)\b", Path(a.send_log).read_text())
    if not sent_match:
        raise SystemExit("No SENT= count found in attacker log")
    sent = int(sent_match.group(1))
    frames = load_csv(a.capture)
    seen = sum(r["data"] == b"\x7f\xff" and r["can_id"] == "101" for r in frames)
    summary = {"attacker_frames_sent": sent, "attacker_frames_observed": seen,
               "observed_missing": max(0, sent-seen),
               "result": "matched" if seen == sent else "different",
               "scope": "Only uniquely tagged 0x101 7FFF frames in this vcan0 capture"}
    Path(a.out).parent.mkdir(exist_ok=True,parents=True)
    Path(a.out).write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
