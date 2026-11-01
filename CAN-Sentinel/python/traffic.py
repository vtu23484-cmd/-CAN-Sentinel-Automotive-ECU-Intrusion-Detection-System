#!/usr/bin/env python3
"""Synthetic CAN traffic generator; sends only to a virtual SocketCAN interface."""
import argparse
import random
import time
import can
import socket
import json

NORMAL_MESSAGES = [
    (0x100, 0.020, lambda: [random.randint(0x03, 0x1F), random.randint(0, 255), 0, 0, 0, 0, 0, 0]),
    (0x101, 0.050, lambda: [random.randint(0, 120), 0, 0, 0, 0, 0, 0, 0]),
    (0x102, 0.200, lambda: [random.randint(60, 110), 0, 0, 0, 0, 0, 0, 0]),
    (0x180, 0.100, lambda: [0, 0, 0, 0, 0, 0, 0, 0]),
]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--interface', default='vcan0')
    ap.add_argument('--mode', choices=['normal', 'anomaly'], default='normal')
    ap.add_argument('--duration', type=float, default=30.0)
    args = ap.parse_args()
    windows_sim = args.interface.lower() in ('sim', 'udp', 'windows-sim')
    if windows_sim:
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bus = None
        def send_frame(can_id, payload):
            packet = {'timestamp': time.time(), 'can_id': can_id, 'dlc': len(payload), 'data': bytes(payload).hex().upper()}
            sender.sendto(json.dumps(packet).encode('utf-8'), ('127.0.0.1', 37000))
    else:
        bus = can.Bus(interface='socketcan', channel=args.interface)
        sender = None
        def send_frame(can_id, payload):
            bus.send(can.Message(arbitration_id=can_id, data=payload, is_extended_id=False))
    deadline = time.monotonic() + max(0.1, args.duration)
    try:
        if args.mode == 'normal':
            next_due = {can_id: time.monotonic() for can_id, _, _ in NORMAL_MESSAGES}
            while time.monotonic() < deadline:
                now = time.monotonic()
                for can_id, interval, payload_fn in NORMAL_MESSAGES:
                    if now >= next_due[can_id]:
                        send_frame(can_id, payload_fn())
                        next_due[can_id] = now + interval
                time.sleep(0.001)
        else:
            # Synthetic anomaly: high-rate frames on a test ID plus changing payload bytes.
            while time.monotonic() < deadline:
                payload = [random.randrange(256) for _ in range(8)]
                send_frame(0x555, payload)
                time.sleep(0.001)
    except KeyboardInterrupt:
        pass
    finally:
        if bus is not None: bus.shutdown()
        if sender is not None: sender.close()
    print(f'Finished {args.mode} traffic on {args.interface} simulation/interface.')

if __name__ == '__main__':
    main()
