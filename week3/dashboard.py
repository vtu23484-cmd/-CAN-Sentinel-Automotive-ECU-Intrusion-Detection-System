#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path

from PyQt6.QtCore import Qt, QRectF, QProcess, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QTextEdit, QPushButton
)

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "week3/socket_server.py"
SNIFFER = ROOT / "week3/sniffer"


class ThreatGauge(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(220, 190)
        self.level = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(25, 15, 170, 170)

        painter.setPen(QPen(QColor("#263449"), 13))
        painter.drawArc(rect, 225 * 16, -270 * 16)

        color = "#22c55e"
        if self.level >= 70:
            color = "#ef4444"
        elif self.level >= 30:
            color = "#f59e0b"

        painter.setPen(QPen(QColor(color), 13))
        painter.drawArc(
            rect, 225 * 16, int(-270 * 16 * self.level / 100)
        )

        painter.setPen(QColor("#f1f5f9"))
        painter.setFont(QFont("Arial", 27, QFont.Weight.Bold))
        painter.drawText(
            QRectF(25, 65, 170, 45),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.level}%"
        )

        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(
            QRectF(25, 108, 170, 25),
            Qt.AlignmentFlag.AlignCenter,
            "THREAT LEVEL"
        )
        painter.end()

    def set_level(self, level):
        self.level = max(0, min(100, int(level)))
        self.update()


