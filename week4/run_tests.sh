#!/usr/bin/env bash
set -e

echo "======================================"
echo " CAN SENTINEL - WEEK 4 TEST SUITE"
echo "======================================"

echo
echo "[1/5] Timing detector"
.venv/bin/python week4/tests/test_timing_detector.py

echo
echo "[2/5] Payload detector"
.venv/bin/python week4/tests/test_payload_detector.py

echo
echo "[3/5] Advanced detection engine"
.venv/bin/python week4/tests/test_advanced_engine.py

echo
echo "[4/5] Risk scoring"
.venv/bin/python week4/tests/test_risk_scorer.py

echo
echo "[5/5] Incident management and storage"
.venv/bin/python week4/tests/test_incident_manager.py
.venv/bin/python week4/tests/test_incident_store.py

echo
echo "======================================"
echo " ALL WEEK 4 TESTS COMPLETED"
echo "======================================"
