CAN-Sentinel — Week 1 Implementation

Project: Automotive ECU Intrusion Detection System
Week 1 Focus: Virtual CAN Network Simulation and Traffic Logging

1. Overview

CAN-Sentinel is a project focused on monitoring Controller Area Network (CAN) traffic to support the detection of potential security threats in automotive electronic control units (ECUs).

Week 1 establishes the basic environment for CAN communication, simulates ECU activity, and records CAN messages in CSV format for future analysis.

2. Implemented Features

- Virtual CAN Network: Configured a "vcan0" virtual CAN interface using Linux SocketCAN tools.
- ECU Simulation: Developed C programs to simulate Steering ECU and RPM ECU activity.
- CAN Communication: Tested CAN frame transmission and reception using "cansend" and "candump".
- Traffic Logging: Implemented a Python logger to capture CAN traffic from "vcan0".
- CSV Data Storage: Stored captured CAN messages in CSV files for further analysis.
- Message Identification: Recorded CAN IDs, data length, hexadecimal payload, timestamps, elapsed time, and message type.
- Traffic Validation: Tested the logger using manually transmitted CAN frames and generated demonstration traffic.

3. Technologies Used

- Operating System: Ubuntu on WSL
- Programming Languages: C, Python
- CAN Communication: Linux SocketCAN, "vcan0", "can-utils"
- Compiler: GCC
- Data Storage: CSV files
- Version Control: Git and GitHub

4. Project Structure

CAN-sentinel/
├── can_logger.py
├── can_logger_demo.py
├── can_logger_test.py
├── steering_ecu.c
├── rpm_ecu.c
├── data/
│   ├── can_traffic.csv
│   ├── can_traffic_before_test.csv
│   ├── can_traffic_demo.csv
│   └── can_traffic_test.csv
└── .gitignore

5. CAN Message Identification

The ECU simulators use the following CAN identifiers:

CAN ID| Message Type
"101"| Steering ECU
"102"| RPM ECU

The Python logger reads CAN traffic and records the messages in CSV format.

CSV Fields

Field| Description
"timestamp_utc"| UTC timestamp of the recorded message
"elapsed_seconds"| Elapsed time associated with the recording
"can_id"| CAN message identifier
"dlc"| Data Length Code
"data_hex"| CAN payload in hexadecimal format
"message_type"| Identified message type

6. Setup and Execution

Step 1: Install the required packages

sudo apt update
sudo apt install -y build-essential can-utils iproute2 python3 python3-pip python3-venv

Step 2: Configure the virtual CAN interface

sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

Verify the interface:

ip -details link show vcan0

If "vcan0" already exists, reuse it instead of creating it again.

Step 3: Compile the ECU simulators

Navigate to the Week 1 project directory:

cd ~/can-sentinel/week1

Compile the Steering ECU:

gcc steering_ecu.c -o steering_ecu

Compile the RPM ECU:

gcc rpm_ecu.c -o rpm_ecu

Step 4: Monitor CAN traffic

candump vcan0

Step 5: Test CAN frame transmission

Open another terminal and execute:

cansend vcan0 123#1122334455667788

The transmitted frame can be observed in the terminal running "candump".

Step 6: Run the Python traffic logger

python3 can_logger.py

The logger records CAN messages in the configured CSV output file. Press "Ctrl+C" to stop the logger.

Note: The "can_logger_test.py" and "can_logger_demo.py" scripts use separate CSV output files for testing and demonstration.

7. Testing and Results

The following Week 1 activities were implemented and tested:

- Created and activated the "vcan0" virtual CAN interface.
- Compiled and tested both ECU simulator programs.
- Verified CAN frame transmission and reception.
- Captured CAN traffic using "candump".
- Recorded CAN messages using the Python logger.
- Verified that manually transmitted CAN frames were recorded.
- Generated demonstration traffic containing Steering ECU and RPM ECU messages.
- Stored captured traffic in CSV files for subsequent processing.

The demonstration capture contained 408 CAN message records: 305 Steering ECU records and 103 RPM ECU records.

8. Current Implementation Status

Completed in Week 1:

- Virtual CAN network configuration.
- Steering and RPM ECU simulation using C.
- CAN frame transmission and reception testing.
- Python-based CAN traffic logging.
- CSV storage and demonstration testing.

Not yet implemented in Week 1:

- Malicious CAN traffic generation using a dedicated attacker script.
- Isolation Forest model training.
- Machine-learning-based anomaly detection.
- Automated attack alerts and threat classification.
- Native PyQt monitoring dashboard.

These features are planned for subsequent development stages.

9. Conclusion

Week 1 established the foundation for CAN-Sentinel by setting up a virtual CAN environment, simulating ECU communication, and capturing CAN traffic in structured CSV files. The recorded data will serve as a starting point for the machine-learning-based anomaly detection work planned for Week 2.
