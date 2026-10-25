"""Run: python -m unittest discover -s week2/tests -v"""
import csv
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "week2"))
from pipeline import (DEFAULT_BASELINE, FEATURES, choose_baseline, classify,
                      load_csv, make_injected_capture, metrics, raw_csv,
                      sessions, train, window_features)


class Week2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_csv(DEFAULT_BASELINE)

    def test_week1_csv_is_compatible(self):
        self.assertEqual(408, len(self.records))
        self.assertEqual({"101", "102"}, {r["can_id"] for r in self.records})
        self.assertEqual(2, self.records[0]["dlc"])

    def test_appended_session_resets_are_detected(self):
        long_log=load_csv(ROOT / "can_traffic.csv")
        self.assertEqual(1699,len(long_log))
        self.assertEqual(5,len(sessions(long_log)))
        best=choose_baseline(long_log)
        self.assertGreater(len(best),100)

    def test_extract_feature_counts(self):
        f=window_features(self.records)
        self.assertGreaterEqual(len(f),60)
        self.assertEqual(len(self.records),sum(r["total_frames"] for r in f))
        self.assertTrue(all(0 <= r["can_id_entropy"] <= 2 for r in f))

    def test_injection_detection_and_csv_schema(self):
        with tempfile.TemporaryDirectory() as td:
            model=pathlib.Path(td)/'test_model.joblib'
            bundle,baseline,train_wins,hold=train(DEFAULT_BASELINE,model)
            mixed, injected=make_injected_capture(baseline,bundle['cut_time'],attack_seconds=8,rate=60)
            self.assertEqual(480,injected)
            windows=window_features(mixed)
            results=classify(bundle,windows)
            self.assertEqual(8,metrics(results,'frequency_alert')['TP'])
            self.assertGreater(metrics(results,'ml_alert')['TP'],0)
            outfile=pathlib.Path(td)/'capture.csv'
            raw_csv(outfile,mixed)
            self.assertEqual(len(mixed),len(load_csv(outfile)))
            with outfile.open(newline='') as handle:
                header=next(csv.reader(handle))
            self.assertEqual(["timestamp_utc", "elapsed_seconds", "can_id", "dlc", "data_hex", "message_type"],header)

    def test_no_spurious_alerts_during_heldout_clean_segment(self):
        with tempfile.TemporaryDirectory() as td:
            bundle,baseline,_,_=train(DEFAULT_BASELINE,pathlib.Path(td)/'model.joblib')
            heldout=[r for r in baseline if r['t'] >= bundle['cut_time']]
            results=classify(bundle,window_features(heldout))
            self.assertEqual(0,sum(r['frequency_alert'] for r in results))

    def test_capture_parser_with_fake_candump_process(self):
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/'candump'
            fake.write_text('''#!/usr/bin/env python3
import time
for i in range(20):
    print(f"(1790000000.{i:06d}) vcan0 101#7FFF", flush=True)
    time.sleep(.012)
time.sleep(2)
''')
            fake.chmod(0o755)
            out=pathlib.Path(td)/'live.csv'
            import os
            env=os.environ.copy()
            env['PATH']=str(fake.parent)+':'+env['PATH']
            completed=subprocess.run([sys.executable,str(ROOT/'week2/capture.py'),'--seconds','1',
                                     '--out',str(out)],capture_output=True,text=True,env=env,timeout=10)
            self.assertEqual(0,completed.returncode,completed.stderr)
            self.assertEqual(20,len(load_csv(out)))


if __name__ == '__main__':
    unittest.main()
