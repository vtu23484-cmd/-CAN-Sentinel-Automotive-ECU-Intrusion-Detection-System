# CAN Sentinel – Automotive ECU Intrusion Detection System

## 1. Project Overview

**CAN Sentinel** is an academic cybersecurity project focused on detecting suspicious activity and potential intrusions in an automotive Controller Area Network (CAN).

Modern vehicles use ECUs (Electronic Control Units) to manage important functions such as engine operation, steering, braking, and other vehicle systems. These ECUs communicate through the CAN bus. However, CAN communication does not provide built-in authentication or encryption in its traditional form, making it important to monitor network traffic for suspicious activity.

This project develops a progressive CAN Intrusion Detection System (IDS) across four development stages:

- **Week 1:** CAN environment setup and basic CAN communication.
- **Week 2:** ECU simulation, attack simulation, traffic capture, and machine-learning-based anomaly detection.
- **Week 3:** Behavioral anomaly detection, CAN sniffing, forensic incident handling, and web dashboard.
- **Week 4:** Advanced anomaly detection, risk scoring, incident storage, model comparison, and forensic reporting.

The project is intended for academic research, demonstration, and cybersecurity learning.

---

## 2. Project Objectives

- Understand automotive CAN communication.
- Simulate communication between multiple ECUs.
- Generate normal and suspicious CAN traffic in an isolated test environment.
- Capture and analyze CAN messages.
- Detect abnormal CAN communication patterns.
- Explore machine-learning-based intrusion detection.
- Monitor suspicious ECU behavior.
- Maintain incident records and forensic evidence.
- Present detection results through a local dashboard.
- Evaluate the system through automated tests.

---

## 3. Project Development – Week 1 to Week 4

### Week 1 – CAN Environment Setup and Basic Communication

**Objective:** Establish the basic environment required for automotive CAN communication and intrusion detection.

Main activities:

- Set up the Linux development environment.
- Configure the virtual CAN interface.
- Understand CAN communication and CAN frames.
- Explore CAN message transmission and reception.
- Establish the foundation for ECU communication and traffic monitoring.

Main project areas:

- CAN interface configuration.
- Basic CAN communication scripts.
- Initial traffic generation and monitoring.
- Environment preparation.

**Purpose:** Build the foundation for subsequent ECU simulation and intrusion detection.

### Week 2 – ECU Simulation and Machine Learning-Based Detection

**Objective:** Simulate ECU communication, generate CAN traffic, and explore anomaly detection.

Main activities:

- Simulate ECU communication.
- Generate normal CAN traffic.
- Simulate suspicious CAN activity in an isolated virtual environment.
- Capture CAN traffic for analysis.
- Collect and process traffic data.
- Use an Isolation Forest model for anomaly detection.
- Analyze captured traffic and detection results.

Important project components include:

- `week2/setup_vcan.sh` – virtual CAN interface setup.
- `week2/attacker` – attack simulation component.
- `week2/rpm_ecu` – RPM ECU simulation.
- `week2/steering_ecu` – steering ECU simulation.
- `week2/results/` – traffic captures, logs, model, and detection results.

**Purpose:** Demonstrate how abnormal CAN traffic can be identified using traffic analysis and machine learning.

### Week 3 – Behavioral Detection and Web Dashboard

**Objective:** Improve detection by analyzing ECU behavior and providing a dashboard for monitoring.

Main files:

| File | Purpose |
|---|---|
| `week3/behavioral_detector.py` | Behavioral anomaly detection |
| `week3/dashboard.py` | Dashboard-related functionality |
| `week3/forensic_manager.py` | Forensic incident handling |
| `week3/sniffer.c` | CAN sniffer source code |
| `week3/socket_server.py` | Socket communication server |
| `week3/web_dashboard.py` | Local web dashboard server |
| `week3/web/index.html` | Dashboard interface |

Main activities:

- Monitor CAN traffic.
- Analyze ECU behavior.
- Detect suspicious communication patterns.
- Capture traffic using the CAN sniffer.
- Manage forensic incidents.
- Display monitoring information through a web dashboard.

**Launch command:**

```bash
./week3.sh
```

Open the dashboard in a browser:

```text
http://127.0.0.1:8765
```

The launcher prepares the virtual CAN interface, checks the Python environment, compiles the C sniffer, and starts the dashboard.

**Purpose:** Provide behavioral monitoring and a visual interface for observing CAN intrusion detection activity.

### Week 4 – Advanced Detection, Risk Scoring and Forensics

**Objective:** Extend CAN Sentinel with advanced detection, incident management, and forensic reporting.

