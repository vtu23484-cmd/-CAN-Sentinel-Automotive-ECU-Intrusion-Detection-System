#!/usr/bin/env python3
"""Repeatable offline *test* of the actual Week 2 model using Week 1 CSV.

This complements, but does NOT replace, the vcan0 runtime audit in run_live_review.sh.
"""
import argparse
import html
import json
from pathlib import Path

from pipeline import (DEFAULT_BASELINE, RESULTS, classify, load_csv, make_injected_capture,
                      metrics, raw_csv, save_csv, train, window_features)


def build_report(destination, dataset, baseline, test, injected, detected, summary):
    rows = ''.join(
        '<tr><td>{window}</td><td>{total_frames}</td><td>{steering_frames}</td><td>{rpm_frames}</td>'
        '<td>{ml_alert}</td><td>{frequency_alert}</td><td class="{class_name}">{answer}</td><td>{reason}</td></tr>'.format(
            window=int(row['window']), total_frames=int(row['total_frames']),
            steering_frames=int(row['steering_frames']),rpm_frames=int(row['rpm_frames']),
            ml_alert=int(row['ml_alert']),frequency_alert=int(row['frequency_alert']),
            class_name='bad' if row['alert'] else 'good',answer='ANOMALY' if row['alert'] else 'NORMAL',
            reason=html.escape(row['reasons'])
        ) for row in detected
    )
    max_count = max(max((r['total_frames'] for r in detected), default=1), 1)
    # Pure SVG: no JavaScript and no network requirements.
    bars=''.join(
        f'<rect x="{25+i*14}" y="{190-round(150*r["total_frames"]/max_count)}" width="10" '
        f'height="{round(150*r["total_frames"]/max_count)}" '
        f'fill="{"#ed625b" if r["alert"] else "#58a6ff"}"/>'
        for i,r in enumerate(detected)
    )
    width=max(440, 50+len(detected)*14)
    row_count=len(detected)
    out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
    <title>CAN-Sentinel Week 2 Mid-Review</title>
    <style>body{{max-width:1050px;margin:40px auto;font:15px/1.6 Arial,sans-serif;color:#172337;padding:0 20px}}
    h1,h2{{color:#12395c}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #cbd4e0;padding:7px;text-align:left}}
    th{{background:#eff4fa}}.bad{{color:#bd2525;font-weight:bold}}.good{{color:#136c4a}}
    .note{{background:#f4f7fb;padding:12px;border-left:3px solid #667d95}}svg{{max-width:100%;height:auto}}</style></head>
    <body><h1>CAN-Sentinel — Week 2 Mid-Project Review</h1>
    <p><strong>Scope:</strong> Offline rehearsal using the actual Week 1 CSV and synthetic injection.
    This report is not proof of a physical vehicle attack or of SocketCAN delivery.</p>
    <h2>Baseline and test setup</h2>
    <p>Source file: <code>{html.escape(str(dataset))}</code><br>Usable normal frames: {len(baseline)}<br>
    Normal training windows: {summary['training_windows']}<br>
    Held-out normal windows: {summary['holdout_windows']}<br>
    Simulated high-frequency injected frames: {injected}<br>Test windows: {row_count}</p>
    <h2>Detection metrics</h2><table><tr><th>Method</th><th>TP</th><th>FP</th><th>FN</th><th>TN</th><th>Recall</th><th>False positive rate</th></tr>
    {''.join('<tr><td>'+html.escape(method)+'</td>'+''.join(f'<td>{value}</td>' for value in (v['TP'],v['FP'],v['FN'],v['TN'],f"{v['recall']:.1%}",f"{v['false_positive_rate']:.1%}"))+'</tr>' for method,v in summary['metrics'].items())}
    </table><p class="note">Isolation Forest and frequency-rule results are reported separately. A combined detection is not an ML-only detection.</p>
    <h2>CAN traffic per second</h2>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 225" width="{width}" role="img" aria-label="Frames per second; red is a detected anomaly">
      <line x1="20" x2="{width-5}" y1="190" y2="190" stroke="#9aaac1" stroke-width="1"/>{bars}
      <text x="20" y="213" font-size="11">Each bar = 1 second; blue = normal prediction; red = alert</text>
    </svg><h2>Detection window details</h2>
    <table><tr><th>Window</th><th>Frames</th><th>Steering</th><th>RPM</th><th>ML alert</th><th>Rate alert</th><th>Final</th><th>Reason</th></tr>{rows}</table>
    <p class="note">Mid-review live demonstration: run <code>bash week2/run_live_review.sh</code> inside Ubuntu WSL2 after setting up vcan0.
    Inspect <code>week2/results/audit.json</code> for sent-vs-observed counts.</p></body></html>'''
    destination.write_text(out,encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv',default=str(DEFAULT_BASELINE))
    p.add_argument('--rate',type=int,default=60)
    p.add_argument('--duration',type=int,default=8)
    a=p.parse_args()
    if not (5 <= a.rate <= 300) or not (1 <= a.duration <= 12):
        p.error('rate must be 5..300 and duration 1..12')
    RESULTS.mkdir(parents=True,exist_ok=True)
    bundle,baseline,train_windows,test_windows=train(a.csv)
    mixed, n=make_injected_capture(baseline,bundle['cut_time'],attack_offset=5,
                                   attack_seconds=a.duration,rate=a.rate)
    raw_csv(RESULTS/'simulated_attack.csv',mixed)
    features=window_features(mixed)
    output=classify(bundle,features)
    save_csv(RESULTS/'offline_detection.csv',output)
    m={
        'Isolation Forest':metrics(output,'ml_alert'),
        'Frequency guardrail':metrics(output,'frequency_alert'),
        'Combined':metrics(output,'alert')
    }
    summary={"source":str(a.csv),"normal_frames":len(baseline),
             "training_windows":len(train_windows),"holdout_windows":len(test_windows),
             "injected_frames":n,"test_windows":len(output),"metrics":m,
             "scope":"synthetic offline test; not vcan0 packet-loss proof"}
    (RESULTS/'offline_metrics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    build_report(RESULTS/'MID_REVIEW.html',a.csv,baseline,test_windows,n,output,summary)
    print('CAN-SENTINEL | WEEK 2 | OFFLINE REHEARSAL')
    print('Normal Week 1 records:',len(baseline))
    print('Training windows:',len(train_windows),'Held-out windows:',len(test_windows))
    print('Synthetic injected frames:',n)
    for name,value in m.items():
        print(name,':', 'TP',value['TP'],'FP',value['FP'],'FN',value['FN'],
              'Recall',f"{value['recall']:.1%}")
    print('Open:',RESULTS/'MID_REVIEW.html')


if __name__=='__main__':
    main()
