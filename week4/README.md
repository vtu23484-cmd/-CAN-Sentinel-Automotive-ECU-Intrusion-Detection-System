# CAN Sentinel - Week 4

## Overview
Week 4 extends CAN Sentinel with advanced offline ECU anomaly
detection, risk scoring, model comparison and forensic reporting.

## Components

- detection/timing_detector.py
- detection/payload_detector.py
- detection/advanced_engine.py
- detection/risk_scorer.py
- detection/incident_manager.py
- detection/incident_store.py
- models/model_comparison.py
- reports/export_forensics.py
- tests/

## Detection capabilities

1. ECU message timing deviation
2. Repeated payload concentration
3. Combined anomaly findings
4. Unified risk scoring
5. Incident prioritization
6. Persistent SQLite incident history
7. JSON forensic report export
8. Isolation Forest and Random Forest comparison

## Testing

Run from the repository root:

    ./week4/run_tests.sh

## Safety

All Week 4 demonstrations and synthetic tests are offline.
Do not connect synthetic attack traffic to a real vehicle or
safety-critical CAN network.

## Limitations

- Timing thresholds are experimental.
- Payload concentration is a heuristic, not proof of replay.
- Risk scores are project-specific, not attack probabilities.
- Model comparison uses a simplified synthetic dataset.
- Live Week 4 integration requires separate validation.
