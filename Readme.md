# CAN-Sentinel: Automotive ECU Intrusion Detection System

CAN-Sentinel is an educational cybersecurity project that simulates communication between automotive Electronic Control Units (ECUs), captures Controller Area Network (CAN) frames, and detects unusual traffic patterns. It uses a **virtual CAN interface (`vcan0`)** for safe testing; it is not designed to connect to or control a real vehicle.

## Project Goals

- Simulate normal Steering ECU and RPM ECU communication.
- Capture and store CAN traffic in CSV format.
- Generate controlled, synthetic high-frequency CAN traffic for testing.
- Train an Isolation Forest model on baseline traffic.
- Flag unusual traffic patterns for further investigation.
- Produce logs, audit results, and an HTML mid-review report.

## Current Features

### Week 1 — CAN simulation and logging
- Virtual CAN network using Linux SocketCAN and `vcan0`.
- C-based Steering ECU and RPM ECU simulators.
- CAN frame testing with `cansend` and `candump`.
- Python traffic logger and CSV storage.
- Captured fields include timestamps, elapsed time, CAN ID, DLC, hexadecimal payload, and message type.

### Week 2 — Detection demonstration
- C-based synthetic CAN traffic injector for controlled testing.
- Baseline training using an Isolation Forest machine-learning model.
- Live virtual-CAN capture and anomaly detection.
- Sent-versus-received traffic audit.
- HTML report generation.

> Detection results are experimental and intended for a student demonstration. An anomaly is not automatically proof of a real attack, and this prototype is not a production automotive safety system.

## Technology Stack

- **Languages:** Python and C
- **CAN networking:** Linux SocketCAN, `vcan0`, `can-utils`
- **Machine learning:** scikit-learn Isolation Forest
- **Data:** CSV, JSON, logs, HTML report
- **Build tools:** GCC, Bash
- **Environment:** Ubuntu Linux or Ubuntu on WSL2
- **Version control:** Git and GitHub

## Repository Structure

```text
CAN-Sentinel/
├── README.md
├── can_logger.py
├── can_logger_demo.py
├── can_logger_test.py
├── can_traffic.csv
├── can_traffic_before_test.csv
├── can_traffic_demo.csv
├── can_traffic_test.csv
├── steering_ecu.c
├── rpm_ecu.c
├── START_WEEK2.sh
├── START_WEEK2_WINDOWS.bat
└── week2/
    ├── attacker.c
    ├── audit.py
    ├── build.sh
    ├── capture.py
    ├── detect.py
    ├── live_report.py
    ├── pipeline.py
    ├── requirements.txt
    ├── review_offline.py
    ├── run_live_review.sh
    ├── setup_vcan.sh
    ├── train.py
    ├── tests/
    │   └── test_week2.py
    └── results/
        ├── LIVE_MID_REVIEW.html
        ├── live_capture.csv
        ├── live_detection.csv
        └── supporting logs and audit output
```

The `week2/results/` files are generated or updated by the demonstration scripts. Exact contents may vary by run.

## Requirements

For the live demonstration, use **Ubuntu Linux or Ubuntu on WSL2** with a kernel that supports SocketCAN and virtual CAN.

Required tools:
- GCC / build-essential
- Python 3 and `venv`
- `iproute2`
- `can-utils`
- `kmod` (for `modprobe`)
- Python packages listed in `week2/requirements.txt`

The Windows batch file is a launcher for Ubuntu WSL2; it does not run the CAN networking code natively in Windows Command Prompt.

## Quick Start — Ubuntu / WSL2

### Option A: Run the complete Week 2 demonstration

From the repository root in Ubuntu/WSL2:

```bash
chmod +x START_WEEK2.sh week2/*.sh
./START_WEEK2.sh
```

The script checks/installs required Linux tools, creates a Python virtual environment, installs the machine-learning dependencies, and launches the live virtual-CAN demonstration. It may request your Linux password for `sudo`.

When it finishes, open:

```text
week2/results/LIVE_MID_REVIEW.html
```

### Option B: Start from Windows

1. Install WSL2 and Ubuntu if they are not already installed.
2. Extract the repository into a Windows folder accessible from WSL.
3. Double-click `START_WEEK2_WINDOWS.bat`, or run it from Command Prompt.
4. If it fails, open Ubuntu and try `./START_WEEK2.sh` from the repository directory to see the full error.

