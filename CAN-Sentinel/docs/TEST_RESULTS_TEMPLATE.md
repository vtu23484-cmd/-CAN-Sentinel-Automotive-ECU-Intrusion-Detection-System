# CAN-Sentinel Validation Record

Do not fill expected results as measured results. Record actual runs only.

| Run ID | Date/time | Model version/hash | Scenario | Duration | Frames captured | Alerts | True positives | False positives | False negatives | Median latency | Notes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| | | | Normal baseline | | | | | | | | |
| | | | Synthetic burst | | | | | | | | |

## Definitions

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- False-positive rate = FP / (FP + TN)
- Detection latency = alert timestamp − first timestamp of the scripted anomalous condition

Define event-level versus frame-level counting before comparing runs. Keep training and test captures separate. Include hardware/VM details, Linux/Python/package versions, traffic profile, and any excluded intervals.
