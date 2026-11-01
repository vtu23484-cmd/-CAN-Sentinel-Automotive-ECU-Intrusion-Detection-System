#!/usr/bin/env python3
"""Native PyQt desktop dashboard for the virtual CAN-Sentinel pilot."""
import argparse, threading
from datetime import datetime
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QGroupBox, QAbstractItemView, QFrame
)
from detector import LiveDetector


class Bridge(QObject):
    frame = pyqtSignal(dict)
    alert = pyqtSignal(dict)
    error = pyqtSignal(str)


class Dashboard(QMainWindow):
    def __init__(self, interface, model):
        super().__init__()
        self.setWindowTitle('CAN-Sentinel | Automotive CAN Bus Intrusion Detection System')
        self.resize(1500, 950)
        self.setMinimumSize(1100, 720)
        self.interface = interface
        self.model_path = model
        self.stop_event = threading.Event()
        self.worker = None
        self.frames_seen = 0
        self.alerts_seen = 0
        self.bridge = Bridge()
        self.bridge.frame.connect(self.add_frame)
        self.bridge.alert.connect(self.add_alert)
        self.bridge.error.connect(self.show_error)

        # Presentation-only styling. Detector, rules, model, traffic and storage are unchanged.
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#031323; color:#e7f1ff; }
            QLabel { color:#e7f1ff; }
            QLabel#brand { font-size:34px; font-weight:800; color:#f2f7ff; }
            QLabel#brandAccent { font-size:34px; font-weight:800; color:#168cff; }
            QLabel#tagline { font-size:15px; color:#9cc9f2; }
            QLabel#meta { color:#b9d7f5; font-size:12px; }
            QFrame#header { background:#03101e; border-bottom:1px solid #12649a; }
            QFrame#metricCard { border-radius:11px; border:1px solid #087dcb; background:#041e37; }
            QFrame#monitorCard { border-color:#00d58a; background:#032f2b; }
            QFrame#alertCard { border-color:#f0143e; background:#310f20; }
            QFrame#threatCard { border-color:#ff6b16; background:#301a12; }
            QLabel#metricLabel { font-size:16px; font-weight:700; color:#5db8ff; }
            QLabel#metricValue { font-size:31px; font-weight:800; color:#f3f7ff; }
            QLabel#metricHint { font-size:13px; color:#c5def6; }
            QLabel#monitorCard QLabel#metricLabel, QLabel#monitorCard QLabel#metricValue { color:#20e9ae; }
            QLabel#alertCard QLabel#metricLabel { color:#ff5267; }
            QLabel#threatCard QLabel#metricLabel, QLabel#threatCard QLabel#metricValue { color:#ff7545; }
            QPushButton { background:#00a96b; color:white; border:0; border-radius:8px; padding:13px 20px; font-size:14px; font-weight:700; }
            QPushButton:hover { background:#00c17a; }
            QPushButton:disabled { background:#25445f; color:#819bb4; }
            QPushButton#stopButton { background:#df1f39; }
            QPushButton#stopButton:hover { background:#f22d48; }
            QPushButton#clearButton { background:#29435d; border:1px solid #3b5b7a; }
            QFrame#infoCard { background:#041d34; border:1px solid #075589; border-radius:8px; }
            QLabel#infoText { color:#c4def8; font-size:12px; }
            QGroupBox { background:#041727; border:1px solid #07517e; border-radius:9px; margin-top:12px; padding:9px; font-size:16px; font-weight:700; color:#f0f6ff; }
            QGroupBox#alertsBox { border-color:#c51637; }
            QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 7px; color:#f0f6ff; }
            QTableWidget { background:#031626; alternate-background-color:#061d31; color:#e5f1ff; gridline-color:#183b58; border:0; selection-background-color:#12456c; selection-color:white; font-size:11px; }
            QTableWidget::item { padding:5px 4px; border-bottom:1px solid #102c44; }
            QHeaderView::section { background:#102b45; color:#e6f2ff; padding:9px 5px; border:0; border-right:1px solid #24435f; border-bottom:1px solid #31516e; font-weight:700; }
            QScrollBar:vertical { background:#061a2b; width:11px; margin:0; }
            QScrollBar::handle:vertical { background:#2d526f; min-height:24px; border-radius:5px; }
            QScrollBar:horizontal { background:#061a2b; height:10px; }
            QScrollBar::handle:horizontal { background:#2d526f; border-radius:5px; }
        """)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(12)

        # Header
        header = QFrame()
        header.setObjectName('header')
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 2, 10, 12)
        header_layout.setSpacing(18)
        shield = QLabel('⬡\\n🚘')
        shield.setStyleSheet('color:#168cff;font-size:29px;font-weight:700;')
        shield.setAlignment(Qt.AlignCenter)
        shield.setMinimumWidth(80)
        header_layout.addWidget(shield)
        brand_col = QVBoxLayout()
        brand_line = QHBoxLayout()
        brand = QLabel('CAN-')
        brand.setObjectName('brand')
        brand2 = QLabel('SENTINEL')
        brand2.setObjectName('brandAccent')
        brand_line.addWidget(brand)
        brand_line.addWidget(brand2)
        brand_line.addStretch()
        brand_col.addLayout(brand_line)
        tagline = QLabel('AUTOMOTIVE CAN BUS INTRUSION DETECTION SYSTEM')
        tagline.setObjectName('tagline')
        brand_col.addWidget(tagline)
        header_layout.addLayout(brand_col, 1)

        self.status = QLabel('●  Simulation Mode\\n    (Virtual CAN Only)')
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet('background:#041a2b;border:1px solid #07517e;border-radius:15px;padding:12px;color:#13dca0;font-size:14px;font-weight:700;')
        header_layout.addWidget(self.status)

        meta = QVBoxLayout()
        self.session = QLabel('Session ID     :  not started')
        self.session.setObjectName('meta')
        self.interface_label = QLabel(f'Interface       :  {interface} (Virtual)' if interface == 'sim' else f'Interface       :  {interface}')
        self.interface_label.setObjectName('meta')
        mode = QLabel('Mode             :  LAB / PILOT')
        mode.setObjectName('meta')
        self.start_time_label = QLabel('Start Time      :  --:--:--')
        self.start_time_label.setObjectName('meta')
        for w in (self.session, self.interface_label, mode, self.start_time_label):
            meta.addWidget(w)
        header_layout.addLayout(meta)
        layout.addWidget(header)

        # Four large summary cards
        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.monitor_card, self.monitor_value, monitor_hint = self._metric_card('Monitoring', 'STOPPED', 'Waiting for CAN traffic...', 'monitorCard', '〰')
        self.messages_card, self.frame_count, messages_hint = self._metric_card('Total Messages', '0', 'Frames received', '', '▤')
        self.alert_card, self.alert_count, alerts_hint = self._metric_card('Open Alerts', '0', 'Suspicious events', 'alertCard', '⬟')
        self.threat_card, self.threat, threat_hint = self._metric_card('Threat Level', 'NONE', 'No unusual CAN activity', 'threatCard', '◉')
        for card in (self.monitor_card, self.messages_card, self.alert_card, self.threat_card):
            stats.addWidget(card, 1)
        layout.addLayout(stats)

        # Controls plus the lab disclaimer
        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.start_btn = QPushButton('▶   Start Monitoring')
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton('■   Stop Monitoring')
        self.stop_btn.setObjectName('stopButton')
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton('▤   Clear Tables')
        self.clear_btn.setObjectName('clearButton')
        self.clear_btn.clicked.connect(self.clear_view)
        for b in (self.start_btn, self.stop_btn, self.clear_btn):
            b.setMinimumHeight(54)
            action_row.addWidget(b)
        info = QFrame()
        info.setObjectName('infoCard')
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(14, 8, 14, 8)
        info_icon = QLabel('ⓘ')
        info_icon.setStyleSheet('font-size:27px;color:#168cff;font-weight:800;')
        info_layout.addWidget(info_icon)
        info_text = QLabel('This is a simulated CAN network. Normal traffic and attack traffic are generated for testing.\\nThe system uses AI and rules to detect suspicious activity.')
        info_text.setObjectName('infoText')
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text, 1)
        action_row.addWidget(info, 1)
        layout.addLayout(action_row)

        # Two side-by-side live tables
        tables = QHBoxLayout()
        tables.setSpacing(16)
        traffic_box = QGroupBox('▮  Live CAN Traffic')
        traffic_layout = QVBoxLayout(traffic_box)
        traffic_layout.setContentsMargins(0, 8, 0, 0)
        self.frames = QTableWidget(0, 9)
        self.frames.setHorizontalHeaderLabels([
            '#', 'Time', 'CAN ID', 'Signal (Demo)', 'DLC', 'Payload (Hex)', 'Frames/s', 'ML Score', 'Status'
        ])
        # The first column is a visual row number; keep all original data columns.
        self.frames.setColumnCount(9)
        self._configure(self.frames, 'traffic')
        self.frames.setToolTip('Each row is one received simulated CAN message. Red rows are flagged for review.')
        traffic_layout.addWidget(self.frames)
        tables.addWidget(traffic_box, 7)

        alerts_box = QGroupBox('⚠  Security Alerts')
        alerts_box.setObjectName('alertsBox')
        alerts_layout = QVBoxLayout(alerts_box)
        alerts_layout.setContentsMargins(0, 8, 0, 0)
        self.alerts = QTableWidget(0, 7)
        self.alerts.setHorizontalHeaderLabels([
            '#', 'Time', 'Severity', 'CAN ID', 'Signal (Demo)', 'Detection Reason', 'ML Score'
        ])
        self._configure(self.alerts, 'alerts')
        self.alerts.setToolTip('Repeated alerts may relate to the same ongoing traffic condition.')
        alerts_layout.addWidget(self.alerts)
        tables.addWidget(alerts_box, 6)
        layout.addLayout(tables, 1)

        footer = QLabel('Simulation only • Normal = not flagged • ANOMALY = unusual pattern flagged • HIGH/CRITICAL = programmed alert level')
        footer.setStyleSheet('color:#7698b8;font-size:11px;padding-left:4px;')
        layout.addWidget(footer)
        self.setCentralWidget(root)

    @staticmethod
    def _metric_card(title, value, hint, object_name='', symbol=''):
        card = QFrame()
        card.setObjectName('metricCard')
        if object_name:
            card.setProperty('class', object_name)
            card.setObjectName(object_name)
        row = QHBoxLayout(card)
        row.setContentsMargins(15, 12, 15, 12)
        row.setSpacing(14)
        icon = QLabel(symbol)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(76, 76)
        icon.setStyleSheet('background:#0b3153;border-radius:38px;color:#168cff;font-size:36px;font-weight:700;')
        row.addWidget(icon)
        col = QVBoxLayout()
        label = QLabel(title)
        label.setObjectName('metricLabel')
        val = QLabel(value)
        val.setObjectName('metricValue')
        detail = QLabel(hint)
        detail.setObjectName('metricHint')
        detail.setWordWrap(True)
        col.addWidget(label)
        col.addWidget(val)
        col.addWidget(detail)
        col.addStretch()
        row.addLayout(col, 1)
        return card, val, detail

    @staticmethod
    def _configure(table, kind):
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(35)
        table.setWordWrap(False)
        header = table.horizontalHeader()
        header.setMinimumSectionSize(48)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        if kind == 'traffic':
            widths = [38, 94, 68, 145, 42, 155, 70, 78, 88]
        else:
            widths = [38, 78, 78, 66, 135, 200, 75]
        for index, width in enumerate(widths):
            table.setColumnWidth(index, width)

    def start_monitoring(self):
        try:
            self.detector = LiveDetector(self.interface, self.model_path)
        except Exception as exc:
            QMessageBox.critical(self, 'Could not start monitoring', str(exc))
            return
        self.stop_event.clear()
        self.session.setText('Session ID     :  ' + self.detector.session_id[:8])
        self.start_time_label.setText('Start Time      :  ' + datetime.now().strftime('%H:%M:%S'))
        self.monitor_value.setText('ACTIVE')
        self.monitor_card.findChild(QLabel, 'metricHint').setText('Receiving CAN traffic...')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        def runner():
            try:
                self.detector.run(on_frame=self.bridge.frame.emit, on_alert=self.bridge.alert.emit, stop_event=self.stop_event)
            except Exception as exc:
                self.bridge.error.emit(str(exc))

        self.worker = threading.Thread(target=runner, daemon=True)
        self.worker.start()

    def stop_monitoring(self):
        self.stop_event.set()
        self.monitor_value.setText('STOPPED')
        self.monitor_card.findChild(QLabel, 'metricHint').setText('Monitoring paused')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def add_frame(self, r):
        self.frames_seen += 1
        self.frame_count.setText(f'{self.frames_seen:,}')
        row = self.frames.rowCount()
        self.frames.insertRow(row)
        vals = [
            str(self.frames_seen), datetime.fromtimestamp(r['timestamp']).strftime('%H:%M:%S.%f')[:-3],
            r['can_id_hex'], r['suspected_ecu'], str(r['dlc']), r['data'],
            f"{r['id_rate_1s']:.1f}", f"{r['anomaly_score']:.4f}",
            'ANOMALY' if r['is_anomaly'] else 'Normal'
        ]
        for column, value in enumerate(vals):
            item = QTableWidgetItem(str(value))
            if r['is_anomaly']:
                item.setBackground(Qt.darkRed)
                item.setForeground(Qt.white)
            self.frames.setItem(row, column, item)
        self.frames.scrollToBottom()
        while self.frames.rowCount() > 1000:
            self.frames.removeRow(0)

    def add_alert(self, a):
        self.alerts_seen += 1
        self.alert_count.setText(f'{self.alerts_seen:,}')
        self.threat.setText(a['severity'])
        self.threat_card.findChild(QLabel, 'metricHint').setText('Unusual CAN activity')
        row = self.alerts.rowCount()
        self.alerts.insertRow(row)
        vals = [
            str(self.alerts_seen), datetime.fromtimestamp(a['timestamp']).strftime('%H:%M:%S'),
            a['severity'], a['can_id_hex'], a['suspected_ecu'], a['reason'],
            f"{a['anomaly_score']:.4f}"
        ]
        for column, value in enumerate(vals):
            item = QTableWidgetItem(str(value))
            if a['severity'] in ('HIGH', 'CRITICAL'):
                item.setBackground(Qt.darkRed)
                item.setForeground(Qt.white)
            else:
                item.setBackground(Qt.darkYellow)
                item.setForeground(Qt.black)
            self.alerts.setItem(row, column, item)
        self.alerts.scrollToBottom()

    def clear_view(self):
        self.frames.setRowCount(0)
        self.alerts.setRowCount(0)
        self.frames_seen = self.alerts_seen = 0
        self.frame_count.setText('0')
        self.alert_count.setText('0')
        self.threat.setText('NONE')
        self.threat_card.findChild(QLabel, 'metricHint').setText('No unusual CAN activity')

    def show_error(self, msg):
        self.monitor_value.setText('ERROR')
        self.monitor_card.findChild(QLabel, 'metricHint').setText('Monitoring error')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, 'Monitoring error', msg)

    def closeEvent(self, event):
        self.stop_event.set()
        event.accept()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', default='sim')
    parser.add_argument('--model', default='models/isolation_forest.joblib')
    args = parser.parse_args()
    app = QApplication([])
    window = Dashboard(args.interface, args.model)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
