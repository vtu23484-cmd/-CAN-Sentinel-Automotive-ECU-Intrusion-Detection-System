# CAN Sentinel — Automotive ECU Intrusion Detection System

  week- 1 
## 📌 Overview

CAN Sentinel is a cybersecurity project focused on detecting suspicious activities and potential intrusion attempts in automotive Electronic Control Units (ECUs) communicating over the Controller Area Network (CAN) bus.

The project aims to analyze CAN traffic, identify abnormal communication patterns, and support the detection of potential automotive cyber threats through traffic monitoring and testing.

## 🎯 Objectives

- Monitor and analyze simulated automotive CAN traffic.
- Identify suspicious messages and potential intrusion patterns.
- Test and demonstrate CAN traffic under normal and test scenarios.
- Improve awareness of security risks affecting automotive ECUs.
- Develop a foundation for an automotive intrusion detection system.

## 🛠️ Technologies Used

- **Programming Languages:** Python, C
- **Data Format:** CSV
- **Development Environment:** Visual Studio Code
- **Version Control:** Git and GitHub

## 📂 Project Structure

```text
CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System/
│
├── data/
│   ├── can_traffic.csv
│   ├── can_traffic_before_test.csv
│   ├── can_traffic_demo.csv
│   └── can_traffic_test.csv
│
├── can_logger.py
├── can_logger_demo.py
├── can_logger_test.py
├── rpm_ecu.c
├── steering_ecu.c
│
└── README.md
```

*Note: The structure above represents the current Week 1 files. Update it as additional modules are integrated into the repository.*

## 📊 Dataset Description

The `data/` directory contains CSV files used for CAN traffic analysis and testing.

- **can_traffic.csv** — CAN traffic dataset for analysis.
- **can_traffic_before_test.csv** — Traffic data collected before a test scenario.
- **can_traffic_demo.csv** — Data intended for demonstration purposes.
- **can_traffic_test.csv** — Traffic data intended for testing.

The actual fields, traffic labels, and attack scenarios depend on the contents of each dataset.

## ⚙️ Current Implementation

The initial implementation includes:

- CAN traffic logging scripts written in Python.
- Separate demo and test scripts.
- C programs representing RPM and steering ECU components.
- CSV datasets for traffic analysis, demonstrations, and testing.

These components provide a starting point for developing and evaluating the intrusion detection system.

## 🚀 Getting Started

### Prerequisites

- Python 3 installed.
- A C compiler, such as GCC, for compiling the ECU programs.
- Git installed.
- Visual Studio Code or another suitable code editor.

### Clone the Repository

```bash
git clone https://github.com/vtu23484-cmd/CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System.git
```

Navigate to the project directory:

```bash
**cd CAN-Sentinel-Automotive-ECU-Intrusion-Detection-System**
```

### Run the Python Logger

After verifying the script's dependencies and configuration, run:

```bash
python can_logger.py
```

For systems that use the `python3` command:

```bash
python3 can_logger.py
```

Refer to each script's implementation for its specific configuration, dependencies, and execution requirements.

## 🔬 Testing and Demonstration

The project includes separate scripts and datasets intended for testing and demonstration.

Testing should be performed in a controlled environment using simulated or authorized CAN traffic. Verify the logger output and dataset contents before evaluating detection results.

## 🔮 Future Enhancements

- Implement automated detection of anomalous CAN messages.
- Add detection rules for suspicious message IDs, frequencies, and payload patterns.
- Develop a dashboard for traffic monitoring and alert visualization.
- Evaluate detection accuracy using labeled datasets.
- Add event logging, reporting, and performance evaluation.
- Integrate additional ECU attack simulations in a controlled test environment.

## 👥 Contributors

Developed collaboratively as an academic cybersecurity project focused on automotive ECU intrusion detection.

## ⚠️ Disclaimer

This project is intended for educational, research, and authorized security-testing purposes. Testing should only be performed on simulated environments or systems for which explicit authorization has been obtained.