Main components:

| File | Purpose |
|---|---|
| `week4/detection/timing_detector.py` | Detects CAN message timing deviations |
| `week4/detection/payload_detector.py` | Detects suspicious payload patterns |
| `week4/detection/advanced_engine.py` | Combines advanced detection results |
| `week4/detection/risk_scorer.py` | Calculates project-specific risk scores |
| `week4/detection/incident_manager.py` | Manages security incidents |
| `week4/detection/incident_store.py` | Stores incident records |
| `week4/detection/live_adapter.py` | Adapter for live-data integration |
| `week4/models/baseline.json` | Saved baseline data |
| `week4/models/save_baseline.py` | Creates and saves the baseline |
| `week4/models/model_comparison.py` | Compares detection models |
| `week4/reports/export_forensics.py` | Exports forensic reports |
| `week4/run_tests.sh` | Week 4 automated test launcher |
| `week4/tests/` | Automated test suite |

Main activities:

- Detect abnormal CAN message timing.
- Analyze suspicious payload patterns.
- Combine detection findings.
- Calculate risk scores.
- Manage and store security incidents.
- Compare detection models.
- Export forensic incident reports.
- Run automated tests.

**Launch command:**

```bash
./week4.sh
```

Run only the Week 4 test suite:

```bash
bash week4/run_tests.sh
```

Export the forensic report independently:

```bash
.venv/bin/python -m week4.reports.export_forensics
```

Expected forensic report location:

```text
week4/reports/forensic_report.json
```

**Purpose:** Provide a more complete intrusion detection and incident investigation workflow.

---

## 4. Repository Structure

The repository is organized into weekly development stages.

```text
CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System/
│
├── week1.sh
├── week2.sh
├── week3.sh
├── week4.sh
├── normal_traffic.sh
│
├── week2/
│   ├── setup_vcan.sh
│   ├── attacker
│   ├── rpm_ecu
│   ├── steering_ecu
│   └── results/
│
├── week3/
│   ├── behavioral_detector.py
│   ├── dashboard.py
│   ├── forensic_manager.py
│   ├── sniffer.c
│   ├── socket_server.py
│   ├── web_dashboard.py
│   ├── web/
│   └── results/
│
├── week4/
│   ├── detection/
│   ├── models/
│   ├── reports/
│   ├── results/
│   ├── tests/
│   ├── run_tests.sh
│   └── README.md
│
├── CAN-Sentinel/
│   └── README.md
│
├── data/
├── backups/
└── README.md
```

*Note: This is a high-level structure. Additional scripts, logs, datasets, databases, and generated files may exist in individual directories.*

---

## 5. Technologies and Dependencies

The project uses the following technologies and tools:

| Technology | Purpose |
|---|---|
| Ubuntu / Linux | Development and execution environment |
| WSL2 | Running Ubuntu on Windows |
| Python 3 | Detection logic and automation |
| Bash | Launchers and setup scripts |
| GCC | Compiling the Week 3 C sniffer |
| SocketCAN | Linux CAN communication framework |
| Virtual CAN (`vcan`) | Isolated CAN testing |
| Scikit-learn | Machine-learning-based anomaly detection |
| Isolation Forest | Anomaly detection model |
| SQLite | Incident and event storage |
| HTML | Dashboard interface |
| JSON / CSV | Data storage and reporting |
| Git and GitHub | Version control and project hosting |

### System requirements

- Windows with WSL2, or a compatible Linux environment.
- Ubuntu.
- Python 3.
- Python virtual environment support.
- GCC compiler for the Week 3 sniffer.
- Linux SocketCAN and virtual CAN support.
- Required Python packages used by the project.

### Python dependencies

The project uses a local Python virtual environment:

```text
.venv/
```

Set up the project environment using the existing Week 2 launcher:

```bash
./week2.sh
```

The exact Python package list should be maintained in a project dependency file such as `requirements.txt` if one is provided. Check the repository for the actual dependency manifest before installing packages manually.

---

## 6. Running the Project

Run commands from the repository root in Ubuntu/WSL.

### Step 1 – Set up the environment

```bash
./week2.sh
```

### Step 2 – Run Week 1

```bash
./week1.sh
```

### Step 3 – Run Week 2

```bash
./week2.sh
```

### Step 4 – Run Week 3

```bash
./week3.sh
```

Dashboard:

```text
http://127.0.0.1:8765
```

### Step 5 – Run Week 4

```bash
./week4.sh
```

### Stop running processes

Use:

```text
Ctrl+C
```

in the terminal running the relevant launcher.

---

## 7. Running from Windows CMD using WSL2

