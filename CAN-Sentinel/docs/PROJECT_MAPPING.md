# Requirement Traceability — Infotact CAN-Sentinel

Source: `PROJECT.pdf`, Project 1, pages 1–2. The PDF is the source of the project scope; the company pilot additions below are engineering recommendations, not requirements stated by the PDF.

| Source requirement | Implementation | Verification evidence |
|---|---|---|
| Linux SocketCAN `vcan0` and simulated RPM/speed/temperature | `scripts/setup_vcan.sh`, `python/traffic.py` | `ip -details link show vcan0`, `candump vcan0` |
| Low-level C CAN traffic sniffer | `c/can_sniffer.c`, `Makefile` | `make clean && make`; capture JSONL |
| Python and Scikit-learn Isolation Forest | `python/features.py`, `python/train_model.py` | model artifact and training metadata |
| Abnormal frequency, timing, payload entropy | per-ID features and hybrid rules in `python/detector.py` | automated tests plus normal/anomaly trials |
| Native PyQt diagnostic dashboard | `python/dashboard.py` | live traffic and alert display |
| Suspected ECU/node identification | `python/ecu_map.py` | illustrative mapping only; validate against a real DBC/network specification before operational use |
| Company-oriented audit trail | `python/event_store.py` | SQLite frames/alerts, session ID, deduplication, export support |
| Operational validation plan | `docs/COMPANY_PILOT_PLAN.md` | acceptance gates and risk controls |

## Current verification performed

- Python source compilation: passed.
- Automated unit tests: 6 passed, including per-ID feature isolation and SQLite alert deduplication.
- C sniffer: compiled with GCC warning flags.
- Isolation Forest model: trained on synthetic baseline rows.
- ZIP integrity: check after packaging.

These checks are not equivalent to a full live SocketCAN + PyQt integration test. Live monitoring, sustained-load behavior, false-positive/false-negative rates, and detection latency still need to be measured on the target Linux environment.

## Milestones

1. **Week 1:** virtual interface, C sniffer, synthetic normal signals, capture provenance.
2. **Week 2:** baseline model, synthetic anomaly generator, feature and rule validation.
3. **Mid-project review:** repeated normal/anomaly trials and confusion matrix.
4. **Week 3:** detector + desktop UI + durable evidence store integration.
5. **Week 4:** load/recovery tests, analyst review, screenshots, final report, and limitations.