class Panel(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("panel")
        self.layout = QVBoxLayout(self)

        heading = QLabel(title)
        heading.setObjectName("panelTitle")
        self.layout.addWidget(heading)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAN Sentinel | Automotive IDS")
        self.resize(1250, 850)

        self.messages = 0
        self.alerts = 0
        self.server_ready = False
        self.stopping = False

        self.startup_timer = QTimer(self)
        self.startup_timer.setSingleShot(True)
        self.startup_timer.timeout.connect(self.server_startup_timeout)

        self.server_process = QProcess(self)
        self.sniffer_process = QProcess(self)

        self.server_process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )
        self.sniffer_process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )

        self.server_process.readyReadStandardOutput.connect(
            self.read_server_output
        )
        self.sniffer_process.readyReadStandardOutput.connect(
            self.read_sniffer_output
        )
        self.server_process.finished.connect(self.server_finished)
        self.sniffer_process.finished.connect(self.sniffer_finished)

        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(22, 18, 22, 18)
        main.setSpacing(14)

        header = QHBoxLayout()
        title_area = QVBoxLayout()

        title = QLabel("CAN SENTINEL")
        title.setObjectName("mainTitle")
        subtitle = QLabel("AUTOMOTIVE INTRUSION DETECTION SYSTEM")
        subtitle.setObjectName("subtitle")

        title_area.addWidget(title)
        title_area.addWidget(subtitle)
        header.addLayout(title_area)
        header.addStretch()

        self.status = QLabel("● STOPPED")
        self.status.setObjectName("status")
        header.addWidget(self.status)
        main.addLayout(header)

        controls = QHBoxLayout()
        self.start_button = QPushButton("▶  START MONITORING")
        self.stop_button = QPushButton("■  STOP MONITORING")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)

        controls.addWidget(self.start_button)
        controls.addWidget(self.stop_button)
        controls.addStretch()
        main.addLayout(controls)

        cards = QGridLayout()
        cards.setSpacing(12)

        self.message_value = self.make_card(
            cards, 0, "CAN MESSAGES", "0", "Live frames received"
        )
        self.alert_value = self.make_card(
            cards, 1, "DETECTED ANOMALIES", "0", "ML / rule alerts"
        )
        self.ecu_value = self.make_card(
            cards, 2, "VIRTUAL ECUs", "2", "Steering + RPM"
        )
        self.model_value = self.make_card(
            cards, 3, "ML MODEL", "READY", "Week 2 Isolation Forest"
        )
        main.addLayout(cards)

        content = QGridLayout()
        content.setSpacing(14)

        threat_panel = Panel("THREAT MONITOR")
        self.gauge = ThreatGauge()
        threat_panel.layout.addWidget(self.gauge)
        self.threat_text = self.info_label("Awaiting live traffic")
        threat_panel.layout.addWidget(self.threat_text)

        ecu_panel = Panel("VIRTUAL VEHICLE NETWORK")
        self.ecu_status = self.info_label(
            "STEERING ECU       ● CONFIGURED\n\n"
            "RPM ECU                 ● CONFIGURED\n\n"
            "vcan0                      ○ CHECKING\n\n"
            "C SNIFFER                ○ STOPPED\n\n"
            "ML INFERENCE          ○ STOPPED"
        )
        ecu_panel.layout.addWidget(self.ecu_status)
        ecu_panel.layout.addStretch()

        content.addWidget(threat_panel, 0, 0)
        content.addWidget(ecu_panel, 0, 1)
        main.addLayout(content, 2)

        terminal_panel = Panel("LIVE CAN TRAFFIC AND ML EVENTS")
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 10))
        self.terminal.setMinimumHeight(250)
        self.terminal.setPlainText(
            "[SYSTEM] CAN Sentinel initialized.\n"
            "[SYSTEM] Press START MONITORING to begin.\n"
            "[SAFETY] Software simulation is restricted to vcan0.\n"
        )
        terminal_panel.layout.addWidget(self.terminal)
        main.addWidget(terminal_panel, 2)

        footer = QLabel(
            "CAN SENTINEL | WEEK 1 + WEEK 2 + WEEK 3 | "
            "ISOLATED SOFTWARE ENVIRONMENT"
        )
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(footer)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0b1220;
                color: #e2e8f0;
                font-family: Arial;
            }
            #mainTitle {
                font-size: 27px;
                font-weight: bold;
                color: #38bdf8;
            }
            #subtitle, #footer {
                color: #8293aa;
                font-size: 10px;
            }
            #status {
                color: #f59e0b;
                font-weight: bold;
                padding: 10px;
                border: 1px solid #73521d;
                border-radius: 7px;
            }
            #panel {
                background-color: #111c2e;
                border: 1px solid #263449;
                border-radius: 12px;
            }
            #panelTitle {
                color: #7dd3fc;
                font-size: 13px;
                font-weight: bold;
                padding-bottom: 8px;
            }
            QTextEdit {
                background-color: #070d18;
                color: #86efac;
                border: 1px solid #263449;
                border-radius: 7px;
                padding: 10px;
            }
            QPushButton {
                background-color: #075985;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 7px;
            }
            QPushButton:disabled {
                background-color: #263449;
                color: #8293aa;
            }
            QLabel {
                background: transparent;
            }
        """)

    def make_card(self, grid, column, title, value, description):
        card = Panel(title)
        value_label = QLabel(value)
        value_label.setStyleSheet(
            "font-size: 25px; font-weight: bold; color: #38bdf8;"
        )
        description_label = QLabel(description)
        description_label.setStyleSheet(
            "font-size: 10px; color: #8293aa;"
        )
        card.layout.addWidget(value_label)
        card.layout.addWidget(description_label)
        card.layout.addStretch()
        grid.addWidget(card, 0, column)
        return value_label

    def info_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 12px; color: #cbd5e1; padding: 10px;"
        )
        return label

    def log(self, message):
        self.terminal.append(message)
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_monitoring(self):
        if self.server_process.state() != QProcess.ProcessState.NotRunning:
            return

        if not SERVER.is_file() or not SNIFFER.is_file():
            self.log("[ERROR] Week 3 server or C sniffer is missing.")
            return

        check = subprocess.run(
            ["ip", "link", "show", "dev", "vcan0"],
            capture_output=True,
            text=True
        )
        if check.returncode != 0:
            self.log("[ERROR] vcan0 is unavailable.")
            self.log("[INFO] Set up the virtual CAN interface first.")
            return

        self.stopping = False
        self.server_ready = False
        self.messages = 0
        self.alerts = 0
        self.message_value.setText("0")
        self.alert_value.setText("0")
        self.gauge.set_level(0)
        self.threat_text.setText("Monitoring starting...")

        self.log("[SYSTEM] Starting Python ML server...")
        self.status.setText("● STARTING")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.server_process.start(
            sys.executable, ["-u", str(SERVER)]
        )

        self.startup_timer.start(15000)

    def server_startup_timeout(self):
        if not self.server_ready:
            self.log("[ERROR] Python server startup timed out.")
            self.stop_monitoring()

    def start_sniffer(self):
        if not self.server_ready:
            return

        if self.server_process.state() == QProcess.ProcessState.NotRunning:
            self.log("[ERROR] Python ML server stopped before sniffer startup.")
            self.stop_monitoring()
            return

        if self.sniffer_process.state() != QProcess.ProcessState.NotRunning:
            return

        self.log("[SYSTEM] Starting C CAN sniffer on vcan0...")
        self.sniffer_process.start(str(SNIFFER), [])

    def read_server_output(self):
        data = bytes(
            self.server_process.readAllStandardOutput()
        ).decode(errors="replace")

        for line in data.splitlines():
            if line.strip():
                self.log(line)

            if "[OK] Isolation Forest model loaded." in line:
                self.model_value.setText("LOADED")
                self.server_ready = True

            if "[2/3] Listening at /tmp/can_sentinel.sock" in line:
                self.server_ready = True
                self.startup_timer.stop()
                self.log("[SYSTEM] Python server ready. Starting C sniffer...")
                self.start_sniffer()

            if "[CONNECTED]" in line:
                self.status.setText("● CONNECTED")
                self.ecu_status.setText(
                    "STEERING ECU       ● CONFIGURED\n\n"
                    "RPM ECU                 ● CONFIGURED\n\n"
                    "vcan0                      ● ACTIVE\n\n"
                    "C SNIFFER                ● CONNECTED\n\n"
                    "ML INFERENCE          ● READY"
                )

            if "[RX]" in line:
                self.messages += 1
                self.message_value.setText(str(self.messages))

            if "[ALERT]" in line:
                self.alerts += 1
                self.alert_value.setText(str(self.alerts))
                self.gauge.set_level(80)
                self.threat_text.setText(
                    "ALERT: suspicious traffic detected"
                )

            elif "[NORMAL]" in line:
                self.gauge.set_level(5)
                self.threat_text.setText(
                    "Traffic classified as NORMAL"
                )

            if "[ERROR]" in line:
                self.status.setText("● ERROR")

    def read_sniffer_output(self):
        data = bytes(
            self.sniffer_process.readAllStandardOutput()
        ).decode(errors="replace")

        for line in data.splitlines():
            if line.strip():
                self.log("[C SNIFFER] " + line)

    def sniffer_finished(self, code, exit_status):
        if self.stop_button.isEnabled():
            self.log("[INFO] C sniffer stopped.")
            self.stop_monitoring()

    def server_finished(self, code, exit_status):
        if self.stop_button.isEnabled():
            self.log("[INFO] Python ML server stopped.")
            self.stop_monitoring()

    def stop_monitoring(self):
        if self.stopping:
            return

        self.stopping = True
        self.startup_timer.stop()
        self.log("[SYSTEM] Stopping monitoring...")

        for process in (self.sniffer_process, self.server_process):
            if process.state() != QProcess.ProcessState.NotRunning:
                process.terminate()
                if not process.waitForFinished(1500):
                    process.kill()
                    process.waitForFinished(1000)

        self.status.setText("● STOPPED")
        self.ecu_status.setText(
            "STEERING ECU       ● CONFIGURED\n\n"
            "RPM ECU                 ● CONFIGURED\n\n"
            "vcan0                      ○ AVAILABLE\n\n"
            "C SNIFFER                ○ STOPPED\n\n"
            "ML INFERENCE          ○ STOPPED"
        )
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log("[SYSTEM] Monitoring stopped.")

    def closeEvent(self, event):
        self.stop_monitoring()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