If `vcan0` cannot be created, update WSL from an Administrator PowerShell window:

```powershell
wsl --update
wsl --shutdown
```

Then reopen Ubuntu and retry. Some WSL/kernel environments may not support the required virtual CAN operations; a compatible Linux VM or Linux machine may be needed.

## Manual Week 1 Setup

Run these commands in Ubuntu. Execute commands from the repository root unless noted.

### 1. Install system packages

```bash
sudo apt update
sudo apt install -y build-essential can-utils iproute2 kmod python3 python3-pip python3-venv
```

### 2. Create the virtual CAN interface

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
ip -details link show vcan0
```

If `vcan0` already exists, do not create it again; bring it up with:

```bash
sudo ip link set up vcan0
```

### 3. Compile the ECU simulators

```bash
gcc steering_ecu.c -o steering_ecu
gcc rpm_ecu.c -o rpm_ecu
```

### 4. Observe traffic

In one terminal:

```bash
candump vcan0
```

In another terminal, send a test frame:

```bash
cansend vcan0 123#1122334455667788
```

The frame should appear in the `candump` terminal if the interface is working.

### 5. Run the Week 1 logger

In another terminal:

```bash
python3 can_logger.py
```

Stop the logger with `Ctrl+C`. Check the configured CSV output file for recorded messages. The demo and test logger scripts use their own output files.

## Week 2 Detection Workflow

The complete launcher runs the following workflow:

1. Configure `vcan0`.
2. Compile the Steering ECU, RPM ECU, and synthetic attacker.
3. Train the Isolation Forest model using `can_traffic_demo.csv`.
4. Capture live frames from the virtual CAN interface.
5. Run normal ECU simulators, then send controlled high-frequency synthetic frames.
6. Run anomaly detection and audit sent/received traffic.
7. Generate `week2/results/LIVE_MID_REVIEW.html`.

The scripts and parameters are available in `week2/`. Review their output logs if a stage fails.

## CSV Data Format

The logger's CSV format includes these columns:

| Column | Meaning |
|---|---|
| `timestamp_utc` | UTC time associated with the captured frame |
| `elapsed_seconds` | Elapsed time recorded by the logger |
| `can_id` | CAN message identifier |
| `dlc` | Data Length Code / payload length |
| `data_hex` | Payload bytes represented in hexadecimal |
| `message_type` | Label assigned by the logger |

The Week 2 pipeline validates the CSV structure and checks CAN identifiers, elapsed times, DLC values, and payload lengths before feature extraction.

## Troubleshooting

### `vcan0` already exists
Run:

```bash
sudo ip link set dev vcan0 up
```

### `RTNETLINK answers: Operation not supported` or permission errors
- Confirm that the command is running inside Ubuntu/Linux, not plain Windows Command Prompt.
- Update WSL2 and restart it.
- Confirm your environment permits virtual CAN and network-interface administration.
- If unsupported, use a compatible Linux VM or Linux computer.

### `ModuleNotFoundError` for `sklearn`, `joblib`, or `numpy`
From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r week2/requirements.txt
```

Then run `./START_WEEK2.sh` again, or use the project's scripts with the same virtual environment.

### No frames appear in `candump`
- Check that `vcan0` exists and is up: `ip -brief link show vcan0`
- Keep `candump vcan0` running while sending a frame.
- Ensure all commands use the same Linux/WSL environment.

### The HTML report is not created
Read the terminal output and logs in `week2/results/`. The report is generated only after the earlier capture, detection, and audit stages complete successfully.

## Safety and Responsible Use

- Use only the provided virtual CAN network for this demonstration.
- Do not connect the synthetic attacker to a real vehicle or safety-critical system.
- Do not interpret model alerts as definitive proof of malicious activity.
- Validate any future extensions with controlled datasets and documented tests.

## Future Improvements

- Add more ECU message patterns and larger baseline datasets.
- Evaluate detection accuracy with labelled normal and synthetic attack traffic.
- Add configurable alert thresholds and clearer alert explanations.
- Add a dashboard for live traffic and investigation history.
- Improve automated tests and document precision, recall, and false-positive rates.

## Author / Project Information

**Project:** CAN-Sentinel — Automotive ECU Intrusion Detection System  
**Focus:** Virtual CAN simulation, traffic logging, and anomaly detection  
**Purpose:** Educational cybersecurity project / internship demonstration

Add your name, institution, mentor, internship organization, and project dates here if required by your submission format.
