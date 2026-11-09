#!/usr/bin/env python3
"""CAN Sentinel browser dashboard. Uses only Python standard library."""

import csv
import io
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "week3" / "incidents.db"
STATUS = ROOT / "week3" / "live_status.json"
PAGE = ROOT / "week3" / "web" / "index.html"
SOCKET = Path("/tmp/can_sentinel.sock")
server_process = None
sniffer_process = None
log_stream = None


def read_status():
    try:
        return json.loads(STATUS.read_text())
    except (OSError, ValueError):
        return {
            "running": False, "frames": 0, "steering": 0, "rpm": 0,
            "risk_score": 0, "severity": "NORMAL", "reasons": [],
            "vcan": False, "sniffer": False, "model": False
        }


def read_incidents():
    if not DB.exists():
        return []
    try:
        with sqlite3.connect(DB, timeout=2) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT id,timestamp,severity,risk_score,can_ids,reasons "
                "FROM incidents ORDER BY id DESC LIMIT 20"
            ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                try:
                    item["reasons"] = ", ".join(json.loads(item["reasons"]))
                except (ValueError, TypeError):
                    item["reasons"] = str(item["reasons"])
                result.append(item)
            return result
    except sqlite3.Error:
        return []


def stop_monitoring():
    global server_process, sniffer_process
    for process in (sniffer_process, server_process):
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    sniffer_process = None
    server_process = None
    return {"message": "Monitoring stopped."}


def start_monitoring():
    global server_process, sniffer_process, log_stream

    if server_process and server_process.poll() is None:
        return {"message": "Monitoring is already running."}, 200

    check = subprocess.run(
        ["ip", "link", "show", "dev", "vcan0"],
        capture_output=True, text=True
    )
    if check.returncode:
        return {"error": "vcan0 is unavailable. Set up the virtual CAN interface first."}, 400

    if not (ROOT / "week3" / "sniffer").is_file():
        return {"error": "C sniffer executable is missing. Build week3/sniffer first."}, 400

    log_stream = open(ROOT / "week3" / "web_dashboard.log", "a")
    server_process = subprocess.Popen(
        [sys.executable, "-u", str(ROOT / "week3" / "socket_server.py")],
        cwd=ROOT, stdout=log_stream, stderr=subprocess.STDOUT
    )

    deadline = time.time() + 12
    while time.time() < deadline:
        if server_process.poll() is not None:
            return {"error": "Detection server exited. Check week3/web_dashboard.log."}, 500
        if SOCKET.exists():
            break
        time.sleep(0.2)
    else:
        stop_monitoring()
        return {"error": "Detection server did not create its CAN socket in time."}, 500

    sniffer_process = subprocess.Popen(
        [str(ROOT / "week3" / "sniffer")],
        cwd=ROOT, stdout=log_stream, stderr=subprocess.STDOUT
    )
    return {"message": "Detection server and C sniffer started on vcan0."}, 200


class Handler(BaseHTTPRequestHandler):
    def send_data(self, data, content_type="application/json", status=200):
        body = data if isinstance(data, bytes) else (
            data.encode() if isinstance(data, str)
            else json.dumps(data).encode()
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            try:
                self.send_data(PAGE.read_bytes(), "text/html; charset=utf-8")
            except OSError:
                self.send_error(500, "Dashboard HTML is missing")
        elif route == "/api/status":
            self.send_data(read_status())
        elif route == "/api/incidents":
            self.send_data(read_incidents())
        elif route == "/api/export":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "id", "timestamp", "severity", "risk_score",
                "can_ids", "frame_count", "reasons", "ml_score", "details"
            ])
            if DB.exists():
                with sqlite3.connect(DB, timeout=2) as db:
                    writer.writerows(db.execute(
                        "SELECT id,timestamp,severity,risk_score,can_ids,"
                        "frame_count,reasons,ml_score,details "
                        "FROM incidents ORDER BY id DESC"
                    ))
            self.send_data(
                output.getvalue(),
                "text/csv; charset=utf-8"
            )
            # Replace the default download disposition with a separate response
        else:
            self.send_error(404)

    def do_POST(self):
        route = urlparse(self.path).path
        if route == "/api/start":
            result, status = start_monitoring()
            self.send_data(result, status=status)
        elif route == "/api/stop":
            self.send_data(stop_monitoring())
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        print("[WEB]", fmt % args)


def main():
    host = os.environ.get("CAN_SENTINEL_HOST", "127.0.0.1")
    port = int(os.environ.get("CAN_SENTINEL_PORT", "8765"))
    print(f"CAN Sentinel Auto-SOC: http://{host}:{port}")
    print("Local browser dashboard. CAN monitoring is restricted to vcan0.")
    httpd = ThreadingHTTPServer((host, port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_monitoring()
        httpd.server_close()


if __name__ == "__main__":
    main()
