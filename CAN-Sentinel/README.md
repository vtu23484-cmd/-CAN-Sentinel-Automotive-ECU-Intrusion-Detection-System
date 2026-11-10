# CAN-Sentinel — Company-Oriented Automotive CAN IDS Pilot

**Scope:** a local engineering pilot aligned with the Infotact project brief, Project 1 (PDF pages 1–2). It implements virtual CAN simulation, a low-level C SocketCAN sniffer, Python feature extraction, Isolation Forest scoring, deterministic anomaly rules, a native PyQt dashboard, and a durable SQLite event/alert store.

> **Important deployment boundary:** this is a company-style prototype for lab validation, not certified automotive safety/security software. Use `vcan0` only. Never connect the traffic generator to a real vehicle, production ECU, or physical CAN adapter. CAN ID-to-ECU labels are illustrative; CAN identifiers do not prove sender identity.

## What is improved for a company review

- **Traceable evidence:** every captured frame includes a session ID, timestamp, interface, CAN ID, payload, feature values, ML score, and detection result.
- **Durable storage:** SQLite with WAL and indexes replaces opening/writing CSV files for every frame. CSV export can be added through `EventStore.export_csv()` for offline review.
- **Per-ID feature engineering:** message rates and inter-arrival intervals are calculated per arbitration ID, avoiding a misleading global traffic rate.
- **Hybrid detection:** Isolation Forest is combined with explicit rules for burst rates, extremely short intervals, invalid classic-CAN DLC, and high payload entropy.
- **Alert deduplication:** repeated similar alerts are grouped into an open incident with an occurrence count instead of flooding the operator.
- **Operator context:** severity, session identifier, likely signal mapping, and a clear lab/pilot disclaimer are visible in the desktop UI.
- **Automated tests:** feature behavior, per-ID rate isolation, SQLite persistence, and alert deduplication are tested.

## Architecture

`vcan0` → C SocketCAN sniffer (standalone raw-frame diagnostic) / python-can live detector → per-ID feature builder → rules + Isolation Forest → SQLite evidence store → PyQt operator dashboard.

The dashboard currently consumes frames directly through python-can. The C sniffer is separately available for low-level verification and emits JSON Lines. For a production deployment, use a versioned IPC contract and integration tests to connect the C sniffer to the detector instead of running two independent capture paths.

## Environment

- Ubuntu 22.04/24.04 or a full Ubuntu VM (recommended on Windows)
- Python 3.10+, GCC, Linux SocketCAN and `vcan` kernel module
- `can-utils` for independent traffic checks

```bash
sudo apt update
sudo apt install -y build-essential can-utils python3-venv python3-dev
chmod +x scripts/setup_vcan.sh
sudo ./scripts/setup_vcan.sh vcan0
make
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 python/train_model.py --output models/isolation_forest.joblib
```

The default model training script uses a **synthetic baseline**. This supports a reproducible demonstration only; it does not establish real-world detection accuracy. A company pilot must train/evaluate on representative, authorized, non-sensitive captures from the target vehicle/network and record dataset provenance.

## Run

Terminal 1 — dashboard and live detector:

```bash
source .venv/bin/activate
python3 python/dashboard.py --interface vcan0 --model models/isolation_forest.joblib
```

Terminal 2 — normal synthetic traffic:

```bash
source .venv/bin/activate
python3 python/traffic.py --interface vcan0 --mode normal --duration 60
```

Terminal 2 — controlled synthetic anomaly (after the normal run):

```bash
source .venv/bin/activate
python3 python/traffic.py --interface vcan0 --mode anomaly --duration 10
```

Optional independent C capture in another terminal:

```bash
./build/can_sniffer vcan0 | tee data/sniffer_capture.jsonl
```

## Tests and acceptance evidence

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
make clean && make
```

Minimum pilot acceptance criteria to record (do not claim results until measured):

1. Five or more independent normal-traffic runs and five or more anomaly runs.
2. Record true positives, false positives, false negatives, detection latency, dropped frames, and CPU/RAM use.
3. Verify each alert links to raw evidence and the model version/session that generated it.
4. Tune thresholds on training/validation data, then evaluate on a separate holdout capture.
5. Review false positives with a domain engineer and maintain a versioned CAN-ID/signal catalogue.
6. Test sustained load, clock anomalies, malformed input, storage exhaustion, application restart, and clean shutdown.

## Data and audit

- `data/can_sentinel.db` — SQLite frame and alert history
- `models/isolation_forest.joblib` — model bundle with feature schema and training metadata
- `data/baseline_features.csv` — training data snapshot
- `data/sniffer_capture.jsonl` — optional C-sniffer capture

Back up the database before cleaning data. Use only synthetic data or authorized captures. Establish retention, access control, encryption-at-rest, change control, and incident review procedures before any workplace deployment.

## Known limitations / production gates

- Synthetic traffic and baseline; no claimed accuracy or false-positive rate.
- Rule thresholds are initial defaults and require vehicle-specific calibration.
- The model is a supporting signal, not a safety decision system.
- CAN ID mapping is illustrative; ECU attribution requires a verified DBC/network specification and additional evidence.
- Classical CAN frames are limited to 8 payload bytes; CAN FD needs separate support and testing.
- Local SQLite and a desktop UI are appropriate for a single-operator pilot, not multi-user fleet scale.
- No active blocking, error-frame injection, or control of real vehicle traffic is implemented.
- Before production: threat model, secure software supply chain, signed/versioned models, role-based access, tamper-evident audit, formal performance evaluation, HIL testing, safety review, and relevant automotive cybersecurity process compliance are required.

See `docs/PROJECT_MAPPING.md` for source requirement traceability and `docs/COMPANY_PILOT_PLAN.md` for the staged validation plan.

## Windows-only quick start (no Ubuntu required for simulation)

This project now includes a **Windows simulation mode** using localhost UDP so you can demonstrate the detector and desktop dashboard without Linux or a physical CAN interface. This mode simulates CAN frames; it is not the Linux kernel SocketCAN sniffer path described in the original project brief.

1. Install **Python 3.11 or 3.12 (64-bit)** from python.org. During setup, enable **Add Python to PATH**.
2. Extract the ZIP to a normal folder, for example `C:\CAN-Sentinel` (avoid running it from inside the ZIP).
3. Double-click `run_windows.bat`. It creates a virtual environment, installs packages, trains a demonstration model, and opens the dashboard.
4. Leave the dashboard open. Double-click `run_normal_traffic.bat` to send normal synthetic frames.
5. Double-click `run_anomaly_test.bat` to send a controlled high-rate synthetic anomaly and observe dashboard alerts.

If Windows Firewall asks about network access, the simulation uses only `127.0.0.1` (this computer). Do not allow public-network access; if asked, cancel the prompt or allow only private/local access as appropriate.

For the full low-level requirement from the PDF—Linux `vcan0`, kernel SocketCAN capture, and C sniffer—use Ubuntu/Linux. Windows simulation mode is provided for easier demonstration and development on a Windows-only laptop. All traffic generators are intended for the local simulator only; never connect them to a real vehicle network.