If you are using Windows CMD, you can execute the project launchers through WSL.

Example:

```cmd
wsl -d Ubuntu --cd "~/-CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System" --exec bash -lc "./week2.sh"
```

For Week 1:

```cmd
wsl -d Ubuntu --cd "~/-CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System" --exec bash -lc "./week1.sh"
```

For Week 3:

```cmd
wsl -d Ubuntu --cd "~/-CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System" --exec bash -lc "./week3.sh"
```

For Week 4:

```cmd
wsl -d Ubuntu --cd "~/-CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System" --exec bash -lc "./week4.sh"
```

---

## 8. Testing and Verification

The project includes different testing and validation activities across its development stages.

### Week 2

- Verify virtual CAN interface setup.
- Check ECU simulation.
- Capture normal and suspicious traffic.
- Review traffic logs and anomaly detection outputs.

### Week 3

- Build the CAN sniffer.
- Start the dashboard.
- Verify local dashboard access.
- Review behavioral detection and forensic outputs.

### Week 4

Run the complete test suite:

```bash
bash week4/run_tests.sh
```

Individual tests:

```bash
.venv/bin/python week4/tests/test_advanced_engine.py
.venv/bin/python week4/tests/test_incident_manager.py
.venv/bin/python week4/tests/test_incident_store.py
.venv/bin/python week4/tests/test_live_adapter.py
.venv/bin/python week4/tests/test_model_comparison.py
.venv/bin/python week4/tests/test_payload_detector.py
.venv/bin/python week4/tests/test_risk_scorer.py
.venv/bin/python week4/tests/test_saved_baseline.py
.venv/bin/python week4/tests/test_timing_detector.py
```

Review generated results in the relevant `results/` and `reports/` directories.

---

## 9. Expected Outputs

Depending on the development stage and tests executed, the project can generate:

- CAN traffic capture logs.
- ECU simulation logs.
- Normal and suspicious traffic datasets.
- Machine-learning anomaly detection results.
- Behavioral detection results.
- Incident records.
- SQLite incident databases.
- Model comparison results.
- Forensic reports in JSON or CSV format.
- Local dashboard monitoring information.

Generated results are stored in the respective weekly project directories.

---

## 10. Security and Safety Considerations

**Important: This project is an academic and experimental CAN intrusion detection system.**

- Use `vcan0` or offline datasets for synthetic CAN traffic and attack demonstrations.
- Never inject synthetic attack traffic into a real vehicle or safety-critical CAN network.
- Do not connect attack simulation scripts to an actual vehicle.
- Treat detection thresholds and risk scores as experimental.
- Risk scores are project-specific indicators, not validated attack probabilities.
- A successful virtual CAN test does not establish readiness for real-vehicle deployment.
- Live CAN integration requires separate safety engineering, validation, and authorization.

---

## 11. Current Project Scope and Limitations

CAN Sentinel demonstrates a progressive approach to automotive network intrusion detection.

The project explores:

- Basic CAN communication.
- ECU simulation.
- Traffic capture and analysis.
- Machine-learning-based anomaly detection.
- Behavioral monitoring.
- Advanced detection methods.
- Incident management.
- Risk scoring.
- Forensic reporting.

The system is not certified for automotive production deployment. Its detection accuracy, performance, thresholds, and compatibility with real vehicle networks require further independent validation.

---

## 12. Future Enhancements

Potential future improvements include:

- More advanced CAN intrusion detection algorithms.
- Improved detection accuracy and false-positive reduction.
- Additional ECU behavioral profiles.
- Real-time alerting and notifications.
- Improved dashboard visualization.
- Extended forensic evidence and audit trails.
- Larger and more diverse CAN datasets.
- Independent performance evaluation.
- Safety-reviewed integration with authorized automotive test benches.

---

## 13. Documentation

Additional project documentation:

- [Week 4 Documentation](week4/README.md)
- [Company-Oriented CAN Sentinel Documentation](CAN-Sentinel/README.md)

---

## 14. Conclusion

CAN Sentinel demonstrates the development of an automotive CAN Intrusion Detection System from basic CAN communication and ECU simulation to behavioral monitoring, advanced anomaly detection, incident management, and forensic reporting.

Through four development stages, the project provides a practical learning platform for understanding automotive cybersecurity and the challenges involved in detecting suspicious CAN bus activity.

**Project:** CAN Sentinel – Automotive ECU Intrusion Detection System  
**Focus:** Automotive Cybersecurity and CAN Intrusion Detection  
**Environment:** Ubuntu / WSL2  
**Development stages:** Week 1 to Week 4
