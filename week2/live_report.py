#!/usr/bin/env python3
"""Build a local HTML report from the REAL vcan0 capture, not synthetic CSV."""
import csv
import json
from html import escape
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / 'results'

def read(name):
    with (RESULTS / name).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))

def main():
    traffic = read('live_capture.csv')
    detected = read('live_detection.csv')
    audit = json.loads((RESULTS / 'audit.json').read_text(encoding='utf-8'))
    flagged = sum(int(row['alert']) for row in detected)
    ml = sum(int(row['ml_alert']) for row in detected)
    rule = sum(int(row['frequency_alert']) for row in detected)
    max_frames = max((int(r['total_frames']) for r in detected), default=1)
    scale = 150 / max(1, max_frames)
    bars = ''.join('<rect x="{x}" y="{y}" width="8" height="{h}" fill="{c}"/>'.format(
        x=25 + 12*i, y=185 - max(1, round(int(r['total_frames']) * scale)),
        h=max(1,round(int(r['total_frames']) * scale)),
        c='#d9534f' if int(r['alert']) else '#21937b') for i,r in enumerate(detected))
    width=max(520, 50 + 12*len(detected))
    rows=''.join('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
        escape(str(r['window_start_seconds'])), escape(str(r['total_frames'])),
        escape(str(r['steering_frames'])), escape(str(r['ml_alert'])),
        escape(str(r['frequency_alert'])), 'ANOMALY' if int(r['alert']) else 'NORMAL')
        for r in detected)
    template='''<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<title>CAN-Sentinel Week 2 Live Mid-Review</title>
<style>body{max-width:1120px;margin:40px auto;padding:0 20px;font:15px/1.5 Arial;color:#1f2937}
h1{color:#12385a}.tiles{display:flex;gap:12px;flex-wrap:wrap}.tile{background:#eef3f9;padding:16px;border-radius:8px;min-width:145px}.tile b{display:block;font-size:27px}
table{border-collapse:collapse;width:100%}th,td{padding:7px;border:1px solid #cbd5e1;text-align:left}th{background:#edf2f7}
.note{border-left:4px solid #b45309;background:#fff7ed;padding:12px}</style></head>
<body><h1>CAN-Sentinel — Week 2 Live Mid-Project Review</h1>
<p>Source: original Week 1 C Steering/RPM ECUs and new Week 2 C injector on <strong>virtual SocketCAN vcan0</strong>.</p>
<div class="tiles"><div class="tile">Captured CAN frames<b>__CAPTURED__</b></div>
<div class="tile">Injected frames sent<b>__SENT__</b></div>
<div class="tile">Injected frames observed<b>__OBSERVED__</b></div>
<div class="tile">Detection alert windows<b>__ALERTS__</b></div>
<div class="tile">ML-only alert windows<b>__ML__</b></div>
<div class="tile">Frequency alert windows<b>__RULE__</b></div></div>
<h2>Transmission audit</h2><p>Sent/observed comparison: <strong>__MATCH__</strong>; observed missing: __MISSING__.</p>
<p class="note"><b>Scope:</b> These are observed frames on a simulated virtual CAN interface, not a physical vehicle.
Only uniquely tagged 0x101 frames with payload 7FFF are counted in the injection audit. Matching counts do not prove zero network loss generally. ML and rule detections are reported separately.</p>
<h2>Traffic volume per second</h2>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 __WIDTH__ 210" width="__WIDTH__" style="max-width:100%">
<line x1="20" y1="185" x2="__WEND__" y2="185" stroke="#94a3b8"/>__BARS__
<text x="20" y="204" font-size="11">Green=normal prediction, red=intrusion alert, one bar per second</text></svg>
<h2>Detection details</h2><table><tr><th>Time (s)</th><th>Frames</th><th>Steering ID frames</th><th>ML</th><th>Rate rule</th><th>Final</th></tr>__ROWS__</table>
<p>Evidence: <code>live_capture.csv</code>, <code>live_detection.csv</code>, <code>audit.json</code>, <code>attack_send.log</code>.</p>
</body></html>'''
    replacements={
        '__CAPTURED__':len(traffic),'__SENT__':audit['attacker_frames_sent'],
        '__OBSERVED__':audit['attacker_frames_observed'],'__ALERTS__':flagged,
        '__ML__':ml,'__RULE__':rule,'__MATCH__':escape(audit['result']),
        '__MISSING__':audit['observed_missing'],'__WIDTH__':width,'__WEND__':width-6,
        '__BARS__':bars,'__ROWS__':rows
    }
    for old,value in replacements.items():template=template.replace(old,str(value))
    destination=RESULTS/'LIVE_MID_REVIEW.html'
    destination.write_text(template,encoding='utf-8')
    print(f'LIVE REPORT: {destination}')
    print(f'Capture frames={len(traffic)}, injected sent={audit["attacker_frames_sent"]}, observed={audit["attacker_frames_observed"]}, anomalous windows={flagged}')

if __name__=='__main__':main()
