# Company Pilot Plan — CAN-Sentinel

## Intended use
A controlled research/engineering demonstrator that identifies unusual traffic on a **virtual** CAN network and gives an operator evidence to investigate. It is not a production ECU protection product.

## Workstreams

1. **Requirements and governance** — define intended vehicle/network, approved data source, safety boundary, stakeholders, retention policy, and measurable acceptance criteria.
2. **Capture and provenance** — version the interface configuration, timestamp source, capture tool, test scenario, and model version. Preserve raw captures for reproducibility.
3. **Detection engineering** — establish per-ID timing/rate baselines; combine rules with anomaly scoring; calibrate on validation data; test on held-out sessions.
4. **Operator workflow** — deduplicate repeated alerts, show severity/reason/evidence, document analyst disposition, and export results for review.
5. **Verification** — unit, integration, load, recovery, false-positive, false-negative, and latency tests. Report measured metrics and limitations.
6. **Production readiness review** — threat model, secure build/release, access control, audit integrity, key/data management, HIL testing, safety and automotive cybersecurity review.

## Suggested acceptance gates (targets to agree with the company)

| Gate | Evidence | Proposed target for pilot, not yet measured |
|---|---|---|
| Functional | Normal and synthetic anomaly scenario results | All scripted scenarios execute and outputs are reproducible |
| Detection | Holdout confusion matrix | Set target only after data review; report precision/recall, not accuracy alone |
| Latency | Event timestamp to alert timestamp | Agree target based on capture rate and use case |
| Stability | 30-minute sustained virtual traffic run | No crash, no unbounded memory growth, recoverable errors |
| Audit | Frame/alert rows linked by session and timestamp | All alerts trace to supporting frame evidence |
| Safety | Interface allowlist and review | Demonstration scripts only permitted on `vcan0` by default |

## Risks and mitigations

- **Synthetic-to-real gap:** use authorized representative captures and a held-out evaluation set.
- **False positives:** tune per-ID thresholds and review every alert class with domain experts.
- **Incorrect ECU attribution:** use a verified DBC or OEM network documentation; otherwise report only CAN ID.
- **Alert flooding:** deduplication exists; tune incident grouping and cooldown for the target profile.
- **Data tampering or sensitive traces:** define storage permissions, retention, backup, and integrity controls before use outside a lab.
- **Unsafe interaction:** keep all generators on `vcan0`; do not add active blocking without a separate safety case and authorized hardware-in-the-loop review.

## Required company sign-off before deployment

- Product owner confirms intended use and scope.
- Vehicle/network owner authorizes data capture and testing.
- Security engineer approves threat model and evaluation methodology.
- Functional-safety/automotive cybersecurity stakeholders approve any integration plan.
- Data owner approves retention and access policy.
